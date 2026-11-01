"""
Forensic Latency & Inference Benchmark
Measures batch throughput, single-sample latency, warmup, and end-to-end preprocessing.
"""

import os
import time
import json
import torch
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
WEIGHTS_PATH = os.path.join(DATA_DIR, "cinematch_neural_weights.pt")
META_PATH = os.path.join(DATA_DIR, "cinematch_neural_meta.json")

def benchmark_latency():
    print("=" * 65)
    print("FORENSIC INFERENCE LATENCY BENCHMARK")
    print("=" * 65)

    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    n_users = meta.get("total_users_indexed") or meta.get("num_users", 9518)
    n_items = meta.get("total_movies_indexed") or meta.get("num_movies", 33007)
    latent_dim = meta.get("latent_dim", 64)

    # 1. Load Model
    from independent_eval import NeuralNCF
    model = NeuralNCF(n_users, n_items, latent_dim=latent_dim)
    model.load_state_dict(torch.load(WEIGHTS_PATH, map_location="cpu"))
    model.eval()

    # TEST A: Batch Throughput (Batch Size = 4096)
    print("\n[TEST A] Batch Throughput (batch_size = 4096)...")
    u_batch = torch.randint(0, n_users, (4096,))
    m_batch = torch.randint(0, n_items, (4096,))

    # Warmup
    for _ in range(5):
        _ = model(u_batch, m_batch)

    # Timed runs
    iterations = 20
    t0 = time.time()
    for _ in range(iterations):
        _ = model(u_batch, m_batch)
    batch_total_sec = time.time() - t0
    total_samples = 4096 * iterations
    ms_per_sample_batch = (batch_total_sec * 1000) / total_samples

    print(f"  Total samples evaluated: {total_samples:,}")
    print(f"  Total time:              {batch_total_sec:.4f} s")
    print(f"  Throughput:              {total_samples / batch_total_sec:,.0f} samples/sec")
    print(f"  Batch Latency per Sample: {ms_per_sample_batch:.4f} ms/sample")
    print(f"  Reported in training script: {meta['evaluation']['neural_ncf']['avg_inference_ms']} ms/sample")

    # TEST B: Single-Sample Latency (Batch Size = 1)
    print("\n[TEST B] Single-Sample Latency (batch_size = 1)...")
    u_single = torch.tensor([12], dtype=torch.long)
    m_single = torch.tensor([45], dtype=torch.long)

    # Warmup
    for _ in range(20):
        _ = model(u_single, m_single)

    single_times = []
    for _ in range(200):
        t_start = time.perf_counter()
        _ = model(u_single, m_single)
        single_times.append((time.perf_counter() - t_start) * 1000)

    print(f"  Mean single-sample latency:   {np.mean(single_times):.4f} ms")
    print(f"  Median single-sample latency: {np.median(single_times):.4f} ms")
    print(f"  p95 single-sample latency:    {np.percentile(single_times, 95):.4f} ms")

    # TEST C: End-to-End Service Latency (with TMDB ID mapping & candidate ranking)
    print("\n[TEST C] End-to-End Service Latency (84 Catalog Movies)...")
    from neural_recommender import neural_service
    from movie_service import movie_service

    # Warmup
    _ = neural_service.predict_user_catalog_affinities([157336], movie_service.movies[:10])

    e2e_times = []
    for _ in range(50):
        t_start = time.perf_counter()
        _ = neural_service.predict_user_catalog_affinities([157336, 27205], movie_service.movies, exclude_ids=[155])
        e2e_times.append((time.perf_counter() - t_start) * 1000)

    print(f"  Mean End-to-End Latency:   {np.mean(e2e_times):.2f} ms")
    print(f"  Median End-to-End Latency: {np.median(e2e_times):.2f} ms")
    print(f"  p95 End-to-End Latency:    {np.percentile(e2e_times, 95):.2f} ms")
    print("=" * 65)

if __name__ == "__main__":
    benchmark_latency()

