# Lightweight prompt-injection detector Table 1 replacement

This is a lightweight open-source replacement candidate for the non-matching BookAgent baseline. It uses the `prompt-injection-defense` package rather than AgentDojo's large Transformers detector.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | Input |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| BIPIA | prompt-injection-defense lightweight detector | 0.0% | 0.0% | 50.0% | 1166.002 | 20 | 10 | 10 | intent_plan |
| InjecAgent | prompt-injection-defense lightweight detector | 0.0% | 0.0% | 50.0% | 1359.147 | 20 | 10 | 10 | intent_plan |
| AgentDojo | prompt-injection-defense lightweight detector | 0.0% | 0.0% | 50.0% | 702.266 | 20 | 10 | 10 | intent_plan |
