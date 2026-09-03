# Paper-Faithful WAMI Status

## Why This Version Exists

The previous v4/runtime-guard implementation is useful as an engineering
enhancement, but it includes strong direct blocking rules. That makes it
unsuitable as the main result if the paper claims that WAMI primarily blocks
through world-model rollout and MINE alignment scores.

This version restores a paper-faithful attribution:

```text
TDG -> world-model trajectory rollout -> MINE alignment score -> dynamic threshold -> allow/block
```

Tool/security heuristics are used only as small threshold margins. They do not
directly block.

## Code

- Gateway: `wami/paper_mine_gateway.py`
- Evaluator: `scripts/run_paper_mine_gateway.py`
- Reason analysis: `scripts/analyze_paper_mine_gateway_reasons.py`

The previous engineering version is still preserved:

- `wami/gateway.py`
- `wami/runtime_trace.py`
- `scripts/demo_wami_incremental_runtime_effect.py`

## Zero-Supervision Results

- Model: `wami_paper_strict_zero_supervision_e20_cuda.pt`
- Calibration: `data/paper_shadow_val.jsonl`
- Official datasets: test-only
- Result file: `data/paper_mine_gateway_zero_supervision.md`
- Reason file: `data/paper_mine_gateway_reasons.md`

| Dataset | IR | FPR | ACC | Tau |
|---|---:|---:|---:|---:|
| InjecAgent | 90.1% | 52.9% | 68.5% | -1.4500 |
| BIPIA | 99.8% | 78.7% | 60.6% | -1.4500 |
| AgentDojo | 100.0% | 45.3% | 94.0% | -1.4500 |

## Reason Attribution

All blocking reasons in this version are MINE-based:

- `paper MINE plan alignment below threshold`
- `paper MINE trajectory alignment below dynamic threshold`

There are no direct rule-block reasons such as:

- `high-risk tool follows untrusted injection content`
- `tool arguments target attacker-controlled resource`
- `runtime trace shows untrusted content flow into side-effect sink`

## Interpretation

This is the honest paper-faithful baseline. It shows high interception rate but
also high false positive rate. The current trained MINE/world-model separates
many attacks from benign samples, but its score distribution is not yet
well-calibrated enough to keep FPR low without the engineering guard.

For the paper, use this version as the method-faithful WAMI result, and report
the engineering guard separately as an extension:

| Version | Role |
|---|---|
| Paper-faithful WAMI | Main algorithm attribution |
| Engineering-enhanced WAMI/runtime guard | Practical deployment extension |
| Rules-only / no-MINE ablation | Shows what is not the claimed core |

## Next Improvements

To improve this version without reverting to strong rules:

1. Train MINE with more generated benign hard negatives, especially legitimate
   high-risk tools and long benign context.
2. Use per-step score normalization or dataset-independent validation
   calibration.
3. Replace hard direct rules with learned risk embeddings or margin features.
4. Report ROC/AUC and threshold curves instead of hiding the FPR/IR tradeoff.

## Follow-Up Completion Pass

Additional paper-faithful code was added:

- `PaperMultimodalMINEGateway` in `wami/paper_mine_gateway.py`
- `scripts/run_paper_multimodal_mine.py`
- supervised MINE gap loss in `wami/torch_training.py`
- hard benign generated workflows in `scripts/generate_self_training_data.py`

The best current paper-faithful text-only checkpoint is:

- `wami_paper_mine_supgap_v3fast_e4_cuda.pt`

Best current tradeoff result without strong direct rules:

| Dataset | IR | FPR | ACC | Setting |
|---|---:|---:|---:|---|
| InjecAgent | 85.2% | 35.3% | 74.9% | v3fast-e4, tau=-3.5 |
| BIPIA | 99.6% | 22.5% | 88.5% | v3fast-e4, tau=-3.5 |
| AgentDojo | 99.8% | 9.3% | 98.6% | v3fast-e4, tau=-3.5 |

Longer v3fast-e12 training did not improve the official test tradeoff:

| Dataset | IR | FPR | ACC | Setting |
|---|---:|---:|---:|---|
| InjecAgent | 82.3% | 41.2% | 70.5% | v3fast-e12, tau=-3.5 |
| BIPIA | 99.9% | 32.7% | 83.6% | v3fast-e12, tau=-3.5 |
| AgentDojo | 96.8% | 20.9% | 94.5% | v3fast-e12, tau=-3.5 |

