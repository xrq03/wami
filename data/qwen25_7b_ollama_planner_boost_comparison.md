# Qwen2.5 Local Planner Boost Comparison

| Run | N | IR | FPR | ACC | Planner Risk Rate | WAMI Action Block Rate | Avg latency ms | Avg steps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| InjecAgent baseline 50x50 | 100 | 76.0% | 0.0% | 88.0% | 76.0% | 100.0% | 5656.2 | 1.97 |
| InjecAgent boosted 50x50 | 100 | 88.0% | 0.0% | 94.0% | 88.0% | 100.0% | 5085.6 | 2.27 |
| BIPIA baseline 50x50 | 100 | 80.0% | 0.0% | 90.0% | 80.0% | 100.0% | 2063.6 | 1.50 |
| BIPIA boosted 50x50 | 100 | 100.0% | 0.0% | 100.0% | 100.0% | 100.0% | 9863.9 | 2.09 |
| AgentDojo baseline 50x50 | 100 | 46.0% | 4.0% | 71.0% | 46.0% | 100.0% | 3765.7 | 1.81 |
| AgentDojo boosted 50x50 | 100 | 58.0% | 6.0% | 76.0% | 60.0% | 96.7% | 3434.5 | 2.52 |

Boosted setting uses --planner-retries 2; InjecAgent and AgentDojo also use --bootstrap-first-observation in this comparison. This improves dangerous action generation without using labels, but can increase latency and AgentDojo FPR.
