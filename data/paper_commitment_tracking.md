# Paper Commitment Tracking

This file tracks every major method, experiment, baseline, and figure promised
by the WAMI paper draft, and records whether the current repository has code,
data, and runnable results.

## Method Modules

| Commitment | Code | Result/Evidence | Status | Next Action |
|---|---|---|---|---|
| TDG construction | `wami/tdg.py` | `trace_wami_decision.py` | cleared | Maintain |
| Security-aware TDG data flow | `analyze_tdg_security` | `data/tdg_security_flow_design.md` | cleared | Maintain |
| Cognitive sandbox | `wami/model.py`, `wami/torch_model.py` | `data/world_model_design_reproduction.md`; `data/paper_exact_reproduction_requirements.md`; `data/commitment_clearing_round_5_paper_strict_wami.md`; `data/wami_paper_strict_zero_supervision_e20_cuda_gateway_v4.md` | strict zero-supervision run completed | Improve generic tool-response injection detection |
| World-model training | `train_world_step`, torch InfoNCE | `data/wami_paper_strict_zero_supervision_e20_cuda.progress.csv`; `data/wami_paper_strict_zero_supervision_e20_cuda.md`; `scripts/train_wami_paper_strict.py` | strict 20-epoch GPU run completed | Improve generated validation distribution |
| MINE gateway | `wami/gateway.py`, torch MLP | main results/ablation; `data/paper_exact_reproduction_requirements.md`; `data/commitment_clearing_round_5_paper_strict_wami.md` | paper-strict code path added | Run strict ablation after full training |
| Dynamic threshold | `threshold(step)`, `greedy_calibrate_gateway` | `data/threshold_strategy_paper_check.md`; `data/static_dynamic_threshold_*.md`; `data/paper_exact_reproduction_requirements.md`; `wami/paper_calibration.py`; `data/wami_paper_strict_zero_supervision_e20_cuda_gateway_v4.md` | strict validation calibration completed | Improve generic tool-response injection detection |
| Shadow adversarial training | `wami/shadow.py` | current models | cleared | LLM-shadow scale-up pending |
| LLM-generated shadow attacks | `wami/shadow_llm.py` | `data/current_llm_shadow_attacks_agentdojo_qwen_10x6.jsonl`; `data/llm_shadow_training_comparison.md` | cleared as runnable | More data/epochs can improve |
| Self-generated training data | `scripts/generate_self_training_data.py`; `scripts/run_self_generated_training_experiment.py` | `data/self_generated_training_experiment_500_per_eval_cal_cap06_e1.md` | cleared as repaired stress-training experiment | Maintain domain-aware calibration |
| Online action gateway | `wami/online_gateway.py` | `demo_online_cognitive_gateway.py` | cleared | Maintain |
| Multimodal input | `wami/multimodal.py` | CyberSecEval3 VPI runs; `data/vpi_native_backend_40.md` | cleared as extension | Larger VPI run optional |

## Datasets And Experiments