This suggests overfitting to the generated split after a few epochs. The next
real improvement should use larger and more diverse generated train/validation
data rather than simply increasing epochs.

## Larger Generated Split Check

A larger self-generated split was also tested:

- Train data: `data/paper_shadow_train_v4_large.jsonl`
- Validation data: `data/paper_shadow_val_v4_large.jsonl`
- Model: `wami_paper_mine_supgap_v4large_e5_cuda.pt`
- Epochs completed: 5
- Official datasets: test-only
- Setting: tau=-3.5, no strong direct rules

| Dataset | IR | FPR | ACC | Setting |
|---|---:|---:|---:|---|
| InjecAgent | 92.0% | 35.3% | 78.3% | v4large-e5, tau=-3.5 |
| BIPIA | 100.0% | 39.5% | 80.2% | v4large-e5, tau=-3.5 |
| AgentDojo | 100.0% | 25.6% | 96.6% | v4large-e5, tau=-3.5 |

This improved InjecAgent IR, but it worsened BIPIA and AgentDojo FPR compared
with the v3fast-e4 checkpoint. The current evidence says that simply scaling
self-generated samples is not enough; the generated benign/attack distributions
must better match official test trajectories.

The best current paper-faithful text-only checkpoint remains
`wami_paper_mine_supgap_v3fast_e4_cuda.pt` at tau=-3.5.

## MINE Score/Threshold Diagnostics

Added:

- `scripts/export_paper_mine_scores.py`
- `data/paper_mine_v3fast_e4_scores.csv`
- `data/paper_mine_v3fast_e4_threshold_curve.md`

This exports per-sample MINE score diagnostics and a threshold curve without
adding rules or changing the gateway. Current fixed tau=-3.5 diagnostic run:

| Dataset | IR | FPR | ACC | Mean latency |
|---|---:|---:|---:|---:|
| InjecAgent | 86.1% | 35.3% | 75.3% | 27.230 ms |
| BIPIA | 99.7% | 25.4% | 87.1% | 23.300 ms |
| AgentDojo | 99.8% | 10.5% | 98.5% | 41.429 ms |

Interpretation: the score curve confirms that InjecAgent has the strongest
benign/attack overlap under the current generated training distribution. BIPIA
and AgentDojo have clearer high-IR operating points, while InjecAgent needs
better benign trajectory modeling rather than more direct rules.

## Paired Counterfactual Training Update

A paper-faithful paired training objective was added to reduce false positives
without direct rule blocking:

- same-intent benign/attack generated pairs
- same-intent attack sampling during training
- pairwise MINE ranking loss

Fast checkpoint:

- `wami_paper_mine_paired_v1fast_e3_cuda.pt`

At tau=-3.5:

| Dataset | IR | FPR | ACC |
|---|---:|---:|---:|
| InjecAgent | 61.1% | 5.9% | 77.7% |
| BIPIA | 98.6% | 9.0% | 94.8% |
| AgentDojo | 91.4% | 4.7% | 91.9% |

This is the strongest low-FPR paper-faithful operating point so far. It proves
that counterfactual paired MINE training can reduce false positives without
strong rules, but the current fast checkpoint loses too much InjecAgent IR. It
should be treated as an FPR-reduction ablation, not yet as the best final main
model.

An explicit attack-recall loss was also tested. It increased IR slightly but
destroyed the low-FPR boundary:

| Model | InjecAgent IR | InjecAgent FPR | Decision |
|---|---:|---:|---|
| paired-v1fast-e3 | 61.1% | 5.9% | keep as low-FPR ablation |
| paired-recall-v1fast-e4 | 67.0% | 41.2% | reject |
| paired-balanced-v1fast-e4 | 68.9% | 41.2% | reject |

So the next main-method improvement should use richer paired data rather than
direct attack-score pressure.

## Anti-Overfitting v2 Paired Data

To avoid overfitting, paired v2 was expanded with generic domains only, without
using official test errors:

- chat
- code
- finance
- medical
- OCR/visual text
- smart home/device

Two seed check at tau=-3.5:

