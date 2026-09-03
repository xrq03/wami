# Final Table 4 Required Columns

This is the current non-Lite Table 4 draft. ToolBench rows use the 600-row local ToolBench default evalset with qwen2.5-generated plans. AgentBench rows use the full qwen2.5 live AgentDojo benign traces as an AgentBench-style utility proxy. No `Lite` baselines are used in the main table.

## Local Non-Lite Results

| Method | ToolBench SR | AgentBench SR | ToolBench Retention | AgentBench Retention | Evidence |
|---|---:|---:|---:|---:|---|
| No Defense qwen2.5 | 86.8% | 90.7% | 100.0% | 100.0% | qwen2.5 planner, no defense |
| Erase-and-Check qwen2.5 judge | 62.3% | 44.2% | 71.8% | 48.7% | non-Lite qwen2.5 erase-check judge |
| ToolEmu-Sandbox qwen2.5 judge | 61.2% | 54.7% | 70.4% | 60.3% | non-Lite qwen2.5 sandbox emulator judge |
| Llama-Guard 3 8B local/Ollama | 85.3% | 80.2% | 98.3% | 88.5% | local `llama-guard3:8b` |
| WAMI + qwen2.5 local agent | 86.0% | 89.5% | 99.0% | 98.7% | qwen2.5 planner + WAMI action gateway |

## Supporting Runs

| Run | File | Key result |
|---|---|---|
| ToolBench default evalset 600 | `data/toolbench_default_evalset_qwen25_table4_600_summary.md` | No Defense 86.8%, Erase 62.3%, ToolEmu 61.2%, Llama-Guard 85.3%, WAMI 86.0% |
| AgentBench-style non-Lite | `data/agentbench_proxy_table4_nonlite_qwen25_summary.md` | WAMI SR 89.5%, retention 98.7%; Erase 44.2%, ToolEmu 54.7%, Llama-Guard 80.2% |

## Paper Reference Values

| Method | ToolBench SR | AgentBench SR | ToolBench Retention | AgentBench Retention | Evidence |
|---|---:|---:|---:|---:|---|
| No Defense | 68.5% | 71.2% | 100.0% | 100.0% | Paper Table 4 reference |
| Erase-and-Check | 55.1% | 57.6% | 80.4% | 80.9% | Paper Table 4 reference |
| ToolEmu-Sandbox | 54.8% | 56.9% | 80.0% | 79.9% | Paper Table 4 reference |
| Llama-Guard 3 | 61.4% | 63.8% | 89.6% | 89.6% | Paper Table 4 reference |
| WAMI | 68.0% | 70.6% | 99.3% | 99.2% | Paper Table 4 reference |

## Reading

- ToolBench now uses 600 local default-evalset examples, so SR is much more stable than the earlier 10-query sample.
- WAMI is close to No Defense on ToolBench utility: 86.0% vs 86.8%, with 99.0% retention.
- The strongest separation appears in the AgentBench-style utility proxy: WAMI preserves 98.7% of no-defense successful benign traces, while Erase-and-Check and ToolEmu-Sandbox over-block many benign traces.
- These rows are code-backed but still not strict official ToolBench/AgentBench full benchmark results.
