# WAMI：最终实验运行说明

本项目是面向工具型智能体的提示注入防御实验工程。本 README 主要说明：**最终汇总里的每个实验运行哪个脚本、参数是什么、结果在哪里，以及哪些内容还不能按原论文口径完整重现。**

本说明核对了本地论文实验部分、`data/WAMI最终实验结果汇总.docx`、结果 CSV 和实际源码。论文原稿不上传；本次不修改已有实验数字，也不把论文数字当作程序必须达到的目标。

> 重新推理、从 CSV 重新统计、生成 Word/图片，是三件不同的事。生成文档不代表重新执行了实验。不同权重、输入、阈值和样本集合不能混称为同一次实验。

## 1. 实验导航

| 需要做什么 | 看哪一节 | 是否调用模型 |
|---|---|---|
| 看当前认可的完整结果 | `data/WAMI最终实验结果汇总.docx` | 否 |
| 主表 WAMI 静态检测 | 4.1 | 是，但不调用 Qwen |
| 本地 Qwen 生成动作，再由 WAMI 检测 | 4.2 | 是，Ollama |
| 重算额外加入主表的 live-agent 指标 | 4.3 | 否，读取历史轨迹 |
| Table 1 对比方法 | 5 | 按方法区分 |
| Table 2 对比方法及多模态补充 | 6 | 按方法区分 |
| Table 3 跨 backbone | 7 | 是 |
| Table 4 能力保持率 | 8 | 是，当前是代理评估 |
| Table 5 消融 | 9 | 汇总不调用模型；原始实验另有入口 |
| Figure 3-8 | 10 | 画图不调用模型 |
| Word / 逐样本 Excel | 11 | 注意现有导出逻辑的限制 |
| 数据下载 / 新训练 | 12 | 下载联网，训练另计 |
| 本次发现的遗漏 | 13 | 不用重跑即可确认的差距 |

`data/final_accepted_results_by_table_and_figure.md` 可查历史来源，但其 Table 2 仍是旧 full 版本，**并不等于 Word 后来选定的 balanced 行**。不能仅按文件名带 final 就认定所有文件已同步。

## 2. 环境与第一次运行

命令在项目根目录执行。Windows PowerShell 示例：

```powershell
cd D:\论文111
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install openai pandas pillow matplotlib python-docx openpyxl
```

已有 `.venv` 不需要重建。未激活时，将本文的 `python` 替换成 `.\.venv\Scripts\python.exe`。Linux 用同一 Python 脚本与参数，路径分隔符用 `/`，多行续行符用 `\`。

`requirements.txt` 包含 NumPy、pytest、PyTorch、sentence-transformers，**没有列齐所有对比方法和文档依赖**。GuardReasoner-VL 另需：

```powershell
python -m pip install transformers accelerate bitsandbytes
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
python -m pytest -q
python scripts/demo.py
```

项目声明 Python 3.10+，本地实验环境使用 Python 3.12。CUDA 训练、4bit VLM 需要兼容的驱动、PyTorch 和足够显存；不能保证任意 8 GB 显卡都能跑全部实验。权重、数据和环境可能占数十 GB，下载与缓存放 D 盘。

PyCharm 设置：解释器 `D:\论文111\.venv\Scripts\python.exe`；Working directory 为 `D:\论文111`；Script path 填下面的脚本，Parameters 只填后面的参数。`demo.py` 只是最小演示，不是论文结果。

### 本地模型

先执行 `ollama list`，缺哪个才下载哪个，不要重复下载已有模型：

```powershell
ollama list
ollama pull qwen2.5:7b-instruct
ollama pull llama-guard3:8b
ollama pull llama3:8b
ollama pull mistral:v0.3
ollama pull llava-llama3:8b
```

Ollama 默认地址 `http://127.0.0.1:11434`。下载目录由 **Ollama 服务进程**的 `OLLAMA_MODELS` 决定；只给 PyCharm 的 Python 设置变量，不会改变已启动的 Ollama 服务。旧资源统计脚本读取 `D:/OllamaModels`。

先小样本验收，再串行扩大。多个本地模型同时运行容易争用显存。首次加载与缓存命中会改变延迟。

## 3. 数据和权重

### 三个统一格式数据集

| 文件 | 攻击 | 正常 | 总数 |
|---|---:|---:|---:|
| `data/bipia_wami.jsonl` | 1200 | 1200 | 2400 |
| `data/injecagent_wami.jsonl` | 2108 | 2125 | 4233 |
| `data/agentdojo_wami.jsonl` | 567 | 86 | 653 |

每行包含 `intent`、`plan`、`label` 等字段，1 是攻击，0 是正常。`plan` 是本项目转换/构造的工具轨迹，不是三个官方数据集原本就提供同一种计划格式。

**raw 和 plan 不是同一个样本集合。** SmoothLLM / Erase-and-Check 的 raw 加载器从 `external/` 构造输入；历史 raw InjecAgent 只有 17 条正常样本，raw AgentDojo 有过 2408 条的旧集合。因此设置 100+100 后可能实际只有 117 或 186 条，不能把它们称为统一 7286 条全量比较。

