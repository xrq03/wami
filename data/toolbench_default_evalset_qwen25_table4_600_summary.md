# ToolBench Default Evalset qwen2.5 Table 4

This run uses the local ToolBench default evalset extracted from the cloned repository. It is larger than `data_example` and avoids Lite baselines.

- Input: `data/toolbench_default_evalset_600.jsonl`
- N: 600
- Planner: `qwen2.5:7b-instruct`
- Match threshold: 0.50

| Method | N | Planner Success | Preserved Success | ToolBench SR | ToolBench Retention | Blocked | Latency ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| No Defense qwen2.5 | 600 | 521 | 521 | 86.8% | 100.0% | 0 | 0.0 |
| Erase-and-Check qwen2.5 judge | 600 | 521 | 374 | 62.3% | 71.8% | 168 | 638.8 |
| ToolEmu-Sandbox qwen2.5 judge | 600 | 521 | 367 | 61.2% | 70.4% | 184 | 742.5 |
| Llama-Guard 3 8B local/Ollama | 600 | 521 | 512 | 85.3% | 98.3% | 11 | 196.3 |
| WAMI + qwen2.5 local agent | 600 | 521 | 516 | 86.0% | 99.0% | 5 | 7.2 |
