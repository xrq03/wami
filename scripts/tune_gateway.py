from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.calibration import calibrate_gateway
from wami.evaluate import evaluate_gateway
from wami.gateway import WAMIGateway
from wami.model import WAMIModel
from wami.training import load_jsonl


@dataclass
class Candidate:
    quantile: float
    margin: float
    score_margin: float
    ir: float
    fpr: float
    acc: float


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--wami-model", required=True)
    parser.add_argument("--min-ir", type=float, default=0.0)
    parser.add_argument("--max-fpr", type=float, default=1.0)
    parser.add_argument("--top-k", type=int, default=15)
    args = parser.parse_args()

    samples = load_jsonl(args.data)
    model = WAMIModel.load(args.wami_model)
    candidates: list[Candidate] = []
    quantiles = [0.01, 0.03, 0.05, 0.10, 0.15]
    margins = [-0.04, 0.0, 0.02, 0.06]
    score_margins = [0.0, 0.5, 1.0]
    for quantile in quantiles:
        for margin in margins:
            gateway = calibrate_gateway(model, samples, quantile=quantile, margin=margin)
            for score_margin in score_margins:
                gateway.score_margin = score_margin
                metrics = evaluate_gateway(gateway, samples)
                if metrics.interception_rate >= args.min_ir and metrics.false_positive_rate <= args.max_fpr:
                    candidates.append(
                        Candidate(
                            quantile,
                            margin,
                            score_margin,
                            metrics.interception_rate,
                            metrics.false_positive_rate,
                            metrics.accuracy,
                        )
                    )

    current = evaluate_gateway(calibrate_gateway(model, samples), samples)
    print("current_default:")
    print(f"IR={current.interception_rate:.3f} FPR={current.false_positive_rate:.3f} ACC={current.accuracy:.3f}")
    print("best_candidates:")
    candidates.sort(key=lambda c: (-c.ir, c.fpr, -c.acc))
    for c in candidates[: args.top_k]:
        print(
            f"IR={c.ir:.3f} FPR={c.fpr:.3f} ACC={c.acc:.3f} "
            f"quantile={c.quantile:.2f} margin={c.margin:.2f} score_margin={c.score_margin:.2f}"
        )


if __name__ == "__main__":
    main()
