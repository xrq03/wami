| Dataset | Variant | IR | FPR | ACC | Latency ms | N | Attack N | Benign N |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | WAMI full | 100.0% | 33.2% | 83.4% | 1.496 | 2400 | 1200 | 1200 |
| BIPIA | WAMI w/o MINE (rules-only) | 100.0% | 0.0% | 100.0% | 1.480 | 2400 | 1200 | 1200 |
| BIPIA | WAMI w/o rules (score-only) | 57.6% | 33.7% | 62.0% | 1.450 | 2400 | 1200 | 1200 |
| BIPIA | WAMI w/o TDG edges | 100.0% | 33.2% | 83.4% | 1.490 | 2400 | 1200 | 1200 |
| BIPIA | High-risk rules only | 100.0% | 0.0% | 100.0% | 1.490 | 2400 | 1200 | 1200 |
| BIPIA | MINE score only | 57.6% | 33.7% | 62.0% | 1.420 | 2400 | 1200 | 1200 |
