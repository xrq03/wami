# WAMI Paper-Strict Training Run

- Data mode: `separate train/validation/test files`
- Train data: `.\data\paper_shadow_train_sourceaware_seed2061.jsonl`
- Validation data: `.\data\paper_shadow_val_sourceaware_seed2061.jsonl`
- Train samples: `128`
- Validation samples: `32`
- Model: 4-layer Transformer Encoder, dim=1024, hidden=1024, heads=8
- MINE: 3-layer MLP with ReLU
- Optimizer: AdamW, lr=2e-4, cosine annealing
- Batch size: `16`
- Labeled attack negatives: `True`
- Benign positive weight: `1.7`
- Supervised gap weight: `0.3`
- Supervised margin: `1.15`
- Pairwise ranking weight: `0.4`
- Pairwise ranking margin: `1.35`
- Attack recall weight: `0.0`
- Attack target score: `-3.5`
- Transition MINE weight: `0.3`
- Source-aware auxiliary weight: `0.1`
- Provenance memory weight: `0.15`
- Epochs: `1`
- Evaluation skipped: `true`

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 4.0840 | 0.0899 | 0.2614 | 4.0327 |
