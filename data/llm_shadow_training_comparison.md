# LLM Shadow Training Comparison

- Data: `data/current_agentdojo_with_llm_shadow_10x6.jsonl`

| Variant | IR | FPR | ACC | N | Model |
|---|---:|---:|---:|---:|---|
| without_llm_shadow_training | 89.2% | 3.5% | 90.0% | 713 | `wami_agentdojo_current_e3.npz` |
| with_llm_shadow_training | 84.5% | 2.3% | 86.1% | 713 | `wami_current_agentdojo_llm_shadow_10x6_e2.npz` |
