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
| injecagent_wami | 82.7% | 23.5% | 79.6% | 17.178 | 4233 | -3.5000 |
| bipia_wami | 99.9% | 5.2% | 97.3% | 15.634 | 2400 | -3.5000 |
| agentdojo_wami | 100.0% | 29.1% | 96.2% | 24.443 | 653 | -3.5000 |
