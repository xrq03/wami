# Commitment Clearing Round 5: Paper-Strict WAMI Code Path

This round starts converting WAMI itself from method-level reproduction to the
final-paper strict implementation path.

## Implemented

- `TorchWAMIConfig.paper_strict(...)`
  - dim = 1024
  - hidden_dim = 1024
  - Transformer layers = 4
  - attention heads = 8
  - learning rate = 2e-4
- MINE estimator uses a 3-linear-layer MLP with ReLU activations.
- `train_shadow_torch(...)` now supports:
  - batch size 64 by default
  - AdamW
  - optional cosine annealing schedule
- `wami/paper_calibration.py`
  - tau initialized at 0.15
  - greedy validation calibration
- `scripts/train_wami_paper_strict.py`
  - paper-strict training entry point
- `scripts/profile_wami_paper_latency.py`
  - TDG / world model / MINE / total latency breakdown
- `scripts/run_wami_paper_strict_ablation.py`
  - Table-5-shaped ablation entry point for torch WAMI

## Smoke Run

Command:

```text
uv run --with numpy --with torch python scripts\train_wami_paper_strict.py --data data\injecagent_wami.jsonl --limit 8 --epochs 1 --batch-size 4 --device cpu --save wami_paper_strict_smoke_e1.pt --output-md data\wami_paper_strict_smoke.md --output-csv data\wami_paper_strict_smoke.csv
```

Result:

```text
calibrated_tau=-1.8500
IR=0.000 FPR=0.000 ACC=1.000 total=8
```

The smoke result is not a paper metric. It only verifies that the paper-sized
torch model can instantiate, train, save, calibrate, and evaluate.

## Latency Smoke

Command:

```text
uv run --with numpy --with torch python scripts\profile_wami_paper_latency.py --data data\injecagent_wami.jsonl --model wami_paper_strict_smoke_e1.pt --limit 5 --output-md data\wami_paper_latency_breakdown_smoke.md --output-csv data\wami_paper_latency_breakdown_smoke.csv
```

Result on CPU:

| TDG ms | World ms | MINE ms | Total ms |
|---:|---:|---:|---:|
| 0.096 | 28.399 | 3.092 | 33.444 |

This is CPU smoke evidence, not the paper's A100 latency claim.

## Remaining For Strict Paper Numbers

- Run full 20-epoch training on InjecAgent/BIPIA with paper config.
- Run 30-epoch dynamics for Figure 8.
- Run Table 5 ablation with the full trained torch model.
- Run latency and VRAM on CUDA hardware.
- Connect Qwen-VL-Max as the main agent backbone for final Table 1/2/3 runs.
