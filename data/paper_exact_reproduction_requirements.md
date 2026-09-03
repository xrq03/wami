# Exact Reproduction Requirements From Final WAMI Paper

Source PDF:

`WAMI__World_model_Assisted_Multi_modal_Intention_Alignment_for_Secure_Agent_Action(6).pdf`

This file treats the PDF as the final paper version and lists what is required
to make the repository match the paper as closely as possible. It intentionally
separates exact paper claims from the current local implementation.

## Paper Implementation Specification

| Item | Paper Specification | Current Local State | Gap |
|---|---|---|---|
| Hardware | 4 x NVIDIA A100 80GB, 2TB RAM, 128-core AMD EPYC | local Windows machine | cannot exactly match unless equivalent server is available |
| Framework | PyTorch 2.2, HuggingFace Transformers, vLLM | numpy WAMI plus optional torch model | torch path exists but not paper-sized/default |
| Agent backbone | Qwen-VL-Max | Qwen API config exists; Qwen-VL used on VPI only | main InjecAgent/BIPIA pipeline not fully Qwen-VL-Max agent harness |
| World model | 4-layer Transformer Encoder | `wami/torch_model.py` default 2 layers | must change/train paper-sized model |
| Hidden dimension | 1024 | torch default hidden 512, numpy dim 128 | must align |
| Attention heads | 8 | torch default 4 heads | must align |
| MINE estimator | 3-layer MLP with ReLU | numpy bilinear critic; torch MLP exists but must verify layer count | must align paper estimator |
| Optimizer | AdamW | torch path uses optimizer, numpy path custom SGD-like updates | strict reproduction requires torch path |
| Learning rate | 2e-4 | script default 0.03 numpy / torch configurable | must align |
| LR schedule | cosine annealing | not guaranteed in all scripts | must align |
| Batch size | 64 | current training mostly sample loop | must implement/run batched training |
| Epochs | 20 | current main e3/e5; torch smoke e1 | must train 20 epochs |
| Dynamic threshold | tau initialized to 0.15, greedy validation calibration | current gateway default -0.05 / calibration quantile; paper formula notes exist | must add exact tau=0.15 greedy search mode |

## Paper Experiments To Reproduce

### Table 1: Agent Defense Methods Performance

| Dataset | Method | Paper IR | Paper FPR | Needed For Strict Reproduction |
|---|---|---:|---:|---|
| BIPIA | GuardReasoner-VL | 62.5% | 6.2% | GuardReasoner-VL model weights/runtime, BIPIA protocol |
| BIPIA | WebAgentGuard | 84.7% | 28.5% | official WebAgentGuard code or exact guard-agent prompt/model |
| BIPIA | BookAgent | 86.3% | 14.8% | exact BookAgent defense protocol used in the paper |
| BIPIA | WAMI | 88.9% | 1.5% | paper WAMI torch model, Qwen-VL-Max agent pipeline, validation threshold |
| InjecAgent | GuardReasoner-VL | 38.4% | 5.8% | GuardReasoner-VL strict run |
| InjecAgent | WebAgentGuard | 91.2% | 36.4% | official/exact WebAgentGuard setup |
| InjecAgent | BookAgent | 85.5% | 17.2% | exact BookAgent defense protocol |
| InjecAgent | WAMI | 90.3% | 1.2% | paper WAMI strict run |

### Table 2: Frontier Security Comparison

| Method | Datasets | Paper Metrics | Needed For Strict Reproduction |
|---|---|---|---|
| No Defense | InjecAgent/BIPIA | IR 0, FPR 0 | easy, define attack success baseline |
| Erase-and-Check | InjecAgent/BIPIA | 66.2/10.5, 63.5/11.0, about 3100-3200ms | exact Erase-and-Check model/prompt/masking settings |
| SmoothVLM | InjecAgent/BIPIA | 72.1/7.9, 69.4/8.2, about 2400ms | SmoothVLM code/model, not SmoothLLM text-only substitute |
| ToolEmu-Sandbox | InjecAgent/BIPIA | 75.6/13.6, 73.2/14.0, >5800ms | ToolEmu runtime plus benchmark adapter |
| Llama-Guard 3 8B | InjecAgent/BIPIA | 79.8/6.1, 77.4/6.5, about 1150ms | Llama-Guard 3 8B weights and GPU inference |
| WAMI | InjecAgent/BIPIA | 90.3/1.2, 88.9/1.5, 85/90ms | paper WAMI strict model and threshold |

### Table 3: Cross-agent Generalization

| Base Model | Paper WAMI Result | Needed |
|---|---|---|
| GPT-4V | 87.8% / 1.0% | GPT-4V API access and exact agent prompts |
| Llama-3-8B | 88.9% / 1.5% | local/API Llama-3-8B multimodal or specified wrapper |
| Qwen-VL-Max | 90.3% / 1.2% | Qwen-VL-Max API and exact WAMI integration |

Also required: Erase-and-Check and Llama-Guard 3 results under each backbone.

