# Self-Generated Training Data Experiment

- Synthetic training rows: `2000`
- Epochs: `3`
- Eval limit per official dataset: `1000`

| Variant | Eval Set | Train N | Eval N | IR | FPR | ACC | Avg ms |
|---|---|---:|---:|---:|---:|---:|---:|
| current_agentdojo_model | InjecAgent | 7286 | 1000 | 91.0% | 0.0% | 95.6% | 2.337 |
| current_agentdojo_model | BIPIA | 7286 | 1000 | 100.0% | 5.2% | 97.4% | 3.450 |
| current_agentdojo_model | AgentDojo | 7286 | 653 | 89.8% | 1.2% | 91.0% | 2.541 |
| current_agentdojo_model | SelfGeneratedHoldout | 7286 | 1000 | 100.0% | 76.6% | 61.7% | 0.836 |
| self_generated_augmented | InjecAgent | 9286 | 1000 | 100.0% | 0.0% | 100.0% | 1.624 |
| self_generated_augmented | BIPIA | 9286 | 1000 | 100.0% | 14.4% | 92.8% | 2.473 |
| self_generated_augmented | AgentDojo | 9286 | 653 | 99.8% | 67.4% | 91.0% | 1.614 |
| self_generated_augmented | SelfGeneratedHoldout | 9286 | 1000 | 100.0% | 0.0% | 100.0% | 1.226 |

The synthetic generator covers benign untrusted-content handling, direct sensitive-tool attacks, cross-tool injection, multi-step context pollution, visual-instruction following, and hidden-goal shift.
