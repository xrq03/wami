# Final Table 1 Reproduction

BookAgent is reproduced as a method-level safety-constraint verifier adapted from its VAS/ICR/TCC guardrail pipeline. AgentDojo is additionally included with its official local prompt-injection detector without an LLM API.

| Dataset | Defense Method | IR | FPR | ACC | Latency ms | Status | Source | Note |
|---|---|---:|---:|---:|---:|---|---|---|
| BIPIA | GuardReasoner-VL Eco-3B 4bit | 72.0% | 72.0% | 50.0% | 28985.400 | sampled-local-4bit | `data/guardreasoner_vl_final_selected_result.csv` | Local released GuardReasoner-VL Eco-3B checkpoint through transformers 4-bit; response-only adapter; sampled partial run. |
| BIPIA | Llama-Guard 3 8B local/Ollama | 12.0% | 1.0% | 55.5% | 2312.223 | sampled-local-ollama | `data/llamaguard3_ollama_pc100_summary.csv` | Local Ollama llama-guard3:8b run on 100 attack + 100 benign samples; maps unsafe to block. |
| BIPIA | WebAgentGuard qwen2.5 + action_fidelity | 72.0% | 16.0% | 78.0% | - | selected-action-fidelity | `data/webagentguard_final_action_fidelity_operating_point.md` | Selected calibrated WebAgentGuard-style operating point: next_action, risk_score >= 80. This is the version accepted for final comparison. |
| BIPIA | AgentDojo official PI detector | 47.7% | 34.1% | 56.8% | 160.436 | implemented-official-detector | `data/agentdojo_official_detector_wami_datasets_full.csv` | Official AgentDojo TransformersBasedPIDetector applied to the same WAMI-format datasets via tool-output input adapter; full available split, no LLM API. |
| BIPIA | BookAgent-style Constraint Verifier | 92.8% | 0.0% | 96.4% | 0.101 | method-level-bookagent-constraints | `data/bookagent_constraint_verifier_full.csv` | Adapts BookAgent's VAS safety guardrails, safety auditor, verify-revise loop, and TCC sequence consistency to agent trajectory defense. |
| BIPIA | WAMI paper-faithful | 99.8% | 0.5% | 99.6% | 38.836 | implemented | `data/paper_mine_ensemble_sourceaware_triplet_taua45_taub50_results.csv` | Use paper-faithful source-aware + triplet-slot ensemble OR; no direct hard-rule veto. |
| InjecAgent | GuardReasoner-VL Eco-3B 4bit | 36.0% | 20.0% | 58.0% | 21836.300 | sampled-local-4bit | `data/guardreasoner_vl_final_selected_result.csv` | Local released GuardReasoner-VL Eco-3B checkpoint through transformers 4-bit; response-only adapter; sampled partial run. |
| InjecAgent | Llama-Guard 3 8B local/Ollama | 77.0% | 0.0% | 88.5% | 2257.606 | sampled-local-ollama | `data/llamaguard3_ollama_pc100_summary.csv` | Local Ollama llama-guard3:8b run on 100 attack + 100 benign samples; maps unsafe to block. |
| InjecAgent | WebAgentGuard qwen2.5 + action_fidelity | 80.0% | 0.0% | 90.0% | - | selected-action-fidelity | `data/webagentguard_final_action_fidelity_operating_point.md` | Selected calibrated WebAgentGuard-style operating point: full_trajectory, risk_score >= 80. This is the version accepted for final comparison. |
| InjecAgent | AgentDojo official PI detector | 78.1% | 64.7% | 56.6% | 110.419 | implemented-official-detector | `data/agentdojo_official_detector_wami_datasets_full.csv` | Official AgentDojo TransformersBasedPIDetector applied to the same WAMI-format datasets via tool-output input adapter; full available split, no LLM API. |
| InjecAgent | BookAgent-style Constraint Verifier | 69.7% | 0.0% | 84.9% | 0.064 | method-level-bookagent-constraints | `data/bookagent_constraint_verifier_full.csv` | Adapts BookAgent's VAS safety guardrails, safety auditor, verify-revise loop, and TCC sequence consistency to agent trajectory defense. |
| InjecAgent | WAMI paper-faithful | 86.8% | 5.9% | 90.5% | 41.971 | implemented | `data/paper_mine_ensemble_sourceaware_triplet_taua45_taub50_results.csv` | Use paper-faithful source-aware + triplet-slot ensemble OR; no direct hard-rule veto. |
| AgentDojo | GuardReasoner-VL Eco-3B 4bit | 42.0% | 40.8% | 50.5% | 21168.700 | sampled-local-4bit | `data/guardreasoner_vl_final_selected_result.csv` | Local released GuardReasoner-VL Eco-3B checkpoint through transformers 4-bit; response-only adapter; sampled partial run. |
| AgentDojo | Llama-Guard 3 8B local/Ollama | 67.0% | 11.6% | 76.9% | 2250.336 | sampled-local-ollama | `data/llamaguard3_ollama_pc100_summary.csv` | Local Ollama llama-guard3:8b run on 100 attack + 86 benign samples; maps unsafe to block. |
| AgentDojo | WebAgentGuard qwen2.5 + action_fidelity | 72.0% | 8.0% | 74.6% | - | selected-action-fidelity | `data/webagentguard_final_action_fidelity_operating_point.md` | Selected calibrated WebAgentGuard-style operating point: full_trajectory, risk_score >= 85. This is the version accepted for final comparison. |
| AgentDojo | AgentDojo official PI detector | 25.7% | 25.6% | 32.2% | 47.331 | implemented-official-detector | `data/agentdojo_official_detector_wami_datasets_full.csv` | Official AgentDojo TransformersBasedPIDetector applied to the same WAMI-format datasets via tool-output input adapter; full available split, no LLM API. |
| AgentDojo | BookAgent-style Constraint Verifier | 60.0% | 3.5% | 64.8% | 0.093 | method-level-bookagent-constraints | `data/bookagent_constraint_verifier_full.csv` | Adapts BookAgent's VAS safety guardrails, safety auditor, verify-revise loop, and TCC sequence consistency to agent trajectory defense. |
| AgentDojo | WAMI paper-faithful | 97.2% | 9.3% | 96.3% | 37.217 | implemented | `data/paper_mine_triplet_slot_seed4071_e4_tau50_results.csv` | Use triplet-slot single model for AgentDojo because ensemble OR raises FPR. |

## Reading Guide

- `blank`: keep empty until the official implementation/model is available.
- `partial`: a runner or proxy exists, but it is not yet an official strict reproduction.
- `method-level-noapi`: no official released checkpoint/runtime was available, so the defense idea was reproduced locally without API calls and must not be reported as official.
- `sampled-local-ollama`: real local Ollama model run on a balanced sample, not full-dataset official reproduction.
- `sampled-local-4bit`: real local transformers 4-bit model run on a balanced sample, not full-dataset official reproduction.
- `method-level-bookagent-constraints`: BookAgent's safety-constraint pipeline is adapted to agent trajectories; this is a method-level baseline, not a native BookAgent benchmark.
- `blank-official`: keep empty until the original official benchmark/harness method is run.
- `implemented-official-detector`: official AgentDojo detector logic is unchanged; only the dataset input is adapted into tool-output texts.
- `implemented`: current WAMI paper-faithful result is available.

Note: `data/agentdojo_spotlighting_table1.*` is treated as an exploratory converted-trajectory adaptation only. The formal no-API same-dataset row uses `data/agentdojo_official_detector_wami_datasets_full.*`.
