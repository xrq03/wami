# Self-Generated Training Data Experiment

- Synthetic training rows: `500`
- Epochs: `1`
- Init model: `wami_agentdojo_current_e3.npz`
- Eval limit per official dataset: `1000`

- Augmented model calibration set: `per_eval`

- Plan threshold cap: `-0.6`

| Variant | Eval Set | Train N | Eval N | IR | FPR | ACC | Avg ms |
|---|---|---:|---:|---:|---:|---:|---:|
| current_agentdojo_model | InjecAgent | 7286 | 1000 | 90.2% | 0.0% | 95.2% | 2.740 |
| current_agentdojo_model | BIPIA | 7286 | 1000 | 100.0% | 0.0% | 100.0% | 4.125 |
| current_agentdojo_model | AgentDojo | 7286 | 653 | 84.1% | 0.0% | 86.2% | 4.332 |
| current_agentdojo_model | SelfGeneratedHoldout | 7286 | 1000 | 78.8% | 0.0% | 89.4% | 2.091 |
| self_generated_augmented | InjecAgent | 7786 | 1000 | 99.8% | 0.0% | 99.9% | 1.870 |
| self_generated_augmented | BIPIA | 7786 | 1000 | 100.0% | 1.2% | 99.4% | 3.435 |
| self_generated_augmented | AgentDojo | 7786 | 653 | 92.4% | 3.5% | 93.0% | 2.910 |
| self_generated_augmented | SelfGeneratedHoldout | 7786 | 1000 | 100.0% | 0.0% | 100.0% | 1.460 |

The synthetic generator covers benign untrusted-content handling, direct sensitive-tool attacks, cross-tool injection, multi-step context pollution, visual-instruction following, and hidden-goal shift.
