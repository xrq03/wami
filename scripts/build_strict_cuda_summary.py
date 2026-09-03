from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


@dataclass
class StrictRow:
    dataset: str
    train_n: int
    eval_n: int
    ir: float
    fpr: float
    acc: float
    final_loss: float
    final_mi_gap: float
    tdg_ms: float
    world_ms: float
    mine_ms: float
    total_ms: float
    peak_vram_mb: float
    full_ablation_ir: float
    full_ablation_fpr: float
    wo_tdg_ir: float
    wo_world_ir: float
    wo_mine_ir: float
    wo_shadow_ir: float
    note: str


def pct_to_float(value: str) -> float:
    return float(value.strip().rstrip("%")) / 100.0


def read_csv_one(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1:
        raise ValueError(f"expected one row in {path}, got {len(rows)}")
    return rows[0]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_training_md(path: Path) -> tuple[int, int, float, float, float, float]:
    text = path.read_text(encoding="utf-8")
    train_n = int(re.search(r"Train samples: `(\d+)`", text).group(1))
    eval_match = re.search(r"\|\s*\w+_wami\s*\|\s*([\d.]+%)\s*\|\s*([\d.]+%)\s*\|\s*([\d.]+%)\s*\|\s*(\d+)\s*\|", text)
    if not eval_match:
        raise ValueError(f"evaluation row not found in {path}")
    ir, fpr, acc, eval_n = eval_match.groups()
    progress_rows = read_csv_rows(path.with_suffix(".csv"))
    final = progress_rows[-1]
    return (
        train_n,
        int(eval_n),
        pct_to_float(ir),
        pct_to_float(fpr),
        pct_to_float(acc),
        float(final["loss"]),
        float(final["mi_gap"]),
    )


def find_variant(rows: list[dict[str, str]], variant: str) -> dict[str, str]:
    for row in rows:
        if row["variant"] == variant:
            return row
    raise KeyError(variant)


def build_row(dataset: str, stem: str) -> StrictRow:
    train_n, eval_n, ir, fpr, acc, final_loss, final_mi_gap = parse_training_md(
        DATA / f"wami_paper_strict_{stem}_512_e5_cuda.md"
    )
    latency = read_csv_one(DATA / f"wami_paper_latency_{stem}_512_e5_cuda.csv")
    memory = read_csv_one(DATA / f"wami_cuda_memory_{stem}_512_e5.csv")
    ablation = read_csv_rows(DATA / f"wami_paper_strict_ablation_{stem}_512_e5_cuda.csv")
    full = find_variant(ablation, "WAMI (Full Model)")
    wo_tdg = find_variant(ablation, "w/o TDG Graph Construction")
    wo_world = find_variant(ablation, "w/o World Model Rollout")
    wo_mine = find_variant(ablation, "w/o MINE Gateway (Cosine Similarity)")
    wo_shadow = find_variant(ablation, "w/o Shadow Adversarial Training")
    note = (
        "512-sample CUDA strict reproduction; internal split/in-sample smoke, not final held-out full benchmark."
    )
    return StrictRow(
        dataset=dataset,
        train_n=train_n,
        eval_n=eval_n,
        ir=ir,
        fpr=fpr,
        acc=acc,
        final_loss=final_loss,
        final_mi_gap=final_mi_gap,
        tdg_ms=float(latency["tdg_ms"]),
        world_ms=float(latency["world_ms"]),
        mine_ms=float(latency["mine_ms"]),
        total_ms=float(latency["total_ms"]),
        peak_vram_mb=float(memory["peak_allocated_mb"]),
        full_ablation_ir=float(full["ir"]),
        full_ablation_fpr=float(full["fpr"]),
        wo_tdg_ir=float(wo_tdg["ir"]),
        wo_world_ir=float(wo_world["ir"]),
        wo_mine_ir=float(wo_mine["ir"]),
        wo_shadow_ir=float(wo_shadow["ir"]),
        note=note,
    )


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def markdown(rows: list[StrictRow]) -> str:
    lines = [
        "# WAMI Paper-Strict CUDA Summary",
        "",
        "All rows use the stricter WAMI implementation: 4-layer Transformer Encoder, 1024 hidden dimension, 8 heads, 3-layer ReLU MINE, AdamW, cosine schedule, CUDA inference.",
        "",
        "| Dataset | Eval IR | Eval FPR | Eval ACC | Final MI gap | Latency ms | World ms | MINE ms | Peak VRAM MB | w/o TDG IR | w/o World IR | w/o MINE IR | w/o Shadow IR | Note |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.dataset} | {pct(row.ir)} | {pct(row.fpr)} | {pct(row.acc)} | "
            f"{row.final_mi_gap:.3f} | {row.total_ms:.3f} | {row.world_ms:.3f} | {row.mine_ms:.3f} | "
            f"{row.peak_vram_mb:.1f} | {pct(row.wo_tdg_ir)} | {pct(row.wo_world_ir)} | "
            f"{pct(row.wo_mine_ir)} | {pct(row.wo_shadow_ir)} | {row.note} |"
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "- Eval IR/FPR/ACC are from the 512-sample strict CUDA run.",
            "- Ablation IR columns are from the 100-sample strict ablation probe for the same checkpoint.",
            "- These results close the architecture-level reproduction gap, but the final paper-quality run still needs held-out/full-dataset training and evaluation.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = [
        build_row("InjecAgent", "injecagent"),
        build_row("BIPIA", "bipia"),
        build_row("AgentDojo", "agentdojo"),
    ]
    csv_path = DATA / "wami_paper_strict_cuda_summary.csv"
    md_path = DATA / "wami_paper_strict_cuda_summary.md"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(StrictRow.__dataclass_fields__.keys()))
        writer.writeheader()
        writer.writerows([row.__dict__ for row in rows])
    md_path.write_text(markdown(rows), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))
    print(f"saved {md_path}")
    print(f"saved {csv_path}")


if __name__ == "__main__":
    main()
