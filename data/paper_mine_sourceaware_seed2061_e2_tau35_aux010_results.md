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
| injecagent_wami | 69.2% | 0.0% | 84.7% | 17.764 | 4233 | -3.5000 |
| bipia_wami | 99.1% | 0.4% | 99.3% | 15.976 | 2400 | -3.5000 |
| agentdojo_wami | 99.3% | 24.4% | 96.2% | 26.947 | 653 | -3.5000 |
