# Commitment Clearing Round 7: v4 Ablation And Contribution

## Protocol

- Model: `wami_paper_strict_zero_supervision_e20_cuda.pt`
- Calibration data: `data/paper_shadow_val.jsonl`
- Official datasets are test-only:
  - `data/injecagent_wami.jsonl`
  - `data/bipia_wami.jsonl`
  - `data/agentdojo_wami.jsonl`
- Main result: `data/wami_paper_strict_zero_supervision_e20_cuda_gateway_v4.md`
- Contribution analysis: `data/wami_v4_decision_contributions.md`
- Ablation: `data/wami_v4_ablation.md`

## Decision Contribution Summary

| Dataset | TP | FP | TN | FN | IR | FPR | ACC |
|---|---:|---:|---:|---:|---:|---:|---:|
| InjecAgent | 2021 | 0 | 2125 | 87 | 95.9% | 0.0% | 97.9% |
| BIPIA | 1200 | 1 | 1199 | 0 | 100.0% | 0.1% | 100.0% |
| AgentDojo | 567 | 1 | 85 | 0 | 100.0% | 1.2% | 99.8% |

Important reason shares:

- InjecAgent attacks: 47.7% blocked by unauthorized high-risk tool logic,
  35.2% by plan-level MINE, 6.1% by trajectory threshold.
- BIPIA attacks: 95.8% blocked by high-risk tool after untrusted injection,
  4.1% by plan-level MINE.
- AgentDojo attacks: 51.5% blocked by trajectory threshold, 21.3% by
  high-risk tool after untrusted injection, 16.4% by plan-level MINE, and
  10.8% by attacker-target argument logic.

## v4 Ablation Summary

| Dataset | Full IR/FPR | w/o action-prior rules | Rules only | Trajectory MINE only |
|---|---:|---:|---:|---:|
| InjecAgent | 95.9% / 0.0% | 88.6% / 52.9% | 93.0% / 0.0% | 88.4% / 52.9% |
| BIPIA | 100.0% / 0.1% | 99.8% / 76.6% | 100.0% / 0.0% | 99.8% / 76.6% |
| AgentDojo | 100.0% / 1.2% | 99.8% / 40.7% | 74.6% / 0.0% | 99.8% / 40.7% |

## Interpretation

The strong v4 result is not explained by a single component.

- Action-prior rules are essential for controlling false positives. Removing
  them causes FPR to jump to 52.9% on InjecAgent, 76.6% on BIPIA, and 40.7% on
  AgentDojo.
- Rules alone are not enough for AgentDojo: IR falls to 74.6%, while full WAMI
  reaches 100.0%. This supports the role of trajectory/world-model scoring.
- Plan-level MINE contributes most visibly on InjecAgent and in the decision
  reason breakdown, though the ablation gap is smaller than the action-prior
  gap.
- Static threshold is close to dynamic threshold in this run, so the current
  v4 result does not strongly support a large dynamic-threshold effect. This
  should be written honestly in the paper.