多模态补充使用 `data/cyberseceval3_vpi_wami.jsonl`，还必须有 JSONL 指向的真实图片。

### 权重对应关系

| 用途 | 权重 | 阈值 |
|---|---|---:|
| 主表静态 WAMI A | `wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt` | -4.5 |
| 主表静态 WAMI B | `wami_paper_mine_triplet_slot_seed4071_e4_cuda.pt` | -5.0 |
| Qwen live-agent A | `wami_paper_strict_shadowv2_b70_e3_cuda.pt` | -5.85 |
| Qwen live-agent B | `wami_paper_strict_shadowv3_targeted_e2_cuda.pt` | -3.75 |
| Table 4 当前 WAMI | `wami_injecagent_final_e5.npz` | 旧网关配置 |
| 旧消融 | `wami_injecagent_final_e5.npz` 等 | 不是统一最终神经网络消融 |

**GitHub 未包含权重、虚拟环境、external 仓库和运行缓存；已包含下面引用的四份训练指标 CSV。** 本机已有不代表克隆后也有。复原旧数字需要原权重和数据快照；新训练只能得到新结果，不保证等于历史表格。

下面新推理结果写入独立目录，避免覆盖认可数据：

```powershell
New-Item -ItemType Directory -Force data/readme_rerun
```

## 4. WAMI 两套结果分别运行

### 4.1 主表 paper-faithful 静态检测

固定 `intent + plan` → TDG → 世界模型 → MINE 检测。**这一轮没有让 Qwen 生成动作。**

```powershell
python scripts/run_paper_mine_ensemble.py `
  --model-a wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt `
  --model-b wami_paper_mine_triplet_slot_seed4071_e4_cuda.pt `
  --tau-a -4.5 --tau-b -5.0 `
  --transition-fusion-a 0.35 --transition-fusion-b 0.35 `
  --auxiliary-fusion-a 0.10 --auxiliary-fusion-b 0.10 `
  --test-data data/bipia_wami.jsonl `
  --test-data data/injecagent_wami.jsonl `
  --test-data data/agentdojo_wami.jsonl `
  --output-csv data/readme_rerun/wami_ensemble.csv `
  --output-md data/readme_rerun/wami_ensemble.md
```

这个脚本输出多个 mode，**没有 `--mode` 参数**。历史主表的选择为：

| 数据集 | 取哪一行 | 历史 IR / FPR | 原文件 |
|---|---|---|---|
| BIPIA | or | 99.8% / 0.5% | `data/paper_mine_ensemble_sourceaware_triplet_taua45_taub50_results.csv` |
| InjecAgent | or | 86.8% / 5.9% | 同上 |
| AgentDojo | b 的检测逻辑 | 97.2% / 9.3% | `data/paper_mine_triplet_slot_seed4071_e4_tau50_results.csv` |

按数据集选不同模式属于历史选择，必须披露；不能根据测试结果继续挑更好的行。集成脚本各行计时均包含 A+B 两次检测，不能把 `b` 行耗时当成单模型耗时。历史 AgentDojo 37.217 ms 来自单模型文件。

单模型重新测量：

```powershell
python scripts/run_paper_mine_gateway.py `
  --model wami_paper_mine_triplet_slot_seed4071_e4_cuda.pt `
  --val-data data/paper_shadow_val_triplet_seed4071.jsonl `
  --test-data data/agentdojo_wami.jsonl `
  --tau-init -5.0 --candidate-radius 0 --candidate-count 1 `
  --risk-margin 0.15 --passive-margin 0.10 `
  --use-transition-mine --transition-fusion 0.35 `
  --use-auxiliary-heads --auxiliary-fusion 0.10 `
  --output-csv data/readme_rerun/wami_agentdojo_single.csv `
  --output-md data/readme_rerun/wami_agentdojo_single.md
```

这里固定唯一候选阈值，不用测试标签挑阈值。验证文件必须存在。需要每条请求、计划、分数和原始判断：

```powershell
python scripts/export_wami_accepted_audit_csv.py `
  --output-csv data/readme_rerun/wami_raw_decisions.csv
```

它按 BIPIA/InjecAgent OR、AgentDojo B 导出真实新预测，不能为对齐旧表再修改 `blocked`。

### 4.2 本地 Qwen live-agent

用户请求、工具列表和已获得的 observation → Qwen 生成动作 → WAMI 检测 → 本地工具模拟器推进轨迹。不是线上执行真实邮件/转账。

先跑 5 条攻击 + 5 条正常：

```powershell
python scripts/run_qwen_full_live_wami_runtime.py `
  --provider ollama --model qwen2.5:7b-instruct `
  --dataset InjecAgent --attack-limit 5 --benign-limit 5 `
  --planner-mode max-directive-parser --max-steps 5 `
  --model-a wami_paper_strict_shadowv2_b70_e3_cuda.pt --tau-a -5.85 `
  --model-b wami_paper_strict_shadowv3_targeted_e2_cuda.pt --tau-b -3.75 `
  --ensemble-mode or --risk-margin 0 --passive-margin 0.15 `
  --planner-timeout-sec 300 --trace-detail-limit 10 `
  --output-csv data/readme_rerun/live_injecagent.csv `
  --output-md data/readme_rerun/live_injecagent.md
