# WebAgentGuard No-API Method-Level Baseline

This is a no-API method-level reproduction of WebAgentGuard's parallel pre-execution guard idea. It is not an official checkpoint reproduction.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| BIPIA | WebAgentGuard no-API method-level | 100.0% | 3.0% | 98.5% | 0.062 | 2400 | 1200 | 1200 | method-level-noapi |
| InjecAgent | WebAgentGuard no-API method-level | 98.4% | 0.0% | 99.2% | 0.047 | 4233 | 2108 | 2125 | method-level-noapi |
| AgentDojo | WebAgentGuard no-API method-level | 83.6% | 0.0% | 85.8% | 0.060 | 653 | 567 | 86 | method-level-noapi |

## Strictness

- This row is useful as a no-API baseline for Table 1 development.
- It should remain marked as method-level unless official WebAgentGuard weights/runtime are provided.
