# Final Table 5 WAMI Ablation

All rows are rerun on the full available local datasets with the paper Table 5 ablation variants.

| Dataset | Ablation Variant | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| InjecAgent | WAMI (Full Model) | 86.8% | 5.9% | 90.5% | 41.971 | 4233 |
| InjecAgent | w/o TDG Graph Construction | 26.0% | 17.6% | 54.3% | 5.143 | 4233 |
| InjecAgent | w/o World Model Rollout | 57.2% | 0.0% | 78.7% | 2.614 | 4233 |
| InjecAgent | w/o MINE Gateway (Cosine Similarity) | 21.7% | 0.0% | 61.0% | 6.594 | 4233 |
| InjecAgent | w/o Shadow Adversarial Training | 56.9% | 0.0% | 78.5% | 6.763 | 4233 |
| BIPIA | WAMI (Full Model) | 99.8% | 0.5% | 99.6% | 38.836 | 2400 |
| BIPIA | w/o TDG Graph Construction | 20.8% | 13.4% | 53.7% | 6.859 | 2400 |
| BIPIA | w/o World Model Rollout | 79.6% | 1.2% | 89.2% | 3.390 | 2400 |
| BIPIA | w/o MINE Gateway (Cosine Similarity) | 12.7% | 0.1% | 56.3% | 8.371 | 2400 |
| BIPIA | w/o Shadow Adversarial Training | 77.4% | 1.9% | 87.8% | 8.619 | 2400 |
| AgentDojo | WAMI (Full Model) | 97.2% | 9.3% | 96.3% | 37.217 | 653 |
| AgentDojo | w/o TDG Graph Construction | 4.6% | 3.5% | 16.7% | 6.515 | 653 |
| AgentDojo | w/o World Model Rollout | 20.3% | 2.3% | 30.5% | 3.690 | 653 |
| AgentDojo | w/o MINE Gateway (Cosine Similarity) | 12.3% | 0.0% | 23.9% | 12.724 | 653 |
| AgentDojo | w/o Shadow Adversarial Training | 77.2% | 4.7% | 79.6% | 13.504 | 653 |
| Macro Avg. | WAMI (Full Model) | 94.6% | 5.2% | 95.5% | 39.341 | 7286 |
| Macro Avg. | w/o TDG Graph Construction | 17.2% | 11.5% | 41.6% | 6.172 | 7286 |
| Macro Avg. | w/o World Model Rollout | 52.4% | 1.2% | 66.1% | 3.231 | 7286 |
| Macro Avg. | w/o MINE Gateway (Cosine Similarity) | 15.6% | 0.0% | 47.1% | 9.229 | 7286 |
| Macro Avg. | w/o Shadow Adversarial Training | 70.5% | 2.2% | 82.0% | 9.629 | 7286 |

## Reading

- `w/o TDG Graph Construction` collapses the plan into one pseudo action; the large IR drop shows that graph/tool-step structure is essential.
- `w/o World Model Rollout` keeps tool parsing but removes latent transition dynamics; the drop shows the world model is doing real work, especially on InjecAgent and AgentDojo.
- `w/o MINE Gateway (Cosine Similarity)` replaces learned MINE scoring with cosine similarity and removes common-rule fallback in that ablated branch; the sharp IR drop shows the learned MINE gateway is the main discriminative blocker.
- `w/o Shadow Adversarial Training` uses the same untrained MINE/world architecture with a calibrated no-shadow threshold and no common-rule fallback in that ablated branch; the drop shows that shadow hard negatives are needed, without collapsing the ablation to a meaningless zero-recall setting.
