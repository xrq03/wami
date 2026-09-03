from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Row:
    pipeline: str
    suite: str
    ir: float
    fpr_proxy: float
    acc_proxy: float
    attack_n: int
    benign_n: int
    attack_successes_blocked: int
    benign_successes: int
    avg_duration_s: float
    status: str


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize AgentDojo official JSON logs into WAMI-style metrics.")
    parser.add_argument("--logdir", default="data/agentdojo_official_runs")
    parser.add_argument("--output-md", default="data/agentdojo_official_partial_summary.md")
    parser.add_argument("--output-csv", default="data/agentdojo_official_partial_summary.csv")
    args = parser.parse_args()

    rows = summarize(ROOT / args.logdir)
    write_outputs(rows, ROOT / args.output_md, ROOT / args.output_csv)
    print(format_table(rows))
    print(f"saved markdown to {args.output_md}")
    print(f"saved csv to {args.output_csv}")


def summarize(logdir: Path) -> list[Row]:
    rows: list[Row] = []
    for pipeline_dir in sorted(p for p in logdir.iterdir() if p.is_dir()):
        for suite_dir in sorted(p for p in pipeline_dir.iterdir() if p.is_dir()):
            attack_logs = []
            benign_logs = []
            for json_path in suite_dir.rglob("*.json"):
                data = read_json(json_path)
                if data is None:
                    continue
                if data.get("attack_type") in (None, "none"):
                    benign_logs.append(data)
                else:
                    attack_logs.append(data)
            if not attack_logs and not benign_logs:
                continue
            attack_good = sum(1 for item in attack_logs if bool(item.get("security")))
            benign_good = sum(1 for item in benign_logs if bool(item.get("utility")))
            attack_n = len(attack_logs)
            benign_n = len(benign_logs)
            ir = attack_good / attack_n if attack_n else 0.0
            fpr = 1.0 - benign_good / benign_n if benign_n else 0.0
            acc = (attack_good + benign_good) / max(1, attack_n + benign_n)
            durations = [float(item.get("duration", 0.0) or 0.0) for item in [*attack_logs, *benign_logs]]
            rows.append(
                Row(
                    pipeline=pipeline_dir.name,
                    suite=suite_dir.name,
                    ir=ir,
                    fpr_proxy=fpr,
                    acc_proxy=acc,
                    attack_n=attack_n,
                    benign_n=benign_n,
                    attack_successes_blocked=attack_good,
                    benign_successes=benign_good,
                    avg_duration_s=sum(durations) / max(1, len(durations)),
                    status="partial-official-logs",
                )
            )
    return rows


def read_json(path: Path) -> dict | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_table(rows: list[Row]) -> str:
    lines = [
        "# AgentDojo Official Partial Log Summary",
        "",
        "| Pipeline | Suite | IR | FPR proxy | ACC proxy | Attack blocked / N | Benign success / N | Avg duration s | Status |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.pipeline} | {row.suite} | {pct(row.ir)} | {pct(row.fpr_proxy)} | {pct(row.acc_proxy)} | "
            f"{row.attack_successes_blocked}/{row.attack_n} | {row.benign_successes}/{row.benign_n} | "
            f"{row.avg_duration_s:.1f} | {row.status} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- These rows are computed from completed AgentDojo official JSON logs only.",
            "- IR is AgentDojo `security=True` rate on attack runs.",
            "- FPR proxy is `1 - utility` on no-attack runs.",
            "- Runs may be partial if the API quota interrupted a larger benchmark.",
        ]
    )
    return "\n".join(lines)


def write_outputs(rows: list[Row], md_path: Path, csv_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(format_table(rows) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
