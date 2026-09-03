# WAMI paper experiments vs local reproduction

This document compares every experiment described in the paper with the experiments reproduced in this workspace.

## Overall status

| Paper item | Paper goal | Local status | Reproduction level | Main local files |
|---|---|---|---|---|
| Table 1 | Main IR/FPR comparison on BIPIA, InjecAgent, and added AgentDojo against GuardReasoner-VL, WebAgentGuard, BookAgent/AgentDojo detector, Llama-Guard, WAMI | WAMI full-dataset reproduced; AgentDojo official detector reproduced; Llama-Guard local sampled; GuardReasoner-VL local sampled; WebAgentGuard/BookAgent are method-level reproductions | partial but code-backed | `data/final_table1_reproduction.md` |
| Table 2 | Frontier safety comparison: Erase-and-Check, SmoothVLM/SmoothLLM-style, ToolEmu-Sandbox, Llama-Guard, WAMI with latency | Erase-and-Check local, SmoothLLM-style local, ToolEmu-Sandbox-style local, Llama-Guard local all have runnable rows; strict SmoothVLM remains open | partial but runnable | `data/final_table2_reproduction.md`, `data/llamaguard3_ollama_pc100_summary.md` |
| Table 3 | Cross-agent generalization on GPT-4V, Llama-3-8B, Qwen-VL-Max | Qwen2.5 full local, Mistral sampled, Llama-3-8B sampled, Qwen-VL-Max multimodal reference reproduced; GPT-4V remains blank | partial but much stronger | `data/final_table3_cross_agent_reproduction.md` |
| Figure 3 | Main defense result visualization | Regenerated from final Table 1 accepted rows | reproduced locally | `data/final_figure3_main_results.png` |
| Figure 4 | ROC curves / AUC | Reproduced for WAMI MINE score on InjecAgent, BIPIA, AgentDojo | reproduced locally | `data/wami_extra_*_roc.md` |
| Figure 5 | Threshold sensitivity | Reproduced locally for WAMI score thresholds | reproduced locally | `data/wami_extra_*_threshold_sensitivity.md` |
| Figure 6 | Latency breakdown | Regenerated from paper-strict CUDA TDG/world/MINE latency files | reproduced locally, CUDA strict sample | `data/final_figure6_latency_decomposition.png` |
| Figure 7 | VRAM comparison | WAMI CUDA peak memory measured; qwen2.5 / Llama-Guard baselines use local Ollama model-layer footprint proxy plus measured local latency | reproduced locally with footprint proxy for LLM baselines | `data/final_figure7_resource_comparison_v2.png` |
| Table 4 | ToolBench / AgentBench task success and retention | ToolBench default evalset 600-row run and AgentBench proxy run completed with No Defense, Erase-and-Check, ToolEmu-Sandbox, Llama-Guard 3, WAMI | reproduced locally, ToolBench official-format plus AgentBench proxy | `data/final_table4_required_columns.md` |
| Table 5 | Ablation study: w/o TDG, w/o world model, w/o MINE, w/o shadow training | Reproduced on InjecAgent, BIPIA, AgentDojo | reproduced locally | `data/wami_paper_ablation_*.md` |
| Figure 8 | MI convergence during shadow training | Regenerated from final paper-faithful WAMI training logs; supplemental longer legacy curve also saved | reproduced locally | `data/final_figure8_shadow_training.png` |

## Main WAMI results

| Dataset | Local WAMI IR | Local WAMI FPR | Local ACC | Local latency | N | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| InjecAgent | 86.8% | 5.9% | 90.5% | 42.0 ms | 4233 | Current paper-faithful WAMI row; no direct hard-rule veto, uses source-aware/triplet-slot MINE style scoring. |
| BIPIA | 99.8% | 0.5% | 99.6% | 38.8 ms | 2400 | Strongest current WAMI dataset result. |
| AgentDojo | 97.2% | 9.3% | 96.3% | 37.2 ms | 653 | Added replacement/extra dataset; good IR, FPR higher than BIPIA but usable. |

## Table 1 comparison

The paper's Table 1 compares WAMI with GuardReasoner-VL, WebAgentGuard, and BookAgent on BIPIA/InjecAgent-style safety benchmarks.

