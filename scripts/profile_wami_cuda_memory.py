from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from wami.datasets import load_plan_samples  # noqa: E402
from wami.gateway import WAMIGateway  # noqa: E402
from wami.torch_model import TorchWAMIModel  # noqa: E402


@dataclass
class MemoryRow:
    method: str
    model: str
    device: str
    samples: int
    allocated_mb: float
    reserved_mb: float
    peak_allocated_mb: float
    peak_reserved_mb: float


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure CUDA memory for WAMI inference.")
    parser.add_argument("--data", default="data/injecagent_wami.jsonl")
    parser.add_argument("--model", default="wami_paper_strict_injecagent_512_e5_cuda.pt")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--output-md", default="data/wami_cuda_memory_profile.md")
    parser.add_argument("--output-csv", default="data/wami_cuda_memory_profile.csv")
    args = parser.parse_args()

    model = TorchWAMIModel.load(args.model)
    torch = model.torch
    if not torch.cuda.is_available() or not str(model.config.device).startswith("cuda"):
        raise SystemExit("CUDA model/device is required for this profiler.")

    samples = load_plan_samples(args.data)[: args.limit]
    gateway = WAMIGateway(model, base_threshold=0.15, use_plan_mine=True, plan_threshold=0.15)

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    for sample in samples:
        gateway.inspect(sample.intent, sample.plan)
    torch.cuda.synchronize()

    row = MemoryRow(
        method="WAMI paper-strict torch inference",
        model=args.model,
        device=torch.cuda.get_device_name(0),
        samples=len(samples),
        allocated_mb=torch.cuda.memory_allocated() / 1024 / 1024,
        reserved_mb=torch.cuda.memory_reserved() / 1024 / 1024,
        peak_allocated_mb=torch.cuda.max_memory_allocated() / 1024 / 1024,
        peak_reserved_mb=torch.cuda.max_memory_reserved() / 1024 / 1024,
    )
    write_outputs(row, ROOT / args.output_md, ROOT / args.output_csv)
    print(
        f"allocated={row.allocated_mb:.1f}MB reserved={row.reserved_mb:.1f}MB "
        f"peak_allocated={row.peak_allocated_mb:.1f}MB peak_reserved={row.peak_reserved_mb:.1f}MB"
    )


def write_outputs(row: MemoryRow, md_path: Path, csv_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "# WAMI CUDA Memory Profile\n\n"
        "| Method | Model | Device | Samples | Allocated MB | Reserved MB | Peak Allocated MB | Peak Reserved MB |\n"
        "|---|---|---|---:|---:|---:|---:|---:|\n"
        f"| {row.method} | `{row.model}` | {row.device} | {row.samples} | "
        f"{row.allocated_mb:.1f} | {row.reserved_mb:.1f} | {row.peak_allocated_mb:.1f} | {row.peak_reserved_mb:.1f} |\n",
        encoding="utf-8",
    )
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(MemoryRow.__dataclass_fields__.keys()))
        writer.writeheader()
        writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
