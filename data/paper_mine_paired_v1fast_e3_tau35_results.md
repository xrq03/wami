# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `.\data\paper_shadow_val_paired_v1_fast.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 61.1% | 5.9% | 77.7% | 14.141 | 4233 | -3.5000 |
| bipia_wami | 98.6% | 9.0% | 94.8% | 13.080 | 2400 | -3.5000 |
| agentdojo_wami | 91.4% | 4.7% | 91.9% | 23.450 | 653 | -3.5000 |
