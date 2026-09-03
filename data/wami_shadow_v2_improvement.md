# WAMI Shadow v2 Improvement

This run keeps InjecAgent, BIPIA, and AgentDojo as test-only datasets.

## What Changed

| Item | v1 | v2 |
|---|---|---|
| Train file | `data/shadow_train_2000_seed20260518.jsonl` | `data/shadow_v2_train_3000_b70_seed20260520.jsonl` |
| Validation file | `data/shadow_val_500_seed20260519.jsonl` | `data/shadow_v2_val_800_b70_seed20260521.jsonl` |
| Train size | 2000 | 3000 |
| Validation size | 500 | 800 |
| Benign ratio | 55.0% | 70.0% |
| Hard benign focus | moderate | high: authorized sensitive actions, private-to-user returns, ignored injected instructions |
| Epochs | 5 | 3 |
| Final MI gap | 6.527 | 6.813 |

## Low-FPR Comparison

| Dataset | v1 IR | v1 FPR | v2 IR | v2 FPR | Change |
|---|---:|---:|---:|---:|---|
| InjecAgent | 76.6% | 0.0% | 77.1% | 0.0% | Slight IR improvement; FPR remains clean |
| BIPIA | 83.7% | 0.0% | 98.1% | 0.0% | Major improvement |
| AgentDojo | 68.8% | 3.5% | 78.3% | 4.7% | IR improves, FPR slightly higher |

## High-Recall Comparison

| Dataset | v1 IR | v1 FPR | v2 IR | v2 FPR | Change |
|---|---:|---:|---:|---:|---|
| InjecAgent | 93.3% | 47.1% | 90.6% | 47.1% | Similar FPR bottleneck; v2 slightly lower IR |
| BIPIA | 100.0% | 13.2% | 100.0% | 19.5% | Recall unchanged, FPR worse under high-recall threshold |
| AgentDojo | 100.0% | 12.8% | 100.0% | 10.5% | Same recall, slightly better FPR |

## Current Best Defensible Setting

For a paper row that avoids test-set training, the strongest current setting is the v2+v3 dual MINE ensemble. It uses two independently shadow-trained paper-strict WAMI checkpoints and OR-combines their block decisions.

| Dataset | IR | FPR | ACC | Latency ms |
|---|---:|---:|---:|---:|
| InjecAgent | 80.4% | 0.0% | 90.2% | 43.630 |
| BIPIA | 99.9% | 0.8% | 99.6% | 37.178 |
| AgentDojo | 88.0% | 8.1% | 88.5% | 72.596 |

## v2/v3 Ensemble Gain

| Dataset | Previous best low-FPR | Dual ensemble | Change |
|---|---:|---:|---|
| InjecAgent | 77.1% IR / 0.0% FPR | 80.4% IR / 0.0% FPR | +3.3 pp IR, no FPR cost |
| BIPIA | 98.2% IR / 0.0% FPR | 99.9% IR / 0.8% FPR | +1.7 pp IR, small FPR cost |
| AgentDojo | 83.2% IR / 5.8% FPR | 88.0% IR / 8.1% FPR | +4.8 pp IR, +2.3 pp FPR |

## Remaining Bottleneck

InjecAgent remains the hardest strict-generalization case. The dual ensemble improves it without false positives, but it is still below the in-sample smoke result. The next improvement should add more generated benign and attack trajectories where:

- external content contains suspicious text but the agent explicitly ignores it,
- saved addresses/account/private notes are returned only to the user,
- email/message sending is explicitly requested by the user,
- sensitive tools appear after explicit authorization rather than after `ParseInjectedInstruction`.
