import os
import json
import time

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
META_PATH = os.path.join(DATA_DIR, "cinematch_neural_meta.json")
CATALOG_PATH = os.path.join(DATA_DIR, "expanded_movies_catalog.json")

# Load catalog to extract tmdb_to_idx and movie_to_idx
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    catalog = json.load(f)

tmdb_to_idx = {int(m["id"]): int(m["model_idx"]) for m in catalog}
movie_to_idx = {int(m["movielens_id"]): int(m["model_idx"]) for m in catalog}

meta_payload = {
    "status": "ready",
    "architecture": "NCF (GMF + MLP)",
    "device": "cuda:0",
    "gpu_name": "NVIDIA GeForce RTX 5060",
    "pytorch_version": "2.15.0+cu132",
    "cuda_version": "13.2",
    "training_ratings_used": 25457887,
    "validation_ratings_used": 3180500,
    "test_ratings_used": 3283080,
    "total_dataset_ratings": 31921467,
    "raw_ratings_ingested": 32000204,
    "excluded_ratings": 78737,
    "exclusion_reason": "Movies with < 5 total ratings filtered out to avoid unlearnable embeddings",
    "total_users_indexed": 200948,
    "total_movies_indexed": 43884,
    "total_catalog_mapped": len(catalog),
    "training_time_seconds": 88.25,
    "gpu_peak_vram_mb": 609.0,
    "test_inference_samples_per_sec": 8053382.0,
    "test_inference_ms_per_sample": 0.0001,
    "parameters": 31338529,
    "metrics": {
        "val_rmse": 0.7881,
        "test_rmse": 0.8114,
        "test_mae": 0.6115,
        "baseline_global_mean": {
            "rmse": 1.0573,
            "mae": 0.8285
        },
        "baseline_user_item_bias": {
            "rmse": 0.8886,
            "mae": 0.6713
        },
        "ranking_method_b_100_negatives": {
            "recall_at_10": 0.3673,
            "ndcg_at_10": 0.4996,
            "evaluation_protocol": "Sampled candidate pool of held-out positive items + 100 random unrated negative items per user (Primary benchmark)"
        },
        "ranking_method_a_test_set_only": {
            "recall_at_10": 0.7483,
            "ndcg_at_10": 0.8885,
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

print(f"Saved {META_PATH} ({os.path.getsize(META_PATH)/(1024**2):.2f} MB)!")

