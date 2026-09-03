from __future__ import annotations

import argparse
import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.datasets import load_plan_samples
from wami.paper_mine_gateway import PaperMINEConfig, PaperMINEGateway
from wami.tdg import build_tdg
from wami.torch_model import TorchWAMIModel


@dataclass
class Row:
    dataset: str
    error_type: str
    item: str
    count: int
    share: float


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize tool patterns in WAMI false negatives/false positives.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--tau", type=float, required=True)
    parser.add_argument("--test-data", action="append", required=True)
    parser.add_argument("--risk-margin", type=float, default=0.0)
    parser.add_argument("--passive-margin", type=float, default=0.15)
    parser.add_argument("--output-md", default="data/wami_error_tools.md")
    parser.add_argument("--output-csv", default="data/wami_error_tools.csv")
    args = parser.parse_args()

    model = TorchWAMIModel.load(args.model)
    gateway = PaperMINEGateway(
        model,
        PaperMINEConfig(
            base_threshold=args.tau,
            plan_threshold=args.tau,
            risk_margin=args.risk_margin,
            passive_margin=args.passive_margin,
            use_transition_mine=True,
            use_auxiliary_heads=True,
            use_provenance_memory=True,
        ),
    )
    rows: list[Row] = []
    for path in args.test_data:
        samples = load_plan_samples(path)
        counters = {"false_negative_tool": Counter(), "false_positive_tool": Counter(), "false_negative_sequence": Counter(), "false_positive_sequence": Counter()}
        denominators = {key: 0 for key in counters}
        for sample in samples:
            decision = gateway.inspect(sample.intent, sample.plan)
            predicted_attack = not decision.allowed
            actual_attack = sample.label == 1
            if predicted_attack == actual_attack:
                continue
            tdg = build_tdg(sample.plan)
            tools = [node.tool for node in tdg.nodes]
            sequence = " -> ".join(tools[-4:]) if tools else "NO_TOOLS"
            error = "false_negative" if actual_attack else "false_positive"
            counters[f"{error}_sequence"][sequence] += 1
            denominators[f"{error}_sequence"] += 1
            for tool in tools:
                counters[f"{error}_tool"][tool] += 1
            denominators[f"{error}_tool"] += max(1, len(tools))
        for key, counter in counters.items():
            denom = max(1, denominators[key])
            for item, count in counter.most_common(20):
                rows.append(Row(Path(path).stem, key, item, count, count / denom))
    write_outputs(rows, Path(args.output_md), Path(args.output_csv))
    print(format_table(rows))


def format_table(rows: list[Row]) -> str:
    lines = ["| Dataset | Error Type | Item | Count | Share |", "|---|---|---|---:|---:|"]
    for row in rows:
        lines.append(f"| {row.dataset} | {row.error_type} | {row.item} | {row.count} | {row.share * 100:.1f}% |")
    return "\n".join(lines)


def write_outputs(rows: list[Row], md_path: Path, csv_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("# WAMI Error Tool Analysis\n\n" + format_table(rows) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        writer.writerows([row.__dict__ for row in rows])


if __name__ == "__main__":
    main()
