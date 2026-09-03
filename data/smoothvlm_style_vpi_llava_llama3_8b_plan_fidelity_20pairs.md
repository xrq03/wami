# SmoothVLM-style CyberSecEval3-VPI Results

This is a method-level SmoothVLM-style reproduction using visual perturbations and VLM voting. It is not an official SmoothVLM codebase run.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | TP/FP/TN/FN |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| CyberSecEval3-VPI | SmoothVLM-style + llava-llama3:8b [plan_fidelity] (2/3 vote) | 35.0% | 0.0% | 67.5% | 1476.2 | 40 | 20 | 20 | 7/0/20/13 |

- Summary CSV: `data\smoothvlm_style_vpi_llava_llama3_8b_plan_fidelity_20pairs.csv`
- Detail CSV: `data\smoothvlm_style_vpi_llava_llama3_8b_plan_fidelity_20pairs_details.csv`
