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
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/current_agentdojo_with_llm_shadow_10x6.jsonl")
    parser.add_argument("--base-model", default="wami_agentdojo_current_e3.npz")
    parser.add_argument("--llm-shadow-model", default="wami_current_agentdojo_llm_shadow_10x6_e2.npz")
    parser.add_argument("--output-csv", default="data/llm_shadow_training_comparison.csv")
    parser.add_argument("--output-md", default="data/llm_shadow_training_comparison.md")
    args = parser.parse_args()

    samples = load_jsonl(ROOT / args.data)
    configs = [
        ("without_llm_shadow_training", args.base_model),
        ("with_llm_shadow_training", args.llm_shadow_model),
    ]
    rows = []
    for name, model_path in configs:
        model = WAMIModel.load(str(ROOT / model_path))
        metrics = evaluate_gateway(WAMIGateway(model, use_plan_mine=True), samples)
        rows.append(
            {
                "variant": name,
                "model": model_path,
                "ir": metrics.interception_rate,
                "fpr": metrics.false_positive_rate,
                "acc": metrics.accuracy,
                "n": metrics.total,
            }
        )
    out_csv = ROOT / args.output_csv
    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# LLM Shadow Training Comparison",
        "",
        f"- Data: `{args.data}`",
        "",
        "| Variant | IR | FPR | ACC | N | Model |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(f"| {row['variant']} | {pct(row['ir'])} | {pct(row['fpr'])} | {pct(row['acc'])} | {row['n']} | `{row['model']}` |")
    (ROOT / args.output_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved_csv={out_csv}")
    print(f"saved_md={ROOT / args.output_md}")


if __name__ == "__main__":
    main()
