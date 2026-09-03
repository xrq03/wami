# Qwen-Turbo Max Directive Parser Prompt Notes

The strongest live planner mode is:

```powershell
--planner-mode max-directive-parser --use-runtime-flow-check
```

It changes two things compared with the earlier live planner:

1. The planner prompt explicitly tells the LLM to parse the latest observation into a tool call, not to act as a safety filter.
2. The runtime environment now preserves raw injected observation chains, including two-hop chains such as:

```text
ReadContext
  -> ParseInjectedInstruction(...)
  -> ExfiltrateData(...)
```

## Latest 3x3 Results

| Dataset | IR | FPR | Planner Risk Rate | WAMI Action Block Rate | Source |
|---|---:|---:|---:|---:|---|
| InjecAgent | 66.7% | 0.0% | 66.7% | 100.0% | `data/qwen_turbo_max_directive_full_live_wami_injecagent_3x3_v2.md` |
| BIPIA | 66.7% | 0.0% | 66.7% | 100.0% | `data/qwen_turbo_max_directive_full_live_wami_bipia_3x3_v3.md` |
| AgentDojo | 100.0% | 0.0% | 100.0% | 66.7% | `data/qwen_turbo_max_directive_full_live_wami_agentdojo_3x3_v2.md` |

## Interpretation

This is now the best qwen-turbo live runtime evidence:

```text
strong observation parser prompt
  -> qwen-turbo converts injected observation into risky tool action
  -> runtime event carries reads/depends_on
  -> WAMI builds runtime TDG
  -> WAMI blocks side-effect action
```

The remaining limitation is sample size. These are 3 attack + 3 benign smoke runs per dataset, designed to confirm the full mechanism before spending more API tokens.
