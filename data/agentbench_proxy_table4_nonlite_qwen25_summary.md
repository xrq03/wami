# AgentBench-style Non-Lite qwen2.5 Baselines

This is an AgentBench-style proxy using the full qwen2.5 live AgentDojo benign traces. No `Lite` baselines are used.

- Input live traces: `data/qwen25_7b_ollama_boost_agentdojo_full.csv`
- Judge model: `qwen2.5:7b-instruct`

| Method | N | No-Defense Success | Preserved Success | AgentBench SR | AgentBench Retention | Blocked | Latency ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| No Defense qwen2.5 instruction-plan | 86 | 78 | 78 | 90.7% | 100.0% | 0 | 0.0 |
| Erase-and-Check qwen2.5 judge | 86 | 78 | 38 | 44.2% | 48.7% | 46 | 929.5 |
| ToolEmu-Sandbox qwen2.5 judge | 86 | 78 | 47 | 54.7% | 60.3% | 37 | 866.8 |
| Llama-Guard 3 8B local/Ollama | 86 | 78 | 69 | 80.2% | 88.5% | 11 | 360.1 |
| WAMI + qwen2.5 local agent | 86 | 78 | 77 | 89.5% | 98.7% | 1 | 9.6 |
