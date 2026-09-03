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
- Labeled attack negatives: `True`
- Benign positive weight: `2.0`
- Epochs: `4`
- Tau init: `0.15`
- Calibrated tau: `-1.8500`

## Evaluation Results

| Eval Set | IR | FPR | ACC | N |
|---|---:|---:|---:|---:|
| paper_shadow_val_v2_fast | 100.0% | 7.7% | 96.2% | 600 |

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 1.8492 | 1.2308 | 2.6032 | 3.4447 |
| 2 | 0.8911 | 2.9300 | 5.7225 | 2.7281 |
| 3 | 0.7770 | 3.5481 | 6.6285 | 2.6673 |
| 4 | 0.7067 | 4.0230 | 7.1974 | 2.6082 |
