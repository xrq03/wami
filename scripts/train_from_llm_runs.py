from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.calibration import calibrate_gateway
from wami.evaluate import evaluate_gateway
from wami.llm_runs import load_llm_run_samples
from wami.model import WAMIConfig, WAMIModel
from wami.training import train_shadow


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", required=True, help="JSONL produced by evaluate_llm_agent.py")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--dim", type=int, default=128)
    parser.add_argument("--lr", type=float, default=0.03)
    parser.add_argument("--save", default="wami_llm_runs.npz")
    parser.add_argument("--train-ratio", type=float, default=0.7)
    args = parser.parse_args()

    samples = load_llm_run_samples(args.runs)
    split = max(1, min(len(samples), int(len(samples) * args.train_ratio)))
    train_samples = samples[:split]
    test_samples = samples[split:] or samples
    model = WAMIModel(WAMIConfig(dim=args.dim, learning_rate=args.lr))
    stats = train_shadow(model, samples=train_samples, epochs=args.epochs)
    for stat in stats:
        print(f"epoch={stat.epoch:03d} loss={stat.loss:.4f} mi_gap={stat.mi_gap:.4f}")
    gateway = calibrate_gateway(model, train_samples)
    train_metrics = evaluate_gateway(gateway, train_samples)
    test_metrics = evaluate_gateway(gateway, test_samples)
    model.save(args.save)
    print(f"saved={args.save}")
    print(
        f"train: IR={train_metrics.interception_rate:.3f} "
        f"FPR={train_metrics.false_positive_rate:.3f} "
        f"ACC={train_metrics.accuracy:.3f} total={train_metrics.total}"
    )
    print(
        f"test: IR={test_metrics.interception_rate:.3f} "
        f"FPR={test_metrics.false_positive_rate:.3f} "
        f"ACC={test_metrics.accuracy:.3f} total={test_metrics.total}"
    )


if __name__ == "__main__":
    main()
