# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `data\paper_shadow_val_v3_fast.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 89.1% | 52.9% | 68.0% | 9.588 | 4233 | -1.8500 |
| bipia_wami | 100.0% | 41.1% | 79.5% | 11.340 | 2400 | -1.8500 |
| agentdojo_wami | 98.1% | 29.1% | 94.5% | 17.312 | 653 | -1.8500 |
