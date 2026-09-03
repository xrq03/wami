# Paper vs local numeric delta report

差值定义：`Delta = Local - Paper`。IR/SR/Retention/AUC 越高越好，FPR/Latency/VRAM 越低越好。

## Table 1 main WAMI

| Item | Metric | Paper | Local | Delta | Equivalence | Cause | Improvement |
|---|---|---:|---:|---:|---|---|---|
| BIPIA WAMI | IR | 88.9% | 100.0% | +11.1 pp | method-level, not identical input pipeline | 本地使用 converted intent/plan/TDG 全量数据；论文表格是完整 agent/benchmark 口径。 | 用原始 benchmark harness 生成 action trajectory，再经过同一个 WAMI gateway 评估。 |
| BIPIA WAMI | FPR | 1.5% | 0.6% | -0.9 pp | method-level, not identical input pipeline | 本地使用 converted intent/plan/TDG 全量数据；论文表格是完整 agent/benchmark 口径。 | 用原始 benchmark harness 生成 action trajectory，再经过同一个 WAMI gateway 评估。 |
| InjecAgent WAMI | IR | 90.3% | 96.1% | +5.8 pp | method-level, not identical input pipeline | 本地使用 converted intent/plan/TDG 全量数据；论文表格是完整 agent/benchmark 口径。 | 用原始 benchmark harness 生成 action trajectory，再经过同一个 WAMI gateway 评估。 |
| InjecAgent WAMI | FPR | 1.2% | 0.0% | -1.2 pp | method-level, not identical input pipeline | 本地使用 converted intent/plan/TDG 全量数据；论文表格是完整 agent/benchmark 口径。 | 用原始 benchmark harness 生成 action trajectory，再经过同一个 WAMI gateway 评估。 |

## Table 1 baselines

| Item | Metric | Paper | Local | Delta | Equivalence | Cause | Improvement |
|---|---|---:|---:|---:|---|---|---|
| BIPIA GuardReasoner-VL | IR/FPR | - | - | - | not reproduced | 论文值为 IR 62.5% / FPR 6.2%，但本地没有该 baseline 的官方模型和 harness 输出。 | 下载对应官方代码，固定同一数据切分，输出 IR/FPR 后再填入差值。 |
| BIPIA WebAgentGuard | IR/FPR | - | - | - | not reproduced | 论文值为 IR 84.7% / FPR 28.5%，但本地没有该 baseline 的官方模型和 harness 输出。 | 下载对应官方代码，固定同一数据切分，输出 IR/FPR 后再填入差值。 |
| BIPIA BookAgent | IR/FPR | - | - | - | not reproduced | 论文值为 IR 86.3% / FPR 14.8%，但本地没有该 baseline 的官方模型和 harness 输出。 | 下载对应官方代码，固定同一数据切分，输出 IR/FPR 后再填入差值。 |
| InjecAgent GuardReasoner-VL | IR/FPR | - | - | - | not reproduced | 论文值为 IR 38.4% / FPR 5.8%，但本地没有该 baseline 的官方模型和 harness 输出。 | 下载对应官方代码，固定同一数据切分，输出 IR/FPR 后再填入差值。 |
| InjecAgent WebAgentGuard | IR/FPR | - | - | - | not reproduced | 论文值为 IR 91.2% / FPR 36.4%，但本地没有该 baseline 的官方模型和 harness 输出。 | 下载对应官方代码，固定同一数据切分，输出 IR/FPR 后再填入差值。 |
| InjecAgent BookAgent | IR/FPR | - | - | - | not reproduced | 论文值为 IR 85.5% / FPR 17.2%，但本地没有该 baseline 的官方模型和 harness 输出。 | 下载对应官方代码，固定同一数据切分，输出 IR/FPR 后再填入差值。 |

## Table 2 frontier comparison

