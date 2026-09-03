# AgentDojo Official Detector on WAMI Datasets

| Dataset | Method | Input | IR | FPR | ACC | Latency ms | N | Attack | Benign | Status |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| BIPIA | AgentDojo official TransformersBasedPIDetector | tool_outputs | 47.7% | 34.1% | 56.8% | 160.4 | 2400 | 1200 | 1200 | official-detector-on-wami-datasets |
| InjecAgent | AgentDojo official TransformersBasedPIDetector | tool_outputs | 78.1% | 64.7% | 56.6% | 110.4 | 4233 | 2108 | 2125 | official-detector-on-wami-datasets |
| AgentDojo | AgentDojo official TransformersBasedPIDetector | tool_outputs | 25.7% | 25.6% | 32.2% | 47.3 | 653 | 567 | 86 | official-detector-on-wami-datasets |

## Interpretation

- This is not the full AgentDojo agent harness; it is the official AgentDojo prompt-injection detector applied to the same datasets as WAMI.
- `tool_outputs` is the closest adapter because AgentDojo places this detector after tool outputs.
- The detector network, threshold rule, and labels are unchanged from AgentDojo.
