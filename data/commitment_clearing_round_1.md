# Commitment Clearing Round 1

This round clears three paper commitments that previously had runnable code but
did not yet have explicit experiment files.

## 1. Static vs Dynamic Threshold

Evidence files:

- `data/static_dynamic_threshold_injecagent.md`
- `data/static_dynamic_threshold_bipia.md`
- `data/static_dynamic_threshold_agentdojo.md`

Results:

| Dataset | Static IR | Static FPR | Best Dynamic IR | Best Dynamic FPR | Observation |
|---|---:|---:|---:|---:|---|
| InjecAgent | 99.7% | 0.0% | 99.7% | 0.0% | Dynamic threshold is equivalent on this dataset. |
| BIPIA | 100.0% | 6.2% | 100.0% | 6.2% | Dynamic threshold is equivalent under tested lambdas. |
| AgentDojo | 94.5% | 3.5% | 94.7% | 3.5% | Dynamic threshold gives a tiny IR increase at lambda 0.05. |

Conclusion: the paper's dynamic threshold formula is implemented and runnable.
On the current converted datasets, the effect is small because many decisions are
dominated by TDG/security-rule evidence rather than only by late-step threshold
decay.

## 2. Multimodal Backend Ablation

Evidence files:

- `data/current_cyberseceval3_vpi_qwenvl_40.md`
- `data/vpi_native_backend_40.md`

Results on 40 CyberSecEval3 VPI rows:

| Backend | IR | FPR | ACC | Avg latency ms |
|---|---:|---:|---:|---:|
| Native text/image metadata only | 100.0% | 90.0% | 55.0% | 53.878 |
| Qwen-VL image understanding | 100.0% | 0.0% | 100.0% | 11384.2 |

Conclusion: the multimodal component has clear measured value on the adapted VPI
test. The native backend catches attack rows but over-blocks benign image rows,
while Qwen-VL separates benign and malicious visual instructions much better at
the cost of much higher latency and API usage.

## 3. LLM Shadow Training Ablation

Evidence files:

- `data/current_llm_shadow_attacks_agentdojo_qwen_10x6.jsonl`
- `data/current_agentdojo_with_llm_shadow_10x6.jsonl`
- `data/llm_shadow_training_comparison.md`

Results on AgentDojo plus 60 generated shadow attacks:

| Variant | IR | FPR | ACC | N |
|---|---:|---:|---:|---:|
| Without LLM-shadow training | 89.2% | 3.5% | 90.0% | 713 |
| With LLM-shadow training | 84.5% | 2.3% | 86.1% | 713 |

Conclusion: LLM-shadow generation and training are now real runnable components,
but the current two-epoch model is not yet a performance win. It reduces false
positives while also lowering interception rate. This should be reported as a
working robustness-training path that still needs more data, harder negative
sampling, and calibration before being claimed as an accuracy improvement.
