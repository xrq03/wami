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
- Epochs: `4`
- Evaluation skipped: `true`

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 2.8905 | 0.8007 | 1.7275 | 3.6895 |
| 2 | 1.4737 | 2.3815 | 4.6691 | 2.9595 |
| 3 | 1.2321 | 2.8136 | 5.5080 | 2.4997 |
| 4 | 1.1002 | 3.2006 | 6.0941 | 2.3379 |
