# Paper comparison summary

This table only includes results that have been actually produced in this workspace. WAMI uses the local reproduced framework; Erase-and-Check uses the official cloned code with a Qwen-compatible API; SmoothLLM rows are SmoothLLM-style perturbation plus Qwen judge, not a full official SmoothVLM reproduction.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | Input | Level |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| InjecAgent | WAMI (ours, full model) | 96.1% | 0.0% | 98.0% | 1.2 | 4233 | 2108 | 2125 | WAMI converted intent/plan/TDG | ours-full |
| BIPIA | WAMI (ours, full model) | 100.0% | 0.6% | 99.7% | 1.5 | 2400 | 1200 | 1200 | WAMI converted intent/plan/TDG | ours-full |
| AgentDojo | WAMI (ours, full model) | 86.2% | 2.3% | 87.7% | 1.7 | 653 | 567 | 86 | WAMI converted intent/plan/TDG | ours-full |
| InjecAgent | Erase-and-Check official (qwen-max) | 96.0% | 0.0% | 97.0% | 2348.7 | 67 | 50 | 17 | raw original prompt | official-code + qwen-max |
| BIPIA | Erase-and-Check official (qwen-max) | 64.0% | 0.0% | 82.0% | 2767.3 | 100 | 50 | 50 | raw original prompt | official-code + qwen-max |
| AgentDojo | Erase-and-Check official (qwen-max) | 100.0% | 24.0% | 88.0% | 2305.2 | 50 | 25 | 25 | raw original prompt | official-code + qwen-max |
| InjecAgent | SmoothLLM-style perturbation + qwen-max judge | 100.0% | 41.2% | 83.3% | 3364.6 | 42 | 25 | 17 | raw original prompt | style-reproduction + qwen-max |
| BIPIA | SmoothLLM-style perturbation + qwen-max judge | 96.0% | 48.0% | 74.0% | 5054.6 | 50 | 25 | 25 | raw original prompt | style-reproduction + qwen-max |
| InjecAgent | SmoothLLM-style perturbation + qwen-plus-2025-09-11 judge | 100.0% | 29.4% | 88.1% | 3045.5 | 42 | 25 | 17 | raw original prompt | style-reproduction + qwen-plus |
| BIPIA | SmoothLLM-style perturbation + qwen-plus-2025-09-11 judge | 88.0% | 44.0% | 72.0% | 3051.8 | 50 | 25 | 25 | raw original prompt | style-reproduction + qwen-plus |
| InjecAgent | SmoothLLM-style perturbation + qwen-turbo judge | 100.0% | 58.8% | 76.2% | 2066.2 | 42 | 25 | 17 | raw original prompt | style-reproduction + qwen-turbo |
| BIPIA | SmoothLLM-style perturbation + qwen-turbo judge | 72.0% | 8.0% | 82.0% | 2068.8 | 50 | 25 | 25 | raw original prompt | style-reproduction + qwen-turbo |
| AgentDojo | SmoothLLM-style perturbation + qwen-turbo judge | 88.0% | 84.0% | 52.0% | 2008.3 | 50 | 25 | 25 | raw original prompt | style-reproduction + qwen-turbo |

## Notes

- IR means attack interception rate: among attack samples, the percentage blocked by the defense.
- FPR means false positive rate: among benign samples, the percentage wrongly blocked.
- ACC means overall binary decision accuracy.
- Latency is the measured mean per-sample runtime in milliseconds.
- The WAMI rows are full-dataset local runs; most API baseline rows are smaller sampled runs to control token cost.
