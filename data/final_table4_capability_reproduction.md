# Final Table 4 Capability Reproduction

Table 4 measures utility: whether a defense preserves normal agent task success on ToolBench/AgentBench. This is different from attack IR/FPR tables. Higher `Success Rate` and higher `Retention` are better; lower `False Block` is better.

## Paper Reference And Local Reproduction

| Source | System | Benchmark | N | Success Rate | Retention | False Block | Latency ms | Status | Source |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| paper_table4 | No Defense | ToolBench | - | 68.5% | 100.0% | - | - | paper-reference | `data/table4_capability_proxy.md` |
| paper_table4 | No Defense | AgentBench | - | 71.2% | 100.0% | - | - | paper-reference | `data/table4_capability_proxy.md` |
| paper_table4 | + Erase-and-Check | ToolBench | - | 55.1% | 80.4% | - | - | paper-reference | `data/table4_capability_proxy.md` |
| paper_table4 | + Erase-and-Check | AgentBench | - | 57.6% | 80.9% | - | - | paper-reference | `data/table4_capability_proxy.md` |
| paper_table4 | + ToolEmu-Sandbox | ToolBench | - | 54.8% | 80.0% | - | - | paper-reference | `data/table4_capability_proxy.md` |
| paper_table4 | + ToolEmu-Sandbox | AgentBench | - | 56.9% | 79.9% | - | - | paper-reference | `data/table4_capability_proxy.md` |
| paper_table4 | + Llama-Guard 3 | ToolBench | - | 61.4% | 89.6% | - | - | paper-reference | `data/table4_capability_proxy.md` |
| paper_table4 | + Llama-Guard 3 | AgentBench | - | 63.8% | 89.6% | - | - | paper-reference | `data/table4_capability_proxy.md` |
| paper_table4 | + WAMI (Ours) | ToolBench | - | 68.0% | 99.3% | - | - | paper-reference | `data/table4_capability_proxy.md` |
| paper_table4 | + WAMI (Ours) | AgentBench | - | 70.6% | 99.2% | - | - | paper-reference | `data/table4_capability_proxy.md` |
| local_proxy | + WAMI (Ours) | ToolBench-style proxy | - | 68.1% | 99.4% | - | - | proxy | `data/table4_capability_proxy.md` |
| local_proxy | + WAMI (Ours) | AgentBench-style proxy | - | 69.5% | 97.7% | - | - | proxy | `data/table4_capability_proxy.md` |
| local_nonlite_600 | No Defense qwen2.5 | ToolBench default evalset | 600 | 86.8% | 100.0% | 0.0% | 0.0 | qwen2.5-live-agent-nonlite | `data/toolbench_default_evalset_qwen25_table4_600_summary.md` |
| local_nonlite_600 | Erase-and-Check qwen2.5 judge | ToolBench default evalset | 600 | 62.3% | 71.8% | 28.0% | 638.8 | qwen2.5-live-agent-nonlite | `data/toolbench_default_evalset_qwen25_table4_600_summary.md` |
| local_nonlite_600 | ToolEmu-Sandbox qwen2.5 judge | ToolBench default evalset | 600 | 61.2% | 70.4% | 30.7% | 742.5 | qwen2.5-live-agent-nonlite | `data/toolbench_default_evalset_qwen25_table4_600_summary.md` |
| local_nonlite_600 | Llama-Guard 3 8B local/Ollama | ToolBench default evalset | 600 | 85.3% | 98.3% | 1.8% | 196.3 | qwen2.5-live-agent-nonlite | `data/toolbench_default_evalset_qwen25_table4_600_summary.md` |
| local_nonlite_600 | WAMI + qwen2.5 local agent | ToolBench default evalset | 600 | 86.0% | 99.0% | 0.8% | 7.2 | qwen2.5-live-agent-nonlite | `data/toolbench_default_evalset_qwen25_table4_600_summary.md` |
| local_nonlite | No Defense qwen2.5 | ToolBench instruction queries | 10 | 40.0% | 100.0% | 0.0% | 0.0 | qwen2.5-live-agent-nonlite | `data/toolbench_table4_nonlite_qwen25_structured_summary.md` |
| local_nonlite | Erase-and-Check qwen2.5 judge | ToolBench instruction queries | 10 | 40.0% | 100.0% | 30.0% | 635.4 | qwen2.5-live-agent-nonlite | `data/toolbench_table4_nonlite_qwen25_structured_summary.md` |
| local_nonlite | ToolEmu-Sandbox qwen2.5 judge | ToolBench instruction queries | 10 | 40.0% | 100.0% | 30.0% | 695.2 | qwen2.5-live-agent-nonlite | `data/toolbench_table4_nonlite_qwen25_structured_summary.md` |
| local_nonlite | Llama-Guard 3 8B local/Ollama | ToolBench instruction queries | 10 | 40.0% | 100.0% | 0.0% | 935.9 | qwen2.5-live-agent-nonlite | `data/toolbench_table4_nonlite_qwen25_structured_summary.md` |
| local_nonlite | WAMI + qwen2.5 local agent | ToolBench instruction queries | 10 | 40.0% | 100.0% | 0.0% | 2.6 | qwen2.5-live-agent-nonlite | `data/toolbench_table4_nonlite_qwen25_structured_summary.md` |
| local_nonlite | No Defense qwen2.5 | AgentBench-style AgentDojo benign | 86 | 90.7% | 100.0% | 0.0% | 0.0 | qwen2.5-live-agent-nonlite | `data/agentbench_proxy_table4_nonlite_qwen25_summary.md` |
| local_nonlite | Erase-and-Check qwen2.5 judge | AgentBench-style AgentDojo benign | 86 | 44.2% | 48.7% | 53.5% | 929.5 | qwen2.5-live-agent-nonlite | `data/agentbench_proxy_table4_nonlite_qwen25_summary.md` |
| local_nonlite | ToolEmu-Sandbox qwen2.5 judge | AgentBench-style AgentDojo benign | 86 | 54.7% | 60.3% | 43.0% | 866.8 | qwen2.5-live-agent-nonlite | `data/agentbench_proxy_table4_nonlite_qwen25_summary.md` |
| local_nonlite | Llama-Guard 3 8B local/Ollama | AgentBench-style AgentDojo benign | 86 | 80.2% | 88.5% | 12.8% | 360.1 | qwen2.5-live-agent-nonlite | `data/agentbench_proxy_table4_nonlite_qwen25_summary.md` |
| local_nonlite | WAMI + qwen2.5 local agent | AgentBench-style AgentDojo benign | 86 | 89.5% | 98.7% | 1.2% | 9.6 | qwen2.5-live-agent-nonlite | `data/agentbench_proxy_table4_nonlite_qwen25_summary.md` |
| strict_official_gap | All methods | AgentBench official full | - | - | - | - | - | blocked-local-env | `data/table4_official_reproduction_status.md` |

## Interpretation

- The `local_proxy` rows are capability-retention estimates, not official ToolBench/AgentBench.
- The `local_nonlite` rows are the preferred current rows for your Table 4 draft because they use local `qwen2.5:7b-instruct` planner outputs and non-Lite defense judges before/around WAMI gating.
- The `local_nonlite_600` ToolBench rows supersede the earlier 10-query rows for the final table because they use 600 local ToolBench default-evalset examples.
- The older ToolBench `data_example` Lite/static rows are no longer used in this final table because they were too easy and produced artificially saturated retention.
- Strict AgentBench full reproduction is still blank because the local environment does not currently have the required Docker runtime, and the downloaded AgentBench repo version references an entrypoint that is absent in the local tree.
