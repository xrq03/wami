# Paper-MINE Learned Ensemble

- Model A: `.\wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt`
- Model B: `.\wami_paper_mine_slotmemory_seed2061_e4_cuda.pt`
- Tau A/B: `-4.5`, `-4.5`
- Modes: `a`, `b`, `or`, `and`

| Dataset | Mode | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| injecagent_wami | a | 83.3% | 5.9% | 88.7% | 37.449 | 4233 |
| injecagent_wami | b | 67.4% | 0.0% | 83.7% | 37.449 | 4233 |
| injecagent_wami | or | 85.2% | 5.9% | 89.7% | 37.449 | 4233 |
| injecagent_wami | and | 65.5% | 0.0% | 82.8% | 37.449 | 4233 |
| bipia_wami | a | 99.6% | 0.4% | 99.6% | 38.304 | 2400 |
| bipia_wami | b | 97.0% | 0.0% | 98.5% | 38.304 | 2400 |
| bipia_wami | or | 99.7% | 0.4% | 99.6% | 38.304 | 2400 |
| bipia_wami | and | 96.9% | 0.0% | 98.5% | 38.304 | 2400 |
| agentdojo_wami | a | 98.8% | 29.1% | 95.1% | 68.504 | 653 |
| agentdojo_wami | b | 99.5% | 16.3% | 97.4% | 68.504 | 653 |
| agentdojo_wami | or | 99.8% | 30.2% | 95.9% | 68.504 | 653 |
| agentdojo_wami | and | 98.4% | 15.1% | 96.6% | 68.504 | 653 |