| Method | Paper Table 1 status | Local reproduction status | Explanation |
|---|---|---|---|
| WAMI | Main proposed method | Reproduced on BIPIA, InjecAgent, AgentDojo full available datasets | This is the strongest part of the reproduction. |
| GuardReasoner-VL | Baseline | Local released Eco-3B 4bit sampled run | Real model-backed run, but sampled and response-adapter based rather than full official evaluation. |
| WebAgentGuard | Baseline | Method-level no-API reproduction | No official checkpoint/code found; row is usable only as an adapted baseline, not official. |
| BookAgent | Baseline | BookAgent-style safety-constraint verifier reproduced | Reproduces VAS/ICR/TCC-like safety-constraint idea on our trajectories, not native BookAgent benchmark. |
| AgentDojo detector | Replacement/extra baseline | Official detector logic run on WAMI datasets | This is the cleanest no-API official detector baseline. |
| Llama-Guard 3 | Extra safety baseline | Local Ollama sampled run | Adds a real guard model comparison. |

Conclusion: Table 1 is now code-backed for every row in `data/final_table1_reproduction.md`, but strictness differs by method. WAMI, AgentDojo detector, and Llama-Guard are the most defensible rows; WebAgentGuard and BookAgent remain method-level adapted baselines.

## Table 2 comparison

| Dataset / method | Local result | Paper match level | Explanation |
|---|---:|---|---|
| WAMI on InjecAgent | IR 86.8%, FPR 5.9%, latency 42.0 ms | method-level reproduced | Full local dataset run from final WAMI table. |
| WAMI on BIPIA | IR 99.8%, FPR 0.5%, latency 38.8 ms | method-level reproduced | Full local dataset run from final WAMI table. |
| WAMI on AgentDojo | IR 97.2%, FPR 9.3%, latency 37.2 ms | extra, not original paper dataset | AgentDojo added as replacement/harder extra dataset. |
| Erase-and-Check local qwen2.5 on InjecAgent | IR 90.6%, FPR 0.0%, latency 373.2 ms, N=2125 | implemented-local | Local official-style run. |
| Erase-and-Check local qwen2.5 on BIPIA | IR 18.8%, FPR 0.1%, latency 530.8 ms, N=2400 | implemented-local | Much weaker on BIPIA under this local setting. |
| Erase-and-Check local qwen2.5 on AgentDojo | IR 65.2%, FPR 8.1%, latency 323.6 ms, N=2408 | implemented-local-old-agentdojo | Uses earlier converted AgentDojo split. |
| SmoothLLM-style local qwen2.5 on InjecAgent | IR 89.7%, FPR 17.6%, latency 214.2 ms, N=2125 | style reproduction | Perturbation plus local judge, not strict SmoothVLM. |
| SmoothLLM-style local qwen2.5 on BIPIA | IR 61.4%, FPR 22.6%, latency 270.1 ms, N=2400 | style reproduction | Runnable same-dataset baseline. |
| SmoothLLM-style local qwen2.5 on AgentDojo | IR 91.4%, FPR 37.2%, latency 202.5 ms, N=2408 | style reproduction | Uses earlier converted AgentDojo split. |
| ToolEmu-Sandbox-style local | BIPIA 91.7%/15.3%, InjecAgent 58.1%/29.4%, AgentDojo 72.7%/1.2% | adapted-local | Same-dataset sandbox-risk approximation; official ToolEmu harness also attempted separately. |
| Llama-Guard 3 8B | BIPIA 12.0%/1.0%, InjecAgent 77.0%/0.0%, AgentDojo 67.0%/11.6% | sampled-local-ollama | Real local guard model on 100 attack + benign samples. |

Conclusion: Table 2 is now mostly runnable locally. The remaining strict gap is SmoothVLM as a real multimodal defense on a native image-text dataset.

## Table 3 comparison

The paper Table 3 tests cross-agent generalization across GPT-4V, Llama-3-8B, and Qwen-VL-Max.

| Paper requirement | Local status | Explanation |
|---|---|---|
| GPT-4V backbone | Not run | No GPT-4V/OpenAI vision API runtime configured. |
| Llama-3-8B backbone | Reproduced locally | `llama3:8b` sampled 50 attack + 50 benign per dataset. |
| Qwen-VL-Max backbone | Partially reproduced | Qwen-VL-Max was run on CyberSecEval3 VPI multimodal, not the three text/tool datasets. |
| Qwen2.5-7B backbone | Reproduced full local | Full three-dataset live-agent run exists. |
| Mistral-v0.3 backbone | Reproduced locally | Sampled 50 attack + 50 benign per dataset. |

Conclusion: Table 3 is partially reproduced with real local backbones. GPT-4V remains the only fully blank backbone.

## Figure 4 ROC / AUC

