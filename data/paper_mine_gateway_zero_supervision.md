# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `data\paper_shadow_val.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 90.1% | 52.9% | 68.5% | 9.987 | 4233 | -1.4500 |
| bipia_wami | 99.8% | 78.7% | 60.6% | 11.648 | 2400 | -1.4500 |
| agentdojo_wami | 100.0% | 45.3% | 94.0% | 19.877 | 653 | -1.4500 |
