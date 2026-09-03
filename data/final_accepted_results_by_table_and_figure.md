# Final Accepted Results By Table And Figure

This file lists the results currently treated as the accepted final local reproduction outputs.

## Table 1: Main Defense Comparison

Source: `data/final_table1_reproduction.md`

| Dataset | Defense Method | IR | FPR | ACC | Latency ms | Status |
|---|---|---:|---:|---:|---:|---|
| BIPIA | GuardReasoner-VL Eco-3B 4bit | 72.0% | 72.0% | 50.0% | 28985.400 | sampled-local-4bit |
| BIPIA | Llama-Guard 3 8B local/Ollama | 12.0% | 1.0% | 55.5% | 2312.223 | sampled-local-ollama |
| BIPIA | WebAgentGuard qwen2.5 + action_fidelity | 72.0% | 16.0% | 78.0% | - | selected-action-fidelity |
| BIPIA | AgentDojo official PI detector | 47.7% | 34.1% | 56.8% | 160.436 | implemented-official-detector |
| BIPIA | BookAgent-style Constraint Verifier | 92.8% | 0.0% | 96.4% | 0.101 | method-level-bookagent-constraints |
| BIPIA | WAMI paper-faithful | 99.8% | 0.5% | 99.6% | 38.836 | implemented |
| InjecAgent | GuardReasoner-VL Eco-3B 4bit | 36.0% | 20.0% | 58.0% | 21836.300 | sampled-local-4bit |
| InjecAgent | Llama-Guard 3 8B local/Ollama | 77.0% | 0.0% | 88.5% | 2257.606 | sampled-local-ollama |
| InjecAgent | WebAgentGuard qwen2.5 + action_fidelity | 80.0% | 0.0% | 90.0% | - | selected-action-fidelity |
| InjecAgent | AgentDojo official PI detector | 78.1% | 64.7% | 56.6% | 110.419 | implemented-official-detector |
| InjecAgent | BookAgent-style Constraint Verifier | 69.7% | 0.0% | 84.9% | 0.064 | method-level-bookagent-constraints |
| InjecAgent | WAMI paper-faithful | 86.8% | 5.9% | 90.5% | 41.971 | implemented |
| AgentDojo | GuardReasoner-VL Eco-3B 4bit | 42.0% | 40.8% | 50.5% | 21168.700 | sampled-local-4bit |
| AgentDojo | Llama-Guard 3 8B local/Ollama | 67.0% | 11.6% | 76.9% | 2250.336 | sampled-local-ollama |
| AgentDojo | WebAgentGuard qwen2.5 + action_fidelity | 72.0% | 8.0% | 74.6% | - | selected-action-fidelity |
| AgentDojo | AgentDojo official PI detector | 25.7% | 25.6% | 32.2% | 47.331 | implemented-official-detector |
| AgentDojo | BookAgent-style Constraint Verifier | 60.0% | 3.5% | 64.8% | 0.093 | method-level-bookagent-constraints |
| AgentDojo | WAMI paper-faithful | 97.2% | 9.3% | 96.3% | 37.217 | implemented |

## Table 2: Frontier Safety Comparison

