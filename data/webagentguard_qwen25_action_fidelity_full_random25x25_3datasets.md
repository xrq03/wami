# WebAgentGuard paper-method sample

This run follows the paper-level idea of WebAgentGuard as a parallel guard agent judging the proposed tool trajectory before execution. It uses an OpenAI-compatible Qwen model as the guard backend, because no official WebAgentGuard implementation/model was found.

| Dataset | Method | Input | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | full_trajectory | 100.0% | 4.0% | 98.0% | 902.3 | 50 | 25 | 25 |
| InjecAgent | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | full_trajectory | 100.0% | 0.0% | 100.0% | 821.1 | 50 | 25 | 25 |
| AgentDojo | WebAgentGuard paper-method (ollama:qwen2.5:7b-instruct) | full_trajectory | 100.0% | 20.0% | 90.0% | 771.1 | 50 | 25 | 25 |
