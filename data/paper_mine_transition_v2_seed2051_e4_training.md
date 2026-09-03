# WAMI Paper-Strict Training Run

- Data mode: `separate train/validation/test files`
- Train data: `.\data\paper_shadow_train_transition_v2_seed2051.jsonl`
- Validation data: `.\data\paper_shadow_val_transition_v2_seed2051.jsonl`
- Train samples: `1920`
- Validation samples: `480`
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
- Transition MINE weight: `0.45`
- Epochs: `4`
- Evaluation skipped: `true`

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 2.4766 | 1.5417 | 3.1601 | 3.4510 |
| 2 | 1.3279 | 3.1869 | 6.0714 | 2.5481 |
| 3 | 1.2317 | 3.7008 | 6.8482 | 2.3415 |
| 4 | 1.1765 | 4.1612 | 7.1773 | 2.2489 |
