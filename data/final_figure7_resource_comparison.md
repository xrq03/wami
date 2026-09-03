# Final Figure 7 Resource Comparison

This table compares the defense overhead used in the final local reproduction. The shared qwen2.5 planner is not counted as WAMI defense memory; WAMI only counts its gateway model.

| Defense | Runtime basis | Footprint kind | Footprint GiB | ToolBench latency ms | AgentBench latency ms | Notes |
|---|---|---|---:|---:|---:|---|
| WAMI gateway | Paper-style WAMI defense module; qwen2.5 planner is shared with no-defense and not counted as defense memory. | Measured CUDA peak reserved | 0.348 | 7.2 | 9.6 | NPZ model file 0.443 MB; peak allocated 336.0 MB. |
| Erase-and-Check | Local qwen2.5 judge baseline. | Ollama model layer footprint proxy | 4.361 | 638.8 | 929.5 | Extra LLM judge beyond the shared planner; footprint is disk model layer, not synchronized VRAM profiler. |
| ToolEmu-Sandbox | Local qwen2.5 sandbox judge baseline. | Ollama model layer footprint proxy | 4.361 | 742.5 | 866.8 | Reproduced as local judge/sandbox protocol; official multi-agent ToolEmu can require larger model stacks. |
| Llama-Guard 3 8B | Local Ollama safety classifier. | Ollama model layer footprint proxy | 4.583 | 196.3 | 360.1 | Local 8B guard model footprint proxy. |

## Interpretation

- WAMI defense footprint is 0.348 GiB measured by CUDA peak reserved memory, while qwen2.5 judge baselines use about 4.361 GiB model-layer footprint.
- WAMI Table 4 defense latency is 7.2 ms on ToolBench and 9.6 ms on AgentBench.
- For non-WAMI baselines, footprint is a local Ollama model-layer proxy. It is suitable for the paper's resource comparison trend, but not a strict live VRAM profiler.
