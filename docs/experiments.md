# 实验配置与结果来源

这里保留各张表的完整参数、结果文件和历史版本说明。日常运行先看[项目README](../README.md)。下面的命令都在项目根目录执行。

> 资源更新：第三方运行代码、原始数据、50张VPI图片和3个旧版`.npz`现已随仓库提供；4个WAMI `.pt`通过`runtime-assets-20260903` Release提供。安装依赖用`requirements-baselines.txt`，资源检查用`check_runtime_resources.py`。下文保留上传资源前的核对记录，其中“未上传external/权重”等旧状态以本段和项目README为准。模型和统计口径方面的限制没有因打包而自动解决。

本项目是面向工具型智能体的提示注入防御实验工程。本 README 对应最新的 **5 页论文 `WORLD_MODEL_ASSISTED_MULTI_MODAL_INTENTION_ALIGNMENT_FOR_SECURE_AGENT_ACTION.pdf`**，逐项说明 **Table 1–5、Figure 1–2 和 SmoothVLM 补充实验**如何运行、使用哪些模型与数据，以及结果来自哪个文件。

版本基准：2026-09-03 核对的最新 5 页稿，不是项目根目录中的旧长稿，也不是旧 Word 的全部历史实验。论文原稿不上传。本说明不修改论文、认可结果 CSV、权重或预测，不把论文数字当作重跑必须达到的目标。

> 重新推理、从 CSV 重新统计、生成 Word/图片，是三件不同的事。生成文档不代表重新执行了实验。不同权重、输入、阈值和样本集合不能混称为同一次实验。

**先看复现边界：**最新论文表1–5的152个数值与选定汇总一致，但汇总一致不代表全部通过原始预测审计。WebAgentGuard 的 AgentDojo ACC 应按历史预测重算为82.0%，论文仍写74.6%；表4为代理任务评价；表5混用模型版本；图2尚无对应的最终训练曲线记录。这些问题不会通过重新生成表格自动解决，详见各节。

## 1. 实验导航

| 需要做什么 | 看哪一节 | 是否调用模型 |
|---|---|---|
| 看最新论文各表采用的数据 | 第5–9节的表格及来源文件 | 否 |
| 主表 WAMI 静态检测 | 4.1 | 是，但不调用 Qwen |
| 本地 Qwen 生成动作，再由 WAMI 检测 | 4.2 | 是，Ollama |
| 查看旧 Word 中额外的 live-agent 行 | 4.3，历史补充，不是新稿表3 | 否，读取历史轨迹 |
| Table 1 对比方法 | 5 | 按方法区分 |
| Table 2 对比方法及多模态补充 | 6 | 按方法区分 |
| Table 3 跨 backbone | 7 | 是 |
| Table 4 能力保持率 | 8 | 是，当前是代理评估 |
| Table 5 消融 | 9 | 汇总不调用模型；原始实验另有入口 |
| Figure 1–2 | 10 | 架构图不涉及评测；图2仍缺对应实测记录 |
| Word / 逐样本 Excel | 11 | 旧导出器不能自动同步最新论文 |
| 数据下载 / 历史训练配置 / 按正文新训练 | 12 | 下载联网，训练另计 |
| 本次发现的遗漏 | 13 | 不用重跑即可确认的差距 |

建议顺序：**环境与资源检查 → 第4.1节主表WAMI → 第5节表1基线 → 第6节表2 → 第7节表3 → 第8节表4 → 第9节消融核查 → 第10节图的来源核查**。只重跑推理时不需要先重新训练。

`data/final_accepted_results_by_table_and_figure.md` 可查历史来源，但其 Table 2 仍是旧 full 版本，**不是新稿选定的 balanced 行**。不能仅按文件名带 final 就认定所有文件已同步。

## 2. 环境与第一次运行

命令在项目根目录执行。Windows PowerShell 示例：

```powershell
cd D:\论文111
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install openai pandas pillow matplotlib
```

