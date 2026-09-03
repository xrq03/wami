# WAMI Memory And Resource Profile

- Limit per dataset: `1000`
- RSS is Windows process working set measured inside the same process.
- Python peak allocation is measured by `tracemalloc` during model load and evaluation.

| Dataset | N | Model MB | Load ms | Avg ms | P50 ms | P95 ms | Peak alloc MB | RSS load delta MB | RSS eval delta MB | IR | FPR | ACC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| InjecAgent | 1000 | 0.443 | 41.907 | 11.201 | 10.657 | 17.375 | 1.759 | 0.000 | 0.000 | 100.0% | 0.0% | 100.0% |
| BIPIA | 1000 | 0.443 | 5.165 | 16.988 | 15.388 | 33.294 | 0.660 | 0.000 | 0.000 | 100.0% | 1.2% | 99.4% |
| AgentDojo | 653 | 0.443 | 4.945 | 21.327 | 15.222 | 55.499 | 0.660 | 0.000 | 0.000 | 82.2% | 1.2% | 84.4% |
