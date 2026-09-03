# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `.\data\paper_shadow_val_paired_v1_fast.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 67.0% | 41.2% | 62.9% | 12.908 | 4233 | -3.5000 |
| bipia_wami | 98.7% | 18.4% | 90.1% | 12.745 | 2400 | -3.5000 |
| agentdojo_wami | 99.1% | 9.3% | 98.0% | 20.653 | 653 | -3.5000 |
