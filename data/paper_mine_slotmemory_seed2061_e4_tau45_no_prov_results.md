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

- Provenance memory: `False`

- Provenance fusion: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 67.4% | 0.0% | 83.7% | 22.939 | 4233 | -4.5000 |
| bipia_wami | 97.0% | 0.0% | 98.5% | 20.234 | 2400 | -4.5000 |
| agentdojo_wami | 99.5% | 16.3% | 97.4% | 36.183 | 653 | -4.5000 |
