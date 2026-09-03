from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


COLORS = {
    "WAMI": "#0B3A67",
    "GuardReasoner-VL": "#8A94A6",
    "WebAgentGuard": "#A778B4",
    "BookAgent-style": "#64A66A",
    "AgentDojo PID": "#B08A5B",
    "Llama-Guard 3": "#D47A3C",
    "InjecAgent": "#2F6B9A",
    "BIPIA": "#3E8F6A",
    "AgentDojo": "#B94D5A",
    "grid": "#E8EBEF",
    "text": "#20242A",
    "muted": "#6B7280",
}


def pct(x: float) -> float:
    return x * 100.0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save(fig: plt.Figure, stem: str) -> None:
    png = DATA / f"{stem}.png"
    pdf = DATA / f"{stem}.pdf"
    fig.savefig(png, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(png)
    print(pdf)


def setup() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "text.color": COLORS["text"],
            "axes.labelcolor": COLORS["text"],
            "axes.titlecolor": COLORS["text"],
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": False,
            "axes.spines.bottom": False,
            "figure.dpi": 180,
            "axes.grid": True,
            "grid.color": COLORS["grid"],
            "grid.linewidth": 0.8,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "xtick.color": COLORS["muted"],
            "ytick.color": COLORS["text"],
        }
    )


def short_method(method: str) -> str:
    if method.startswith("GuardReasoner"):
        return "GuardReasoner-VL"
    if method.startswith("Llama-Guard"):
        return "Llama-Guard 3"
    if method.startswith("WebAgentGuard"):
        return "WebAgentGuard"
    if method.startswith("BookAgent"):
        return "BookAgent-style"
    if method.startswith("AgentDojo"):
        return "AgentDojo PID"
    if method.startswith("WAMI"):
        return "WAMI"
    return method


def plot_figure3() -> None:
    rows = read_csv(DATA / "final_table1_reproduction.csv")
    datasets = ["InjecAgent", "BIPIA", "AgentDojo"]
    methods = [
        "GuardReasoner-VL",
        "WebAgentGuard",
        "BookAgent-style",
        "AgentDojo PID",
        "Llama-Guard 3",
        "WAMI",
    ]
    values = {(r["dataset"], short_method(r["method"])): r for r in rows}

    fig, axes = plt.subplots(
        len(datasets),
        2,
        figsize=(12.8, 8.6),
        sharex="col",
        constrained_layout=True,
    )
    y = np.arange(len(methods))
    method_colors = [COLORS[m] if m in COLORS else "#A0AEC0" for m in methods]
    for row_idx, ds in enumerate(datasets):
        for col_idx, (metric, title, limit_line) in enumerate(
            [("ir", "Interception Rate", 90), ("fpr", "False Positive Rate", 10)]
        ):
            ax = axes[row_idx, col_idx]
            vals = [pct(float(values[(ds, m)][metric])) for m in methods]
            ax.barh(y, vals, color=method_colors, height=0.66, edgecolor="white", linewidth=0.8)
            ax.set_xlim(0, 105)
            ax.set_yticks(y)
            ax.set_yticklabels(methods if col_idx == 0 else [])
            ax.invert_yaxis()
            ax.set_title(f"{ds} - {title}", loc="left", fontsize=12, fontweight="bold")
            ax.axvline(limit_line, color="#3D4652", linewidth=1.0, linestyle=(0, (3, 3)), alpha=0.75)
            ax.grid(axis="x")
            ax.grid(axis="y", visible=False)
            for idx, value in enumerate(vals):
                label_x = min(value + 1.4, 101)
                ax.text(label_x, idx, f"{value:.1f}", va="center", fontsize=9.5, color=COLORS["text"])
            if row_idx == len(datasets) - 1:
                ax.set_xlabel("Percent")
    fig.suptitle("Figure 3. Defense Performance Across Benchmarks", fontsize=16, fontweight="bold")
    save(fig, "final_figure3_main_results")


