from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys
import time

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.datasets import load_plan_samples
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
    threshold: float


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a validation-only learned ensemble gate for two WAMI models.")
    parser.add_argument("--model-a", required=True)
    parser.add_argument("--model-b", required=True)
    parser.add_argument("--val-data", required=True)
    parser.add_argument("--test-data", action="append", required=True)
    parser.add_argument("--tau-a", type=float, default=-4.5)
    parser.add_argument("--tau-b", type=float, default=-4.5)
    parser.add_argument("--target-fpr", type=float, default=0.05)
    parser.add_argument("--output-md", default="data/paper_mine_ensemble_gate_results.md")
    parser.add_argument("--output-csv", default="data/paper_mine_ensemble_gate_results.csv")
    args = parser.parse_args()

    gw_a = make_gateway(TorchWAMIModel.load(args.model_a), args.tau_a)
    gw_b = make_gateway(TorchWAMIModel.load(args.model_b), args.tau_b)
    x_val, y_val = features(gw_a, gw_b, load_plan_samples(args.val_data))
    w, b = train_logreg(x_val, y_val)
    probs = sigmoid(x_val @ w + b)
    threshold = choose_threshold(probs, y_val, args.target_fpr)

    rows = []
    for path in args.test_data:
        samples = load_plan_samples(path)
        started = time.perf_counter()
        x_test, y_test = features(gw_a, gw_b, samples)
        pred = sigmoid(x_test @ w + b) >= threshold
        latency = (time.perf_counter() - started) * 1000.0 / max(1, len(samples))
        ir, fpr, acc = metrics(pred, y_test)
        rows.append(Row(Path(path).stem, ir, fpr, acc, latency, len(samples), threshold))
    write_outputs(Path(args.output_md), Path(args.output_csv), rows, args, w, b)
    print(format_table(rows))


def make_gateway(model, tau):
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


def features(gw_a, gw_b, samples):
    xs = []
    ys = []
    for sample in samples:
        da = gw_a.inspect(sample.intent, sample.plan)
        db = gw_b.inspect(sample.intent, sample.plan)
        xs.append(
            [
                float(not da.allowed),
                float(not db.allowed),
                da.score,
                da.threshold,
                da.score - da.threshold,
                db.score,
                db.threshold,
                db.score - db.threshold,
                float(da.step if da.step is not None else -1),
                float(db.step if db.step is not None else -1),
            ]
        )
        ys.append(float(sample.label))
    x = np.asarray(xs, dtype=np.float64)
    x = (x - x.mean(axis=0, keepdims=True)) / (x.std(axis=0, keepdims=True) + 1e-6)
    return x, np.asarray(ys, dtype=np.float64)


def train_logreg(x, y, epochs=1000, lr=0.05):
    w = np.zeros(x.shape[1], dtype=np.float64)
    b = 0.0
    pos_weight = (len(y) - y.sum()) / max(1.0, y.sum())
    weights = np.where(y > 0.5, pos_weight, 1.0)
    for _ in range(epochs):
        p = sigmoid(x @ w + b)
        err = (p - y) * weights
        w -= lr * (x.T @ err / len(y) + 1e-3 * w)
        b -= lr * float(err.mean())
    return w, b


def choose_threshold(probs, y, target_fpr):
    best = 0.5
    best_key = (-1.0, -1.0)
    for t in sorted(set(float(v) for v in probs), reverse=True):
        ir, fpr, acc = metrics(probs >= t, y)
        if fpr <= target_fpr and (ir, acc) > best_key:
            best = t
            best_key = (ir, acc)
    return best


def metrics(pred, y):
    actual = y > 0.5
    tp = int(np.logical_and(pred, actual).sum())
    fp = int(np.logical_and(pred, ~actual).sum())
    tn = int(np.logical_and(~pred, ~actual).sum())
    fn = int(np.logical_and(~pred, actual).sum())
    return tp / max(1, tp + fn), fp / max(1, fp + tn), (tp + tn) / max(1, len(y))


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40, 40)))


def format_table(rows):
    lines = ["| Dataset | IR | FPR | ACC | Latency ms | N | Threshold |", "|---|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row.dataset} | {row.ir*100:.1f}% | {row.fpr*100:.1f}% | {row.acc*100:.1f}% | {row.latency_ms:.3f} | {row.n} | {row.threshold:.4f} |")
    return "\n".join(lines)


def write_outputs(md, csv_path, rows, args, w, b):
    md.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md.write_text(
        "# Learned WAMI Ensemble Gate\n\n"
        f"- Model A: `{args.model_a}`\n"
        f"- Model B: `{args.model_b}`\n"
        f"- Validation data: `{args.val_data}`\n"
        f"- Weights: `{', '.join(f'{v:.4f}' for v in w)}`\n"
        f"- Bias: `{b:.4f}`\n\n"
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
