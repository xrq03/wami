# Paper-Calibrated WAMI Search

- Data: `data\bipia_wami.jsonl`
- Model: `wami_bipia_current_e3.npz`
- Target IR/FPR: 0.889/0.015

| rank | base_threshold | score_margin | plan_mine | action_prior | IR | FPR | ACC | distance |
|---:|---:|---:|---|---|---:|---:|---:|---:|
| 1 | -0.50 | 0.35 | True | False | 0.904 | 0.009 | 0.948 | 0.021 |
| 2 | -0.50 | 0.50 | True | False | 0.904 | 0.007 | 0.949 | 0.023 |
| 3 | -0.50 | 0.20 | True | False | 0.906 | 0.022 | 0.942 | 0.024 |
| 4 | -0.50 | 1.00 | True | False | 0.903 | 0.004 | 0.950 | 0.025 |
| 5 | -0.50 | 0.75 | True | False | 0.904 | 0.005 | 0.950 | 0.025 |
| 6 | -0.50 | 0.10 | True | False | 0.907 | 0.038 | 0.934 | 0.041 |
| 7 | -0.50 | 0.05 | True | False | 0.910 | 0.052 | 0.929 | 0.058 |
| 8 | -0.30 | 1.00 | True | False | 0.951 | 0.016 | 0.968 | 0.063 |
| 9 | -0.30 | 0.75 | True | False | 0.951 | 0.018 | 0.967 | 0.064 |
| 10 | -0.30 | 0.50 | True | False | 0.951 | 0.024 | 0.963 | 0.071 |
