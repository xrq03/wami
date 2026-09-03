# WebAgentGuard paper-method sample

This run follows the paper-level idea of WebAgentGuard as a parallel guard agent judging the proposed tool trajectory before execution. It uses an OpenAI-compatible Qwen model as the guard backend, because no official WebAgentGuard implementation/model was found.

| Dataset | Method | Input | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | next_action_abstract | 48.0% | 4.0% | 72.0% | 419.1 | 50 | 25 | 25 |
| InjecAgent | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | next_action_abstract | 100.0% | 0.0% | 100.0% | 362.7 | 50 | 25 | 25 |
| AgentDojo | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | next_action_abstract | 100.0% | 80.0% | 60.0% | 326.0 | 50 | 25 | 25 |
