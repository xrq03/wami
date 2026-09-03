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
    reason: str
    count: int
    share: float


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--tau", type=float, required=True)
    parser.add_argument("--test-data", action="append", required=True)
    parser.add_argument("--use-transition-mine", action="store_true")
    parser.add_argument("--transition-fusion", type=float, default=0.35)
    parser.add_argument("--use-auxiliary-heads", action="store_true")
    parser.add_argument("--auxiliary-fusion", type=float, default=0.20)
    parser.add_argument("--use-provenance-memory", action="store_true")
    parser.add_argument("--provenance-fusion", type=float, default=0.10)
    parser.add_argument("--output-md", default="data/paper_mine_gateway_reasons.md")
    parser.add_argument("--output-csv", default="data/paper_mine_gateway_reasons.csv")
    args = parser.parse_args()

    model = TorchWAMIModel.load(args.model)
    gateway = PaperMINEGateway(
        model,
        PaperMINEConfig(
            base_threshold=args.tau,
            plan_threshold=args.tau,
            use_transition_mine=args.use_transition_mine,
            transition_fusion=args.transition_fusion,
            use_auxiliary_heads=args.use_auxiliary_heads,
            auxiliary_fusion=args.auxiliary_fusion,
            use_provenance_memory=args.use_provenance_memory,
            provenance_fusion=args.provenance_fusion,
        ),
    )
    rows = []
    for path in args.test_data:
        samples = load_plan_samples(path)
        counters = {"attack": Counter(), "benign": Counter()}
        denominators = {"attack": 0, "benign": 0}
        for sample in samples:
            label = "attack" if sample.label == 1 else "benign"
            denominators[label] += 1
            decision = gateway.inspect(sample.intent, sample.plan)
            counters[label][decision.reason] += 1
        for label, counter in counters.items():
            denom = max(1, denominators[label])
            for reason, count in counter.most_common():
                rows.append(Row(Path(path).stem, label, reason, count, count / denom))
    write_outputs(rows, Path(args.output_md), Path(args.output_csv))
    print(format_table(rows))


def format_table(rows: list[Row]) -> str:
    lines = ["| Dataset | Label | Reason | Count | Share |", "|---|---|---|---:|---:|"]
    for row in rows:
        lines.append(f"| {row.dataset} | {row.label} | {row.reason} | {row.count} | {row.share * 100:.1f}% |")
    return "\n".join(lines)


def write_outputs(rows: list[Row], md_path: Path, csv_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("# Paper MINE Gateway Reason Analysis\n\n" + format_table(rows) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
