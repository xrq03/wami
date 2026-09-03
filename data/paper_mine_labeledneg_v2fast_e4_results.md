# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `data\paper_shadow_val_v2_fast.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 94.6% | 41.2% | 76.7% | 9.105 | 4233 | -1.8500 |
| bipia_wami | 100.0% | 68.3% | 65.8% | 11.034 | 2400 | -1.8500 |
| agentdojo_wami | 100.0% | 36.0% | 95.3% | 15.638 | 653 | -1.8500 |
