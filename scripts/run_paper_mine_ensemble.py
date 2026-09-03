from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.datasets import load_plan_samples
from wami.paper_mine_gateway import PaperMINEConfig, PaperMINEGateway
from wami.torch_model import TorchWAMIModel


@dataclass
class Row:
    dataset: str
    mode: str
    ir: float
    fpr: float
    acc: float
    latency_ms: float
    n: int


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate an ensemble of two learned paper-MINE WAMI gateways.")
    parser.add_argument("--model-a", required=True)
    parser.add_argument("--model-b", required=True)
    parser.add_argument("--test-data", action="append", required=True)
    parser.add_argument("--tau-a", type=float, default=-4.5)
    parser.add_argument("--tau-b", type=float, default=-4.5)
    parser.add_argument("--transition-fusion-a", type=float, default=0.35)
    parser.add_argument("--transition-fusion-b", type=float, default=0.35)
    parser.add_argument("--auxiliary-fusion-a", type=float, default=0.10)
    parser.add_argument("--auxiliary-fusion-b", type=float, default=0.10)
    parser.add_argument("--use-provenance-b", action="store_true")
    parser.add_argument("--provenance-fusion-b", type=float, default=0.0)
    parser.add_argument("--output-md", default="data/paper_mine_ensemble_results.md")
    parser.add_argument("--output-csv", default="data/paper_mine_ensemble_results.csv")
    args = parser.parse_args()

    gateway_a = make_gateway(
        TorchWAMIModel.load(args.model_a),
        args.tau_a,
        args.transition_fusion_a,
        args.auxiliary_fusion_a,
        False,
        0.0,
    )
    gateway_b = make_gateway(
        TorchWAMIModel.load(args.model_b),
        args.tau_b,
        args.transition_fusion_b,
        args.auxiliary_fusion_b,
        args.use_provenance_b,
        args.provenance_fusion_b,
    )
    rows = []
    for path in args.test_data:
        samples = load_plan_samples(path)
        dataset = Path(path).stem
        started = time.perf_counter()
        decisions = [(not gateway_a.inspect(s.intent, s.plan).allowed, not gateway_b.inspect(s.intent, s.plan).allowed, s.label == 1) for s in samples]
        latency = (time.perf_counter() - started) * 1000.0 / max(1, len(samples))
        for mode in ("a", "b", "or", "and", "b_or_agree"):
            predicted = []
            actual = []
            for a, b, label in decisions:
                if mode == "a":
                    pred = a
                elif mode == "b":
                    pred = b
                elif mode == "or":
                    pred = a or b
                elif mode == "and":
                    pred = a and b
                else:
                    pred = b
                predicted.append(pred)
                actual.append(label)
            ir, fpr, acc = metrics(predicted, actual)
            rows.append(Row(dataset, mode, ir, fpr, acc, latency, len(samples)))
    write_outputs(Path(args.output_md), Path(args.output_csv), rows, args)
    print(format_table(rows))


def make_gateway(model, tau: float, transition_fusion: float, auxiliary_fusion: float, use_provenance: bool, provenance_fusion: float):
    return PaperMINEGateway(
        model,
        PaperMINEConfig(
            base_threshold=tau,
            plan_threshold=tau,
            use_transition_mine=True,
            transition_fusion=transition_fusion,
            use_auxiliary_heads=True,
            auxiliary_fusion=auxiliary_fusion,
            use_provenance_memory=use_provenance,
            provenance_fusion=provenance_fusion,
        ),
    )


def metrics(predicted: list[bool], actual: list[bool]) -> tuple[float, float, float]:
    tp = fp = tn = fn = 0
    for pred, label in zip(predicted, actual):
        if pred and label:
            tp += 1
        elif pred and not label:
            fp += 1
        elif not pred and label:
            fn += 1
        else:
            tn += 1
    return tp / max(1, tp + fn), fp / max(1, fp + tn), (tp + tn) / max(1, len(actual))


def format_table(rows: list[Row]) -> str:
    lines = ["| Dataset | Mode | IR | FPR | ACC | Latency ms | N |", "|---|---|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row.dataset} | {row.mode} | {row.ir * 100:.1f}% | {row.fpr * 100:.1f}% | "
            f"{row.acc * 100:.1f}% | {row.latency_ms:.3f} | {row.n} |"
        )
    return "\n".join(lines)


def write_outputs(md_path: Path, csv_path: Path, rows: list[Row], args) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "# Paper-MINE Learned Ensemble\n\n"
        f"- Model A: `{args.model_a}`\n"
        f"- Model B: `{args.model_b}`\n"
        f"- Tau A/B: `{args.tau_a}`, `{args.tau_b}`\n"
        "- Modes: `a`, `b`, `or`, `and`\n\n"
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
