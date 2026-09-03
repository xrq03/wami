# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `.\data\paper_shadow_val_paired_v2_seed2041.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 58.4% | 29.4% | 64.5% | 13.981 | 4233 | -3.5000 |
| bipia_wami | 99.7% | 9.4% | 95.1% | 13.206 | 2400 | -3.5000 |
| agentdojo_wami | 98.6% | 2.3% | 98.5% | 21.311 | 653 | -3.5000 |
