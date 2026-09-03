# AgentDojo Official Detector on WAMI Datasets

| Dataset | Method | Input | IR | FPR | ACC | Latency ms | N | Attack | Benign | Status |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| BIPIA | AgentDojo official TransformersBasedPIDetector | tool_outputs | 78.0% | 70.0% | 54.0% | 104.3 | 100 | 50 | 50 | official-detector-on-wami-datasets |
| InjecAgent | AgentDojo official TransformersBasedPIDetector | tool_outputs | 74.0% | 64.0% | 55.0% | 121.9 | 100 | 50 | 50 | official-detector-on-wami-datasets |
| AgentDojo | AgentDojo official TransformersBasedPIDetector | tool_outputs | 8.0% | 6.0% | 51.0% | 46.3 | 100 | 50 | 50 | official-detector-on-wami-datasets |

## Interpretation

- This is not the full AgentDojo agent harness; it is the official AgentDojo prompt-injection detector applied to the same datasets as WAMI.
- `tool_outputs` is the closest adapter because AgentDojo places this detector after tool outputs.
- The detector network, threshold rule, and labels are unchanged from AgentDojo.
