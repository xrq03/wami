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
from wami.tdg import build_tdg
from wami.torch_model import TorchWAMIModel


@dataclass
class EvalRow:
    dataset: str
    ir: float
    fpr: float
    acc: float
    latency_ms: float
    n: int
    threshold: float


def main() -> None:
    parser = argparse.ArgumentParser(description="Train validation-only learned calibrator for source-aware WAMI scores.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--val-data", required=True)
    parser.add_argument("--test-data", action="append", required=True)
    parser.add_argument("--target-fpr", type=float, default=0.05)
    parser.add_argument("--epochs", type=int, default=1000)
    parser.add_argument("--lr", type=float, default=0.05)
    parser.add_argument("--output-md", default="data/sourceaware_calibrator_results.md")
    parser.add_argument("--output-csv", default="data/sourceaware_calibrator_results.csv")
    args = parser.parse_args()

    model = TorchWAMIModel.load(args.model)
    val_samples = load_plan_samples(args.val_data)
    x_val_raw, y_val = featurize_samples(model, val_samples)
    x_val, center, scale = normalize_fit(x_val_raw)
    weights, bias = train_logreg(x_val, y_val, epochs=args.epochs, lr=args.lr)
    val_probs = sigmoid(x_val @ weights + bias)
    threshold = choose_threshold(val_probs, y_val, args.target_fpr)

    rows: list[EvalRow] = []
    for path in args.test_data:
        samples = load_plan_samples(path)
        started = time.perf_counter()
        x_test_raw, y_test = featurize_samples(model, samples)
        x_test = normalize_apply(x_test_raw, center, scale)
        probs = sigmoid(x_test @ weights + bias)
        latency = (time.perf_counter() - started) * 1000.0 / max(1, len(samples))
        ir, fpr, acc = metrics(probs >= threshold, y_test)
        rows.append(EvalRow(Path(path).stem, ir, fpr, acc, latency, len(samples), threshold))
    write_outputs(Path(args.output_md), Path(args.output_csv), rows, args, weights, bias)
    print(format_table(rows))


def featurize_samples(model: TorchWAMIModel, samples) -> tuple[np.ndarray, np.ndarray]:
    features = []
    labels = []
    for sample in samples:
        features.append(featurize_sample(model, sample.intent, sample.plan))
        labels.append(float(sample.label))
    return np.asarray(features, dtype=np.float64), np.asarray(labels, dtype=np.float64)


def normalize_fit(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    center = x.mean(axis=0, keepdims=True)
    scale = x.std(axis=0, keepdims=True) + 1e-6
    return (x - center) / scale, center, scale


def normalize_apply(x: np.ndarray, center: np.ndarray, scale: np.ndarray) -> np.ndarray:
    return (x - center) / scale


def featurize_sample(model: TorchWAMIModel, intent: str, plan: str) -> list[float]:
    tdg = build_tdg(plan)
    intent_vec = model.encode_intent(intent)
    plan_score = model.plan_score(intent, plan)
    scores = [plan_score]
    transition_scores = []
    source_logits = []
    drift_logits = []
    sink_logits = []
    step_count = 0
    if tdg.nodes:
        for item in model.cognitive_rollout(intent, tdg):
            step_count += 1
            state_score = model.mine_score(intent_vec, item["state"])
            transition_score = model.transition_score(
                intent_vec,
                item["previous_state"],
                item["action"],
                item["observation"],
                item["state"],
            )
            source_logit, drift_logit, sink_logit = model.aux_scores(
                intent_vec,
                item["previous_state"],
                item["action"],
                item["observation"],
                item["state"],
            )
            scores.append(state_score)
            transition_scores.append(transition_score)
            source_logits.append(source_logit)
            drift_logits.append(drift_logit)
            sink_logits.append(sink_logit)
    return [
        min(scores),
        mean(scores),
        plan_score,
        min_or_zero(transition_scores),
        mean(transition_scores),
        max_or_zero(source_logits),
        mean(source_logits),
        max_or_zero(drift_logits),
        mean(drift_logits),
        min_or_zero(sink_logits),
        mean(sink_logits),
        float(step_count),
    ]


def train_logreg(x: np.ndarray, y: np.ndarray, epochs: int, lr: float) -> tuple[np.ndarray, float]:
    weights = np.zeros(x.shape[1], dtype=np.float64)
    bias = 0.0
    pos_weight = (len(y) - y.sum()) / max(1.0, y.sum())
    sample_weight = np.where(y > 0.5, pos_weight, 1.0)
    for _ in range(epochs):
        probs = sigmoid(x @ weights + bias)
        err = (probs - y) * sample_weight
        weights -= lr * (x.T @ err / len(y) + 1e-3 * weights)
        bias -= lr * float(err.mean())
    return weights, bias


def choose_threshold(probs: np.ndarray, y: np.ndarray, target_fpr: float) -> float:
    candidates = sorted(set(float(v) for v in probs), reverse=True)
    best = candidates[0] if candidates else 0.5
    best_key = (-1.0, -1.0)
    for threshold in candidates:
        ir, fpr, acc = metrics(probs >= threshold, y)
        if fpr <= target_fpr and (ir, acc) > best_key:
            best = threshold
            best_key = (ir, acc)
    if best_key[0] < 0:
        best = max(candidates, key=lambda t: metrics(probs >= t, y)[2]) if candidates else 0.5
    return float(best)


def metrics(predicted: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    actual = y > 0.5
    tp = int(np.logical_and(predicted, actual).sum())
    fp = int(np.logical_and(predicted, ~actual).sum())
    tn = int(np.logical_and(~predicted, ~actual).sum())
    fn = int(np.logical_and(~predicted, actual).sum())
    return tp / max(1, tp + fn), fp / max(1, fp + tn), (tp + tn) / max(1, len(y))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40, 40)))


def mean(values: list[float]) -> float:
    return float(np.mean(values)) if values else 0.0


def min_or_zero(values: list[float]) -> float:
    return min(values) if values else 0.0


def max_or_zero(values: list[float]) -> float:
    return max(values) if values else 0.0


def format_table(rows: list[EvalRow]) -> str:
    lines = ["| Dataset | IR | FPR | ACC | Latency ms | N | Threshold |", "|---|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row.dataset} | {row.ir * 100:.1f}% | {row.fpr * 100:.1f}% | {row.acc * 100:.1f}% | "
            f"{row.latency_ms:.3f} | {row.n} | {row.threshold:.4f} |"
        )
    return "\n".join(lines)


def write_outputs(md_path: Path, csv_path: Path, rows: list[EvalRow], args, weights: np.ndarray, bias: float) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "# Source-Aware Learned Calibrator\n\n"
        f"- Model: `{args.model}`\n"
        f"- Validation data: `{args.val_data}`\n"
        f"- Target validation FPR: `{args.target_fpr}`\n"
        f"- Calibrator: logistic regression over learned WAMI features\n"
        f"- Bias: `{bias:.6f}`\n"
        f"- Weights: `{', '.join(f'{v:.4f}' for v in weights)}`\n\n"
        + format_table(rows)
        + "\n",
        encoding="utf-8",
    )
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(EvalRow.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
