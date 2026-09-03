# Dual Paper-MINE WAMI Ensemble

- Model A: `wami_paper_strict_shadowv2_b70_e3_cuda.pt`, tau `-5.85`
- Model B: `wami_paper_strict_shadowv3_targeted_e2_cuda.pt`, tau `-1.85`
- Mode: `or`
- Risk margin: `0.0`
- Passive margin: `0.15`

| Dataset | Mode | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| injecagent_wami | OR | 91.1% | 29.4% | 80.8% | 38.118 | 4233 |
| bipia_wami | OR | 100.0% | 19.4% | 90.3% | 34.453 | 2400 |
| agentdojo_wami | OR | 98.8% | 20.9% | 96.2% | 55.982 | 653 |
