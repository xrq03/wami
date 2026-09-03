# WAMI Paper-Strict Training Run

- Data: `data\injecagent_wami.jsonl`
- Samples used: `8`
- Model: 4-layer Transformer Encoder, dim=1024, hidden=1024, heads=8
- MINE: 3-layer MLP with ReLU
- Optimizer: AdamW, lr=2e-4, cosine annealing
- Batch size: `4`
- Epochs: `1`
- Tau init: `0.15`
- Calibrated tau: `-1.8500`

| Metric | Value |
|---|---:|
| IR | 0.0% |
| FPR | 0.0% |
| ACC | 100.0% |
| N | 8 |

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 1.8389 | 0.0052 | 0.0072 | 2.2630 |
