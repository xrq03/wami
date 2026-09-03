# WAMI Paper-Strict Ablation

- Calibrated tau: `-1.8500`

| Ablation Variant | IR | FPR | Latency | ACC | N |
|---|---:|---:|---:|---:|---:|
| WAMI (Full Model) | 100.0% | 0.0% | 9.392 ms | 100.0% | 100 |
| w/o TDG Graph Construction | 100.0% | 0.0% | 5.664 ms | 100.0% | 100 |
| w/o World Model Rollout | 100.0% | 0.0% | 2.645 ms | 100.0% | 100 |
| w/o MINE Gateway (Cosine Similarity) | 85.4% | 0.0% | 12.789 ms | 94.0% | 100 |
| w/o Shadow Adversarial Training | 95.1% | 0.0% | 10.357 ms | 98.0% | 100 |
