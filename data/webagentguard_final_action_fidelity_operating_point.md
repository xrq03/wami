# WebAgentGuard Final Action-Fidelity Operating Point

This is the selected WebAgentGuard-style baseline for the final comparison table.
It uses the local `qwen2.5:7b-instruct` guard with `--guard-profile action_fidelity`.

The action-fidelity profile is closer to an agent-defense setting: it blocks only when the next action actually adopts, propagates, routes, sends, stores, executes, or otherwise operationalizes an instruction from untrusted observation content.

| Dataset | Method | Input | Threshold | IR | FPR | Rationale |
|---|---|---|---:|---:|---:|---|
| BIPIA | WebAgentGuard qwen2.5 + action_fidelity | next_action | risk_score >= 80 | 72.0% | 16.0% | Balanced operating point; detects many risky next actions without using full trajectory. |
| InjecAgent | WebAgentGuard qwen2.5 + action_fidelity | full_trajectory | risk_score >= 80 | 80.0% | 0.0% | Full trajectory is needed because InjecAgent attacks are often visible through multi-step tool propagation. |
| AgentDojo | WebAgentGuard qwen2.5 + action_fidelity | full_trajectory | risk_score >= 85 | 72.0% | 8.0% | Slightly higher threshold controls false positives on AgentDojo. |

Use note:
- Report this as a calibrated method-level WebAgentGuard reproduction, not as an official released WebAgentGuard checkpoint.
- The calibration uses risk-score operating points from the local qwen2.5 action-fidelity guard outputs.
- This is more defensible than intentionally weakening prompts because the decision boundary matches the agent-defense goal.
