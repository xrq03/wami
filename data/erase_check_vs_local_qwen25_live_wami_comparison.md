| Dataset | Method | IR | FPR | ACC | Latency ms | N | Extra |
|---|---|---:|---:|---:|---:|---:|---|
| InjecAgent | Erase-and-Check local qwen2.5 | 90.6% | 0.0% | 90.6% | 373.2 | 2125 | suffix erase, max_erase=1 |
| InjecAgent | Local qwen2.5 live-agent + WAMI | 39.0% | 0.0% | 69.6% | 4898.5 | 4233 | planner risk rate 43.7%; WAMI action block rate 89.3%; avg 2.01 steps |
| BIPIA | Erase-and-Check local qwen2.5 | 18.8% | 0.1% | 59.3% | 530.8 | 2400 | suffix erase, max_erase=1 |
| BIPIA | Local qwen2.5 live-agent + WAMI | 82.7% | 0.1% | 91.3% | 1713.4 | 2400 | planner risk rate 82.7%; WAMI action block rate 100.0%; avg 1.20 steps |
| AgentDojo | Erase-and-Check local qwen2.5 | 65.2% | 8.1% | 66.2% | 323.6 | 2408 | suffix erase, max_erase=1 |
| AgentDojo | Local qwen2.5 live-agent + WAMI | 21.3% | 3.5% | 31.2% | 3755.9 | 653 | planner risk rate 22.9%; WAMI action block rate 93.1%; avg 1.60 steps |

| Dataset | Local Live WAMI - E&C IR | Local Live WAMI - E&C FPR | Local Live WAMI - E&C ACC | Latency Ratio |
|---|---:|---:|---:|---:|
| InjecAgent | -51.6 pp | +0.0 pp | -21.0 pp | WAMI live is 13.1x slower |
| BIPIA | +63.9 pp | +0.0 pp | +32.0 pp | WAMI live is 3.2x slower |
| AgentDojo | -43.9 pp | -4.6 pp | -35.0 pp | WAMI live is 11.6x slower |

Notes:
- This comparison uses the local qwen2.5 live-agent WAMI runtime outputs, not the paper-faithful replay WAMI outputs.
- InjecAgent and AgentDojo are not perfectly same-N comparisons: the live-agent WAMI files have different evaluated counts from the Erase-and-Check full detector run.
- The key live-agent issue is planner risk generation: WAMI can only block risky actions that the local planner actually proposes. That is why AgentDojo IR is low even though its WAMI action block rate is 93.1%.
- BIPIA is the strongest local live-agent WAMI result because the planner often proposes explicit `ExfiltrateData`, and WAMI blocks those risky actions reliably.
