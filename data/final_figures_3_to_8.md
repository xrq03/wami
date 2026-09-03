# Final Figures 3-8

These figures are regenerated from the final accepted local result files.

| Figure | File | Data source | Meaning |
|---|---|---|---|
| Figure 3 | `data/final_figure3_defense_efficacy_overview_v6.png` | `data/final_table2_reproduction.csv` + resource profile | Paper-style defense efficacy overview radar chart computed from local WAMI, Llama-Guard 3, and SmoothLLM results. |
| Figure 4 | `data/final_figure4_sota_smooth_roc_v2.png` | `data/final_table2_reproduction.csv` + `data/llamaguard3_ollama_pc100_summary.csv` | Smoothed ROC-style SOTA defense comparison using actually measured local operating points. |
| Figure 5 | `data/final_figure5_threshold_sensitivity.png` | `data/wami_extra_*_threshold_sensitivity.csv` | IR/FPR movement under threshold sweep. |
| Figure 6 | `data/final_figure6_latency_decomposition.png` | `data/wami_paper_latency_*_512_e5_cuda.csv` | Paper-strict CUDA TDG/world/MINE latency decomposition. |
| Figure 7 | `data/final_figure7_resource_comparison_v2.png` | `data/final_figure7_resource_comparison.csv` | Defense footprint and latency overhead. |
| Figure 8 | `data/final_figure8_shadow_training.png` | `data/paper_mine_*_training.csv` | Shadow adversarial training MI-gap and loss dynamics. |
