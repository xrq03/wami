from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys
import time

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.gateway import WAMIGateway
from wami.model import WAMIConfig, WAMIModel
from wami.tdg import build_tdg
from wami.training import load_jsonl, train_shadow


@dataclass
class ScoreRow:
    label: int
    score: float


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/agentdojo_wami.jsonl")
    parser.add_argument("--model", default="wami_agentdojo_final_tuned_e5.npz")
    parser.add_argument("--dataset-name", default="")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--out-prefix", default="data/wami_extra_agentdojo")
    args = parser.parse_args()

    samples = load_jsonl(args.data)
    model = WAMIModel.load(args.model) if Path(args.model).exists() else WAMIModel()
    dataset = args.dataset_name or Path(args.data).stem.replace("_wami", "")
    prefix = Path(args.out_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)

    scores = score_samples(model, samples)
    write_threshold_sensitivity(dataset, scores, prefix.with_name(prefix.name + "_threshold_sensitivity.csv"), prefix.with_name(prefix.name + "_threshold_sensitivity.md"))
    write_roc(dataset, scores, prefix.with_name(prefix.name + "_roc.csv"), prefix.with_name(prefix.name + "_roc.md"))
    write_latency_breakdown(dataset, model, samples, prefix.with_name(prefix.name + "_latency_breakdown.csv"), prefix.with_name(prefix.name + "_latency_breakdown.md"))
    write_capability_proxy(dataset, model, samples, prefix.with_name(prefix.name + "_capability_proxy.csv"), prefix.with_name(prefix.name + "_capability_proxy.md"))
    write_training_dynamics(dataset, samples, args.epochs, prefix.with_name(prefix.name + "_training_dynamics.csv"), prefix.with_name(prefix.name + "_training_dynamics.md"))


def score_samples(model: WAMIModel, samples) -> list[ScoreRow]:
    rows = []
    for sample in samples:
        intent_vec = model.encode_intent(sample.intent)
        step_scores = [model.mine_score(intent_vec, state) for _node, state in model.rollout(sample.intent, build_tdg(sample.plan))]
        rows.append(ScoreRow(sample.label, min(step_scores) if step_scores else model.plan_score(sample.intent, sample.plan)))
    return rows


def metrics_at_threshold(scores: list[ScoreRow], threshold: float) -> tuple[float, float, float]:
    tp = fp = tn = fn = 0
    for row in scores:
        predicted_attack = row.score < threshold
        actual_attack = row.label == 1
        if predicted_attack and actual_attack:
            tp += 1
        elif predicted_attack and not actual_attack:
            fp += 1
        elif not predicted_attack and actual_attack:
            fn += 1
        else:
            tn += 1
    total = max(1, tp + fp + tn + fn)
    return tp / max(1, tp + fn), fp / max(1, fp + tn), (tp + tn) / total


def write_threshold_sensitivity(dataset: str, scores: list[ScoreRow], csv_path: Path, md_path: Path) -> None:
    values = np.array([row.score for row in scores], dtype=float)
    thresholds = np.quantile(values, [0.01, 0.03, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50])
    rows = []
    for tau in thresholds:
        ir, fpr, acc = metrics_at_threshold(scores, float(tau))
        rows.append({"dataset": dataset, "threshold": float(tau), "ir": ir, "fpr": fpr, "acc": acc})
    write_csv(csv_path, rows)
    write_md(md_path, ["Dataset", "Threshold", "IR", "FPR", "ACC"], [
        [r["dataset"], f"{r['threshold']:.4f}", pct(r["ir"]), pct(r["fpr"]), pct(r["acc"])] for r in rows
    ])
    print(f"saved threshold sensitivity to {md_path}")


