# WAMI v4 Ablation

- Calibration data: `data\paper_shadow_val.jsonl`
- Calibrated tau: `-1.8500`

| Dataset | Variant | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| injecagent_wami | WAMI full | 95.9% | 0.0% | 97.9% | 11.881 | 4233 |
| injecagent_wami | w/o plan-level MINE | 94.5% | 0.0% | 97.3% | 12.485 | 4233 |
| injecagent_wami | w/o action-prior rules | 88.6% | 52.9% | 67.7% | 10.929 | 4233 |
| injecagent_wami | static threshold | 95.9% | 0.0% | 97.9% | 10.822 | 4233 |
| injecagent_wami | rules only | 93.0% | 0.0% | 96.5% | 0.073 | 4233 |
| injecagent_wami | trajectory MINE only | 88.4% | 52.9% | 67.6% | 10.812 | 4233 |
| bipia_wami | WAMI full | 100.0% | 0.1% | 100.0% | 12.366 | 2400 |
| bipia_wami | w/o plan-level MINE | 100.0% | 0.1% | 100.0% | 10.911 | 2400 |
| bipia_wami | w/o action-prior rules | 99.8% | 76.6% | 61.6% | 12.294 | 2400 |
| bipia_wami | static threshold | 100.0% | 0.1% | 100.0% | 12.887 | 2400 |
| bipia_wami | rules only | 100.0% | 0.0% | 100.0% | 0.109 | 2400 |
| bipia_wami | trajectory MINE only | 99.8% | 76.6% | 61.6% | 10.804 | 2400 |
| agentdojo_wami | WAMI full | 100.0% | 1.2% | 99.8% | 22.469 | 653 |
| agentdojo_wami | w/o plan-level MINE | 100.0% | 1.2% | 99.8% | 22.738 | 653 |
| agentdojo_wami | w/o action-prior rules | 99.8% | 40.7% | 94.5% | 21.888 | 653 |
| agentdojo_wami | static threshold | 100.0% | 1.2% | 99.8% | 22.486 | 653 |
| agentdojo_wami | rules only | 74.6% | 0.0% | 77.9% | 0.093 | 653 |
| agentdojo_wami | trajectory MINE only | 99.8% | 40.7% | 94.5% | 22.285 | 653 |
