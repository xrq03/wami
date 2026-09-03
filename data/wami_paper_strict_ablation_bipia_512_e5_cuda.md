# WAMI Paper-Strict Ablation

- Calibrated tau: `-1.8500`

| Ablation Variant | IR | FPR | Latency | ACC | N |
|---|---:|---:|---:|---:|---:|
| WAMI (Full Model) | 100.0% | 0.0% | 6.913 ms | 100.0% | 100 |
| w/o TDG Graph Construction | 80.0% | 0.0% | 5.709 ms | 90.0% | 100 |
| w/o World Model Rollout | 100.0% | 0.0% | 2.931 ms | 100.0% | 100 |
| w/o MINE Gateway (Cosine Similarity) | 100.0% | 0.0% | 10.584 ms | 100.0% | 100 |
| w/o Shadow Adversarial Training | 100.0% | 0.0% | 13.476 ms | 100.0% | 100 |
