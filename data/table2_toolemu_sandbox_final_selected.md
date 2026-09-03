# Table 2 selected ToolEmu-Sandbox result

Selected row for the current paper reproduction pass:

| Dataset | Method | IR | FPR | ACC | Latency ms | N |
|---|---|---:|---:|---:|---:|---:|
| BIPIA | ToolEmu-Sandbox-style local (tau=7) | 91.7% | 15.3% | 88.2% | 0.236 | 2400 |
| InjecAgent | ToolEmu-Sandbox-style local (tau=7) | 58.1% | 29.4% | 64.4% | 0.183 | 4233 |
| AgentDojo | ToolEmu-Sandbox-style local (tau=7) | 72.7% | 1.2% | 76.1% | 0.262 | 653 |

Source: `data/toolemu_sandbox_style_table2_full_tau7.md`

Runner: `scripts/run_toolemu_sandbox_table2.py`

Interpretation: this is not a strict official ToolEmu run. It is a local same-dataset reproduction of the ToolEmu-Sandbox defense idea: run the proposed tool trajectory through a sandbox-style TDG analyzer, predict unsafe side effects and sensitive/untrusted data propagation, then block actions above a risk threshold.
