| Dataset | Method | IR | FPR | ACC | Latency ms | N | Copies |
|---|---|---:|---:|---:|---:|---:|---:|
| InjecAgent | SmoothLLM-style local judge, qwen2.5:7b-instruct, head-tail truncation | 88.0% | 17.6% | 85.7% | 238.7 | 42 | 1 |
| BIPIA | SmoothLLM-style local judge, qwen2.5:7b-instruct, head-tail truncation | 72.0% | 16.0% | 78.0% | 266.7 | 50 | 1 |
| AgentDojo | SmoothLLM-style local judge, qwen2.5:7b-instruct, head-tail truncation | 88.0% | 44.0% | 72.0% | 251.1 | 50 | 1 |

Notes:
- This is a local no-token baseline, not the strict official SmoothVLM implementation.
- The judge model is local Ollama `qwen2.5:7b-instruct`.
- Long prompts are shortened with head-tail truncation, keeping both the user task and the likely injected tail content.
- `IR` is the attack interception rate; `FPR` is the false positive rate on benign samples.
