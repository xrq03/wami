# WebAgentGuard paper-method sample

This run follows the paper-level idea of WebAgentGuard as a parallel guard agent judging the proposed tool trajectory before execution. It uses an OpenAI-compatible Qwen model as the guard backend, because no official WebAgentGuard implementation/model was found.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | WebAgentGuard paper-method (qwen-max) | 100.0% | 40.0% | 80.0% | 3597.1 | 10 | 5 | 5 |
| InjecAgent | WebAgentGuard paper-method (qwen-max) | 100.0% | 20.0% | 90.0% | 3885.9 | 10 | 5 | 5 |
