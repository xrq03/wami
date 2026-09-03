# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `data\shadow_val_500_seed20260519.jsonl`
- Target FPR on generated validation: `0.02`
- Risk margin: `0.15`
- Passive margin: `0.1`

- Transition MINE: `True`

- Transition fusion: `0.35`

- Source-aware auxiliary heads: `True`

- Auxiliary fusion: `0.2`

- Provenance memory: `True`

- Provenance fusion: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 93.3% | 47.1% | 73.0% | 16.509 | 4233 | -1.8500 |
| bipia_wami | 100.0% | 13.2% | 93.4% | 16.889 | 2400 | -1.8500 |
| agentdojo_wami | 100.0% | 12.8% | 98.3% | 20.319 | 653 | -1.8500 |