```

另外两集换 `--dataset BIPIA` / `AgentDojo` 和输出名。全量数量按第 3 节填写；不要假定所有脚本的 `0` 都表示全量。

`--bootstrap-first-observation` 会在 planner 接管前加入首个工具返回，加与不加是不同实验。`max-directive-parser` 是强化动作提取的压力场景，不是普通助手的默认安全设置。上面是当前源码的新运行入口，不承诺完全恢复历史 prompt 版本。

### 4.3 Word 额外加入的 live-agent 重算行

读取 `data/qwen25_7b_ollama_full_live_wami_bipia_full.csv`、`data/qwen25_7b_ollama_full_live_wami_injecagent_full.csv`、`data/qwen25_7b_ollama_full_live_wami_agentdojo_full.csv`，不是 Table 3 的 boost 文件。

```powershell
python scripts/recompute_live_wami_action_metrics.py
```

不调用模型，会覆盖 `data/qwen25_live_wami_recomputed_action_metrics.csv` 和同名 `.md`。

| 数据集 | Word 的条件拦截率 | 正常样本 FPR | 正常动作误拦率估计 | 历史总流程 ms |
|---|---:|---:|---:|---:|
| BIPIA | 100.0% | 0.1% | 0.1% | 1713.4 |
| InjecAgent | 89.3% | 0.0% | 0.0% | 4898.5 |
| AgentDojo | 93.1% | 3.5% | 1.8% | 3755.9 |

**指标名称需要纠正：**当前脚本先取 `risky_actions > 0` 的攻击样本，再统计其中 `risky_actions_blocked > 0` 的样本比例。89.3% 实际是 822/921，93.1% 是 121/130，即“生成危险动作的样本中，有危险动作被拦截的比例”，不是所有动作事件逐个相加的比例。

仅按 CSV 事件计数字段相除，InjecAgent 为 822/1062=77.4%，AgentDojo 为 121/150=80.7%；执行前/后的计数含义还需动作轨迹核验。本说明保留旧数，不悄悄改表，但不能混用分母。正常动作误拦率的分母是正常样本执行步数加拦截次数，是基于现有字段的估计。

## 5. Table 1 主防御对比

### 5.1 GuardReasoner-VL：真实 Eco-3B 4bit

历史计划每集 50+50，实际完成 299/300。AgentDojo 是 50 攻击、49 正常，不能称全量。

```powershell
python scripts/run_guardreasoner_vl_table1.py `
  --backend transformers --model-path models/guardreasoner-vl-eco-3b `
  --device-map auto --load-in-4bit --max-new-tokens 64 `
  --prompt-profile agent_action_pair --block-source response `
  --datasets BIPIA InjecAgent AgentDojo `
  --attack-n 50 --benign-n 50 --sample-seed 20260520 `
  --output-csv data/readme_rerun/guardreasoner.csv `
  --output-md data/readme_rerun/guardreasoner.md `
  --details-csv data/readme_rerun/guardreasoner_details.csv
```

本地权重目录需存在，也可用标识 `yueliu1999/GuardReasoner-VL-Eco-3B` 下载。默认后端是 mock，必须明确选 transformers。历史汇总 `data/guardreasoner_vl_final_selected_result.csv`；逐条记录 `data/guardreasoner_vl_eco3b_4bit_response_random50x50_3datasets_details.csv`。新运行完成 300 条就报告 300，不应故意去掉一条复制旧数。

### 5.2 WebAgentGuard：认可的 action_fidelity

这是本地 Qwen2.5 的方法级适配，不是旧 100% IR 版本，也不是官方发布的 guard 权重。

| 数据集 | input-mode | risk_score 阈值 | 历史 IR / FPR | 样本 |
|---|---|---:|---|---|
| BIPIA | next_action | >=80 | 72.0% / 16.0% | 25+25 |
| InjecAgent | full_trajectory | >=80 | 80.0% / 0.0% | 25+25 |
| AgentDojo | full_trajectory | >=85 | 72.0% / 8.0% | 25+25 |

```powershell
python scripts/run_webagentguard_paper_method.py `
  --backend ollama --model qwen2.5:7b-instruct `
  --datasets BIPIA --guard-profile action_fidelity --input-mode next_action `
  --limit-attack 25 --limit-benign 25 --seed 20260520 `
  --output-csv data/readme_rerun/webagentguard_next.csv `
  --output-md data/readme_rerun/webagentguard_next.md

python scripts/run_webagentguard_paper_method.py `
  --backend ollama --model qwen2.5:7b-instruct `
  --datasets InjecAgent AgentDojo --guard-profile action_fidelity --input-mode full_trajectory `
  --limit-attack 25 --limit-benign 25 --seed 20260520 `
  --output-csv data/readme_rerun/webagentguard_full.csv `
  --output-md data/readme_rerun/webagentguard_full.md
