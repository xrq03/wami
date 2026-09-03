# WAMI Paper-Strict Training Run

- Data: `data\injecagent_wami.jsonl`
- Samples used: `512`
- Model: 4-layer Transformer Encoder, dim=1024, hidden=1024, heads=8
- MINE: 3-layer MLP with ReLU
- Optimizer: AdamW, lr=2e-4, cosine annealing
- Batch size: `64`
- Epochs: `1`
- Tau init: `0.15`
- Calibrated tau: `-0.1000`

| Metric | Value |
|---|---:|
| IR | 100.0% |
| FPR | 0.0% |
| ACC | 100.0% |
| N | 512 |

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 2.0872 | 0.0904 | 0.0971 | 3.6928 |
