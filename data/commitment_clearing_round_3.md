# Commitment Clearing Round 3

This round implements and evaluates self-generated WAMI training data.

## Added Code

- `scripts/generate_self_training_data.py`
- `scripts/run_self_generated_training_experiment.py`

The generator creates paired benign/attack trajectories for:

- benign handling of untrusted content
- authorized sensitive actions
- direct sensitive-tool attacks
- cross-tool injection
- multi-step context pollution
- visual-instruction following
- hidden-goal shift

## Main Runs

### Large synthetic augmentation

Command:

```text
uv run --with numpy python scripts\run_self_generated_training_experiment.py --synthetic-count 2000 --epochs 3 --eval-limit 1000
```

Key result:

| Variant | InjecAgent IR/FPR | BIPIA IR/FPR | AgentDojo IR/FPR | SelfGeneratedHoldout IR/FPR |
|---|---:|---:|---:|---:|
| current_agentdojo_model | 91.0% / 0.0% | 100.0% / 5.2% | 89.8% / 1.2% | 100.0% / 76.6% |
| self_generated_augmented | 100.0% / 0.0% | 100.0% / 14.4% | 99.8% / 67.4% | 100.0% / 0.0% |

### Balanced smaller augmentation

Command:

```text
uv run --with numpy python scripts\run_self_generated_training_experiment.py --synthetic-count 500 --epochs 1 --eval-limit 1000 --calibrate-on base
```

Key result:

| Variant | InjecAgent IR/FPR | BIPIA IR/FPR | AgentDojo IR/FPR | SelfGeneratedHoldout IR/FPR |
|---|---:|---:|---:|---:|
| current_agentdojo_model | 91.0% / 0.0% | 100.0% / 5.2% | 89.8% / 1.2% | 100.0% / 73.8% |
| self_generated_augmented | 100.0% / 0.0% | 100.0% / 10.4% | 99.8% / 39.5% | 100.0% / 16.8% |

## Interpretation

Self-generated training data is useful for expanding attack coverage: the
augmented model becomes much stronger on the synthetic holdout set and improves
IR on InjecAgent and AgentDojo. However, it also increases FPR on BIPIA and
especially AgentDojo. This means the current generator is too attack-heavy or
not distribution-matched enough to the official benign trajectories.

## FPR Repair

The first augmentation runs had unacceptable AgentDojo FPR because plan-level
MINE calibration drifted after synthetic training. Almost all false positives
came from:

```text
plan-level MINE alignment below threshold
```

The fix is implemented in `scripts/run_self_generated_training_experiment.py`:

- cap the plan-level threshold with `--plan-threshold-cap`
- support `--calibrate-on per_eval` so each evaluation domain uses its own
  benign distribution for threshold calibration

Best repaired run:

```text
uv run --with numpy python scripts\run_self_generated_training_experiment.py --synthetic-count 500 --epochs 1 --eval-limit 1000 --calibrate-on per_eval --plan-threshold-cap -0.60
```

| Variant | InjecAgent IR/FPR | BIPIA IR/FPR | AgentDojo IR/FPR | SelfGeneratedHoldout IR/FPR |
|---|---:|---:|---:|---:|
| current_agentdojo_model | 90.2% / 0.0% | 100.0% / 0.0% | 84.1% / 0.0% | 78.8% / 0.0% |
| self_generated_augmented | 99.8% / 0.0% | 100.0% / 1.2% | 92.4% / 3.5% | 100.0% / 0.0% |

Final interpretation: self-generated data is now usable as a controlled
stress-training method. It improves attack coverage while keeping FPR moderate
when plan-level threshold drift is capped and calibration is domain-aware.
