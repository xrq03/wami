# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `data\shadow_val_500_seed20260519.jsonl`
- Target FPR on generated validation: `0.02`
- Risk margin: `0.0`
- Passive margin: `0.25`

- Transition MINE: `True`

- Transition fusion: `0.35`

- Source-aware auxiliary heads: `True`

- Auxiliary fusion: `0.2`

- Provenance memory: `True`

- Provenance fusion: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 76.6% | 0.0% | 88.4% | 23.381 | 4233 | -5.8500 |
| bipia_wami | 83.7% | 0.0% | 91.8% | 21.244 | 2400 | -5.8500 |
| agentdojo_wami | 68.8% | 3.5% | 72.4% | 44.038 | 653 | -5.8500 |
