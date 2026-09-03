# GuardReasoner-VL Table 1 Baseline

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | Status | Source |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| BIPIA | GuardReasoner-VL official transformers | 40.0% | 60.0% | 40.0% | 22320.686 | 10 | 5 | 5 | official-model-transformers | `models\guardreasoner-vl-eco-3b` |

## Strictness

- `official-model-transformers` can be reported as an official-model reproduction.
- `adapter-mock` is only a pipeline check and must not be reported as GuardReasoner-VL performance.
- The adapter defaults to blocking from GuardReasoner-VL's assistant response/action label, not the user-request label, because these agent datasets often contain benign user requests over private tools.
