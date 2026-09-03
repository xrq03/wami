# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `.\data\paper_shadow_val_paired_v1_fast.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 65.2% | 35.3% | 64.9% | 13.437 | 4233 | -3.0000 |
| bipia_wami | 98.8% | 20.1% | 89.3% | 13.194 | 2400 | -3.0000 |
| agentdojo_wami | 94.5% | 8.1% | 94.2% | 22.443 | 653 | -3.0000 |
