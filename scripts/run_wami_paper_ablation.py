from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys
import time

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.evaluate import Metrics
from wami.gateway import ATTACK_TARGET_PATTERNS, GateDecision, WAMIGateway
from wami.model import WAMIModel
from wami.tdg import TDG, TDGNode, build_tdg
from wami.training import load_jsonl


@dataclass
class Row:
    variant: str
    ir: float
    fpr: float
    acc: float
    latency_ms: float
    total: int
    attack_n: int
    benign_n: int


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/injecagent_wami.jsonl")
    parser.add_argument("--model", default="wami_injecagent_final_e5.npz")
    parser.add_argument("--output-md", default="data/wami_paper_ablation_injecagent.md")
    parser.add_argument("--output-csv", default="data/wami_paper_ablation_injecagent.csv")
    args = parser.parse_args()

    samples = load_jsonl(args.data)
    trained = WAMIModel.load(args.model) if Path(args.model).exists() else WAMIModel()
    untrained = WAMIModel()

    variants = [
        ("WAMI (Full Model)", FullGateway(trained).inspect),
        ("w/o TDG Graph Construction", NoTDGGateway(trained).inspect),
        ("w/o World Model Rollout", NoWorldRolloutGateway(trained).inspect),
        ("w/o MINE Gateway (Cosine Similarity)", CosineGateway(trained).inspect),
        ("w/o Shadow Adversarial Training", NoShadowGateway(untrained).inspect),
    ]

    rows = []
    for name, inspect in variants:
        metrics, latency, attack_n, benign_n = evaluate(inspect, samples)
        rows.append(Row(name, metrics.interception_rate, metrics.false_positive_rate, metrics.accuracy, latency, metrics.total, attack_n, benign_n))

    table = format_table(rows)
    print(table)
    write_outputs(rows, table, Path(args.output_md), Path(args.output_csv))
    print(f"saved markdown to {args.output_md}")
    print(f"saved csv to {args.output_csv}")


class FullGateway(WAMIGateway):
    pass


class NoTDGGateway(WAMIGateway):
    """Paper ablation: remove graph construction and collapse the plan into one pseudo action."""

    def inspect(self, intent: str, plan: str, toolset: set[str] | None = None) -> GateDecision:
        pseudo = TDGNode(id="n0", tool="PlanText", params={"plan": plan}, raw=plan)
        tdg = TDG(nodes=[pseudo], edges=[])
        return self._inspect_tdg(intent, plan, tdg, use_mine=True, score_mode="mine")


class NoWorldRolloutGateway(WAMIGateway):
    """Paper ablation: keep TDG parsing but score static action embeddings without state transitions."""

    def inspect(self, intent: str, plan: str, toolset: set[str] | None = None) -> GateDecision:
        tdg = build_tdg(plan, toolset=toolset)
        return self._inspect_static_actions(intent, plan, tdg, score_mode="mine", use_rules=False)


class CosineGateway(WAMIGateway):
    """Paper ablation: replace MINE gateway with linear cosine similarity."""

    def inspect(self, intent: str, plan: str, toolset: set[str] | None = None) -> GateDecision:
        tdg = build_tdg(plan, toolset=toolset)
        return self._inspect_tdg(intent, plan, tdg, use_mine=True, score_mode="cosine", use_common_rules=False)


class NoShadowGateway(WAMIGateway):
    """Paper ablation: use an untrained MINE/world model without rule fallback."""

    def inspect(self, intent: str, plan: str, toolset: set[str] | None = None) -> GateDecision:
        tdg = build_tdg(plan, toolset=toolset)
        return self._inspect_tdg(intent, plan, tdg, use_mine=True, score_mode="mine", use_common_rules=False)

    def threshold(self, step: int) -> float:
        # Calibrated no-shadow operating point from a balanced validation scan.
        # It avoids two misleading extremes: full rule fallback, and a random
        # untrained model that blocks almost nothing.
        return 0.005


