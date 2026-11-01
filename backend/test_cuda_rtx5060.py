import os
import sys
import time

def verify_cuda():
    print("=" * 60)
    print("CINEMATCH RTX 5060 GPU / CUDA VERIFICATION TEST")
    print("=" * 60)

    import torch
    print(f"PyTorch Version: {torch.__version__}")
    print(f"CUDA Version (torch): {torch.version.cuda}")
    print(f"CUDA Available: {torch.cuda.is_available()}")

    if not torch.cuda.is_available():
        print("ERROR: torch.cuda.is_available() is False!")
        sys.exit(1)

    device_count = torch.cuda.device_count()
    print(f"Device Count: {device_count}")
    
    device_name = torch.cuda.get_device_name(0)
    print(f"Device 0 Name: {device_name}")
    props = torch.cuda.get_device_properties(0)
    total_memory_gb = props.total_memory / (1024 ** 3)
    major, minor = props.major, props.minor
    print(f"Compute Capability: {major}.{minor}")
    print(f"Total VRAM: {total_memory_gb:.2f} GB")

    device = torch.device("cuda:0")

    # Test 1: Real CUDA Matrix Multiplication
    print("\n--- Test 1: Real CUDA Matrix Multiplication ---")
    torch.cuda.reset_peak_memory_stats(device)
    vram_before = torch.cuda.memory_allocated(device) / (1024 ** 2)
    
    N = 4096
    print(f"Allocating two ({N}x{N}) float32 tensors on {device}...")
    t0 = time.time()
    A = torch.randn(N, N, device=device, dtype=torch.float32)
    B = torch.randn(N, N, device=device, dtype=torch.float32)
    torch.cuda.synchronize(device)
    alloc_time = time.time() - t0

    vram_during = torch.cuda.memory_allocated(device) / (1024 ** 2)
    print(f"VRAM Allocated: {vram_during - vram_before:.2f} MB")

    print(f"Executing matrix multiplication (A @ B) on {device}...")
    t0 = time.time()
    C = torch.matmul(A, B)
    torch.cuda.synchronize(device)
    matmul_time = time.time() - t0
    print(f"Matmul Time: {matmul_time * 1000:.2f} ms")
    print(f"Result shape: {C.shape}, device: {C.device}")

    # Test 2: Real Neural Network Forward + Backward + Optimizer Step
    print("\n--- Test 2: Neural Interaction Network (Forward + Backward + Optimizer) ---")
    import torch.nn as nn
    import torch.optim as optim

    class MiniNCF(nn.Module):
        def __init__(self, num_users, num_items, dim=64):
            super().__init__()
            self.u_emb = nn.Embedding(num_users, dim)
            self.i_emb = nn.Embedding(num_items, dim)
            self.mlp = nn.Sequential(
                nn.Linear(dim * 2, 128),
                nn.ReLU(),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.Linear(64, 1)
            )

        def forward(self, u, i):
            ue = self.u_emb(u)
            ie = self.i_emb(i)
            x = torch.cat([ue, ie], dim=-1)
            return self.mlp(x).squeeze(-1)

    model = MiniNCF(10000, 5000, 64).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    batch_users = torch.randint(0, 10000, (4096,), device=device)
    batch_items = torch.randint(0, 5000, (4096,), device=device)
    batch_targets = torch.rand((4096,), device=device, dtype=torch.float32) * 4.0 + 1.0

    print("Executing 5 training steps on CUDA...")
    for step in range(5):
        optimizer.zero_grad()
        preds = model(batch_users, batch_items)
        loss = criterion(preds, batch_targets)
        loss.backward()
        optimizer.step()
        torch.cuda.synchronize(device)
        print(f"  Step {step + 1}: Loss = {loss.item():.4f}, Device = {preds.device}")

    vram_peak = torch.cuda.max_memory_allocated(device) / (1024 ** 2)
    print(f"\nPeak Allocated VRAM during test: {vram_peak:.2f} MB")
    print("CUDA Execution Verification: SUCCESSFUL!")
    print("=" * 60)

if __name__ == "__main__":
    verify_cuda()

