# WAMI Paper-Strict Training Run

- Data mode: `single data file split internally; smoke/in-sample mode`
- Train data: `data\injecagent_wami.jsonl`
- Validation data: `internal split`
- Test data: `data\injecagent_wami.jsonl`
- Train samples: `51`
- Validation samples: `13`
- Model: 4-layer Transformer Encoder, dim=1024, hidden=1024, heads=8
- MINE: 3-layer MLP with ReLU
- Optimizer: AdamW, lr=2e-4, cosine annealing
- Batch size: `16`
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
- Epochs: `1`
- Tau init: `0.15`
- Calibrated tau: `-1.8500`

## Evaluation Results

| Eval Set | IR | FPR | ACC | N |
|---|---:|---:|---:|---:|
| injecagent_wami | 100.0% | 0.0% | 100.0% | 64 |

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 4.4284 | 0.1728 | 0.2010 | 3.1658 |
