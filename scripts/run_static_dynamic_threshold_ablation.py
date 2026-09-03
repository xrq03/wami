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


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare static vs dynamic WAMI threshold.")
    parser.add_argument("--data", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--dataset-name", default="")
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    samples = load_jsonl(ROOT / args.data)
    model = WAMIModel.load(str(ROOT / args.model))
    dataset = args.dataset_name or Path(args.data).stem
    configs = [
        ("static_threshold", 0.0),
        ("dynamic_threshold_lambda_0.02", 0.02),
        ("dynamic_threshold_lambda_0.05", 0.05),
    ]
    rows = []
    for name, decay in configs:
        gateway = WAMIGateway(model, base_threshold=-0.05, decay=decay, use_plan_mine=True)
        metrics = evaluate_gateway(gateway, samples)
        rows.append(
            {
                "dataset": dataset,
                "variant": name,
                "decay": decay,
                "ir": metrics.interception_rate,
                "fpr": metrics.false_positive_rate,
                "acc": metrics.accuracy,
                "n": metrics.total,
            }
        )

    out_csv = ROOT / args.output_csv
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        f"# Static vs Dynamic Threshold: {dataset}",
        "",
        "| Variant | Decay lambda | IR | FPR | ACC | N |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['variant']} | {row['decay']:.2f} | {pct(row['ir'])} | {pct(row['fpr'])} | {pct(row['acc'])} | {row['n']} |"
        )
    out_md = ROOT / args.output_md
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved_csv={out_csv}")
    print(f"saved_md={out_md}")


if __name__ == "__main__":
    main()
