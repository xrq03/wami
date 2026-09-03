# Self-Generated Training Data Experiment

- Synthetic training rows: `500`
- Epochs: `1`
- Init model: `wami_agentdojo_current_e3.npz`
- Eval limit per official dataset: `1000`

- Augmented model calibration set: `base`

| Variant | Eval Set | Train N | Eval N | IR | FPR | ACC | Avg ms |
|---|---|---:|---:|---:|---:|---:|---:|
| current_agentdojo_model | InjecAgent | 7286 | 1000 | 91.0% | 0.0% | 95.6% | 2.631 |
| current_agentdojo_model | BIPIA | 7286 | 1000 | 100.0% | 5.2% | 97.4% | 3.820 |
| current_agentdojo_model | AgentDojo | 7286 | 653 | 89.8% | 1.2% | 91.0% | 3.002 |
| current_agentdojo_model | SelfGeneratedHoldout | 7286 | 1000 | 100.0% | 73.8% | 63.1% | 0.967 |
| self_generated_augmented | InjecAgent | 7286 | 1000 | 100.0% | 0.0% | 100.0% | 1.831 |
| self_generated_augmented | BIPIA | 7286 | 1000 | 100.0% | 10.4% | 94.8% | 2.849 |
| self_generated_augmented | AgentDojo | 7286 | 653 | 99.8% | 39.5% | 94.6% | 2.108 |
| self_generated_augmented | SelfGeneratedHoldout | 7286 | 1000 | 100.0% | 16.8% | 91.6% | 1.360 |

The synthetic generator covers benign untrusted-content handling, direct sensitive-tool attacks, cross-tool injection, multi-step context pollution, visual-instruction following, and hidden-goal shift.
