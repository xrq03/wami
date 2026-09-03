# WAMI 15-Improvement Implementation Status

## Implemented Core Changes

| # | Improvement | Status | Main Files |
|---:|---|---|---|
| 1 | Counterfactual triplet training data | implemented | `scripts/generate_self_training_data.py` |
| 2 | Slot-specific losses | implemented | `wami/torch_training.py` |
| 3 | Learned ensemble gate | implemented | `scripts/run_paper_mine_ensemble_gate.py` |
| 4 | Subgoal contrastive learning | implemented | `wami/torch_training.py` |
| 5 | Memory contamination/provenance prediction | implemented | `wami/torch_model.py`, `wami/torch_training.py` |
| 6 | Sink authorization scoring | implemented | `wami/torch_model.py`, `wami/torch_training.py` |
| 7 | Multi-hop injection generation | implemented | `scripts/generate_self_training_data.py` |
| 8 | Hard benign sensitive actions | implemented | `scripts/generate_self_training_data.py` |
| 9 | Learned aggregation / ensemble gate | implemented | `scripts/run_paper_mine_ensemble_gate.py` |
| 10 | Multi-seed summaries | implemented | `scripts/summarize_paper_mine_runs.py` |
| 11 | Dataset-independent calibration suite | implemented partially | `scripts/run_operating_points.py`, calibration pools |
| 12 | Better encoder backend interface | stubbed | `wami/encoder_backends.py` |
| 13 | LLM-generated shadow attack interface | stubbed | `scripts/generate_llm_shadow_attacks_stub.py` |
| 14 | Real agent trace training interface | stubbed | `scripts/collect_real_agent_trace_stub.py` |
| 15 | Official benchmark harness alignment | partially implemented | dataset converters and test-only evaluation scripts |

## New Verification Run

Triplet + slot-specific + subgoal model:

- Model: `wami_paper_mine_triplet_slot_seed4071_e2_cuda.pt`
- Train data: `data/paper_shadow_train_triplet_seed4071.jsonl`
- Validation data: `data/paper_shadow_val_triplet_seed4071.jsonl`
- Epochs: 2

| Dataset | IR | FPR | ACC |
|---|---:|---:|---:|
| InjecAgent | 57.2% | 0.0% | 78.7% |
| BIPIA | 86.2% | 0.0% | 93.1% |
| AgentDojo | 90.8% | 2.3% | 91.7% |

The first two-epoch verification run confirmed the new training chain works,
but it was too conservative.

## Four-Epoch Triplet/Slot Result

Model:

- `wami_paper_mine_triplet_slot_seed4071_e4_cuda.pt`

| Setting | InjecAgent IR | InjecAgent FPR | BIPIA IR | BIPIA FPR | AgentDojo IR | AgentDojo FPR |
|---|---:|---:|---:|---:|---:|---:|
| tau=-5.0 | 74.8% | 0.0% | 99.3% | 0.5% | 97.2% | 9.3% |
| tau=-4.75 | 77.6% | 11.8% | 99.4% | 1.2% | 98.8% | 11.6% |
| tau=-4.5 | 79.8% | 11.8% | 99.6% | 3.5% | 99.5% | 11.6% |

The triplet model is still not the best single model, but it is highly
complementary to the source-aware recall model.

## Best Current Ensemble

Model A:

- `wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt`
- tau=-4.5

Model B:

- `wami_paper_mine_triplet_slot_seed4071_e4_cuda.pt`
- tau=-5.0

Mode:

- OR of two learned WAMI decisions

| Dataset | IR | FPR | ACC |
|---|---:|---:|---:|
| InjecAgent | 86.8% | 5.9% | 90.5% |
| BIPIA | 99.8% | 0.5% | 99.6% |
| AgentDojo | 99.3% | 25.6% | 96.0% |

Higher-recall InjecAgent point:

| Setting | InjecAgent IR | InjecAgent FPR |
|---|---:|---:|
| source-aware tau=-4.5 + triplet tau=-4.75 OR | 87.9% | 17.6% |

## Current Best Result

| Method | InjecAgent IR | InjecAgent FPR |
|---|---:|---:|
| source-aware + slot-memory ensemble OR | 80.6% | 5.9% |
| source-aware + triplet-slot ensemble OR | 86.8% | 5.9% |

## Notes

- The implementation keeps the paper-faithful boundary: weak labels are used
  for training, not direct test-time veto rules.
- Stubbed items require external resources before they can become real
  experiments: embedding model downloads, API credentials, or live agent traces.
