# Paper-Faithful MINE-Dominant WAMI

- Blocking source: plan-level and trajectory-level MINE scores.
- Tool/security heuristics are margins only, not direct veto rules.
- Validation data: `.\data\paper_shadow_val_paired_v2_seed2042.jsonl`
- Target FPR on generated validation: `0.05`
- Risk margin: `0.15`
- Passive margin: `0.1`

- Transition MINE: `True`

- Transition fusion: `0.35`

| Dataset | IR | FPR | ACC | Latency ms | N | Tau |
|---|---:|---:|---:|---:|---:|---:|
| injecagent_wami | 76.0% | 23.5% | 76.2% | 15.992 | 4233 | -3.5000 |
| bipia_wami | 97.9% | 8.2% | 94.9% | 14.770 | 2400 | -3.5000 |
| agentdojo_wami | 100.0% | 12.8% | 98.3% | 24.071 | 653 | -3.5000 |
