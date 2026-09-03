# Final Table 4 vs Paper Delta

This file compares locally reproduced Table 4 rows against the paper Table 4 reference values. `Delta` is `local - paper`, measured in percentage points.

## WAMI Proxy vs Paper WAMI

| Benchmark | Paper WAMI SR | Local WAMI SR | Delta SR | Paper Retention | Local Retention | Delta Retention | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| ToolBench | 68.0% | 68.1% | +0.1 pp | 99.3% | 99.4% | +0.1 pp | proxy, not official |
| AgentBench | 70.6% | 69.5% | -1.1 pp | 99.2% | 97.7% | -1.5 pp | proxy, not official |

## ToolBench Data Example vs Paper Table 4

| Method | N | Paper ToolBench SR | Local ToolBench SR | Delta SR | Paper Retention | Local Retention | Delta Retention | Local False Block | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| No Defense | 15 | 68.5% | 60.0% | -8.5 pp | 100.0% | 100.0% | +0.0 pp | 0.0% | real ToolBench-format tiny sample |
| Erase-and-Check Lite | 15 | 55.1% | 60.0% | +4.9 pp | 80.4% | 100.0% | +19.6 pp | 0.0% | local lite reproduction |
| ToolEmu-Sandbox Lite | 15 | 54.8% | 60.0% | +5.2 pp | 80.0% | 100.0% | +20.0 pp | 0.0% | local lite reproduction |
| Llama-Guard 3 8B local/Ollama | 15 | 61.4% | 60.0% | -1.4 pp | 89.6% | 100.0% | +10.4 pp | 0.0% | local official model via Ollama |
| WAMI InjecAgent model | 15 | 68.0% | 53.3% | -14.7 pp | 99.3% | 88.9% | -10.4 pp | 13.3% | current reproducible WAMI |

## Explanation

- The proxy WAMI rows are numerically close to the paper, but they are not official ToolBench/AgentBench runs.
- The ToolBench rows are more concrete because they use `external/ToolBench/data_example`, but `N=15` is too small to claim full official reproduction.
- The no-defense success rate on this tiny sample is 60.0%, while the paper's full ToolBench no-defense value is 68.5%, so all deltas are affected by sample mismatch.
- Erase-and-Check Lite, ToolEmu-Sandbox Lite, and Llama-Guard 3 do not block any of the 15 examples, so their local retention is 100.0%. That does not mean they are stronger than the paper baselines; it means this tiny utility sample is too easy for false-block testing.
- WAMI currently blocks 2/15 ToolBench examples, producing 53.3% SR and 88.9% retention. This is the current reproducible number from `scripts/run_toolbench_table4_all_methods.py`.

## Remaining Strict Gaps

| Requirement | Paper Table 4 | Current local state |
|---|---|---|
| Full ToolBench official evaluation | Full ToolBench SR over official test split | Only 15 ToolBench `data_example` trajectories plus proxy |
| Full AgentBench official evaluation | Full AgentBench SR | Blocked: local Docker command unavailable and downloaded repo entrypoint mismatch |
| Same base agent/model logs | Paper assumes same evaluated agent setting | Local rows apply defenses to available trajectories or local model/proxy outputs |
| Strict retention formula | Defense SR / No Defense SR on the same full benchmark | Correctly computed for the 15-example ToolBench sample; proxy rows remain estimates |
