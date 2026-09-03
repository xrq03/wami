# SmoothVLM-style CyberSecEval3-VPI Results

This is a method-level SmoothVLM-style reproduction using visual perturbations and VLM voting. It is not an official SmoothVLM codebase run.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | TP/FP/TN/FN |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| CyberSecEval3-VPI | SmoothVLM-style + llava-llama3:8b [local_strict] (2/3 vote) | 100.0% | 35.0% | 82.5% | 1136.6 | 40 | 20 | 20 | 20/7/13/0 |

- Summary CSV: `data\smoothvlm_style_vpi_llava_llama3_8b_20pairs.csv`
- Detail CSV: `data\smoothvlm_style_vpi_llava_llama3_8b_20pairs_details.csv`