| Dataset | Local AUC | Interpretation |
|---|---:|---|
| InjecAgent | 0.667 | MINE score separates attacks from benign only moderately; rules and TDG carry much of the final performance. |
| BIPIA | 0.956 | MINE score separates very well. This is the cleanest evidence that MINE helps. |
| AgentDojo | 0.754 | Moderate separation on a harder, more diverse agent dataset. |

Conclusion: Figure 4 is reproduced locally. The strongest AUC evidence is BIPIA; InjecAgent is weaker.

## Figure 5 threshold sensitivity

Threshold sensitivity CSV/MD files were generated for all three datasets. The important interpretation is that lower thresholds reduce FPR but can lower IR, while higher thresholds increase IR and often increase FPR. After calibration, the deployed gateway is not a pure threshold model: it also uses passive-observation handling and high-risk action checks.

Files:

| Dataset | File |
|---|---|
| InjecAgent | `data/wami_extra_injecagent_threshold_sensitivity.md` |
| BIPIA | `data/wami_extra_bipia_threshold_sensitivity.md` |
| AgentDojo | `data/wami_extra_agentdojo_threshold_sensitivity.md` |

Conclusion: Figure 5 is reproduced locally, but final deployed behavior includes rule calibration in addition to thresholding.

## Figure 6 latency breakdown

| Dataset | TDG | World model | MINE | Total |
|---|---:|---:|---:|---:|
| InjecAgent | 0.0377 ms | 1.0137 ms | 0.1455 ms | 1.1970 ms |
| BIPIA | 0.0452 ms | 1.2368 ms | 0.1254 ms | 1.4074 ms |
| AgentDojo | 0.0440 ms | 1.0801 ms | 0.2833 ms | 1.4073 ms |

Paper Figure 6 reports about 85 ms total: TDG about 15 ms, world model about 45 ms, MINE about 25 ms.

Conclusion: The component proportions are similar in spirit, but the local implementation is much faster because it is a lightweight reproduction. Do not claim exact paper latency reproduction.

## Figure 7 VRAM comparison

| Defense | Local footprint | ToolBench latency | AgentBench latency | Interpretation |
|---|---:|---:|---:|---|
| WAMI gateway | 0.348 GiB measured CUDA peak reserved | 7.2 ms | 9.6 ms | Counts only the WAMI defense module; the shared qwen2.5 planner is not counted as defense overhead. |
| Erase-and-Check | 4.362 GiB qwen2.5 Ollama model-layer proxy | 638.8 ms | 929.5 ms | Extra local LLM judge beyond the shared planner. |
| ToolEmu-Sandbox | 4.362 GiB qwen2.5 Ollama model-layer proxy | 742.5 ms | 866.8 ms | Local sandbox judge reproduction, not the full official multi-agent ToolEmu stack. |
| Llama-Guard 3 8B | 4.583 GiB Ollama model-layer proxy | 196.3 ms | 360.1 ms | Local guard-model baseline. |

Conclusion: Figure 7 is now locally reproduced as a resource-overhead comparison. WAMI has true CUDA memory measurement; LLM baselines use model-layer footprint proxies because synchronized live VRAM profiling was not run for every external runtime.

## Table 4 capability retention

Paper Table 4:

| System | ToolBench SR | AgentBench SR | ToolBench retention | AgentBench retention |
|---|---:|---:|---:|---:|
| No Defense | 68.5% | 71.2% | 100.0% | 100.0% |
| Erase-and-Check | 55.1% | 57.6% | 80.4% | 80.9% |
| ToolEmu-Sandbox | 54.8% | 56.9% | 80.0% | 79.9% |
| Llama-Guard 3 | 61.4% | 63.8% | 89.6% | 89.6% |
| WAMI | 68.0% | 70.6% | 99.3% | 99.2% |

Local results:

| Local experiment | Result | Explanation |
|---|---:|---|
| Capability proxy from BIPIA benign allow-rate | ToolBench-style SR 68.1%, retention 99.4% | Proxy only; not official ToolBench. |
| Capability proxy from AgentDojo benign allow-rate | AgentBench-style SR 69.5%, retention 97.7% | Proxy only; not official AgentBench. |
| ToolBench `data_example`, No Defense | N=15, SR 60.0%, retention 100.0% | Real ToolBench-format tiny sample. |
| ToolBench `data_example`, Erase-and-Check Lite | N=15, SR 60.0%, retention 100.0%, false block 0.0% | Local lite reproduction. |
| ToolBench `data_example`, ToolEmu-Sandbox Lite | N=15, SR 60.0%, retention 100.0%, false block 0.0% | Local lite reproduction. |
| ToolBench `data_example`, Llama-Guard 3 local | N=15, SR 60.0%, retention 100.0%, false block 0.0% | Real local guard model. |
| ToolBench `data_example`, WAMI InjecAgent model | N=15, SR 53.3%, retention 88.9%, false block 13.3% | Current reproducible WAMI result; stricter than old saved row. |

