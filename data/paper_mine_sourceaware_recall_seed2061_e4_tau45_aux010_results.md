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
| injecagent_wami | 78.4% | 5.9% | 86.3% | 17.545 | 4233 | -4.5000 |
| bipia_wami | 99.4% | 0.2% | 99.6% | 16.204 | 2400 | -4.5000 |
| agentdojo_wami | 98.4% | 23.3% | 95.6% | 27.635 | 653 | -4.5000 |
