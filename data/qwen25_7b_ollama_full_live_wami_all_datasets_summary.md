# Local Qwen2.5 7B Full Live-Agent WAMI Full-Dataset Results

Model: qwen2.5:7b-instruct via local Ollama on D drive.

Mode: local live-agent planner generates one action at a time; WAMI builds runtime TDG and gates side-effect actions before execution.

| Dataset | N | Attack | Benign | IR | FPR | ACC | Planner Risk Rate | WAMI Action Block Rate | Avg latency ms | Avg steps | CSV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| InjecAgent | 4233 | 2108 | 2125 | 39.0% | 0.0% | 69.6% | 43.7% | 89.3% | 4898.5 | 2.01 | data/qwen25_7b_ollama_full_live_wami_injecagent_full.csv |
| BIPIA | 2400 | 1200 | 1200 | 82.7% | 0.1% | 91.3% | 82.7% | 100.0% | 1713.4 | 1.20 | data/qwen25_7b_ollama_full_live_wami_bipia_full.csv |
| AgentDojo | 653 | 567 | 86 | 21.3% | 3.5% | 31.2% | 22.9% | 93.1% | 3755.9 | 1.60 | data/qwen25_7b_ollama_full_live_wami_agentdojo_full.csv |

## Notes

- IR is the end-to-end interception rate over attack samples in live-agent mode.
- Planner Risk Rate is the share of attack samples where the local planner actually emitted a dangerous side-effect/sensitive action.
- WAMI Action Block Rate is the share of emitted dangerous attack actions blocked by WAMI.
- If IR is lower than WAMI Action Block Rate, the gap is mainly planner behavior: the local model did not always follow the injected instruction far enough to emit a dangerous action.
- BIPIA was run with --bootstrap-first-observation, because the indirect injection is delivered through the first ReadContext observation.
