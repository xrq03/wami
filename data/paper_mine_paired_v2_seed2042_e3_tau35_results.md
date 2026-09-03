# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `.\data\paper_shadow_val_paired_v2_seed2042.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 63.5% | 23.5% | 70.0% | 14.249 | 4233 | -3.5000 |
| bipia_wami | 97.2% | 5.8% | 95.7% | 13.616 | 2400 | -3.5000 |
| agentdojo_wami | 97.2% | 7.0% | 96.6% | 24.589 | 653 | -3.5000 |
