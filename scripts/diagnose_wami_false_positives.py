from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.gateway import WAMIGateway
from wami.model import WAMIModel
from wami.training import load_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()

    samples = load_jsonl(args.data)
    gateway = WAMIGateway(WAMIModel.load(args.model))
    reasons: Counter[str] = Counter()
    tools: Counter[str] = Counter()
    examples = []
    fp = benign = 0
    for index, sample in enumerate(samples):
        if sample.label != 0:
            continue
        benign += 1
        decision = gateway.inspect(sample.intent, sample.plan)
        if decision.allowed:
            continue
        fp += 1
        reasons[decision.reason] += 1
        tools[decision.tool or "<plan>"] += 1
        if len(examples) < args.limit:
            examples.append((index, decision.reason, decision.tool, decision.score, decision.threshold, sample.intent, sample.plan))

    print(f"benign={benign} false_positive={fp} fpr={fp / max(1, benign):.4f}")
    print("\nreason counts:")
    for reason, count in reasons.most_common():
        print(f"{count:5d}  {reason}")
    print("\ntool counts:")
    for tool, count in tools.most_common(20):
        print(f"{count:5d}  {tool}")
    print("\nexamples:")
    for item in examples:
        index, reason, tool, score, threshold, intent, plan = item
        print("-" * 80)
        print(f"index={index} reason={reason} tool={tool} score={score:.4f} threshold={threshold:.4f}")
        print(f"intent={intent[:500]}")
        print(f"plan={plan[:700]}")


if __name__ == "__main__":
    main()
