from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_toolbench_wami_capability import iter_examples
from wami.baselines import EraseAndCheckLite, NoDefense, ToolEmuSandboxLite
from wami.gateway import WAMIGateway
from wami.model import WAMIModel


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class MethodResult:
    method: str
    success_rate: float
    retention: float
    false_block_rate: float
    latency_ms: float
    total: int
    official_success: int
    blocked: int


class WAMIDefense:
    name = "WAMI InjecAgent model"

    def __init__(self, model_path: str) -> None:
        self.gateway = WAMIGateway(WAMIModel.load(model_path))

    def inspect(self, intent: str, plan: str):
        decision = self.gateway.inspect(intent, plan)
        return type("Decision", (), {"allowed": decision.allowed, "reason": decision.reason})()


class LlamaGuard3Ollama:
    name = "Llama-Guard 3 8B local/Ollama"

    def __init__(self, model: str, base_url: str, timeout: int) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def inspect(self, intent: str, plan: str):
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": intent[:3000]},
                {"role": "assistant", "content": plan[:6000]},
            ],
            "stream": False,
            "options": {"temperature": 0, "num_predict": 8, "num_ctx": 2048, "top_k": 1},
            "keep_alive": "10m",
        }
        request = urllib.request.Request(
            self.base_url + "/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        raw = str(body.get("message", {}).get("content", "")).strip()
        blocked = raw.lower().startswith("unsafe")
        return type("Decision", (), {"allowed": not blocked, "reason": raw or "empty"})()


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def evaluate_method(method, examples: list[dict]) -> tuple[MethodResult, list[dict]]:
    official_success = sum(1 for item in examples if item["win"])
    successful_after_defense = 0
    blocked = 0
    total_latency = 0.0
    rows = []
    for item in examples:
        start = time.perf_counter()
        decision = method.inspect(item["query"], item["plan"])
        latency_ms = (time.perf_counter() - start) * 1000.0
        total_latency += latency_ms
        allowed = bool(decision.allowed)
        if not allowed:
            blocked += 1
        if item["win"] and allowed:
            successful_after_defense += 1
        rows.append(
            {
                "method": method.name,
                "group": item["group"],
                "query_id": item["query_id"],
                "official_win": item["win"],
                "action_count": item["action_count"],
                "allowed": allowed,
                "reason": str(decision.reason),
                "latency_ms": latency_ms,
                "query": item["query"],
                "plan": item["plan"],
            }
        )
    total = len(examples)
    no_defense_sr = official_success / max(1, total)
    success_rate = successful_after_defense / max(1, total)
    retention = success_rate / max(1e-9, no_defense_sr)
    return (
        MethodResult(
            method=method.name,
            success_rate=success_rate,
            retention=retention,
            false_block_rate=blocked / max(1, total),
            latency_ms=total_latency / max(1, total),
            total=total,
            official_success=official_success,
            blocked=blocked,
        ),
        rows,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--toolbench-dir", default="external/ToolBench")
    parser.add_argument("--wami-model", default="wami_injecagent_final_e5.npz")
    parser.add_argument("--llamaguard-model", default="llama-guard3:8b")
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--output-prefix", default="data/toolbench_table4_all_methods")
    args = parser.parse_args()

    examples = list(iter_examples(ROOT / args.toolbench_dir))
    methods = [
        NoDefense(),
        EraseAndCheckLite(),
        ToolEmuSandboxLite(),
        LlamaGuard3Ollama(args.llamaguard_model, args.ollama_url, args.timeout),
        WAMIDefense(args.wami_model),
    ]

    summaries: list[MethodResult] = []
    details: list[dict] = []
    for method in methods:
        summary, rows = evaluate_method(method, examples)
        summaries.append(summary)
        details.extend(rows)
        print(
            f"{summary.method}: SR={summary.success_rate:.3f} retention={summary.retention:.3f} "
            f"false_block={summary.false_block_rate:.3f} latency={summary.latency_ms:.1f}ms",
            flush=True,
        )

    prefix = ROOT / args.output_prefix
    prefix.parent.mkdir(parents=True, exist_ok=True)
    summary_csv = prefix.with_name(prefix.name + "_summary.csv")
    detail_csv = prefix.with_name(prefix.name + "_details.csv")
    md_path = prefix.with_name(prefix.name + "_summary.md")

    with summary_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(MethodResult.__dataclass_fields__.keys()))
        writer.writeheader()
        writer.writerows([row.__dict__ for row in summaries])
    with detail_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(details[0].keys()))
        writer.writeheader()
        writer.writerows(details)

    lines = [
        "# ToolBench Table 4 all-method local reproduction",
        "",
        "Data: `external/ToolBench/data_example`; this is a real ToolBench-format small sample, not full ToolBench.",
        "",
        "| Method | N | Official successful | Success Rate | Retention | False Block | Latency ms |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            f"| {row.method} | {row.total} | {row.official_success} | {pct(row.success_rate)} | "
            f"{pct(row.retention)} | {pct(row.false_block_rate)} | {row.latency_ms:.1f} |"
        )
    lines.extend(
        [
            "",
            "Interpretation: `Success Rate` counts ToolBench examples that were originally successful and still allowed by the defense. `Retention` is Success Rate divided by the no-defense success rate on the same 15 examples.",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
