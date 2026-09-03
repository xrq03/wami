# Paper-MINE Learned Ensemble

- Model A: `.\wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt`
- Model B: `.\wami_paper_mine_slotmemory_seed2061_e4_cuda.pt`
- Tau A/B: `-4.5`, `-4.5`
- Modes: `a`, `b`, `or`, `and`

| Dataset | Mode | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| injecagent_wami | a | 78.4% | 5.9% | 86.3% | 44.321 | 4233 |
| injecagent_wami | b | 67.4% | 0.0% | 83.7% | 44.321 | 4233 |
| injecagent_wami | or | 80.6% | 5.9% | 87.4% | 44.321 | 4233 |
| injecagent_wami | and | 65.1% | 0.0% | 82.6% | 44.321 | 4233 |
| bipia_wami | a | 99.4% | 0.2% | 99.6% | 38.076 | 2400 |
| bipia_wami | b | 97.0% | 0.0% | 98.5% | 38.076 | 2400 |
| bipia_wami | or | 99.4% | 0.2% | 99.6% | 38.076 | 2400 |
| bipia_wami | and | 97.0% | 0.0% | 98.5% | 38.076 | 2400 |
| agentdojo_wami | a | 98.4% | 23.3% | 95.6% | 66.535 | 653 |
| agentdojo_wami | b | 99.5% | 16.3% | 97.4% | 66.535 | 653 |
| agentdojo_wami | or | 99.8% | 24.4% | 96.6% | 66.535 | 653 |
| agentdojo_wami | and | 98.1% | 15.1% | 96.3% | 66.535 | 653 |
