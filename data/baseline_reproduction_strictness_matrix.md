# Baseline Reproduction Strictness Matrix

This file separates strict official reproduction from method-level and proxy
reproduction. It prevents over-claiming baseline coverage.

| Paper Baseline / Experiment | Current Status | Strictness | Evidence / File | Remaining Work |
|---|---|---|---|---|
| WAMI main method | Implemented and rerun | Method-level strong | `data/current_full_experiment_rerun_summary.md` | Exact original weights/latent encoder unavailable |
| Erase-and-Check | Implemented with Qwen/OpenAI-compatible API | Method-level | `data/table2_official_erase_check_*.md` | Need exact paper model/prompt/settings for strict replication |
| SmoothLLM | Partial scripts and Qwen judge variants | Method-level / partial | `data/smoothllm_*` | Need official SmoothLLM target model/tokenizer setup |
| ToolEmu-Sandbox | Not strict | Proxy / not complete | `scripts/run_official_toolemu.py` | Requires official ToolEmu runtime/model environment |
| Llama-Guard 3 8B | Not run by request earlier | Not reproduced | N/A | Requires downloading/running Llama-Guard 3 8B |
| GuardReasoner-VL | Official repo inspected, not fully run | Partial official setup | `external/GuardReasoner-VL` | Requires model weights and vLLM/Qwen-VL runtime |
| WebAgentGuard | No official runnable code found; method-level Qwen guard | Method-level | `data/webagentguard_paper_method_sample.md` | Need official implementation if released |
| BookAgent | Paper found unrelated to prompt-injection defense | Not applicable | `data/bookagent_replaced_by_agentdojo_status.md` | Replaced with AgentDojo as discussed |
| AgentDojo replacement | Dataset integrated and evaluated | Additional benchmark | `data/current_wami_paper_ablation_agentdojo.md` | Not a paper-original BookAgent row |
| ToolBench/AgentBench Table 4 | Proxy only | Proxy | `data/table4_capability_proxy.md` | Requires official agent harness, Docker/services, model logs |
| CyberSecEval3 VPI | Added as multimodal extension | Additional benchmark | `data/current_cyberseceval3_vpi_qwenvl_40.md` | Not a paper-original table |

Recommended reporting language:

```text
We report WAMI as a method-level reproduction and mark baselines as official,
method-level, proxy, or not reproduced depending on runnable code and available
model/runtime conditions.
```