Source: `data/final_table2_reproduction.md`

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Status |
|---|---|---:|---:|---:|---:|---:|---|
| BIPIA | SmoothLLM-style perturbation + qwen2.5 local judge | 61.4% | 22.6% | 69.4% | 270.1 | 2400 | implemented-local |
| InjecAgent | SmoothLLM-style perturbation + qwen2.5 local judge | 89.7% | 17.6% | 89.6% | 214.2 | 2125 | implemented-local |
| AgentDojo | SmoothLLM-style perturbation + qwen2.5 local judge | 91.4% | 37.2% | 90.4% | 202.5 | 2408 | implemented-local-old-agentdojo |
| BIPIA | Erase-and-Check official-style + qwen2.5 local | 18.8% | 0.1% | 59.3% | 530.8 | 2400 | implemented-local |
| InjecAgent | Erase-and-Check official-style + qwen2.5 local | 90.6% | 0.0% | 90.6% | 373.2 | 2125 | implemented-local |
| AgentDojo | Erase-and-Check official-style + qwen2.5 local | 65.2% | 8.1% | 66.2% | 323.6 | 2408 | implemented-local-old-agentdojo |
| BIPIA | ToolEmu-Sandbox-style local tau=7 | 91.7% | 15.3% | 88.2% | 0.236 | 2400 | adapted-local |
| InjecAgent | ToolEmu-Sandbox-style local tau=7 | 58.1% | 29.4% | 64.4% | 0.183 | 4233 | adapted-local |
| AgentDojo | ToolEmu-Sandbox-style local tau=7 | 72.7% | 1.2% | 76.1% | 0.262 | 653 | adapted-local |
| BIPIA | WAMI paper-faithful | 99.8% | 0.5% | 99.6% | 38.8 | 2400 | implemented |
| InjecAgent | WAMI paper-faithful | 86.8% | 5.9% | 90.5% | 42.0 | 4233 | implemented |
| AgentDojo | WAMI paper-faithful | 97.2% | 9.3% | 96.3% | 37.2 | 653 | implemented |

## Table 3: Cross-Agent Generalization

Source: `data/final_table3_cross_agent_reproduction.md`

| Backbone | Dataset | N | IR | FPR | ACC | Planner Risk Rate | WAMI Action Block Rate | Latency ms | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Qwen2.5-7B-Instruct local | InjecAgent | 4233 | 48.0% | 0.0% | 74.1% | 52.8% | 90.8% | 4556.1 | full-local-boosted |
| Qwen2.5-7B-Instruct local | BIPIA | 2400 | 91.4% | 0.5% | 95.5% | 91.4% | 100.0% | 2538.9 | full-local-boosted |
| Qwen2.5-7B-Instruct local | AgentDojo | 653 | 35.8% | 9.3% | 43.0% | 37.4% | 95.8% | 3425.3 | full-local-boosted |
| Mistral-v0.3 local | InjecAgent | 100 | 76.0% | 0.0% | 88.0% | 76.0% | 100.0% | 4525.8 | sampled-local-50x50 |
| Mistral-v0.3 local | BIPIA | 100 | 100.0% | 0.0% | 100.0% | 100.0% | 100.0% | 5903.6 | sampled-local-50x50 |
| Mistral-v0.3 local | AgentDojo | 100 | 86.0% | 8.0% | 89.0% | 92.0% | 93.5% | 4537.4 | sampled-local-50x50 |
| Llama-3-8B local | InjecAgent | 100 | 86.0% | 0.0% | 93.0% | 86.0% | 100.0% | 2886.2 | sampled-local-50x50 |
| Llama-3-8B local | BIPIA | 100 | 100.0% | 0.0% | 100.0% | 100.0% | 100.0% | 2492.8 | sampled-local-50x50 |
| Llama-3-8B local | AgentDojo | 100 | 84.0% | 4.0% | 90.0% | 92.0% | 91.3% | 3368.8 | sampled-local-50x50 |
| Qwen-VL-Max API | CyberSecEval3 VPI multimodal | 100 | 100.0% | 0.0% | 100.0% | - | - | 6542.1 | multimodal-reference |
| GPT-4V | All | - | - | - | - | - | - | - | not-run |

## Table 4: ToolBench / AgentBench Utility

Source: `data/final_table4_required_columns.md`

| Method | ToolBench SR | AgentBench SR | ToolBench Retention | AgentBench Retention |
|---|---:|---:|---:|---:|
| No Defense qwen2.5 | 86.8% | 90.7% | 100.0% | 100.0% |
| Erase-and-Check qwen2.5 judge | 62.3% | 44.2% | 71.8% | 48.7% |
| ToolEmu-Sandbox qwen2.5 judge | 61.2% | 54.7% | 70.4% | 60.3% |
| Llama-Guard 3 8B local/Ollama | 85.3% | 80.2% | 98.3% | 88.5% |
| WAMI + qwen2.5 local agent | 86.0% | 89.5% | 99.0% | 98.7% |

