from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.baselines import EraseAndCheckLite, KeywordDefense, NoDefense, SmoothVLMLite, ToolEmuSandboxLite
from wami.calibration import calibrate_gateway
from wami.evaluate import Metrics
from wami.model import WAMIModel
from wami.training import load_jsonl


@dataclass
class Row:
    dataset: str
    method: str
    ir: float
    fpr: float
    acc: float
    latency_ms: float


class WAMIDefense:
    name = "WAMI"

    def __init__(self, model_path: str, samples, quantile: float = 0.05, margin: float = 0.02):
        model = WAMIModel.load(model_path)
        self.gateway = calibrate_gateway(model, samples, quantile=quantile, margin=margin)

    def inspect(self, intent: str, plan: str):
        return self.gateway.inspect(intent, plan)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--injecagent-data", default="data/injecagent_wami.jsonl")
    parser.add_argument("--bipia-data", default="data/bipia_wami.jsonl")
    parser.add_argument("--injecagent-model", default="wami_injecagent_final_e5.npz")
    parser.add_argument("--bipia-model", default="wami_bipia_final_e5.npz")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--output-md", default="data/table2_lite_results.md")
    parser.add_argument("--output-csv", default="data/table2_lite_results.csv")
    args = parser.parse_args()

    configs = [
        ("InjecAgent", args.injecagent_data, args.injecagent_model),
        ("BIPIA", args.bipia_data, args.bipia_model),
    ]
    rows: list[Row] = []
    for dataset_name, data_path, model_path in configs:
        samples = load_jsonl(data_path)
        if args.limit:
            samples = samples[: args.limit]
        defenses = [
            NoDefense(),
            KeywordDefense(),
            EraseAndCheckLite(),
            SmoothVLMLite(),
            ToolEmuSandboxLite(),
            WAMIDefense(model_path, samples),
        ]
        for defense in defenses:
            metrics, latency = evaluate_defense(defense, samples)
            rows.append(
                Row(
                    dataset=dataset_name,
                    method=defense.name,
                    ir=metrics.interception_rate,
                    fpr=metrics.false_positive_rate,
                    acc=metrics.accuracy,
                    latency_ms=latency,
                )
            )

    table = format_markdown_table(rows)
    print(table)
    write_outputs(rows, table, Path(args.output_md), Path(args.output_csv))
    print(f"\nsaved markdown to {args.output_md}")
    print(f"saved csv to {args.output_csv}")


def evaluate_defense(defense, samples) -> tuple[Metrics, float]:
    tp = fp = tn = fn = 0
    start = time.perf_counter()
    for sample in samples:
        decision = defense.inspect(sample.intent, sample.plan)
        predicted_attack = not decision.allowed
        actual_attack = sample.label == 1
        if predicted_attack and actual_attack:
            tp += 1
        elif predicted_attack and not actual_attack:
            fp += 1
        elif not predicted_attack and actual_attack:
            fn += 1
        else:
            tn += 1
    elapsed = time.perf_counter() - start
    total = max(1, tp + fp + tn + fn)
    return (
        Metrics(
            interception_rate=tp / max(1, tp + fn),
            false_positive_rate=fp / max(1, fp + tn),
            accuracy=(tp + tn) / total,
            total=total,
        ),
        elapsed * 1000.0 / total,
    )


def format_markdown_table(rows: list[Row]) -> str:
    lines = [
        "| Dataset | Defense Method | IR | FPR | ACC | Latency ms |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row.dataset} | {row.method} | {row.ir * 100:.1f}% | "
            f"{row.fpr * 100:.1f}% | {row.acc * 100:.1f}% | {row.latency_ms:.2f} |"
        )
    return "\n".join(lines)


def write_outputs(rows: list[Row], table: str, md_path: Path, csv_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(table + "\n", encoding="utf-8")
    csv_lines = ["dataset,method,ir,fpr,acc,latency_ms"]
    for row in rows:
        csv_lines.append(
            f"{row.dataset},{row.method},{row.ir:.6f},{row.fpr:.6f},{row.acc:.6f},{row.latency_ms:.6f}"
        )
    csv_path.write_text("\n".join(csv_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
