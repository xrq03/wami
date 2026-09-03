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
- Epochs: `4`
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
| 2 | 0.9493 | 2.9048 | 5.9578 | 2.7363 |
| 3 | 0.8188 | 3.5924 | 6.9303 | 2.5829 |
| 4 | 0.7563 | 4.1001 | 7.5969 | 2.5281 |
