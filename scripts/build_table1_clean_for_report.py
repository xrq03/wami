from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Row:
    dataset: str
    method: str
    ir: float | None
    fpr: float | None
    acc: float | None
    latency_ms: float | None
    level: str
    source: str
    note: str


def main() -> None:
    rows = build_rows()
    write(rows, ROOT / "data/table1_clean_for_report.md", ROOT / "data/table1_clean_for_report.csv")
    print(format_md(rows))
    print("saved data/table1_clean_for_report.md")
    print("saved data/table1_clean_for_report.csv")


def build_rows() -> list[Row]:
    agentdojo = load_by_dataset(ROOT / "data/agentdojo_official_detector_wami_datasets_full.csv")
    bookagent = load_by_dataset(ROOT / "data/bookagent_constraint_verifier_full.csv")
    wami_ensemble = load_wami_ensemble(ROOT / "data/paper_mine_ensemble_sourceaware_triplet_taua45_taub50_results.csv")
    wami_agentdojo = load_by_dataset(ROOT / "data/paper_mine_triplet_slot_seed4071_e4_tau50_results.csv")
    live = {
        "InjecAgent": load_single(ROOT / "data/live_planner_wami_injecagent_qwen3_10x10_summary.csv"),
        "BIPIA": load_single(ROOT / "data/live_planner_wami_bipia_qwen3_10x10_summary.csv"),
        "AgentDojo": load_single(ROOT / "data/live_planner_wami_agentdojo_qwen3_10x10_summary.csv"),
    }

    rows: list[Row] = []
    for dataset in ["BIPIA", "InjecAgent", "AgentDojo"]:
        rows.append(Row(dataset, "GuardReasoner-VL", None, None, None, None, "missing-official", "", "Official agent-trajectory adapter/checkpoint not available."))
        book = bookagent.get(dataset)
        rows.append(
            Row(
                dataset,
                "BookAgent-style Constraint Verifier",
                f(book, "ir"),
                f(book, "fpr"),
                f(book, "acc"),
                f(book, "latency_ms"),
                "method-level",
                "data/bookagent_constraint_verifier_full.csv",
                "BookAgent VAS/ICR/TCC safety constraints adapted to agent trajectories.",
            )
        )
        dojo = agentdojo.get(dataset)
        rows.append(
            Row(
                dataset,
                "AgentDojo official PI detector",
                f(dojo, "ir"),
                f(dojo, "fpr"),
                f(dojo, "acc"),
                f(dojo, "latency_ms"),
                "official-local-detector",
                "data/agentdojo_official_detector_wami_datasets_full.csv",
                "Official AgentDojo detector logic; WAMI-format tool-output adapter.",
            )
        )
        if dataset == "AgentDojo":
            wami = wami_agentdojo.get("AgentDojo")
            source = "data/paper_mine_triplet_slot_seed4071_e4_tau50_results.csv"
        else:
            key = "bipia_wami" if dataset == "BIPIA" else "injecagent_wami"
            wami = wami_ensemble.get((key, "or"))
            source = "data/paper_mine_ensemble_sourceaware_triplet_taua45_taub50_results.csv"
        rows.append(
            Row(
                dataset,
                "WAMI paper-faithful replay",
                f(wami, "ir"),
                f(wami, "fpr"),
                f(wami, "acc"),
                f(wami, "latency_ms"),
                "main-replay",
                source,
                "Main action-level replay result.",
            )
        )
        live_row = live.get(dataset)
        rows.append(
            Row(
                dataset,
                "Live planner + WAMI",
                f(live_row, "ir"),
                f(live_row, "fpr"),
                f(live_row, "acc"),
                f(live_row, "latency_ms"),
                "live-agent-small",
                f"data/live_planner_wami_{dataset.lower()}_qwen3_10x10_summary.csv",
                f"Small qwen3-32b planner-only run; WAMI action block rate {pct(f(live_row, 'wami_action_block_rate'))}.",
            )
        )
    return rows


def load_by_dataset(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {norm(row["dataset"]): row for row in csv.DictReader(handle)}


def load_single(path: Path) -> dict[str, str] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8", newline="") as handle:
        return next(csv.DictReader(handle), None)


def load_wami_ensemble(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    if not path.exists():
        return {}
    rows = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows[(row["dataset"], row["mode"])] = row
    return rows


def norm(name: str) -> str:
    mapping = {"bipia": "BIPIA", "injecagent": "InjecAgent", "agentdojo": "AgentDojo"}
    return mapping.get(name.strip().lower().replace("_wami", ""), name)


def f(row: dict[str, str] | None, key: str) -> float | None:
    if not row:
        return None
    value = row.get(key)
    return float(value) if value not in (None, "") else None


def pct(value: float | None) -> str:
    return "" if value is None else f"{value * 100:.1f}%"


def ms(value: float | None) -> str:
    return "" if value is None else f"{value:.3f}"


def format_md(rows: list[Row]) -> str:
    lines = [
        "# Clean Table 1 For Report",
        "",
        "This version separates missing official baselines, method-level baselines, local official detectors, WAMI replay, and small live-agent evidence. WebAgentGuard-style no-API is intentionally excluded from the main table because it is too rule-like and should stay in appendix.",
        "",
        "| Dataset | Method | IR | FPR | ACC | Latency ms | Level | Source | Note |",
        "|---|---|---:|---:|---:|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.dataset} | {row.method} | {pct(row.ir)} | {pct(row.fpr)} | {pct(row.acc)} | "
            f"{ms(row.latency_ms)} | {row.level} | `{row.source}` | {row.note} |"
        )
    return "\n".join(lines)


def write(rows: list[Row], md_path: Path, csv_path: Path) -> None:
    md_path.write_text(format_md(rows) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