| Item | Metric | Paper | Local | Delta | Equivalence | Cause | Improvement |
|---|---|---:|---:|---:|---|---|---|
| InjecAgent WAMI (ours, full model) | IR | 90.3% | 96.1% | +5.8 pp | direct local WAMI | 本地 WAMI 是轻量 NumPy/结构化计划实现，因此延迟远低于论文。 | 用完整论文运行栈测端到端 latency，并固定同样数据切分。 |
| InjecAgent WAMI (ours, full model) | FPR | 1.2% | 0.0% | -1.2 pp | direct local WAMI | 本地 WAMI 是轻量 NumPy/结构化计划实现，因此延迟远低于论文。 | 用完整论文运行栈测端到端 latency，并固定同样数据切分。 |
| InjecAgent WAMI (ours, full model) | Latency | 85.0 ms | 1.2 ms | -83.8 ms | direct local WAMI | 本地 WAMI 是轻量 NumPy/结构化计划实现，因此延迟远低于论文。 | 用完整论文运行栈测端到端 latency，并固定同样数据切分。 |
| BIPIA WAMI (ours, full model) | IR | 88.9% | 100.0% | +11.1 pp | direct local WAMI | 本地 WAMI 是轻量 NumPy/结构化计划实现，因此延迟远低于论文。 | 用完整论文运行栈测端到端 latency，并固定同样数据切分。 |
| BIPIA WAMI (ours, full model) | FPR | 1.5% | 0.6% | -0.9 pp | direct local WAMI | 本地 WAMI 是轻量 NumPy/结构化计划实现，因此延迟远低于论文。 | 用完整论文运行栈测端到端 latency，并固定同样数据切分。 |
| BIPIA WAMI (ours, full model) | Latency | 90.0 ms | 1.5 ms | -88.5 ms | direct local WAMI | 本地 WAMI 是轻量 NumPy/结构化计划实现，因此延迟远低于论文。 | 用完整论文运行栈测端到端 latency，并固定同样数据切分。 |
| InjecAgent Erase-and-Check official (qwen-max) | IR | 66.2% | 96.0% | +29.8 pp | approximate baseline | 本地 baseline 使用 Qwen API 或 SmoothLLM-style judge，样本量也小于论文 full benchmark。 | 跑完整 raw benchmark，统一模型、prompt、随机种子和样本量。 |
| InjecAgent Erase-and-Check official (qwen-max) | FPR | 10.5% | 0.0% | -10.5 pp | approximate baseline | 本地 baseline 使用 Qwen API 或 SmoothLLM-style judge，样本量也小于论文 full benchmark。 | 跑完整 raw benchmark，统一模型、prompt、随机种子和样本量。 |
| InjecAgent Erase-and-Check official (qwen-max) | Latency | 3100.0 ms | 2348.7 ms | -751.3 ms | approximate baseline | 本地 baseline 使用 Qwen API 或 SmoothLLM-style judge，样本量也小于论文 full benchmark。 | 跑完整 raw benchmark，统一模型、prompt、随机种子和样本量。 |
| BIPIA Erase-and-Check official (qwen-max) | IR | 63.5% | 64.0% | +0.5 pp | approximate baseline | 本地 baseline 使用 Qwen API 或 SmoothLLM-style judge，样本量也小于论文 full benchmark。 | 跑完整 raw benchmark，统一模型、prompt、随机种子和样本量。 |
| BIPIA Erase-and-Check official (qwen-max) | FPR | 11.0% | 0.0% | -11.0 pp | approximate baseline | 本地 baseline 使用 Qwen API 或 SmoothLLM-style judge，样本量也小于论文 full benchmark。 | 跑完整 raw benchmark，统一模型、prompt、随机种子和样本量。 |
| BIPIA Erase-and-Check official (qwen-max) | Latency | 3200.0 ms | 2767.3 ms | -432.7 ms | approximate baseline | 本地 baseline 使用 Qwen API 或 SmoothLLM-style judge，样本量也小于论文 full benchmark。 | 跑完整 raw benchmark，统一模型、prompt、随机种子和样本量。 |
| InjecAgent SmoothLLM-style perturbation + qwen-max judge | IR | 72.1% | 100.0% | +27.9 pp | approximate baseline | 本地 baseline 使用 Qwen API 或 SmoothLLM-style judge，样本量也小于论文 full benchmark。 | 跑完整 raw benchmark，统一模型、prompt、随机种子和样本量。 |
| InjecAgent SmoothLLM-style perturbation + qwen-max judge | FPR | 7.9% | 41.2% | +33.3 pp | approximate baseline | 本地 baseline 使用 Qwen API 或 SmoothLLM-style judge，样本量也小于论文 full benchmark。 | 跑完整 raw benchmark，统一模型、prompt、随机种子和样本量。 |
| InjecAgent SmoothLLM-style perturbation + qwen-max judge | Latency | 2400.0 ms | 3364.6 ms | +964.6 ms | approximate baseline | 本地 baseline 使用 Qwen API 或 SmoothLLM-style judge，样本量也小于论文 full benchmark。 | 跑完整 raw benchmark，统一模型、prompt、随机种子和样本量。 |
| BIPIA SmoothLLM-style perturbation + qwen-max judge | IR | 69.4% | 96.0% | +26.6 pp | approximate baseline | 本地 baseline 使用 Qwen API 或 SmoothLLM-style judge，样本量也小于论文 full benchmark。 | 跑完整 raw benchmark，统一模型、prompt、随机种子和样本量。 |
| BIPIA SmoothLLM-style perturbation + qwen-max judge | FPR | 8.2% | 48.0% | +39.8 pp | approximate baseline | 本地 baseline 使用 Qwen API 或 SmoothLLM-style judge，样本量也小于论文 full benchmark。 | 跑完整 raw benchmark，统一模型、prompt、随机种子和样本量。 |
| BIPIA SmoothLLM-style perturbation + qwen-max judge | Latency | 2450.0 ms | 5054.6 ms | +2604.6 ms | approximate baseline | 本地 baseline 使用 Qwen API 或 SmoothLLM-style judge，样本量也小于论文 full benchmark。 | 跑完整 raw benchmark，统一模型、prompt、随机种子和样本量。 |

