from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


@dataclass
class DeltaRow:
    section: str
    item: str
    metric: str
    paper: float | None
    local: float | None
    unit: str
    equivalence: str
    cause: str
    improvement: str

    @property
    def delta(self) -> float | None:
        if self.paper is None or self.local is None:
            return None
        return self.local - self.paper


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def pct(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value * 100:.1f}%"


def pp(value: float | None) -> str:
    if value is None:
        return "-"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.1f} pp"


def ms(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.1f} ms"


def auc(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.3f}"


def fmt(row: DeltaRow, value: float | None, is_delta: bool = False) -> str:
    if row.unit == "percent":
        return pp(value) if is_delta else pct(value)
    if row.unit == "auc":
        if is_delta:
            if value is None:
                return "-"
            sign = "+" if value >= 0 else ""
            return f"{sign}{value:.3f}"
        return auc(value)
    if row.unit == "ms":
        if is_delta:
            if value is None:
                return "-"
            sign = "+" if value >= 0 else ""
            return f"{sign}{value:.1f} ms"
        return ms(value)
    if row.unit == "gb":
        if value is None:
            return "-"
        return f"{value:.2f} GB"
    return "-" if value is None else str(value)


def find_row(rows: list[dict[str, str]], **kwargs: str) -> dict[str, str]:
    for row in rows:
        if all(row.get(k) == v for k, v in kwargs.items()):
            return row
    raise KeyError(kwargs)


