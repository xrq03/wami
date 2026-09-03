from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OLLAMA = Path("D:/OllamaModels")


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def mb_to_gb(mb: float) -> float:
    return mb / 1024.0


def bytes_to_gib(n: int) -> float:
    return n / (1024.0**3)


def read_summary(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return {row["method"]: row for row in csv.DictReader(f)}


def read_wami_cpu_profile() -> dict[str, float]:
    path = DATA / "wami_resource_profile.csv"
    rows = list(csv.DictReader(path.open("r", encoding="utf-8", newline="")))
    return {
        "model_size_mb": max(float(r["model_size_mb"]) for r in rows),
        "avg_latency_ms": sum(float(r["avg_latency_ms"]) for r in rows) / len(rows),
        "p95_latency_ms": max(float(r["p95_latency_ms"]) for r in rows),
    }


def read_wami_cuda_peak_mb() -> dict[str, float]:
    peaks = []
    allocs = []
    for path in DATA.glob("wami_cuda_memory_*_512_e5.csv"):
        rows = list(csv.DictReader(path.open("r", encoding="utf-8", newline="")))
        if not rows:
            continue
        row = rows[0]
        peaks.append(float(row["peak_reserved_mb"]))
        allocs.append(float(row["peak_allocated_mb"]))
    return {
        "peak_reserved_mb": max(peaks) if peaks else 0.0,
        "peak_allocated_mb": max(allocs) if allocs else 0.0,
    }


def ollama_model_layer_size_bytes(model: str, tag: str) -> int:
    manifest = OLLAMA / "manifests" / "registry.ollama.ai" / "library" / model / tag
    obj = json.loads(manifest.read_text(encoding="utf-8"))
    model_layers = [
        layer
        for layer in obj.get("layers", [])
        if layer.get("mediaType", "").endswith("model")
    ]
    if not model_layers:
        raise RuntimeError(f"No model layer found in {manifest}")
    return int(model_layers[0]["size"])


def row(
    defense: str,
    runtime_basis: str,
    footprint_kind: str,
    footprint_gib: float,
    toolbench_latency_ms: float,
    agentbench_latency_ms: float,
    notes: str,
) -> dict[str, str]:
    return {
        "defense": defense,
        "runtime_basis": runtime_basis,
        "footprint_kind": footprint_kind,
        "footprint_gib": f"{footprint_gib:.3f}",
        "toolbench_latency_ms": f"{toolbench_latency_ms:.1f}",
        "agentbench_latency_ms": f"{agentbench_latency_ms:.1f}",
        "notes": notes,
    }


def main() -> None:
    toolbench = read_summary(DATA / "toolbench_default_evalset_qwen25_table4_600_summary.csv")
    agentbench = read_summary(DATA / "agentbench_proxy_table4_nonlite_qwen25_summary.csv")
    wami_cpu = read_wami_cpu_profile()
    wami_cuda = read_wami_cuda_peak_mb()
    qwen25_gib = bytes_to_gib(ollama_model_layer_size_bytes("qwen2.5", "7b-instruct"))
    llama_guard_gib = bytes_to_gib(ollama_model_layer_size_bytes("llama-guard3", "8b"))

    rows = [
        row(
            "WAMI gateway",
            "Paper-style WAMI defense module; qwen2.5 planner is shared with no-defense and not counted as defense memory.",
            "Measured CUDA peak reserved",
            mb_to_gb(wami_cuda["peak_reserved_mb"]),
            float(toolbench["WAMI + qwen2.5 local agent"]["latency_ms"]),
            float(agentbench["WAMI + qwen2.5 local agent"]["latency_ms"]),
            f"NPZ model file {wami_cpu['model_size_mb']:.3f} MB; peak allocated {wami_cuda['peak_allocated_mb']:.1f} MB.",
        ),
        row(
            "Erase-and-Check",
            "Local qwen2.5 judge baseline.",
            "Ollama model layer footprint proxy",
            qwen25_gib,
            float(toolbench["Erase-and-Check qwen2.5 judge"]["latency_ms"]),
            float(agentbench["Erase-and-Check qwen2.5 judge"]["latency_ms"]),
            "Extra LLM judge beyond the shared planner; footprint is disk model layer, not synchronized VRAM profiler.",
        ),
        row(
            "ToolEmu-Sandbox",
            "Local qwen2.5 sandbox judge baseline.",
            "Ollama model layer footprint proxy",
            qwen25_gib,
            float(toolbench["ToolEmu-Sandbox qwen2.5 judge"]["latency_ms"]),
            float(agentbench["ToolEmu-Sandbox qwen2.5 judge"]["latency_ms"]),
            "Reproduced as local judge/sandbox protocol; official multi-agent ToolEmu can require larger model stacks.",
        ),
        row(
            "Llama-Guard 3 8B",
            "Local Ollama safety classifier.",
            "Ollama model layer footprint proxy",
            llama_guard_gib,
            float(toolbench["Llama-Guard 3 8B local/Ollama"]["latency_ms"]),
            float(agentbench["Llama-Guard 3 8B local/Ollama"]["latency_ms"]),
            "Local 8B guard model footprint proxy.",
        ),
    ]

    out_csv = DATA / "final_figure7_resource_comparison.csv"
    out_md = DATA / "final_figure7_resource_comparison.md"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Final Figure 7 Resource Comparison",
        "",
        "This table compares the defense overhead used in the final local reproduction. The shared qwen2.5 planner is not counted as WAMI defense memory; WAMI only counts its gateway model.",
        "",
        "| Defense | Runtime basis | Footprint kind | Footprint GiB | ToolBench latency ms | AgentBench latency ms | Notes |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['defense']} | {r['runtime_basis']} | {r['footprint_kind']} | "
            f"{r['footprint_gib']} | {r['toolbench_latency_ms']} | {r['agentbench_latency_ms']} | {r['notes']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- WAMI defense footprint is {mb_to_gb(wami_cuda['peak_reserved_mb']):.3f} GiB measured by CUDA peak reserved memory, while qwen2.5 judge baselines use about {qwen25_gib:.3f} GiB model-layer footprint.",
            f"- WAMI Table 4 defense latency is {float(toolbench['WAMI + qwen2.5 local agent']['latency_ms']):.1f} ms on ToolBench and {float(agentbench['WAMI + qwen2.5 local agent']['latency_ms']):.1f} ms on AgentBench.",
            "- For non-WAMI baselines, footprint is a local Ollama model-layer proxy. It is suitable for the paper's resource comparison trend, but not a strict live VRAM profiler.",
        ]
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out_md)
    print(out_csv)


if __name__ == "__main__":
    main()
