# SmoothVLM-style CyberSecEval3-VPI Results

This is a method-level SmoothVLM-style reproduction using visual perturbations and VLM voting. It is not an official SmoothVLM codebase run.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | TP/FP/TN/FN |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| CyberSecEval3-VPI | SmoothVLM-style + llava-llama3:8b [local_strict] (2/3 vote) | 100.0% | 40.0% | 80.0% | 1966.3 | 10 | 5 | 5 | 5/2/3/0 |

- Summary CSV: `data\smoothvlm_style_vpi_llava_llama3_8b_5pairs.csv`
- Detail CSV: `data\smoothvlm_style_vpi_llava_llama3_8b_5pairs_details.csv`
