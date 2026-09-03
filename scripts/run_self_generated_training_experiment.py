from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.calibration import calibrate_gateway
from wami.datasets import load_plan_samples, write_jsonl
from wami.evaluate import evaluate_gateway
from wami.gateway import WAMIGateway
from wami.model import WAMIConfig, WAMIModel
from wami.shadow import PlanSample
from wami.training import train_shadow

from generate_self_training_data import generate_samples


@dataclass
class ResultRow:
    variant: str
    eval_set: str
    train_n: int
    eval_n: int
    ir: float
    fpr: float
    acc: float
    avg_latency_ms: float
    model_path: str


BASE_DATASETS = [
    ("InjecAgent", "data/injecagent_wami.jsonl"),
    ("BIPIA", "data/bipia_wami.jsonl"),
    ("AgentDojo", "data/agentdojo_wami.jsonl"),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic-count", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=31)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--eval-limit", type=int, default=1000)
    parser.add_argument("--init-model", default="wami_agentdojo_current_e3.npz")
    parser.add_argument("--calibrate-on", choices=["base", "augmented", "per_eval"], default="base")
    parser.add_argument("--plan-threshold-cap", type=float, default=-0.25)
    parser.add_argument("--synthetic-output", default="data/self_generated_wami_train_2000.jsonl")
    parser.add_argument("--model-output", default="wami_self_generated_augmented_e3.npz")
    parser.add_argument("--output-md", default="data/self_generated_training_experiment.md")
    parser.add_argument("--output-csv", default="data/self_generated_training_experiment.csv")
    args = parser.parse_args()

    synthetic = generate_samples(args.synthetic_count, args.seed)
    write_jsonl(synthetic, args.synthetic_output)
    base_train = []
    for _, path in BASE_DATASETS:
        base_train.extend(load_plan_samples(path))
    augmented_train = base_train + synthetic

    baseline_model = WAMIModel.load("wami_agentdojo_current_e3.npz")
    augmented_model = WAMIModel.load(args.init_model) if Path(args.init_model).exists() else WAMIModel(WAMIConfig(dim=128, learning_rate=0.03))
    train_shadow(augmented_model, augmented_train, epochs=args.epochs, seed=args.seed)
    augmented_model.save(args.model_output)

    rows: list[ResultRow] = []
    rows.extend(
        evaluate_variant(
            "current_agentdojo_model",
            baseline_model,
            base_train,
            args.eval_limit,
            "wami_agentdojo_current_e3.npz",
            args.plan_threshold_cap,
            args.calibrate_on,
            augmented_train,
        )
    )
    calibration_samples = base_train if args.calibrate_on == "base" else augmented_train
    rows.extend(
        evaluate_variant(
            "self_generated_augmented",
            augmented_model,
            calibration_samples,
            args.eval_limit,
            args.model_output,
            args.plan_threshold_cap,
            args.calibrate_on,
            augmented_train,
        )
    )
    write_outputs(rows, Path(args.output_md), Path(args.output_csv), args)
    print(format_table(rows))
    print(f"saved_synthetic={Path(args.synthetic_output).resolve()}")
    print(f"saved_model={Path(args.model_output).resolve()}")
    print(f"saved_markdown={Path(args.output_md).resolve()}")
    print(f"saved_csv={Path(args.output_csv).resolve()}")


def evaluate_variant(
    name: str,
    model: WAMIModel,
    calibration_samples: list[PlanSample],
    eval_limit: int,
    model_path: str,
    plan_threshold_cap: float | None,
    calibrate_on: str,
    augmented_train: list[PlanSample],
) -> list[ResultRow]:
    rows = []
    for eval_name, path in BASE_DATASETS:
        samples = load_plan_samples(path)
        if eval_limit > 0:
            samples = samples[:eval_limit]
        gateway = build_gateway_for_eval(
            model,
            samples if calibrate_on == "per_eval" else calibration_samples,
            plan_threshold_cap,
        )
        rows.append(evaluate_one(name, eval_name, gateway, samples, len(calibration_samples), model_path))
    synthetic_eval = generate_samples(min(1000, eval_limit if eval_limit > 0 else 1000), 91)
    gateway = build_gateway_for_eval(
        model,
        synthetic_eval if calibrate_on == "per_eval" else calibration_samples,
        plan_threshold_cap,
    )
    rows.append(evaluate_one(name, "SelfGeneratedHoldout", gateway, synthetic_eval, len(calibration_samples), model_path))
    return rows


def build_gateway_for_eval(
    model: WAMIModel,
    calibration_samples: list[PlanSample],
    plan_threshold_cap: float | None,
) -> WAMIGateway:
    gateway = calibrate_gateway(model, calibration_samples, quantile=0.05, margin=0.02)
    gateway.use_plan_mine = True
    if plan_threshold_cap is not None:
        gateway.plan_threshold = min(gateway.plan_threshold, plan_threshold_cap)
    gateway.score_margin = 0.05
    return gateway


def evaluate_one(
    variant: str,
    eval_name: str,
    gateway: WAMIGateway,
    samples: list[PlanSample],
    train_n: int,
    model_path: str,
) -> ResultRow:
    start = time.perf_counter()
    metrics = evaluate_gateway(gateway, samples)
    latency = (time.perf_counter() - start) * 1000.0 / max(1, len(samples))
    return ResultRow(
        variant=variant,
        eval_set=eval_name,
        train_n=train_n,
        eval_n=len(samples),
        ir=metrics.interception_rate,
        fpr=metrics.false_positive_rate,
        acc=metrics.accuracy,
        avg_latency_ms=latency,
        model_path=model_path,
    )


def format_table(rows: list[ResultRow]) -> str:
    lines = [
        "| Variant | Eval Set | Train N | Eval N | IR | FPR | ACC | Avg ms |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row.variant} | {row.eval_set} | {row.train_n} | {row.eval_n} | "
            f"{row.ir * 100:.1f}% | {row.fpr * 100:.1f}% | {row.acc * 100:.1f}% | {row.avg_latency_ms:.3f} |"
        )
    return "\n".join(lines)


def write_outputs(rows: list[ResultRow], md_path: Path, csv_path: Path, args: argparse.Namespace) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    text = (
        "# Self-Generated Training Data Experiment\n\n"
        f"- Synthetic training rows: `{args.synthetic_count}`\n"
        f"- Epochs: `{args.epochs}`\n"
        f"- Init model: `{args.init_model}`\n"
        f"- Eval limit per official dataset: `{args.eval_limit}`\n\n"
        f"- Augmented model calibration set: `{args.calibrate_on}`\n\n"
        f"- Plan threshold cap: `{args.plan_threshold_cap}`\n\n"
        + format_table(rows)
        + "\n\n"
        "The synthetic generator covers benign untrusted-content handling, direct sensitive-tool attacks, "
        "cross-tool injection, multi-step context pollution, visual-instruction following, and hidden-goal shift.\n"
    )
    md_path.write_text(text, encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ResultRow.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
