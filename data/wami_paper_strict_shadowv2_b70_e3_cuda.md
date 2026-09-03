# WAMI Paper-Strict Training Run

- Data mode: `separate train/validation/test files`
- Train data: `data\shadow_v2_train_3000_b70_seed20260520.jsonl`
- Validation data: `data\shadow_v2_val_800_b70_seed20260521.jsonl`
- Train samples: `3000`
- Validation samples: `800`
- Model: 4-layer Transformer Encoder, dim=1024, hidden=1024, heads=8
- MINE: 3-layer MLP with ReLU
- Optimizer: AdamW, lr=2e-4, cosine annealing
- Batch size: `64`
- Labeled attack negatives: `True`
- Benign positive weight: `1.5`
- Supervised gap weight: `0.25`
- Supervised margin: `1.0`
- Pairwise ranking weight: `0.35`
- Pairwise ranking margin: `1.25`
- Attack recall weight: `0.2`
- Attack target score: `-3.5`
- Transition MINE weight: `0.25`
- Source-aware auxiliary weight: `0.2`
- Provenance memory weight: `0.15`
- Slot-specific weight: `0.15`
- Subgoal contrastive weight: `0.15`
- Epochs: `3`
- Evaluation skipped: `true`

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 2.3811 | 1.8692 | 4.0303 | 3.8398 |
| 2 | 1.3595 | 3.2857 | 6.2132 | 2.8645 |
| 3 | 1.2179 | 3.9418 | 6.8128 | 2.6646 |
