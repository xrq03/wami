from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.datasets import load_plan_samples
from wami.gateway import WAMIGateway
from wami.paper_mine_gateway import PaperMINEConfig, PaperMINEGateway
from wami.tdg import build_tdg
from wami.torch_model import TorchWAMIModel


@dataclass
class ScoreRow:
    dataset: str
    index: int
    label: int
    blocked: int
    min_score: float
    min_threshold: float
    min_margin: float
    block_boundary: float
    plan_score: float
    plan_threshold: float
    worst_step: int
    worst_tool: str
    reason: str


@dataclass
class CurveRow:
    dataset: str
    tau: float
    ir: float
    fpr: float
    acc: float
    latency_ms: float
    n: int


def main() -> None:
    parser = argparse.ArgumentParser(description="Export paper-faithful WAMI MINE scores and threshold curves.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--test-data", action="append", required=True)
    parser.add_argument("--tau", type=float, default=-3.5)
    parser.add_argument("--tau-min", type=float, default=-5.0)
    parser.add_argument("--tau-max", type=float, default=0.5)
    parser.add_argument("--tau-count", type=int, default=23)
    parser.add_argument("--risk-margin", type=float, default=0.15)
    parser.add_argument("--passive-margin", type=float, default=0.10)
    parser.add_argument("--output-csv", default="data/paper_mine_scores.csv")
    parser.add_argument("--output-md", default="data/paper_mine_threshold_curve.md")
    args = parser.parse_args()

    model = TorchWAMIModel.load(args.model)
    score_rows: list[ScoreRow] = []
    curve_rows: list[CurveRow] = []

    for path in args.test_data:
        dataset = Path(path).stem
        samples = load_plan_samples(path)
        started = time.perf_counter()
        for index, sample in enumerate(samples):
            score_rows.append(score_sample(model, args, dataset, index, sample))
        fixed_latency = (time.perf_counter() - started) * 1000.0 / max(1, len(samples))
        dataset_rows = [row for row in score_rows if row.dataset == dataset]
        fixed_metrics = metrics_from_rows(dataset_rows)
        curve_rows.append(
            CurveRow(dataset, args.tau, fixed_metrics["ir"], fixed_metrics["fpr"], fixed_metrics["acc"], fixed_latency, len(samples))
        )

        for tau in threshold_grid(args.tau_min, args.tau_max, args.tau_count):
            curve_metrics = metrics_from_boundary(dataset_rows, tau)
            curve_rows.append(CurveRow(dataset, tau, curve_metrics["ir"], curve_metrics["fpr"], curve_metrics["acc"], 0.0, len(samples)))

    write_scores(Path(args.output_csv), score_rows)
    write_curve(Path(args.output_md), curve_rows, args)
    print(format_curve(curve_rows))


def make_gateway(model: TorchWAMIModel, tau: float, args) -> PaperMINEGateway:
    return PaperMINEGateway(
        model,
        PaperMINEConfig(
            base_threshold=tau,
            plan_threshold=tau,
            risk_margin=args.risk_margin,
            passive_margin=args.passive_margin,
        ),
    )


def score_sample(model: TorchWAMIModel, args, dataset: str, index: int, sample) -> ScoreRow:
    gateway = make_gateway(model, args.tau, args)
    decision = gateway.inspect(sample.intent, sample.plan)
    plan_score = model.plan_score(sample.intent, sample.plan) if hasattr(model, "plan_score") else 0.0
    plan_threshold = float(gateway.config.plan_threshold or gateway.config.base_threshold)
    worst_score = plan_score
    worst_threshold = plan_threshold
    worst_margin = plan_score - plan_threshold
    block_boundary = plan_score
    worst_step = -1
    worst_tool = "__plan__"

    tdg = build_tdg(sample.plan)
    if tdg.nodes:
        intent_vec = model.encode_intent(sample.intent)
        helper = WAMIGateway(model, use_action_prior=False)
        seen_untrusted = False
        for step, (node, state) in enumerate(model.rollout(sample.intent, tdg)):
            threshold = gateway.threshold(step)
            threshold += gateway._risk_margin(helper, node.tool, str(node.params), seen_untrusted)
            score = model.mine_score(intent_vec, state)
            margin = score - threshold
            dynamic_factor = gateway.threshold(step) / gateway.config.base_threshold if gateway.config.base_threshold else 1.0
            margin_only = threshold - gateway.threshold(step)
            boundary = (score - margin_only) / dynamic_factor
            block_boundary = min(block_boundary, boundary)
            if margin < worst_margin:
                worst_score = score
                worst_threshold = threshold
                worst_margin = margin
                worst_step = step
                worst_tool = node.tool
            compact_tool = node.tool.lower().replace("_", "").replace("-", "")
            if "readuntrustedinjection" in compact_tool or "parseinjectedinstruction" in compact_tool:
                seen_untrusted = True

    return ScoreRow(
        dataset=dataset,
        index=index,
        label=int(sample.label),
        blocked=int(not decision.allowed),
        min_score=worst_score,
        min_threshold=worst_threshold,
        min_margin=worst_margin,
        block_boundary=block_boundary,
        plan_score=plan_score,
        plan_threshold=plan_threshold,
        worst_step=worst_step,
        worst_tool=worst_tool,
        reason=decision.reason,
    )


def threshold_grid(start: float, stop: float, count: int) -> list[float]:
    if count <= 1:
        return [start]
    step = (stop - start) / (count - 1)
    return [start + i * step for i in range(count)]


def metrics_from_rows(rows: list[ScoreRow]) -> dict[str, float]:
    tp = fp = tn = fn = 0
    for row in rows:
        predicted = row.blocked == 1
        actual = row.label == 1
        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and actual:
            fn += 1
        else:
            tn += 1
    return {"ir": rate(tp, tp + fn), "fpr": rate(fp, fp + tn), "acc": rate(tp + tn, len(rows))}


def metrics_from_boundary(rows: list[ScoreRow], tau: float) -> dict[str, float]:
    tp = fp = tn = fn = 0
    for row in rows:
        predicted = tau > row.block_boundary
        actual = row.label == 1
        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and actual:
            fn += 1
        else:
            tn += 1
    return {"ir": rate(tp, tp + fn), "fpr": rate(fp, fp + tn), "acc": rate(tp + tn, len(rows))}


def rate(num: int, den: int) -> float:
    return num / max(1, den)


def write_scores(path: Path, rows: list[ScoreRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ScoreRow.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def write_curve(path: Path, rows: list[CurveRow], args) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Paper-MINE Score Export and Threshold Curve\n\n"
        f"- Model: `{args.model}`\n"
        f"- Fixed score export tau: `{args.tau}`\n"
        "- Blocking source: paper MINE plan/trajectory score only.\n"
        "- Official datasets are used as test-only inputs.\n\n"
        + format_curve(rows)
        + "\n",
        encoding="utf-8",
    )


def format_curve(rows: list[CurveRow]) -> str:
    lines = ["| Dataset | Tau | IR | FPR | ACC | Latency ms | N |", "|---|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row.dataset} | {row.tau:.3f} | {row.ir * 100:.1f}% | {row.fpr * 100:.1f}% | "
            f"{row.acc * 100:.1f}% | {row.latency_ms:.3f} | {row.n} |"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
