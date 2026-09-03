# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `.\data\paper_shadow_val_paired_v1_fast.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 68.9% | 41.2% | 63.8% | 13.379 | 4233 | -3.5000 |
| bipia_wami | 98.8% | 19.2% | 89.8% | 13.458 | 2400 | -3.5000 |
| agentdojo_wami | 99.6% | 17.4% | 97.4% | 23.026 | 653 | -3.5000 |