| Commitment | Current Dataset | Result File | Status | Next Action |
|---|---|---|---|---|
| InjecAgent main result | `data/injecagent_wami.jsonl` | `data/current_full_experiment_rerun_summary.md` | cleared | Maintain |
| BIPIA main result | `data/bipia_wami.jsonl` | `data/current_full_experiment_rerun_summary.md` | cleared | Maintain |
| AgentDojo / replacement | `data/agentdojo_wami.jsonl` | `data/current_wami_paper_ablation_agentdojo.md` | cleared as replacement | State clearly |
| Multimodal VPI | CyberSecEval3 VPI | `data/current_cyberseceval3_vpi_qwenvl_40.md`; `data/vpi_native_backend_40.md` | cleared as extension | Larger run optional |
| Ablation: w/o TDG | all main datasets | `data/current_wami_paper_ablation_*.md`; `data/wami_v4_ablation.md` | cleared; v4 unified rerun partial | Maintain / add stricter TDG edge ablation if needed |
| Ablation: w/o World | all main datasets | `data/current_wami_paper_ablation_*.md`; `data/wami_v4_ablation.md` | cleared; v4 unified rerun partial | Maintain / add explicit no-rollout variant if needed |
| Ablation: w/o MINE | all main datasets | `data/current_wami_paper_ablation_*.md`; `data/wami_v4_ablation.md` | cleared; v4 unified rerun | Maintain |
| Ablation: w/o Shadow | all main datasets | `data/current_wami_paper_ablation_*.md` | cleared | Maintain |
| Ablation: static threshold | main datasets | `data/static_dynamic_threshold_*.md` | cleared | Maintain |
| Ablation: w/o multimodal | VPI | `data/vpi_native_backend_40.md`; `data/current_cyberseceval3_vpi_qwenvl_40.md` | cleared | Larger run optional |
| Ablation: w/o LLM shadow | AgentDojo LLM-shadow data | `data/llm_shadow_training_comparison.md` | cleared | Tune epochs/calibration |
| Self-generated data augmentation | mixed official + synthetic | `data/self_generated_training_experiment_500_per_eval_cal_cap06_e1.md` | cleared as repaired stress-training experiment | Maintain domain-aware calibration |
| Zero-supervision official test | generated train/val only; official datasets test-only | `data/wami_paper_strict_zero_supervision_e20_cuda_gateway_v4.md`; `data/wami_paper_strict_zero_supervision_e20_cuda_gateway_v4.csv` | completed, current best | Improve InjecAgent response-embedded injection detection |

## Baselines

| Baseline | Current Status | Strictness | Evidence | Next Action |
|---|---|---|---|---|
| Erase-and-Check | implemented/API sampled | method-level | `data/table2_official_erase_check_*.md`; `data/commitment_clearing_round_4_baselines.md`; `data/paper_exact_reproduction_requirements.md` | Need exact paper model/prompt/settings |
| SmoothVLM / SmoothLLM | SmoothLLM partial, SmoothVLM not strict | method-level/partial | `data/smoothllm_*`; `data/commitment_clearing_round_4_baselines.md`; `data/paper_exact_reproduction_requirements.md` | Need SmoothVLM official code/model |
| ToolEmu-Sandbox | import/proxy only | proxy/incomplete | `scripts/run_official_toolemu.py`; `data/official_baseline_status.md`; `data/commitment_clearing_round_4_baselines.md` | State limitation |
| Llama-Guard 3 8B | not run | missing | none | Optional if GPU/model allowed |
| GuardReasoner-VL | repo present, not full inference | partial/proxy | `external/GuardReasoner-VL`; `data/table1_proxy_baselines.md`; `data/commitment_clearing_round_4_baselines.md` | Optional model setup |
| WebAgentGuard | Qwen method-level | method-level | `data/webagentguard_paper_method_sample.md`; `data/commitment_clearing_round_4_baselines.md` | Maintain as method-level |
| ToolBench/AgentBench | proxy | proxy | `data/toolbench_agentbench_official_harness_status.md`; `data/table4_capability_proxy.md`; `data/commitment_clearing_round_4_baselines.md` | State limitation |
| Final paper exact reproduction map | final PDF parsed | requirements audit | `data/paper_exact_reproduction_requirements.md` | Work through strict pending items |

## Figures / Analysis

| Figure/Analysis | Current Evidence | Status | Next Action |
|---|---|---|---|
| ROC/AUC | `data/current_wami_extra_*_roc.*` | cleared for WAMI | Baseline AUC optional |
| Threshold sensitivity | `data/current_wami_extra_*_threshold_sensitivity.*`; `data/static_dynamic_threshold_*.md` | cleared | Maintain |
| Latency breakdown | `data/current_wami_extra_*_latency_breakdown.*` | cleared | Maintain |
| Memory/resource | `data/wami_resource_profile.md`; `scripts/run_wami_resource_profile.py` | cleared | Optional full-limit rerun |
| Training dynamics | `data/current_wami_extra_*_training_dynamics.*` | cleared | Maintain |
| Case study trace | `trace_wami_decision.py` | cleared | Add selected case to paper |
| v4 decision contribution | `scripts/analyze_wami_v4_decision_contributions.py` | `data/wami_v4_decision_contributions.md` | cleared | Use to explain strong results |