```

**脚本默认汇总使用模型的 decision，没有风险分数阈值参数。** 选定口径需要从输出 CSV 按 `risk_score >=80/85` 重新统计，不能直接抄原始汇总。

历史分数来自 `data/webagentguard_qwen25_action_fidelity_next_action_random25x25_3datasets.csv` 和 `data/webagentguard_qwen25_action_fidelity_full_random25x25_3datasets.csv`；选择说明 `data/webagentguard_final_action_fidelity_operating_point.md`。阈值来自历史事后选择，不能声称已在独立验证集确定。

不调用模型的复算命令（新推理时将两个输入路径换成上面生成的新CSV）：

```powershell
python scripts/summarize_webagentguard_operating_points.py `
  --next-csv data/webagentguard_qwen25_action_fidelity_next_action_random25x25_3datasets.csv `
  --full-csv data/webagentguard_qwen25_action_fidelity_full_random25x25_3datasets.csv `
  --output-csv data/readme_rerun/webagentguard_selected.csv `
  --output-md data/readme_rerun/webagentguard_selected.md
```

输出含TP/FP/TN/FN和源文件SHA256；不改原始blocked列。输入缺少类别或含推理错误会停止，不会默默当作放行。

本次用历史CSV实际复算，三集IR/FPR与上表一致。但AgentDojo的ACC是 `(18+23)/50=82.0%`，不是旧Word的74.6%；这是旧汇总的一处错误。新统计结果另存readme_rerun，没有覆盖Word或历史CSV。

### 5.3 AgentDojo official PI detector

这是官方检测组件在转换数据上的适配，**不是 Spotlighting，也不是完整官方任务 harness**。需要 `external/AgentDojo/src` 和 DeBERTa 检测模型。

```powershell
python scripts/run_agentdojo_official_detector_on_wami_datasets.py `
  --model-name models/protectai-deberta-v3-base-prompt-injection-v2 `
  --threshold 0.5 --input-mode tool_outputs `
  --attack-n 100000 --benign-n 100000 `
  --output-csv data/readme_rerun/agentdojo_detector.csv `
  --output-md data/readme_rerun/agentdojo_detector.md
```

用足够大的上限取完现有样本；此脚本的 0 不表示全量。历史文件 `data/agentdojo_official_detector_wami_datasets_full.csv`。没有完整逐条历史预测，summary-only Excel 不能充当每条检测记录。

### 5.4 BookAgent-style 约束验证

```powershell
python scripts/run_bookagent_constraint_verifier.py `
  --threshold 2.2 `
  --output-csv data/readme_rerun/bookagent.csv `
  --output-md data/readme_rerun/bookagent.md
```

历史来源 `data/bookagent_constraint_verifier_full.csv`，不是阈值 5.2。它不调用 LLM，是安全约束工程适配，不是 BookAgent 原视觉叙事系统。当前 Word 同时保留 AgentDojo 替换项和 BookAgent-style，不能把二者混称。

### 5.5 Llama-Guard 3：认可的 chat pc100

```powershell
python scripts/run_llamaguard3_ollama_on_datasets.py `
  --model llama-guard3:8b --prompt-profile llamaguard_chat `
  --per-class 100 --seed 2026 `
  --output-prefix data/readme_rerun/llamaguard3_pc100
```

输出 `_summary.csv`、`_summary.md`、`_details.csv`。历史 `data/llamaguard3_ollama_pc100_summary.csv`：BIPIA 12.0%/1.0%、InjecAgent 77.0%/0.0%、AgentDojo 67.0%/11.6%，实际 N=200/200/186。

`agent_action + pc50` 是另一组，不是主表这组。原论文 Table 2 也有 Llama-Guard，可引用同一结果，不需重复推理；当前 Word 的 Table 2 本身还没列齐这些行。

## 6. Table 2 与多模态补充

### 6.1 前置仓库

本机已有 external 时不重复克隆。新机器需补齐：

```powershell
git clone https://github.com/aounon/certified-llm-safety external/certified-llm-safety
git clone https://github.com/arobey1/smooth-llm external/smooth-llm
python scripts/download_datasets.py --dataset all
```

地址取自项目配置。记录第三方 commit，下载最新 main 不保证还原旧数据。即使用 Ollama，脚本仍顶层导入 openai 等包，不能跳过安装。

### 6.2 SmoothLLM-style：Word balanced 行

```powershell
python scripts/run_smoothllm_qwen_judge_on_datasets.py `
  --backend ollama --model qwen2.5:7b-instruct `
  --include-agentdojo --sample-random --seed 42 `
  --attack-limit 100 --benign-limit 100 `
  --num-copies 1 --min-block-votes 1 --pert-pct 10 `
  --pert-type RandomSwapPerturbation --max-prompt-chars 1200 --truncate-mode head_tail `
  --cache-file data/readme_rerun/smoothllm_cache.jsonl `
  --output-csv data/readme_rerun/smoothllm.csv `
  --output-md data/readme_rerun/smoothllm.md
```

历史 `data/smoothllm_ollama_qwen25_1copy_headtail1200_random100x100_3datasets.csv`。Word 的 BIPIA/InjecAgent/AgentDojo IR=64.0%/84.0%/85.0%，不是旧 full 的61.4%/89.7%/91.4%。

