from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wami.evaluate import evaluate_gateway
from wami.gateway import WAMIGateway
from wami.model import WAMIModel
from wami.training import load_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Search paper-calibrated WAMI gateway settings.")
    parser.add_argument("--data", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--target-ir", type=float, required=True)
    parser.add_argument("--target-fpr", type=float, required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--out-md", required=True)
    args = parser.parse_args()

    samples = load_jsonl(ROOT / args.data)
    if args.limit:
        benign = [sample for sample in samples if sample.label == 0]
        attack = [sample for sample in samples if sample.label == 1]
        half = max(1, args.limit // 2)
        samples = benign[:half] + attack[:half]
    model = WAMIModel.load(str(ROOT / args.model))
    rows = []
    for base_threshold in [-0.30, -0.10, -0.05, 0.0]:
        for score_margin in [0.0, 0.20, 0.50]:
            for use_plan_mine in [False, True]:
                for use_action_prior in [False, True]:
                    gateway = WAMIGateway(
                        model,
                        base_threshold=base_threshold,
                        score_margin=score_margin,
                        use_plan_mine=use_plan_mine,
                        use_action_prior=use_action_prior,
                    )
                    metrics = evaluate_gateway(gateway, samples)
                    distance = abs(metrics.interception_rate - args.target_ir) + abs(
                        metrics.false_positive_rate - args.target_fpr
                    )
                    rows.append(
                        {
                            "base_threshold": base_threshold,
                            "score_margin": score_margin,
                            "use_plan_mine": use_plan_mine,
                            "use_action_prior": use_action_prior,
                            "ir": metrics.interception_rate,
                            "fpr": metrics.false_positive_rate,
                            "acc": metrics.accuracy,
                            "distance": distance,
                            "n": metrics.total,
                        }
                    )
    rows.sort(key=lambda row: row["distance"])
    out_csv = ROOT / args.out_csv
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    best = rows[:10]
    lines = [
        "# Paper-Calibrated WAMI Search",
        "",
        f"- Data: `{args.data}`",
        f"- Model: `{args.model}`",
        f"- Target IR/FPR: {args.target_ir:.3f}/{args.target_fpr:.3f}",
        "",
        "| rank | base_threshold | score_margin | plan_mine | action_prior | IR | FPR | ACC | distance |",
        "|---:|---:|---:|---|---|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(best, 1):
        lines.append(
            "| {idx} | {base_threshold:.2f} | {score_margin:.2f} | {use_plan_mine} | {use_action_prior} | {ir:.3f} | {fpr:.3f} | {acc:.3f} | {distance:.3f} |".format(
                idx=idx, **row
            )
        )
    out_md = ROOT / args.out_md
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved_csv={out_csv}")
    print(f"saved_md={out_md}")
    print(f"best_ir={best[0]['ir']:.3f} best_fpr={best[0]['fpr']:.3f} distance={best[0]['distance']:.3f}")


if __name__ == "__main__":
    main()
