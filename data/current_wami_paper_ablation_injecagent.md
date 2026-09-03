| Dataset | Variant | IR | FPR | ACC | Latency ms | N | Attack N | Benign N |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| InjecAgent | WAMI full | 93.4% | 0.0% | 96.7% | 1.762 | 4233 | 2108 | 2125 |
| InjecAgent | WAMI w/o MINE (rules-only) | 93.0% | 0.0% | 96.5% | 1.673 | 4233 | 2108 | 2125 |
| InjecAgent | WAMI w/o rules (score-only) | 50.1% | 5.9% | 72.2% | 1.691 | 4233 | 2108 | 2125 |
| InjecAgent | WAMI w/o TDG edges | 96.5% | 5.9% | 95.3% | 1.678 | 4233 | 2108 | 2125 |
| InjecAgent | High-risk rules only | 93.0% | 0.0% | 96.5% | 1.619 | 4233 | 2108 | 2125 |
| InjecAgent | MINE score only | 50.1% | 5.9% | 72.2% | 1.668 | 4233 | 2108 | 2125 |
