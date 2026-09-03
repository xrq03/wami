# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `data\paper_shadow_val_v3_fast.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 93.1% | 41.2% | 75.9% | 8.027 | 4233 | -1.8500 |
| bipia_wami | 99.8% | 35.8% | 82.0% | 9.916 | 2400 | -1.8500 |
| agentdojo_wami | 100.0% | 23.3% | 96.9% | 14.297 | 653 | -1.8500 |
