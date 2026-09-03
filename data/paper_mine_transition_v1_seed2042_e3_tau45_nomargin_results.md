# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `.\data\paper_shadow_val_paired_v2_seed2042.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.0`
- Passive margin: `0.0`

- Transition MINE: `True`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 78.3% | 35.3% | 71.5% | 14.025 | 4233 | -4.5000 |
| bipia_wami | 98.0% | 7.4% | 95.3% | 14.338 | 2400 | -4.5000 |
| agentdojo_wami | 100.0% | 14.0% | 98.2% | 26.211 | 653 | -4.5000 |
