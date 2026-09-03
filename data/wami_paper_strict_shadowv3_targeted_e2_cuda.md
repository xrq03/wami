# WAMI Paper-Strict Training Run

- Data mode: `separate train/validation/test files`
- Train data: `data\shadow_v3_train_3500_targeted_seed20260522.jsonl`
- Validation data: `data\shadow_v3_val_900_targeted_seed20260523.jsonl`
- Train samples: `3500`
- Validation samples: `900`
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
- Epochs: `2`
- Evaluation skipped: `true`

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 2.6332 | 1.5327 | 3.5451 | 4.1753 |
| 2 | 1.3608 | 2.9278 | 5.9440 | 2.9872 |
