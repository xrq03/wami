from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.gateway import WAMIGateway
from wami.model import WAMIModel


ROOT = Path(__file__).resolve().parents[1]


def load_queries(toolbench_dir: Path) -> dict[str, dict[int, dict[str, Any]]]:
    queries: dict[str, dict[int, dict[str, Any]]] = {}
    instruction_dir = toolbench_dir / "data_example" / "instruction"
    for name in ("G1", "G2", "G3"):
        path = instruction_dir / f"{name}_query.json"
        rows = json.loads(path.read_text(encoding="utf-8"))
        queries[name] = {int(row["query_id"]): row for row in rows}
    return queries


def best_path_actions(node: dict[str, Any]) -> list[tuple[str, str]]:
    actions: list[tuple[str, str]] = []
    current = node
    pending_action: str | None = None
    while current:
        node_type = current.get("node_type")
        description = current.get("description", "")
        if node_type == "Action":
            pending_action = description
        elif node_type == "Action Input" and pending_action:
            actions.append((pending_action, description or "{}"))
            pending_action = None
        children = current.get("children") or []
        if not children:
            break
        finished = [child for child in children if child.get("finished") or child.get("node_type") == "Action"]
        current = finished[0] if finished else children[0]
    return actions


def action_to_plan(actions: list[tuple[str, str]]) -> str:
    lines = []
    for tool, params in actions:
        if tool.lower() == "finish":
            continue
        compact = " ".join(params.split())
        if len(compact) > 400:
            compact = compact[:400] + "..."
        lines.append(f"Action: {tool}(input={json.dumps(compact, ensure_ascii=False)})")
    return "\n".join(lines)


def extract_query(payload: dict[str, Any]) -> str:
    if isinstance(payload.get("query"), str) and payload["query"].strip():
        return payload["query"].strip()
    messages = payload.get("compare_candidates") or []
    stack = list(messages)
    while stack:
        item = stack.pop(0)
        if isinstance(item, list):
            stack.extend(item)
            continue
        if not isinstance(item, dict):
            continue
        content = item.get("content")
        if isinstance(content, str) and "Begin!" in content:
            before_begin = content.split("Begin!", 1)[0].strip()
            if before_begin:
                return before_begin
        stack.extend(item.get("children") or [])
    return "Complete the ToolBench tool-use task successfully."


def iter_examples(toolbench_dir: Path):
    queries = load_queries(toolbench_dir)
    answer_root = toolbench_dir / "data_example" / "answer"
    for group in ("G1", "G2", "G3"):
        for path in sorted((answer_root / f"{group}_answer").glob("*.json")):
            query_id = int(path.name.split("_", 1)[0])
            query = queries[group].get(query_id)
            payload = json.loads(path.read_text(encoding="utf-8"))
            actions = best_path_actions(payload["tree"]["tree"])
            plan = action_to_plan(actions)
            if not plan:
                continue
            query_text = query["query"] if query else extract_query(payload)
            yield {
                "group": group,
                "query_id": query_id,
                "query": query_text,
                "plan": plan,
                "win": bool(payload.get("win", False)),
                "action_count": len(actions),
            }


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--toolbench-dir", default="external/ToolBench")
    parser.add_argument("--model", default="wami_bipia_final_e5.npz")
    parser.add_argument("--output-csv", default="data/toolbench_wami_capability.csv")
    parser.add_argument("--output-md", default="data/toolbench_wami_capability.md")
    args = parser.parse_args()

    gateway = WAMIGateway(WAMIModel.load(args.model))
    examples = list(iter_examples(ROOT / args.toolbench_dir))
    rows = []
    allowed = blocked = official_success = 0
    for item in examples:
        decision = gateway.inspect(item["query"], item["plan"])
        if item["win"]:
            official_success += 1
        if decision.allowed:
            allowed += 1
        else:
            blocked += 1
        rows.append(
            {
                **item,
                "wami_allowed": decision.allowed,
                "blocked_tool": decision.tool or "",
                "reason": decision.reason,
                "score": decision.score,
                "threshold": decision.threshold,
            }
        )

    total = len(rows)
    no_defense_sr = official_success / max(1, total)
    wami_sr = sum(1 for row in rows if row["win"] and row["wami_allowed"]) / max(1, total)
    retention = wami_sr / max(1e-9, no_defense_sr)
    false_block_rate = blocked / max(1, total)

    out_csv = ROOT / args.output_csv
    out_md = ROOT / args.output_md
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "group",
            "query_id",
            "win",
            "action_count",
            "wami_allowed",
            "blocked_tool",
            "reason",
            "score",
            "threshold",
            "query",
            "plan",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# ToolBench example WAMI capability",
        "",
        "This is a small ToolBench official-format example run using `external/ToolBench/data_example`. "
        "It measures whether WAMI blocks already successful benign ToolBench trajectories.",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Examples | {total} |",
        f"| No-defense example SR | {pct(no_defense_sr)} |",
        f"| WAMI example SR | {pct(wami_sr)} |",
        f"| Capability retention | {pct(retention)} |",
        f"| WAMI false block rate | {pct(false_block_rate)} |",
        "",
        "## Blocked examples",
        "",
        "| Group | Query ID | Tool | Reason |",
        "|---|---:|---|---|",
    ]
    for row in rows:
        if not row["wami_allowed"]:
            lines.append(f"| {row['group']} | {row['query_id']} | {row['blocked_tool']} | {row['reason']} |")
    if all(row["wami_allowed"] for row in rows):
        lines.append("| - | - | - | none |")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"examples={total} no_defense_sr={no_defense_sr:.4f} wami_sr={wami_sr:.4f} retention={retention:.4f} false_block={false_block_rate:.4f}")
    print(f"wrote {out_csv}")
    print(f"wrote {out_md}")


if __name__ == "__main__":
    main()
