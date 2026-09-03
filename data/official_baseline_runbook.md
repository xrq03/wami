# Official Baseline Runbook

This file records the non-secret setup for running official baseline code.
Copy `config/official_baselines.example.env` to `config/official_baselines.local.env`
and fill API/model paths locally.

## What Is Already Prepared

- Official Erase-and-Check source: `external/certified-llm-safety`
- Official SmoothLLM source: `external/smooth-llm`
- Official ToolEmu source: `external/ToolEmu`
- ToolEmu PromptCoder dependency: `external/PromptCoder`
- Local config template: `config/official_baselines.example.env`
- Official baseline status output:
  - `data/official_baseline_status.md`
  - `data/official_baseline_status.json`

## Local Compatibility Patches

The following local compatibility patches were added. They do not change the
baseline algorithms, but let official code read local environment settings.

- `external/certified-llm-safety/main.py`
  - Reads `OPENAI_API_KEY`
  - Reads `OPENAI_BASE_URL` or `OPENAI_API_BASE`
- `external/certified-llm-safety/defenses.py`
  - Reads `ERASE_CHECK_MODEL`
- `external/ToolEmu/toolemu/utils/llm.py`
  - Allows custom OpenAI-compatible model names when `WAMI_ALLOW_CUSTOM_OPENAI_MODEL=1`
  - Reads `OPENAI_BASE_URL` or `OPENAI_API_BASE`

## Erase-and-Check

Dry run:

```powershell
uv run --with numpy python scripts\run_official_erase_check.py --env-file config\official_baselines.local.env --dry-run
```

Run:

```powershell
uv run --with numpy --with torch --with transformers --with openai python scripts\run_official_erase_check.py --env-file config\official_baselines.local.env
```

Results are written under:

```text
data/official_erase_check_results/
```

## SmoothLLM

SmoothLLM requires local Vicuna or Llama-2 weights and GPU. Fill these in
`config/official_baselines.local.env`:

```text
SMOOTHLLM_LLAMA2_MODEL_PATH=
SMOOTHLLM_LLAMA2_TOKENIZER_PATH=
```

Dry run:

```powershell
uv run --with numpy python scripts\run_official_smoothllm.py --env-file config\official_baselines.local.env --dry-run
```

Run only after model paths and dependencies are installed:

```powershell
uv run --with torch --with transformers --with pandas python scripts\run_official_smoothllm.py --env-file config\official_baselines.local.env
```

## ToolEmu

ToolEmu requires API access. Fill:

```text
OPENAI_API_KEY=
OPENAI_BASE_URL=
TOOL_EMU_AGENT_MODEL=
TOOL_EMU_EVALUATOR_MODEL=
```

Dry run:

```powershell
uv run --with numpy python scripts\run_official_toolemu.py --env-file config\official_baselines.local.env --dry-run
```

Run a tiny official subset:

```powershell
uv run --with numpy --with roman --with langchain==0.0.277 --with python-dotenv==1.0.0 --with pandas --with tiktoken --with openai --with transformers --with scipy --with scikit-learn --with statsmodels --with matplotlib --with seaborn --with anthropic==0.3.6 --with rouge_score --with fire --with wikipedia --with chromadb python scripts\run_official_toolemu.py --env-file config\official_baselines.local.env --trunc-num 3
```

Important: official ToolEmu evaluates its own benchmark assets. It is not a
drop-in detector for converted InjecAgent/BIPIA plans.
