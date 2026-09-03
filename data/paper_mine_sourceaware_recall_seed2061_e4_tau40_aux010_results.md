# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `.\data\paper_shadow_val_sourceaware_seed2061.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

- Transition MINE: `True`

- Transition fusion: `0.35`

- Source-aware auxiliary heads: `True`

- Auxiliary fusion: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 80.5% | 23.5% | 78.5% | 16.741 | 4233 | -4.0000 |
| bipia_wami | 99.8% | 1.2% | 99.3% | 15.404 | 2400 | -4.0000 |
| agentdojo_wami | 99.6% | 26.7% | 96.2% | 25.958 | 653 | -4.0000 |
