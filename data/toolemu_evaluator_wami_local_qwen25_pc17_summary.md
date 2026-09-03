# ToolEmu evaluator adapted to WAMI datasets

Model: `qwen2.5:7b-instruct`

| Dataset | IR | FPR | ACC | Latency ms/sample | N | Attack | Benign | Parsed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | 17.6% | 17.6% | 50.0% | 91473.8 | 34 | 17 | 17 | 34 |
| InjecAgent | 80.0% | 11.8% | 84.4% | 98836.5 | 34 | 17 | 17 | 32 |
| AgentDojo | 57.1% | 58.8% | 48.4% | 110733.8 | 34 | 17 | 17 | 31 |
