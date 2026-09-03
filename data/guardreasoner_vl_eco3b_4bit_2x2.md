# GuardReasoner-VL Table 1 Baseline

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | Status | Source |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| BIPIA | GuardReasoner-VL official transformers | 100.0% | 100.0% | 50.0% | 73539.223 | 4 | 2 | 2 | official-model-transformers | `D:\论文111\models\guardreasoner-vl-eco-3b` |
| InjecAgent | GuardReasoner-VL official transformers | 100.0% | 100.0% | 50.0% | 70066.368 | 4 | 2 | 2 | official-model-transformers | `D:\论文111\models\guardreasoner-vl-eco-3b` |

## Strictness

- `official-model-transformers` can be reported as an official-model reproduction.
- `adapter-mock` is only a pipeline check and must not be reported as GuardReasoner-VL performance.
- The adapter blocks when GuardReasoner-VL predicts either the user request or the proposed agent response/action as harmful.
