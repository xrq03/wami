# WAMI Paper-Strict Training Run

- Data mode: `separate train/validation/test files`
- Train data: `data\paper_shadow_train_v2_fast.jsonl`
- Validation data: `data\paper_shadow_val_v2_fast.jsonl`
- Test data: `data\paper_shadow_val_v2_fast.jsonl`
- Train samples: `2400`
- Validation samples: `600`
- Model: 4-layer Transformer Encoder, dim=1024, hidden=1024, heads=8
- MINE: 3-layer MLP with ReLU
- Optimizer: AdamW, lr=2e-4, cosine annealing
- Batch size: `64`
- Epochs: `8`
- Tau init: `0.15`
- Calibrated tau: `-1.8500`

## Evaluation Results

| Eval Set | IR | FPR | ACC | N |
|---|---:|---:|---:|---:|
| paper_shadow_val_v2_fast | 100.0% | 7.7% | 96.2% | 600 |

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 1.5892 | 0.9550 | 2.0425 | 3.3185 |
| 2 | 0.8486 | 2.5956 | 4.8747 | 2.6829 |
| 3 | 0.7544 | 3.2583 | 5.8143 | 2.6326 |
| 4 | 0.7544 | 3.7820 | 6.3769 | 2.5946 |
| 5 | 0.6723 | 4.6012 | 7.1776 | 2.5670 |
| 6 | 0.6303 | 4.9906 | 7.4801 | 2.5436 |
| 7 | 0.6411 | 5.1198 | 7.5314 | 2.5155 |
| 8 | 0.6326 | 5.1926 | 7.4621 | 2.5206 |
