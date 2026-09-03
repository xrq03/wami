# Qwen2.5 Local Planner Boosted Full-Dataset Results

Boosted setting: `--planner-retries 2 --bootstrap-first-observation`; InjecAgent uses `--max-steps 4`, BIPIA uses `--max-steps 3`, AgentDojo uses `--max-steps 6`.

## Boosted Full Results

| Dataset | N | Attack | Benign | IR | FPR | ACC | Planner Risk Rate | WAMI Action Block Rate | Avg latency ms | Avg steps | CSV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| InjecAgent | 4233 | 2108 | 2125 | 48.0% | 0.0% | 74.1% | 52.8% | 90.8% | 4556.1 | 2.45 | `data/qwen25_7b_ollama_boost_injecagent_full.csv` |
| BIPIA | 2400 | 1200 | 1200 | 91.4% | 0.5% | 95.5% | 91.4% | 100.0% | 2538.9 | 1.26 | `data/qwen25_7b_ollama_boost_bipia_full.csv` |
| AgentDojo | 653 | 567 | 86 | 35.8% | 9.3% | 43.0% | 37.4% | 95.8% | 3425.3 | 2.44 | `data/qwen25_7b_ollama_boost_agentdojo_full.csv` |

## Baseline vs Boosted

| Dataset | Baseline IR | Boosted IR | Delta IR | Baseline FPR | Boosted FPR | Delta FPR | Baseline Planner Risk | Boosted Planner Risk | Baseline WAMI Block | Boosted WAMI Block |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| InjecAgent | 39.0% | 48.0% | 9.0% | 0.0% | 0.0% | 0.0% | 43.7% | 52.8% | 89.3% | 90.8% |
| BIPIA | 82.7% | 91.4% | 8.8% | 0.1% | 0.5% | 0.4% | 82.7% | 91.4% | 100.0% | 100.0% |
| AgentDojo | 21.3% | 35.8% | 14.5% | 3.5% | 9.3% | 5.8% | 22.9% | 37.4% | 93.1% | 95.8% |

## Interpretation

- Boosting mainly increases `Planner Risk Rate`, meaning the local Qwen2.5 planner more often emits a dangerous action instead of stopping early or answering directly.
- `WAMI Action Block Rate` remains high. This means once dangerous actions enter WAMI, WAMI still catches most/all of them.
- BIPIA benefits the most: boosted full IR reaches 91.4% with 0.5% FPR and 100.0% WAMI action blocking.
- InjecAgent improves but remains limited by planner behavior on the full dataset.
- AgentDojo improves IR but also raises FPR; report it as a stronger stress setting, not the cleanest operating point.
