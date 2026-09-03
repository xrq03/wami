from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.datasets import load_plan_samples
from wami.evaluate import Metrics
from wami.paper_mine_gateway import PaperMINEConfig, PaperMINEGateway
from wami.torch_model import TorchWAMIModel


@dataclass
class Row:
    dataset: str
    ir: float
    fpr: float
    acc: float
    latency_ms: float
    n: int
    tau: float


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate paper-faithful MINE-dominant WAMI.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--val-data", required=True)
    parser.add_argument("--test-data", action="append", required=True)
    parser.add_argument("--candidate-count", type=int, default=21)
    parser.add_argument("--target-fpr", type=float, default=0.05)
    parser.add_argument("--tau-init", type=float, default=0.15)
    parser.add_argument("--candidate-radius", type=float, default=2.0)
    parser.add_argument("--risk-margin", type=float, default=0.15)
    parser.add_argument("--passive-margin", type=float, default=0.10)
    parser.add_argument("--use-transition-mine", action="store_true")
    parser.add_argument("--transition-fusion", type=float, default=0.35)
    parser.add_argument("--use-auxiliary-heads", action="store_true")
    parser.add_argument("--auxiliary-fusion", type=float, default=0.20)
    parser.add_argument("--use-provenance-memory", action="store_true")
    parser.add_argument("--provenance-fusion", type=float, default=0.10)
    parser.add_argument("--output-md", default="data/paper_mine_gateway_results.md")
    parser.add_argument("--output-csv", default="data/paper_mine_gateway_results.csv")
    args = parser.parse_args()

    model = TorchWAMIModel.load(args.model)
    val = load_plan_samples(args.val_data)
    gateway, tau = calibrate(model, val, args)
    rows = []
    for path in args.test_data:
        samples = load_plan_samples(path)
        started = time.perf_counter()
        metrics = evaluate(gateway, samples)
        latency = (time.perf_counter() - started) * 1000.0 / max(1, len(samples))
        rows.append(Row(Path(path).stem, metrics.interception_rate, metrics.false_positive_rate, metrics.accuracy, latency, len(samples), tau))
    write_outputs(rows, Path(args.output_md), Path(args.output_csv), args)
    print(format_table(rows))


def calibrate(model, val, args):
    candidates = candidate_thresholds(args.tau_init, args.candidate_radius, args.candidate_count)
    all_results = []
    feasible = []
    for tau in candidates:
        gateway = PaperMINEGateway(
            model,
            PaperMINEConfig(
                base_threshold=tau,
                plan_threshold=tau,
                risk_margin=args.risk_margin,
                passive_margin=args.passive_margin,
                use_transition_mine=args.use_transition_mine,
                transition_fusion=args.transition_fusion,
                use_auxiliary_heads=args.use_auxiliary_heads,
                auxiliary_fusion=args.auxiliary_fusion,
                use_provenance_memory=args.use_provenance_memory,
                provenance_fusion=args.provenance_fusion,
            ),
        )
        metrics = evaluate(gateway, val)
        item = (gateway, tau, metrics)
        all_results.append(item)
        if metrics.false_positive_rate <= args.target_fpr:
            feasible.append(item)
    selected = max(feasible or all_results, key=lambda item: (item[2].interception_rate, item[2].accuracy, -item[2].false_positive_rate))
    return selected[0], selected[1]


def candidate_thresholds(center: float, radius: float, count: int) -> list[float]:
    if count <= 1:
        return [center]
    step = (radius * 2.0) / (count - 1)
    return [center - radius + step * i for i in range(count)]


def evaluate(gateway, samples) -> Metrics:
    tp = fp = tn = fn = 0
    for sample in samples:
        decision = gateway.inspect(sample.intent, sample.plan)
        predicted = not decision.allowed
        actual = sample.label == 1
        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and actual:
            fn += 1
        else:
            tn += 1
    total = max(1, len(samples))
    return Metrics(tp / max(1, tp + fn), fp / max(1, fp + tn), (tp + tn) / total, total)


def format_table(rows: list[Row]) -> str:
    lines = ["| Dataset | IR | FPR | ACC | Latency ms | N | Tau |", "|---|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row.dataset} | {row.ir * 100:.1f}% | {row.fpr * 100:.1f}% | "
            f"{row.acc * 100:.1f}% | {row.latency_ms:.3f} | {row.n} | {row.tau:.4f} |"
        )
    return "\n".join(lines)


def write_outputs(rows: list[Row], md_path: Path, csv_path: Path, args) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "# Paper-Faithful MINE-Dominant WAMI\n\n"
        "- Blocking source: plan-level and trajectory-level MINE scores.\n"
        "- Tool/security heuristics are margins only, not direct veto rules.\n"
        f"- Validation data: `{args.val_data}`\n"
        f"- Target FPR on generated validation: `{args.target_fpr}`\n"
        f"- Risk margin: `{args.risk_margin}`\n"
        f"- Passive margin: `{args.passive_margin}`\n\n"
        f"- Transition MINE: `{args.use_transition_mine}`\n\n"
        f"- Transition fusion: `{args.transition_fusion}`\n\n"
        f"- Source-aware auxiliary heads: `{args.use_auxiliary_heads}`\n\n"
        f"- Auxiliary fusion: `{args.auxiliary_fusion}`\n\n"
        f"- Provenance memory: `{args.use_provenance_memory}`\n\n"
        f"- Provenance fusion: `{args.provenance_fusion}`\n\n"
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
