# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `.\data\paper_shadow_val_paired_v1_fast.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 63.0% | 35.3% | 63.8% | 13.529 | 4233 | -3.2500 |
| bipia_wami | 98.7% | 17.9% | 90.4% | 12.983 | 2400 | -3.2500 |
| agentdojo_wami | 93.1% | 7.0% | 93.1% | 22.497 | 653 | -3.2500 |
