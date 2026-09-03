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
| injecagent_wami | 66.4% | 0.0% | 83.3% | 17.862 | 4233 | -4.0000 |
| bipia_wami | 98.2% | 0.1% | 99.1% | 16.107 | 2400 | -4.0000 |
| agentdojo_wami | 96.8% | 20.9% | 94.5% | 27.501 | 653 | -4.0000 |
