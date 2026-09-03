# Table 4 capability reproduction

This file separates the paper's official Table 4 values from the local proxy reproduction. The local row uses the updated WAMI benign allow-rate as a capability-retention proxy, because the official ToolBench/AgentBench harnesses are not present in this workspace.

| Source | System | ToolBench SR | AgentBench SR | ToolBench Retention | AgentBench Retention | Note |
|---|---|---:|---:|---:|---:|---|
| paper_table4 | No Defense | 68.5% | 71.2% | 100.0% | 100.0% | values extracted from the paper Table 4 |
| paper_table4 | + Erase-and-Check | 55.1% | 57.6% | 80.4% | 80.9% | values extracted from the paper Table 4 |
| paper_table4 | + ToolEmu-Sandbox | 54.8% | 56.9% | 80.0% | 79.9% | values extracted from the paper Table 4 |
| paper_table4 | + Llama-Guard 3 | 61.4% | 63.8% | 89.6% | 89.6% | values extracted from the paper Table 4 |
| paper_table4 | + WAMI (Ours) | 68.0% | 70.6% | 99.3% | 99.2% | values extracted from the paper Table 4 |
| local_proxy | + WAMI (Ours, proxy) | 68.1% | 69.5% | 99.4% | 97.7% | computed from local benign allow-rate proxy; not official ToolBench/AgentBench |

## Interpretation

- Paper Table 4 WAMI: ToolBench SR 68.0%, AgentBench SR 70.6%, retention 99.3% / 99.2%.
- Local proxy WAMI: ToolBench-style SR 68.1%, AgentBench-style SR 69.5%, retention 99.4% / 97.7%.
- Strict official reproduction still requires the ToolBench and AgentBench agent harnesses plus model execution logs.
