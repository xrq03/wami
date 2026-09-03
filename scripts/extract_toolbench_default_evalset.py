from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-dir",
        default="external/ToolBench/toolbench/tooleval/results/default_evalset/gpt-3.5-turbo_CoT",
    )
    parser.add_argument("--output-jsonl", default="data/toolbench_default_evalset_600.jsonl")
    parser.add_argument("--output-md", default="data/toolbench_default_evalset_600_status.md")
    args = parser.parse_args()

    input_dir = ROOT / args.input_dir
    rows = []
    counts: dict[str, int] = {}
    for path in sorted(input_dir.glob("*.json")):
        split = path.stem
        payload = json.loads(path.read_text(encoding="utf-8"))
        counts[split] = len(payload)
        for query_id, item in payload.items():
            tools = item.get("available_tools") or []
            answer = item.get("answer") or {}
            official_tools = extract_answer_tools(answer)
            rows.append(
                {
                    "split": split,
                    "query_id": str(query_id),
                    "query": item.get("query", ""),
                    "available_tools": tools,
                    "available_tool_names": [tool.get("name", "") for tool in tools if isinstance(tool, dict)],
                    "official_tools": official_tools,
                    "official_answer_method": answer.get("method", ""),
                    "official_total_steps": answer.get("total_steps", None),
                    "official_final_answer": answer.get("final_answer", ""),
                }
            )

    out_jsonl = ROOT / args.output_jsonl
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with out_jsonl.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    out_md = ROOT / args.output_md
    lines = [
        "# ToolBench Default Evalset Extraction",
        "",
        "The official full `data.zip` download was not reachable from the current network, but the cloned ToolBench repository already contains `toolbench/tooleval/results/default_evalset/gpt-3.5-turbo_CoT`.",
        "",
        "| Split | Rows |",
        "|---|---:|",
    ]
    for split, count in counts.items():
        lines.append(f"| {split} | {count} |")
    lines.extend(
        [
            f"| **Total** | **{len(rows)}** |",
            "",
            f"Output JSONL: `{args.output_jsonl}`",
            "",
            "Use this as the larger local ToolBench evaluation source until the official `data.zip` mirror is reachable.",
        ]
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out_md.read_text(encoding="utf-8"))


def extract_answer_tools(answer: dict) -> list[str]:
    names: list[str] = []
    stack = list(answer.get("answer_details") or [])
    while stack:
        item = stack.pop(0)
        if isinstance(item, list):
            stack.extend(item)
            continue
        if not isinstance(item, dict):
            continue
        if item.get("role") == "tool":
            message = str(item.get("message") or "")
            name = extract_tool_name(message)
            if name and name.lower() != "finish":
                names.append(name)
        children = item.get("next") or []
        if isinstance(children, list):
            stack.extend(children)
    return list(dict.fromkeys(names))


def extract_tool_name(message: str) -> str:
    patterns = [
        r"'name'\s*:\s*'([^']+)'",
        r'"name"\s*:\s*"([^"]+)"',
        r"name\s*[:=]\s*([A-Za-z0-9_./:-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            return match.group(1)
    return ""


if __name__ == "__main__":
    main()
