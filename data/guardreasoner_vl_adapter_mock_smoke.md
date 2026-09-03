# GuardReasoner-VL Table 1 Baseline

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | Status | Source |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| BIPIA | GuardReasoner-VL adapter mock | 100.0% | 0.0% | 100.0% | 0.059 | 4 | 2 | 2 | adapter-mock | `scripts/run_guardreasoner_vl_table1.py` |
| InjecAgent | GuardReasoner-VL adapter mock | 100.0% | 0.0% | 100.0% | 0.014 | 4 | 2 | 2 | adapter-mock | `scripts/run_guardreasoner_vl_table1.py` |
| AgentDojo | GuardReasoner-VL adapter mock | 100.0% | 0.0% | 100.0% | 0.012 | 4 | 2 | 2 | adapter-mock | `scripts/run_guardreasoner_vl_table1.py` |

## Strictness

- `official-model-transformers` can be reported as an official-model reproduction.
- `adapter-mock` is only a pipeline check and must not be reported as GuardReasoner-VL performance.
- The adapter blocks when GuardReasoner-VL predicts either the user request or the proposed agent response/action as harmful.