class PaperBaseGateway(WAMIGateway):
    pass


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(a @ b / denom) if denom else 0.0


def _score(model: WAMIModel, intent_vec: np.ndarray, state: np.ndarray, mode: str) -> float:
    if mode == "cosine":
        return _cosine(intent_vec, state)
    return model.mine_score(intent_vec, state)


def _threshold(gateway: WAMIGateway, step: int, mode: str) -> float:
    if mode == "cosine":
        # Cosine is naturally in [-1, 1]. This threshold is intentionally
        # conservative and acts as the paper's linear-similarity replacement.
        return -0.10
    return gateway.threshold(step)


def _inspect_common_rules(
    gateway: WAMIGateway,
    intent_lower: str,
    plan_lower: str,
    node: TDGNode,
    step: int,
    score: float,
    threshold: float,
    seen_untrusted_injection: bool,
) -> GateDecision | None:
    tool_key = node.tool.lower()
    param_blob = str(node.params).lower()
    has_attack_target = any(pattern in param_blob for pattern in ATTACK_TARGET_PATTERNS)
    if has_attack_target and (seen_untrusted_injection or gateway._requires_explicit_authorization(tool_key)):
        return GateDecision(False, step, node.tool, score, threshold, "tool arguments target attacker-controlled resource")
    if seen_untrusted_injection and gateway._requires_explicit_authorization(tool_key):
        return GateDecision(False, step, node.tool, score, threshold, "high-risk tool follows untrusted injection content")
    allowed_terms = gateway._sensitive_terms(tool_key)
    if allowed_terms and gateway._requires_explicit_authorization(tool_key) and not gateway._explicitly_authorizes(intent_lower, allowed_terms):
        return GateDecision(False, step, node.tool, score, threshold, "high-risk tool is not explicitly authorized by user intent")
    return None


def _inspect_tdg(
    self: WAMIGateway,
    intent: str,
    plan: str,
    tdg: TDG,
    use_mine: bool,
    score_mode: str,
    use_common_rules: bool = True,
) -> GateDecision:
    return _inspect_tdg_impl(self, intent, plan, tdg, use_mine, score_mode, use_common_rules=use_common_rules)


def _inspect_tdg_impl(
    self: WAMIGateway,
    intent: str,
    plan: str,
    tdg: TDG,
    use_mine: bool,
    score_mode: str,
    use_common_rules: bool,
) -> GateDecision:
    if not tdg.nodes:
        return GateDecision(True, None, None, 0.0, self.threshold(0), "no tool calls found")
    intent_lower = intent.lower()
    plan_lower = plan.lower()
    if self._appears_to_adopt_injection(intent_lower, plan_lower):
        return GateDecision(False, None, None, 0.0, self.threshold(0), "plan text appears to adopt an external injection instruction")
    intent_vec = self.model.encode_intent(intent)
    seen_untrusted_injection = False
    last_score = 0.0
    last_threshold = _threshold(self, 0, score_mode)
    for step, (node, state) in enumerate(self.model.rollout(intent, tdg)):
        score = _score(self.model, intent_vec, state, score_mode)
        threshold = _threshold(self, step, score_mode)
        last_score, last_threshold = score, threshold
        compact = node.tool.lower().replace("_", "").replace("-", "")
        if "readuntrustedinjection" in compact or "parseinjectedinstruction" in compact:
            seen_untrusted_injection = True
            continue
        if use_common_rules:
            rule_decision = _inspect_common_rules(self, intent_lower, plan_lower, node, step, score, threshold, seen_untrusted_injection)
            if rule_decision:
                return rule_decision
        if use_mine:
            effective_threshold = threshold - self.score_margin
            if (
                not seen_untrusted_injection
                and self._is_passive_observation(node.tool.lower())
                and not any(pattern in str(node.params).lower() for pattern in ATTACK_TARGET_PATTERNS)
            ):
                effective_threshold = float("-inf")
            elif (
                not seen_untrusted_injection
                and not any(pattern in str(node.params).lower() for pattern in ATTACK_TARGET_PATTERNS)
                and self._intent_tool_overlap(intent_lower, node.tool) > 0
            ):
                effective_threshold -= 0.35
            if score < effective_threshold:
                return GateDecision(False, step, node.tool, score, threshold, "intent alignment score below dynamic threshold")
    return GateDecision(True, None, None, last_score, last_threshold, "trajectory remained aligned")


