# WebAgentGuard paper-method sample

This run follows the paper-level idea of WebAgentGuard as a parallel guard agent judging the proposed tool trajectory before execution. It uses an OpenAI-compatible Qwen model as the guard backend, because no official WebAgentGuard implementation/model was found.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | WebAgentGuard paper-method (qwen-turbo) | 100.0% | 40.0% | 80.0% | 2125.3 | 10 | 5 | 5 |
| InjecAgent | WebAgentGuard paper-method (qwen-turbo) | 100.0% | 0.0% | 100.0% | 2026.7 | 10 | 5 | 5 |
