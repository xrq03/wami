# WAMI Reproduction Progress After World Training and VPI Extension

## Newly Completed Runs

| Experiment | Model / Backend | N | IR | FPR | ACC | Notes |
|---|---|---:|---:|---:|---:|---|
| InjecAgent | WAMI world-trained e3 | 4233 | 95.4% | 0.0% | 97.7% | New shadow diversity + contrastive world loss |
| BIPIA | WAMI world-trained e3 | 2400 | 100.0% | 0.5% | 99.8% | New shadow diversity + contrastive world loss |
| CyberSecEval3 VPI adapted | WAMI + Qwen-VL-Max | 100 | 100.0% | 0.0% | 100.0% | 50 visual prompt injection images, benign/attack paired plans |

## What Became Closer To The Paper

| Paper Method Component | Previous Gap | Current Improvement |
|---|---|---|
| Autoregressive cognitive sandbox | World transition existed but was not directly trained | Added contrastive `train_world_step` and `world_loss` training logs |
| Shadow adversarial training | Mostly replaced one tool with a sensitive tool | Added injection insertion, secret leakage, policy/logic violation, attacker exfiltration variants |
| Multimodal evaluation | Only interface and ad-hoc images | Added CyberSecEval3 VPI dataset download, conversion, Qwen-VL evaluation, CSV/MD result tables |
| Online action gateway | Mostly full-plan judging | Added `OnlineWAMIGateway` with tool observation, memory, subgoal, and state updates per step |
| Result reproducibility | Terminal-only output | Saved VPI results to CSV/Markdown and created reusable scripts |

## Remaining Differences From A Strict Original-Paper Reproduction

| Difference | Why It Remains |
|---|---|
| Original WAMI latent encoder is unknown | The paper does not provide released weights/source for the exact latent encoder; current implementation uses hashing + optional Qwen-VL/CLIP adapters |
| Original world model architecture is unknown | Current world model is a lightweight numpy implementation with contrastive training, not guaranteed to match paper hidden layers/loss exactly |
| TDG is still parser-based | It handles ReAct/tool-call traces and variable dependencies, but not a full dynamic data-flow engine |
| CyberSecEval3 VPI is adapted | The dataset has images and visual prompt injection cases, but not native WAMI tool trajectories; we convert it into paired benign/attack plans |
| Official baseline coverage remains incomplete | Some baselines lack runnable official code or require heavy Docker/GPU/model environments |

## Files

- `scripts/download_cyberseceval3_vpi.py`
- `scripts/convert_cyberseceval3_vpi_to_wami.py`
- `scripts/run_cyberseceval3_vpi_wami_qwenvl.py`
- `data/cyberseceval3_vpi_wami.jsonl`
- `data/cyberseceval3_vpi_qwenvl_100.csv`
- `data/cyberseceval3_vpi_qwenvl_100.md`
- `wami_injecagent_worldtrained_e3.npz`
- `wami_bipia_worldtrained_e3.npz`
