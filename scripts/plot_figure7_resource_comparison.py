from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load_rows() -> list[dict[str, str]]:
    path = DATA / "final_figure7_resource_comparison.csv"
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    rows = load_rows()
    methods = [r["defense"] for r in rows]
    footprint = [float(r["footprint_gib"]) for r in rows]
    toolbench_ms = [float(r["toolbench_latency_ms"]) for r in rows]
    agentbench_ms = [float(r["agentbench_latency_ms"]) for r in rows]

    colors = ["#2E6F95", "#C44E52", "#8172B2", "#55A868"]
    x = np.arange(len(methods))

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.dpi": 180,
        }
    )

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.5), constrained_layout=True)

    ax = axes[0]
    bars = ax.bar(x, footprint, color=colors, width=0.62)
    ax.set_ylabel("Memory / model footprint (GiB)")
    ax.set_title("Defense footprint")
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=22, ha="right")
    ax.grid(axis="y", color="#E5E5E5", linewidth=0.8)
    for bar, value in zip(bars, footprint):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + max(footprint) * 0.025,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax = axes[1]
    width = 0.34
    ax.bar(x - width / 2, toolbench_ms, width, label="ToolBench", color="#4C72B0")
    ax.bar(x + width / 2, agentbench_ms, width, label="AgentBench", color="#DD8452")
    ax.set_ylabel("Defense latency (ms)")
    ax.set_title("Runtime overhead")
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=22, ha="right")
    ax.grid(axis="y", color="#E5E5E5", linewidth=0.8)
    ax.legend(frameon=False)

    fig.suptitle("Figure 7. Resource Overhead Comparison", fontsize=13, y=1.03)
    fig.text(
        0.5,
        -0.03,
        "WAMI uses measured CUDA peak reserved memory. LLM baselines use local Ollama model-layer footprint proxy.",
        ha="center",
        fontsize=9,
        color="#555555",
    )

    out_png = DATA / "final_figure7_resource_comparison.png"
    out_pdf = DATA / "final_figure7_resource_comparison.pdf"
    fig.savefig(out_png, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    print(out_png)
    print(out_pdf)


if __name__ == "__main__":
    main()
