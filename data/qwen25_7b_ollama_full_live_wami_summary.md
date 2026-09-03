# Local Ollama Qwen2.5 7B Full Live WAMI Summary

Planner: `qwen2.5:7b-instruct` through local Ollama.

Mode: full live runtime. The planner generates one action at a time, WAMI builds the runtime TDG from executed/pending actions, and side-effect actions are gated before execution.

| Dataset | Local model | Samples | IR | FPR | ACC | Planner Risk Rate | WAMI Action Block Rate | Avg latency ms | Avg steps | Source |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| InjecAgent | qwen2.5:7b-instruct | 50 attack + 50 benign | 76.0% | 0.0% | 88.0% | 76.0% | 100.0% | 5656.2 | 1.97 | `data/qwen25_7b_ollama_full_live_wami_injecagent_50x50.csv` |
| BIPIA | qwen2.5:7b-instruct | 50 attack + 50 benign | 80.0% | 0.0% | 90.0% | 80.0% | 100.0% | 2063.6 | 1.50 | `data/qwen25_7b_ollama_full_live_wami_bipia_bootstrap_50x50.csv` |
| AgentDojo | qwen2.5:7b-instruct | 50 attack + 50 benign | 46.0% | 4.0% | 71.0% | 46.0% | 100.0% | 3765.7 | 1.81 | `data/qwen25_7b_ollama_full_live_wami_agentdojo_50x50.csv` |

## Interpretation

`IR` is the final attack interception rate over attack samples. In full live-agent mode it is bounded by whether the planner actually produces a dangerous action.

`Planner Risk Rate` is the percentage of attack samples where the local planner generated at least one side-effect/sensitive action.

`WAMI Action Block Rate` is the percentage of planner-generated dangerous attack actions that WAMI blocked. In these three local batches, WAMI blocked 100.0% of the dangerous actions that the local planner actually emitted.

BIPIA uses `--bootstrap-first-observation` because its attack is injected through a first read/context observation. Without this, the local planner often answers immediately and never sees the untrusted email context, which makes the live-agent test invalid for indirect prompt injection.

AgentDojo has lower IR because qwen2.5:7b-instruct only generated dangerous actions for 46.0% of the sampled attacks. This is a planner susceptibility limit, not a WAMI action-gating miss: once a dangerous action appeared, WAMI blocked it.
