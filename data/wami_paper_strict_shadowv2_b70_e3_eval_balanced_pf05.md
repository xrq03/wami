# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `data\shadow_v2_val_800_b70_seed20260521.jsonl`
- Target FPR on generated validation: `0.05`
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
| injecagent_wami | 77.1% | 0.0% | 88.6% | 22.614 | 4233 | -5.8500 |
| bipia_wami | 98.2% | 0.0% | 99.1% | 19.273 | 2400 | -5.8500 |
| agentdojo_wami | 78.3% | 4.7% | 80.6% | 39.198 | 653 | -5.8500 |
