# WebAgentGuard paper-method sample

This run follows the paper-level idea of WebAgentGuard as a parallel guard agent judging the proposed tool trajectory before execution. It uses an OpenAI-compatible Qwen model as the guard backend, because no official WebAgentGuard implementation/model was found.

| Dataset | Method | Input | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| AgentDojo | WebAgentGuard paper-method (ollama:mistral:v0.3) | next_action_abstract | 56.0% | 0.0% | 78.0% | 5520.6 | 100 | 50 | 50 |
