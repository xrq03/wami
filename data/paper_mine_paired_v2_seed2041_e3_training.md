# WAMI Paper-Strict Training Run

- Data mode: `separate train/validation/test files`
- Train data: `.\data\paper_shadow_train_paired_v2_seed2041.jsonl`
- Validation data: `.\data\paper_shadow_val_paired_v2_seed2041.jsonl`
- Train samples: `1280`
- Validation samples: `320`
- Model: 4-layer Transformer Encoder, dim=1024, hidden=1024, heads=8
- MINE: 3-layer MLP with ReLU
- Optimizer: AdamW, lr=2e-4, cosine annealing
- Batch size: `32`
- Labeled attack negatives: `True`
- Benign positive weight: `2.0`
- Supervised gap weight: `0.35`
- Supervised margin: `1.25`
- Pairwise ranking weight: `0.45`
- Pairwise ranking margin: `1.5`
- Attack recall weight: `0.0`
- Attack target score: `-3.5`
- Epochs: `3`
- Evaluation skipped: `true`

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 2.5045 | 1.1158 | 2.3551 | 3.7216 |
| 2 | 1.2691 | 2.5748 | 5.1793 | 2.6978 |
| 3 | 1.0866 | 3.1700 | 6.0242 | 2.4259 |
