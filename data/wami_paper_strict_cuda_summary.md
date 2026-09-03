# WAMI Paper-Strict CUDA Summary

All rows use the stricter WAMI implementation: 4-layer Transformer Encoder, 1024 hidden dimension, 8 heads, 3-layer ReLU MINE, AdamW, cosine schedule, CUDA inference.

| Dataset | Eval IR | Eval FPR | Eval ACC | Final MI gap | Latency ms | World ms | MINE ms | Peak VRAM MB | w/o TDG IR | w/o World IR | w/o MINE IR | w/o Shadow IR | Note |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| InjecAgent | 100.0% | 0.0% | 100.0% | 6.292 | 32.316 | 16.949 | 2.978 | 336.0 | 100.0% | 100.0% | 85.4% | 95.1% | 512-sample CUDA strict reproduction; internal split/in-sample smoke, not final held-out full benchmark. |
| BIPIA | 100.0% | 0.0% | 100.0% | 3.859 | 22.944 | 13.960 | 1.960 | 336.0 | 80.0% | 100.0% | 100.0% | 100.0% | 512-sample CUDA strict reproduction; internal split/in-sample smoke, not final held-out full benchmark. |
| AgentDojo | 92.0% | 0.0% | 93.4% | 0.321 | 19.030 | 15.048 | 2.355 | 335.9 | 0.0% | 100.0% | 100.0% | 100.0% | 512-sample CUDA strict reproduction; internal split/in-sample smoke, not final held-out full benchmark. |

## Reading

- Eval IR/FPR/ACC are from the 512-sample strict CUDA run.
- Ablation IR columns are from the 100-sample strict ablation probe for the same checkpoint.
- These results close the architecture-level reproduction gap, but the final paper-quality run still needs held-out/full-dataset training and evaluation.
