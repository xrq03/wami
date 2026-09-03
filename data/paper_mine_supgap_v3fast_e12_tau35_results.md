# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `data\paper_shadow_val_v3_fast.jsonl`
- Target FPR on generated validation: `1.0`
- Risk margin: `0.0`
- Passive margin: `0.5`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 82.3% | 41.2% | 70.5% | 11.925 | 4233 | -3.5000 |
| bipia_wami | 99.9% | 32.7% | 83.6% | 11.385 | 2400 | -3.5000 |
| agentdojo_wami | 96.8% | 20.9% | 94.5% | 20.711 | 653 | -3.5000 |
