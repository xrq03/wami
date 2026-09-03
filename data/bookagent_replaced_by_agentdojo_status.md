# BookAgent replacement with AgentDojo

## Decision

BookAgent is removed from the formal Table 1 reproduction because the provided BookAgent PDF is about safety-aware visual storybook generation, not prompt-injection defense for tool agents.

Replacement target:

| Old baseline | Replacement baseline |
|---|---|
| BookAgent | AgentDojo Transformers PI Detector |

## Why AgentDojo is a better replacement

AgentDojo is an open-source benchmark/framework for evaluating prompt injection attacks and defenses in LLM agents. Its official defenses include:

| Defense | Official AgentDojo name | Relevance |
|---|---|---|
| Tool filtering | `tool_filter` | Filters tools to those relevant to user task |
| Prompt injection detector | `transformers_pi_detector` | Detects prompt injection in tool outputs |
| Prompt repetition | `repeat_user_prompt` | Reinforces user instruction after tool results |
| Spotlighting | `spotlighting_with_delimiting` | Delimits tool outputs and tells the agent not to follow them |

For replacing BookAgent, the best first choice is `transformers_pi_detector`, because it is a concrete open-source prompt-injection defense. AgentDojo's code uses:

`protectai/deberta-v3-base-prompt-injection-v2`

with the rule:

`is_injection = safety_score < threshold`

where the default threshold is `0.5`.

## Implementation added

Script:

`scripts/run_agentdojo_pi_detector_table1.py`

This script adapts the official AgentDojo detector logic to the local BIPIA, InjecAgent, and AgentDojo JSONL datasets.

## Current run status

Attempted command:

`uv run --with numpy --with torch --with transformers --with sentencepiece python .\scripts\run_agentdojo_pi_detector_table1.py --attack-n 5 --benign-n 5`

Result:

The HuggingFace model download/load did not finish within 15 minutes. The cache directory now contains a partial/started model cache:

`C:\Users\ruoan\.cache\huggingface\hub\models--protectai--deberta-v3-base-prompt-injection-v2`

No final IR/FPR result was produced yet.

## Next options

1. Let the same command run longer until the HuggingFace model finishes downloading.
2. Manually download `protectai/deberta-v3-base-prompt-injection-v2` into the HuggingFace cache.
3. Use a smaller available prompt-injection detector as a temporary AgentDojo-compatible fallback, clearly labeled as fallback.
4. Run AgentDojo's `tool_filter` with the official AgentDojo benchmark harness instead, but this requires a full LLM agent execution environment rather than direct JSONL classification.

