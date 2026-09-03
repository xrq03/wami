# WAMI Runtime Action Replay

This replay evaluates WAMI as an action-level runtime gateway instead of an input-level prompt filter.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| BIPIA | WAMI runtime action replay | 41.1% | 0.0% | 70.5% | 1.381 | 2400 | 1200 | 1200 | runtime-replay-action-level |
| InjecAgent | WAMI runtime action replay | 48.6% | 0.0% | 74.4% | 1.091 | 4233 | 2108 | 2125 | runtime-replay-action-level |
| AgentDojo | WAMI runtime action replay | 44.6% | 18.6% | 49.5% | 3.230 | 653 | 567 | 86 | runtime-replay-action-level |

## Protocol

- Observation/read/search steps are allowed so prompt injection can enter the agent context.
- WAMI is invoked only before later non-observation actions in the replayed trajectory.
- This shows whether WAMI can block unsafe action transitions after untrusted content has already been observed.
