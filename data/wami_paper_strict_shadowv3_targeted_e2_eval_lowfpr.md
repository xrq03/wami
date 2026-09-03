# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `data\shadow_v3_val_900_targeted_seed20260523.jsonl`
- Target FPR on generated validation: `0.02`
- Risk margin: `0.0`
- Passive margin: `0.15`

- Transition MINE: `True`

- Transition fusion: `0.35`

- Source-aware auxiliary heads: `True`

- Auxiliary fusion: `0.2`

- Provenance memory: `True`

- Provenance fusion: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 74.3% | 0.0% | 87.2% | 22.105 | 4233 | -3.7500 |
| bipia_wami | 99.9% | 0.8% | 99.6% | 18.454 | 2400 | -3.7500 |
| agentdojo_wami | 83.2% | 5.8% | 84.7% | 34.291 | 653 | -3.7500 |
