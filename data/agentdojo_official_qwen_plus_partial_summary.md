# AgentDojo Official Partial Log Summary

| Pipeline | Suite | IR | FPR proxy | ACC proxy | Attack blocked / N | Benign success / N | Avg duration s | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| qwen-max-spotlighting_with_delimiting | banking | 0.0% | 50.0% | 33.3% | 0/1 | 1/2 | 10.8 | partial-official-logs |
| qwen-max-spotlighting_with_delimiting | slack | 0.0% | 0.0% | 50.0% | 0/1 | 1/1 | 4.8 | partial-official-logs |
| qwen-max-spotlighting_with_delimiting | travel | 0.0% | 0.0% | 25.0% | 0/9 | 3/3 | 12.2 | partial-official-logs |
| qwen-max-spotlighting_with_delimiting | workspace | 0.0% | 0.0% | 25.0% | 0/9 | 3/3 | 8.4 | partial-official-logs |
| qwen-max-transformers_pi_detector | banking | 0.0% | 0.0% | 50.0% | 0/1 | 1/1 | 10.2 | partial-official-logs |
| qwen-max-transformers_pi_detector | slack | 0.0% | 0.0% | 50.0% | 0/1 | 1/1 | 4.3 | partial-official-logs |
| qwen-max-transformers_pi_detector | travel | 0.0% | 0.0% | 50.0% | 0/2 | 2/2 | 6.5 | partial-official-logs |
| qwen-max-transformers_pi_detector | workspace | 0.0% | 0.0% | 50.0% | 0/1 | 1/1 | 6.0 | partial-official-logs |
| qwen-plus-2025-09-11-spotlighting_with_delimiting | banking | 33.3% | 33.3% | 41.7% | 3/9 | 2/3 | 8.0 | partial-official-logs |
| qwen-plus-2025-09-11-spotlighting_with_delimiting | slack | 11.1% | 0.0% | 33.3% | 1/9 | 3/3 | 9.2 | partial-official-logs |
| qwen-plus-2025-09-11-spotlighting_with_delimiting | travel | 0.0% | 33.3% | 16.7% | 0/9 | 2/3 | 9.8 | partial-official-logs |
| qwen-plus-2025-09-11-spotlighting_with_delimiting | workspace | 0.0% | 0.0% | 25.0% | 0/9 | 3/3 | 7.0 | partial-official-logs |
| qwen-plus-2025-09-11-transformers_pi_detector | banking | 0.0% | 100.0% | 0.0% | 0/1 | 0/1 | 3.8 | partial-official-logs |
| qwen-plus-2025-09-11-transformers_pi_detector | slack | 0.0% | 0.0% | 50.0% | 0/1 | 1/1 | 11.1 | partial-official-logs |
| qwen-plus-2025-09-11-transformers_pi_detector | travel | 0.0% | 100.0% | 0.0% | 0/1 | 0/1 | 5.1 | partial-official-logs |
| qwen-plus-2025-09-11-transformers_pi_detector | workspace | 0.0% | 33.3% | 33.3% | 0/3 | 2/3 | 16.5 | partial-official-logs |

## Notes

- These rows are computed from completed AgentDojo official JSON logs only.
- IR is AgentDojo `security=True` rate on attack runs.
- FPR proxy is `1 - utility` on no-attack runs.
- Runs may be partial if the API quota interrupted a larger benchmark.
