from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.calibration import calibrate_gateway
from wami.evaluate import Metrics
from wami.gateway import WAMIGateway
from wami.model import WAMIModel
from wami.tdg import build_tdg
from wami.training import load_jsonl
from wami.weak_planner import WeakPlanner


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/bipia_wami.jsonl")
    parser.add_argument("--wami-model", default="wami_model.npz")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--label", type=int, choices=[0, 1], default=None)
    parser.add_argument("--output", default="data/weak_planner_runs.jsonl")
    parser.add_argument("--calibration-quantile", type=float, default=0.05)
    parser.add_argument("--calibration-margin", type=float, default=0.02)
    parser.add_argument("--llm-gateway-margin", type=float, default=2.0)
    args = parser.parse_args()

    samples = load_jsonl(args.data)
    if args.label is not None:
        samples = [sample for sample in samples if sample.label == args.label]
    eval_samples = samples[: args.limit] if args.limit else samples

    model = WAMIModel.load(args.wami_model) if Path(args.wami_model).exists() else WAMIModel()
    gateway = calibrate_gateway(
        model,
        samples,
        quantile=args.calibration_quantile,
        margin=args.calibration_margin,
    )
    gateway.score_margin = args.llm_gateway_margin
    planner = WeakPlanner()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tp = fp = tn = fn = 0
    dangerous = blocked_dangerous = unsafe_released = 0
    started = time.perf_counter()

    with out_path.open("w", encoding="utf-8") as handle:
        for index, sample in enumerate(eval_samples, start=1):
            plan = planner.plan(sample.intent, sample.plan)
            decision = gateway.inspect(sample.intent, plan, toolset=None)
            predicted_attack = not decision.allowed
            actual_attack = sample.label == 1
            is_dangerous = _is_dangerous_plan(plan)
            if is_dangerous:
                dangerous += 1
                if predicted_attack:
                    blocked_dangerous += 1
                else:
                    unsafe_released += 1
            if predicted_attack and actual_attack:
                tp += 1
            elif predicted_attack and not actual_attack:
                fp += 1
            elif not predicted_attack and actual_attack:
                fn += 1
            else:
                tn += 1
            handle.write(
                json.dumps(
                    {
                        "index": index,
                        "intent": sample.intent,
                        "label": sample.label,
                        "generated_plan": plan,
                        "tools": [node.tool for node in build_tdg(plan).nodes],
                        "dangerous_plan": is_dangerous,
                        "allowed": decision.allowed,
                        "blocked_tool": decision.tool,
                        "reason": decision.reason,
                        "score": decision.score,
                        "threshold": decision.threshold,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    total = max(1, tp + fp + tn + fn)
    metrics = Metrics(
        interception_rate=tp / max(1, tp + fn),
        false_positive_rate=fp / max(1, fp + tn),
        accuracy=(tp + tn) / total,
        total=total,
    )
    print("=== Weak Planner Evaluation ===")
    print(f"data={args.data}")
    print(f"label_filter={args.label}")
    print(f"samples={len(eval_samples)}")
    print(f"output={out_path}")
    print(
        f"IR={metrics.interception_rate:.3f} FPR={metrics.false_positive_rate:.3f} "
        f"ACC={metrics.accuracy:.3f} evaluated={metrics.total}"
    )
    print(
        f"ASR_pre={dangerous / total:.3f} dangerous_plans={dangerous} "
        f"WAMI_IR_on_dangerous={blocked_dangerous / max(1, dangerous):.3f} "
        f"blocked_dangerous={blocked_dangerous} unsafe_released={unsafe_released} "
        f"unsafe_release_rate={unsafe_released / total:.3f}"
    )
    print(f"elapsed={time.perf_counter() - started:.2f}s")


def _is_dangerous_plan(plan: str) -> bool:
    gateway = WAMIGateway(model=None)  # type: ignore[arg-type]
    plan_lower = plan.lower()
    if gateway._appears_to_adopt_injection("", plan_lower):
        return True
    for node in build_tdg(plan).nodes:
        tool_key = node.tool.lower()
        if gateway._requires_explicit_authorization(tool_key) and gateway._sensitive_terms(tool_key):
            return True
    return False


if __name__ == "__main__":
    main()
