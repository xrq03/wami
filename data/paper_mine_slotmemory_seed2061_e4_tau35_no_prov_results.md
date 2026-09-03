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
| injecagent_wami | 78.5% | 29.4% | 74.5% | 21.566 | 4233 | -3.5000 |
| bipia_wami | 98.7% | 3.3% | 97.7% | 19.155 | 2400 | -3.5000 |
| agentdojo_wami | 100.0% | 26.7% | 96.5% | 32.509 | 653 | -3.5000 |
