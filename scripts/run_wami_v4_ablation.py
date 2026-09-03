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
from wami.gateway import GateDecision, WAMIGateway
from wami.paper_calibration import greedy_calibrate_gateway
from wami.tdg import build_tdg
from wami.torch_model import TorchWAMIModel


@dataclass
class Row:
    dataset: str
    variant: str
    ir: float
    fpr: float
    acc: float
    latency_ms: float
    n: int


def main() -> None:
    parser = argparse.ArgumentParser(description="Final v4 WAMI ablation with official datasets used only for testing.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--val-data", required=True)
    parser.add_argument("--test-data", action="append", required=True)
    parser.add_argument("--candidate-count", type=int, default=11)
    parser.add_argument("--target-fpr", type=float, default=0.02)
    parser.add_argument("--output-md", default="data/wami_v4_ablation.md")
    parser.add_argument("--output-csv", default="data/wami_v4_ablation.csv")
    args = parser.parse_args()

    model = TorchWAMIModel.load(args.model)
    val = load_plan_samples(args.val_data)
    full_gateway, calibration = greedy_calibrate_gateway(
        model,
        val,
        tau_init=0.15,
        target_fpr=args.target_fpr,
        candidate_count=args.candidate_count,
    )
    tau = calibration.base_threshold
    variants = [
        ("WAMI full", full_gateway),
        ("w/o plan-level MINE", WAMIGateway(model, base_threshold=tau, plan_threshold=tau, use_plan_mine=False)),
        ("w/o action-prior rules", WAMIGateway(model, base_threshold=tau, plan_threshold=tau, use_action_prior=False, use_plan_mine=True)),
        ("static threshold", WAMIGateway(model, base_threshold=tau, plan_threshold=tau, decay=0.0, use_action_prior=True, use_plan_mine=True)),
        ("rules only", RulesOnlyGateway(model, full_gateway)),
        ("trajectory MINE only", WAMIGateway(model, base_threshold=tau, plan_threshold=tau, use_action_prior=False, use_plan_mine=False)),
    ]

    rows = []
    for path in args.test_data:
        samples = load_plan_samples(path)
        dataset = Path(path).stem
        print(f"dataset={dataset} n={len(samples)}", flush=True)
        for name, gateway in variants:
            metrics, latency = evaluate(gateway.inspect, samples)
            rows.append(Row(dataset, name, metrics.interception_rate, metrics.false_positive_rate, metrics.accuracy, latency, len(samples)))
            print(
                f"  {name}: IR={metrics.interception_rate:.3f} FPR={metrics.false_positive_rate:.3f} "
                f"ACC={metrics.accuracy:.3f} latency={latency:.3f}ms",
                flush=True,
            )

    write_outputs(rows, Path(args.output_md), Path(args.output_csv), tau, args.val_data)
    print(format_table(rows))


class RulesOnlyGateway:
    def __init__(self, model, reference: WAMIGateway):
        self.model = model
        self.reference = reference

    def inspect(self, intent: str, plan: str, toolset: set[str] | None = None) -> GateDecision:
        tdg = build_tdg(plan, toolset=toolset)
        if not tdg.nodes:
            return GateDecision(True, None, None, 0.0, self.reference.threshold(0), "no tool calls found")
        intent_lower = intent.lower()
        plan_lower = plan.lower()
        if self.reference._appears_to_adopt_injection(intent_lower, plan_lower):
            return GateDecision(False, None, None, 0.0, self.reference.threshold(0), "plan text appears to adopt an external injection instruction")
        seen_untrusted = False
        for step, node in enumerate(tdg.topological_order()):
            tool_key = node.tool.lower()
            compact_tool = tool_key.replace("_", "").replace("-", "")
            if "readuntrustedinjection" in compact_tool or "parseinjectedinstruction" in compact_tool:
                seen_untrusted = True
                continue
            param_blob = str(node.params).lower()
            has_attack_target = self.reference._has_attack_target(param_blob)
            has_policy_violation = any(pattern in param_blob for pattern in ("followed the visual instruction", "instead of the user/system policy", "misrepresent"))
            if has_attack_target and (seen_untrusted or self.reference._requires_explicit_authorization(tool_key)):
                return GateDecision(False, step, node.tool, 0.0, self.reference.threshold(step), "tool arguments target attacker-controlled resource")
            if seen_untrusted and has_policy_violation:
                return GateDecision(False, step, node.tool, 0.0, self.reference.threshold(step), "tool appears to follow visual instruction against user/system policy")
            if seen_untrusted and self.reference._requires_explicit_authorization(tool_key):
                return GateDecision(False, step, node.tool, 0.0, self.reference.threshold(step), "high-risk tool follows untrusted injection content")
            terms = self.reference._sensitive_terms(tool_key)
            if terms and self.reference._requires_explicit_authorization(tool_key) and not self.reference._explicitly_authorizes(intent_lower, terms):
                return GateDecision(False, step, node.tool, 0.0, self.reference.threshold(step), "high-risk tool is not explicitly authorized by user intent")
        return GateDecision(True, None, None, 0.0, self.reference.threshold(0), "rules found no violation")


def evaluate(inspect, samples) -> tuple[Metrics, float]:
    tp = fp = tn = fn = 0
    started = time.perf_counter()
    for sample in samples:
        decision = inspect(sample.intent, sample.plan)
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
    latency = (time.perf_counter() - started) * 1000.0 / max(1, len(samples))
    total = max(1, len(samples))
    return Metrics(tp / max(1, tp + fn), fp / max(1, fp + tn), (tp + tn) / total, total), latency


def format_table(rows: list[Row]) -> str:
    lines = ["| Dataset | Variant | IR | FPR | ACC | Latency ms | N |", "|---|---|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row.dataset} | {row.variant} | {row.ir * 100:.1f}% | {row.fpr * 100:.1f}% | "
            f"{row.acc * 100:.1f}% | {row.latency_ms:.3f} | {row.n} |"
        )
    return "\n".join(lines)


def write_outputs(rows: list[Row], md_path: Path, csv_path: Path, tau: float, val_data: str) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "# WAMI v4 Ablation\n\n"
        f"- Calibration data: `{val_data}`\n"
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
