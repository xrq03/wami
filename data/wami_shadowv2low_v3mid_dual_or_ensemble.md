# Dual Paper-MINE WAMI Ensemble

- Model A: `wami_paper_strict_shadowv2_b70_e3_cuda.pt`, tau `-5.85`
- Model B: `wami_paper_strict_shadowv3_targeted_e2_cuda.pt`, tau `-2.75`
- Mode: `or`
- Risk margin: `0.0`
- Passive margin: `0.15`

| Dataset | Mode | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| injecagent_wami | OR | 86.1% | 11.8% | 87.1% | 40.041 | 4233 |
| bipia_wami | OR | 100.0% | 6.3% | 96.8% | 36.779 | 2400 |
| agentdojo_wami | OR | 92.9% | 11.6% | 92.3% | 65.699 | 653 |