def plot_figure4() -> None:
    files = {
        "InjecAgent": DATA / "wami_extra_injecagent_roc.csv",
        "BIPIA": DATA / "wami_extra_bipia_roc.csv",
        "AgentDojo": DATA / "wami_extra_agentdojo_roc.csv",
    }
    fig, ax = plt.subplots(figsize=(7.0, 5.4), constrained_layout=True)
    for ds, path in files.items():
        rows = read_csv(path)
        fpr = [float(r["fpr"]) for r in rows]
        tpr = [float(r["tpr"]) for r in rows]
        auc = float(rows[0]["auc"])
        ax.plot(fpr, tpr, linewidth=2.7, color=COLORS[ds], label=f"{ds}  AUC={auc:.3f}")
    ax.plot([0, 1], [0, 1], color="#AEB6C2", linewidth=1.2, linestyle="--", label="Random")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("Figure 4. WAMI ROC Curves", fontsize=15, fontweight="bold")
    ax.grid(True)
    ax.legend(frameon=True, facecolor="white", edgecolor="#E5E7EB", loc="lower right")
    save(fig, "final_figure4_wami_roc")


def plot_figure5() -> None:
    files = {
        "InjecAgent": DATA / "wami_extra_injecagent_threshold_sensitivity.csv",
        "BIPIA": DATA / "wami_extra_bipia_threshold_sensitivity.csv",
        "AgentDojo": DATA / "wami_extra_agentdojo_threshold_sensitivity.csv",
    }
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.9), constrained_layout=True)
    for ds, path in files.items():
        rows = read_csv(path)
        xs = np.linspace(0, 100, len(rows))
        ir = [pct(float(r["ir"])) for r in rows]
        fpr = [pct(float(r["fpr"])) for r in rows]
        axes[0].plot(xs, ir, linewidth=2.4, color=COLORS[ds], label=ds)
        axes[1].plot(xs, fpr, linewidth=2.4, color=COLORS[ds], label=ds)
    axes[0].set_title("IR under threshold sweep")
    axes[1].set_title("FPR under threshold sweep")
    for ax in axes:
        ax.set_xlabel("Operating point percentile")
        ax.set_ylabel("Percent")
        ax.set_ylim(0, 105)
        ax.grid(True)
        ax.legend(frameon=True, facecolor="white", edgecolor="#E5E7EB")
    fig.suptitle("Figure 5. WAMI Threshold Sensitivity", fontsize=15, fontweight="bold")
    save(fig, "final_figure5_threshold_sensitivity")


