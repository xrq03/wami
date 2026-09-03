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

- Auxiliary fusion: `0.2`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 54.4% | 0.0% | 77.3% | 18.027 | 4233 | -4.7500 |
| bipia_wami | 32.9% | 0.0% | 66.5% | 16.233 | 2400 | -4.7500 |
| agentdojo_wami | 79.0% | 5.8% | 81.0% | 29.373 | 653 | -4.7500 |