## Table 2 missing baselines

| Item | Metric | Paper | Local | Delta | Equivalence | Cause | Improvement |
|---|---|---:|---:|---:|---|---|---|
| InjecAgent ToolEmu-Sandbox | IR/FPR/Latency | - | - | - | not reproduced | 论文值为 IR 75.6% / FPR 13.6% / latency about 5800 ms；本地未得到可比输出。 | 下载模型或完成 ToolEmu harness，按 raw benchmark 跑完整结果。 |
| InjecAgent Llama-Guard 3 8B | IR/FPR/Latency | - | - | - | not reproduced | 论文值为 IR 79.8% / FPR 6.1% / latency about 1150 ms；本地未得到可比输出。 | 下载模型或完成 ToolEmu harness，按 raw benchmark 跑完整结果。 |
| BIPIA ToolEmu-Sandbox | IR/FPR/Latency | - | - | - | not reproduced | 论文值为 IR 73.2% / FPR 14.0% / latency about 5900 ms；本地未得到可比输出。 | 下载模型或完成 ToolEmu harness，按 raw benchmark 跑完整结果。 |
| BIPIA Llama-Guard 3 8B | IR/FPR/Latency | - | - | - | not reproduced | 论文值为 IR 77.4% / FPR 6.5% / latency about 1180 ms；本地未得到可比输出。 | 下载模型或完成 ToolEmu harness，按 raw benchmark 跑完整结果。 |

## Table 3 cross-backbone

| Item | Metric | Paper | Local | Delta | Equivalence | Cause | Improvement |
|---|---|---:|---:|---:|---|---|---|
| GPT-4V WAMI IR | IR | 87.8% | - | - | not reproduced | 本地没有严格替换 GPT-4V/Llama-3-8B/Qwen-VL-Max 多模态 backbone；Qwen-VL-Max 这里只能用 InjecAgent WAMI 本地行作近似参考。 | 接入三个 backbone 的同一 agent harness，记录各自 action trajectory 后复跑 WAMI。 |
| GPT-4V WAMI FPR | FPR | 1.0% | - | - | not reproduced | 同上，当前不是论文原始跨 backbone 实验。 | 补齐 GPT-4V、Llama-3-8B、Qwen-VL-Max 的统一 agent 输出。 |
| Llama-3-8B WAMI IR | IR | 88.9% | - | - | not reproduced | 本地没有严格替换 GPT-4V/Llama-3-8B/Qwen-VL-Max 多模态 backbone；Qwen-VL-Max 这里只能用 InjecAgent WAMI 本地行作近似参考。 | 接入三个 backbone 的同一 agent harness，记录各自 action trajectory 后复跑 WAMI。 |
| Llama-3-8B WAMI FPR | FPR | 1.5% | - | - | not reproduced | 同上，当前不是论文原始跨 backbone 实验。 | 补齐 GPT-4V、Llama-3-8B、Qwen-VL-Max 的统一 agent 输出。 |
| Qwen-VL-Max WAMI IR | IR | 90.3% | 96.1% | +5.8 pp | not strictly comparable | 本地没有严格替换 GPT-4V/Llama-3-8B/Qwen-VL-Max 多模态 backbone；Qwen-VL-Max 这里只能用 InjecAgent WAMI 本地行作近似参考。 | 接入三个 backbone 的同一 agent harness，记录各自 action trajectory 后复跑 WAMI。 |
| Qwen-VL-Max WAMI FPR | FPR | 1.2% | 0.0% | -1.2 pp | not strictly comparable | 同上，当前不是论文原始跨 backbone 实验。 | 补齐 GPT-4V、Llama-3-8B、Qwen-VL-Max 的统一 agent 输出。 |

## Figure 4 ROC AUC

