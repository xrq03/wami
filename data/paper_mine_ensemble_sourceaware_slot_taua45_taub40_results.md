# Paper-MINE Learned Ensemble

- Model A: `.\wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt`
- Model B: `.\wami_paper_mine_slotmemory_seed2061_e4_cuda.pt`
- Tau A/B: `-4.5`, `-4.0`
- Modes: `a`, `b`, `or`, `and`

| Dataset | Mode | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| injecagent_wami | a | 78.4% | 5.9% | 86.3% | 42.848 | 4233 |
| injecagent_wami | b | 73.7% | 17.6% | 78.1% | 42.848 | 4233 |
| injecagent_wami | or | 83.1% | 17.6% | 82.7% | 42.848 | 4233 |
| injecagent_wami | and | 69.0% | 5.9% | 81.6% | 42.848 | 4233 |
| bipia_wami | a | 99.4% | 0.2% | 99.6% | 37.879 | 2400 |
| bipia_wami | b | 98.2% | 0.9% | 98.6% | 37.879 | 2400 |
| bipia_wami | or | 99.4% | 0.9% | 99.2% | 37.879 | 2400 |
| bipia_wami | and | 98.2% | 0.2% | 99.0% | 37.879 | 2400 |
| agentdojo_wami | a | 98.4% | 23.3% | 95.6% | 66.387 | 653 |
| agentdojo_wami | b | 100.0% | 22.1% | 97.1% | 66.387 | 653 |
| agentdojo_wami | or | 100.0% | 29.1% | 96.2% | 66.387 | 653 |
| agentdojo_wami | and | 98.4% | 16.3% | 96.5% | 66.387 | 653 |
