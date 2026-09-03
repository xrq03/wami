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
| injecagent_wami | 71.0% | 11.8% | 79.6% | 15.876 | 4233 | -4.5000 |
| bipia_wami | 97.2% | 1.2% | 98.0% | 14.761 | 2400 | -4.5000 |
| agentdojo_wami | 96.8% | 8.1% | 96.2% | 27.804 | 653 | -4.5000 |
