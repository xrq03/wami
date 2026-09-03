# Paper-MINE Learned Ensemble

- Model A: `.\wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt`
- Model B: `.\wami_paper_mine_triplet_slot_seed4071_e4_cuda.pt`
- Tau A/B: `-4.5`, `-4.75`
- Modes: `a`, `b`, `or`, `and`

| Dataset | Mode | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| injecagent_wami | a | 78.4% | 5.9% | 86.3% | 41.416 | 4233 |
| injecagent_wami | b | 77.6% | 11.8% | 82.9% | 41.416 | 4233 |
| injecagent_wami | or | 87.9% | 17.6% | 85.1% | 41.416 | 4233 |
| injecagent_wami | and | 68.1% | 0.0% | 84.1% | 41.416 | 4233 |
| bipia_wami | a | 99.4% | 0.2% | 99.6% | 37.448 | 2400 |
| bipia_wami | b | 99.4% | 1.2% | 99.1% | 37.448 | 2400 |
| bipia_wami | or | 99.8% | 1.2% | 99.2% | 37.448 | 2400 |
| bipia_wami | and | 99.1% | 0.2% | 99.5% | 37.448 | 2400 |
| agentdojo_wami | a | 98.4% | 23.3% | 95.6% | 67.002 | 653 |
| agentdojo_wami | b | 98.8% | 11.6% | 97.4% | 67.002 | 653 |
| agentdojo_wami | or | 100.0% | 26.7% | 96.5% | 67.002 | 653 |
| agentdojo_wami | and | 97.2% | 8.1% | 96.5% | 67.002 | 653 |
