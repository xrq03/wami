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
from wami.torch_model import TorchWAMIModel


@dataclass
class Row:
    dataset: str
    label: str
    pattern: str
    count: int
    share: float


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-a", required=True)
    parser.add_argument("--model-b", required=True)
    parser.add_argument("--test-data", action="append", required=True)
    parser.add_argument("--tau-a", type=float, default=-4.5)
    parser.add_argument("--tau-b", type=float, default=-5.0)
    parser.add_argument("--output-md", default="data/ensemble_disagreement.md")
    parser.add_argument("--output-csv", default="data/ensemble_disagreement.csv")
    args = parser.parse_args()

    gw_a = gateway(TorchWAMIModel.load(args.model_a), args.tau_a)
    gw_b = gateway(TorchWAMIModel.load(args.model_b), args.tau_b)
    rows = []
    for path in args.test_data:
        counters = {"attack": Counter(), "benign": Counter()}
        totals = {"attack": 0, "benign": 0}
        for sample in load_plan_samples(path):
            da = gw_a.inspect(sample.intent, sample.plan)
            db = gw_b.inspect(sample.intent, sample.plan)
            label = "attack" if sample.label == 1 else "benign"
            totals[label] += 1
            pattern = f"A{int(not da.allowed)}B{int(not db.allowed)}"
            counters[label][pattern] += 1
        for label, counter in counters.items():
            for pattern, count in counter.most_common():
                rows.append(Row(Path(path).stem, label, pattern, count, count / max(1, totals[label])))
    write(Path(args.output_md), Path(args.output_csv), rows)
    print(format_rows(rows))


def gateway(model, tau):
    return PaperMINEGateway(
        model,
        PaperMINEConfig(
            base_threshold=tau,
            plan_threshold=tau,
            use_transition_mine=True,
            transition_fusion=0.35,
            use_auxiliary_heads=True,
            auxiliary_fusion=0.10,
        ),
    )


def format_rows(rows):
    lines = ["| Dataset | Label | Pattern | Count | Share |", "|---|---|---|---:|---:|"]
    for row in rows:
        lines.append(f"| {row.dataset} | {row.label} | {row.pattern} | {row.count} | {row.share * 100:.1f}% |")
    return "\n".join(lines)


def write(md, csv_path, rows):
    md.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md.write_text("# Ensemble Disagreement Analysis\n\n" + format_rows(rows) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
