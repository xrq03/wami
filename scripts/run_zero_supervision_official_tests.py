from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.datasets import load_plan_samples
from wami.evaluate import evaluate_gateway
from wami.paper_calibration import greedy_calibrate_gateway
from wami.torch_model import TorchWAMIModel


@dataclass
class Row:
    dataset: str
    ir: float
    fpr: float
    acc: float
    latency_ms: float
    n: int


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--val-data", required=True)
    parser.add_argument("--test-data", action="append", required=True)
    parser.add_argument("--output-md", default="data/wami_paper_strict_zero_supervision_test.md")
    parser.add_argument("--output-csv", default="data/wami_paper_strict_zero_supervision_test.csv")
    parser.add_argument("--target-fpr", type=float, default=0.02)
    parser.add_argument("--candidate-count", type=int, default=11)
    parser.add_argument("--progress-every", type=int, default=100)
    args = parser.parse_args()

    model = TorchWAMIModel.load(args.model)
    val = load_plan_samples(args.val_data)
    print(f"calibrating on {args.val_data} n={len(val)} candidates={args.candidate_count}", flush=True)
    gateway, calibration = greedy_calibrate_gateway(
        model,
        val,
        tau_init=0.15,
        target_fpr=args.target_fpr,
        candidate_count=args.candidate_count,
    )
    rows = []
    for path in args.test_data:
        samples = load_plan_samples(path)
        start = time.perf_counter()
        metrics = evaluate_with_progress(gateway, samples, Path(path).stem, args.progress_every)
        latency = (time.perf_counter() - start) * 1000.0 / max(1, len(samples))
        rows.append(Row(Path(path).stem, metrics.interception_rate, metrics.false_positive_rate, metrics.accuracy, latency, len(samples)))
    write_outputs(rows, Path(args.output_md), Path(args.output_csv), args, calibration.base_threshold)
    print(format_table(rows))
    print(f"calibrated_tau={calibration.base_threshold:.4f}")


def evaluate_with_progress(gateway, samples, name: str, progress_every: int):
    from wami.evaluate import Metrics

    tp = fp = tn = fn = 0
    start = time.perf_counter()
    for index, sample in enumerate(samples, start=1):
        decision = gateway.inspect(sample.intent, sample.plan)
        predicted_attack = not decision.allowed
        actual_attack = sample.label == 1
        if predicted_attack and actual_attack:
            tp += 1
        elif predicted_attack and not actual_attack:
            fp += 1
        elif not predicted_attack and actual_attack:
            fn += 1
        else:
            tn += 1
        if progress_every > 0 and (index % progress_every == 0 or index == len(samples)):
            elapsed = time.perf_counter() - start
            avg = elapsed / index
            eta = avg * (len(samples) - index)
            print(
                f"{name}: {index}/{len(samples)} "
                f"IR={tp / max(1, tp + fn):.3f} FPR={fp / max(1, fp + tn):.3f} "
                f"avg_ms={avg * 1000.0:.1f} eta_s={eta:.1f}",
                flush=True,
            )
    total = max(1, len(samples))
    return Metrics(
        interception_rate=tp / max(1, tp + fn),
        false_positive_rate=fp / max(1, fp + tn),
        accuracy=(tp + tn) / total,
        total=total,
    )


def format_table(rows: list[Row]) -> str:
    lines = ["| Dataset | IR | FPR | ACC | Latency ms | N |", "|---|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row.dataset} | {row.ir * 100:.1f}% | {row.fpr * 100:.1f}% | {row.acc * 100:.1f}% | {row.latency_ms:.3f} | {row.n} |")
    return "\n".join(lines)


def write_outputs(rows: list[Row], md_path: Path, csv_path: Path, args, tau: float) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "# WAMI Paper-Strict Zero-Supervision Official Tests\n\n"
        "- Official benchmark datasets are used only for testing.\n"
        f"- Calibration data: `{args.val_data}`\n"
        f"- Calibrated tau: `{tau:.4f}`\n\n"
        + format_table(rows)
        + "\n",
        encoding="utf-8",
    )
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
