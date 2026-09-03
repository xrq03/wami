# GuardReasoner-VL Table 1 Baseline

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | Status | Source |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| BIPIA | GuardReasoner-VL official transformers | 100.0% | 0.0% | 100.0% | 21054.964 | 2 | 1 | 1 | official-model-transformers | `models\guardreasoner-vl-eco-3b` |
| InjecAgent | GuardReasoner-VL official transformers | 0.0% | 0.0% | 50.0% | 22070.208 | 2 | 1 | 1 | official-model-transformers | `models\guardreasoner-vl-eco-3b` |
| AgentDojo | GuardReasoner-VL official transformers | 100.0% | 0.0% | 100.0% | 19427.839 | 2 | 1 | 1 | official-model-transformers | `models\guardreasoner-vl-eco-3b` |

## Strictness

- `official-model-transformers` can be reported as an official-model reproduction.
- `adapter-mock` is only a pipeline check and must not be reported as GuardReasoner-VL performance.
- The adapter defaults to blocking from GuardReasoner-VL's assistant response/action label, not the user-request label, because these agent datasets often contain benign user requests over private tools.
