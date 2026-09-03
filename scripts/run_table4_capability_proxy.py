from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


PAPER_ROWS = [
    ("No Defense", 0.685, 0.712, 1.000, 1.000),
    ("+ Erase-and-Check", 0.551, 0.576, 0.804, 0.809),
    ("+ ToolEmu-Sandbox", 0.548, 0.569, 0.800, 0.799),
    ("+ Llama-Guard 3", 0.614, 0.638, 0.896, 0.896),
    ("+ WAMI (Ours)", 0.680, 0.706, 0.993, 0.992),
]


def read_retention(path: Path) -> float:
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["system"] == "WAMI":
                return float(row["capability_retention_proxy"])
    raise ValueError(f"WAMI row not found in {path}")


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def main() -> None:
    # This is an explicitly marked proxy:
    # - BIPIA benign allow rate approximates ToolBench retention.
    # - AgentDojo benign allow rate approximates AgentBench-style utility retention.
    # It is not a replacement for official ToolBench/AgentBench agent execution.
    toolbench_retention_proxy = read_retention(DATA / "wami_extra_bipia_capability_proxy.csv")
    agentbench_retention_proxy = read_retention(DATA / "wami_extra_agentdojo_capability_proxy.csv")

    no_defense_toolbench_sr = 0.685
    no_defense_agentbench_sr = 0.712
    local_wami_toolbench_sr_proxy = no_defense_toolbench_sr * toolbench_retention_proxy
    local_wami_agentbench_sr_proxy = no_defense_agentbench_sr * agentbench_retention_proxy

    rows = []
    for system, tb_sr, ab_sr, tb_ret, ab_ret in PAPER_ROWS:
        rows.append(
            {
                "source": "paper_table4",
                "system": system,
                "toolbench_sr": tb_sr,
                "agentbench_sr": ab_sr,
                "toolbench_retention": tb_ret,
                "agentbench_retention": ab_ret,
                "note": "values extracted from the paper Table 4",
            }
        )
    rows.append(
        {
            "source": "local_proxy",
            "system": "+ WAMI (Ours, proxy)",
            "toolbench_sr": local_wami_toolbench_sr_proxy,
            "agentbench_sr": local_wami_agentbench_sr_proxy,
            "toolbench_retention": toolbench_retention_proxy,
            "agentbench_retention": agentbench_retention_proxy,
            "note": "computed from local benign allow-rate proxy; not official ToolBench/AgentBench",
        }
    )

    out_csv = DATA / "table4_capability_proxy.csv"
    out_md = DATA / "table4_capability_proxy.md"
    fieldnames = [
        "source",
        "system",
        "toolbench_sr",
        "agentbench_sr",
        "toolbench_retention",
        "agentbench_retention",
        "note",
    ]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Table 4 capability reproduction",
        "",
        "This file separates the paper's official Table 4 values from the local proxy reproduction. "
        "The local row uses the updated WAMI benign allow-rate as a capability-retention proxy, "
        "because the official ToolBench/AgentBench harnesses are not present in this workspace.",
        "",
        "| Source | System | ToolBench SR | AgentBench SR | ToolBench Retention | AgentBench Retention | Note |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {source} | {system} | {tb_sr} | {ab_sr} | {tb_ret} | {ab_ret} | {note} |".format(
                source=row["source"],
                system=row["system"],
                tb_sr=pct(float(row["toolbench_sr"])),
                ab_sr=pct(float(row["agentbench_sr"])),
                tb_ret=pct(float(row["toolbench_retention"])),
                ab_ret=pct(float(row["agentbench_retention"])),
                note=row["note"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Paper Table 4 WAMI: ToolBench SR 68.0%, AgentBench SR 70.6%, retention 99.3% / 99.2%.",
            f"- Local proxy WAMI: ToolBench-style SR {pct(local_wami_toolbench_sr_proxy)}, AgentBench-style SR {pct(local_wami_agentbench_sr_proxy)}, retention {pct(toolbench_retention_proxy)} / {pct(agentbench_retention_proxy)}.",
            "- Strict official reproduction still requires the ToolBench and AgentBench agent harnesses plus model execution logs.",
        ]
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out_csv}")
    print(f"wrote {out_md}")


if __name__ == "__main__":
    main()
