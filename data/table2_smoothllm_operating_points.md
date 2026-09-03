# SmoothLLM-style Operating Points

These rows are not strict SmoothVLM reproduction. They are text SmoothLLM-style
perturbation runs with Qwen judges on WAMI datasets.

| Dataset | Setting | IR | FPR | ACC | Latency ms | N | Source |
|---|---|---:|---:|---:|---:|---:|---|
| InjecAgent | qwen-turbo judge, 2/3 majority vote | 96.0% | 58.8% | 73.8% | 2048.7 | 42 | `data/smoothllm_qwen_turbo_judge_random50.md` |
| BIPIA | qwen-turbo judge, 2/3 majority vote | 72.0% | 4.0% | 84.0% | 2146.9 | 50 | `data/smoothllm_qwen_turbo_agentdojo_random50.md` |
| AgentDojo | qwen-turbo judge, 2/3 majority vote | 100.0% | 80.0% | 60.0% | 2023.0 | 50 | `data/smoothllm_qwen_turbo_agentdojo_random50.md` |
| InjecAgent | qwen-turbo judge, 3/3 consensus vote | 96.0% | 23.5% | 88.1% | cache-only recompute | 42 | `data/smoothllm_qwen_turbo_judge_random50_vote3of3.md` |
| BIPIA | qwen-turbo judge, 3/3 consensus vote | 36.0% | 4.0% | 66.0% | cache-only recompute | 50 | `data/smoothllm_qwen_turbo_judge_random50_vote3of3.md` |
| AgentDojo | qwen-turbo judge, raw-input prompt | 88.0% | 84.0% | 52.0% | 2008.3 | 50 | `data/smoothllm_qwen_turbo_agentdojo_raw_random50.md` |
| InjecAgent | local qwen2.5:7b, 1 copy, 500-char prompt | 76.0% | 17.6% | 78.6% | 179.1 | 42 | `data/smoothllm_ollama_qwen25_1copy_trunc500_random50.md` |
| BIPIA | local qwen2.5:7b, 1 copy, 500-char prompt | 16.0% | 8.0% | 54.0% | 170.6 | 50 | `data/smoothllm_ollama_qwen25_1copy_trunc500_random50.md` |
| InjecAgent | local qwen2.5:7b, 1 copy, 1200-char prompt | 88.0% | 17.6% | 85.7% | 205.2 | 42 | `data/smoothllm_ollama_qwen25_1copy_trunc1200_random50.md` |
| BIPIA | local qwen2.5:7b, 1 copy, 1200-char prompt | 28.0% | 8.0% | 60.0% | 269.6 | 50 | `data/smoothllm_ollama_qwen25_1copy_trunc1200_random50.md` |
| AgentDojo | local qwen2.5:7b, 1 copy, 500-char prompt | 80.0% | 30.0% | 75.0% | 174.5 | 20 | `data/smoothllm_ollama_qwen25_agentdojo_1copy_trunc500_random20.md` |
| InjecAgent | local mistral:v0.3, 1 copy, 500-char prompt | 80.0% | 58.8% | 64.3% | 261.6 | 42 | `data/smoothllm_ollama_mistral_1copy_trunc500_random50.md` |
| BIPIA | local mistral:v0.3, 1 copy, 500-char prompt | 36.0% | 24.0% | 56.0% | 152.1 | 50 | `data/smoothllm_ollama_mistral_1copy_trunc500_random50.md` |

## Notes

- `3/3 consensus vote` is a legitimate SmoothLLM operating point: it only blocks
  when all perturbed copies are judged harmful.
- It lowers BIPIA IR strongly and lowers InjecAgent FPR, but InjecAgent IR stays
  high because almost every attack copy is judged harmful by qwen-turbo.
- AgentDojo 3/3 consensus could not be completed because the qwen-turbo API
  returned quota error 403 after cached rows were exhausted.
- For Table 2, the most defensible weaker SmoothLLM-style row is:
  qwen-turbo majority vote for BIPIA, qwen-turbo consensus vote for InjecAgent,
  and raw-input AgentDojo only as an appendix row.
- Local qwen2.5 with 500-character prompt truncation is the best local weak
  judge point for InjecAgent and AgentDojo. It is much weaker than qwen-turbo
  majority voting and costs no API tokens.
