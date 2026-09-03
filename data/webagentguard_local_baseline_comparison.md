# WebAgentGuard Local Baseline Comparison

| Setting | Dataset | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5 next_action | BIPIA | 100.0% | 32.0% | 84.0% | 4880.1 | 100 | 50 | 50 |
| qwen2.5 next_action | InjecAgent | 100.0% | 0.0% | 100.0% | 4735.4 | 100 | 50 | 50 |
| qwen2.5 next_action | AgentDojo | 92.0% | 26.0% | 83.0% | 4673.8 | 100 | 50 | 50 |
| mistral full_trajectory | BIPIA | 84.0% | 0.0% | 92.0% | 4858.4 | 100 | 50 | 50 |
| mistral full_trajectory | InjecAgent | 48.0% | 0.0% | 74.0% | 4735.1 | 100 | 50 | 50 |
| mistral full_trajectory | AgentDojo | 88.0% | 0.0% | 94.0% | 4696.9 | 100 | 50 | 50 |
| mistral next_action | BIPIA | 36.0% | 0.0% | 68.0% | 877.7 | 50 | 25 | 25 |
| mistral next_action | InjecAgent | 76.0% | 0.0% | 88.0% | 788.2 | 50 | 25 | 25 |
| mistral next_action | AgentDojo | 48.0% | 0.0% | 74.0% | 753.5 | 50 | 25 | 25 |
