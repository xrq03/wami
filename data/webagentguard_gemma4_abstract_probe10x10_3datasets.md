# WebAgentGuard paper-method sample

This run follows the paper-level idea of WebAgentGuard as a parallel guard agent judging the proposed tool trajectory before execution. It uses an OpenAI-compatible Qwen model as the guard backend, because no official WebAgentGuard implementation/model was found.

| Dataset | Method | Input | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | WebAgentGuard paper-method (ollama:gemma4:26b) | next_action_abstract | 0.0% | 0.0% | 50.0% | 4760.7 | 20 | 10 | 10 |
| InjecAgent | WebAgentGuard paper-method (ollama:gemma4:26b) | next_action_abstract | 0.0% | 0.0% | 50.0% | 4005.1 | 20 | 10 | 10 |
| AgentDojo | WebAgentGuard paper-method (ollama:gemma4:26b) | next_action_abstract | 0.0% | 0.0% | 50.0% | 3947.7 | 20 | 10 | 10 |
