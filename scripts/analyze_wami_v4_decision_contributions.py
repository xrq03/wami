from __future__ import annotations

import argparse
import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.datasets import load_plan_samples
from wami.paper_calibration import greedy_calibrate_gateway
from wami.torch_model import TorchWAMIModel


@dataclass
class Row:
    dataset: str
    label: str
    reason: str
    count: int
    share: float


@dataclass
class SummaryRow:
    dataset: str
    total: int
    attack_n: int
    benign_n: int
    tp: int
    fp: int
    tn: int
    fn: int
    ir: float
    fpr: float
    acc: float
    latency_ms: float


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze which WAMI components drive final decisions.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--val-data", required=True)
    parser.add_argument("--test-data", action="append", required=True)
    parser.add_argument("--candidate-count", type=int, default=11)
    parser.add_argument("--target-fpr", type=float, default=0.02)
    parser.add_argument("--output-md", default="data/wami_v4_decision_contributions.md")
    parser.add_argument("--output-csv", default="data/wami_v4_decision_contributions.csv")
    args = parser.parse_args()

    model = TorchWAMIModel.load(args.model)
    val = load_plan_samples(args.val_data)
    gateway, calibration = greedy_calibrate_gateway(
        model,
        val,
        tau_init=0.15,
        target_fpr=args.target_fpr,
        candidate_count=args.candidate_count,
    )

    all_rows: list[Row] = []
    summaries: list[SummaryRow] = []
    for path in args.test_data:
        dataset = Path(path).stem
        samples = load_plan_samples(path)
        summary, reason_rows = analyze_dataset(dataset, gateway, samples)
        summaries.append(summary)
        all_rows.extend(reason_rows)

    write_outputs(
        summaries,
        all_rows,
        Path(args.output_md),
        Path(args.output_csv),
        calibration.base_threshold,
        args.val_data,
    )
    print(format_summary(summaries))
    print(f"saved markdown to {args.output_md}")
    print(f"saved csv to {args.output_csv}")


def analyze_dataset(dataset, gateway, samples):
    reason_counts = {"attack": Counter(), "benign": Counter()}
    tp = fp = tn = fn = 0
    started = time.perf_counter()
    for sample in samples:
        decision = gateway.inspect(sample.intent, sample.plan)
        actual_attack = sample.label == 1
        predicted_attack = not decision.allowed
        label_name = "attack" if actual_attack else "benign"
        reason_counts[label_name][decision.reason] += 1
        if predicted_attack and actual_attack:
            tp += 1
        elif predicted_attack and not actual_attack:
            fp += 1
        elif not predicted_attack and actual_attack:
            fn += 1
        else:
            tn += 1
    latency = (time.perf_counter() - started) * 1000.0 / max(1, len(samples))
    attack_n = tp + fn
    benign_n = fp + tn
    rows = []
    for label_name, counter in reason_counts.items():
        denom = max(1, attack_n if label_name == "attack" else benign_n)
        for reason, count in counter.most_common():
            rows.append(Row(dataset, label_name, reason, count, count / denom))
    total = max(1, len(samples))
    summary = SummaryRow(
        dataset=dataset,
        total=len(samples),
        attack_n=attack_n,
        benign_n=benign_n,
        tp=tp,
        fp=fp,
        tn=tn,
        fn=fn,
        ir=tp / max(1, attack_n),
        fpr=fp / max(1, benign_n),
        acc=(tp + tn) / total,
        latency_ms=latency,
    )
    return summary, rows


def format_summary(summaries: list[SummaryRow]) -> str:
    lines = [
        "| Dataset | IR | FPR | ACC | TP | FP | TN | FN | Latency ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            f"| {row.dataset} | {row.ir * 100:.1f}% | {row.fpr * 100:.1f}% | "
            f"{row.acc * 100:.1f}% | {row.tp} | {row.fp} | {row.tn} | {row.fn} | {row.latency_ms:.3f} |"
        )
    return "\n".join(lines)


def format_reason_table(rows: list[Row]) -> str:
    lines = [
        "| Dataset | Label | Decision reason | Count | Share |",
        "|---|---|---|---:|---:|",
    ]
    for row in rows:
        lines.append(f"| {row.dataset} | {row.label} | {row.reason} | {row.count} | {row.share * 100:.1f}% |")
    return "\n".join(lines)


def write_outputs(
    summaries: list[SummaryRow],
    reason_rows: list[Row],
    md_path: Path,
    csv_path: Path,
    tau: float,
    val_data: str,
) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "# WAMI v4 Decision Contribution Analysis\n\n"
        f"- Calibration data: `{val_data}`\n"
        f"- Calibrated tau: `{tau:.4f}`\n\n"
        "## Summary\n\n"
        + format_summary(summaries)
        + "\n\n## Decision Reasons\n\n"
        + format_reason_table(reason_rows)
        + "\n",
        encoding="utf-8",
    )
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in reason_rows:
            writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