已有 `.venv` 不需要重建。未激活时，将本文的 `python` 替换成 `.\.venv\Scripts\python.exe`。Linux 用同一 Python 脚本与参数，路径分隔符用 `/`，多行续行符用 `\`。

`requirements.txt` 包含 NumPy、pytest、PyTorch、sentence-transformers，**没有列齐所有对比方法和文档依赖，也不是历史版本锁文件**。需要生成Word/Excel时另装 `python-docx openpyxl`。GuardReasoner-VL 另需：

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

Ollama 默认地址 `http://127.0.0.1:11434`。先启动 Ollama 服务；`ollama list` 成功只表示可连接服务，仍需确认对应模型存在。模型未安装时才运行 `pull`，不要一次性下载全部模型。

下载目录由 **Ollama 服务进程**的 `OLLAMA_MODELS` 决定；只给 PyCharm 的 Python 设置变量，不会改变已启动的 Ollama 服务。服务启动前设置到 D 盘，例如 `D:/OllamaModels`；Hugging Face 缓存可在当前 PowerShell 中设置：

```powershell
$env:HF_HOME = 'D:/论文111/hf-cache'
$env:PIP_CACHE_DIR = 'D:/论文111/.pip-cache'
```

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

**GitHub 未包含权重、虚拟环境、external 仓库和运行缓存；本机已有不代表克隆后也有。** 复原旧数字需要原权重和数据快照；新训练只能得到新结果，不保证等于历史表格。不要把旧 `.npz` 更名为 `.pt`，也不要用任意同名新权重替代历史模型。

资源检查示例，输出必须为 `True` 才能执行主表命令：

```powershell
Test-Path data/bipia_wami.jsonl
Test-Path data/injecagent_wami.jsonl
Test-Path data/agentdojo_wami.jsonl
Test-Path wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt
Test-Path wami_paper_mine_triplet_slot_seed4071_e4_cuda.pt
Get-FileHash data/bipia_wami.jsonl -Algorithm SHA256
```

下面新推理结果写入独立目录，避免覆盖认可数据：

```powershell
New-Item -ItemType Directory -Force data/readme_rerun
```

## 4. WAMI 两套结果分别运行

### 4.1 表1、表2及表5 Full行：paper-faithful静态检测

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

### 4.3 历史补充：旧Word额外加入的live-agent重算行

**这三行不是最新论文表3采用的boost结果，复现新稿时可跳过本节。** 保留此说明是为了避免把两组结果混用。

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

以下是最新论文采用的历史汇总值，每格为 **IR / FPR / ACC（%）**，不是本次重新推理的结果。

| 方法 | BIPIA | InjecAgent | AgentDojo | 运行入口 |
|---|---|---|---|---|
| GuardReasoner-VL Eco-3B | 72.0 / 72.0 / 50.0 | 36.0 / 20.0 / 58.0 | 42.0 / 40.8 / 50.5 | 5.1 |
| WebAgentGuard适配 | 72.0 / 16.0 / 78.0 | 80.0 / 0.0 / 90.0 | 72.0 / 8.0 / **74.6（论文），82.0（重算）** | 5.2 |
| AgentDojo PI detector | 47.7 / 34.1 / 56.8 | 78.1 / 64.7 / 56.6 | 25.7 / 25.6 / 32.2 | 5.3 |
| BookAgent-style verifier | 92.8 / 0.0 / 96.4 | 69.7 / 0.0 / 84.9 | 60.0 / 3.5 / 64.8 | 5.4 |
| Llama-Guard 3 | 12.0 / 1.0 / 55.5 | 77.0 / 0.0 / 88.5 | 67.0 / 11.6 / 76.9 | 5.5 |
| WAMI | 99.8 / 0.5 / 99.6 | 86.8 / 5.9 / 90.5 | 97.2 / 9.3 / 96.3 | 4.1 |

汇编文件：`data/final_table1_reproduction.csv`。各行的实际输入、样本量、模型和实现级别如下；表名相同不表示运行协议相同。

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

历史CSV复算后三集IR/FPR与上表一致。但AgentDojo的ACC是 `(TP18+TN23)/50=82.0%`，不是最新论文和旧Word的74.6%；FP=2、FN=7。这是汇总计算错误，不是模型配置变化。新统计结果另存readme_rerun，没有覆盖论文、Word或历史CSV。相应WebAgentGuard宏平均ACC为83.3%，按当前WAMI未舍入汇总计算的优势约为12.1个百分点，而不是论文的14.6个百分点。

