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
| injecagent_wami | 79.8% | 11.8% | 84.0% | 21.956 | 4233 | -4.5000 |
| bipia_wami | 99.6% | 3.5% | 98.0% | 18.885 | 2400 | -4.5000 |
| agentdojo_wami | 99.5% | 11.6% | 98.0% | 32.550 | 653 | -4.5000 |
