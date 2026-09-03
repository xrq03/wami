# WAMI Paper-Strict Training Run

- Data mode: `separate train/validation/test files`
- Train data: `data\paper_shadow_train.jsonl`
- Validation data: `data\paper_shadow_val.jsonl`
- Test data: `data\injecagent_wami.jsonl, data\bipia_wami.jsonl, data\agentdojo_wami.jsonl`
- Train samples: `64`
- Validation samples: `16`
- Model: 4-layer Transformer Encoder, dim=1024, hidden=1024, heads=8
- MINE: 3-layer MLP with ReLU
- Optimizer: AdamW, lr=2e-4, cosine annealing
- Batch size: `32`
- Epochs: `1`
- Tau init: `0.15`
- Calibrated tau: `-1.8500`

## Evaluation Results

| Eval Set | IR | FPR | ACC | N |
|---|---:|---:|---:|---:|
| injecagent_wami | 100.0% | 0.0% | 100.0% | 64 |
| bipia_wami | 100.0% | 0.0% | 100.0% | 64 |
| agentdojo_wami | 100.0% | 0.0% | 100.0% | 64 |

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 2.3542 | 0.0027 | 0.0048 | 4.8218 |
