# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `data\self_generated_wami_train_smoke_independent_benign.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

- Transition MINE: `False`

- Transition fusion: `0.35`

- Source-aware auxiliary heads: `False`

- Auxiliary fusion: `0.2`

- Provenance memory: `False`

- Provenance fusion: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| self_generated_wami_train_smoke_independent_benign | 100.0% | 1.8% | 98.8% | 16.050 | 80 | -1.8500 |
