# ToolBench Full Data Download Status

## Official Download Attempts

| Source | URL / path | Result |
|---|---|---|
| Google Drive official `data.zip` | `https://drive.google.com/uc?export=download&id=1XFjDxVZdUY7TXYF2yvzx3pJlS2fy78jk&confirm=yes` | failed: current network cannot connect to `drive.google.com:443` |
| Tsinghua Cloud official mirror | `https://cloud.tsinghua.edu.cn/f/c9e50625743b40bfbe10/` | failed: page returns `Link does not exist` |
| HuggingFace mirror probe | `Yhyu13/ToolBench_toolllama_G123_dfs` | failed: current network cannot connect to `huggingface.co:443` |

## Local Usable Larger Evalset

The cloned ToolBench repository already contains official ToolEval default-evalset result files under:

`external/ToolBench/toolbench/tooleval/results/default_evalset/gpt-3.5-turbo_CoT`

Extracted local dataset:

`data/toolbench_default_evalset_600.jsonl`

| Split | Rows |
|---|---:|
| G1_category | 100 |
| G1_instruction | 100 |
| G1_tool | 100 |
| G2_category | 100 |
| G2_instruction | 100 |
| G3_instruction | 100 |
| Total | 600 |

This is not the full 126K ToolBench `data.zip`, but it is much larger and more suitable than the 10-query `data_example/instruction` sample for Table 4 experiments.
