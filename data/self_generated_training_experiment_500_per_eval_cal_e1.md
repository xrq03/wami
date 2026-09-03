# Self-Generated Training Data Experiment

- Synthetic training rows: `500`
- Epochs: `1`
- Init model: `wami_agentdojo_current_e3.npz`
- Eval limit per official dataset: `1000`

- Augmented model calibration set: `per_eval`

- Plan threshold cap: `-0.25`

| Variant | Eval Set | Train N | Eval N | IR | FPR | ACC | Avg ms |
|---|---|---:|---:|---:|---:|---:|---:|
| current_agentdojo_model | InjecAgent | 7286 | 1000 | 90.2% | 0.0% | 95.2% | 2.772 |
| current_agentdojo_model | BIPIA | 7286 | 1000 | 100.0% | 0.2% | 99.9% | 4.178 |
| current_agentdojo_model | AgentDojo | 7286 | 653 | 88.2% | 0.0% | 89.7% | 3.538 |
| current_agentdojo_model | SelfGeneratedHoldout | 7286 | 1000 | 97.6% | 0.0% | 98.8% | 1.694 |
| self_generated_augmented | InjecAgent | 7786 | 1000 | 100.0% | 0.0% | 100.0% | 1.869 |
| self_generated_augmented | BIPIA | 7786 | 1000 | 100.0% | 4.8% | 97.6% | 3.043 |
| self_generated_augmented | AgentDojo | 7786 | 653 | 92.9% | 5.8% | 93.1% | 2.716 |
| self_generated_augmented | SelfGeneratedHoldout | 7786 | 1000 | 100.0% | 2.2% | 98.9% | 1.437 |

The synthetic generator covers benign untrusted-content handling, direct sensitive-tool attacks, cross-tool injection, multi-step context pollution, visual-instruction following, and hidden-goal shift.
