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
| injecagent_wami | 69.6% | 5.9% | 81.9% | 16.765 | 4233 | -4.7500 |
| bipia_wami | 97.0% | 0.2% | 98.4% | 14.899 | 2400 | -4.7500 |
| agentdojo_wami | 94.7% | 7.0% | 94.5% | 25.827 | 653 | -4.7500 |