### 5.3 AgentDojo official PI detector

这是官方检测组件在转换数据上的适配，**不是 Spotlighting，也不是完整官方任务 harness**。需要 `external/AgentDojo/src` 和 DeBERTa 检测模型。`download_datasets.py`下载到`external/agentdojo-main`，不能自动满足这个包目录；新机器还需准备独立的AgentDojo包：

```powershell
git clone https://github.com/ethz-spylab/agentdojo external/AgentDojo
```

已有目录不要重复克隆。记录第三方commit并按该版本的依赖安装；当前解释器已知存在`pydantic.fields.ModelField`导入冲突，解决前本项不可直接运行，不建议为了本项盲目降级整个主环境。模型目录不存在时，可把下面的`--model-name`改为`protectai/deberta-v3-base-prompt-injection-v2`，会联网下载。

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

历史来源 `data/bookagent_constraint_verifier_full.csv`，不是阈值 5.2。它不调用 LLM，是安全约束工程适配，不是 BookAgent 原视觉叙事系统。最新论文表1同时保留 AgentDojo PI detector 和 BookAgent-style，不能把二者混称。

### 5.5 Llama-Guard 3：认可的 chat pc100

```powershell
python scripts/run_llamaguard3_ollama_on_datasets.py `
  --model llama-guard3:8b --prompt-profile llamaguard_chat `
  --per-class 100 --seed 2026 `
  --output-prefix data/readme_rerun/llamaguard3_pc100
```

输出 `_summary.csv`、`_summary.md`、`_details.csv`。历史 `data/llamaguard3_ollama_pc100_summary.csv`：BIPIA 12.0%/1.0%、InjecAgent 77.0%/0.0%、AgentDojo 67.0%/11.6%，实际 N=200/200/186。

`agent_action + pc50` 是另一组，不是主表这组。最新论文将Llama-Guard放在表1，并在表4进行另一项任务保持率评测；不需要为新稿表2补造Llama-Guard行。

## 6. Table 2 与多模态补充

每格为 **IR / FPR / ACC（%）**，以下是新稿实际采用的结果，不是旧全量版本：

| 方法 | BIPIA | InjecAgent | AgentDojo | 运行入口 |
|---|---|---|---|---|
| SmoothLLM-style | 64.0 / 24.0 / 70.0 | 84.0 / 29.4 / 82.1 | 85.0 / 46.5 / 70.4 | 6.2 |
| Erase-and-Check适配 | 18.8 / 0.1 / 59.3 | 74.0 / 0.0 / 87.0 | 65.2 / 8.1 / 66.2 | 6.3 |
| ToolEmu-Sandbox适配 | 91.7 / 15.3 / 88.2 | 58.1 / 29.4 / 64.4 | 72.7 / 1.2 / 76.1 | 6.4 |
| WAMI | 99.8 / 0.5 / 99.6 | 86.8 / 5.9 / 90.5 | 97.2 / 9.3 / 96.3 | 4.1，不重复训练 |

**不要直接使用`data/final_table2_reproduction.csv`替代本表**，它仍包含旧full来源。需要按下面列出的源文件选行，而不是从所有实验里重新挑最好或最差的一行。

### 6.1 前置仓库

本机已有 external 时不重复克隆。新机器需补齐：

```powershell
git clone https://github.com/aounon/certified-llm-safety external/certified-llm-safety
git clone https://github.com/arobey1/smooth-llm external/smooth-llm
python scripts/download_datasets.py --dataset all
```

地址取自项目配置。记录第三方 commit，下载最新 main 不保证还原旧数据。即使用 Ollama，脚本仍顶层导入 openai 等包，不能跳过安装。

### 6.2 SmoothLLM-style：新稿balanced行

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

历史 `data/smoothllm_ollama_qwen25_1copy_headtail1200_random100x100_3datasets.csv`。新稿的 BIPIA/InjecAgent/AgentDojo IR=64.0%/84.0%/85.0%，不是旧 full 的61.4%/89.7%/91.4%。`100+100`是抽样上限，实际类别数量以输入和输出为准，raw InjecAgent的正常样本不足100。

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

也会计算 BIPIA，但新稿未采用这个 BIPIA 分支。当前 plan 分支只加载 InjecAgent/BIPIA，即使加 include-agentdojo 也不会处理 AgentDojo。

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

| 新稿采用行 | 历史来源 | IR / FPR / N |
|---|---|---|
| InjecAgent | `data/erase_check_ollama_qwen25_plan_suffix_m1_random100x100_3datasets.csv` | 74.0% / 0.0% / 200 |
| BIPIA | `data/erase_check_ollama_qwen25_suffix_m1_full_3datasets.csv` | 18.8% / 0.1% / 2400 |
| AgentDojo | 同上，旧 raw 集合 | 65.2% / 8.1% / 2408 |

调用官方 erase_and_check，但 judge、输入和字符级适配属于本项目。不同数据集混用输入与样本数，不能写作统一协议严格比较。

### 6.4 ToolEmu：不要混用两个入口

新稿tau=7结果来自无API的规则/风险评分适配：

```powershell
python scripts/run_toolemu_sandbox_table2.py `
  --per-class 0 --threshold 7 --seed 2026 `
  --output-csv data/readme_rerun/toolemu.csv `
  --output-md data/readme_rerun/toolemu.md `
  --details-csv data/readme_rerun/toolemu_details.csv
