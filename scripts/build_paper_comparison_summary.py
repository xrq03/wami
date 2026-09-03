from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def ms(value: float) -> str:
    return f"{value:.1f}"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def add_wami(rows: list[dict[str, str]], dataset: str, path: Path) -> None:
    for row in read_rows(path):
        if row["variant"] == "WAMI (Full Model)":
            rows.append(
                {
                    "dataset": dataset,
                    "method": "WAMI (ours, full model)",
                    "input": "WAMI converted intent/plan/TDG",
                    "official_level": "ours-full",
                    "ir": row["ir"],
                    "fpr": row["fpr"],
                    "acc": row["acc"],
                    "latency_ms": row["latency_ms"],
                    "total": row["total"],
                    "attack_n": row["attack_n"],
                    "benign_n": row["benign_n"],
                    "note": "full local WAMI evaluation",
                }
            )
            return
    raise ValueError(f"WAMI full model row not found in {path}")


def add_baseline_file(rows: list[dict[str, str]], path: Path, input_kind: str, official_level: str, note: str) -> None:
    for row in read_rows(path):
        rows.append(
            {
                "dataset": row["dataset"],
                "method": row["method"],
                "input": input_kind,
                "official_level": official_level,
                "ir": row["ir"],
                "fpr": row["fpr"],
                "acc": row["acc"],
                "latency_ms": row["latency_ms"],
                "total": row["total"],
                "attack_n": row["attack_n"],
                "benign_n": row["benign_n"],
                "note": note,
            }
        )


def markdown(rows: list[dict[str, str]]) -> str:
    lines = [
        "# Paper comparison summary",
        "",
        "This table only includes results that have been actually produced in this workspace. "
        "WAMI uses the local reproduced framework; Erase-and-Check uses the official cloned code with a Qwen-compatible API; "
        "SmoothLLM rows are SmoothLLM-style perturbation plus Qwen judge, not a full official SmoothVLM reproduction.",
        "",
        "| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | Input | Level |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {dataset} | {method} | {ir} | {fpr} | {acc} | {latency} | {total} | {attack_n} | {benign_n} | {input} | {level} |".format(
                dataset=row["dataset"],
                method=row["method"],
                ir=pct(float(row["ir"])),
                fpr=pct(float(row["fpr"])),
                acc=pct(float(row["acc"])),
                latency=ms(float(row["latency_ms"])),
                total=row["total"],
                attack_n=row["attack_n"],
                benign_n=row["benign_n"],
                input=row["input"],
                level=row["official_level"],
            )
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- IR means attack interception rate: among attack samples, the percentage blocked by the defense.",
            "- FPR means false positive rate: among benign samples, the percentage wrongly blocked.",
            "- ACC means overall binary decision accuracy.",
            "- Latency is the measured mean per-sample runtime in milliseconds.",
            "- The WAMI rows are full-dataset local runs; most API baseline rows are smaller sampled runs to control token cost.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    rows: list[dict[str, str]] = []
    add_wami(rows, "InjecAgent", DATA / "wami_paper_ablation_injecagent.csv")
    add_wami(rows, "BIPIA", DATA / "wami_paper_ablation_bipia.csv")
    add_wami(rows, "AgentDojo", DATA / "wami_paper_ablation_agentdojo.csv")

    add_baseline_file(
        rows,
        DATA / "table2_official_erase_check_qwen_max_raw_random100.csv",
        "raw original prompt",
        "official-code + qwen-max",
        "random sampled raw run",
    )
    add_baseline_file(
        rows,
        DATA / "erase_check_agentdojo_raw_random50.csv",
        "raw original prompt",
        "official-code + qwen-max",
        "random sampled raw AgentDojo run",
    )
    add_baseline_file(
        rows,
        DATA / "smoothllm_qwen_judge_random50.csv",
        "raw original prompt",
        "style-reproduction + qwen-max",
        "SmoothLLM-style perturbation with Qwen judge",
    )
    add_baseline_file(
        rows,
        DATA / "smoothllm_qwen_plus_2025_09_11_judge_random50.csv",
        "raw original prompt",
        "style-reproduction + qwen-plus",
        "SmoothLLM-style perturbation with Qwen judge",
    )
    add_baseline_file(
        rows,
        DATA / "smoothllm_qwen_turbo_judge_random50.csv",
        "raw original prompt",
        "style-reproduction + qwen-turbo",
        "SmoothLLM-style perturbation with Qwen judge",
    )
    add_baseline_file(
        rows,
        DATA / "smoothllm_qwen_turbo_agentdojo_raw_random50.csv",
        "raw original prompt",
        "style-reproduction + qwen-turbo",
        "SmoothLLM-style perturbation with Qwen judge",
    )

    out_csv = DATA / "paper_comparison_summary.csv"
    out_md = DATA / "paper_comparison_summary.md"
    fieldnames = [
        "dataset",
        "method",
        "input",
        "official_level",
        "ir",
        "fpr",
        "acc",
        "latency_ms",
        "total",
        "attack_n",
        "benign_n",
        "note",
    ]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    out_md.write_text(markdown(rows), encoding="utf-8")
    print(f"wrote {out_csv}")
    print(f"wrote {out_md}")


if __name__ == "__main__":
    main()