def main() -> None:
    summary = read_csv(DATA / "paper_comparison_summary.csv")
    table4 = read_csv(DATA / "table4_capability_proxy.csv")
    ablation = read_csv(DATA / "wami_paper_ablation_injecagent.csv")
    toolbench = read_csv(DATA / "toolbench_wami_capability_injecagent_model.csv")

    rows: list[DeltaRow] = []

    # Paper Table 1 values.
    table1_wami = {
        "BIPIA": {"ir": 0.889, "fpr": 0.015},
        "InjecAgent": {"ir": 0.903, "fpr": 0.012},
    }
    for dataset, paper_values in table1_wami.items():
        local = find_row(summary, dataset=dataset, method="WAMI (ours, full model)")
        for metric in ("ir", "fpr"):
            rows.append(
                DeltaRow(
                    "Table 1 main WAMI",
                    f"{dataset} WAMI",
                    metric.upper(),
                    paper_values[metric],
                    float(local[metric]),
                    "percent",
                    "method-level, not identical input pipeline",
                    "本地使用 converted intent/plan/TDG 全量数据；论文表格是完整 agent/benchmark 口径。",
                    "用原始 benchmark harness 生成 action trajectory，再经过同一个 WAMI gateway 评估。",
                )
            )

    # Paper Table 1 baselines not run.
    for dataset in ("BIPIA", "InjecAgent"):
        for method, ir, fpr in [
            ("GuardReasoner-VL", 0.625 if dataset == "BIPIA" else 0.384, 0.062 if dataset == "BIPIA" else 0.058),
            ("WebAgentGuard", 0.847 if dataset == "BIPIA" else 0.912, 0.285 if dataset == "BIPIA" else 0.364),
            ("BookAgent", 0.863 if dataset == "BIPIA" else 0.855, 0.148 if dataset == "BIPIA" else 0.172),
        ]:
            rows.append(
                DeltaRow(
                    "Table 1 baselines",
                    f"{dataset} {method}",
                    "IR/FPR",
                    None,
                    None,
                    "percent",
                    "not reproduced",
                    f"论文值为 IR {pct(ir)} / FPR {pct(fpr)}，但本地没有该 baseline 的官方模型和 harness 输出。",
                    "下载对应官方代码，固定同一数据切分，输出 IR/FPR 后再填入差值。",
                )
            )

    # Paper Table 2 values.
    table2 = {
        ("InjecAgent", "WAMI (ours, full model)"): (0.903, 0.012, 85.0),
        ("BIPIA", "WAMI (ours, full model)"): (0.889, 0.015, 90.0),
        ("InjecAgent", "Erase-and-Check official (qwen-max)"): (0.662, 0.105, 3100.0),
        ("BIPIA", "Erase-and-Check official (qwen-max)"): (0.635, 0.110, 3200.0),
        ("InjecAgent", "SmoothLLM-style perturbation + qwen-max judge"): (0.721, 0.079, 2400.0),
        ("BIPIA", "SmoothLLM-style perturbation + qwen-max judge"): (0.694, 0.082, 2450.0),
    }
    for (dataset, method), (paper_ir, paper_fpr, paper_latency) in table2.items():
        local = find_row(summary, dataset=dataset, method=method)
        label = f"{dataset} {method}"
        equivalence = "direct local WAMI" if method.startswith("WAMI") else "approximate baseline"
        cause = (
            "本地 WAMI 是轻量 NumPy/结构化计划实现，因此延迟远低于论文。"
            if method.startswith("WAMI")
            else "本地 baseline 使用 Qwen API 或 SmoothLLM-style judge，样本量也小于论文 full benchmark。"
        )
        improvement = (
            "用完整论文运行栈测端到端 latency，并固定同样数据切分。"
            if method.startswith("WAMI")
            else "跑完整 raw benchmark，统一模型、prompt、随机种子和样本量。"
        )
        for metric, paper_value, local_value in [
            ("IR", paper_ir, float(local["ir"])),
            ("FPR", paper_fpr, float(local["fpr"])),
            ("Latency", paper_latency, float(local["latency_ms"])),
        ]:
            rows.append(DeltaRow("Table 2 frontier comparison", label, metric, paper_value, local_value, "ms" if metric == "Latency" else "percent", equivalence, cause, improvement))

    for dataset in ("InjecAgent", "BIPIA"):
        for method, ir, fpr, lat in [
            ("ToolEmu-Sandbox", 0.756 if dataset == "InjecAgent" else 0.732, 0.136 if dataset == "InjecAgent" else 0.140, 5800.0 if dataset == "InjecAgent" else 5900.0),
            ("Llama-Guard 3 8B", 0.798 if dataset == "InjecAgent" else 0.774, 0.061 if dataset == "InjecAgent" else 0.065, 1150.0 if dataset == "InjecAgent" else 1180.0),
        ]:
            rows.append(
                DeltaRow(
                    "Table 2 missing baselines",
                    f"{dataset} {method}",
                    "IR/FPR/Latency",
                    None,
                    None,
                    "percent",
                    "not reproduced",
                    f"论文值为 IR {pct(ir)} / FPR {pct(fpr)} / latency about {lat:.0f} ms；本地未得到可比输出。",
                    "下载模型或完成 ToolEmu harness，按 raw benchmark 跑完整结果。",
                )
            )

    # Table 3.
    for backbone, paper_ir, paper_fpr in [
        ("GPT-4V", 0.878, 0.010),
        ("Llama-3-8B", 0.889, 0.015),
        ("Qwen-VL-Max", 0.903, 0.012),
    ]:
        local_ir = float(find_row(summary, dataset="InjecAgent", method="WAMI (ours, full model)")["ir"]) if backbone == "Qwen-VL-Max" else None
        local_fpr = float(find_row(summary, dataset="InjecAgent", method="WAMI (ours, full model)")["fpr"]) if backbone == "Qwen-VL-Max" else None
        rows.append(
            DeltaRow(
                "Table 3 cross-backbone",
                f"{backbone} WAMI IR",
                "IR",
                paper_ir,
                local_ir,
                "percent",
                "not strictly comparable" if local_ir is not None else "not reproduced",
                "本地没有严格替换 GPT-4V/Llama-3-8B/Qwen-VL-Max 多模态 backbone；Qwen-VL-Max 这里只能用 InjecAgent WAMI 本地行作近似参考。",
                "接入三个 backbone 的同一 agent harness，记录各自 action trajectory 后复跑 WAMI。",
            )
        )
        rows.append(
            DeltaRow(
                "Table 3 cross-backbone",
                f"{backbone} WAMI FPR",
                "FPR",
                paper_fpr,
                local_fpr,
                "percent",
                "not strictly comparable" if local_fpr is not None else "not reproduced",
                "同上，当前不是论文原始跨 backbone 实验。",
                "补齐 GPT-4V、Llama-3-8B、Qwen-VL-Max 的统一 agent 输出。",
            )
        )

    # Figure 4 AUC.
    for dataset, local_auc in [("InjecAgent", 0.667), ("BIPIA", 0.956), ("AgentDojo", 0.754)]:
        rows.append(
            DeltaRow(
                "Figure 4 ROC AUC",
                f"{dataset} WAMI AUC",
                "AUC",
                0.992,
                local_auc,
                "auc",
                "same metric, different dataset/score extraction",
                "论文 Figure 4 给的是整体 WAMI ROC AUC；本地是各数据集 MINE score AUC。InjecAgent/AgentDojo 的纯 MINE 分离弱于论文。",
                "用最终 gateway decision score 构造 ROC，而不是只用 MINE step score；同时增加 shadow training epoch 和 hard negatives。",
            )
        )

    # Table 4.
    local_proxy = find_row(table4, source="local_proxy", system="+ WAMI (Ours, proxy)")
    for metric, paper, local in [
        ("ToolBench SR", 0.680, float(local_proxy["toolbench_sr"])),
        ("AgentBench SR", 0.706, float(local_proxy["agentbench_sr"])),
        ("ToolBench Retention", 0.993, float(local_proxy["toolbench_retention"])),
        ("AgentBench Retention", 0.992, float(local_proxy["agentbench_retention"])),
    ]:
        rows.append(
            DeltaRow(
                "Table 4 capability",
                "WAMI proxy",
                metric,
                paper,
                local,
                "percent",
                "proxy, not official",
                "本地用 BIPIA/AgentDojo 良性放行率估计能力保持，不是 ToolBench/AgentBench 官方 SR。",
                "完成 ToolBench/AgentBench 官方 harness，计算 No Defense SR 与 WAMI SR。",
            )
        )
    no_def_sr = sum(1 for row in toolbench if row["win"] == "True") / max(1, len(toolbench))
    wami_sr = sum(1 for row in toolbench if row["win"] == "True" and row["wami_allowed"] == "True") / max(1, len(toolbench))
    rows.append(
        DeltaRow(
            "Table 4 capability",
            "ToolBench data_example WAMI",
            "ToolBench SR",
            0.680,
            wami_sr,
            "percent",
            "real ToolBench format, tiny sample",
            "只跑了 ToolBench data_example 的 15 条轨迹；No Defense 示例 SR 为 60.0%，和论文 full ToolBench 68.5% 不同。",
            "下载 reproduction_data/full data，跑六个 test subsets 的 ToolEval pass rate。",
        )
    )

    # Table 5.
    paper_ablation = {
        "WAMI (Full Model)": (0.903, 0.012, 85.0),
        "w/o TDG Graph Construction": (0.783, 0.045, 92.0),
        "w/o World Model Rollout": (0.642, 0.081, 35.0),
        "w/o MINE Gateway (Cosine Similarity)": (0.815, 0.058, 82.0),
        "w/o Shadow Adversarial Training": (0.757, 0.124, 85.0),
    }
    for variant, (paper_ir, paper_fpr, paper_lat) in paper_ablation.items():
        local = find_row(ablation, variant=variant)
        for metric, paper, local_value in [
            ("IR", paper_ir, float(local["ir"])),
            ("FPR", paper_fpr, float(local["fpr"])),
            ("Latency", paper_lat, float(local["latency_ms"])),
        ]:
            rows.append(
                DeltaRow(
                    "Table 5 ablation",
                    variant,
                    metric,
                    paper,
                    local_value,
                    "ms" if metric == "Latency" else "percent",
                    "same ablation name, local implementation",
                    "本地消融结构一致，但模型实现、数据转换、规则校准和端到端 runtime 与论文不同。",
                    "统一到论文的 agent trajectory 输入，冻结 gateway calibration，再跑 ablation。",
                )
            )

    # Figure 6 latency components.
    for item, paper, local in [
        ("TDG construction", 15.0, 0.0377),
        ("World model rollout", 45.0, 1.0137),
        ("MINE gateway", 25.0, 0.1455),
        ("WAMI total", 85.0, 1.1970),
    ]:
        rows.append(
            DeltaRow(
                "Figure 6 latency",
                item,
                "Latency",
                paper,
                local,
                "ms",
                "same component idea, different runtime scale",
                "本地是轻量 NumPy/文本 TDG 实现，没有论文完整多模态 agent 和部署开销。",
                "用同一硬件、完整 agent loop、显式计时 TDG/world/MINE，并报告 mean/p95。",
            )
        )

    # Figure 7.
    for item, paper in [("WAMI VRAM", 0.45), ("Llama-Guard 3 VRAM", 16.0), ("SmoothVLM/Erase KV cache", 3.5), ("ToolEmu-Sandbox VRAM lower bound", 16.0)]:
        rows.append(
            DeltaRow(
                "Figure 7 VRAM",
                item,
                "VRAM",
                paper,
                None,
                "gb",
                "not measured",
                "本地没有做 GPU memory profiling。",
                "用 nvidia-smi 或 torch.cuda.max_memory_allocated 分别测 batch=1 的 WAMI/baseline 显存。",
            )
        )

    # Figure 8.
    rows.append(
        DeltaRow(
            "Figure 8 MI convergence",
            "InjecAgent MI gap epoch 8",
            "MI gap",
            None,
            1.2694,
            "raw",
            "local supporting evidence",
            "论文图展示 epoch 15 左右稳定分离；本地 InjecAgent 子集到 epoch 8 已从 0.1576 增至 1.2694。",
            "跑满 30 epoch 并保存 benign/attack 两条 MI 曲线，而不只报告 gap。",
        )
    )

    out_csv = DATA / "paper_vs_local_numeric_deltas.csv"
    out_md = DATA / "paper_vs_local_numeric_deltas.md"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "section",
                "item",
                "metric",
                "paper",
                "local",
                "delta",
                "unit",
                "equivalence",
                "cause",
                "improvement",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "section": row.section,
                    "item": row.item,
                    "metric": row.metric,
                    "paper": row.paper,
                    "local": row.local,
                    "delta": row.delta,
                    "unit": row.unit,
                    "equivalence": row.equivalence,
                    "cause": row.cause,
                    "improvement": row.improvement,
                }
            )

    lines = [
        "# Paper vs local numeric delta report",
        "",
        "差值定义：`Delta = Local - Paper`。IR/SR/Retention/AUC 越高越好，FPR/Latency/VRAM 越低越好。",
        "",
    ]
    for section in dict.fromkeys(row.section for row in rows):
        lines.append(f"## {section}")
        lines.append("")
        lines.append("| Item | Metric | Paper | Local | Delta | Equivalence | Cause | Improvement |")
        lines.append("|---|---|---:|---:|---:|---|---|---|")
        for row in [r for r in rows if r.section == section]:
            lines.append(
                f"| {row.item} | {row.metric} | {fmt(row, row.paper)} | {fmt(row, row.local)} | {fmt(row, row.delta, True)} | {row.equivalence} | {row.cause} | {row.improvement} |"
            )
        lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out_csv}")
    print(f"wrote {out_md}")


if __name__ == "__main__":
    main()
