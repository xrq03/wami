# Paper-MINE Score Export and Threshold Curve

- Model: `.\wami_paper_mine_paired_recall_v1fast_e4_cuda.pt`
- Fixed score export tau: `-3.5`
- Blocking source: paper MINE plan/trajectory score only.
- Official datasets are used as test-only inputs.

| Dataset | Tau | IR | FPR | ACC | Latency ms | N |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | -3.500 | 67.0% | 41.2% | 62.9% | 28.767 | 4233 |
| injecagent_wami | -4.500 | 17.0% | 0.0% | 58.7% | 0.000 | 4233 |
| injecagent_wami | -4.250 | 45.9% | 29.4% | 58.3% | 0.000 | 4233 |
| injecagent_wami | -4.000 | 63.2% | 41.2% | 61.0% | 0.000 | 4233 |
| injecagent_wami | -3.750 | 65.7% | 41.2% | 62.2% | 0.000 | 4233 |
| injecagent_wami | -3.500 | 67.0% | 41.2% | 62.9% | 0.000 | 4233 |
| injecagent_wami | -3.250 | 69.8% | 41.2% | 64.3% | 0.000 | 4233 |
| injecagent_wami | -3.000 | 72.8% | 41.2% | 65.8% | 0.000 | 4233 |
| injecagent_wami | -2.750 | 75.1% | 41.2% | 66.9% | 0.000 | 4233 |
| injecagent_wami | -2.500 | 77.6% | 41.2% | 68.2% | 0.000 | 4233 |
