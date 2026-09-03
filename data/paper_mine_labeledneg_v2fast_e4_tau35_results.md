# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `data\paper_shadow_val_v2_fast.jsonl`
- Target FPR on generated validation: `1.0`
- Risk margin: `0.0`
- Passive margin: `0.5`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 84.9% | 35.3% | 74.7% | 11.026 | 4233 | -3.5000 |
| bipia_wami | 100.0% | 11.6% | 94.2% | 10.986 | 2400 | -3.5000 |
| agentdojo_wami | 99.6% | 16.3% | 97.5% | 18.859 | 653 | -3.5000 |
