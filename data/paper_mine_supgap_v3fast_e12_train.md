# WAMI Paper-Strict Training Run

- Data mode: `separate train/validation/test files`
- Train data: `data\paper_shadow_train_v3_fast.jsonl`
- Validation data: `data\paper_shadow_val_v3_fast.jsonl`
- Test data: `data\paper_shadow_val_v3_fast.jsonl`
- Train samples: `2400`
- Validation samples: `600`
- Model: 4-layer Transformer Encoder, dim=1024, hidden=1024, heads=8
- MINE: 3-layer MLP with ReLU
- Optimizer: AdamW, lr=2e-4, cosine annealing
- Batch size: `64`
- Labeled attack negatives: `True`
- Benign positive weight: `2.0`
- Supervised gap weight: `0.5`
- Supervised margin: `1.5`
- Epochs: `12`
- Tau init: `0.15`
- Calibrated tau: `-1.8500`

## Evaluation Results

| Eval Set | IR | FPR | ACC | N |
|---|---:|---:|---:|---:|
| paper_shadow_val_v3_fast | 100.0% | 5.9% | 97.0% | 600 |

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 2.1777 | 1.1733 | 2.9042 | 3.8010 |
| 2 | 0.9506 | 2.9196 | 6.0224 | 2.7365 |
| 3 | 0.8155 | 3.7433 | 7.1199 | 2.5948 |
| 4 | 0.7714 | 4.7048 | 8.4092 | 2.5832 |
| 5 | 0.7941 | 4.5359 | 8.4411 | 2.6123 |
| 6 | 0.7247 | 5.0104 | 8.4082 | 2.5268 |
| 7 | 0.6581 | 5.5742 | 8.7949 | 2.4434 |
| 8 | 0.6908 | 5.4576 | 8.7855 | 2.4779 |
| 9 | 0.6632 | 5.6258 | 8.8349 | 2.4631 |
| 10 | 0.6461 | 5.7872 | 8.9397 | 2.4344 |
| 11 | 0.6683 | 5.6326 | 8.9119 | 2.4397 |
| 12 | 0.6632 | 5.6629 | 8.8214 | 2.4197 |
