# WAMI

一个用于工具型Agent提示注入防御的Python项目。

WAMI把工具调用组织成TDG，通过world model预测后续状态，再用MINE分数判断动作是否偏离用户意图。项目也包含论文用到的对比方法、跨模型测试和消融实验。

这里主要讲怎么运行。每张表的完整数值、历史配置和版本差异放在[实验说明](docs/experiments.md)里。

## 从GitHub下载后先做这几步

运行需要的第三方代码、原始数据、50张VPI图片和3个旧版WAMI小权重已放进仓库，不用再逐个克隆`external/`。4个较大的WAMI权重放在[Release附件](https://github.com/xrq03/wami/releases/tag/runtime-assets-20260903)中。

装好下面的Python环境后，再按需要安装对比方法依赖：

```powershell
python -m pip install -r requirements-baselines.txt
python scripts/check_runtime_resources.py --group external --verify-hashes
python scripts/check_runtime_resources.py --group vpi-images --verify-hashes
```

下载主表WAMI权重需要GitHub CLI，并登录有仓库访问权限的账号：

```powershell
gh auth login
python scripts/check_runtime_resources.py --group wami-main --download --verify-hashes
```

跑live-agent时，将`--group wami-main`换成`--group wami-live`。也可以在Release页面手动下载同名`.pt`，放到项目根目录。检查器会验证文件大小和SHA256，不会覆盖已经存在但内容不匹配的权重。

**Ollama模型不上传。** 它们和另外两个第三方检测模型按下表准备，装需要的即可。

| 模型 | 用在哪 | 怎么准备 |
|---|---|---|
| `qwen2.5:7b-instruct` | Qwen live-agent、WebAgentGuard、SmoothLLM、Erase-and-Check、表4 | `ollama pull qwen2.5:7b-instruct` |
| `llama-guard3:8b` | Llama-Guard、表4 | `ollama pull llama-guard3:8b` |
| `llama3:8b` | 表3Llama跨模型实验 | `ollama pull llama3:8b` |
| `mistral:v0.3` | 表3Mistral跨模型实验 | `ollama pull mistral:v0.3` |
| `llava-llama3:8b` | SmoothVLM多模态补充 | `ollama pull llava-llama3:8b` |
| `yueliu1999/GuardReasoner-VL-Eco-3B` | GuardReasoner-VL，非Ollama，原权重约7.6GB | 下载到`models/guardreasoner-vl-eco-3b` |
| `protectai/deberta-v3-base-prompt-injection-v2` | AgentDojo PI detector，非Ollama | 下载到`models/protectai-deberta-v3-base-prompt-injection-v2` |

两个Hugging Face模型的下载命令：

```powershell
hf download yueliu1999/GuardReasoner-VL-Eco-3B --local-dir models/guardreasoner-vl-eco-3b
hf download protectai/deberta-v3-base-prompt-injection-v2 --local-dir models/protectai-deberta-v3-base-prompt-injection-v2
```

`hf`命令随`huggingface-hub`安装。当前上传包不含这两个Hugging Face模型的完整权重；DeBERTa原来的本地目录也没有完整模型文件，不能只复制配置文件就运行检测。

## 从哪里开始

- 先安装环境，准备数据和对应的模型权重。
- 跑主表WAMI：看“先跑WAMI”里的计划检查命令，不需要Qwen。
- 跑本地Qwen生成动作的版本：先试几条，再用表3的全量配置。
- 跑对比方法：按表1、表2依次执行，结果会放在`data/readme_rerun/`。

## 项目结构

```text
wami/       TDG、world model、MINE、训练和网关代码
scripts/    数据处理、实验运行、结果统计和绘图脚本
tests/      测试
config/     配置模板，本地密钥配置不上传
data/       数据集与实验结果
models/     本地模型，需要另外准备
external/   已打包的第三方运行代码和数据，保留原许可证
docs/       完整实验说明
```

## 快速开始

下面用Windows PowerShell举例，所有命令都在项目根目录执行。项目路径不同的话，把`D:\论文111`换成自己的目录。

```powershell
cd D:\论文111
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install openai pandas pillow matplotlib
```

已有 `.venv` 不需要重建。未激活时，将本文的 `python` 替换成 `.\.venv\Scripts\python.exe`。Linux 用同一 Python 脚本与参数，路径分隔符用 `/`，多行续行符用 `\`。

`requirements.txt`包含基础依赖。需要生成Word/Excel时另装`python-docx openpyxl`；跑GuardReasoner-VL时还需要下面几个包。历史环境没有完整锁定，换环境后结果和耗时可能变化：

```powershell
python -m pip install transformers accelerate bitsandbytes
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
python -m pytest -q
python scripts/demo.py
```

本地使用Python 3.12。CUDA训练和4bit VLM需要兼容的驱动、PyTorch和足够显存，权重、数据和环境可能占数十GB，建议放D盘。

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

先跑几条确认能完成，再扩大数量。多个本地模型同时运行容易争用显存，首次加载和缓存也会影响耗时。

## 准备数据和权重

### 三个统一格式数据集

| 文件 | 攻击 | 正常 | 总数 |
|---|---:|---:|---:|
| `data/bipia_wami.jsonl` | 1200 | 1200 | 2400 |
| `data/injecagent_wami.jsonl` | 2108 | 2125 | 4233 |
| `data/agentdojo_wami.jsonl` | 567 | 86 | 653 |

每行包含 `intent`、`plan`、`label` 等字段，1 是攻击，0 是正常。`plan` 是本项目转换/构造的工具轨迹，不是三个官方数据集原本就提供同一种计划格式。

SmoothLLM和Erase-and-Check的`raw`模式从`external/`读取原始数据，和上表的`plan`集合不同。设置100+100是数量上限，正常样本不足时会少于200条，以实际输出为准。

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

Git仓库包含3个旧版`.npz`小权重，4个主表/live-agent的`.pt`从Release下载。虚拟环境、Ollama模型和运行缓存不打包。只评测时不用重新训练。

先确认下面的文件都存在，`Test-Path`应该返回`True`：

```powershell
Test-Path data/bipia_wami.jsonl
Test-Path data/injecagent_wami.jsonl
Test-Path data/agentdojo_wami.jsonl
Test-Path wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt
Test-Path wami_paper_mine_triplet_slot_seed4071_e4_cuda.pt
Get-FileHash data/bipia_wami.jsonl -Algorithm SHA256
```

后面的新结果统一放这里，和原来的结果分开：

```powershell
New-Item -ItemType Directory -Force data/readme_rerun
```

## 先跑WAMI

### 检查已有计划

数据中的`intent + plan`直接交给WAMI检查，流程是TDG → world model → MINE。这对应表1、表2的WAMI行和表5的Full行，不需要调用Qwen。

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

沿用上面的模式即可，不需要根据新的测试结果再挑一行。集成脚本的计时包含A和B两次检测；AgentDojo单模型的耗时用下面的命令测。

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

导出的CSV包含每条数据及本次模型判断，采用上面的OR/B配置。

### 让本地Qwen生成动作

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

另外两集换`--dataset BIPIA`或`AgentDojo`，并换一个输出文件名。全量配置见后面的表3。

`--bootstrap-first-observation` 会在 planner 接管前加入首个工具返回，加与不加是不同实验。`max-directive-parser` 是强化动作提取的压力场景，不是普通助手的默认安全设置。这是当前代码的运行方式，历史prompt版本不完整，重跑结果可能不同。

## 表1：对比方法

### GuardReasoner-VL

每集最多50条攻击和50条正常样本。历史运行完成299条，其中AgentDojo少了1条正常样本。

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

权重目录不存在时，可以把`--model-path`改成`yueliu1999/GuardReasoner-VL-Eco-3B`下载。保留`--backend transformers`，脚本默认的mock后端只用于演示。新结果看`guardreasoner.md`，逐条记录看`guardreasoner_details.csv`。

### WebAgentGuard

这里使用本地Qwen2.5的`action_fidelity`适配，不是独立的官方guard权重。

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

前两条命令默认按模型decision汇总。要用上表的风险分数阈值，再运行下面的统计脚本。

统计刚刚生成的两个CSV，不需要再次调用模型：

```powershell
python scripts/summarize_webagentguard_operating_points.py `
  --next-csv data/readme_rerun/webagentguard_next.csv `
  --full-csv data/readme_rerun/webagentguard_full.csv `
  --output-csv data/readme_rerun/webagentguard_selected.csv `
  --output-md data/readme_rerun/webagentguard_selected.md
```

结果看`webagentguard_selected.md`。这组阈值来自历史事后选择，不是独立验证集校准结果。旧AgentDojo行的ACC有计算错误：按原预测应为82.0%，不是74.6%。

### AgentDojo PI detector

这里运行官方提示注入检测组件，不是Spotlighting或完整的AgentDojo任务环境。需要`external/AgentDojo/src`和DeBERTa模型。数据下载脚本的目录不同，这个包另外准备：

```powershell
git clone https://github.com/ethz-spylab/agentdojo external/AgentDojo
```

仓库已经包含这个目录，不用再克隆。安装`requirements-baselines.txt`会同时安装AgentDojo及其依赖，并避开旧版langchain与Pydantic 2的冲突；建议使用新虚拟环境。模型目录不存在时，将`--model-name`改为`protectai/deberta-v3-base-prompt-injection-v2`即可联网下载。

```powershell
python scripts/run_agentdojo_official_detector_on_wami_datasets.py `
  --model-name models/protectai-deberta-v3-base-prompt-injection-v2 `
  --threshold 0.5 --input-mode tool_outputs `
  --attack-n 100000 --benign-n 100000 `
  --output-csv data/readme_rerun/agentdojo_detector.csv `
  --output-md data/readme_rerun/agentdojo_detector.md
```

这里用较大的上限取完现有样本，`0`不表示全量。输出是数据集级汇总，不包含每条历史判断。

### BookAgent-style 约束验证

```powershell
python scripts/run_bookagent_constraint_verifier.py `
  --threshold 2.2 `
  --output-csv data/readme_rerun/bookagent.csv `
  --output-md data/readme_rerun/bookagent.md
```

这是本地安全约束适配，不调用LLM。历史结果在`data/bookagent_constraint_verifier_full.csv`。

### Llama-Guard 3

```powershell
python scripts/run_llamaguard3_ollama_on_datasets.py `
  --model llama-guard3:8b --prompt-profile llamaguard_chat `
  --per-class 100 --seed 2026 `
  --output-prefix data/readme_rerun/llamaguard3_pc100
```

输出 `_summary.csv`、`_summary.md`、`_details.csv`。历史 `data/llamaguard3_ollama_pc100_summary.csv`：BIPIA 12.0%/1.0%、InjecAgent 77.0%/0.0%、AgentDojo 67.0%/11.6%，实际 N=200/200/186。

保持`llamaguard_chat`和每类100条这组设置即可，`agent_action + pc50`对应另一项实验。

## 表2与多模态补充

### 前置仓库

仓库已经带上下面两份运行代码和原始数据。只有目录缺失时才需要重新获取：

```powershell
git clone https://github.com/aounon/certified-llm-safety external/certified-llm-safety
git clone https://github.com/arobey1/smooth-llm external/smooth-llm
python scripts/download_datasets.py --dataset all
```

上游版本可能变化，建议记下所用commit。即使用Ollama，脚本仍会导入`openai`包，前面的安装步骤不要跳过。

### SmoothLLM-style

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

这组配置是1-copy扰动、首尾截取1200字符，历史IR分别为64.0%、84.0%、85.0%。它是分类judge适配，不是完整多拷贝平滑投票。`100+100`是抽样上限，实际数量看输出；复用缓存后的耗时也会不同。

### Erase-and-Check

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

这里调用官方erase_and_check函数，judge、输入和字符处理由本项目适配。论文这组结果混用了输入类型和样本数。

### ToolEmu-Sandbox适配

新稿tau=7结果来自无API的规则/风险评分适配：

```powershell
python scripts/run_toolemu_sandbox_table2.py `
  --per-class 0 --threshold 7 --seed 2026 `
  --output-csv data/readme_rerun/toolemu.csv `
  --output-md data/readme_rerun/toolemu.md `
  --details-csv data/readme_rerun/toolemu_details.csv
```

结果看`toolemu.md`。这个tau=7版本是本地规则/风险评分适配，不调用官方LLM工具模拟器。另一套官方评估器入口`run_toolemu_evaluator_on_wami_datasets.py`对应不同结果。

### SmoothVLM-style 多模态补充

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

## 表3：换模型跑live-agent

这一组分别使用Qwen2.5、Mistral和Llama3生成动作。历史结果在`data/final_table3_cross_agent_reproduction.csv`的前9行。

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

Llama3和Mistral使用同一个入口，每集50+50。历史实验还开启了`runtime flow check`规则，因此拦截不全来自MINE。按当前代码和已知设置运行：

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

模型分别用`mistral:v0.3`和`llama3:8b`，每个模型跑三个数据集，每项50攻击+50正常，共6次。每次换一个输出名。上面采用当前网关默认配置；历史启动参数没有全部保存，重跑可能和旧结果不同。

## 表4：正常任务保持率

### ToolBench 600 条

```powershell
python scripts/run_toolbench_default_evalset_qwen25_table4.py `
  --input-jsonl data/toolbench_default_evalset_600.jsonl --limit 600 `
  --planner-model qwen2.5:7b-instruct --judge-model qwen2.5:7b-instruct `
  --llamaguard-model llama-guard3:8b --wami-model wami_injecagent_final_e5.npz `
  --match-threshold 0.5 --output-prefix data/readme_rerun/toolbench600
```

输出 summary/details/plans 等。历史 `data/toolbench_default_evalset_qwen25_table4_600_summary.csv`，WAMI SR86.0%、保持率99.0%。成功依据是生成工具计划与参考工具匹配，**不是实际执行 ToolBench API 后的官方 SR**。skip-existing-plans 仅能复用同模型同输入的计划。

### 论文中标为AgentBench的列

```powershell
python scripts/run_agentbench_proxy_table4_nonlite_baselines.py `
  --live-csv data/qwen25_7b_ollama_boost_agentdojo_full.csv `
  --data data/agentdojo_wami.jsonl --limit 86 `
  --judge-model qwen2.5:7b-instruct --llamaguard-model llama-guard3:8b `
  --wami-model wami_injecagent_final_e5.npz `
  --output-prefix data/readme_rerun/agentbench_proxy
```

历史 `data/agentbench_proxy_table4_nonlite_qwen25_summary.csv`，WAMI SR89.5%、保持率98.7%。实际输入是 AgentDojo 的86条正常 live 轨迹，不是 AgentBench 官方环境。

SR是判定成功且未中断的任务比例，保持率是有防御SR除以同次无防御SR。这两个脚本都使用旧`.npz`网关，和前面的主表模型不同。

## 表5：消融实验

逐数据集源：`data/final_table5_ablation_injecagent.csv`、`data/final_table5_ablation_bipia.csv`、`data/final_table5_ablation_agentdojo.csv`。只合并汇总：

```powershell
python scripts/build_final_table5_ablation.py
```

输出`data/final_table5_ablation.csv/.md`，会覆盖同名汇总文件，不会重新训练。

旧四个删模块分支来自 NumPy 入口，例如：

```powershell
python scripts/run_wami_paper_ablation.py `
  --data data/injecagent_wami.jsonl --model wami_injecagent_final_e5.npz `
  --output-csv data/readme_rerun/legacy_ablation.csv `
  --output-md data/readme_rerun/legacy_ablation.md
```

先确认权重存在，旧脚本缺权重时会创建新模型。目前Full取自主表，删模块的行来自旧实现，部分变体还同时改变了其他设置，因此这还不是同一版网络的完整消融。具体差别放在[实验说明](docs/experiments.md)里。

## 下载缺少的数据

已有数据可以直接用，需要重新下载和转换时运行：

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

## 重新训练WAMI

只想评测的话可以跳过这一节。下面按Triplet-slot记录的配置重新训练，需要命令中的独立训练集和验证集，三个测试集继续留作评测。

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

完成后得到新`.pt`和每轮loss/MINE日志。评估它时将前面的单模型命令的`--model`改为新路径，并用新的输出名；保留与旧结果的差异，不覆盖原权重。`--skip-eval`仅跳过评估，不是跳过训练。

新权重的阈值可以在独立验证集上校准，确定后再评估测试集，不用测试结果反复调参。

历史主模型是4轮、batch32，模型seed为7。论文正文写20轮、batch64；要按正文重训可以修改这两个参数并更换输出名，但得到的是新实验。当前训练还用了带标签负样本和辅助损失，完整设置见[实验说明](docs/experiments.md)。

## 图片和结果在哪看

运行结束后，通常打开输出的`.md`看表格，用`.csv`继续统计。带`details`的CSV保存逐条结果；只有汇总数字的文件不能反推出每条判断。

| 内容 | 历史结果位置 |
|---|---|
| 表1 | `data/final_table1_reproduction.csv` |
| 表2 | 使用不同配置选行，源文件列表见实验说明；旧`final_table2_reproduction.csv`未同步 |
| 表3 | `data/final_table3_cross_agent_reproduction.csv`的前9行 |
| 表4 | `data/final_table4_required_columns.csv`中`local_nonlite`行 |
| 表5 | `data/final_table5_ablation.csv` |
| 新运行结果 | `data/readme_rerun/` |

最新论文图1是架构图，目前没有对应的可编辑绘图源文件。图2是训练曲线，但图中30轮、正文20轮和现有4轮日志还没对上，暂时没有能直接生成论文图2的实测绘图命令。旧图3–8和Word生成脚本没有同步到最新5页稿。

需要看每条WAMI数据如何判断，运行前面的`export_wami_accepted_audit_csv.py`。旧Excel导出器存在按目标计数改写预测的问题，暂时不要用它作为原始预测导出工具，详情在实验说明里。

## 常见问题

**为什么重跑和论文数字不同？**

先检查权重、数据版本、样本数量、阈值和prompt。重新训练或换模型版本都会影响结果，缓存和硬件也会影响耗时。先保留新结果，再对照配置查差异。

**IR、FPR和ACC怎么看？**

- IR：攻击样本中被拦截的比例。
- FPR：正常样本中被误拦截的比例。
- ACC：所有样本中判断正确的比例。
- 表3的Block：使用前文的条件样本分母，不和IR混用。
- 保持率：有防御的任务成功率 / 同次无防御的任务成功率。

**如何检查命令和运行测试？**

```powershell
python scripts/check_readme_experiments.py
python -m unittest discover -s tests -p test_readme_experiments.py -v
python -m pytest -q
```

第一条只检查README里的脚本路径和参数，不运行模型。最后一条是完整测试入口，需要安装测试依赖；前两条通过不等于完整实验已经跑通。

更多参数、每张表的具体数值、环境问题和历史结果来源，见[实验说明](docs/experiments.md)。

资源来源、SHA256和打包时排除的文件记录在`config/runtime_assets.json`。这次只补运行资源，没有改实验算法或原来的结果数字。
