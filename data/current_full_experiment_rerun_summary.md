# Current Full Experiment Rerun Summary

This summary records the experiments rerun after the latest WAMI changes:

- Transformer/GRU-style cognitive world model support.
- Contrastive world training.
- Enhanced security-aware TDG data-flow analysis.
- LLM/local shadow attack generation.
- CyberSecEval3 visual prompt injection adaptation.

## 1. Health Check

```text
pytest: 10 passed
```

## 2. Main Dataset Training And Evaluation

| Dataset | Model | Epochs | IR | FPR | ACC | N | Training Notes |
|---|---|---:|---:|---:|---:|---:|---|
| InjecAgent | `wami_injecagent_current_e3.npz` | 3 | 94.6% | 0.0% | 97.3% | 4233 | `mi_gap` 0.4387 -> 1.0630 |
| BIPIA | `wami_bipia_current_e3.npz` | 3 | 100.0% | 1.0% | 99.5% | 2400 | `mi_gap` 0.1811 -> 0.5446 |
| AgentDojo | `wami_agentdojo_current_e3.npz` | 3 | 90.1% | 2.3% | 91.1% | 653 | `mi_gap` 0.0176 -> 0.0698 |

## 3. Paper-Style Ablation

### InjecAgent

| Variant | IR | FPR | Latency | ACC |
|---|---:|---:|---:|---:|
| Full WAMI | 94.6% | 0.0% | 1.566 ms | 97.3% |
| w/o TDG | 31.2% | 5.9% | 1.958 ms | 62.8% |
| w/o World | 100.0% | 5.9% | 0.906 ms | 97.0% |
| w/o MINE | 93.0% | 0.0% | 1.530 ms | 96.5% |
| w/o Shadow | 93.0% | 0.0% | 1.550 ms | 96.5% |

### BIPIA

| Variant | IR | FPR | Latency | ACC |
|---|---:|---:|---:|---:|
| Full WAMI | 100.0% | 1.0% | 2.759 ms | 99.5% |
| w/o TDG | 36.8% | 35.2% | 2.778 ms | 50.8% |
| w/o World | 100.0% | 0.2% | 1.423 ms | 99.9% |
| w/o MINE | 100.0% | 0.0% | 2.789 ms | 100.0% |
| w/o Shadow | 100.0% | 0.0% | 2.709 ms | 100.0% |

### AgentDojo

| Variant | IR | FPR | Latency | ACC |
|---|---:|---:|---:|---:|
| Full WAMI | 90.1% | 2.3% | 2.808 ms | 91.1% |
| w/o TDG | 24.5% | 24.4% | 2.565 ms | 31.2% |
| w/o World | 58.2% | 2.3% | 1.267 ms | 63.4% |
| w/o MINE | 83.6% | 0.0% | 2.831 ms | 85.8% |
| w/o Shadow | 83.6% | 0.0% | 2.794 ms | 85.8% |

## 4. Extra Paper-Style Outputs

Generated current CSV/Markdown files:

- `data/current_wami_extra_injecagent_threshold_sensitivity.*`
- `data/current_wami_extra_injecagent_roc.*`
- `data/current_wami_extra_injecagent_latency_breakdown.*`
- `data/current_wami_extra_injecagent_capability_proxy.*`
- `data/current_wami_extra_injecagent_training_dynamics.*`
- `data/current_wami_extra_bipia_threshold_sensitivity.*`
- `data/current_wami_extra_bipia_roc.*`
- `data/current_wami_extra_bipia_latency_breakdown.*`
- `data/current_wami_extra_bipia_capability_proxy.*`
- `data/current_wami_extra_bipia_training_dynamics.*`
- `data/current_wami_extra_agentdojo_threshold_sensitivity.*`
- `data/current_wami_extra_agentdojo_roc.*`
- `data/current_wami_extra_agentdojo_latency_breakdown.*`
- `data/current_wami_extra_agentdojo_capability_proxy.*`
- `data/current_wami_extra_agentdojo_training_dynamics.*`

Selected current extra results:

| Dataset | TDG ms | World ms | MINE ms | Total ms | Capability Retention Proxy |
|---|---:|---:|---:|---:|---:|
| InjecAgent | 0.0591 | 1.8473 | 0.2061 | 2.1125 | see generated file |
| BIPIA | see generated file | see generated file | see generated file | see generated file | 99.0% |
| AgentDojo | see generated file | see generated file | see generated file | see generated file | 97.7% |

## 5. CyberSecEval3 Visual Prompt Injection

The current 100-row rerun was attempted but timed out because Qwen-VL image calls were slow. The previous 100-row completed table remains available:

- `data/cyberseceval3_vpi_qwenvl_100.csv`
- `data/cyberseceval3_vpi_qwenvl_100.md`

Current rerun completed 40 rows:

| Dataset | Backend | Rows | TP | FP | TN | FN | IR | FPR | ACC | Avg Latency |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CyberSecEval3 VPI adapted | WAMI + Qwen-VL-Max | 40 | 20 | 0 | 20 | 0 | 100.0% | 0.0% | 100.0% | 11384.2 ms |

Files:

- `data/current_cyberseceval3_vpi_qwenvl_40.csv`
- `data/current_cyberseceval3_vpi_qwenvl_40.md`

## 6. LLM Shadow Attack Generation

Current rerun generated:

| Generator | Samples | Attacks | Attack Kinds |
|---|---:|---:|---|
| Local fallback | 3 | 18 | all 6 kinds |
| Qwen LLM | 3 | 18 | all 6 kinds |

Attack kinds:

- `cross_tool_injection`
- `multi_step_indirect_injection`
- `visual_injection`
- `context_pollution`
- `hidden_goal_shift`
- `sensitive_tool_hijack`

Merged training smoke:

```text
merged_rows=671
epoch=001 loss=1.3797 mi_gap=0.0176 world_loss=0.1478
IR=0.841 FPR=0.012 ACC=0.860 total=671
```

Files:

- `data/current_local_shadow_attacks_agentdojo_smoke.jsonl`
- `data/current_llm_shadow_attacks_agentdojo_qwen_smoke.jsonl`
- `data/current_agentdojo_with_llm_shadow_smoke.jsonl`
- `wami_current_agentdojo_llm_shadow_smoke_e1.npz`

## 7. Current Interpretation

The current WAMI implementation now has stronger method-level coverage:

- Security-aware TDG with tool order, data dependency, taint propagation, sensitive flow, and memory dependency.
- Autoregressive cognitive sandbox with memory/subgoal/observation.
- World-model contrastive training.
- MINE gateway.
- LLM-generated shadow adversarial training.
- Qwen-VL multimodal visual prompt-injection evaluation.

Remaining strict-reproduction limits:

- The exact original paper latent encoder and world-model weights are not available.
- Several official baselines still require external official harnesses or heavy model environments.
- CyberSecEval3 VPI is an adapted multimodal benchmark, not a native WAMI paper dataset.
