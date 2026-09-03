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
| injecagent_wami | 77.6% | 11.8% | 82.9% | 19.750 | 4233 | -4.7500 |
| bipia_wami | 99.4% | 1.2% | 99.1% | 17.870 | 2400 | -4.7500 |
| agentdojo_wami | 98.8% | 11.6% | 97.4% | 31.695 | 653 | -4.7500 |
