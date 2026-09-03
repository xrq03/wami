# Source-Aware Learned Calibrator

- Model: `.\wami_paper_mine_sourceaware_seed2061_e2_cuda.pt`
- Validation data: `.\data\paper_shadow_val_sourceaware_seed2061.jsonl`
- Target validation FPR: `0.05`
- Calibrator: logistic regression over learned WAMI features
- Bias: `0.137665`
- Weights: `-0.8327, -0.8389, -0.8330, -0.8777, -0.8490, 0.1333, 0.1578, 0.8017, 0.8050, -0.4067, -0.3856, -0.0248`

| Dataset | IR | FPR | ACC | Latency ms | N | Threshold |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 65.5% | 5.9% | 79.9% | 17.934 | 4233 | 0.9628 |
| bipia_wami | 92.6% | 2.7% | 95.0% | 16.330 | 2400 | 0.9628 |
| agentdojo_wami | 33.0% | 2.3% | 41.5% | 31.956 | 653 | 0.9628 |