```

来源 `data/toolemu_sandbox_style_table2_full_tau7.csv`。不是通过官方 LLM sandbox 跑出的 0.2 ms 推理。

`scripts/run_toolemu_evaluator_on_wami_datasets.py` 是另一套官方评估器适配，需要 external/ToolEmu、external/PromptCoder、兼容依赖和本地 Qwen；其 pc*_summary 不能冒充新稿tau=7行。脚本能输出这些数字的同类结果，不等于已经按ToolEmu原始LLM模拟器流程严格复现。

### 6.5 无防御的指标定义

静态计划检测中始终放行，IR=0、FPR=0，ACC=正常数/N，无需编造推理耗时。live-agent 的无防御攻击成功率则需真实运行，不能把攻击标签直接当成功。**最新论文表2没有要求这行；表4才需要相同任务上的No Defense作为保持率分母。**

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

历史 `data/smoothvlm_style_vpi_llava_llama3_8b_plan_fidelity_20pairs.csv`，20对/40条，IR35.0%、FPR0.0%、ACC67.5%。对应最新论文3.2节补充实验；使用CyberSecEval3-VPI，不进入表1–2，不是官方SmoothVLM严格复现。

## 7. Table 3 跨 backbone

最新论文表3是WAMI搭配Qwen2.5、Mistral、Llama3的live-agent实验。历史汇总：`data/final_table3_cross_agent_reproduction.csv`的前9行，**不要取其中额外的Qwen-VL/GPT-4V行**。

| 模型 | 数据集 | IR / FPR / Block（%） | 实际N | 轨迹源文件 |
|---|---|---|---:|---|
| Qwen2.5-7B | InjecAgent | 48.0 / 0.0 / 90.8 | 4233 | `data/qwen25_7b_ollama_boost_injecagent_full.csv` |
| Qwen2.5-7B | BIPIA | 91.4 / 0.5 / 100.0 | 2400 | `data/qwen25_7b_ollama_boost_bipia_full.csv` |
| Qwen2.5-7B | AgentDojo | 35.8 / 9.3 / 95.8 | 653 | `data/qwen25_7b_ollama_boost_agentdojo_full.csv` |
| Mistral-v0.3 | InjecAgent | 76.0 / 0.0 / 100.0 | 100 | `data/mistral_v03_table3_injecagent_50x50.csv` |
| Mistral-v0.3 | BIPIA | 100.0 / 0.0 / 100.0 | 100 | `data/mistral_v03_table3_bipia_50x50.csv` |
| Mistral-v0.3 | AgentDojo | 86.0 / 8.0 / 93.5 | 100 | `data/mistral_v03_table3_agentdojo_50x50.csv` |
| Llama-3-8B | InjecAgent | 86.0 / 0.0 / 100.0 | 100 | `data/llama3_8b_table3_injecagent_50x50.csv` |
| Llama-3-8B | BIPIA | 100.0 / 0.0 / 100.0 | 100 | `data/llama3_8b_table3_bipia_50x50.csv` |
| Llama-3-8B | AgentDojo | 84.0 / 4.0 / 91.3 | 100 | `data/llama3_8b_table3_agentdojo_50x50.csv` |

IR = 被拦截的攻击样本 / 全部攻击样本。当前`Block`代码按**生成过危险动作的攻击样本**统计其中有危险动作被拦的样本比例，不是逐个动作事件相加。无危险动作的样本不计入这个Block分母；危险样本数为0时不能把指标解释为防御成功。

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

另外两集按下表替换参数，并更换`--output-csv`和`--output-md`文件名，不能覆盖上一集：

| `--dataset` | `--attack-limit` | `--benign-limit` | `--max-steps` | 输出文件名主干 |
|---|---:|---:|---:|---|
| InjecAgent | 2108 | 2125 | 4 | `boost_injecagent` |
| BIPIA | 1200 | 1200 | 3 | `boost_bipia` |
| AgentDojo | 567 | 86 | 6 | `boost_agentdojo` |

输出CSV保存逐样本结果，MD包含同次指标；直接读取新MD，不必把新CSV覆盖到历史路径。`scripts/summarize_boosted_results.py`读取固定历史路径，不自动汇总readme_rerun新文件。

Llama3 / Mistral也用full-live入口。历史汇总明确注明它们开启了**额外的runtime flow check**，逐样本记录也出现了该规则的拦截原因，因此不能把这些数字全部归因于MINE。按当前代码与已知配置启动的新运行示例：

```powershell
python scripts/run_qwen_full_live_wami_runtime.py `
  --provider ollama --model llama3:8b `
  --dataset InjecAgent --attack-limit 50 --benign-limit 50 `
  --planner-mode max-directive-parser --max-steps 5 --use-runtime-flow-check `
  --model-a wami_paper_strict_shadowv2_b70_e3_cuda.pt --tau-a -5.85 `
  --model-b wami_paper_strict_shadowv3_targeted_e2_cuda.pt --tau-b -3.75 `
  --ensemble-mode or --risk-margin 0 --passive-margin 0.15 `
  --output-csv data/readme_rerun/llama3_injecagent.csv `
  --output-md data/readme_rerun/llama3_injecagent.md
