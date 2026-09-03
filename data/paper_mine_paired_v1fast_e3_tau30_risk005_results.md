# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `.\data\paper_shadow_val_paired_v1_fast.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.05`
- Passive margin: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 64.5% | 35.3% | 64.6% | 14.009 | 4233 | -3.0000 |
| bipia_wami | 98.7% | 20.1% | 89.3% | 13.574 | 2400 | -3.0000 |
| agentdojo_wami | 94.0% | 8.1% | 93.7% | 23.429 | 653 | -3.0000 |
