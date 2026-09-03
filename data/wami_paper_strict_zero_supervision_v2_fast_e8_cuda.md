# WAMI Paper-Strict Zero-Supervision Official Tests

- Official benchmark datasets are used only for testing.
- Calibration data: `data\paper_shadow_val_v2_fast.jsonl`
- Calibrated tau: `-1.8500`

| Dataset | IR | FPR | ACC | Latency ms | N |
|---|---:|---:|---:|---:|---:|
| injecagent_wami | 98.7% | 52.9% | 72.8% | 9.303 | 4233 |
| bipia_wami | 100.0% | 2.6% | 98.7% | 12.004 | 2400 |
| agentdojo_wami | 95.8% | 32.6% | 92.0% | 19.042 | 653 |
