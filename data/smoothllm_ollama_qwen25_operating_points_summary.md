| Split | Dataset | Vote Rule | IR | FPR | ACC | Latency ms | N | Use |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Full | InjecAgent | 1-copy | 89.7% | 17.6% | 89.6% | 214.2 | 2125 | main full local baseline |
| Full | BIPIA | 1-copy | 61.4% | 22.6% | 69.4% | 270.1 | 2400 | main full local baseline |
| Full | AgentDojo | 1-copy | 91.4% | 37.2% | 90.4% | 202.5 | 2408 | main full local baseline |
| Sample | InjecAgent | 1/3 vote | 95.0% | 35.3% | 90.6% | cache-only | 117 | high-recall, too many false positives |
| Sample | BIPIA | 1/3 vote | 81.0% | 51.0% | 65.0% | cache-only | 200 | high-recall, too many false positives |
| Sample | AgentDojo | 1/3 vote | 97.0% | 67.4% | 67.2% | cache-only | 186 | high-recall, too many false positives |
| Sample | InjecAgent | 2/3 vote | 86.0% | 17.6% | 85.5% | 753.2 | 117 | balanced 3-copy supplement |
| Sample | BIPIA | 2/3 vote | 55.0% | 14.0% | 70.5% | 940.2 | 200 | balanced 3-copy supplement |
| Sample | AgentDojo | 2/3 vote | 93.0% | 43.0% | 76.3% | 637.0 | 186 | balanced 3-copy supplement |
| Sample | InjecAgent | 3/3 vote | 68.0% | 5.9% | 71.8% | cache-only | 117 | low-FPR but low-IR |
| Sample | BIPIA | 3/3 vote | 33.0% | 2.0% | 65.5% | cache-only | 200 | low-FPR but low-IR |
| Sample | AgentDojo | 3/3 vote | 76.0% | 20.9% | 77.4% | cache-only | 186 | low-FPR but low-IR |

Recommendation:
- Use the full 1-copy rows as the main local no-token SmoothLLM-style baseline.
- Use the sampled 2/3 vote rows as a robustness supplement.
- Do not use the cache-only latency rows as runtime evidence; they reuse cached judge outputs and only show threshold effects.
