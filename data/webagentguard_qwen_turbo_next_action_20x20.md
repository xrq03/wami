# WebAgentGuard paper-method sample

This run follows the paper-level idea of WebAgentGuard as a parallel guard agent judging the proposed tool trajectory before execution. It uses an OpenAI-compatible Qwen model as the guard backend, because no official WebAgentGuard implementation/model was found.

| Dataset | Method | Input | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | WebAgentGuard paper-method (qwen-turbo) | next_action | 80.0% | 20.0% | 80.0% | 1883.2 | 40 | 20 | 20 |
| InjecAgent | WebAgentGuard paper-method (qwen-turbo) | next_action | 100.0% | 0.0% | 100.0% | 2078.1 | 40 | 20 | 20 |
