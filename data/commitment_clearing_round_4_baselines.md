# Commitment Clearing Round 4: Baseline Reproduction Audit

This round clears the baseline-reporting gap by consolidating the existing
official, method-level, proxy, and missing-baseline results into one auditable
table. It does not claim strict official reproduction where the required model
weights, harness, or runtime are missing.

## Baseline Status Summary

| Baseline | Current Level | Runnable Locally | Main Evidence | What Can Be Claimed |
|---|---|---:|---|---|
| Erase-and-Check | method-level / official-code inspired | yes | `data/table2_official_erase_check_qwen_max_raw_random100.md` | Qwen-backed Erase-and-Check style defense evaluated on WAMI-converted datasets |
| SmoothLLM | method-level / partial official algorithm | yes | `data/smoothllm_qwen_turbo_judge_random50.md`; `data/smoothllm_wami_datasets_qwen05b_5x5.md` | SmoothLLM-style perturbation and official perturbation algorithm variants tested |
| WebAgentGuard | method-level | yes | `data/webagentguard_paper_method_sample.md` | Parallel guard-agent idea tested with Qwen backend; not official released code |
| GuardReasoner-VL | proxy / repo inspected | partial | `external/GuardReasoner-VL`; `data/table1_proxy_baselines.md` | Repository present; local proxy only on WAMI data |
| ToolEmu-Sandbox | import/proxy only | partial | `data/official_baseline_status.md`; `scripts/run_official_toolemu.py` | Official code import status known; strict run needs ToolEmu runtime and API/model setup |
| Llama-Guard 3 8B | not reproduced | no | none | Do not claim local reproduction unless model is downloaded and run |
| ToolBench/AgentBench Table 4 | proxy only | partial | `data/table4_capability_proxy.md`; `data/toolbench_agentbench_official_harness_status.md` | Capability-retention proxy only, not official success-rate harness |

## Numeric Results Already Run

### Erase-and-Check

Source: `data/table2_official_erase_check_qwen_max_raw_random100.md`

| Dataset | Method | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| InjecAgent | Erase-and-Check official-style qwen-max | 96.0% | 0.0% | 97.0% | 2348.7 | 67 |
| BIPIA | Erase-and-Check official-style qwen-max | 64.0% | 0.0% | 82.0% | 2767.3 | 100 |

Interpretation: Erase-and-Check is conservative and keeps FPR low, but its BIPIA
IR is lower than WAMI in the local runs.

### SmoothLLM

Source: `data/smoothllm_qwen_turbo_judge_random50.md`

| Dataset | Method | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| InjecAgent | SmoothLLM-style perturbation + qwen-turbo judge | 100.0% | 58.8% | 76.2% | 2066.2 | 42 |
| BIPIA | SmoothLLM-style perturbation + qwen-turbo judge | 72.0% | 8.0% | 82.0% | 2068.8 | 50 |

Source: `data/smoothllm_wami_datasets_qwen05b_5x5.md`

| Dataset | Method | IR | ASR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|---:|
| InjecAgent | SmoothLLM official algorithm + local target model | 0.0% | 100.0% | 0.0% | 50.0% | 1040.5 | 10 |
| BIPIA | SmoothLLM official algorithm + local target model | 0.0% | 100.0% | 0.0% | 50.0% | 1278.6 | 10 |

Interpretation: the Qwen-judge variant detects many attacks but can over-block.
The small local-target official-algorithm run failed to intercept attacks,
likely because the local target/judge setup is not equivalent to the official
SmoothLLM experiment stack.

### WebAgentGuard

Source: `data/webagentguard_paper_method_sample.md`

| Dataset | Method | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| BIPIA | WebAgentGuard paper-method qwen-max | 100.0% | 40.0% | 80.0% | 3597.1 | 10 |
| InjecAgent | WebAgentGuard paper-method qwen-max | 100.0% | 20.0% | 90.0% | 3885.9 | 10 |

Interpretation: guard-agent judging can catch attacks, but the small sample has
high FPR and high API latency.

### Table 1 Proxy Baselines

Source: `data/table1_proxy_baselines.md`

| Dataset | Defense Method | Local IR | Local FPR | ACC | Latency ms | Level |
|---|---|---:|---:|---:|---:|---|
| BIPIA | GuardReasoner-VL proxy | 100.0% | 0.0% | 100.0% | 0.011 | proxy baseline, not official |
| BIPIA | WebAgentGuard proxy | 100.0% | 3.0% | 98.5% | 0.072 | proxy baseline, not official |
| BIPIA | BookAgent proxy | 100.0% | 3.0% | 98.5% | 0.070 | proxy baseline, not official |
| InjecAgent | GuardReasoner-VL proxy | 14.5% | 0.0% | 57.4% | 0.003 | proxy baseline, not official |
| InjecAgent | WebAgentGuard proxy | 92.0% | 0.0% | 96.0% | 0.062 | proxy baseline, not official |
| InjecAgent | BookAgent proxy | 14.5% | 0.0% | 57.4% | 0.047 | proxy baseline, not official |

Interpretation: these rows are useful for trend sanity checks only. They should
not be described as official reproductions of GuardReasoner-VL/WebAgentGuard/
BookAgent.

### ToolBench / AgentBench Table 4

Source: `data/table4_capability_proxy.md`

| Source | System | ToolBench SR | AgentBench SR | ToolBench Retention | AgentBench Retention |
|---|---|---:|---:|---:|---:|
| paper_table4 | No Defense | 68.5% | 71.2% | 100.0% | 100.0% |
| paper_table4 | + Erase-and-Check | 55.1% | 57.6% | 80.4% | 80.9% |
| paper_table4 | + ToolEmu-Sandbox | 54.8% | 56.9% | 80.0% | 79.9% |
| paper_table4 | + Llama-Guard 3 | 61.4% | 63.8% | 89.6% | 89.6% |
| paper_table4 | + WAMI (Ours) | 68.0% | 70.6% | 99.3% | 99.2% |
| local_proxy | + WAMI (Ours, proxy) | 68.1% | 69.5% | 99.4% | 97.7% |

Interpretation: local Table 4 is a capability-retention proxy. Strict Table 4
still requires official ToolBench/AgentBench agent harnesses, model execution,
tool logs, and scoring.

## Recommended Paper Wording

Use this wording style:

```text
For baselines without fully reproducible released harnesses or matching model
weights, we report method-level or proxy reproductions and mark their strictness
explicitly. Official-equivalent reproduction is claimed only when the official
runtime, model, and benchmark protocol are available.
```

Do not write:

```text
We strictly reproduce all baselines.
```

That would overstate the current repository.
