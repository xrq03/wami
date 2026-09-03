# SmoothVLM-style CyberSecEval3-VPI Results

This is a method-level SmoothVLM-style reproduction using visual perturbations and VLM voting. It is not an official SmoothVLM codebase run.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | TP/FP/TN/FN |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| CyberSecEval3-VPI | SmoothVLM-style + qwen-vl-max (2/3 vote) | 100.0% | 100.0% | 50.0% | 3521.8 | 20 | 10 | 10 | 10/10/0/0 |

- Summary CSV: `data\smoothvlm_style_vpi_qwenvl_10pairs.csv`
- Detail CSV: `data\smoothvlm_style_vpi_qwenvl_10pairs_details.csv`
