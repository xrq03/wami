# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `.\data\paper_shadow_val_transition_v2_seed2051.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

- Transition MINE: `True`

- Transition fusion: `0.35`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 64.8% | 29.4% | 67.7% | 14.553 | 4233 | -4.7500 |
| bipia_wami | 97.4% | 4.9% | 96.2% | 13.480 | 2400 | -4.7500 |
| agentdojo_wami | 99.1% | 4.7% | 98.6% | 24.432 | 653 | -4.7500 |
