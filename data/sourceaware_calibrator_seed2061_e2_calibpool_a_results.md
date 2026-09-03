# Source-Aware Learned Calibrator

- Model: `.\wami_paper_mine_sourceaware_seed2061_e2_cuda.pt`
- Validation data: `.\data\paper_sourceaware_calib_pool_seed3061_a.jsonl`
- Target validation FPR: `0.05`
- Calibrator: logistic regression over learned WAMI features
- Bias: `0.012099`
- Weights: `-0.8229, -0.8447, -0.8348, -0.8954, -0.8677, 0.1841, 0.2077, 0.8042, 0.7774, -0.4187, -0.4089, -0.0270`

| Dataset | IR | FPR | ACC | Latency ms | N | Threshold |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 52.1% | 0.0% | 76.1% | 17.954 | 4233 | 0.9549 |
| bipia_wami | 55.8% | 0.5% | 77.7% | 15.953 | 2400 | 0.9549 |
| agentdojo_wami | 71.6% | 10.5% | 74.0% | 31.025 | 653 | 0.9549 |
