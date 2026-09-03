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
| injecagent_wami | 81.0% | 41.2% | 69.9% | 15.011 | 4233 | -4.0000 |
| bipia_wami | 98.7% | 8.5% | 95.1% | 12.840 | 2400 | -4.0000 |
| agentdojo_wami | 100.0% | 16.3% | 97.9% | 21.128 | 653 | -4.0000 |
