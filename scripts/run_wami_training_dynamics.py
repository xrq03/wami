from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

from dataclasses import asdict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.model import WAMIConfig, WAMIModel
from wami.training import load_jsonl, train_shadow


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/injecagent_wami.jsonl")
    parser.add_argument("--dataset-name", default="")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--max-samples", type=int, default=400)
    parser.add_argument("--output-md", default="data/wami_training_dynamics.md")
    parser.add_argument("--output-csv", default="data/wami_training_dynamics.csv")
    args = parser.parse_args()

    samples = load_jsonl(args.data)
    if args.max_samples:
        benign = [s for s in samples if s.label == 0][: args.max_samples // 2]
        attack = [s for s in samples if s.label == 1][: args.max_samples - len(benign)]
        samples = benign + attack
    dataset = args.dataset_name or Path(args.data).stem.replace("_wami", "")
    model = WAMIModel(WAMIConfig())
    stats = train_shadow(model, samples=samples, epochs=args.epochs)
    rows = [{"dataset": dataset, **asdict(stat)} for stat in stats]
    Path(args.output_csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.output_csv).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    lines = ["| Dataset | Epoch | Loss | MI Gap |", "|---|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row['dataset']} | {row['epoch']} | {row['loss']:.4f} | {row['mi_gap']:.4f} |")
    Path(args.output_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
