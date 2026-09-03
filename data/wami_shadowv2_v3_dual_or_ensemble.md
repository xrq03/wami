# Dual Paper-MINE WAMI Ensemble

- Model A: `wami_paper_strict_shadowv2_b70_e3_cuda.pt`, tau `-5.85`
- Model B: `wami_paper_strict_shadowv3_targeted_e2_cuda.pt`, tau `-3.75`
- Mode: `or`
- Risk margin: `0.0`
- Passive margin: `0.15`

| Dataset | Mode | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| injecagent_wami | OR | 80.4% | 0.0% | 90.2% | 43.630 | 4233 |
| bipia_wami | OR | 99.9% | 0.8% | 99.6% | 37.178 | 2400 |
| agentdojo_wami | OR | 88.0% | 8.1% | 88.5% | 72.596 | 653 |
