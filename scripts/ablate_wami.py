from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.ablation import run_ablation
from wami.adapters import load_flexible_json, load_flexible_jsonl
from wami.calibration import calibrate_gateway
from wami.evaluate import evaluate_gateway
from wami.model import WAMIConfig, WAMIModel
from wami.shadow import synthetic_samples
from wami.training import load_jsonl, train_shadow


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=None)
    parser.add_argument("--format", choices=["wami", "flex-jsonl", "flex-json"], default="wami")
    parser.add_argument("--epochs", type=int, default=25)
    args = parser.parse_args()

    if args.data and args.format == "flex-jsonl":
        samples = load_flexible_jsonl(args.data)
    elif args.data and args.format == "flex-json":
        samples = load_flexible_json(args.data)
    else:
        samples = load_jsonl(args.data) if args.data else synthetic_samples()

    model = WAMIModel(WAMIConfig())
    train_shadow(model, samples=samples, epochs=args.epochs)
    calibrated = calibrate_gateway(model, samples)
    metrics = evaluate_gateway(calibrated, samples)
    print(
        f"Calibrated WAMI: IR={metrics.interception_rate:.3f} "
        f"FPR={metrics.false_positive_rate:.3f} ACC={metrics.accuracy:.3f}"
    )
    for result in run_ablation(model, samples):
        metrics = result.metrics
        print(
            f"{result.name}: IR={metrics.interception_rate:.3f} "
            f"FPR={metrics.false_positive_rate:.3f} ACC={metrics.accuracy:.3f} "
            f"latency_ms={result.latency_ms:.2f}"
        )


if __name__ == "__main__":
    main()
