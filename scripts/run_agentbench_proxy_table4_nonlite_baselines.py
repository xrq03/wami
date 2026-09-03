from __future__ import annotations

import argparse
import csv
import sys
import time
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_toolbench_table4_nonlite_baselines import (
    LlamaGuard3Ollama,
    NoDefense,
    QwenEraseAndCheck,
    QwenToolEmuSandbox,
    OllamaChatClient,
    WAMIDefense,
    pct,
)
from wami.datasets import load_plan_samples


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class InputRow:
    index: int
    intent: str
    plan: str
    no_defense_success_proxy: bool


@dataclass
class Summary:
    method: str
    total: int
    no_defense_success: int
    preserved_success: int
    blocked: int
    agentbench_sr: float
    agentbench_retention: float
    latency_ms: float


@dataclass
class Detail:
    method: str
    index: int
    no_defense_success_proxy: bool
    allowed: bool
    reason: str
    latency_ms: float


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-csv", default="data/qwen25_7b_ollama_boost_agentdojo_full.csv")
    parser.add_argument("--data", default="data/agentdojo_wami.jsonl")
    parser.add_argument("--limit", type=int, default=86)
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--judge-model", default="qwen2.5:7b-instruct")
    parser.add_argument("--llamaguard-model", default="llama-guard3:8b")
    parser.add_argument("--wami-model", default="wami_injecagent_final_e5.npz")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--output-prefix", default="data/agentbench_proxy_table4_nonlite_qwen25")
    args = parser.parse_args()

    rows = load_inputs(ROOT / args.live_csv, ROOT / args.data, args.limit)
    client = OllamaChatClient(args.judge_model, args.ollama_url, args.timeout)
    defenses = [
        NoDefense(),
        QwenEraseAndCheck(client),
        QwenToolEmuSandbox(client),
        LlamaGuard3Ollama(args.ollama_url, args.llamaguard_model, args.timeout),
        WAMIDefense(args.wami_model),
    ]

    no_defense_sr = sum(row.no_defense_success_proxy for row in rows) / max(1, len(rows))
    summaries: list[Summary] = []
    details: list[Detail] = []
    for defense in defenses:
        summary, method_details = evaluate(defense, rows, no_defense_sr)
        summaries.append(summary)
        details.extend(method_details)
        print(
            f"{summary.method}: AgentBenchSR={summary.agentbench_sr:.3f} "
            f"retention={summary.agentbench_retention:.3f} blocked={summary.blocked}/{summary.total} "
            f"latency={summary.latency_ms:.1f}ms",
            flush=True,
        )
    write_outputs(ROOT / args.output_prefix, summaries, details, args)


def load_inputs(live_csv: Path, data_path: Path, limit: int) -> list[InputRow]:
    samples = load_plan_samples(data_path)
    out: list[InputRow] = []
    with live_csv.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["label"] != "0":
                continue
            index = int(row["index"])
            sample = samples[index]
            blocked = row["blocked"].lower() == "true"
            has_activity = int(row["executed_steps"]) > 0 or row["planner_finished"].lower() == "true"
            out.append(
                InputRow(
                    index=index,
                    intent=sample.intent,
                    plan=row["trace_plan"] or sample.plan,
                    no_defense_success_proxy=has_activity and not blocked,
                )
            )
            if len(out) >= limit:
                break
    return out


def evaluate(defense, rows: list[InputRow], no_defense_sr: float) -> tuple[Summary, list[Detail]]:
    preserved = blocked = 0
    no_defense_success = sum(row.no_defense_success_proxy for row in rows)
    total_latency = 0.0
    details: list[Detail] = []
    for row in rows:
        started = time.perf_counter()
        allowed, reason = defense.inspect(row.intent, row.plan)
        latency_ms = (time.perf_counter() - started) * 1000.0
        total_latency += latency_ms
        if not allowed:
            blocked += 1
        if row.no_defense_success_proxy and allowed:
            preserved += 1
        details.append(
            Detail(
                method=defense.name,
                index=row.index,
                no_defense_success_proxy=row.no_defense_success_proxy,
                allowed=allowed,
                reason=reason,
                latency_ms=latency_ms,
            )
        )
    total = len(rows)
    sr = preserved / max(1, total)
    return (
        Summary(
            method=defense.name,
            total=total,
            no_defense_success=no_defense_success,
            preserved_success=preserved,
            blocked=blocked,
            agentbench_sr=sr,
            agentbench_retention=sr / max(1e-9, no_defense_sr),
            latency_ms=total_latency / max(1, total),
        ),
        details,
    )


def write_outputs(prefix: Path, summaries: list[Summary], details: list[Detail], args: argparse.Namespace) -> None:
    prefix.parent.mkdir(parents=True, exist_ok=True)
    summary_csv = prefix.with_name(prefix.name + "_summary.csv")
    details_csv = prefix.with_name(prefix.name + "_details.csv")
    md_path = prefix.with_name(prefix.name + "_summary.md")
    with summary_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Summary.__dataclass_fields__.keys()))
        writer.writeheader()
        writer.writerows([row.__dict__ for row in summaries])
    with details_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Detail.__dataclass_fields__.keys()))
        writer.writeheader()
        writer.writerows([row.__dict__ for row in details])
    lines = [
        "# AgentBench-style Non-Lite qwen2.5 Baselines",
        "",
        "This is an AgentBench-style proxy using the full qwen2.5 live AgentDojo benign traces. No `Lite` baselines are used.",
        "",
        f"- Input live traces: `{args.live_csv}`",
        f"- Judge model: `{args.judge_model}`",
        "",
        "| Method | N | No-Defense Success | Preserved Success | AgentBench SR | AgentBench Retention | Blocked | Latency ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            f"| {row.method} | {row.total} | {row.no_defense_success} | {row.preserved_success} | "
            f"{pct(row.agentbench_sr)} | {pct(row.agentbench_retention)} | {row.blocked} | {row.latency_ms:.1f} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
