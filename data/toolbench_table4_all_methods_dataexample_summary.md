# ToolBench Table 4 all-method local reproduction

Data: `external/ToolBench/data_example`; this is a real ToolBench-format small sample, not full ToolBench.

| Method | N | Official successful | Success Rate | Retention | False Block | Latency ms |
|---|---:|---:|---:|---:|---:|---:|
| No Defense | 15 | 9 | 60.0% | 100.0% | 0.0% | 0.0 |
| Erase-and-Check Lite | 15 | 9 | 60.0% | 100.0% | 0.0% | 0.1 |
| ToolEmu-Sandbox Lite | 15 | 9 | 60.0% | 100.0% | 0.0% | 0.1 |
| Llama-Guard 3 8B local/Ollama | 15 | 9 | 60.0% | 100.0% | 0.0% | 460.7 |
| WAMI InjecAgent model | 15 | 9 | 53.3% | 88.9% | 13.3% | 7.8 |

Interpretation: `Success Rate` counts ToolBench examples that were originally successful and still allowed by the defense. `Retention` is Success Rate divided by the no-defense success rate on the same 15 examples.
