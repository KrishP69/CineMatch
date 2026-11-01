"""
Independent Forensic Recalculation of Model Evaluation Metrics
Loads saved model weights directly from disk without retraining.
Evaluates on untouched test data split.
"""

import os
import json
import math
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ML32M_DIR = os.path.join(DATA_DIR, "movielens", "ml-32m")
WEIGHTS_PATH = os.path.join(DATA_DIR, "cinematch_neural_weights.pt")
META_PATH = os.path.join(DATA_DIR, "cinematch_neural_meta.json")

class RecommenderDataset(Dataset):
    def __init__(self, u, m, r):
        self.u = torch.tensor(u, dtype=torch.long)
        self.m = torch.tensor(m, dtype=torch.long)
        self.r = torch.tensor(r, dtype=torch.float32)

    def __len__(self):
        return len(self.u)

    def __getitem__(self, idx):
        return self.u[idx], self.m[idx], self.r[idx]

class NeuralNCF(nn.Module):
    def __init__(self, n_users, n_items, latent_dim=64):
        super().__init__()
        self.user_embed_gmf = nn.Embedding(n_users, latent_dim)
        self.item_embed_gmf = nn.Embedding(n_items, latent_dim)
        self.user_embed_mlp = nn.Embedding(n_users, latent_dim)
        self.item_embed_mlp = nn.Embedding(n_items, latent_dim)
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
        self.out = nn.Linear(latent_dim + 32, 1)

    def forward(self, u, m):
        gmf_out = self.user_embed_gmf(u) * self.item_embed_gmf(m)
        mlp_in = torch.cat([self.user_embed_mlp(u), self.item_embed_mlp(m)], dim=-1)
        mlp_out = self.mlp(mlp_in)
        fusion = torch.cat([gmf_out, mlp_out], dim=-1)
        return self.out(fusion).squeeze(-1)

