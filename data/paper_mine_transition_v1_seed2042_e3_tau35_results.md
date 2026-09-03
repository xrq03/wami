# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `.\data\paper_shadow_val_paired_v2_seed2042.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

- Transition MINE: `True`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 83.6% | 41.2% | 71.2% | 15.540 | 4233 | -3.5000 |
| bipia_wami | 99.0% | 9.9% | 94.5% | 14.415 | 2400 | -3.5000 |
| agentdojo_wami | 100.0% | 18.6% | 97.5% | 23.928 | 653 | -3.5000 |
