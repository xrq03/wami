# WAMI Paper-Strict Training Run

- Data mode: `single data file split internally; smoke/in-sample mode`
- Train data: `data\agentdojo_wami.jsonl`
- Validation data: `internal split`
- Test data: `data\agentdojo_wami.jsonl`
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
- Calibrated tau: `-1.5000`

## Evaluation Results

| Eval Set | IR | FPR | ACC | N |
|---|---:|---:|---:|---:|
| agentdojo_wami | 92.0% | 0.0% | 93.4% | 512 |

## Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 5.4718 | -0.0049 | -0.0031 | 5.6945 |
| 2 | 5.0647 | 0.0434 | 0.0503 | 5.1010 |
| 3 | 4.7934 | 0.0907 | 0.1304 | 4.7528 |
| 4 | 4.6187 | 0.0632 | 0.2296 | 4.3705 |
| 5 | 4.4801 | 0.1542 | 0.3211 | 4.2892 |
