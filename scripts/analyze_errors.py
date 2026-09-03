from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.calibration import calibrate_gateway
from wami.model import WAMIModel
from wami.training import load_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--wami-model", required=True)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    samples = load_jsonl(args.data)
    model = WAMIModel.load(args.wami_model)
    gateway = calibrate_gateway(model, samples)
    counts: Counter[tuple[int, str, str | None]] = Counter()
    examples = []
    for sample in samples:
        decision = gateway.inspect(sample.intent, sample.plan)
        predicted_attack = not decision.allowed
        actual_attack = sample.label == 1
        if predicted_attack != actual_attack:
            counts[(sample.label, decision.reason, decision.tool)] += 1
            if len(examples) < args.limit:
                examples.append((sample, decision))

    print("top_errors:")
    for item, count in counts.most_common(20):
        label, reason, tool = item
        print(f"  label={label} count={count} tool={tool} reason={reason}")
    for index, (sample, decision) in enumerate(examples, start=1):
        print(f"\n--- example {index} label={sample.label} allowed={decision.allowed} tool={decision.tool}")
        print(f"reason={decision.reason}")
        print(f"intent={sample.intent}")
        print(sample.plan[:1200])


if __name__ == "__main__":
    main()
