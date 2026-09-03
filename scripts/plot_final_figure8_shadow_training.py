from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


FINAL_RUNS = {
    "Source-aware WAMI": DATA / "paper_mine_sourceaware_recall_seed2061_e4_training.csv",
    "Triplet-slot WAMI": DATA / "paper_mine_triplet_slot_seed4071_e4_training.csv",
    "Transition-fusion WAMI": DATA / "paper_mine_transition_v2_seed2051_e4_training.csv",
    "Paired-recall WAMI": DATA / "paper_mine_paired_recall_v1fast_e4_training.csv",
}

SUPPLEMENTAL_RUNS = {
    "InjecAgent legacy": DATA / "wami_extra_injecagent_training_dynamics.csv",
    "BIPIA legacy": DATA / "wami_extra_bipia_training_dynamics.csv",
    "AgentDojo legacy": DATA / "wami_extra_agentdojo_training_dynamics.csv",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def setup() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "text.color": "#20242A",
            "axes.labelcolor": "#20242A",
            "axes.titlecolor": "#20242A",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": False,
            "axes.spines.bottom": False,
            "figure.dpi": 180,
            "axes.grid": True,
            "grid.color": "#E8EBEF",
            "grid.linewidth": 0.8,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "xtick.color": "#6B7280",
            "ytick.color": "#6B7280",
        }
    )


def plot() -> None:
    setup()
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.9), constrained_layout=True)

    colors = ["#0B3A67", "#3E8F6A", "#B94D5A", "#8A6BBE"]
    for (label, path), color in zip(FINAL_RUNS.items(), colors):
        rows = read_csv(path)
        epochs = [int(r["epoch"]) for r in rows]
        mi_gap = [float(r["mi_gap"]) for r in rows]
        loss = [float(r["loss"]) for r in rows]
        axes[0].plot(epochs, mi_gap, marker="o", markersize=5.5, linewidth=2.5, color=color, label=label)
        axes[1].plot(epochs, loss, marker="o", markersize=5.5, linewidth=2.5, color=color, label=label)

    axes[0].set_title("MI gap during shadow training", fontweight="bold")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("MI gap")
    axes[1].set_title("Training loss", fontweight="bold")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Loss")
    for ax in axes:
        ax.grid(True)
        ax.legend(frameon=True, facecolor="white", edgecolor="#E5E7EB", fontsize=9)
    fig.suptitle("Figure 8. Shadow Adversarial Training Dynamics", fontsize=15, fontweight="bold")
    out_png = DATA / "final_figure8_shadow_training.png"
    out_pdf = DATA / "final_figure8_shadow_training.pdf"
    fig.savefig(out_png, bbox_inches="tight", facecolor="white")
    fig.savefig(out_pdf, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(out_png)
    print(out_pdf)

    # Supplemental three-dataset curve from the longer legacy dynamics.
    fig, ax = plt.subplots(figsize=(7.0, 4.8), constrained_layout=True)
    for label, path in SUPPLEMENTAL_RUNS.items():
        rows = read_csv(path)
        if len(rows) < 2:
            continue
        epochs = [int(r["epoch"]) for r in rows]
        mi_gap = [float(r["mi_gap"]) for r in rows]
        ax.plot(epochs, mi_gap, marker="o", linewidth=2.3, label=label)
    ax.set_title("Supplemental MI gap on dataset-specific training", fontweight="bold")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MI gap")
    ax.legend(frameon=True, facecolor="white", edgecolor="#E5E7EB")
    supp_png = DATA / "final_figure8_shadow_training_supplemental.png"
    supp_pdf = DATA / "final_figure8_shadow_training_supplemental.pdf"
    fig.savefig(supp_png, bbox_inches="tight", facecolor="white")
    fig.savefig(supp_pdf, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(supp_png)
    print(supp_pdf)

    index = DATA / "final_figure8_shadow_training.md"
    index.write_text(
        "\n".join(
            [
                "# Final Figure 8 Shadow Training",
                "",
                "| Figure | File | Data source |",
                "|---|---|---|",
                "| Main Figure 8 | `data/final_figure8_shadow_training.png` | paper-faithful source-aware / triplet-slot / transition / paired training logs |",
                "| Supplemental | `data/final_figure8_shadow_training_supplemental.png` | longer dataset-specific legacy MI-gap logs |",
                "",
                "The main curve uses the paper-faithful WAMI variants that feed the final accepted WAMI rows. The supplemental curve is kept only to show longer epoch behavior where available.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(index)


if __name__ == "__main__":
    plot()
