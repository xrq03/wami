# SmoothVLM-style CyberSecEval3-VPI Results

This is a method-level SmoothVLM-style reproduction using visual perturbations and VLM voting. It is not an official SmoothVLM codebase run.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | TP/FP/TN/FN |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| CyberSecEval3-VPI | SmoothVLM-style + llava:7b [local_strict] (2/3 vote) | 0.0% | 0.0% | 50.0% | 1337.3 | 10 | 5 | 5 | 0/0/5/5 |

- Summary CSV: `data\smoothvlm_style_vpi_llava7b_local_strict_5pairs.csv`
- Detail CSV: `data\smoothvlm_style_vpi_llava7b_local_strict_5pairs_details.csv`