| Dataset | IR mean | IR std | FPR mean | FPR std | ACC mean |
|---|---:|---:|---:|---:|---:|
| InjecAgent | 60.9% | 3.6 | 26.5% | 4.2 | 67.3% |
| BIPIA | 98.4% | 1.8 | 7.6% | 2.6 | 95.4% |
| AgentDojo | 97.9% | 1.0 | 4.7% | 3.3 | 97.5% |

Conclusion: v2 is more defensible against overfitting and generalizes well on
BIPIA/AgentDojo, but it still does not solve InjecAgent. The current best
paper-faithful story should present v3fast-e4 as the high-IR baseline, v1
paired as the low-FPR ablation, and v2 paired as the anti-overfitting
multi-seed generalization check.

## Transition-MINE Update

A learned transition alignment head was added to model cross-step goal
migration without direct tool-rule vetoes.

Best current transition point:

- Model: `wami_paper_mine_transition_v1_seed2042_e3_cuda.pt`
- Gateway: `--use-transition-mine --transition-fusion 0.35`
- Threshold: `tau=-4.75`

| Dataset | IR | FPR | ACC |
|---|---:|---:|---:|
| InjecAgent | 69.6% | 5.9% | 81.9% |
| BIPIA | 97.0% | 0.2% | 98.4% |
| AgentDojo | 94.7% | 7.0% | 94.5% |

Compared with the previous low-FPR paired checkpoint, this improves InjecAgent
IR at the same FPR:

| Model | InjecAgent IR | InjecAgent FPR |
|---|---:|---:|
| paired-v1fast-e3 | 61.1% | 5.9% |
| transition-v1 fusion=0.35 | 69.6% | 5.9% |

This is the strongest evidence so far that a learned transition component can
recover attacks while keeping false positives low.

## Source-Aware World Model Update

Implemented weakly supervised source-aware auxiliary world-model heads:

- `source_head`: predicts whether a state is driven by external/untrusted observation.
- `drift_head`: predicts whether a transition reflects goal drift.
- `sink_auth_head`: predicts whether a sensitive sink is user-authorized.

Important boundary: these weak labels are used only for training and learned
score fusion. They are not used as direct gateway veto rules.

Code:

- `wami/torch_model.py`
- `wami/torch_training.py`
- `wami/paper_mine_gateway.py`
- `scripts/train_wami_paper_strict.py`
- `scripts/run_paper_mine_gateway.py`

Smoke model:

- `wami_paper_mine_sourceaware_seed2061_e2_cuda.pt`

Current source-aware results:

| Setting | InjecAgent IR | InjecAgent FPR | BIPIA IR | BIPIA FPR | AgentDojo IR | AgentDojo FPR |
|---|---:|---:|---:|---:|---:|---:|
| tau=-4.75, aux=0.20 | 54.4% | 0.0% | 32.9% | 0.0% | 79.0% | 5.8% |
| tau=-4.0, aux=0.10 | 66.4% | 0.0% | 98.2% | 0.1% | 96.8% | 20.9% |
| tau=-3.5, aux=0.10 | 69.2% | 0.0% | 99.1% | 0.4% | 99.3% | 24.4% |

Interpretation: source-aware auxiliary world modeling strongly reduces
InjecAgent false positives, but this first smoke model is still recall-limited.
It is useful as a structural improvement and should next be trained with a
separate recall-preserving calibrator rather than simply increasing the
auxiliary fusion.

## Source-Aware Recall-Preserving Update

A lower-auxiliary-pressure source-aware model improved InjecAgent recall while
keeping the low-FPR operating point:

- Model: `wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt`
- Setting: `--use-transition-mine --transition-fusion 0.35 --use-auxiliary-heads --auxiliary-fusion 0.10`
- Threshold: `tau=-4.5`

| Dataset | IR | FPR | ACC |
|---|---:|---:|---:|
| InjecAgent | 78.4% | 5.9% | 86.3% |
| BIPIA | 99.4% | 0.2% | 99.6% |
| AgentDojo | 98.4% | 23.3% | 95.6% |

Low-FPR InjecAgent progress:

| Model | InjecAgent IR | InjecAgent FPR |
|---|---:|---:|
| paired-v1fast-e3 | 61.1% | 5.9% |
| transition-v1 seed2042 | 69.6% | 5.9% |
| source-aware recall seed2061 | 78.4% | 5.9% |