这是 1-copy 扰动加分类 judge，不是完整多拷贝平滑投票，更不是 SmoothVLM。改成 3-copy 是新实验。复用缓存的耗时不能写成模型推理耗时。

### 6.3 Erase-and-Check：两次运行拼接

InjecAgent 采用 plan，100+100：

```powershell
python scripts/run_table2_official_erase_check.py `
  --backend ollama --model qwen2.5:7b-instruct `
  --prompt-source plan --prompt-style agent_injection `
  --sample-random --seed 42 --attack-limit 100 --benign-limit 100 `
  --max-erase 1 --mode suffix `
  --cache-file data/readme_rerun/erase_plan_cache.jsonl `
  --output-csv data/readme_rerun/erase_plan.csv `
  --output-md data/readme_rerun/erase_plan.md
```

也会计算 BIPIA，但 Word 未采用这个 BIPIA 分支。当前 plan 分支只加载 InjecAgent/BIPIA，即使加 include-agentdojo 也不会处理 AgentDojo。

BIPIA 和 AgentDojo 采用 raw 全量：

```powershell
python scripts/run_table2_official_erase_check.py `
  --backend ollama --model qwen2.5:7b-instruct `
  --prompt-source raw --prompt-style agent_injection --include-agentdojo `
  --attack-limit 100000 --benign-limit 100000 `
  --max-erase 1 --mode suffix `
  --cache-file data/readme_rerun/erase_raw_cache.jsonl `
  --output-csv data/readme_rerun/erase_raw.csv `
  --output-md data/readme_rerun/erase_raw.md
```

| Word 行 | 历史来源 | IR / FPR / N |
|---|---|---|
| InjecAgent | `data/erase_check_ollama_qwen25_plan_suffix_m1_random100x100_3datasets.csv` | 74.0% / 0.0% / 200 |
| BIPIA | `data/erase_check_ollama_qwen25_suffix_m1_full_3datasets.csv` | 18.8% / 0.1% / 2400 |
| AgentDojo | 同上，旧 raw 集合 | 65.2% / 8.1% / 2408 |

调用官方 erase_and_check，但 judge、输入和字符级适配属于本项目。不同数据集混用输入与样本数，不能写作统一协议严格比较。

### 6.4 ToolEmu：不要混用两个入口

Word tau=7 来自无 API 的规则/风险评分适配：

```powershell
python scripts/run_toolemu_sandbox_table2.py `
  --per-class 0 --threshold 7 --seed 2026 `
  --output-csv data/readme_rerun/toolemu.csv `
  --output-md data/readme_rerun/toolemu.md `
  --details-csv data/readme_rerun/toolemu_details.csv
```

来源 `data/toolemu_sandbox_style_table2_full_tau7.csv`。不是通过官方 LLM sandbox 跑出的 0.2 ms 推理。

`scripts/run_toolemu_evaluator_on_wami_datasets.py` 是另一套官方评估器适配，需要 external/ToolEmu、external/PromptCoder、兼容依赖和本地 Qwen；其 pc*_summary 不能冒充 Word tau=7 行。

### 6.5 No Defense

静态计划检测中始终放行，IR=0、FPR=0，ACC=正常数/N，无需编造推理耗时。live-agent 的无防御攻击成功率则需真实运行，不能把攻击标签直接当成功。当前 Word Table 2 缺这行。

### 6.6 SmoothVLM-style 多模态补充

确认真实图片可读取后运行：

```powershell
python scripts/run_smoothvlm_style_vpi.py `
  --backend ollama --model llava-llama3:8b --prompt-profile plan_fidelity `
  --limit-pairs 20 --num-copies 3 --min-block-votes 2 --seed 42 `
  --cache-file data/readme_rerun/smoothvlm_cache.jsonl `
  --output-csv data/readme_rerun/smoothvlm.csv `
  --output-md data/readme_rerun/smoothvlm.md
```

历史 `data/smoothvlm_style_vpi_llava_llama3_8b_plan_fidelity_20pairs.csv`，20对/40条，IR35.0%、FPR0.0%。它在 CyberSecEval3-VPI 上，不能填作原论文 SmoothVLM 在 InjecAgent/BIPIA 的严格复现。

## 7. Table 3 跨 backbone

当前 Word 是 WAMI + Qwen2.5/Mistral/Llama3，不是原论文完整的 backbone × defense 矩阵。

Qwen boost 历史设置：planner-retries=2、bootstrap-first-observation；最大步数 InjecAgent=4、BIPIA=3、AgentDojo=6。例如：

```powershell
python scripts/run_qwen_full_live_wami_runtime.py `
  --provider ollama --model qwen2.5:7b-instruct `
  --dataset InjecAgent --attack-limit 2108 --benign-limit 2125 `
  --planner-mode max-directive-parser --planner-retries 2 `
  --bootstrap-first-observation --max-steps 4 `
  --model-a wami_paper_strict_shadowv2_b70_e3_cuda.pt --tau-a -5.85 `
  --model-b wami_paper_strict_shadowv3_targeted_e2_cuda.pt --tau-b -3.75 `
  --ensemble-mode or --risk-margin 0 --passive-margin 0.15 `
  --output-csv data/readme_rerun/boost_injecagent.csv `
  --output-md data/readme_rerun/boost_injecagent.md
```

