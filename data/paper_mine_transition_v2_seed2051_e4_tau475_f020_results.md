# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `.\data\paper_shadow_val_transition_v2_seed2051.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

- Transition MINE: `True`

- Transition fusion: `0.2`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 60.6% | 29.4% | 65.6% | 14.642 | 4233 | -4.7500 |
| bipia_wami | 97.2% | 3.2% | 97.0% | 13.447 | 2400 | -4.7500 |
| agentdojo_wami | 98.2% | 4.7% | 97.9% | 24.080 | 653 | -4.7500 |
