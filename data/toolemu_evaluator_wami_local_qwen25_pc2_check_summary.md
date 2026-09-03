# ToolEmu evaluator adapted to WAMI datasets

Model: `qwen2.5:7b-instruct`

| Dataset | IR | FPR | ACC | Latency ms/sample | N | Attack | Benign | Parsed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | 50.0% | 0.0% | 75.0% | 87723.8 | 4 | 2 | 2 | 4 |
| InjecAgent | 100.0% | 0.0% | 100.0% | 86435.2 | 4 | 2 | 2 | 4 |
| AgentDojo | 100.0% | 100.0% | 50.0% | 88617.1 | 4 | 2 | 2 | 4 |
