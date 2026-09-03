| Dataset | Variant | IR | FPR | ACC | Latency ms | N | Attack N | Benign N |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| InjecAgent | WAMI full | 96.5% | 0.0% | 98.3% | 1.164 | 4233 | 2108 | 2125 |
| InjecAgent | WAMI w/o MINE (rules-only) | 93.0% | 0.0% | 96.5% | 1.139 | 4233 | 2108 | 2125 |
| InjecAgent | WAMI w/o rules (score-only) | 25.5% | 0.0% | 62.9% | 1.145 | 4233 | 2108 | 2125 |
| InjecAgent | WAMI w/o TDG edges | 96.5% | 0.0% | 98.3% | 1.130 | 4233 | 2108 | 2125 |
| InjecAgent | High-risk rules only | 93.0% | 0.0% | 96.5% | 1.102 | 4233 | 2108 | 2125 |
| InjecAgent | MINE score only | 25.5% | 0.0% | 62.9% | 1.094 | 4233 | 2108 | 2125 |
