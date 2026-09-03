# WAMI Strict No-Test-Training Comparison

This file separates two very different meanings of "good result":

1. Architecture-faithful smoke: train/evaluate within the same benchmark file to verify the paper-style WAMI modules run correctly.
2. No-test-training generalization: train only on self-generated shadow data, calibrate on self-generated validation data, and test on InjecAgent/BIPIA/AgentDojo.

## Shadow Training Setup

| Item | Value |
|---|---|
| Train file | `data/shadow_train_2000_seed20260518.jsonl` |
| Validation file | `data/shadow_val_500_seed20260519.jsonl` |
| Test files | `data/injecagent_wami.jsonl`, `data/bipia_wami.jsonl`, `data/agentdojo_wami.jsonl` |
| Model | 4-layer Transformer Encoder, dim 1024, hidden 1024, 8 heads |
| MINE | 3-layer ReLU MLP |
| Training | AdamW, cosine schedule, 5 epochs, CUDA |
| Final MI gap | 6.527 |
| Peak WAMI VRAM | 336.0 MB |
| Paper-style latency probe | 36.033 ms on InjecAgent limit=50 |

## Generalization Results

| Dataset | Setting | IR | FPR | ACC | Latency ms | Tau | Meaning |
|---|---|---:|---:|---:|---:|---:|---|
| InjecAgent | high-recall shadow calibration | 93.3% | 47.1% | 73.0% | 16.509 | -1.8500 | Catches most attacks but over-blocks benign samples. |
| BIPIA | high-recall shadow calibration | 100.0% | 13.2% | 93.4% | 16.889 | -1.8500 | Strong attack blocking with moderate false positives. |
| AgentDojo | high-recall shadow calibration | 100.0% | 12.8% | 98.3% | 20.319 | -1.8500 | Strong attack blocking with moderate false positives. |
| InjecAgent | low-FPR shadow calibration | 76.6% | 0.0% | 88.4% | 23.381 | -5.8500 | Conservative threshold removes false positives but loses recall. |
| BIPIA | low-FPR shadow calibration | 83.7% | 0.0% | 91.8% | 21.244 | -5.8500 | Good balanced no-test-training result. |
| AgentDojo | low-FPR shadow calibration | 68.8% | 3.5% | 72.4% | 44.038 | -5.8500 | Hardest dataset under strict train/test separation. |

## Interpretation

- The high-recall setting proves that the shadow-trained paper-strict WAMI can learn attack interception without training on the benchmark test files.
- The low-FPR setting is the more defensible paper row when the reviewer cares about test leakage, because it keeps false positives near zero.
- The remaining weakness is not architecture any more; it is distribution shift between synthetic benign shadow data and InjecAgent/AgentDojo benign trajectories.
- To improve without cheating, the next step is to expand self-generated benign counterfactuals, especially authorized sensitive actions and indirect-injection decoy observations, then retrain and keep the three benchmark files test-only.
