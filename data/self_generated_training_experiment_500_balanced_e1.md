# Self-Generated Training Data Experiment

- Synthetic training rows: `500`
- Epochs: `1`
- Init model: `wami_agentdojo_current_e3.npz`
- Eval limit per official dataset: `1000`

| Variant | Eval Set | Train N | Eval N | IR | FPR | ACC | Avg ms |
|---|---|---:|---:|---:|---:|---:|---:|
| current_agentdojo_model | InjecAgent | 7286 | 1000 | 91.0% | 0.0% | 95.6% | 2.365 |
| current_agentdojo_model | BIPIA | 7286 | 1000 | 100.0% | 5.2% | 97.4% | 3.447 |
| current_agentdojo_model | AgentDojo | 7286 | 653 | 89.8% | 1.2% | 91.0% | 2.499 |
| current_agentdojo_model | SelfGeneratedHoldout | 7286 | 1000 | 100.0% | 73.8% | 63.1% | 0.875 |
| self_generated_augmented | InjecAgent | 7786 | 1000 | 100.0% | 0.0% | 100.0% | 1.619 |
| self_generated_augmented | BIPIA | 7786 | 1000 | 100.0% | 10.2% | 94.9% | 2.612 |
| self_generated_augmented | AgentDojo | 7786 | 653 | 99.3% | 37.2% | 94.5% | 1.921 |
| self_generated_augmented | SelfGeneratedHoldout | 7786 | 1000 | 100.0% | 15.6% | 92.2% | 1.229 |

The synthetic generator covers benign untrusted-content handling, direct sensitive-tool attacks, cross-tool injection, multi-step context pollution, visual-instruction following, and hidden-goal shift.
