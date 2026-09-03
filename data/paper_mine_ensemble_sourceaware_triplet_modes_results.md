# Paper-MINE Learned Ensemble

- Model A: `.\wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt`
- Model B: `.\wami_paper_mine_triplet_slot_seed4071_e4_cuda.pt`
- Tau A/B: `-4.5`, `-5.0`
- Modes: `a`, `b`, `or`, `and`

| Dataset | Mode | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| injecagent_wami | a | 78.4% | 5.9% | 86.3% | 42.817 | 4233 |
| injecagent_wami | b | 74.8% | 0.0% | 87.5% | 42.817 | 4233 |
| injecagent_wami | or | 86.8% | 5.9% | 90.5% | 42.817 | 4233 |
| injecagent_wami | and | 66.4% | 0.0% | 83.3% | 42.817 | 4233 |
| injecagent_wami | b_or_agree | 74.8% | 0.0% | 87.5% | 42.817 | 4233 |
| bipia_wami | a | 99.4% | 0.2% | 99.6% | 33.912 | 2400 |
| bipia_wami | b | 99.3% | 0.5% | 99.4% | 33.912 | 2400 |
| bipia_wami | or | 99.8% | 0.5% | 99.6% | 33.912 | 2400 |
| bipia_wami | and | 99.0% | 0.2% | 99.4% | 33.912 | 2400 |
| bipia_wami | b_or_agree | 99.3% | 0.5% | 99.4% | 33.912 | 2400 |
| agentdojo_wami | a | 98.4% | 23.3% | 95.6% | 60.227 | 653 |
| agentdojo_wami | b | 97.2% | 9.3% | 96.3% | 60.227 | 653 |
| agentdojo_wami | or | 99.3% | 25.6% | 96.0% | 60.227 | 653 |
| agentdojo_wami | and | 96.3% | 7.0% | 95.9% | 60.227 | 653 |
| agentdojo_wami | b_or_agree | 97.2% | 9.3% | 96.3% | 60.227 | 653 |
