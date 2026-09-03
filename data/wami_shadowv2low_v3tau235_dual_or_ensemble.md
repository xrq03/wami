# Dual Paper-MINE WAMI Ensemble

- Model A: `wami_paper_strict_shadowv2_b70_e3_cuda.pt`, tau `-5.85`
- Model B: `wami_paper_strict_shadowv3_targeted_e2_cuda.pt`, tau `-2.35`
- Mode: `or`
- Risk margin: `0.0`
- Passive margin: `0.15`

| Dataset | Mode | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| injecagent_wami | OR | 88.6% | 29.4% | 79.5% | 38.954 | 4233 |
| bipia_wami | OR | 100.0% | 11.1% | 94.5% | 36.105 | 2400 |
| agentdojo_wami | OR | 95.6% | 16.3% | 94.0% | 64.643 | 653 |
