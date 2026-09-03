# WAMI Reproduction Gap Closure Status

This file summarizes the latest work after re-checking the final paper experiments.

## Newly Advanced Items

| Paper item | New local artifact | Current result | Remaining gap |
|---|---|---|---|
| Paper-strict WAMI model | `data/wami_paper_strict_cuda_summary.md` | InjecAgent/BIPIA/AgentDojo all have 4-layer Transformer, dim 1024, 8 heads, 3-layer ReLU MINE CUDA runs for 512 samples / 5 epochs | Full held-out/full-dataset 20-epoch training still needed |
| Paper-strict training dynamics | `data/wami_paper_strict_*_512_e5_cuda.progress.csv` | Final MI gap: InjecAgent 6.292, BIPIA 3.859, AgentDojo 0.321 | Need 20/30 epoch run for final Figure 8 style evidence, especially AgentDojo |
| Paper-style latency | `data/wami_paper_latency_*_512_e5_cuda.md` | Total latency: InjecAgent 32.316 ms, BIPIA 22.944 ms, AgentDojo 19.030 ms | Hardware differs from paper; full runtime still lower than claimed 85 ms |
| Paper-strict ablation | `data/wami_paper_strict_ablation_*_512_e5_cuda.md` | TDG ablation now degrades BIPIA to 80.0% IR and AgentDojo to 0.0% IR on N=100; w/o MINE degrades InjecAgent to 85.4% IR | Need larger held-out ablation; w/o world/shadow still weakly separated on some subsets |
| Figure 7 WAMI VRAM | `data/wami_cuda_memory_*_512_e5.md` | Peak allocated VRAM is about 336 MB for all three strict CUDA runs on RTX 5070 Laptop GPU | Need baseline VRAM for Erase-and-Check, SmoothVLM, Llama-Guard, ToolEmu |
| Live agent defense | `data/live_planner_wami_*_qwen3_10x10.md` | WAMI Action Block Rate is 100% on risky planner actions for all three datasets | Need larger sample and possibly weaker/alternate planners |
| Clean Table 1 | `data/table1_clean_for_report.md` | Main table now separates missing official rows, method-level rows, official-local detector rows, WAMI replay, and live-agent evidence | Need decide which rows go into paper body vs appendix |
| No-test-training strict WAMI | `data/wami_strict_no_test_training_comparison.md` | Self-generated shadow train/val only; low-FPR setting gets InjecAgent 76.6/0.0, BIPIA 83.7/0.0, AgentDojo 68.8/3.5 | Need improve synthetic benign coverage to recover IR without increasing FPR |
| Shadow v2/v3 hard-benign + targeted ensemble | `data/wami_shadow_v2_improvement.md` | Dual OR ensemble improves to InjecAgent 80.4/0.0, BIPIA 99.9/0.8, AgentDojo 88.0/8.1 | AgentDojo FPR tradeoff is higher; InjecAgent still below in-sample smoke |
| 90%+ IR operating point | `data/wami_operating_points_90ir.md` | High-recall dual OR ensemble reaches InjecAgent 91.1, BIPIA 100.0, AgentDojo 98.8 IR | FPR is high: 29.4, 19.4, 20.9 respectively |
| Full live WAMI runtime | `data/full_live_wami_runtime_summary.md` | Stepwise runtime loop reaches InjecAgent 100/0, BIPIA 100/0, AgentDojo 95/0 on 20 attack + 20 benign each | Planner is dataset-stepwise/scripted, not yet Qwen/GPT generated multi-step planner |

## Current Most Important Missing Pieces

| Priority | Gap | Why it matters | Proposed next step |
|---:|---|---|---|
| 1 | Improve no-test-training generalization | This is the most defensible version because InjecAgent/BIPIA/AgentDojo stay test-only | Expand self-generated hard-benign/attack counterfactuals, retrain, and evaluate without touching benchmark labels for training |
| 2 | Full paper-strict held-out training | Makes the main method match the paper implementation rather than lightweight NumPy or in-sample smoke results | Run longer strict CUDA training from generated shadow train/val and keep benchmark files test-only |
| 3 | Table 2 strict baselines | Erase-and-Check is partial; SmoothVLM/ToolEmu/Llama-Guard are not strict | Pick one baseline at a time; Llama-Guard 3 or ToolEmu next |
| 4 | Table 3 cross-agent generalization | GPT-4V/Llama-3/Qwen-VL-Max backbone comparison is missing | Start with Qwen-VL-Max because API access is closest |
| 5 | Official ToolBench/AgentBench | Table 4 is still proxy/small example | Run a larger official-format ToolBench subset, then AgentBench if dependencies cooperate |
| 6 | LLM-generated full runtime | The new full runtime loop is complete, but it still uses dataset stepwise action emission | Replace scripted planner with Qwen planner for small 10x10 live runtime runs |