def plot_figure6() -> None:
    paths = {
        "InjecAgent": DATA / "wami_paper_latency_injecagent_512_e5_cuda.csv",
        "BIPIA": DATA / "wami_paper_latency_bipia_512_e5_cuda.csv",
        "AgentDojo": DATA / "wami_paper_latency_agentdojo_512_e5_cuda.csv",
    }
    datasets = list(paths)
    tdg, world, mine, other = [], [], [], []
    for ds in datasets:
        row = read_csv(paths[ds])[0]
        t = float(row["tdg_ms"])
        w = float(row["world_ms"])
        m = float(row["mine_ms"])
        total = float(row["total_ms"])
        tdg.append(t)
        world.append(w)
        mine.append(m)
        other.append(max(0.0, total - t - w - m))

    x = np.arange(len(datasets))
    fig, ax = plt.subplots(figsize=(7.8, 5.1), constrained_layout=True)
    ax.bar(x, tdg, label="TDG construction", color="#7895B2")
    ax.bar(x, world, bottom=tdg, label="World model", color="#3E8F6A")
    bottom = np.array(tdg) + np.array(world)
    ax.bar(x, mine, bottom=bottom, label="MINE gateway", color="#B94D5A")
    bottom = bottom + np.array(mine)
    ax.bar(x, other, bottom=bottom, label="Runtime overhead", color="#CBD5E1")
    totals = np.array(tdg) + np.array(world) + np.array(mine) + np.array(other)
    for idx, total in enumerate(totals):
        ax.text(idx, total + 0.8, f"{total:.1f} ms", ha="center", fontsize=10, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(datasets)
    ax.set_ylabel("Latency (ms)")
    ax.set_title("Figure 6. WAMI Latency Decomposition", fontsize=15, fontweight="bold")
    ax.legend(frameon=True, facecolor="white", edgecolor="#E5E7EB", ncol=2)
    save(fig, "final_figure6_latency_decomposition")


def plot_figure7() -> None:
    rows = read_csv(DATA / "final_figure7_resource_comparison.csv")
    methods = [r["defense"].replace(" gateway", "") for r in rows]
    footprint = [float(r["footprint_gib"]) for r in rows]
    toolbench_ms = [float(r["toolbench_latency_ms"]) for r in rows]
    agentbench_ms = [float(r["agentbench_latency_ms"]) for r in rows]
    x = np.arange(len(methods))
    colors = ["#2E6F95", "#C44E52", "#8172B2", "#55A868"]

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.9), constrained_layout=True)
    bars = axes[0].bar(x, footprint, color=colors, width=0.62)
    axes[0].set_title("Defense footprint", fontweight="bold")
    axes[0].set_ylabel("GiB")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(methods, rotation=18, ha="right")
    for bar, value in zip(bars, footprint):
        axes[0].text(bar.get_x() + bar.get_width() / 2, value + 0.08, f"{value:.2f}", ha="center", fontsize=9)

    width = 0.34
    axes[1].bar(x - width / 2, toolbench_ms, width, label="ToolBench", color="#4C72B0")
    axes[1].bar(x + width / 2, agentbench_ms, width, label="AgentBench", color="#DD8452")
    axes[1].set_title("Runtime overhead", fontweight="bold")
    axes[1].set_ylabel("Latency (ms)")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(methods, rotation=18, ha="right")
    axes[1].legend(frameon=True, facecolor="white", edgecolor="#E5E7EB")
    fig.suptitle("Figure 7. Resource Overhead Comparison", fontsize=15, fontweight="bold")
    save(fig, "final_figure7_resource_comparison_v2")


def write_index() -> None:
    lines = [
        "# Final Figures 3-8",
        "",
        "These figures are regenerated from the final accepted local result files.",
        "",
        "| Figure | File | Data source | Meaning |",
        "|---|---|---|---|",
        "| Figure 3 | `data/final_figure3_main_results.png` | `data/final_table1_reproduction.csv` | Main IR/FPR defense comparison. |",
        "| Figure 4 | `data/final_figure4_wami_roc.png` | `data/wami_extra_*_roc.csv` | WAMI ROC and AUC on the three datasets. |",
        "| Figure 5 | `data/final_figure5_threshold_sensitivity.png` | `data/wami_extra_*_threshold_sensitivity.csv` | IR/FPR movement under threshold sweep. |",
        "| Figure 6 | `data/final_figure6_latency_decomposition.png` | `data/wami_paper_latency_*_512_e5_cuda.csv` | Paper-strict CUDA TDG/world/MINE latency decomposition. |",
        "| Figure 7 | `data/final_figure7_resource_comparison_v2.png` | `data/final_figure7_resource_comparison.csv` | Defense footprint and latency overhead. |",
        "| Figure 8 | `data/final_figure8_shadow_training.png` | `data/paper_mine_*_training.csv` | Shadow adversarial training MI-gap and loss dynamics. |",
    ]
    (DATA / "final_figures_3_to_8.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    setup()
    plot_figure3()
    plot_figure4()
    plot_figure5()
    plot_figure6()
    plot_figure7()
    write_index()
    print(DATA / "final_figures_3_to_8.md")


if __name__ == "__main__":
    main()
