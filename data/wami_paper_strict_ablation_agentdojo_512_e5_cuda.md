# WAMI Paper-Strict Ablation

- Calibrated tau: `-1.8500`

| Ablation Variant | IR | FPR | Latency | ACC | N |
|---|---:|---:|---:|---:|---:|
| WAMI (Full Model) | 100.0% | 0.0% | 19.046 ms | 100.0% | 100 |
| w/o TDG Graph Construction | 0.0% | 0.0% | 5.235 ms | 16.0% | 100 |
| w/o World Model Rollout | 100.0% | 0.0% | 3.584 ms | 100.0% | 100 |
| w/o MINE Gateway (Cosine Similarity) | 100.0% | 0.0% | 14.809 ms | 100.0% | 100 |
| w/o Shadow Adversarial Training | 100.0% | 0.0% | 18.986 ms | 100.0% | 100 |
