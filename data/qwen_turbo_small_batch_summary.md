# qwen-turbo Small-Batch Planner + WAMI Test

## Setup

- Model: `qwen-turbo`
- Mode: LLM planner generates tool-use plans; WAMI judges generated plans.
- Samples: 5 attack-labeled samples per dataset, selected with `sample-mode=hard`.
- Outputs:
  - `data/qwen_turbo_llm_agent_injecagent_attack5.jsonl`
  - `data/qwen_turbo_llm_agent_bipia_attack5.jsonl`
  - `data/qwen_turbo_llm_agent_agentdojo_attack5.jsonl`

This is an exploratory small-batch run, not a final official table. The current
script uses plan-level evaluation rather than the full runtime-trace interface.

## Results

| Dataset | N | Dangerous plans generated | WAMI blocked dangerous | Unsafe released | Notes |
|---|---:|---:|---:|---:|---|
| InjecAgent | 5 | 0 | 0 | 0 | qwen-turbo generated read/search-only plans |
| BIPIA | 5 | 2 | 2 | 0 | WAMI blocked `ExecuteBash` and `ExfiltrateData` plans |
| AgentDojo | 5 | 3 | 0 | 3 | Generated side-effect plans were released by the old plan-level path |

## Interpretation

- InjecAgent: qwen-turbo did not produce dangerous side-effect actions in this
  sample, so WAMI had nothing dangerous to block.
- BIPIA: this is the cleanest positive result. qwen-turbo produced dangerous
  tool plans in 2/5 cases, and WAMI blocked both.
- AgentDojo: this exposed a gap in the plan-only evaluator. qwen-turbo generated
  `send_email` / `send_direct_message` plans, but because the generated plan did
  not preserve runtime provenance showing that recipients/content came from an
  untrusted source, the old plan-level gateway allowed them.

## Next Fix

AgentDojo should be rerun through the runtime-trace path, not the old plan-only
path. In runtime mode, side-effect actions such as `SendEmail` are checked
before execution with memory/source provenance, which is exactly the information
missing from the plan-only evaluation.