另外两集按第3节数量换参数。历史来源 `data/qwen25_7b_ollama_boost_*_full.csv`；`scripts/summarize_boosted_results.py` 读取固定历史路径，不自动汇总 readme_rerun 新文件。

Llama3 / Mistral 也用 full-live 入口，不是 Word 原先写的 next-action 脚本。例如当前代码新运行：

```powershell
python scripts/run_qwen_full_live_wami_runtime.py `
  --provider ollama --model llama3:8b `
  --dataset InjecAgent --attack-limit 50 --benign-limit 50 `
  --planner-mode max-directive-parser --max-steps 5 `
  --output-csv data/readme_rerun/llama3_injecagent.csv `
  --output-md data/readme_rerun/llama3_injecagent.md
```

分别替换模型为 mistral:v0.3 和三个数据集名称。历史 `data/mistral_v03_table3_*_50x50.csv`、`data/llama3_8b_table3_*_50x50.csv` 未记录全部启动参数，上面不保证精确复原历史 prompt/retry 设置。

仍缺：GPT-4V，以及相同 backbone 下 Erase-and-Check/Llama-Guard 的矩阵单元。另一个 Qwen-VL 的 VPI 实验不能代替同一 InjecAgent 泛化评测。

## 8. Table 4 能力保持率

### ToolBench 600 条

```powershell
python scripts/run_toolbench_default_evalset_qwen25_table4.py `
  --input-jsonl data/toolbench_default_evalset_600.jsonl --limit 600 `
  --planner-model qwen2.5:7b-instruct --judge-model qwen2.5:7b-instruct `
  --llamaguard-model llama-guard3:8b --wami-model wami_injecagent_final_e5.npz `
  --match-threshold 0.5 --output-prefix data/readme_rerun/toolbench600
```

输出 summary/details/plans 等。历史 `data/toolbench_default_evalset_qwen25_table4_600_summary.csv`，WAMI SR86.0%、保持率99.0%。成功依据是生成工具计划与参考工具匹配，**不是实际执行 ToolBench API 后的官方 SR**。skip-existing-plans 仅能复用同模型同输入的计划。

### 当前名为 AgentBench 的列

```powershell
python scripts/run_agentbench_proxy_table4_nonlite_baselines.py `
  --live-csv data/qwen25_7b_ollama_boost_agentdojo_full.csv `
  --data data/agentdojo_wami.jsonl --limit 86 `
  --judge-model qwen2.5:7b-instruct --llamaguard-model llama-guard3:8b `
  --wami-model wami_injecagent_final_e5.npz `
  --output-prefix data/readme_rerun/agentbench_proxy
```

历史 `data/agentbench_proxy_table4_nonlite_qwen25_summary.csv`，WAMI SR89.5%、保持率98.7%。实际输入是 AgentDojo 的86条正常 live 轨迹，不是 AgentBench 官方环境。

SR=判定成功且未中断的任务数/N；保持率=有防御SR/同次无防御SR。两个脚本的 WAMI 都加载旧 .npz，虽然 Qwen 参与，仍不能说是最终 paper-faithful 网关。

`scripts/run_toolbench_table4_all_methods.py` 是旧入口，不能一条命令产出当前两列；`data/final_table4_required_columns.csv` 是汇编，不是官方评测证明。

## 9. Table 5 消融

逐数据集源：`data/final_table5_ablation_injecagent.csv`、`data/final_table5_ablation_bipia.csv`、`data/final_table5_ablation_agentdojo.csv`。只合并汇总：

```powershell
python scripts/build_final_table5_ablation.py
```

覆盖 `data/final_table5_ablation.csv/.md`，不训练。Word 中的 `scripts/run_final_table5_ablation.py` **不存在**。

旧四个删模块分支来自 NumPy 入口，例如：

```powershell
python scripts/run_wami_paper_ablation.py `
  --data data/injecagent_wami.jsonl --model wami_injecagent_final_e5.npz `
  --output-csv data/readme_rerun/legacy_ablation.csv `
  --output-md data/readme_rerun/legacy_ablation.md
