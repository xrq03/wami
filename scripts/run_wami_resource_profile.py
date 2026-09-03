from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import statistics
import sys
import time
import tracemalloc

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.datasets import load_plan_samples
from wami.gateway import WAMIGateway
from wami.model import WAMIModel


@dataclass
class ProfileRow:
    dataset: str
    data_path: str
    model_path: str
    samples_used: int
    model_size_mb: float
    load_time_ms: float
    eval_total_ms: float
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    python_peak_alloc_mb: float
    rss_before_mb: float
    rss_after_load_mb: float
    rss_after_eval_mb: float
    rss_delta_load_mb: float
    rss_delta_eval_mb: float
    ir: float
    fpr: float
    acc: float


DEFAULT_RUNS = [
    ("InjecAgent", "data/injecagent_wami.jsonl", "wami_injecagent_current_e3.npz"),
    ("BIPIA", "data/bipia_wami.jsonl", "wami_bipia_current_e3.npz"),
    ("AgentDojo", "data/agentdojo_wami.jsonl", "wami_agentdojo_current_e3.npz"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile WAMI runtime and resource overhead.")
    parser.add_argument("--limit", type=int, default=1000, help="Max samples per dataset; 0 means all.")
    parser.add_argument("--output-md", default="data/wami_resource_profile.md")
    parser.add_argument("--output-csv", default="data/wami_resource_profile.csv")
    args = parser.parse_args()

    rows = []
    for name, data_path, model_path in DEFAULT_RUNS:
        rows.append(profile_one(name, Path(data_path), Path(model_path), args.limit))

    write_outputs(rows, Path(args.output_md), Path(args.output_csv), args.limit)
    print(format_table(rows))
    print(f"saved markdown to {args.output_md}")
    print(f"saved csv to {args.output_csv}")


def profile_one(name: str, data_path: Path, model_path: Path, limit: int) -> ProfileRow:
    samples = load_plan_samples(data_path)
    if limit > 0:
        samples = samples[:limit]

    rss_before = current_rss_mb()
    tracemalloc.start()
    load_start = time.perf_counter()
    model = WAMIModel.load(str(model_path))
    gateway = WAMIGateway(
        model,
        base_threshold=-0.05,
        decay=0.02,
        use_action_prior=True,
        use_plan_mine=True,
        plan_threshold=-0.25,
        score_margin=0.05,
    )
    load_time_ms = (time.perf_counter() - load_start) * 1000.0
    rss_after_load = current_rss_mb()

    latencies = []
    tp = fp = tn = fn = 0
    eval_start = time.perf_counter()
    for sample in samples:
        start = time.perf_counter()
        decision = gateway.inspect(sample.intent, sample.plan)
        latencies.append((time.perf_counter() - start) * 1000.0)
        predicted_attack = not decision.allowed
        actual_attack = sample.label == 1
        if predicted_attack and actual_attack:
            tp += 1
        elif predicted_attack and not actual_attack:
            fp += 1
        elif not predicted_attack and actual_attack:
            fn += 1
        else:
            tn += 1
    eval_total_ms = (time.perf_counter() - eval_start) * 1000.0
    current_alloc, peak_alloc = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    rss_after_eval = current_rss_mb()

    total = max(1, tp + fp + tn + fn)
    attack_total = max(1, tp + fn)
    benign_total = max(1, fp + tn)
    return ProfileRow(
        dataset=name,
        data_path=str(data_path),
        model_path=str(model_path),
        samples_used=len(samples),
        model_size_mb=bytes_to_mb(model_path.stat().st_size),
        load_time_ms=load_time_ms,
        eval_total_ms=eval_total_ms,
        avg_latency_ms=statistics.fmean(latencies) if latencies else 0.0,
        p50_latency_ms=percentile(latencies, 50),
        p95_latency_ms=percentile(latencies, 95),
        python_peak_alloc_mb=bytes_to_mb(peak_alloc),
        rss_before_mb=rss_before,
        rss_after_load_mb=rss_after_load,
        rss_after_eval_mb=rss_after_eval,
        rss_delta_load_mb=rss_after_load - rss_before,
        rss_delta_eval_mb=rss_after_eval - rss_after_load,
        ir=tp / attack_total,
        fpr=fp / benign_total,
        acc=(tp + tn) / total,
    )


def current_rss_mb() -> float:
    if sys.platform.startswith("win"):
        return windows_working_set_mb()
    return 0.0


def windows_working_set_mb() -> float:
    import ctypes
    from ctypes import wintypes

    class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    counters = PROCESS_MEMORY_COUNTERS()
    counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    ok = ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb)
    if not ok:
        return 0.0
    return bytes_to_mb(counters.WorkingSetSize)


def percentile(values: list[float], pct: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = round((len(ordered) - 1) * pct / 100)
    return ordered[index]


def bytes_to_mb(value: int | float) -> float:
    return float(value) / (1024.0 * 1024.0)


def format_table(rows: list[ProfileRow]) -> str:
    lines = [
        "| Dataset | N | Model MB | Load ms | Avg ms | P50 ms | P95 ms | Peak alloc MB | RSS load delta MB | RSS eval delta MB | IR | FPR | ACC |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row.dataset} | {row.samples_used} | {row.model_size_mb:.3f} | "
            f"{row.load_time_ms:.3f} | {row.avg_latency_ms:.3f} | {row.p50_latency_ms:.3f} | "
            f"{row.p95_latency_ms:.3f} | {row.python_peak_alloc_mb:.3f} | "
            f"{row.rss_delta_load_mb:.3f} | {row.rss_delta_eval_mb:.3f} | "
            f"{row.ir * 100:.1f}% | {row.fpr * 100:.1f}% | {row.acc * 100:.1f}% |"
        )
    return "\n".join(lines)


def write_outputs(rows: list[ProfileRow], md_path: Path, csv_path: Path, limit: int) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    note = (
        "# WAMI Memory And Resource Profile\n\n"
        f"- Limit per dataset: `{limit if limit > 0 else 'all'}`\n"
        "- RSS is Windows process working set measured inside the same process.\n"
        "- Python peak allocation is measured by `tracemalloc` during model load and evaluation.\n\n"
    )
    md_path.write_text(note + format_table(rows) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ProfileRow.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
