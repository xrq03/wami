# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `data\paper_shadow_val_v3_fast.jsonl`
- Target FPR on generated validation: `1.0`
- Risk margin: `0.0`
- Passive margin: `0.5`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 85.2% | 35.3% | 74.9% | 13.659 | 4233 | -3.5000 |
| bipia_wami | 99.6% | 22.5% | 88.5% | 13.197 | 2400 | -3.5000 |
| agentdojo_wami | 99.8% | 9.3% | 98.6% | 23.326 | 653 | -3.5000 |
