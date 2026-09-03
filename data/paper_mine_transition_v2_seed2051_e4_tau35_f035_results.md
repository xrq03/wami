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
| injecagent_wami | 69.9% | 29.4% | 70.3% | 14.029 | 4233 | -3.5000 |
| bipia_wami | 97.7% | 7.2% | 95.2% | 13.162 | 2400 | -3.5000 |
| agentdojo_wami | 99.6% | 7.0% | 98.8% | 23.350 | 653 | -3.5000 |
