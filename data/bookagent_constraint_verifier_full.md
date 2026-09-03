# BookAgent-Style Constraint Verifier

This adapts BookAgent's VAS/ICR/TCC safety-constraint pipeline to agent trajectory defense.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| BIPIA | BookAgent-style Constraint Verifier | 92.8% | 0.0% | 96.4% | 0.101 | 2400 | 1200 | 1200 | method-level-bookagent-constraints |
| InjecAgent | BookAgent-style Constraint Verifier | 69.7% | 0.0% | 84.9% | 0.064 | 4233 | 2108 | 2125 | method-level-bookagent-constraints |
| AgentDojo | BookAgent-style Constraint Verifier | 60.0% | 3.5% | 64.8% | 0.093 | 653 | 567 | 86 | method-level-bookagent-constraints |

## Mapping

- VAS maps to extracting allowed actions, sensitive entities, destination constraints, and readonly constraints from the user intent.
- Safety auditing maps to checking external/tool-output content for instruction-like contamination.
- ICR verify-revise maps to rejecting untrusted-to-side-effect transitions.
- TCC maps to sequence-level checks for goal drift and sensitive-data flow across steps.
