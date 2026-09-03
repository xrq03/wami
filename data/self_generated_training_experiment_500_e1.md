# Self-Generated Training Data Experiment

- Synthetic training rows: `500`
- Epochs: `1`
- Init model: `wami_agentdojo_current_e3.npz`
- Eval limit per official dataset: `1000`

| Variant | Eval Set | Train N | Eval N | IR | FPR | ACC | Avg ms |
|---|---|---:|---:|---:|---:|---:|---:|
| current_agentdojo_model | InjecAgent | 7286 | 1000 | 91.0% | 0.0% | 95.6% | 2.310 |
| current_agentdojo_model | BIPIA | 7286 | 1000 | 100.0% | 5.2% | 97.4% | 3.456 |
| current_agentdojo_model | AgentDojo | 7286 | 653 | 89.8% | 1.2% | 91.0% | 2.480 |
| current_agentdojo_model | SelfGeneratedHoldout | 7286 | 1000 | 100.0% | 76.6% | 61.7% | 0.832 |
| self_generated_augmented | InjecAgent | 7786 | 1000 | 100.0% | 0.0% | 100.0% | 1.659 |
| self_generated_augmented | BIPIA | 7786 | 1000 | 100.0% | 10.8% | 94.6% | 2.551 |
| self_generated_augmented | AgentDojo | 7786 | 653 | 99.5% | 38.4% | 94.5% | 1.841 |
| self_generated_augmented | SelfGeneratedHoldout | 7786 | 1000 | 100.0% | 1.4% | 99.3% | 1.230 |

The synthetic generator covers benign untrusted-content handling, direct sensitive-tool attacks, cross-tool injection, multi-step context pollution, visual-instruction following, and hidden-goal shift.
