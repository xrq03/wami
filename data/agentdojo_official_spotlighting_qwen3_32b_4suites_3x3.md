# AgentDojo Official Harness Table 1 Replacement

| Suite | Defense | Attack | Model | Security Rate | ASR | Utility | Injection Utility | N | Latency ms | Status |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|

## WAMI-style Metrics

| Suite | Defense | IR | FPR proxy | ACC proxy | Attack N | Benign N | Latency ms |
|---|---|---:|---:|---:|---:|---:|---:|
| workspace | spotlighting_with_delimiting | 0.0% | 66.7% | 16.7% | 9 | 9 | 10880.0 |
| travel | spotlighting_with_delimiting | 22.2% | 55.6% | 33.3% | 9 | 9 | 15519.9 |
| banking | spotlighting_with_delimiting | 33.3% | 77.8% | 27.8% | 9 | 9 | 9607.3 |
| slack | spotlighting_with_delimiting | 55.6% | 22.2% | 66.7% | 9 | 9 | 9579.7 |

## AgentDojo Native Metrics

| Suite | Defense | Attack | Model | Security Rate | ASR | Utility | Injection Utility | N | Latency ms | Status |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| workspace | spotlighting_with_delimiting | injecagent | qwen3-32b | 0.0% | 100.0% | 33.3% | 100.0% | 9 | 10880.0 | official-harness |
| travel | spotlighting_with_delimiting | injecagent | qwen3-32b | 22.2% | 77.8% | 44.4% | 100.0% | 9 | 15519.9 | official-harness |
| banking | spotlighting_with_delimiting | injecagent | qwen3-32b | 33.3% | 66.7% | 22.2% | 66.7% | 9 | 9607.3 | official-harness |
| slack | spotlighting_with_delimiting | injecagent | qwen3-32b | 55.6% | 44.4% | 77.8% | 100.0% | 9 | 9579.7 | official-harness |

## Notes

- Security Rate is AgentDojo's official `security_results` success rate; higher means better defense.
- ASR is `1 - Security Rate`.
- WAMI-style IR is mapped from Security Rate.
- FPR proxy is `1 - Utility Rate`; this is a task-level false-positive proxy, not a per-sample classifier FPR.
- ACC proxy combines attack security successes and benign utility successes.
- This is an official AgentDojo harness run, not the converted-trajectory adaptation.
