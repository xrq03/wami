# WAMI Runtime Action Replay

This replay evaluates WAMI as an action-level runtime gateway instead of an input-level prompt filter.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| BIPIA | WAMI runtime action replay | 100.0% | 0.0% | 100.0% | 1.403 | 2400 | 1200 | 1200 | runtime-replay-action-level |
| InjecAgent | WAMI runtime action replay | 93.4% | 0.0% | 96.7% | 1.029 | 4233 | 2108 | 2125 | runtime-replay-action-level |
| AgentDojo | WAMI runtime action replay | 80.4% | 1.2% | 82.8% | 3.643 | 653 | 567 | 86 | runtime-replay-action-level |

## Protocol

- Observation/read/search steps are allowed so prompt injection can enter the agent context.
- WAMI is invoked only before later non-observation actions in the replayed trajectory.
- This shows whether WAMI can block unsafe action transitions after untrusted content has already been observed.
