from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
import statistics


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize WAMI paper-MINE runs across seeds.")
    parser.add_argument("--csv", action="append", required=True)
    parser.add_argument("--output-md", default="data/paper_mine_multiseed_summary.md")
    args = parser.parse_args()

    rows = []
    for path in args.csv:
        with Path(path).open("r", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                row["source"] = Path(path).name
                rows.append(row)

    grouped = defaultdict(list)
    for row in rows:
        grouped[row["dataset"]].append(row)

    lines = [
        "# Paper-MINE Multi-Seed Summary",
        "",
        "| Dataset | Runs | IR mean | IR std | FPR mean | FPR std | ACC mean | ACC std |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for dataset, items in sorted(grouped.items()):
        ir = [float(item["ir"]) * 100.0 for item in items]
        fpr = [float(item["fpr"]) * 100.0 for item in items]
        acc = [float(item["acc"]) * 100.0 for item in items]
        lines.append(
            f"| {dataset} | {len(items)} | {mean(ir):.1f}% | {std(ir):.1f} | "
            f"{mean(fpr):.1f}% | {std(fpr):.1f} | {mean(acc):.1f}% | {std(acc):.1f} |"
        )
    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def std(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


if __name__ == "__main__":
    main()
