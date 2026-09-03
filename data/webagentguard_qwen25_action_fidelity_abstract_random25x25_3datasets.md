# WebAgentGuard paper-method sample

This run follows the paper-level idea of WebAgentGuard as a parallel guard agent judging the proposed tool trajectory before execution. It uses an OpenAI-compatible Qwen model as the guard backend, because no official WebAgentGuard implementation/model was found.

| Dataset | Method | Input | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | next_action_abstract | 24.0% | 0.0% | 62.0% | 790.5 | 50 | 25 | 25 |
| InjecAgent | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | next_action_abstract | 100.0% | 0.0% | 100.0% | 745.9 | 50 | 25 | 25 |
| AgentDojo | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | next_action_abstract | 100.0% | 44.0% | 78.0% | 722.8 | 50 | 25 | 25 |
