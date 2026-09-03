# WebAgentGuard paper-method sample

This run follows the paper-level idea of WebAgentGuard as a parallel guard agent judging the proposed tool trajectory before execution. It uses an OpenAI-compatible Qwen model as the guard backend, because no official WebAgentGuard implementation/model was found.

| Dataset | Method | Input | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | next_action | 100.0% | 40.0% | 80.0% | 350.6 | 50 | 25 | 25 |
| InjecAgent | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | next_action | 100.0% | 0.0% | 100.0% | 371.4 | 50 | 25 | 25 |
