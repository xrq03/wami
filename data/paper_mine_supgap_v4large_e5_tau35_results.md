# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `data\paper_shadow_val_v4_large.jsonl`
- Target FPR on generated validation: `1.0`
- Risk margin: `0.0`
- Passive margin: `0.5`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 92.0% | 35.3% | 78.3% | 12.801 | 4233 | -3.5000 |
| bipia_wami | 100.0% | 39.5% | 80.2% | 12.089 | 2400 | -3.5000 |
| agentdojo_wami | 100.0% | 25.6% | 96.6% | 21.418 | 653 | -3.5000 |