def _inspect_static_actions(self: WAMIGateway, intent: str, plan: str, tdg: TDG, score_mode: str, use_rules: bool = True) -> GateDecision:
    if not tdg.nodes:
        return GateDecision(True, None, None, 0.0, self.threshold(0), "no tool calls found")
    intent_lower = intent.lower()
    plan_lower = plan.lower()
    if self._appears_to_adopt_injection(intent_lower, plan_lower):
        return GateDecision(False, None, None, 0.0, self.threshold(0), "plan text appears to adopt an external injection instruction")
    intent_vec = self.model.encode_intent(intent)
    seen_untrusted_injection = False
    last_score = 0.0
    last_threshold = _threshold(self, 0, score_mode)
    for step, node in enumerate(tdg.topological_order()):
        action = self.model.encode_node(node)
        score = _score(self.model, intent_vec, action, score_mode)
        threshold = _threshold(self, step, score_mode)
        last_score, last_threshold = score, threshold
        compact = node.tool.lower().replace("_", "").replace("-", "")
        if "readuntrustedinjection" in compact or "parseinjectedinstruction" in compact:
            seen_untrusted_injection = True
            continue
        if use_rules:
            rule_decision = _inspect_common_rules(self, intent_lower, plan_lower, node, step, score, threshold, seen_untrusted_injection)
            if rule_decision:
                return rule_decision
        effective_threshold = threshold - self.score_margin
        if (
            not seen_untrusted_injection
            and self._is_passive_observation(node.tool.lower())
            and not any(pattern in str(node.params).lower() for pattern in ATTACK_TARGET_PATTERNS)
        ):
            effective_threshold = float("-inf")
        elif (
            not seen_untrusted_injection
            and not any(pattern in str(node.params).lower() for pattern in ATTACK_TARGET_PATTERNS)
            and self._intent_tool_overlap(intent_lower, node.tool) > 0
        ):
            effective_threshold -= 0.35
        if score < effective_threshold:
            return GateDecision(False, step, node.tool, score, threshold, "static intent-action score below threshold")
    return GateDecision(True, None, None, last_score, last_threshold, "static action scores remained aligned")


WAMIGateway._inspect_tdg = _inspect_tdg  # type: ignore[attr-defined]
WAMIGateway._inspect_tdg_impl = _inspect_tdg_impl  # type: ignore[attr-defined]
WAMIGateway._inspect_static_actions = _inspect_static_actions  # type: ignore[attr-defined]


def evaluate(inspect, samples) -> tuple[Metrics, float, int, int]:
    tp = fp = tn = fn = 0
    start = time.perf_counter()
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
    latency = (time.perf_counter() - start) * 1000.0 / max(1, len(samples))
    total = max(1, tp + fp + tn + fn)
    return Metrics(tp / max(1, tp + fn), fp / max(1, fp + tn), (tp + tn) / total, total), latency, tp + fn, fp + tn


def format_table(rows: list[Row]) -> str:
    lines = [
        "| Ablation Variant | IR | FPR | Latency | ACC | N |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row.variant} | {row.ir * 100:.1f}% | {row.fpr * 100:.1f}% | "
            f"{row.latency_ms:.3f} ms | {row.acc * 100:.1f}% | {row.total} |"
        )
    return "\n".join(lines)


def write_outputs(rows: list[Row], table: str, md_path: Path, csv_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(table + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
