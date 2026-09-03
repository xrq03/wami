# Llama-Guard 3 8B Ollama baseline

Model: `llama-guard3:8b`

| Dataset | IR | FPR | ACC | Latency ms/sample | N | Attack | Benign |
|---|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | 12.0% | 1.0% | 55.5% | 2312.2 | 200 | 100 | 100 |
| InjecAgent | 77.0% | 0.0% | 88.5% | 2257.6 | 200 | 100 | 100 |
| AgentDojo | 67.0% | 11.6% | 76.9% | 2250.3 | 186 | 100 | 86 |
