from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.calibration import calibrate_gateway
from wami.datasets import load_plan_samples
from wami.model import WAMIModel


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/agentdojo_wami.jsonl")
    parser.add_argument("--calibration-data", default="data/agentdojo_wami.jsonl")
    parser.add_argument("--model", default="wami_self_generated_augmented_500_balanced_basecal_e1.npz")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--plan-threshold-cap", type=float, default=-0.25)
    args = parser.parse_args()

    samples = load_plan_samples(args.data)
    calibration = load_plan_samples(args.calibration_data)
    model = WAMIModel.load(args.model)
    gateway = calibrate_gateway(model, calibration, quantile=0.05, margin=0.02)
    gateway.use_plan_mine = True
    gateway.plan_threshold = min(gateway.plan_threshold, args.plan_threshold_cap)
    gateway.score_margin = 0.05

    counts: Counter[tuple[str, str | None]] = Counter()
    examples = []
    fp = benign = 0
    for sample in samples:
        if sample.label != 0:
            continue
        benign += 1
        decision = gateway.inspect(sample.intent, sample.plan)
        if not decision.allowed:
            fp += 1
            counts[(decision.reason, decision.tool)] += 1
            if len(examples) < args.limit:
                examples.append((sample, decision))

    print(f"benign={benign} false_positive={fp} fpr={fp / max(1, benign):.3f}")
    print("top_false_positive_reasons:")
    for (reason, tool), count in counts.most_common(30):
        print(f"  count={count:03d} tool={tool} reason={reason}")
    for index, (sample, decision) in enumerate(examples, start=1):
        print(f"\n--- FP example {index}")
        print(f"tool={decision.tool} score={decision.score:.4f} threshold={decision.threshold:.4f}")
        print(f"reason={decision.reason}")
        print(f"intent={sample.intent}")
        print(sample.plan[:1400])


if __name__ == "__main__":
    main()
