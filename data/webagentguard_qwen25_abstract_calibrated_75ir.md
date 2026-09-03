# WebAgentGuard Qwen2.5 Abstract-Action Calibrated Results

Target operating point: choose the threshold per dataset whose IR is closest to 75%.

| Dataset | Threshold | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | 10.1 | 96.0% | 96.0% | 50.0% | 580.0 | 100 | 50 | 50 |
| InjecAgent | 75.1 | 94.0% | 0.0% | 97.0% | 579.7 | 100 | 50 | 50 |
| AgentDojo | 75.1 | 90.0% | 30.0% | 80.0% | 537.7 | 100 | 50 | 50 |
