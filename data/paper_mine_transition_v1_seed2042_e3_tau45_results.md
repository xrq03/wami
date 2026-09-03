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
| injecagent_wami | 79.3% | 35.3% | 72.0% | 16.640 | 4233 | -4.5000 |
| bipia_wami | 98.3% | 7.3% | 95.5% | 14.545 | 2400 | -4.5000 |
| agentdojo_wami | 100.0% | 14.0% | 98.2% | 27.113 | 653 | -4.5000 |
