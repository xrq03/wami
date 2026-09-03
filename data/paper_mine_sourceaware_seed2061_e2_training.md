# WAMI Paper-Strict Training Run

- Data mode: `separate train/validation/test files`
- Train data: `.\data\paper_shadow_train_sourceaware_seed2061.jsonl`
- Validation data: `.\data\paper_shadow_val_sourceaware_seed2061.jsonl`
- Train samples: `960`
- Validation samples: `240`
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
- Transition MINE weight: `0.35`
- Source-aware auxiliary weight: `0.25`
- Epochs: `2`
- Evaluation skipped: `true`

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 3.2170 | 0.8743 | 1.9625 | 3.8218 |
| 2 | 1.6041 | 2.4690 | 4.7216 | 3.0765 |
