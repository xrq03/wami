# Table 4 Official Reproduction Status

## Download Status

| Component | Local path | Status |
|---|---|---|
| ToolBench official repo | `external/ToolBench` | downloaded |
| ToolBench official-format sample | `external/ToolBench/data_example` | runnable, 15 examples |
| AgentBench official repo | `external/AgentBench` | downloaded |

## What Table 4 Requires

The paper Table 4 reports ToolBench SR, AgentBench SR, and capability retention. Strict reproduction requires running the official benchmark agent harnesses, then inserting the defense before tool execution.

| Benchmark | Official metric | Extra requirements found after download | Current state |
|---|---|---|---|
| ToolBench | task success rate / ToolEval result | full ToolBench data zip, ToolEval dependencies, tool environment, model backend | small `data_example` all-method run completed |
| AgentBench | task success rate / benchmark score | Python 3.9 style environment, Docker, task containers, model backend | strict run blocked locally |

## Completed Local ToolBench Reproduction

Source: `data/toolbench_table4_all_methods_dataexample_summary.md`

| Method | N | Success Rate | Retention | False Block | Latency ms |
|---|---:|---:|---:|---:|---:|
| No Defense | 15 | 60.0% | 100.0% | 0.0% | 0.0 |
| Erase-and-Check Lite | 15 | 60.0% | 100.0% | 0.0% | 0.1 |
| ToolEmu-Sandbox Lite | 15 | 60.0% | 100.0% | 0.0% | 0.1 |
| Llama-Guard 3 8B local/Ollama | 15 | 60.0% | 100.0% | 0.0% | 460.7 |
| WAMI InjecAgent model | 15 | 53.3% | 88.9% | 13.3% | 7.8 |

This is a real ToolBench-format run, but it is not full ToolBench because the local sample has only 15 trajectories.

## AgentBench Blocker

Strict AgentBench is not completed in this environment for two concrete reasons:

1. Docker is required by the official AgentBench environments, but the local `docker` command is unavailable.
2. The downloaded AgentBench repository/documentation references `python -m src.start_task`, but the local `external/AgentBench/src` tree does not contain `start_task.py`.

Because of this, AgentBench official full rows remain blank in `data/final_table4_capability_reproduction.md`. The current AgentBench-style number is only the proxy row from `data/table4_capability_proxy.md`.

## Current Proxy

| System | ToolBench-style SR | AgentBench-style SR | ToolBench retention | AgentBench retention |
|---|---:|---:|---:|---:|
| WAMI proxy | 68.1% | 69.5% | 99.4% | 97.7% |

These proxy values are derived from local benign allow-rate after FPR calibration. They are useful as a capability-retention sanity check, but they are not official ToolBench/AgentBench results.

## Next Strict Steps

1. ToolBench: obtain the full official ToolBench data/reproduction logs, then run ToolEval on the target split.
2. AgentBench: install/enable Docker Desktop, use a compatible AgentBench branch or restore the missing `src.start_task` entrypoint, then run a small task first.
3. Insert WAMI as a pre-tool-call defense in each benchmark's agent loop.
4. Compute No Defense SR and defense SR on the same examples, then calculate retention as `Defense_SR / No_Defense_SR`.
