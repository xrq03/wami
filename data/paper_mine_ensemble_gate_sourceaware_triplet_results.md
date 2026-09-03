# Learned WAMI Ensemble Gate

- Model A: `.\wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt`
- Model B: `.\wami_paper_mine_triplet_slot_seed4071_e4_cuda.pt`
- Validation data: `.\data\paper_shadow_val_triplet_seed4071.jsonl`
- Weights: `0.9394, 0.9394, -0.6822, -0.6321, -0.6774, -0.9185, -0.2611, -0.9187, 0.3544, 0.5722`
- Bias: `-0.3611`

| Dataset | IR | FPR | ACC | Latency ms | N | Threshold |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 66.2% | 0.0% | 83.2% | 40.960 | 4233 | 0.9848 |
| bipia_wami | 63.0% | 0.2% | 81.4% | 35.655 | 2400 | 0.9848 |
| agentdojo_wami | 0.2% | 0.0% | 13.3% | 61.805 | 653 | 0.9848 |
