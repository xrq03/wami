| Dataset | Method | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| InjecAgent | Erase-and-Check local qwen2.5 | 90.6% | 0.0% | 90.6% | 373.2 | 2125 |
| InjecAgent | WAMI paper-faithful replay | 86.8% | 5.9% | 90.5% | 42.0 | 2125 |
| BIPIA | Erase-and-Check local qwen2.5 | 18.8% | 0.1% | 59.3% | 530.8 | 2400 |
| BIPIA | WAMI paper-faithful replay | 99.8% | 0.5% | 99.6% | 38.8 | 2400 |
| AgentDojo | Erase-and-Check local qwen2.5 | 65.2% | 8.1% | 66.2% | 323.6 | 2408 |
| AgentDojo | WAMI paper-faithful replay | 97.2% | 9.3% | 96.3% | 37.2 | 2408 |

| Dataset | WAMI IR - E&C IR | WAMI FPR - E&C FPR | WAMI ACC - E&C ACC | Speedup |
|---|---:|---:|---:|---:|
| InjecAgent | -3.8 pp | +5.9 pp | -0.1 pp | 8.9x faster |
| BIPIA | +81.0 pp | +0.4 pp | +40.3 pp | 13.7x faster |
| AgentDojo | +32.0 pp | +1.2 pp | +30.1 pp | 8.7x faster |

Notes:
- E&C means Erase-and-Check.
- Positive IR/ACC deltas favor WAMI.
- Negative FPR deltas favor WAMI; here WAMI trades slightly higher FPR for much higher IR on BIPIA and AgentDojo.
- WAMI is consistently faster because it uses the local action-level scoring gateway rather than repeated LLM judge calls.