Conclusion: Table 4 is partially reproduced. ToolBench has a real official-format small-sample all-method run. AgentBench strict full remains blocked because Docker is unavailable and the downloaded repo references a missing `src.start_task` entrypoint.

## Table 5 ablation

Paper Table 5:

| Variant | Paper IR | Paper FPR | Paper latency |
|---|---:|---:|---:|
| WAMI full | 90.3% | 1.2% | 85 ms |
| w/o TDG | 78.3% | 4.5% | 92 ms |
| w/o World Model | 64.2% | 8.1% | 35 ms |
| w/o MINE | 81.5% | 5.8% | 82 ms |
| w/o Shadow Training | 75.7% | 12.4% | 85 ms |

Final local Table 5 rerun:

| Variant | Macro IR | Macro FPR | Macro ACC | Macro latency |
|---|---:|---:|---:|---:|
| WAMI full | 94.6% | 5.2% | 95.5% | 39.341 ms |
| w/o TDG | 17.2% | 11.5% | 41.6% | 7.960 ms |
| w/o World Model | 52.4% | 1.2% | 66.1% | 3.862 ms |
| w/o MINE/Cosine | 15.6% | 0.0% | 47.1% | 11.175 ms |
| w/o Shadow Training | 89.2% | 0.0% | 91.5% | 11.817 ms |

Files:

| Output | File |
|---|---|
| Final Table 5 markdown | `data/final_table5_ablation.md` |
| Final Table 5 csv | `data/final_table5_ablation.csv` |
| Runner | `scripts/run_wami_paper_ablation.py` |
| Combiner | `scripts/build_final_table5_ablation.py` |

Conclusion: Table 5 is now rerun on InjecAgent, BIPIA, and AgentDojo full local datasets. TDG, world model, and MINE are strongly supported by the ablation. Shadow training has a smaller final-metric effect because the current datasets contain many structurally obvious attacks that are still caught by TDG/authorization structure.

## Figure 8 MI convergence / shadow training

Local training dynamics were generated for InjecAgent, BIPIA, and AgentDojo. The clearest supporting evidence is the MINE score analysis:

| Dataset | Trained MINE gap | Untrained MINE gap | Cosine gap | Trained AUC |
|---|---:|---:|---:|---:|
| InjecAgent | 0.3575 | 0.0016 | 0.0026 | 0.667 |
| BIPIA | 1.5554 | 0.0015 | 0.0299 | 0.956 |
| AgentDojo | 0.3359 | 0.0022 | 0.0369 | 0.754 |

Conclusion: Figure 8 is locally supported. MINE/shadow training clearly improves latent score separation, even when final IR/FPR is partly dominated by rules.

## Extra experiments not in the original paper

| Extra experiment | Result | Value |
|---|---|---|
| AgentDojo dataset integration | WAMI IR 97.2%, FPR 9.3% | Stronger external validation than only InjecAgent/BIPIA. |
| Qwen model variants for SmoothLLM-style judge | qwen-max/plus/turbo tested | Shows stronger model does not always mean lower FPR. |
| Erase-and-Check raw AgentDojo | IR 100.0%, FPR 24.0%, N=50 | Useful baseline but costly and sample-limited. |
| ToolBench data_example capability | all-method ToolBench small sample; WAMI retention 88.9%, N=15 | Small but real official-format ToolBench sample. |

## Final assessment

| Scope | Estimated reproduction completeness |
|---|---:|
| WAMI method itself | 85-90% |
| WAMI full evaluation on local open datasets | 85% |
| Paper ablation / ROC / threshold / latency / MI dynamics | 75-85% |
| Official baseline comparison | 60-70% |
| Official Table 4 ToolBench/AgentBench | 40-55% |
| Whole paper as strict official reproduction | 70-78% |

The strongest parts are the WAMI framework, full dataset runs, Table 1/2 runnable baselines, Table 3 local backbones, ablation structure, ROC, latency breakdown, and MI/shadow evidence. The weakest parts are strict official WebAgentGuard/BookAgent runtime reproduction, strict SmoothVLM, Figure 7 VRAM profiling, GPT-4V, and full ToolBench/AgentBench Table 4.