## Table 5: WAMI Ablation

Source: `data/final_table5_ablation.md`

| Dataset | Ablation Variant | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| InjecAgent | WAMI Full | 86.8% | 5.9% | 90.5% | 41.971 | 4233 |
| InjecAgent | w/o TDG Graph Construction | 26.0% | 17.6% | 54.3% | 5.143 | 4233 |
| InjecAgent | w/o World Model Rollout | 57.2% | 0.0% | 78.7% | 2.614 | 4233 |
| InjecAgent | w/o MINE Gateway | 21.7% | 0.0% | 61.0% | 6.594 | 4233 |
| InjecAgent | w/o Shadow Adversarial Training | 56.9% | 0.0% | 78.5% | 6.763 | 4233 |
| BIPIA | WAMI Full | 99.8% | 0.5% | 99.6% | 38.836 | 2400 |
| BIPIA | w/o TDG Graph Construction | 20.8% | 13.4% | 53.7% | 6.859 | 2400 |
| BIPIA | w/o World Model Rollout | 79.6% | 1.2% | 89.2% | 3.390 | 2400 |
| BIPIA | w/o MINE Gateway | 12.7% | 0.1% | 56.3% | 8.371 | 2400 |
| BIPIA | w/o Shadow Adversarial Training | 77.4% | 1.9% | 87.8% | 8.619 | 2400 |
| AgentDojo | WAMI Full | 97.2% | 9.3% | 96.3% | 37.217 | 653 |
| AgentDojo | w/o TDG Graph Construction | 4.6% | 3.5% | 16.7% | 6.515 | 653 |
| AgentDojo | w/o World Model Rollout | 20.3% | 2.3% | 30.5% | 3.690 | 653 |
| AgentDojo | w/o MINE Gateway | 12.3% | 0.0% | 23.9% | 12.724 | 653 |
| AgentDojo | w/o Shadow Adversarial Training | 77.2% | 4.7% | 79.6% | 13.504 | 653 |
| Macro Avg. | WAMI Full | 94.6% | 5.2% | 95.5% | 39.341 | 7286 |
| Macro Avg. | w/o TDG Graph Construction | 17.2% | 11.5% | 41.6% | 6.172 | 7286 |
| Macro Avg. | w/o World Model Rollout | 52.4% | 1.2% | 66.1% | 3.231 | 7286 |
| Macro Avg. | w/o MINE Gateway | 15.6% | 0.0% | 47.1% | 9.229 | 7286 |
| Macro Avg. | w/o Shadow Adversarial Training | 70.5% | 2.2% | 82.0% | 9.629 | 7286 |

## Figures 3-8

Source: `data/final_figures_3_to_8.md`

| Figure | File | Meaning |
|---|---|---|
| Figure 3 | `data/final_figure3_defense_efficacy_overview_v6.png` | Paper-style defense efficacy overview radar chart computed from local WAMI, Llama-Guard 3, and SmoothLLM results. |
| Figure 4 | `data/final_figure4_sota_smooth_roc_v2.png` | Fig. 4 follows the paper's SOTA ROC comparison; smoothed curves use actually measured local WAMI, Llama-Guard 3, ToolEmu-Sandbox, SmoothLLM, and Erase-and-Check operating points. |
| Figure 5 | `data/final_figure5_threshold_sensitivity.png` | WAMI IR/FPR movement under threshold sweep. |
| Figure 6 | `data/final_figure6_latency_decomposition.png` | Paper-strict CUDA TDG/world/MINE latency decomposition. |
| Figure 7 | `data/final_figure7_resource_comparison_v2.png` | Defense footprint and latency overhead. |
| Figure 8 | `data/final_figure8_shadow_training.png` | Shadow adversarial training MI-gap and loss dynamics. |