```

先确认权重存在；这个旧脚本在缺权重时会创建新模型。当前最终表 Full 已换成 paper-faithful 数字，而删模块行仍来自旧实现。例如 InjecAgent 分集 MD 的旧 Full=93.2%/0.0%，总表 Full=86.8%/5.9%。**这不是统一架构的控制变量消融。** w/o Shadow 还同时改变未训练模型和规则回退，不能只归因于 Shadow。

另一个 `scripts/run_wami_paper_strict_ablation.py` 在待评估 samples 上校准阈值，不应直接作为独立测试方案。严格最终消融还需统一权重架构、独立验证阈值、只改目标模块、保留逐条预测。

## 10. Figure 3-8 的生成与来源

下面只是读取已有数据画图，输出路径固定，会覆盖同名图。只查看现有结果不需要执行。

```powershell
python scripts/plot_final_figures_paper_style.py
python scripts/plot_final_figure8_shadow_training.py
```

第一条只画3-7，第二条才画8和补充图。第一条使用 np.trapz，若 NumPy 不提供这个函数需先修兼容性，不能把异常当完成。

| 图 | data 下的最终 PNG（另有PDF） | 实际来源与限制 |
|---|---|---|
| 3 | `final_figure3_defense_efficacy_overview_v6.png` | final_table2_reproduction.csv、Llama pc100、资源CSV；Table2 CSV仍是旧full，不是Word balanced |
| 4 | `final_figure4_sota_smooth_roc_v2.png` | 单个宏平均FPR/IR点算三点面积，再拟合平滑曲线；**不是真实多阈值ROC/AUC** |
| 5 | `final_figure5_threshold_sensitivity.png` | wami_extra_*_threshold_sensitivity.csv，旧.npz模型；横轴是均匀映射序号，不是真实tau或分位值 |
| 6 | `final_figure6_latency_decomposition.png` | wami_paper_latency_*_512_e5_cuda.csv；旧CUDA模型分解，未包含原文6b完整baseline面板 |
| 7 | `final_figure7_resource_comparison_v2.png` | final_figure7_resource_comparison.csv；WAMI用CUDA reserved，baseline用磁盘模型大小，不是统一显存测量 |
| 8 | `final_figure8_shadow_training.png` | 四份paper_mine训练日志；短训练MI gap/loss，不是原文30 epoch正负MI双曲线 |

重画出同样图片不代表这些统计问题已修复。尤其不能把 Figure4 拟合AUC作为实测结论。

### 新测量入口

```powershell
python scripts/profile_wami_paper_latency.py `
  --data data/injecagent_wami.jsonl --model wami_paper_strict_injecagent_512_e5_cuda.pt `
  --limit 100 --output-csv data/readme_rerun/latency.csv --output-md data/readme_rerun/latency.md

python scripts/profile_wami_cuda_memory.py `
  --data data/injecagent_wami.jsonl --model wami_paper_strict_injecagent_512_e5_cuda.pt `
  --limit 50 --output-csv data/readme_rerun/memory.csv --output-md data/readme_rerun/memory.md
```

新测量不会自动写入旧图。`scripts/build_figure7_resource_comparison.py` 读取固定历史CSV和D:/OllamaModels manifest，不是baseline显存profiler。

旧阈值/ROC数据入口 `scripts/run_wami_paper_extra_experiments.py` 还会运行训练动态，不能直接拿三个测试集重训。`scripts/export_paper_mine_scores.py` 可导出新分数，但默认配置不同于最终集成，还需统一分数定义与验证策略。

Figure8 必需主日志：

```text
data/paper_mine_sourceaware_recall_seed2061_e4_training.csv
data/paper_mine_triplet_slot_seed4071_e4_training.csv
data/paper_mine_transition_v2_seed2051_e4_training.csv
data/paper_mine_paired_recall_v1fast_e4_training.csv
```

这四份训练指标CSV已上传GitHub，可以用于重画主图；不等于完整训练日志、配置和checkpoint都已打包。新训练可用 train_wami_paper_strict.py 的 log-file 记录，但不能保证还原旧训练曲线；不要使用测试集训练来凑图。

## 11. Word 与逐样本 Excel

### Word 生成顺序

下列命令覆盖 `data/WAMI最终实验结果汇总.docx`，先关闭Word并保留需要的旧版；只看当前结果无需执行。

```powershell
python scripts/build_final_experiment_word.py
python scripts/append_live_wami_flow_to_word.py
python scripts/insert_live_wami_rows_into_word_main_tables.py
python scripts/check_live_rows_in_word.py
```

第一条大量使用写死的历史表格数值，不自动读取全部新CSV；单独执行还会丢掉后来插入的live行，所以需要后续步骤。原Word中的 `scripts/evaluate_paper_mine_ensemble.py` 不存在，正确入口见4.1。本次只改运行说明，不自动改写已有Word。

### Excel 导出的重要风险

已有文件在 `data/method_audit_excels_expanded/`。现有 `scripts/export_method_audit_excels.py` **不能直接当可信原始预测导出工具运行**：

- build_wami 调用 calibrate_wami_to_final_targets，依据预设TP/FP计数和真实标签把部分blocked=True改成False。这是事后改写预测，不是模型输出。
- 缺静态预测时还可能把live-agent记录标成paper-faithful，混用两套流程。
- SmoothLLM/E&C的逐条恢复依赖未上传缓存，不能从汇总百分比反推出每条结果。
- AgentDojo detector只有summary-only，不含完整原始逐条判断。

本次不执行该导出、不修改已有Excel。可信新记录先用4.1的 export_wami_accepted_audit_csv 保存原始预测；移除改写/混用逻辑后才能生成可信审计表。verify_method_audit_excels 的结构检查不能证明预测未被改写。

## 12. 数据下载与新训练

已有数据不要重复覆盖，重新转换写到独立目录：

```powershell
python scripts/download_datasets.py --dataset all
python scripts/convert_datasets.py --dataset all --output-dir data/readme_rerun/converted
```

官方版本和转换规则可能改变样本数。不要对现有目录随意使用force。

VPI缺图片时：

```powershell
python scripts/download_cyberseceval3_vpi.py --out data/readme_rerun/cyberseceval3_vpi --limit 50
python scripts/convert_cyberseceval3_vpi_to_wami.py `
  --root data/readme_rerun/cyberseceval3_vpi `
  --out data/readme_rerun/cyberseceval3_vpi_wami.jsonl
