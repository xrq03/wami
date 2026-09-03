# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `data\paper_shadow_val_v2_fast.jsonl`
- Target FPR on generated validation: `1.0`
- Risk margin: `0.0`
- Passive margin: `0.5`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 45.9% | 0.0% | 73.0% | 14.298 | 4233 | -4.0000 |
| bipia_wami | 77.0% | 0.0% | 88.5% | 13.571 | 2400 | -4.0000 |
| agentdojo_wami | 91.0% | 8.1% | 91.1% | 24.518 | 653 | -4.0000 |
