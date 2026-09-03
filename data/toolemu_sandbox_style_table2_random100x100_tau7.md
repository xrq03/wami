# ToolEmu-Sandbox-style Table 2 result

This is a local same-dataset reproduction of ToolEmu-Sandbox's safety idea, not the full official ToolEmu benchmark harness.

The sandbox applies ToolEmu-style principles: risk-aware tool execution; avoid direct risky tool calls; ask for user confirmation before privacy, security, or real-world side effects; validate that tool inputs are grounded in the user request or previous observations.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | ToolEmu-Sandbox-style local (tau=7) | 97.0% | 12.0% | 92.5% | 0.231 | 200 | 100 | 100 |
| InjecAgent | ToolEmu-Sandbox-style local (tau=7) | 64.0% | 28.0% | 68.0% | 0.178 | 200 | 100 | 100 |
| AgentDojo | ToolEmu-Sandbox-style local (tau=7) | 73.0% | 1.2% | 84.9% | 0.194 | 186 | 100 | 86 |

Use note: report this as `ToolEmu-Sandbox-style local reproduction`, not as strict official ToolEmu.