### Figure 4: ROC Curves

| Method | Paper AUC |
|---|---:|
| WAMI | 0.992 |
| Llama-Guard 3 | 0.841 |
| ToolEmu-Sandbox | 0.795 |
| SmoothVLM | 0.785 |
| Erase-and-Check | 0.768 |

Needed: score outputs, not only binary decisions, for all baselines.

### Figure 5: Threshold Sensitivity

Paper varies mutual-information threshold tau from 0 to 5 and shows IR/FPR.

Needed: WAMI score scale must match paper tau scale. Current local scores use a
different scale, so the figure can be reproduced structurally but not numerically
until the paper MINE network and training procedure are used.

### Figure 6: Latency Decomposition

Paper claims:

| Component | Paper Latency |
|---|---:|
| TDG construction | about 15 ms |
| World model inference | about 45 ms |
| MINE gateway | about 25 ms |
| Total | 85 ms |

Needed: benchmark paper-sized torch model on comparable GPU. Current numpy
model is much faster and much smaller, so its latency cannot be used as strict
evidence for the paper claim.

### Figure 7: VRAM Consumption

Paper claims:

| Method | Paper VRAM |
|---|---:|
| WAMI | about 450 MB |
| SmoothVLM / Erase-and-Check | 2-5 GB |
| Llama-Guard 3 8B | about 16 GB |
| ToolEmu-Sandbox | 16-140 GB |

Needed: GPU memory measurement on a CUDA setup. Current CPU/RSS profiling is
not a strict reproduction.

### Table 4: ToolBench / AgentBench Capability

| System | ToolBench SR | AgentBench SR | ToolBench Retention | AgentBench Retention |
|---|---:|---:|---:|---:|
| No Defense | 68.5% | 71.2% | 100.0% | 100.0% |
| Erase-and-Check | 55.1% | 57.6% | 80.4% | 80.9% |
| ToolEmu-Sandbox | 54.8% | 56.9% | 80.0% | 79.9% |
| Llama-Guard 3 | 61.4% | 63.8% | 89.6% | 89.6% |
| WAMI | 68.0% | 70.6% | 99.3% | 99.2% |

Needed: official ToolBench and AgentBench harness execution, base model, tool
logs, scoring scripts.

### Table 5: Ablation Study

| Variant | Paper IR | Paper FPR | Paper Latency |
|---|---:|---:|---:|
| WAMI Full | 90.3% | 1.2% | 85 ms |
| w/o TDG Graph Construction | 78.3% | 4.5% | 92 ms |
| w/o World Model Rollout | 64.2% | 8.1% | 35 ms |
| w/o MINE Gateway | 81.5% | 5.8% | 82 ms |
| w/o Shadow Adversarial Training | 75.7% | 12.4% | 85 ms |

Needed: paper-sized WAMI model, InjecAgent exact evaluation set, identical
threshold calibration, GPU latency measurement.

### Figure 8: Shadow Training Dynamics

Paper claim: MI gap separates and stabilizes around epoch 15 over 30 epochs.

Needed: 30-epoch training logs from the paper-sized torch WAMI model.

## What You Need To Provide Or Enable

| Priority | Need | Why |
|---:|---|---|
| 1 | Confirm we can use Qwen-VL-Max API for main WAMI runs | paper main backbone is Qwen-VL-Max |
| 2 | Provide/approve local GPU details and CUDA/PyTorch setup | strict latency/VRAM and 4-layer 1024 model training need GPU |
| 3 | Provide Llama-Guard 3 8B weights/access | Table 2/3 and ROC require it |
| 4 | Provide SmoothVLM official code/model or exact repo | paper says SmoothVLM, not SmoothLLM |
| 5 | Provide official WebAgentGuard implementation or exact prompt/model | Table 1 strict baseline |
| 6 | Provide exact BookAgent defense protocol used in paper | current BookAgent PDF is not enough for the claimed defense row |
| 7 | Provide ToolEmu official runtime/API credentials | Table 2 strict ToolEmu-Sandbox |
| 8 | Provide ToolBench/AgentBench full harness configuration | Table 4 strict capability results |
| 9 | Confirm train/validation/test split for InjecAgent and BIPIA | paper mentions validation calibration but not split details in extracted text |
| 10 | Confirm whether paper numbers should be treated as target values or replaced by rerun values | important because current local results differ |

## Immediate Next Coding Tasks

These can be done without new external assets:

1. Add a paper-strict torch config: 4 layers, hidden 1024, 8 heads, MINE 3-layer MLP.
2. Add a paper-strict training script: AdamW, lr 2e-4, cosine schedule, batch size 64, 20/30 epochs.
3. Add tau=0.15 plus greedy validation calibration.
4. Add component latency measurement for TDG/world/MINE separately.
5. Add score export for ROC and threshold sensitivity.

These will make WAMI itself closer to the paper. Baseline strict reproduction
still depends on the external models and harnesses above.
