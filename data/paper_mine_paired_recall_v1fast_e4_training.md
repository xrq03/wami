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
- Benign positive weight: `1.6`
- Supervised gap weight: `0.25`
- Supervised margin: `1.0`
- Pairwise ranking weight: `0.3`
- Pairwise ranking margin: `1.2`
- Attack recall weight: `0.45`
- Attack target score: `-3.5`
- Epochs: `4`
- Evaluation skipped: `true`

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 2.9433 | 1.0819 | 3.0723 | 3.8100 |
| 2 | 1.6074 | 2.7716 | 5.5606 | 3.1827 |
| 3 | 1.4705 | 3.2397 | 6.0729 | 2.8917 |
| 4 | 1.4043 | 3.4700 | 6.2822 | 2.7688 |
