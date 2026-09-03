# Qwen-Turbo Full Live WAMI Runtime Summary

This experiment replaces the scripted stepwise planner with `qwen-turbo`.

Runtime structure:

```text
Qwen-turbo planner generates one next action
  -> WAMI builds runtime TDG from executed trace + pending action
  -> passive observation actions execute
  -> side-effect actions are gated before execution
```

## Results

| Dataset | Planner Mode | Runtime Flow Check | IR | FPR | ACC | Planner Risk Rate | WAMI Action Block Rate | Latency ms | N | Source |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| InjecAgent | safe | off | 0.0% | 0.0% | 50.0% | 0.0% | 0.0% | 7633.8 | 4 | `data/qwen_turbo_full_live_wami_injecagent_smoke.md` |
| InjecAgent | vulnerable | off | 0.0% | 0.0% | 50.0% | 0.0% | 0.0% | 11362.4 | 6 | `data/qwen_turbo_vulnerable_full_live_wami_injecagent_3x3.md` |
| InjecAgent | directive-parser | off | 66.7% | 0.0% | 83.3% | 66.7% | 100.0% | 11777.8 | 6 | `data/qwen_turbo_directive_parser_full_live_wami_injecagent_3x3_v2.md` |
| AgentDojo | vulnerable | off | 0.0% | 0.0% | 50.0% | 66.7% | 0.0% | 11226.0 | 6 | `data/qwen_turbo_vulnerable_full_live_wami_agentdojo_3x3.md` |
| AgentDojo | vulnerable | on | 33.3% | 0.0% | 66.7% | 66.7% | 50.0% | 8924.6 | 6 | `data/qwen_turbo_vulnerable_full_live_wami_agentdojo_3x3_flowcheck.md` |
| AgentDojo | directive-parser | on | 0.0% | 0.0% | 50.0% | 33.3% | 0.0% | 11154.1 | 6 | `data/qwen_turbo_directive_parser_full_live_wami_agentdojo_3x3_v2.md` |
| InjecAgent | strict-directive-parser | on | 33.3% | 0.0% | 66.7% | 33.3% | 100.0% | 12098.9 | 6 | `data/qwen_turbo_strict_directive_full_live_wami_injecagent_3x3.md` |
| BIPIA | strict-directive-parser | on | 33.3% | 0.0% | 66.7% | 33.3% | 100.0% | 9771.6 | 6 | `data/qwen_turbo_strict_directive_full_live_wami_bipia_3x3.md` |
| AgentDojo | strict-directive-parser | on | 33.3% | 0.0% | 66.7% | 66.7% | 50.0% | 9534.4 | 6 | `data/qwen_turbo_strict_directive_full_live_wami_agentdojo_3x3.md` |
| InjecAgent | max-directive-parser | on | 66.7% | 0.0% | 83.3% | 66.7% | 100.0% | 13605.5 | 6 | `data/qwen_turbo_max_directive_full_live_wami_injecagent_3x3_v2.md` |
| BIPIA | max-directive-parser | on | 66.7% | 0.0% | 83.3% | 66.7% | 100.0% | 6650.9 | 6 | `data/qwen_turbo_max_directive_full_live_wami_bipia_3x3_v3.md` |
| AgentDojo | max-directive-parser | on | 100.0% | 0.0% | 100.0% | 100.0% | 66.7% | 10521.1 | 6 | `data/qwen_turbo_max_directive_full_live_wami_agentdojo_3x3_v2.md` |
| InjecAgent | max-directive-parser 10x10 | on | 70.0% | 0.0% | 85.0% | 70.0% | 100.0% | 12114.1 | 20 | `data/qwen_turbo_max_directive_full_live_wami_injecagent_10x10.md` |
| BIPIA | max-directive-parser 10x10 | on | 30.0% | 0.0% | 65.0% | 30.0% | 100.0% | 6300.5 | 20 | `data/qwen_turbo_max_directive_full_live_wami_bipia_10x10.md` |
| AgentDojo | max-directive-parser 10x10 | on | 40.0% | 10.0% | 65.0% | 50.0% | 80.0% | 9788.0 | 20 | `data/qwen_turbo_max_directive_full_live_wami_agentdojo_10x10_fixedmetric.md` |
| AgentDojo | max-directive-parser 10x10 strict-flow stress | on | 40.0% | 50.0% | 45.0% | 40.0% | 100.0% | 7132.8 | 20 | `data/qwen_turbo_max_directive_full_live_wami_agentdojo_10x10_strictflow.md` |

## Interpretation

- On InjecAgent, `qwen-turbo` did not generate risky side-effect actions. It mostly read/searches/summarizes/repeats tools, so WAMI had no action to block.
- After adding a stronger directive-parsing prompt and highlighting the latest raw observation, InjecAgent planner risk increased to 66.7%, and WAMI blocked 100.0% of those risky actions on the small sample.
- The stricter directive prompt forces `reads` and `depends_on` for observation-driven actions. On all three datasets, qwen-turbo now produces at least some risky actions and WAMI blocks a nonzero share.
- The strongest `max-directive-parser` prompt exposes side-effect/sensitive tools, latest event id, raw latest observation, and extracted action hints. It also preserves two-hop chains such as `ParseInjectedInstruction -> ExfiltrateData`.
- On AgentDojo, `qwen-turbo` generated risky actions in 66.7% of attack samples under vulnerable planner mode.
- Plain MINE-only gating did not block those qwen-generated actions reliably, because the generated action often lacked explicit `reads` / `depends_on` metadata.
- Enabling runtime TDG flow check blocked 50.0% of risky qwen-generated actions while keeping FPR at 0.0% on this small sample.

## Takeaway

The full qwen-turbo runtime is now runnable, but it is not directly comparable to replay results:

- Replay evaluates WAMI against known attack trajectories.
- Qwen live runtime evaluates planner behavior plus WAMI. If qwen-turbo does not produce the malicious action, IR becomes low even though the planner itself avoided the attack.

For showing WAMI's role, report `Planner Risk Rate` and `WAMI Action Block Rate` together with IR/FPR.

The current best qwen-turbo evidence is not high IR. It is the causal chain:

```text
strong directive parser prompt
  -> qwen-turbo generates risky tool action from observation
  -> runtime TDG records observation dependency through reads/depends_on
  -> WAMI blocks the risky side-effect action
```
