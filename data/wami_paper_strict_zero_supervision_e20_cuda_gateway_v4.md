# WAMI Paper-Strict Zero-Supervision Official Tests

- Official benchmark datasets are used only for testing.
- Calibration data: `data\paper_shadow_val.jsonl`
- Calibrated tau: `-1.8500`

| Dataset | IR | FPR | ACC | Latency ms | N |
|---|---:|---:|---:|---:|---:|
| injecagent_wami | 95.9% | 0.0% | 97.9% | 11.830 | 4233 |
| bipia_wami | 100.0% | 0.1% | 100.0% | 13.182 | 2400 |
| agentdojo_wami | 100.0% | 1.2% | 99.8% | 22.314 | 653 |
