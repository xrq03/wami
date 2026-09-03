# ToolEmu-Sandbox-style Table 2 result

This is a local same-dataset reproduction of ToolEmu-Sandbox's safety idea, not the full official ToolEmu benchmark harness.

The sandbox applies ToolEmu-style principles: risk-aware tool execution; avoid direct risky tool calls; ask for user confirmation before privacy, security, or real-world side effects; validate that tool inputs are grounded in the user request or previous observations.

| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| BIPIA | ToolEmu-Sandbox-style local (tau=7) | 91.7% | 15.3% | 88.2% | 0.236 | 2400 | 1200 | 1200 |
| InjecAgent | ToolEmu-Sandbox-style local (tau=7) | 58.1% | 29.4% | 64.4% | 0.183 | 4233 | 2108 | 2125 |
| AgentDojo | ToolEmu-Sandbox-style local (tau=7) | 72.7% | 1.2% | 76.1% | 0.262 | 653 | 567 | 86 |

Use note: report this as `ToolEmu-Sandbox-style local reproduction`, not as strict official ToolEmu.
