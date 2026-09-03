# WebAgentGuard paper-method sample

This run follows the paper-level idea of WebAgentGuard as a parallel guard agent judging the proposed tool trajectory before execution. It uses an OpenAI-compatible Qwen model as the guard backend, because no official WebAgentGuard implementation/model was found.

| Dataset | Method | Input | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | next_action_abstract | 24.0% | 2.0% | 61.0% | 580.0 | 100 | 50 | 50 |
| InjecAgent | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | next_action_abstract | 96.0% | 0.0% | 98.0% | 579.7 | 100 | 50 | 50 |
| AgentDojo | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | next_action_abstract | 98.0% | 36.0% | 81.0% | 537.7 | 100 | 50 | 50 |
