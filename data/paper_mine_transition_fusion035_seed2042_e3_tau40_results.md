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
| injecagent_wami | 73.3% | 23.5% | 74.9% | 16.164 | 4233 | -4.0000 |
| bipia_wami | 97.7% | 5.2% | 96.2% | 14.806 | 2400 | -4.0000 |
| agentdojo_wami | 99.6% | 11.6% | 98.2% | 25.898 | 653 | -4.0000 |
