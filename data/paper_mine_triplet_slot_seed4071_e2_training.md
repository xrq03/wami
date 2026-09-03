# WAMI Paper-Strict Training Run

- Data mode: `separate train/validation/test files`
- Train data: `.\data\paper_shadow_train_triplet_seed4071.jsonl`
- Validation data: `.\data\paper_shadow_val_triplet_seed4071.jsonl`
- Train samples: `1440`
- Validation samples: `360`
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
- Provenance memory weight: `0.12`
- Slot-specific weight: `0.12`
- Subgoal contrastive weight: `0.15`
- Epochs: `2`
- Evaluation skipped: `true`

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 2.6001 | 1.4164 | 2.8639 | 3.8416 |
| 2 | 1.4729 | 2.6574 | 5.0469 | 3.0012 |
