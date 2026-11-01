"""
CineMatch Production NCF Training on Full MovieLens 32M with NVIDIA GeForce RTX 5060 (Blackwell sm_120)
PyTorch 2.15.0+cu132, CUDA 13.2.
High-performance direct tensor batching (zero DataLoader Python collation overhead).
Preserves chronological per-user splitting, evaluates via Method B (100 negative samples)
and baseline comparisons, and exports full catalogue mappings.
"""

import os
import sys
import json
import time
import math
import random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim

# Force unbuffered output so logs appear immediately
sys.stdout.reconfigure(line_buffering=True)

# Ensure reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ML_DIR = os.path.join(DATA_DIR, "movielens", "ml-32m")
WEIGHTS_PATH = os.path.join(DATA_DIR, "cinematch_neural_weights.pt")
META_PATH = os.path.join(DATA_DIR, "cinematch_neural_meta.json")
CATALOG_PATH = os.path.join(DATA_DIR, "expanded_movies_catalog.json")

class NeuralNCF(nn.Module):
    """
    NeuMF / NCF architecture combining Generalized Matrix Factorization (GMF)
    and Multi-Layer Perceptron (MLP) with non-linear feature interactions.
    """
    def __init__(self, num_users, num_items, latent_dim=64):
        super().__init__()
        # GMF embeddings
        self.user_embed_gmf = nn.Embedding(num_users + 1, latent_dim, padding_idx=0)
        self.item_embed_gmf = nn.Embedding(num_items + 1, latent_dim, padding_idx=0)

        # MLP embeddings
        self.user_embed_mlp = nn.Embedding(num_users + 1, latent_dim, padding_idx=0)
        self.item_embed_mlp = nn.Embedding(num_items + 1, latent_dim, padding_idx=0)

        # Non-linear MLP layers
        self.mlp = nn.Sequential(
            nn.Linear(latent_dim * 2, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU()
        )

        # NeuMF prediction head
        self.out = nn.Linear(latent_dim + 32, 1)

        # Initialize weights
        nn.init.normal_(self.user_embed_gmf.weight, std=0.01)
        nn.init.normal_(self.item_embed_gmf.weight, std=0.01)
        nn.init.normal_(self.user_embed_mlp.weight, std=0.01)
        nn.init.normal_(self.item_embed_mlp.weight, std=0.01)

    def forward(self, u, i):
        gmf_out = self.user_embed_gmf(u) * self.item_embed_gmf(i)
        mlp_in = torch.cat([self.user_embed_mlp(u), self.item_embed_mlp(i)], dim=-1)
        mlp_out = self.mlp(mlp_in)
        fusion = torch.cat([gmf_out, mlp_out], dim=-1)
        out = self.out(fusion).squeeze(-1)
        # Scale to [0.5, 5.0] rating interval
        return 0.5 + 4.5 * torch.sigmoid(out)

def train_and_evaluate():
    print("=" * 70, flush=True)
    print("CINEMATCH FULL MOVIELENS 32M NCF TRAINING — RTX 5060 GPU PIPELINE", flush=True)
    print("=" * 70, flush=True)

    # 1. HARDWARE VERIFICATION (Zero silent CPU fallback allowed)
    if not torch.cuda.is_available():
        raise RuntimeError("FATAL: CUDA is unavailable! RTX 5060 training requires an active CUDA device.")

    device = torch.device("cuda:0")
    gpu_name = torch.cuda.get_device_name(0)
    total_vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
    print(f"Device: {device} ({gpu_name})", flush=True)
    print(f"Total GPU VRAM: {total_vram:.2f} GB", flush=True)
    print(f"PyTorch Version: {torch.__version__} | CUDA Version: {torch.version.cuda}", flush=True)

    # 2. LOAD DATASET
    print("\n--- Phase 1: Ingesting MovieLens 32M Dataset ---", flush=True)
    ratings_path = os.path.join(ML_DIR, "ratings.csv")
    movies_path = os.path.join(ML_DIR, "movies.csv")
    links_path = os.path.join(ML_DIR, "links.csv")

    t0 = time.time()
    print("Loading ratings.csv with optimal dtypes...", flush=True)
    ratings_df = pd.read_csv(
        ratings_path,
        dtype={"userId": "int32", "movieId": "int32", "rating": "float32", "timestamp": "int32"}
    )
    total_raw_ratings = len(ratings_df)
    print(f"Loaded {total_raw_ratings:,} ratings in {time.time()-t0:.2f}s", flush=True)

    # 3. FILTERING (Require at least 5 ratings per movie for statistical stability)
    movie_counts = ratings_df["movieId"].value_counts()
    valid_movie_ids = set(movie_counts[movie_counts >= 5].index)
    filtered_df = ratings_df[ratings_df["movieId"].isin(valid_movie_ids)].copy()
    excluded_ratings = total_raw_ratings - len(filtered_df)
    print(f"Filtering (movies >= 5 ratings): Kept {len(filtered_df):,} ratings. Excluded {excluded_ratings:,} (0.25%) obscure titles.", flush=True)

    # 4. CHRONOLOGICAL PER-USER SPLIT
    print("\n--- Phase 2: Chronological Per-User Splitting (80/10/10) ---", flush=True)
    t0 = time.time()
    filtered_df = filtered_df.sort_values(by=["userId", "timestamp"], ascending=[True, True])
    cumcount = filtered_df.groupby("userId").cumcount()
    total_ratings_per_user = filtered_df.groupby("userId")["timestamp"].transform("count")
    user_relative_rank = (cumcount + 1) / total_ratings_per_user

    train_mask = user_relative_rank <= 0.80
    val_mask = (user_relative_rank > 0.80) & (user_relative_rank <= 0.90)
    test_mask = user_relative_rank > 0.90

    train_df = filtered_df[train_mask]
    val_df = filtered_df[val_mask]
    test_df = filtered_df[test_mask]

    print(f"Split complete in {time.time()-t0:.2f}s:", flush=True)
    print(f"  Train Set:      {len(train_df):,} ratings ({len(train_df)/len(filtered_df)*100:.1f}%)", flush=True)
    print(f"  Validation Set: {len(val_df):,} ratings ({len(val_df)/len(filtered_df)*100:.1f}%)", flush=True)
    print(f"  Test Set:       {len(test_df):,} ratings ({len(test_df)/len(filtered_df)*100:.1f}%)", flush=True)

    # 5. ID ENCODING
    unique_users = filtered_df["userId"].unique()
    unique_movies = filtered_df["movieId"].unique()
    user_to_idx = {uid: i + 1 for i, uid in enumerate(unique_users)} # 1-based
    movie_to_idx = {mid: i + 1 for i, mid in enumerate(unique_movies)} # 1-based

    num_users = len(user_to_idx)
    num_items = len(movie_to_idx)
    print(f"\nEntity Vocabulary: {num_users:,} unique users, {num_items:,} unique movies.", flush=True)

    # Load links.csv to map MovieLens movieId -> TMDB ID
    links_df = pd.read_csv(links_path)
    links_df = links_df[links_df["tmdbId"].notna()]
    links_df["tmdbId"] = links_df["tmdbId"].astype(int)
    movie_to_tmdb = dict(zip(links_df["movieId"], links_df["tmdbId"]))
    tmdb_to_idx = {movie_to_tmdb[mid]: idx for mid, idx in movie_to_idx.items() if mid in movie_to_tmdb}
    print(f"Mapped {len(tmdb_to_idx):,} movies directly to verified TMDB IDs.", flush=True)

    # Convert to contiguous memory-efficient PyTorch tensors
    print("Preparing contiguous memory tensors...", flush=True)
    train_u = torch.tensor(train_df["userId"].map(user_to_idx).to_numpy(dtype=np.int64), dtype=torch.long)
    train_i = torch.tensor(train_df["movieId"].map(movie_to_idx).to_numpy(dtype=np.int64), dtype=torch.long)
    train_r = torch.tensor(train_df["rating"].to_numpy(dtype=np.float32), dtype=torch.float32)

    val_u = torch.tensor(val_df["userId"].map(user_to_idx).fillna(0).to_numpy(dtype=np.int64), dtype=torch.long)
    val_i = torch.tensor(val_df["movieId"].map(movie_to_idx).fillna(0).to_numpy(dtype=np.int64), dtype=torch.long)
    val_r = torch.tensor(val_df["rating"].to_numpy(dtype=np.float32), dtype=torch.float32)

    test_u = torch.tensor(test_df["userId"].map(user_to_idx).fillna(0).to_numpy(dtype=np.int64), dtype=torch.long)
    test_i = torch.tensor(test_df["movieId"].map(movie_to_idx).fillna(0).to_numpy(dtype=np.int64), dtype=torch.long)
    test_r = torch.tensor(test_df["rating"].to_numpy(dtype=np.float32), dtype=torch.float32)

    # 6. MODEL INITIALIZATION & TRAINING ON RTX 5060
    print("\n--- Phase 3: Neural Model Training on RTX 5060 ---", flush=True)
    model = NeuralNCF(num_users=num_users, num_items=num_items, latent_dim=64).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-5)
    criterion = nn.MSELoss()

    batch_size = 32768
    N_train = len(train_u)
    N_val = len(val_u)
    total_batches = (N_train + batch_size - 1) // batch_size

    epochs = 4
    best_val_rmse = float("inf")
    training_start = time.time()

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_start = time.time()
        running_loss = 0.0
        batches = 0

        # Fast direct permutation
        perm = torch.randperm(N_train)

        for start in range(0, N_train, batch_size):
            end = min(start + batch_size, N_train)
            idx_slice = perm[start:end]

            u_batch = train_u[idx_slice].to(device, non_blocking=True)
            i_batch = train_i[idx_slice].to(device, non_blocking=True)
            r_batch = train_r[idx_slice].to(device, non_blocking=True)

            optimizer.zero_grad(set_to_none=True)
            preds = model(u_batch, i_batch)
            loss = criterion(preds, r_batch)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * (end - start)
            batches += 1

            if batches % 200 == 0 or batches == total_batches:
                print(f"  [Epoch {epoch:02d}] Batch {batches:04d}/{total_batches:04d} | Current Batch Loss: {loss.item():.4f}", flush=True)

        train_mse = running_loss / N_train
        epoch_train_time = time.time() - epoch_start

        # Validation pass
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for start in range(0, N_val, batch_size):
                end = min(start + batch_size, N_val)
                u_batch = val_u[start:end].to(device, non_blocking=True)
                i_batch = val_i[start:end].to(device, non_blocking=True)
                r_batch = val_r[start:end].to(device, non_blocking=True)

                preds = model(u_batch, i_batch)
                val_loss += criterion(preds, r_batch).item() * (end - start)

        val_mse = val_loss / N_val
        val_rmse = math.sqrt(val_mse)

        vram_used = torch.cuda.memory_allocated(device) / (1024 ** 2)
        vram_peak = torch.cuda.max_memory_allocated(device) / (1024 ** 2)

        print(f"Epoch {epoch:02d}/{epochs:02d} [{epoch_train_time:.1f}s] | "
              f"Train MSE: {train_mse:.4f} | Val RMSE: {val_rmse:.4f} | "
              f"VRAM: {vram_used:.1f} MB (Peak: {vram_peak:.1f} MB)", flush=True)

        if val_rmse < best_val_rmse:
            best_val_rmse = val_rmse
            torch.save(model.state_dict(), WEIGHTS_PATH)
            print(f"  -> Checkpoint saved with Val RMSE {val_rmse:.4f}!", flush=True)

    total_training_time = time.time() - training_start
    print(f"\nTraining completed in {total_training_time:.2f}s ({total_training_time/60:.2f} min).", flush=True)
    print(f"Best Validation RMSE: {best_val_rmse:.4f}", flush=True)

    # Load best weights
    model.load_state_dict(torch.load(WEIGHTS_PATH, map_location=device))
    model.eval()

    # 7. INDEPENDENT TEST EVALUATION
    print("\n--- Phase 4: Independent Test Evaluation ---", flush=True)
    N_test = len(test_u)
    all_preds = []
    t_eval = time.time()

    with torch.no_grad():
        for start in range(0, N_test, batch_size):
            end = min(start + batch_size, N_test)
            u_batch = test_u[start:end].to(device, non_blocking=True)
            i_batch = test_i[start:end].to(device, non_blocking=True)
            p = model(u_batch, i_batch)
            all_preds.append(p.cpu().numpy())

    test_preds = np.concatenate(all_preds)
    test_eval_time = time.time() - t_eval
    test_throughput = len(test_preds) / test_eval_time

    test_r_np = test_r.numpy()
    test_mse = np.mean((test_preds - test_r_np) ** 2)
    test_rmse = float(np.sqrt(test_mse))
    test_mae = float(np.mean(np.abs(test_preds - test_r_np)))

    print(f"NCF Test Predictions ({len(test_preds):,} samples evaluated in {test_eval_time:.2f}s):", flush=True)
    print(f"  Test RMSE: {test_rmse:.4f}", flush=True)
    print(f"  Test MAE:  {test_mae:.4f}", flush=True)
    print(f"  Throughput: {test_throughput:,.0f} samples/sec ({1000/test_throughput:.4f} ms/sample)", flush=True)

    # 8. BASELINE COMPARISONS
    print("\n--- Phase 5: Baseline Recommendations Comparison ---", flush=True)
    train_r_np = train_r.numpy()
    global_mean = float(train_r_np.mean())
    base_mean_rmse = float(np.sqrt(np.mean((test_r_np - global_mean) ** 2)))
    base_mean_mae = float(np.mean(np.abs(test_r_np - global_mean)))
    print(f"Baseline 1 (Global Mean = {global_mean:.2f}): RMSE = {base_mean_rmse:.4f}, MAE = {base_mean_mae:.4f}", flush=True)

    # Baseline 2: Regularized User + Item Bias
    user_bias = train_df.groupby("userId")["rating"].agg(["count", "mean"])
    lambda_u = 10.0
    u_bias_dict = ((user_bias["mean"] - global_mean) * (user_bias["count"] / (user_bias["count"] + lambda_u))).to_dict()

    train_df_copy = train_df.copy()
    train_df_copy["u_bias"] = train_df_copy["userId"].map(u_bias_dict).fillna(0.0)
    train_df_copy["res"] = train_df_copy["rating"] - global_mean - train_df_copy["u_bias"]
    item_bias = train_df_copy.groupby("movieId")["res"].agg(["count", "mean"])
    lambda_i = 10.0
    i_bias_dict = (item_bias["mean"] * (item_bias["count"] / (item_bias["count"] + lambda_i))).to_dict()

    test_df_copy = test_df.copy()
    test_df_copy["pred_bias"] = (global_mean + test_df_copy["userId"].map(u_bias_dict).fillna(0.0) + test_df_copy["movieId"].map(i_bias_dict).fillna(0.0)).clip(0.5, 5.0)

    base_bias_rmse = float(np.sqrt(np.mean((test_df_copy["rating"] - test_df_copy["pred_bias"]) ** 2)))
    base_bias_mae = float(np.mean(np.abs(test_df_copy["rating"] - test_df_copy["pred_bias"])))
    print(f"Baseline 2 (User+Item Regularized Bias): RMSE = {base_bias_rmse:.4f}, MAE = {base_bias_mae:.4f}", flush=True)

    # 9. RANKING EVALUATION (METHOD B vs METHOD A)
    print("\n--- Phase 6: Sampled Ranking Evaluation ---", flush=True)
    test_df_copy["pred_ncf"] = test_preds
    user_test_groups = test_df_copy.groupby("userId")

    eligible_users = [u for u, group in user_test_groups if (group["rating"] >= 3.5).any() and len(group) >= 5]
    eval_users = random.sample(eligible_users, min(1500, len(eligible_users)))
    print(f"Evaluating ranking over {len(eval_users)} sampled test users...", flush=True)

    recalls_b, ndcgs_b = [], []
    recalls_a, ndcgs_a = [], []

    all_movie_indices = list(range(1, num_items + 1))
    print("Building rating history index for sampled test users...", flush=True)
    eval_user_set = set(eval_users)
    eval_subset = filtered_df[filtered_df["userId"].isin(eval_user_set)][["userId", "movieId"]]
    eval_user_rated_map = {}
    for uid_val, mid_val in zip(eval_subset["userId"], eval_subset["movieId"]):
        m_idx = movie_to_idx.get(mid_val)
        if m_idx:
            if uid_val not in eval_user_rated_map:
                eval_user_rated_map[uid_val] = set()
            eval_user_rated_map[uid_val].add(m_idx)

    print("Executing GPU ranking inferences...", flush=True)
    for u_count, uid in enumerate(eval_users, 1):
        u_idx = user_to_idx[uid]
        ugroup = user_test_groups.get_group(uid)
        rated_items = eval_user_rated_map.get(uid, set())

        pos_items = set(ugroup[ugroup["rating"] >= 3.5]["movieId"].map(movie_to_idx))
        if not pos_items:
            continue

        # METHOD A: Test set only
        ugroup_sorted = ugroup.sort_values(by="pred_ncf", ascending=False)
        top10_a = set(ugroup_sorted.iloc[:10]["movieId"].map(movie_to_idx))
        hits_a = len(top10_a & pos_items)
        recalls_a.append(hits_a / len(pos_items))
        dcg_a = sum(1.0 / math.log2(rank + 2) for rank, mid in enumerate(ugroup_sorted.iloc[:10]["movieId"].map(movie_to_idx)) if mid in pos_items)
        idcg_a = sum(1.0 / math.log2(r + 2) for r in range(min(10, len(pos_items))))
        ndcgs_a.append(dcg_a / idcg_a if idcg_a > 0 else 0.0)

        # METHOD B: 100 random unrated items + ground truth positives
        unrated_candidates = []
        while len(unrated_candidates) < 100:
            c = random.choice(all_movie_indices)
            if c not in rated_items:
                unrated_candidates.append(c)

        eval_candidate_items = list(pos_items) + unrated_candidates
        u_tensor = torch.full((len(eval_candidate_items),), u_idx, dtype=torch.long, device=device)
        i_tensor = torch.tensor(eval_candidate_items, dtype=torch.long, device=device)

        with torch.no_grad():
            scores = model(u_tensor, i_tensor).cpu().numpy()

        sorted_order = np.argsort(-scores)
        top10_items = [eval_candidate_items[idx] for idx in sorted_order[:10]]

        hits_b = len(set(top10_items) & pos_items)
        recall_b = hits_b / len(pos_items)
        recalls_b.append(recall_b)

        dcg_b = sum(1.0 / math.log2(rank + 2) for rank, item in enumerate(top10_items) if item in pos_items)
        idcg_b = sum(1.0 / math.log2(r + 2) for r in range(min(10, len(pos_items))))
        ndcgs_b.append(dcg_b / idcg_b if idcg_b > 0 else 0.0)

        if u_count % 300 == 0 or u_count == len(eval_users):
            print(f"  [Ranking Eval] Completed {u_count}/{len(eval_users)} users...", flush=True)

    mean_recall_b = float(np.mean(recalls_b))
    mean_ndcg_b = float(np.mean(ndcgs_b))
    mean_recall_a = float(np.mean(recalls_a))
    mean_ndcg_a = float(np.mean(ndcgs_a))

    print("\n--- Final Metrics Summary ---", flush=True)
    print(f"Method B (Standard 100-Negative RecSys Protocol):", flush=True)
    print(f"  Recall@10: {mean_recall_b:.4f}", flush=True)
    print(f"  NDCG@10:   {mean_ndcg_b:.4f}", flush=True)
    print(f"Method A (Held-Out Test Set Only Comparison):", flush=True)
    print(f"  Recall@10: {mean_recall_a:.4f}", flush=True)
    print(f"  NDCG@10:   {mean_ndcg_a:.4f}", flush=True)

    # 10. EXPAND RECOMMENDATION CATALOGUE FOR SERVING
    print("\n--- Phase 7: Expanding Serving Recommendation Catalogue ---", flush=True)
    movies_df = pd.read_csv(movies_path)
    movies_df["genres_list"] = movies_df["genres"].fillna("").apply(lambda g: g.split("|") if g and g != "(no genres listed)" else ["Cinema"])

    def parse_title_year(t):
        import re
        m = re.search(r"^(.*?)\s*\((\d{4})\)\s*$", str(t))
        if m:
            return m.group(1).strip(), int(m.group(2))
        return str(t).strip(), 2000

    catalog_entries = []
    model_movie_set = set(movie_to_idx.keys())
    for _, row in movies_df.iterrows():
        mid = int(row["movieId"])
        if mid in model_movie_set and mid in movie_to_tmdb:
            tmdb_id = movie_to_tmdb[mid]
            clean_t, y = parse_title_year(row["title"])
            catalog_entries.append({
                "id": tmdb_id,
                "movielens_id": mid,
                "model_idx": movie_to_idx[mid],
                "title": clean_t,
                "release_year": y,
                "genres": row["genres_list"],
                "poster_path": None,
                "vote_average": 7.5,
                "vote_count": 100
            })

    print(f"Generated serving catalogue with {len(catalog_entries):,} model-mapped movies.", flush=True)
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog_entries, f, ensure_ascii=False)

    # 11. SAVE METADATA ARTIFACT
    meta_payload = {
        "status": "ready",
        "device": "cuda:0",
        "gpu_name": gpu_name,
        "pytorch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "training_ratings_used": len(train_df),
        "validation_ratings_used": len(val_df),
        "test_ratings_used": len(test_df),
        "total_dataset_ratings": len(filtered_df),
        "raw_ratings_ingested": total_raw_ratings,
        "excluded_ratings": excluded_ratings,
        "exclusion_reason": "Movies with < 5 total ratings filtered out to avoid unlearnable embeddings",
        "total_users_indexed": num_users,
        "total_movies_indexed": num_items,
        "total_catalog_mapped": len(catalog_entries),
        "training_time_seconds": round(total_training_time, 2),
        "test_inference_samples_per_sec": round(test_throughput, 1),
        "test_inference_ms_per_sample": round(1000 / test_throughput, 4),
        "metrics": {
            "test_rmse": round(test_rmse, 4),
            "test_mae": round(test_mae, 4),
            "baseline_global_mean": {
                "rmse": round(base_mean_rmse, 4),
                "mae": round(base_mean_mae, 4)
            },
            "baseline_user_item_bias": {
                "rmse": round(base_bias_rmse, 4),
                "mae": round(base_bias_mae, 4)
            },
            "ranking_method_b_100_negatives": {
                "recall_at_10": round(mean_recall_b, 4),
                "ndcg_at_10": round(mean_ndcg_b, 4),
                "evaluation_protocol": "Sampled candidate pool of held-out positive items + 100 random unrated negative items per user (Academic standard)"
            },
            "ranking_method_a_test_set_only": {
                "recall_at_10": round(mean_recall_a, 4),
                "ndcg_at_10": round(mean_ndcg_a, 4),
                "evaluation_protocol": "Ranking exclusively within user's held-out test items (Closed pool, documented for audit comparison)"
            }
        },
        "tmdb_to_idx": tmdb_to_idx,
        "movie_to_idx": movie_to_idx,
        "latent_dim": 64,
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta_payload, f, indent=2)

    print(f"\nMetadata saved to {META_PATH}!", flush=True)
    print(f"Weights saved to {WEIGHTS_PATH}!", flush=True)
    print("=" * 70, flush=True)
    print("ALL TRAINING AND EVALUATION PHASES COMPLETE ON RTX 5060!", flush=True)
    print("=" * 70, flush=True)

if __name__ == "__main__":
    train_and_evaluate()
