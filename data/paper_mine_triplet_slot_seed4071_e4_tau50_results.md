# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `.\data\paper_shadow_val_triplet_seed4071.jsonl`
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
| injecagent_wami | 74.8% | 0.0% | 87.5% | 23.531 | 4233 | -5.0000 |
| bipia_wami | 99.3% | 0.5% | 99.4% | 20.444 | 2400 | -5.0000 |
| agentdojo_wami | 97.2% | 9.3% | 96.3% | 37.217 | 653 | -5.0000 |
