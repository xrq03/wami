# Clean Table 1 For Report

This version separates missing official baselines, method-level baselines, local official detectors, WAMI replay, and small live-agent evidence. WebAgentGuard-style no-API is intentionally excluded from the main table because it is too rule-like and should stay in appendix.

| Dataset | Method | IR | FPR | ACC | Latency ms | Level | Source | Note |
|---|---|---:|---:|---:|---:|---|---|---|
| BIPIA | GuardReasoner-VL |  |  |  |  | missing-official | `` | Official agent-trajectory adapter/checkpoint not available. |
| BIPIA | BookAgent-style Constraint Verifier | 92.8% | 0.0% | 96.4% | 0.101 | method-level | `data/bookagent_constraint_verifier_full.csv` | BookAgent VAS/ICR/TCC safety constraints adapted to agent trajectories. |
| BIPIA | AgentDojo official PI detector | 47.7% | 34.1% | 56.8% | 160.436 | official-local-detector | `data/agentdojo_official_detector_wami_datasets_full.csv` | Official AgentDojo detector logic; WAMI-format tool-output adapter. |
| BIPIA | WAMI paper-faithful replay | 99.8% | 0.5% | 99.6% | 38.836 | main-replay | `data/paper_mine_ensemble_sourceaware_triplet_taua45_taub50_results.csv` | Main action-level replay result. |
| BIPIA | Live planner + WAMI | 40.0% | 0.0% | 70.0% | 2239.405 | live-agent-small | `data/live_planner_wami_bipia_qwen3_10x10_summary.csv` | Small qwen3-32b planner-only run; WAMI action block rate 100.0%. |
| InjecAgent | GuardReasoner-VL |  |  |  |  | missing-official | `` | Official agent-trajectory adapter/checkpoint not available. |
| InjecAgent | BookAgent-style Constraint Verifier | 69.7% | 0.0% | 84.9% | 0.064 | method-level | `data/bookagent_constraint_verifier_full.csv` | BookAgent VAS/ICR/TCC safety constraints adapted to agent trajectories. |
| InjecAgent | AgentDojo official PI detector | 78.1% | 64.7% | 56.6% | 110.419 | official-local-detector | `data/agentdojo_official_detector_wami_datasets_full.csv` | Official AgentDojo detector logic; WAMI-format tool-output adapter. |
| InjecAgent | WAMI paper-faithful replay | 86.8% | 5.9% | 90.5% | 41.971 | main-replay | `data/paper_mine_ensemble_sourceaware_triplet_taua45_taub50_results.csv` | Main action-level replay result. |
| InjecAgent | Live planner + WAMI | 90.0% | 0.0% | 95.0% | 2499.467 | live-agent-small | `data/live_planner_wami_injecagent_qwen3_10x10_summary.csv` | Small qwen3-32b planner-only run; WAMI action block rate 100.0%. |
| AgentDojo | GuardReasoner-VL |  |  |  |  | missing-official | `` | Official agent-trajectory adapter/checkpoint not available. |
| AgentDojo | BookAgent-style Constraint Verifier | 60.0% | 3.5% | 64.8% | 0.093 | method-level | `data/bookagent_constraint_verifier_full.csv` | BookAgent VAS/ICR/TCC safety constraints adapted to agent trajectories. |
| AgentDojo | AgentDojo official PI detector | 25.7% | 25.6% | 32.2% | 47.331 | official-local-detector | `data/agentdojo_official_detector_wami_datasets_full.csv` | Official AgentDojo detector logic; WAMI-format tool-output adapter. |
| AgentDojo | WAMI paper-faithful replay | 97.2% | 9.3% | 96.3% | 37.217 | main-replay | `data/paper_mine_triplet_slot_seed4071_e4_tau50_results.csv` | Main action-level replay result. |
| AgentDojo | Live planner + WAMI | 10.0% | 0.0% | 55.0% | 1983.117 | live-agent-small | `data/live_planner_wami_agentdojo_qwen3_10x10_summary.csv` | Small qwen3-32b planner-only run; WAMI action block rate 100.0%. |
