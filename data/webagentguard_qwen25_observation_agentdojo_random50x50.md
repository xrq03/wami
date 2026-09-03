# WebAgentGuard paper-method sample

This run follows the paper-level idea of WebAgentGuard as a parallel guard agent judging the proposed tool trajectory before execution. It uses an OpenAI-compatible Qwen model as the guard backend, because no official WebAgentGuard implementation/model was found.

| Dataset | Method | Input | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| AgentDojo | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | observation_only | 94.0% | 8.0% | 93.0% | 5491.9 | 100 | 50 | 50 |
