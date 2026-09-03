# WAMI Paper-Strict Training Run

- Data mode: `separate train/validation/test files`
- Train data: `.\data\paper_shadow_train_paired_v1_fast.jsonl`
- Validation data: `.\data\paper_shadow_val_paired_v1_fast.jsonl`
- Train samples: `1280`
- Validation samples: `320`
- Model: 4-layer Transformer Encoder, dim=1024, hidden=1024, heads=8
- MINE: 3-layer MLP with ReLU
- Optimizer: AdamW, lr=2e-4, cosine annealing
- Batch size: `32`
- Labeled attack negatives: `True`
- Benign positive weight: `1.9`
- Supervised gap weight: `0.25`
- Supervised margin: `1.0`
- Pairwise ranking weight: `0.35`
- Pairwise ranking margin: `1.25`
- Attack recall weight: `0.15`
- Attack target score: `-3.0`
- Epochs: `4`
- Evaluation skipped: `true`

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 2.5121 | 1.1827 | 2.6509 | 3.6774 |
| 2 | 1.3897 | 2.7241 | 5.3459 | 3.0432 |
| 3 | 1.2453 | 3.0917 | 5.9433 | 2.7464 |
| 4 | 1.1703 | 3.4204 | 6.3684 | 2.6731 |