```

分别将`--model`替换为`mistral:v0.3`或`llama3:8b`，将`--dataset`替换为三个数据集名称；每项仍为50攻击+50正常，输出分别命名，合计6次运行。历史CSV没有记录全部启动参数，以上明确使用当前网关默认权重与阈值，不声称已经恢复每项历史prompt、retry和权重配置。

最新5页稿不要求旧版GPT-4V或backbone×全部baseline矩阵，不再把这些列为缺项。仍须披露并处理的是：抽样规模不同、额外flow规则和历史配置快照不完整；公平的新跨模型比较应先冻结相同数据和防御配置再运行。

## 8. Table 4 能力保持率

以下是论文采用的历史数值。**TB/AB是论文中的列名，不代表当前脚本已经接入两个官方评测器。**

| 方法 | TB SR（%） | AB SR（%） | TB保持率（%） | AB保持率（%） |
|---|---:|---:|---:|---:|
| No Defense | 86.8 | 90.7 | 100.0 | 100.0 |
| Erase-and-Check | 62.3 | 44.2 | 71.8 | 48.7 |
| ToolEmu-Sandbox | 61.2 | 54.7 | 70.4 | 60.3 |
| Llama-Guard 3 | 85.3 | 80.2 | 98.3 | 88.5 |
| WAMI | 86.0 | 89.5 | 99.0 | 98.7 |

汇编：`data/final_table4_required_columns.csv`中`section=local_nonlite`的行。下面**两条命令分别评测两列任务，每条内部运行多个防御方法**，不是要手工为每个方法跑同一命令。

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

论文采用的三个数据集宏平均如下，**目前只能追溯其汇总来源，不能称为最终网络的统一控制变量消融**：

| 变体 | IR（%） | FPR（%） | ACC（%） | 当前来源 |
|---|---:|---:|---:|---|
| WAMI Full | 94.6 | 5.2 | 95.5 | 表1最终静态结果 |
| w/o TDG | 17.2 | 11.5 | 41.6 | 旧NumPy消融 |
| w/o World Model | 52.4 | 1.2 | 66.1 | 旧NumPy消融 |
| w/o MINE | 15.6 | 0.0 | 47.1 | 旧NumPy消融 |
| w/o Shadow Training | 70.5 | 2.2 | 82.0 | 旧NumPy消融 |

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

## 10. 最新论文Figure 1–2

### Figure 1：框架示意图

这是结构图，不是调用某个数据集得到的指标图。对应关系如下：

| 图中部分 | 主要代码 | 说明 |
|---|---|---|
| 工具依赖图TDG | `wami/tdg.py` | 从计划构造依赖图；live-agent还从runtime trace形成待检查计划 |
| latent/world model与memory | `wami/torch_model.py` | 编码、状态预测、记忆更新 |
| Shadow Training | `wami/torch_training.py` | 训练目标、正负样本、辅助监督 |
| MINE与路径拦截 | `wami/paper_mine_gateway.py` | 从状态分数作执行前检测 |
| agent动作循环 | `scripts/run_qwen_full_live_wami_runtime.py` | 生成动作、网关检查、本地模拟器推进 |

没有确认到生成新稿Figure 1的可编辑源文件或独立绘图命令。不能把复制PDF截图称为代码生成；图中的音频等通道也没有因出现在结构图中就自动获得主表实验支持。

### Figure 2：目前缺对应实测曲线

| 项目 | 新稿Figure 2 | 当前最终训练记录 |
|---|---|---|
| 横轴 | 0–30轮，标注第15轮稳定分离 | 两个主模型均记录4轮 |
| 纵轴 | 正常/注入意图两条0–1范围曲线 | `mine_bound`、`mi_gap`、`loss`、`world_loss` |
| 阴影 | 图中有波动带 | 未找到对应逐轮重复实验统计 |
| 与正文关系 | 图为30轮 | 正文写20轮、batch64；实际记录4轮、batch32 |

因此，**目前没有可以诚实保证生成这张Figure 2的实验命令**。不能补写30轮数字、任意归一化MINE分数或拟合两条曲线来对齐图片。需要保存同一次训练中固定验证集上的正负分数、轮数、统计口径和重复实验数据，再绘制相应曲线；只把4改成20并不能补齐这些字段。

现有真实训练日志：

```text
data/paper_mine_sourceaware_recall_seed2061_e4_training.csv
data/paper_mine_triplet_slot_seed4071_e4_training.csv
```

历史`plot_final_figure8_shadow_training.py`可画MI gap/loss，**不是最新Figure 2**；`plot_final_figures_paper_style.py`绘制的旧图3–7也不属于这份5页稿。它们不再列为最新论文必须复现的图，不建议为了生成新稿而执行旧绘图器。

## 11. Word 与逐样本 Excel

### 旧Word导出器，不是最新论文的一键生成器

**复现最新论文时可跳过本节。** 下列命令覆盖`data/WAMI最终实验结果汇总.docx`，先关闭Word并保留需要的旧版；只看当前结果无需执行。它们是旧文档工作流，可能保留旧数字及旧图，不会自动把本README中的纠错写入Word。

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

### 12.1 产生主表权重的已知历史配置

下表来自两份`*_training.md`及本地checkpoint的`config`，**不是照抄论文正文**。

| 配置 | Source-aware A | Triplet-slot B |
|---|---|---|
| 训练集 | `data/paper_shadow_train_sourceaware_seed2061.jsonl` | `data/paper_shadow_train_triplet_seed4071.jsonl` |
| 验证集 | `data/paper_shadow_val_sourceaware_seed2061.jsonl` | `data/paper_shadow_val_triplet_seed4071.jsonl` |
| 训练 / 验证条数 | 960 / 240 | 1440 / 360 |
| 网络 | 4层、1024维、8头Transformer | 相同，包含slot memory |
| MINE | 3层ReLU MLP | 3层ReLU MLP |
| optimizer / lr | AdamW / 0.0002 | 相同 |
| weight decay / dropout | 0.0001 / 0.1 | 相同 |
| 模型seed | **7** | **7** |
| epochs / batch size | **4 / 32** | **4 / 32** |
| benign weight | 1.7 | 1.7 |
| supervised gap weight / margin | 0.3 / 1.15 | 相同 |
| pairwise weight / margin | 0.4 / 1.35 | 相同 |
| attack recall weight | 0.0 | 0.0 |
| transition / auxiliary weight | 0.3 / 0.1 | 相同 |
| provenance / slot / subgoal weight | 旧日志未完整记录，不能补猜 | 0.12 / 0.12 / 0.15 |
| labeled attack negatives | 开启 | 开启 |

两个数据文件名的2061/4071不是checkpoint保存的模型seed。当前训练脚本默认20轮、batch64，**直接不带参数运行，不会复原历史4轮权重**。当前源码也已演进，尤其A旧模型不能简单用当前默认slot结构重训后宣称完全相同。

### 12.2 按Triplet-slot日志已知配置重新训练

这是**新训练**，需要上表中的独立训练/验证JSONL。没有这些快照时先补齐资源，不得替换成三个测试集。已有最终权重、只想评测时跳过本命令。

```powershell
python scripts/train_wami_paper_strict.py `
  --train-data data/paper_shadow_train_triplet_seed4071.jsonl `
  --val-data data/paper_shadow_val_triplet_seed4071.jsonl `
  --epochs 4 --batch-size 32 --seed 7 --device cuda --skip-eval `
  --benign-weight 1.7 --supervised-gap-weight 0.3 --supervised-margin 1.15 `
  --pairwise-weight 0.4 --pairwise-margin 1.35 `
  --attack-recall-weight 0 --attack-target-score -3.5 `
  --transition-weight 0.3 --auxiliary-weight 0.1 `
  --provenance-weight 0.12 --slot-specific-weight 0.12 --subgoal-weight 0.15 `
  --save data/readme_rerun/triplet_slot_e4.pt `
  --log-file data/readme_rerun/triplet_slot_e4_steps.csv `
  --output-csv data/readme_rerun/triplet_slot_e4_training.csv `
  --output-md data/readme_rerun/triplet_slot_e4_training.md
