# Commitment Clearing Round 2

This round clears the memory/resource overhead experiment.

## Resource Profile

Evidence files:

- `scripts/run_wami_resource_profile.py`
- `data/wami_resource_profile.md`
- `data/wami_resource_profile.csv`

Command:

```text
uv run --with numpy python scripts\run_wami_resource_profile.py --limit 1000
```

Results:

| Dataset | N | Model MB | Load ms | Avg ms | P50 ms | P95 ms | Peak alloc MB | IR | FPR | ACC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| InjecAgent | 1000 | 0.443 | 24.778 | 8.660 | 8.385 | 11.727 | 1.760 | 100.0% | 0.0% | 100.0% |
| BIPIA | 1000 | 0.443 | 4.520 | 13.483 | 11.389 | 24.893 | 0.660 | 100.0% | 2.2% | 98.9% |
| AgentDojo | 653 | 0.443 | 4.366 | 16.481 | 11.314 | 41.913 | 0.660 | 89.8% | 1.2% | 91.0% |

Conclusion: the non-API WAMI implementation is lightweight. The saved numpy
model is under 0.5 MB, load time is in the single-digit to tens-of-milliseconds
range, and per-sample evaluation is roughly 9-16 ms on the current machine.

The Windows RSS delta columns in the raw profile are zero in this run because
the model is very small and the process working-set measurement did not show a
stable page-level increase between checkpoints. The more reliable memory signal
for this implementation is therefore model file size plus Python peak allocation.
