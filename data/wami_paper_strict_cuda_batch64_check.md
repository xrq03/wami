# WAMI Paper-Strict Training Run

- Data: `data\injecagent_wami.jsonl`
- Samples used: `128`
- Model: 4-layer Transformer Encoder, dim=1024, hidden=1024, heads=8
- MINE: 3-layer MLP with ReLU
- Optimizer: AdamW, lr=2e-4, cosine annealing
- Batch size: `64`
- Epochs: `1`
- Tau init: `0.15`
- Calibrated tau: `-1.8500`

| Metric | Value |
|---|---:|
| IR | 96.4% |
| FPR | 0.0% |
| ACC | 98.4% |
| N | 128 |

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 2.4626 | -0.0004 | 0.0014 | 5.3583 |
