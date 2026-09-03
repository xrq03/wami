from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import statistics
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.datasets import load_plan_samples
from wami.gateway import WAMIGateway
from wami.tdg import build_tdg
from wami.torch_model import TorchWAMIModel


@dataclass
class LatencyRow:
    samples: int
    tdg_ms: float
    world_ms: float
    mine_ms: float
    total_ms: float


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/injecagent_wami.jsonl")
    parser.add_argument("--model", default="wami_paper_strict_injecagent_e20.pt")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--output-md", default="data/wami_paper_latency_breakdown.md")
    parser.add_argument("--output-csv", default="data/wami_paper_latency_breakdown.csv")
    args = parser.parse_args()

    samples = load_plan_samples(args.data)[: args.limit]
    model = TorchWAMIModel.load(args.model)
    gateway = WAMIGateway(model, base_threshold=0.15, use_plan_mine=True, plan_threshold=0.15)
    tdg_times = []
    world_times = []
    mine_times = []
    total_times = []
    for sample in samples:
        start_total = time.perf_counter()
        start = time.perf_counter()
        tdg = build_tdg(sample.plan)
        tdg_times.append((time.perf_counter() - start) * 1000.0)
        start = time.perf_counter()
        trace = model.rollout(sample.intent, tdg)
        world_times.append((time.perf_counter() - start) * 1000.0)
        start = time.perf_counter()
        intent_vec = model.encode_intent(sample.intent)
        for _, state in trace:
            model.mine_score(intent_vec, state)
        mine_times.append((time.perf_counter() - start) * 1000.0)
        gateway.inspect(sample.intent, sample.plan)
        total_times.append((time.perf_counter() - start_total) * 1000.0)
    row = LatencyRow(
        samples=len(samples),
        tdg_ms=statistics.fmean(tdg_times),
        world_ms=statistics.fmean(world_times),
        mine_ms=statistics.fmean(mine_times),
        total_ms=statistics.fmean(total_times),
    )
    write_outputs(row, Path(args.output_md), Path(args.output_csv))
    print(f"TDG={row.tdg_ms:.3f}ms World={row.world_ms:.3f}ms MINE={row.mine_ms:.3f}ms Total={row.total_ms:.3f}ms")


def write_outputs(row: LatencyRow, md_path: Path, csv_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "# WAMI Paper-Style Latency Breakdown\n\n"
        "| Samples | TDG ms | World ms | MINE ms | Total ms |\n"
        "|---:|---:|---:|---:|---:|\n"
        f"| {row.samples} | {row.tdg_ms:.3f} | {row.world_ms:.3f} | {row.mine_ms:.3f} | {row.total_ms:.3f} |\n",
        encoding="utf-8",
    )
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(LatencyRow.__dataclass_fields__.keys()))
        writer.writeheader()
        writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
