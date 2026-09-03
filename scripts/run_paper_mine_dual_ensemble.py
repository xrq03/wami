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
    parser = argparse.ArgumentParser(description="Evaluate dual WAMI MINE ensemble.")
    parser.add_argument("--model-a", required=True)
    parser.add_argument("--model-b", required=True)
    parser.add_argument("--tau-a", type=float, required=True)
    parser.add_argument("--tau-b", type=float, required=True)
    parser.add_argument("--mode", choices=["or", "and"], default="or")
    parser.add_argument("--test-data", action="append", required=True)
    parser.add_argument("--risk-margin", type=float, default=0.0)
    parser.add_argument("--passive-margin", type=float, default=0.15)
    parser.add_argument("--output-md", default="data/wami_dual_ensemble.md")
    parser.add_argument("--output-csv", default="data/wami_dual_ensemble.csv")
    args = parser.parse_args()

    gateway_a = make_gateway(args.model_a, args.tau_a, args)
    gateway_b = make_gateway(args.model_b, args.tau_b, args)
    rows = []
    for path in args.test_data:
        samples = load_plan_samples(path)
        started = time.perf_counter()
        tp = fp = tn = fn = 0
        for sample in samples:
            blocked_a = not gateway_a.inspect(sample.intent, sample.plan).allowed
            blocked_b = not gateway_b.inspect(sample.intent, sample.plan).allowed
            predicted = blocked_a or blocked_b if args.mode == "or" else blocked_a and blocked_b
            actual = sample.label == 1
            if predicted and actual:
                tp += 1
            elif predicted and not actual:
                fp += 1
            elif not predicted and actual:
                fn += 1
            else:
                tn += 1
        latency = (time.perf_counter() - started) * 1000.0 / max(1, len(samples))
        rows.append(
            Row(
                dataset=Path(path).stem,
                mode=args.mode,
                ir=tp / max(1, tp + fn),
                fpr=fp / max(1, fp + tn),
                acc=(tp + tn) / max(1, len(samples)),
                latency_ms=latency,
                n=len(samples),
            )
        )
    write_outputs(rows, Path(args.output_md), Path(args.output_csv), args)
    print(format_table(rows))


def make_gateway(model_path: str, tau: float, args) -> PaperMINEGateway:
    return PaperMINEGateway(
        TorchWAMIModel.load(model_path),
        PaperMINEConfig(
            base_threshold=tau,
            plan_threshold=tau,
            risk_margin=args.risk_margin,
            passive_margin=args.passive_margin,
            use_transition_mine=True,
            use_auxiliary_heads=True,
            use_provenance_memory=True,
        ),
    )


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_table(rows: list[Row]) -> str:
    lines = ["| Dataset | Mode | IR | FPR | ACC | Latency ms | N |", "|---|---|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row.dataset} | {row.mode.upper()} | {pct(row.ir)} | {pct(row.fpr)} | "
            f"{pct(row.acc)} | {row.latency_ms:.3f} | {row.n} |"
        )
    return "\n".join(lines)


def write_outputs(rows: list[Row], md_path: Path, csv_path: Path, args) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "# Dual Paper-MINE WAMI Ensemble\n\n"
        f"- Model A: `{args.model_a}`, tau `{args.tau_a}`\n"
        f"- Model B: `{args.model_b}`, tau `{args.tau_b}`\n"
        f"- Mode: `{args.mode}`\n"
        f"- Risk margin: `{args.risk_margin}`\n"
        f"- Passive margin: `{args.passive_margin}`\n\n"
        + format_table(rows)
        + "\n",
        encoding="utf-8",
    )
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        writer.writerows([row.__dict__ for row in rows])


if __name__ == "__main__":
    main()