def run_independent_eval():
    print("=" * 65)
    print("INDEPENDENT FORENSIC RECALCULATION SUITE")
    print("=" * 65)

    if not os.path.exists(WEIGHTS_PATH) or not os.path.exists(META_PATH):
        print(f"[FAIL] Missing model weights ({WEIGHTS_PATH}) or meta ({META_PATH})")
        return

    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    n_users = meta.get("total_users_indexed") or meta.get("num_users", 9518)
    n_items = meta.get("total_movies_indexed") or meta.get("num_movies", 33007)
    latent_dim = meta.get("latent_dim", 64)

    print(f"Meta report: Users={n_users:,}, Items={n_items:,}, LatentDim={latent_dim}")
    print(f"Reported Test RMSE: {meta['evaluation']['neural_ncf']['test_rmse']}")
    print(f"Reported Test MAE:  {meta['evaluation']['neural_ncf']['test_mae']}")
    print(f"Reported Recall@10: {meta['evaluation']['neural_ncf']['recall_at_10']}")
    print(f"Reported NDCG@10:   {meta['evaluation']['neural_ncf']['ndcg_at_10']}")

    # 1. Load Model
    model = NeuralNCF(n_users, n_items, latent_dim=latent_dim)
    model.load_state_dict(torch.load(WEIGHTS_PATH, map_location="cpu"))
    model.eval()
    print("\n[OK] Loaded PyTorch model state_dict successfully from disk.")

    # 2. Re-create exact test split
    ratings_path = os.path.join(ML32M_DIR, "ratings.csv")
    print(f"Reading ratings from: {ratings_path} (1.5M rows)")
    ratings_df = pd.read_csv(ratings_path, nrows=1500000)

    unique_users = ratings_df["userId"].unique()
    unique_movies = ratings_df["movieId"].unique()
    user_to_idx = {uid: i for i, uid in enumerate(unique_users)}
    movie_to_idx = {mid: i for i, mid in enumerate(unique_movies)}

    ratings_df = ratings_df.sort_values(by=["userId", "timestamp"]).reset_index(drop=True)
    ratings_df["u_idx"] = ratings_df["userId"].map(user_to_idx)
    ratings_df["m_idx"] = ratings_df["movieId"].map(movie_to_idx)

    user_counts = ratings_df.groupby("userId")["timestamp"].transform("count")
    user_cumcounts = ratings_df.groupby("userId").cumcount()
    ratings_df["user_rank"] = (user_cumcounts + 1) / user_counts

    test_df = ratings_df[ratings_df["user_rank"] > 0.90].copy()
    print(f"Test split size: {len(test_df):,} ratings ({len(test_df)/len(ratings_df)*100:.1f}%)")

    test_ds = RecommenderDataset(test_df["u_idx"].values, test_df["m_idx"].values, test_df["rating"].values)
    test_loader = DataLoader(test_ds, batch_size=4096, shuffle=False)

    # 3. Independent RMSE and MAE calculation
    criterion = nn.MSELoss()
    total_loss = 0.0
    total_mae = 0.0
    all_preds = []
    all_actuals = []

    with torch.no_grad():
        for u_b, m_b, r_b in test_loader:
            preds = model(u_b, m_b)
            total_loss += criterion(preds, r_b).item() * len(r_b)
            total_mae += torch.sum(torch.abs(preds - r_b)).item()
            all_preds.extend(preds.numpy())
            all_actuals.extend(r_b.numpy())

    recalc_rmse = math.sqrt(total_loss / len(test_ds))
    recalc_mae = total_mae / len(test_ds)

    print("\n" + "-" * 50)
    print("INDEPENDENT METRIC RECALCULATION:")
    print("-" * 50)
    print(f"Recalculated Test RMSE: {recalc_rmse:.4f} (Reported: {meta['evaluation']['neural_ncf']['test_rmse']})")
    print(f"Recalculated Test MAE:  {recalc_mae:.4f} (Reported: {meta['evaluation']['neural_ncf']['test_mae']})")

    rmse_match = abs(recalc_rmse - meta['evaluation']['neural_ncf']['test_rmse']) < 0.005
    mae_match = abs(recalc_mae - meta['evaluation']['neural_ncf']['test_mae']) < 0.005
    print(f"RMSE Match: {'PASS' if rmse_match else 'FAIL'}")
    print(f"MAE Match:  {'PASS' if mae_match else 'FAIL'}")

    # 4. Independent Ranking Recalculation (Method A: test candidate set as in training script)
    test_dict = {}
    for _, row in test_df.iterrows():
        u = int(row["u_idx"])
        m = int(row["m_idx"])
        r = float(row["rating"])
        if u not in test_dict:
            test_dict[u] = {}
        test_dict[u][m] = r

    def eval_ranking_method_a(k=10, pos_thresh=3.5, max_users=500):
        recalls, ndcgs = [], []
        eval_users = list(test_dict.keys())[:max_users]
        for u in eval_users:
            user_items = test_dict[u]
            positives = {m for m, r in user_items.items() if r >= pos_thresh}
            if not positives or len(user_items) < k:
                continue
            candidates = list(user_items.keys())
            with torch.no_grad():
                u_t = torch.full((len(candidates),), u, dtype=torch.long)
                m_t = torch.tensor(candidates, dtype=torch.long)
                scores = model(u_t, m_t).numpy()
            ranked_idx = np.argsort(scores)[::-1]
            top_k = [candidates[i] for i in ranked_idx[:k]]

            hits = len(set(top_k) & positives)
            recalls.append(hits / len(positives))

            dcg = sum(1.0 / math.log2(rank + 2) for rank, m in enumerate(top_k) if m in positives)
            idcg = sum(1.0 / math.log2(rank + 2) for rank in range(min(len(positives), k)))
            ndcgs.append(dcg / idcg if idcg > 0 else 0.0)
        return float(np.mean(recalls)), float(np.mean(ndcgs))

    recall_a, ndcg_a = eval_ranking_method_a()
    print(f"\nRecalculated Recall@10 (Method A): {recall_a:.4f} (Reported: {meta['evaluation']['neural_ncf']['recall_at_10']})")
    print(f"Recalculated NDCG@10   (Method A): {ndcg_a:.4f} (Reported: {meta['evaluation']['neural_ncf']['ndcg_at_10']})")

    ranking_match = abs(recall_a - meta['evaluation']['neural_ncf']['recall_at_10']) < 0.02 and abs(ndcg_a - meta['evaluation']['neural_ncf']['ndcg_at_10']) < 0.02
    print(f"Ranking Match: {'PASS' if ranking_match else 'FAIL'}")

    # 5. Method B: Standard 100 Negative Unrated Sample Protocol
    print("\nEvaluating under Standard RecSys Protocol (1 Positive Test Item vs 100 Random Unrated Items)...")
    np.random.seed(42)
    recalls_std, ndcgs_std = [], []
    eval_users_std = list(test_dict.keys())[:500]

    for u in eval_users_std:
        user_items = test_dict[u]
        positives = [m for m, r in user_items.items() if r >= 3.5]
        if not positives:
            continue
        target_positive = positives[0]

        # Sample 100 negative unrated items
        rated_items = set(user_items.keys())
        negatives = []
        while len(negatives) < 100:
            rand_item = np.random.randint(0, n_items)
            if rand_item not in rated_items and rand_item not in negatives:
                negatives.append(rand_item)

        eval_candidates = [target_positive] + negatives
        with torch.no_grad():
            u_t = torch.full((len(eval_candidates),), u, dtype=torch.long)
            m_t = torch.tensor(eval_candidates, dtype=torch.long)
            scores = model(u_t, m_t).numpy()

        ranked_indices = np.argsort(scores)[::-1]
        top_10 = [eval_candidates[i] for i in ranked_indices[:10]]

        if target_positive in top_10:
            recalls_std.append(1.0)
            rank = top_10.index(target_positive)
            ndcgs_std.append(1.0 / math.log2(rank + 2))
        else:
            recalls_std.append(0.0)
            ndcgs_std.append(0.0)

    recall_std_mean = float(np.mean(recalls_std))
    ndcg_std_mean = float(np.mean(ndcgs_std))
    print(f"Standard 100-negative protocol: Recall@10 = {recall_std_mean:.4f} | NDCG@10 = {ndcg_std_mean:.4f}")
    print("=" * 65)

if __name__ == "__main__":
    run_independent_eval()