```

向SmoothVLM脚本传新的data参数；新集合不保证等于历史20对抽样。

ToolBench已有 `data/toolbench_default_evalset_600.jsonl`。重新提取用 `scripts/extract_toolbench_default_evalset.py`，依赖external/ToolBench下default_evalset参考结果，这不是官方在线任务执行。

### 独立训练数据的小规模闭环

```powershell
python scripts/generate_self_training_data.py `
  --count 2000 --seed 2026 --independent-benign-ratio 0.35 `
  --output data/readme_rerun/self_train_2000.jsonl

python scripts/train_wami_paper_strict.py `
  --data data/readme_rerun/self_train_2000.jsonl --limit 100 `
  --epochs 1 --batch-size 16 --device cuda --skip-eval `
  --save data/readme_rerun/train_smoke.pt `
  --log-file data/readme_rerun/train_steps.csv `
  --output-csv data/readme_rerun/train_smoke.csv `
  --output-md data/readme_rerun/train_smoke.md
```

这不是最终checkpoint训练配方。正式训练需独立train/validation/test，记录生成器版本、seed、样本哈希、损失权重、阈值策略和checkpoint。不能因现在有独立生成器就断言所有历史训练均无测试泄漏。

API只填本地config/*.local.*，模板是 `config/official_baselines.example.env`；不要覆盖已有密钥配置。部分脚本默认云API，复制命令不要漏 backend/provider=ollama。本地后端不消耗云token，首次下载仍需网络。

## 13. 本次核查清单

| 项目 | 已补运行说明 | 仍缺/不能这样称呼 |
|---|---|---|
| Table1 WAMI | 正确权重/阈值/融合/计时 | 全部都用Qwen live；完整历史训练快照 |
| Table1 baseline | Guard299、Web分数后处理、detector、Book2.2、Llama chat100 | 统一样本协议；Web官方checkpoint严格复现 |
| Table2 | Word balanced来源、E&C混合输入、ToolEmu纠错 | No Defense/Llama行；原论文SmoothVLM原样覆盖 |
| live指标 | 历史轨迹与条件样本分母 | 完整逐动作计数及执行前拦截核验 |
| Table3 | full-live入口和boost配置 | 原论文backbone×defense完整矩阵 |
| Table4 | 两个真实入口、600/86样本 | 官方ToolBench/AgentBench SR；最终神经网关 |
| Table5 | 真正存在的汇总和旧消融入口 | 同一最终架构的控制变量消融 |
| Figure3/4 | 数据来源和画图代码 | 与Word最新行同步；真实多阈值ROC |
| Figure5/6 | 旧模型、横轴、计时来源 | 最终模型阈值扫描；原文6b面板 |
| Figure7 | CUDA与磁盘代理区别 | 同硬件同batch同范围的显存实测 |
| Figure8 | 单独脚本、四份日志 | 完整长训练和正负MI曲线 |
| Word/Excel | 覆盖行为和插入流程 | 清除预测改写；统一从原始CSV生成 |

缺口依据当前文件与源码，不是要求把数字调成原论文结果。本次没有重跑所有模型、没有修改认可结果、没有补造缺失数据。

## 14. 指标与运行验收

TP=攻击被拦，FN=攻击未拦，FP=正常误拦，TN=正常放行。IR=TP/(TP+FN)，FPR=FP/(FP+TN)，ACC=(TP+TN)/N。Macro先分别计算各数据集指标，再做算术平均；类别不均衡时ACC不是两类召回的平均。

延迟必须区分防御模块、含planner的总流程、缓存读取；不能直接混比。每次保存代码版本、完整命令、模型、数据SHA256、seed、阈值、实际正负样本数、错误数、缓存状态和硬件环境。超时/解析失败不能默默算放行后声称完成。

本README命令的离线入口检查：

```powershell
python scripts/check_readme_experiments.py
```

仅验证脚本存在、参数名及必需参数，不加载模型、不联网，不证明实验正确。长实验先小样本跑通，再扩大；真实重跑与旧表不同应保留差异，不能改预测去凑目标数字。

### 本次实际验证范围

核对命令参数后，另外对26个提供命令行解析器的入口执行了真实 `--help`：25个正常退出；AgentDojo detector 因现有环境的 `pydantic.fields.ModelField` 导入不兼容而失败。必须准备兼容的 AgentDojo 独立环境，不能称当前解释器直接可跑该项。本次没有修改整个环境的依赖版本。

当前项目虚拟环境还缺 pytest、python-docx、openpyxl、sentence-transformers，安装命令见第2节；这些缺失意味着不能直接运行完整pytest或Word/Excel生成。本次新增检查器和只读统计脚本的12项标准库测试通过，不声称全部项目测试通过。没有启动全量LLM评测或云API调用。