| Item | Metric | Paper | Local | Delta | Equivalence | Cause | Improvement |
|---|---|---:|---:|---:|---|---|---|
| InjecAgent WAMI AUC | AUC | 0.992 | 0.667 | -0.325 | same metric, different dataset/score extraction | 论文 Figure 4 给的是整体 WAMI ROC AUC；本地是各数据集 MINE score AUC。InjecAgent/AgentDojo 的纯 MINE 分离弱于论文。 | 用最终 gateway decision score 构造 ROC，而不是只用 MINE step score；同时增加 shadow training epoch 和 hard negatives。 |
| BIPIA WAMI AUC | AUC | 0.992 | 0.956 | -0.036 | same metric, different dataset/score extraction | 论文 Figure 4 给的是整体 WAMI ROC AUC；本地是各数据集 MINE score AUC。InjecAgent/AgentDojo 的纯 MINE 分离弱于论文。 | 用最终 gateway decision score 构造 ROC，而不是只用 MINE step score；同时增加 shadow training epoch 和 hard negatives。 |
| AgentDojo WAMI AUC | AUC | 0.992 | 0.754 | -0.238 | same metric, different dataset/score extraction | 论文 Figure 4 给的是整体 WAMI ROC AUC；本地是各数据集 MINE score AUC。InjecAgent/AgentDojo 的纯 MINE 分离弱于论文。 | 用最终 gateway decision score 构造 ROC，而不是只用 MINE step score；同时增加 shadow training epoch 和 hard negatives。 |

## Table 4 capability

| Item | Metric | Paper | Local | Delta | Equivalence | Cause | Improvement |
|---|---|---:|---:|---:|---|---|---|
| WAMI proxy | ToolBench SR | 68.0% | 68.1% | +0.1 pp | proxy, not official | 本地用 BIPIA/AgentDojo 良性放行率估计能力保持，不是 ToolBench/AgentBench 官方 SR。 | 完成 ToolBench/AgentBench 官方 harness，计算 No Defense SR 与 WAMI SR。 |
| WAMI proxy | AgentBench SR | 70.6% | 69.5% | -1.1 pp | proxy, not official | 本地用 BIPIA/AgentDojo 良性放行率估计能力保持，不是 ToolBench/AgentBench 官方 SR。 | 完成 ToolBench/AgentBench 官方 harness，计算 No Defense SR 与 WAMI SR。 |
| WAMI proxy | ToolBench Retention | 99.3% | 99.4% | +0.1 pp | proxy, not official | 本地用 BIPIA/AgentDojo 良性放行率估计能力保持，不是 ToolBench/AgentBench 官方 SR。 | 完成 ToolBench/AgentBench 官方 harness，计算 No Defense SR 与 WAMI SR。 |
| WAMI proxy | AgentBench Retention | 99.2% | 97.7% | -1.5 pp | proxy, not official | 本地用 BIPIA/AgentDojo 良性放行率估计能力保持，不是 ToolBench/AgentBench 官方 SR。 | 完成 ToolBench/AgentBench 官方 harness，计算 No Defense SR 与 WAMI SR。 |
| ToolBench data_example WAMI | ToolBench SR | 68.0% | 60.0% | -8.0 pp | real ToolBench format, tiny sample | 只跑了 ToolBench data_example 的 15 条轨迹；No Defense 示例 SR 为 60.0%，和论文 full ToolBench 68.5% 不同。 | 下载 reproduction_data/full data，跑六个 test subsets 的 ToolEval pass rate。 |

## Table 5 ablation

