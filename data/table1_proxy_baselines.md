# Table 1 proxy baseline reproduction

GuardReasoner-VL official repository was downloaded to `external/GuardReasoner-VL`, but its released evaluation code targets general harmfulness/VL guard benchmarks rather than BIPIA/InjecAgent. WebAgentGuard and the Table-1 BookAgent implementation could not be located as official runnable code. Therefore the three baseline rows below are proxy reproductions of the defense paradigms described in the paper, not official numbers.

| Dataset | Defense Method | Paper IR | Local IR | Delta IR | Paper FPR | Local FPR | Delta FPR | ACC | Latency ms | Level |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| BIPIA | GuardReasoner-VL proxy | 62.5% | 100.0% | +37.5 pp | 6.2% | 0.0% | -6.2 pp | 100.0% | 0.011 | proxy baseline, not official |
| BIPIA | WebAgentGuard proxy | 84.7% | 100.0% | +15.3 pp | 28.5% | 3.0% | -25.5 pp | 98.5% | 0.072 | proxy baseline, not official |
| BIPIA | BookAgent proxy | 86.3% | 100.0% | +13.7 pp | 14.8% | 3.0% | -11.8 pp | 98.5% | 0.070 | proxy baseline, not official |
| BIPIA | WAMI (local) | 88.9% | 100.0% | +11.1 pp | 1.5% | 0.6% | -0.9 pp | 99.7% | 1.528 | local WAMI |
| InjecAgent | GuardReasoner-VL proxy | 38.4% | 14.5% | -23.9 pp | 5.8% | 0.0% | -5.8 pp | 57.4% | 0.003 | proxy baseline, not official |
| InjecAgent | WebAgentGuard proxy | 91.2% | 92.0% | +0.8 pp | 36.4% | 0.0% | -36.4 pp | 96.0% | 0.062 | proxy baseline, not official |
| InjecAgent | BookAgent proxy | 85.5% | 14.5% | -71.0 pp | 17.2% | 0.0% | -17.2 pp | 57.4% | 0.047 | proxy baseline, not official |
| InjecAgent | WAMI (local) | 90.3% | 96.1% | +5.8 pp | 1.2% | 0.0% | -1.2 pp | 98.0% | 1.191 | local WAMI |

## Interpretation

- GuardReasoner-VL proxy only checks direct injection/harmful text markers, so it misses many tool-side hijacks.
- WebAgentGuard proxy blocks high-risk API calls conservatively, which tends to raise both IR and FPR.
- BookAgent proxy verifies the trajectory and blocks high-risk actions after untrusted steps or attacker-controlled arguments.
- These rows are useful for sanity checking Table 1 trends, but they should not be described as official baseline reproductions.
