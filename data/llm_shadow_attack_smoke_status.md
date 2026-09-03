# LLM Shadow Attack Smoke Status

## Generated Files

| File | Description |
|---|---|
| `data/local_shadow_attacks_agentdojo_smoke.jsonl` | Local fallback shadow attacks, 3 benign samples x 6 attack kinds |
| `data/llm_shadow_attacks_agentdojo_qwen_smoke.jsonl` | Qwen-generated shadow attacks, 3 benign samples x 6 attack kinds |
| `data/agentdojo_with_llm_shadow_smoke.jsonl` | AgentDojo data merged with Qwen shadow attacks |
| `wami_agentdojo_llm_shadow_smoke_e1.npz` | One-epoch smoke model trained with the merged LLM shadow bank |

## Attack Coverage

The generated attacks cover:

- `cross_tool_injection`
- `multi_step_indirect_injection`
- `visual_injection`
- `context_pollution`
- `hidden_goal_shift`
- `sensitive_tool_hijack`

## Smoke Training Result

```text
epoch=001 loss=1.3797 mi_gap=0.0176 world_loss=0.1478
IR=0.839 FPR=0.012 ACC=0.858 total=671
```

This is a smoke test, not a final tuned model. Its purpose is to verify that
LLM-generated shadow plans are saved, merged, and sampled as negative
trajectories during WAMI shadow adversarial training.