| Item | Metric | Paper | Local | Delta | Equivalence | Cause | Improvement |
|---|---|---:|---:|---:|---|---|---|
| WAMI (Full Model) | IR | 90.3% | 96.1% | +5.8 pp | same ablation name, local implementation | 本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。 | 统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。 |
| WAMI (Full Model) | FPR | 1.2% | 0.0% | -1.2 pp | same ablation name, local implementation | 本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。 | 统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。 |
| WAMI (Full Model) | Latency | 85.0 ms | 1.2 ms | -83.8 ms | same ablation name, local implementation | 本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。 | 统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。 |
| w/o TDG Graph Construction | IR | 78.3% | 55.5% | -22.8 pp | same ablation name, local implementation | 本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。 | 统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。 |
| w/o TDG Graph Construction | FPR | 4.5% | 47.1% | +42.6 pp | same ablation name, local implementation | 本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。 | 统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。 |
| w/o TDG Graph Construction | Latency | 92.0 ms | 1.1 ms | -90.9 ms | same ablation name, local implementation | 本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。 | 统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。 |
| w/o World Model Rollout | IR | 64.2% | 65.8% | +1.6 pp | same ablation name, local implementation | 本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。 | 统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。 |
| w/o World Model Rollout | FPR | 8.1% | 0.0% | -8.1 pp | same ablation name, local implementation | 本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。 | 统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。 |
| w/o World Model Rollout | Latency | 35.0 ms | 0.9 ms | -34.1 ms | same ablation name, local implementation | 本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。 | 统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。 |
| w/o MINE Gateway (Cosine Similarity) | IR | 81.5% | 93.2% | +11.7 pp | same ablation name, local implementation | 本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。 | 统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。 |
| w/o MINE Gateway (Cosine Similarity) | FPR | 5.8% | 0.0% | -5.8 pp | same ablation name, local implementation | 本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。 | 统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。 |
| w/o MINE Gateway (Cosine Similarity) | Latency | 82.0 ms | 1.2 ms | -80.8 ms | same ablation name, local implementation | 本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。 | 统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。 |
| w/o Shadow Adversarial Training | IR | 75.7% | 93.0% | +17.3 pp | same ablation name, local implementation | 本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。 | 统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。 |
| w/o Shadow Adversarial Training | FPR | 12.4% | 0.0% | -12.4 pp | same ablation name, local implementation | 本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。 | 统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。 |
| w/o Shadow Adversarial Training | Latency | 85.0 ms | 1.2 ms | -83.8 ms | same ablation name, local implementation | 本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。 | 统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。 |

## Figure 6 latency

| Item | Metric | Paper | Local | Delta | Equivalence | Cause | Improvement |
|---|---|---:|---:|---:|---|---|---|
| TDG construction | Latency | 15.0 ms | 0.0 ms | -15.0 ms | same component idea, different runtime scale | 本地是轻量 NumPy/文本 TDG 实现，没有论文完整多模态 agent 和部署开销。 | 用同一硬件、完整 agent loop、显式计时 TDG/world/MINE，并报告 mean/p95。 |
| World model rollout | Latency | 45.0 ms | 1.0 ms | -44.0 ms | same component idea, different runtime scale | 本地是轻量 NumPy/文本 TDG 实现，没有论文完整多模态 agent 和部署开销。 | 用同一硬件、完整 agent loop、显式计时 TDG/world/MINE，并报告 mean/p95。 |
| MINE gateway | Latency | 25.0 ms | 0.1 ms | -24.9 ms | same component idea, different runtime scale | 本地是轻量 NumPy/文本 TDG 实现，没有论文完整多模态 agent 和部署开销。 | 用同一硬件、完整 agent loop、显式计时 TDG/world/MINE，并报告 mean/p95。 |
| WAMI total | Latency | 85.0 ms | 1.2 ms | -83.8 ms | same component idea, different runtime scale | 本地是轻量 NumPy/文本 TDG 实现，没有论文完整多模态 agent 和部署开销。 | 用同一硬件、完整 agent loop、显式计时 TDG/world/MINE，并报告 mean/p95。 |

## Figure 7 VRAM

| Item | Metric | Paper | Local | Delta | Equivalence | Cause | Improvement |
|---|---|---:|---:|---:|---|---|---|
| WAMI VRAM | VRAM | 0.45 GB | - | - | not measured | 本地没有做 GPU memory profiling。 | 用 nvidia-smi 或 torch.cuda.max_memory_allocated 分别测 batch=1 的 WAMI/baseline 显存。 |
| Llama-Guard 3 VRAM | VRAM | 16.00 GB | - | - | not measured | 本地没有做 GPU memory profiling。 | 用 nvidia-smi 或 torch.cuda.max_memory_allocated 分别测 batch=1 的 WAMI/baseline 显存。 |
| SmoothVLM/Erase KV cache | VRAM | 3.50 GB | - | - | not measured | 本地没有做 GPU memory profiling。 | 用 nvidia-smi 或 torch.cuda.max_memory_allocated 分别测 batch=1 的 WAMI/baseline 显存。 |
| ToolEmu-Sandbox VRAM lower bound | VRAM | 16.00 GB | - | - | not measured | 本地没有做 GPU memory profiling。 | 用 nvidia-smi 或 torch.cuda.max_memory_allocated 分别测 batch=1 的 WAMI/baseline 显存。 |

## Figure 8 MI convergence

| Item | Metric | Paper | Local | Delta | Equivalence | Cause | Improvement |
|---|---|---:|---:|---:|---|---|---|
| InjecAgent MI gap epoch 8 | MI gap | - | 1.2694 | - | local supporting evidence | 论文图展示 epoch 15 左右稳定分离；本地 InjecAgent 子集到 epoch 8 已从 0.1576 增至 1.2694。 | 跑满 30 epoch 并保存 benign/attack 两条 MI 曲线，而不只报告 gap。 |
