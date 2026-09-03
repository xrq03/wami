# LLM Shadow Attack Generation Design

The shadow adversarial training pipeline now supports both local template
generation and LLM-generated attack plans.

## Attack Classes

| Attack kind | Meaning |
|---|---|
| `cross_tool_injection` | A benign tool result carries an instruction that changes a later tool call |
| `multi_step_indirect_injection` | The malicious instruction propagates through several intermediate steps |
| `visual_injection` | The injected instruction is represented as visual/OCR content |
| `context_pollution` | Untrusted context contaminates later reasoning or responses |
| `hidden_goal_shift` | The plan gradually shifts from the user objective to a hidden objective |
| `sensitive_tool_hijack` | A high-risk tool is redirected toward attacker-controlled behavior |

## Implementation

- Local fallback: `wami.shadow_llm.local_shadow_attacks`
- LLM generation: `wami.shadow_llm.generate_llm_shadow_attacks`
- CLI: `scripts/generate_llm_shadow_attacks.py`
- Merge utility: `scripts/merge_shadow_training_data.py`

## Training Integration

`train_shadow` now builds an attack bank from `label=1` samples. For each benign
sample, if generated attacks share the same intent, one attack plan is sampled
as the negative trajectory. Otherwise, the original `perturb_tdg` fallback is
used.

This makes shadow adversarial training support:

- LLM-generated diverse attacks.
- Cross-tool injection.
- Multi-step indirect injection.
- Visual injection.
- Context pollution.
- Hidden goal migration.
- Sensitive tool hijacking.