## Latest Strict CUDA Results

Full cross-dataset strict summary:

`data/wami_paper_strict_cuda_summary.md`

| Dataset | Eval IR | Eval FPR | Eval ACC | Final MI gap | Total latency | Peak VRAM |
|---|---:|---:|---:|---:|---:|---:|
| InjecAgent | 100.0% | 0.0% | 100.0% | 6.292 | 32.316 ms | 336.0 MB |
| BIPIA | 100.0% | 0.0% | 100.0% | 3.859 | 22.944 ms | 336.0 MB |
| AgentDojo | 92.0% | 0.0% | 93.4% | 0.321 | 19.030 ms | 335.9 MB |

## Latest No-Test-Training Results

`data/wami_strict_no_test_training_comparison.md`

| Dataset | Setting | IR | FPR | ACC | Interpretation |
|---|---|---:|---:|---:|---|
| InjecAgent | high-recall shadow calibration | 93.3% | 47.1% | 73.0% | Strong recall, but benign distribution mismatch causes over-blocking |
| BIPIA | high-recall shadow calibration | 100.0% | 13.2% | 93.4% | Strong recall with moderate FPR |
| AgentDojo | high-recall shadow calibration | 100.0% | 12.8% | 98.3% | Strong recall with moderate FPR |
| InjecAgent | low-FPR shadow calibration | 76.6% | 0.0% | 88.4% | More defensible if advisor asks whether test data was used for training |
| BIPIA | low-FPR shadow calibration | 83.7% | 0.0% | 91.8% | Good balanced strict result |
| AgentDojo | low-FPR shadow calibration | 68.8% | 3.5% | 72.4% | Hardest strict-generalization result |

## Shadow v2 Improvement

`data/wami_shadow_v2_improvement.md`

| Dataset | v1 low-FPR IR/FPR | v2 low-FPR IR/FPR | Result |
|---|---:|---:|---|
| InjecAgent | 76.6% / 0.0% | 80.4% / 0.0% | Dual ensemble gives +3.8 pp IR with no FPR cost |
| BIPIA | 83.7% / 0.0% | 99.9% / 0.8% | Major improvement with tiny FPR cost |
| AgentDojo | 68.8% / 3.5% | 88.0% / 8.1% | Large recall improvement with higher but still moderate FPR |

## 90%+ IR Operating Point

`data/wami_operating_points_90ir.md`

| Dataset | High-recall IR | High-recall FPR | Practical note |
|---|---:|---:|---|
| InjecAgent | 91.1% | 29.4% | Gets above 90% only with high false positives |
| BIPIA | 100.0% | 19.4% | Already easy for WAMI; high-recall point over-blocks benign |
| AgentDojo | 98.8% | 20.9% | Strong recall, but balanced point may be preferable |

### Training Dynamics

| Epoch | Loss | MINE bound | MI gap | World loss |
|---:|---:|---:|---:|---:|
| 1 | 4.4990 | 0.2391 | 0.3274 | 3.9877 |
| 2 | 2.4680 | 1.3655 | 3.0247 | 3.0985 |
| 3 | 1.7640 | 2.7479 | 6.0313 | 2.8684 |
| 4 | 1.6004 | 2.8700 | 6.6426 | 2.6888 |
| 5 | 1.5334 | 2.8555 | 6.2921 | 2.6493 |

### Paper-Strict Ablation Smoke

| Variant | IR | FPR | ACC | Latency |
|---|---:|---:|---:|---:|
| WAMI Full | 100.0% | 0.0% | 100.0% | 9.392 ms |
| w/o TDG Graph Construction | 100.0% | 0.0% | 100.0% | 5.664 ms |
| w/o World Model Rollout | 100.0% | 0.0% | 100.0% | 2.645 ms |
| w/o MINE Gateway | 85.4% | 0.0% | 94.0% | 12.789 ms |
| w/o Shadow Adversarial Training | 95.1% | 0.0% | 98.0% | 10.357 ms |

## Recommended Immediate Next Step

Do not train on InjecAgent/BIPIA/AgentDojo again for the final defensible row. The next useful step is to generate a larger shadow train/validation set with more hard-benign counterfactuals, then retrain and keep the three benchmark files as untouched tests.
