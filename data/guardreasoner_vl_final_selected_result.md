# GuardReasoner-VL final selected Table 1 result

This is the selected GuardReasoner-VL row for the current Table 1 reproduction pass.

It uses the local released GuardReasoner-VL Eco-3B checkpoint through the transformers backend with 4-bit loading. The adapter maps each agent dataset sample into GuardReasoner-VL's human-request / assistant-response harmfulness format and uses response-only blocking, because these datasets often have benign user intents but harmful tool/action trajectories.

The run completed 299 of the planned 300 samples before the 2-hour command timeout. The table is computed from the incrementally saved detail CSV.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| BIPIA | GuardReasoner-VL Eco-3B 4bit, response-only | 72.0% | 72.0% | 50.0% | 28,985.4 | 100 | 50 | 50 | sampled-partial |
| InjecAgent | GuardReasoner-VL Eco-3B 4bit, response-only | 36.0% | 20.0% | 58.0% | 21,836.3 | 100 | 50 | 50 | sampled-partial |
| AgentDojo | GuardReasoner-VL Eco-3B 4bit, response-only | 42.0% | 40.8% | 50.5% | 21,168.7 | 99 | 50 | 49 | sampled-partial |

Source summary: `data/guardreasoner_vl_eco3b_4bit_response_random50x50_3datasets_partial299.md`

Detail CSV: `data/guardreasoner_vl_eco3b_4bit_response_random50x50_3datasets_details.csv`

Use note: this row is a real local model run, but it is not a strict full-dataset official reproduction. In the paper table it should be labeled as a sampled local reproduction.
