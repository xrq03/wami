# WebAgentGuard paper-method sample

This run follows the paper-level idea of WebAgentGuard as a parallel guard agent judging the proposed tool trajectory before execution. It uses an OpenAI-compatible Qwen model as the guard backend, because no official WebAgentGuard implementation/model was found.

| Dataset | Method | Input | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | WebAgentGuard paper-method (ollama:mistral:v0.3) | next_action | 36.0% | 0.0% | 68.0% | 877.7 | 50 | 25 | 25 |
| InjecAgent | WebAgentGuard paper-method (ollama:mistral:v0.3) | next_action | 76.0% | 0.0% | 88.0% | 788.2 | 50 | 25 | 25 |
| AgentDojo | WebAgentGuard paper-method (ollama:mistral:v0.3) | next_action | 48.0% | 0.0% | 74.0% | 753.5 | 50 | 25 | 25 |
