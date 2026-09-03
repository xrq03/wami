# Qwen-Turbo Max Directive Parser 10x10 Summary

This run expands the strongest qwen-turbo live runtime setting to 10 attack + 10 benign samples per dataset.

Configuration:

```powershell
--model qwen-turbo
--planner-mode max-directive-parser
--use-runtime-flow-check
--max-steps 5
```

## Results

| Dataset | IR | FPR | ACC | Planner Risk Rate | WAMI Action Block Rate | Latency ms | N | Source |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| InjecAgent | 70.0% | 0.0% | 85.0% | 70.0% | 100.0% | 12114.1 | 20 | `data/qwen_turbo_max_directive_full_live_wami_injecagent_10x10.md` |
| BIPIA | 30.0% | 0.0% | 65.0% | 30.0% | 100.0% | 6300.5 | 20 | `data/qwen_turbo_max_directive_full_live_wami_bipia_10x10.md` |
| AgentDojo | 40.0% | 10.0% | 65.0% | 50.0% | 80.0% | 9788.0 | 20 | `data/qwen_turbo_max_directive_full_live_wami_agentdojo_10x10_fixedmetric.md` |

## Interpretation

- InjecAgent: best live qwen-turbo result so far. When qwen-turbo generates a risky action, WAMI blocks all of them.
- BIPIA: WAMI blocks all risky actions qwen-turbo generates, but qwen-turbo only generates risky actions in 30% of attack samples.
- AgentDojo: after fixing the risky-action block accounting, WAMI blocks 80.0% of qwen-generated risky attack actions. End-to-end IR remains 40.0% because qwen-turbo only produces risky actions in 50.0% of attack samples. One benign side-effect plan is blocked, so FPR is 10.0%.

## Strict Flow Stress Point

An additional strict side-effect dependency flow mode was tested:

| Dataset | IR | FPR | Planner Risk Rate | WAMI Action Block Rate | Source |
|---|---:|---:|---:|---:|---|
| AgentDojo | 40.0% | 50.0% | 40.0% | 100.0% | `data/qwen_turbo_max_directive_full_live_wami_agentdojo_10x10_strictflow.md` |

This shows WAMI can force risky-action blocking to 100%, but the mode is too strict for a main result because FPR increases to 50%.

## Key Point

The live qwen-turbo experiment is dominated by planner behavior:

```text
IR ~= Planner Risk Rate x WAMI Action Block Rate
```

For WAMI-focused reporting, use both:

- replay/full-runtime scripted results for WAMI's action-gating ability;
- qwen-turbo live results as a small case study showing the end-to-end planner/runtime interaction.
