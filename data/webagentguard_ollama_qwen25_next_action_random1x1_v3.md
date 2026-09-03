# WebAgentGuard paper-method sample

This run follows the paper-level idea of WebAgentGuard as a parallel guard agent judging the proposed tool trajectory before execution. It uses an OpenAI-compatible Qwen model as the guard backend, because no official WebAgentGuard implementation/model was found.

| Dataset | Method | Input | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | next_action | 100.0% | 0.0% | 100.0% | 406.5 | 2 | 1 | 1 |
| InjecAgent | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | next_action | 100.0% | 0.0% | 100.0% | 385.5 | 2 | 1 | 1 |