```

完成后得到新`.pt`和每轮loss/MINE日志。评估它时将第4.1节单模型命令的`--model`改为新路径，并用新的输出名；保留与旧结果的差异，不覆盖原权重。`--skip-eval`仅跳过评估，不是跳过训练。

重新训练后不能假定旧阈值仍然合适。若校准新阈值，只能在独立验证集上操作，冻结后再评估测试集；不能根据测试结果反复修改阈值。

### 12.3 正文20轮、batch64怎样运行

要实际执行论文正文的轮数和批量，可将12.2的`--epochs 4 --batch-size 32`改成`--epochs 20 --batch-size 64`，同时将全部输出主干改为`triplet_slot_e20_b64`。这会产生**另一项新实验**，不能描述成已经得到表1那些数字的历史训练，也不能仅改这两个参数就声称负样本策略、损失和图2全部符合正文。

当前训练含带标签的攻击负样本和辅助监督；论文2.3只描述正常配对和batch打乱负样本。`--no-labeled-negatives`仅控制其中一项，不等于完整“零监督”开关。需要按实际运行补充方法说明，或者另行实现并验证严格对应正文的训练方案。本README不隐去这个差异。

### 12.4 独立生成数据的小规模闭环

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

这不是最终checkpoint训练配方，也不会自动生成上表同名的source-aware/triplet数据快照。正式训练需独立train/validation/test，记录生成器版本、seed、样本哈希、损失权重、阈值策略和checkpoint。不能因现在有独立生成器就断言所有历史训练均无测试泄漏。不要省略`--data`或`--train-data`后直接训练：旧入口默认数据是InjecAgent测试转换集。

API只填本地config/*.local.*，模板是 `config/official_baselines.example.env`；不要覆盖已有密钥配置。部分脚本默认云API，复制命令不要漏 backend/provider=ollama。本地后端不消耗云token，首次下载仍需网络。

## 13. 最新论文对应状态

| 项目 | 已补运行说明 | 仍缺/不能这样称呼 |
|---|---|---|
| Table1 WAMI | 主表权重/阈值/融合/计时、历史训练配置 | 不能说全都经过Qwen live；历史训练和最终逐样本证据仍需审计 |
| Table1 baseline | Guard299、Web阈值后处理、detector、Book2.2、Llama chat100 | Web ACC需纠正；不是统一样本或全部官方流程 |
| Table2 | 最新balanced来源、E&C混合输入、ToolEmu tau7 | 不可把适配器称为完整官方LLM sandbox复现 |
| Table3 | full-live入口、boost配置、6项抽样跨模型运行方式 | 条件样本Block不等于事件级Block；额外flow规则和历史配置需披露 |
| Table4 | 两个真实入口、600/86样本 | 官方ToolBench/AgentBench SR；最终神经网关 |
| Table5 | 真正存在的汇总和旧消融入口 | 同一最终架构的控制变量消融 |
| Figure1 | 图中模块与源码对应 | 可编辑作图源文件；未评测通道的验证 |
| Figure2 | 明确实际日志与图中曲线的差别 | 对应轮数的正负分数及阴影统计，没有已验证的一键命令 |
| SmoothVLM补充 | llava-llama3、20对、3-copy、2票 | 不是官方SmoothVLM严格复现，不能塞入三个文本数据集的列 |
| Word/Excel | 旧流程的覆盖行为和数据风险 | 清除预测改写；统一从原始CSV生成，旧生成器不能自动同步新稿 |

新稿表2不要求额外No Defense/Llama行，表3不要求GPT-4V矩阵，图3–8不再属于本版范围。缺口依据当前文件与源码，不是要求把数字调成论文结果。

## 14. 指标与运行验收

TP=攻击被拦，FN=攻击未拦，FP=正常误拦，TN=正常放行。IR=TP/(TP+FN)，FPR=FP/(FP+TN)，ACC=(TP+TN)/N。Macro先分别计算各数据集指标，再做算术平均；类别不均衡时ACC不是两类召回的平均。

延迟必须区分防御模块、含planner的总流程、缓存读取；不能直接混比。每次保存代码版本、完整命令、模型、数据SHA256、seed、阈值、实际正负样本数、错误数、缓存状态和硬件环境。超时/解析失败不能默默算放行后声称完成。

本README命令的离线入口检查：

```powershell
python scripts/check_readme_experiments.py
```

仅验证脚本存在、参数名及必需参数，不加载模型、不联网，不证明实验正确。长实验先小样本跑通，再扩大；真实重跑与旧表不同应保留差异，不能改预测去凑目标数字。

### 验证范围与已知环境问题

历史README检查曾对26个命令行入口执行`--help`：25个正常退出，AgentDojo detector因`pydantic.fields.ModelField`导入不兼容而失败。必须准备兼容的AgentDojo独立环境，不能称当前解释器直接可跑该项。本次文档更新没有修改整个环境的依赖版本。

依赖缺失时先按第2节安装对应包。`--help`通过只说明入口可以解析，不能证明模型权重、数据快照或最终指标正确。运行离线检查器及其标准库测试可使用：

```powershell
python -m unittest discover -s tests -p test_readme_experiments.py -v
```

本次README更新仅核对源码、元数据、历史结果和命令；未启动全量LLM评测、CUDA训练或云API调用，未修改论文、认可结果、逐条预测、模型参数或密钥。

2026-09-03本次实际检查：37条实验命令、31个脚本的路径/参数名/必需参数检查通过；7项README标准库测试通过；集成检测、单模型检测、训练、full-live、WebAgentGuard、GuardReasoner-VL共6个关键入口的`--help`通过。这里只确认入口可解析，不声称各模型实验已重新跑通。