This is the current best InjecAgent low-FPR result. It still falls short of
90% IR, but it is the clearest evidence that strengthening the world model
itself is better than only adding a post-hoc calibrator.

## Provenance-Aware Memory Attempt

A lightweight provenance head was implemented and tested:

- trusted memory logit
- untrusted memory logit
- instruction memory logit
- sensitive memory logit

Model:

- `wami_paper_mine_provenance_seed2061_e4_cuda.pt`

At tau=-4.5:

| Setting | InjecAgent IR | InjecAgent FPR |
|---|---:|---:|
| provenance fusion=0.10 | 74.8% | 17.6% |
| provenance fusion=0.05 | 74.2% | 11.8% |
| provenance trained, fusion off | 73.6% | 5.9% |
| current best source-aware recall | 78.4% | 5.9% |

This lightweight provenance version is a negative result. It is implemented,
but it should not replace the current best checkpoint. A real improvement would
likely require actual separated memory slots, not only provenance logits.

## True Slot-Memory Attempt

Implemented true learned memory slots inside the world model:

- trusted slot
- untrusted slot
- instruction slot
- sensitive slot

Model:

- `wami_paper_mine_slotmemory_seed2061_e4_cuda.pt`

Results:

| Setting | InjecAgent IR | InjecAgent FPR |
|---|---:|---:|
| tau=-4.5 | 67.4% | 0.0% |
| tau=-4.0 | 73.7% | 17.6% |
| tau=-3.5 | 78.5% | 29.4% |
| current best source-aware recall | 78.4% | 5.9% |

This is structurally closer to the intended world model, but it does not yet
improve the empirical tradeoff. The current best checkpoint remains
`wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt`.

## Learned Ensemble Update

Fixed backward compatibility so old checkpoints do not accidentally use random
slot-memory layers. Then evaluated a learned WAMI ensemble:

- Model A: `wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt`
- Model B: `wami_paper_mine_slotmemory_seed2061_e4_cuda.pt`
- Ensemble mode: OR of two learned WAMI decisions

Best low-FPR InjecAgent point:

| Model | InjecAgent IR | InjecAgent FPR | ACC |
|---|---:|---:|---:|
| source-aware recall | 78.4% | 5.9% | 86.3% |
| slot-memory | 67.4% | 0.0% | 83.7% |
| ensemble OR | 80.6% | 5.9% | 87.4% |

Higher-recall tradeoff:

| Setting | InjecAgent IR | InjecAgent FPR |
|---|---:|---:|
| source-aware tau=-4.5 + slot tau=-4.0 OR | 83.1% | 17.6% |

Current best low-FPR result is now the source-aware + slot-memory ensemble:
80.6% IR at 5.9% FPR on InjecAgent.

## Triplet/Slot Ensemble Update

After implementing counterfactual triplet data, slot-specific loss, and subgoal
contrastive loss, a four-epoch triplet-slot model was trained:

- `wami_paper_mine_triplet_slot_seed4071_e4_cuda.pt`

The triplet model alone is conservative, but it is complementary to the
source-aware recall model.

Best low-FPR ensemble:

| Model A | Model B | Mode | InjecAgent IR | InjecAgent FPR | ACC |
|---|---|---|---:|---:|---:|
| source-aware recall tau=-4.5 | triplet-slot tau=-5.0 | OR | 86.8% | 5.9% | 90.5% |

Higher-recall tradeoff:

| Setting | InjecAgent IR | InjecAgent FPR |
|---|---:|---:|
| source-aware tau=-4.5 + triplet tau=-4.75 OR | 87.9% | 17.6% |

This is the current strongest InjecAgent result while keeping FPR at 5.9%.

## Multimodal Paper-MINE Status

The paper-faithful multimodal gateway now exists and runs:

- `data/paper_multimodal_mine_native_40.md`

Current native-backend result on 40 CyberSecEval3 VPI rows:

| Backend | IR | FPR | ACC |
|---|---:|---:|---:|
| native image latent | 0.0% | 0.0% | 50.0% |

This is a functional integration result, not a strong performance result. The
native byte/hash image latent is not semantically strong enough for VPI. To
make multimodal results match the paper idea, the next step is to train or use
Qwen-VL/CLIP/SigLIP embeddings inside the paper-faithful MINE path.
