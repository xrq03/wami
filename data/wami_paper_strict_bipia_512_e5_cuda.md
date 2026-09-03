# WAMI Paper-Strict Training Run

- Data mode: `single data file split internally; smoke/in-sample mode`
- Train data: `data\bipia_wami.jsonl`
- Validation data: `internal split`
- Test data: `data\bipia_wami.jsonl`
- Train samples: `409`
- Validation samples: `103`
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
- Epochs: `5`
- Tau init: `0.15`
- Calibrated tau: `-1.8500`

## Evaluation Results

| Eval Set | IR | FPR | ACC | N |
|---|---:|---:|---:|---:|
| bipia_wami | 100.0% | 0.0% | 100.0% | 512 |

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 4.2655 | 0.3032 | 0.4686 | 4.3106 |
| 2 | 2.6214 | 1.2875 | 2.8437 | 3.6672 |
| 3 | 2.3161 | 1.6215 | 3.6769 | 3.4252 |
| 4 | 2.0895 | 1.9947 | 3.7204 | 3.2298 |
| 5 | 2.0108 | 2.1257 | 3.8587 | 3.1360 |
