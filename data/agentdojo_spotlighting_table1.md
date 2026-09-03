# AgentDojo spotlighting Table 1 replacement

This replaces BookAgent with AgentDojo's open-source `spotlighting_with_delimiting` defense idea. It is adapted to the local converted trajectory format rather than run inside the full AgentDojo agent harness.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | Level |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| BIPIA | AgentDojo spotlighting_with_delimiting | 100.0% | 0.0% | 100.0% | 0.064 | 2400 | 1200 | 1200 | AgentDojo official defense idea adapted to converted trajectories |
| InjecAgent | AgentDojo spotlighting_with_delimiting | 14.5% | 0.0% | 57.4% | 0.032 | 4233 | 2108 | 2125 | AgentDojo official defense idea adapted to converted trajectories |
| AgentDojo | AgentDojo spotlighting_with_delimiting | 83.6% | 0.0% | 85.8% | 0.046 | 653 | 567 | 86 | AgentDojo official defense idea adapted to converted trajectories |
