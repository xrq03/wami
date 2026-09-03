# Final Table 2 Reproduction

This table collects the currently runnable Table 2 baselines. It separates real local runs from adapted local reproductions when the strict official benchmark/runtime is not available.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Status | Source |
|---|---|---:|---:|---:|---:|---:|---|---|
| BIPIA | SmoothLLM-style perturbation + qwen2.5 local judge | 61.4% | 22.6% | 69.4% | 270.1 | 2400 | implemented-local | `data/smoothllm_ollama_qwen25_1copy_headtail1200_full_3datasets.md` |
| InjecAgent | SmoothLLM-style perturbation + qwen2.5 local judge | 89.7% | 17.6% | 89.6% | 214.2 | 2125 | implemented-local | `data/smoothllm_ollama_qwen25_1copy_headtail1200_full_3datasets.md` |
| AgentDojo | SmoothLLM-style perturbation + qwen2.5 local judge | 91.4% | 37.2% | 90.4% | 202.5 | 2408 | implemented-local-old-agentdojo | `data/smoothllm_ollama_qwen25_1copy_headtail1200_full_3datasets.md` |
| BIPIA | Erase-and-Check official-style + qwen2.5 local | 18.8% | 0.1% | 59.3% | 530.8 | 2400 | implemented-local | `data/erase_check_ollama_qwen25_suffix_m1_full_3datasets.md` |
| InjecAgent | Erase-and-Check official-style + qwen2.5 local | 90.6% | 0.0% | 90.6% | 373.2 | 2125 | implemented-local | `data/erase_check_ollama_qwen25_suffix_m1_full_3datasets.md` |
| AgentDojo | Erase-and-Check official-style + qwen2.5 local | 65.2% | 8.1% | 66.2% | 323.6 | 2408 | implemented-local-old-agentdojo | `data/erase_check_ollama_qwen25_suffix_m1_full_3datasets.md` |
| BIPIA | ToolEmu-Sandbox-style local tau=7 | 91.7% | 15.3% | 88.2% | 0.236 | 2400 | adapted-local | `data/table2_toolemu_sandbox_final_selected.md` |
| InjecAgent | ToolEmu-Sandbox-style local tau=7 | 58.1% | 29.4% | 64.4% | 0.183 | 4233 | adapted-local | `data/table2_toolemu_sandbox_final_selected.md` |
| AgentDojo | ToolEmu-Sandbox-style local tau=7 | 72.7% | 1.2% | 76.1% | 0.262 | 653 | adapted-local | `data/table2_toolemu_sandbox_final_selected.md` |
| BIPIA | WAMI paper-faithful | 99.8% | 0.5% | 99.6% | 38.8 | 2400 | implemented | `data/paper_mine_ensemble_sourceaware_triplet_taua45_taub50_results.csv` |
| InjecAgent | WAMI paper-faithful | 86.8% | 5.9% | 90.5% | 42.0 | 4233 | implemented | `data/paper_mine_ensemble_sourceaware_triplet_taua45_taub50_results.csv` |
| AgentDojo | WAMI paper-faithful | 97.2% | 9.3% | 96.3% | 37.2 | 653 | implemented | `data/paper_mine_triplet_slot_seed4071_e4_tau50_results.csv` |

## Status Notes

- `implemented-local`: real local run with the method adapter and local qwen2.5 judge.
- `implemented-local-old-agentdojo`: real local run, but the AgentDojo split comes from an earlier converted AgentDojo file with 2408 samples rather than the current 653-row table split.
- `adapted-local`: method-level same-dataset reproduction, not strict official benchmark reproduction.
- `implemented`: final proposed WAMI row using the accepted paper-faithful operating point.

## Remaining Gap

SmoothVLM is still blank for strict reproduction because the current three main datasets are text/tool-trajectory datasets, not native image-text VLM safety datasets. A credible SmoothVLM row needs a fixed multimodal dataset adapter and image perturbation path.