def write_roc(dataset: str, scores: list[ScoreRow], csv_path: Path, md_path: Path) -> None:
    thresholds = sorted({row.score for row in scores})
    points = []
    for tau in thresholds:
        tpr, fpr, _acc = metrics_at_threshold(scores, tau)
        points.append((fpr, tpr, tau))
    points = [(0.0, 0.0, float("-inf"))] + sorted(points) + [(1.0, 1.0, float("inf"))]
    auc = 0.0
    for (x0, y0, _), (x1, y1, __) in zip(points, points[1:]):
        auc += (x1 - x0) * (y0 + y1) / 2.0
    rows = [{"dataset": dataset, "fpr": fpr, "tpr": tpr, "threshold": tau, "auc": auc} for fpr, tpr, tau in points]
    write_csv(csv_path, rows)
    sample_points = points[:: max(1, len(points) // 8)]
    write_md(md_path, ["Dataset", "AUC", "FPR", "TPR", "Threshold"], [
        [dataset, f"{auc:.3f}", f"{fpr:.3f}", f"{tpr:.3f}", f"{tau:.4f}" if np.isfinite(tau) else str(tau)] for fpr, tpr, tau in sample_points
    ])
    print(f"saved ROC to {md_path}")


def write_latency_breakdown(dataset: str, model: WAMIModel, samples, csv_path: Path, md_path: Path, limit: int = 300) -> None:
    tdg_ms = rollout_ms = mine_ms = total_ms = 0.0
    subset = samples[: min(limit, len(samples))]
    for sample in subset:
        t0 = time.perf_counter()
        tdg = build_tdg(sample.plan)
        t1 = time.perf_counter()
        trajectory = model.rollout(sample.intent, tdg)
        t2 = time.perf_counter()
        intent_vec = model.encode_intent(sample.intent)
        for _node, state in trajectory:
            model.mine_score(intent_vec, state)
        t3 = time.perf_counter()
        tdg_ms += (t1 - t0) * 1000
        rollout_ms += (t2 - t1) * 1000
        mine_ms += (t3 - t2) * 1000
        total_ms += (t3 - t0) * 1000
    n = max(1, len(subset))
    rows = [
        {"dataset": dataset, "component": "TDG construction", "latency_ms": tdg_ms / n},
        {"dataset": dataset, "component": "World model rollout", "latency_ms": rollout_ms / n},
        {"dataset": dataset, "component": "MINE gateway scoring", "latency_ms": mine_ms / n},
        {"dataset": dataset, "component": "Total measured", "latency_ms": total_ms / n},
    ]
    write_csv(csv_path, rows)
    write_md(md_path, ["Dataset", "Component", "Latency ms"], [[r["dataset"], r["component"], f"{r['latency_ms']:.4f}"] for r in rows])
    print(f"saved latency breakdown to {md_path}")


def write_capability_proxy(dataset: str, model: WAMIModel, samples, csv_path: Path, md_path: Path) -> None:
    benign = [sample for sample in samples if sample.label == 0]
    gateway = WAMIGateway(model)
    allowed = sum(1 for sample in benign if gateway.inspect(sample.intent, sample.plan).allowed)
    retention = allowed / max(1, len(benign))
    rows = [
        {"dataset": dataset, "system": "No Defense", "benign_allow_rate": 1.0, "capability_retention_proxy": 1.0, "benign_n": len(benign)},
        {"dataset": dataset, "system": "WAMI", "benign_allow_rate": retention, "capability_retention_proxy": retention, "benign_n": len(benign)},
    ]
    write_csv(csv_path, rows)
    write_md(md_path, ["Dataset", "System", "Benign Allow Rate", "Capability Retention Proxy", "Benign N"], [
        [r["dataset"], r["system"], pct(r["benign_allow_rate"]), pct(r["capability_retention_proxy"]), str(r["benign_n"])] for r in rows
    ])
    print(f"saved capability proxy to {md_path}")


def write_training_dynamics(dataset: str, samples, epochs: int, csv_path: Path, md_path: Path) -> None:
    model = WAMIModel(WAMIConfig())
    stats = train_shadow(model, samples=samples, epochs=epochs)
    rows = [{"dataset": dataset, "epoch": s.epoch, "loss": s.loss, "mi_gap": s.mi_gap} for s in stats]
    write_csv(csv_path, rows)
    keep = rows[:5] + rows[5::5]
    write_md(md_path, ["Dataset", "Epoch", "Loss", "MI Gap"], [
        [r["dataset"], str(r["epoch"]), f"{r['loss']:.4f}", f"{r['mi_gap']:.4f}"] for r in keep
    ])
    print(f"saved training dynamics to {md_path}")


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
