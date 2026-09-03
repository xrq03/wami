from __future__ import annotations

import argparse
import csv
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from wami.gateway import GateDecision, WAMIGateway  # noqa: E402
from wami.model import WAMIModel  # noqa: E402
from wami.tdg import build_tdg  # noqa: E402
from wami.training import load_jsonl  # noqa: E402


@dataclass
class SummaryRow:
    dataset: str
    method: str
    ir: float
    fpr: float
    acc: float
    latency_ms: float
    total: int
    attack_n: int
    benign_n: int
    status: str
    note: str


@dataclass
class TraceRow:
    dataset: str
    index: int
    label: int
    blocked: bool
    blocked_step: int | None
    blocked_tool: str | None
    score: float
    threshold: float
    reason: str
    latency_ms: float


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replay WAMI as an action-level runtime gateway over stored agent trajectories."
    )
    parser.add_argument("--injecagent-data", default="data/injecagent_wami.jsonl")
    parser.add_argument("--bipia-data", default="data/bipia_wami.jsonl")
    parser.add_argument("--agentdojo-data", default="data/agentdojo_wami.jsonl")
    parser.add_argument("--injecagent-model", default="wami_injecagent_current_e3.npz")
    parser.add_argument("--bipia-model", default="wami_bipia_current_e3.npz")
    parser.add_argument("--agentdojo-model", default="wami_agentdojo_current_e3.npz")
    parser.add_argument("--threshold", type=float, default=-0.05)
    parser.add_argument("--use-action-prior", action="store_true")
    parser.add_argument("--output-md", default="data/wami_runtime_replay_results.md")
    parser.add_argument("--output-csv", default="data/wami_runtime_replay_results.csv")
    parser.add_argument("--trace-csv", default="data/wami_runtime_replay_traces.csv")
    args = parser.parse_args()

    configs = [
        ("BIPIA", args.bipia_data, args.bipia_model),
        ("InjecAgent", args.injecagent_data, args.injecagent_model),
        ("AgentDojo", args.agentdojo_data, args.agentdojo_model),
    ]

    summaries: list[SummaryRow] = []
    traces: list[TraceRow] = []
    for dataset, data_path, model_path in configs:
        gateway = WAMIGateway(
            WAMIModel.load(resolve(model_path)),
            base_threshold=args.threshold,
            use_action_prior=args.use_action_prior,
            use_plan_mine=False,
        )
        summary, rows = evaluate_dataset(dataset, load_jsonl(resolve(data_path)), gateway)
        summaries.append(summary)
        traces.extend(rows)

    write_outputs(summaries, traces, ROOT / args.output_md, ROOT / args.output_csv, ROOT / args.trace_csv)
    print(format_table(summaries))
    print(f"saved markdown to {args.output_md}")
    print(f"saved csv to {args.output_csv}")
    print(f"saved traces to {args.trace_csv}")


def resolve(path_text: str | Path) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def evaluate_dataset(dataset: str, samples, gateway: WAMIGateway) -> tuple[SummaryRow, list[TraceRow]]:
    tp = fp = tn = fn = 0
    traces: list[TraceRow] = []
    started = time.perf_counter()
    for index, sample in enumerate(samples):
        t0 = time.perf_counter()
        decision = replay_sample(sample.intent, sample.plan, gateway)
        latency_ms = (time.perf_counter() - t0) * 1000.0
        blocked = not decision.allowed
        actual = sample.label == 1
        if blocked and actual:
            tp += 1
        elif blocked and not actual:
            fp += 1
        elif not blocked and actual:
            fn += 1
        else:
            tn += 1
        traces.append(
            TraceRow(
                dataset=dataset,
                index=index,
                label=sample.label,
                blocked=blocked,
                blocked_step=decision.step,
                blocked_tool=decision.tool,
                score=decision.score,
                threshold=decision.threshold,
                reason=decision.reason,
                latency_ms=latency_ms,
            )
        )
    total = max(1, tp + fp + tn + fn)
    attack_n = tp + fn
    benign_n = fp + tn
    summary = SummaryRow(
        dataset=dataset,
        method="WAMI runtime action replay",
        ir=tp / max(1, attack_n),
        fpr=fp / max(1, benign_n),
        acc=(tp + tn) / total,
        latency_ms=(time.perf_counter() - started) * 1000.0 / total,
        total=total,
        attack_n=attack_n,
        benign_n=benign_n,
        status="runtime-replay-action-level",
        note="Read/search/observation steps are replayed first; WAMI is applied before non-observation action transitions.",
    )
    return summary, traces


def replay_sample(intent: str, plan: str, gateway: WAMIGateway) -> GateDecision:
    tdg = build_tdg(plan)
    if not tdg.nodes:
        return GateDecision(True, None, None, 0.0, gateway.threshold(0), "no tool calls found")

    prefix_lines: list[str] = []
    last_decision = GateDecision(True, None, None, 0.0, gateway.threshold(0), "trajectory remained aligned")
    for node in tdg.topological_order():
        prefix_lines.append(node.raw)
        if gateway._is_passive_observation(node.tool.lower()):
            continue
        prefix_plan = "\n".join(prefix_lines)
        decision = gateway.inspect(intent, prefix_plan)
        last_decision = decision
        if not decision.allowed:
            return decision
    return last_decision


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_table(rows: list[SummaryRow]) -> str:
    lines = [
        "# WAMI Runtime Action Replay",
        "",
        "This replay evaluates WAMI as an action-level runtime gateway instead of an input-level prompt filter.",
        "",
        "| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | Status |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.dataset} | {row.method} | {pct(row.ir)} | {pct(row.fpr)} | {pct(row.acc)} | "
            f"{row.latency_ms:.3f} | {row.total} | {row.attack_n} | {row.benign_n} | {row.status} |"
        )
    lines.extend(
        [
            "",
            "## Protocol",
            "",
            "- Observation/read/search steps are allowed so prompt injection can enter the agent context.",
            "- WAMI is invoked only before later non-observation actions in the replayed trajectory.",
            "- This shows whether WAMI can block unsafe action transitions after untrusted content has already been observed.",
        ]
    )
    return "\n".join(lines)


def write_outputs(
    summaries: list[SummaryRow],
    traces: list[TraceRow],
    md_path: Path,
    csv_path: Path,
    trace_path: Path,
) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(format_table(summaries) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(SummaryRow.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in summaries:
            writer.writerow(row.__dict__)
    with trace_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(TraceRow.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in traces:
            writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
