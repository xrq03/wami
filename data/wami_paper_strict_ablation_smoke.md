# WAMI Paper-Strict Ablation

- Calibrated tau: `-1.8500`

| Ablation Variant | IR | FPR | Latency | ACC | N |
|---|---:|---:|---:|---:|---:|
| WAMI (Full Model) | 0.0% | 0.0% | 33.547 ms | 100.0% | 8 |
| w/o TDG Graph Construction | 0.0% | 0.0% | 8.917 ms | 100.0% | 8 |
| w/o World Model Rollout | 0.0% | 0.0% | 3.464 ms | 100.0% | 8 |
| w/o MINE Gateway (Cosine Similarity) | 0.0% | 0.0% | 27.231 ms | 100.0% | 8 |
| w/o Shadow Adversarial Training | 0.0% | 0.0% | 34.268 ms | 100.0% | 8 |
