# Self-Generated Training Data Experiment

- Synthetic training rows: `500`
- Epochs: `1`
- Init model: `wami_agentdojo_current_e3.npz`
- Eval limit per official dataset: `1000`

- Augmented model calibration set: `base`

- Plan threshold cap: `-0.25`

| Variant | Eval Set | Train N | Eval N | IR | FPR | ACC | Avg ms |
|---|---|---:|---:|---:|---:|---:|---:|
| current_agentdojo_model | InjecAgent | 7286 | 1000 | 90.2% | 0.0% | 95.2% | 2.384 |
| current_agentdojo_model | BIPIA | 7286 | 1000 | 100.0% | 0.2% | 99.9% | 3.718 |
| current_agentdojo_model | AgentDojo | 7286 | 653 | 88.2% | 0.0% | 89.7% | 3.124 |
| current_agentdojo_model | SelfGeneratedHoldout | 7286 | 1000 | 97.6% | 0.0% | 98.8% | 1.487 |
| self_generated_augmented | InjecAgent | 7286 | 1000 | 100.0% | 0.0% | 100.0% | 1.634 |
| self_generated_augmented | BIPIA | 7286 | 1000 | 100.0% | 6.8% | 96.6% | 2.674 |
| self_generated_augmented | AgentDojo | 7286 | 653 | 98.4% | 25.6% | 95.3% | 2.077 |
| self_generated_augmented | SelfGeneratedHoldout | 7286 | 1000 | 100.0% | 9.4% | 95.3% | 1.243 |

The synthetic generator covers benign untrusted-content handling, direct sensitive-tool attacks, cross-tool injection, multi-step context pollution, visual-instruction following, and hidden-goal shift.
