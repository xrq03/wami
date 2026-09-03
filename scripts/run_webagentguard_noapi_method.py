from __future__ import annotations

import argparse
import csv
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from wami.gateway import ATTACK_TARGET_PATTERNS, INJECTION_ADOPTION_PATTERNS, WAMIGateway  # noqa: E402
from wami.tdg import build_tdg  # noqa: E402
from wami.training import load_jsonl  # noqa: E402


@dataclass
class Row:
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="No-API method-level WebAgentGuard baseline on WAMI-format datasets."
    )
    parser.add_argument("--injecagent-data", default="data/injecagent_wami.jsonl")
    parser.add_argument("--bipia-data", default="data/bipia_wami.jsonl")
    parser.add_argument("--agentdojo-data", default="data/agentdojo_wami.jsonl")
    parser.add_argument("--output-md", default="data/webagentguard_noapi_method_full.md")
    parser.add_argument("--output-csv", default="data/webagentguard_noapi_method_full.csv")
    args = parser.parse_args()

    rows = []
    for dataset, path in [
        ("BIPIA", args.bipia_data),
        ("InjecAgent", args.injecagent_data),
        ("AgentDojo", args.agentdojo_data),
    ]:
        rows.append(evaluate(dataset, load_jsonl(resolve(path))))

    write_outputs(rows, ROOT / args.output_md, ROOT / args.output_csv)
    print(format_table(rows))
    print(f"saved markdown to {args.output_md}")
    print(f"saved csv to {args.output_csv}")


def resolve(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def evaluate(dataset: str, samples) -> Row:
    tp = fp = tn = fn = 0
    started = time.perf_counter()
    for sample in samples:
        blocked = webagentguard_noapi_block(sample.intent, sample.plan)
        actual = sample.label == 1
        if blocked and actual:
            tp += 1
        elif blocked and not actual:
            fp += 1
        elif not blocked and actual:
            fn += 1
        else:
            tn += 1
    total = max(1, tp + fp + tn + fn)
    attack_n = tp + fn
    benign_n = fp + tn
    return Row(
        dataset=dataset,
        method="WebAgentGuard no-API method-level",
        ir=tp / max(1, attack_n),
        fpr=fp / max(1, benign_n),
        acc=(tp + tn) / total,
        latency_ms=(time.perf_counter() - started) * 1000.0 / total,
        total=total,
        attack_n=attack_n,
        benign_n=benign_n,
        status="method-level-noapi",
        note=(
            "No official WebAgentGuard checkpoint/code was available. This reproduces the paper-level "
            "parallel pre-execution trajectory guard idea without an LLM API; do not report it as official."
        ),
    )


def webagentguard_noapi_block(intent: str, plan: str) -> bool:
    intent_lower = intent.lower()
    plan_lower = plan.lower()
    tdg = build_tdg(plan)

    if any(pattern in plan_lower and pattern not in intent_lower for pattern in INJECTION_ADOPTION_PATTERNS):
        return True

    seen_untrusted = False
    for node in tdg.nodes:
        tool_key = node.tool.lower()
        compact_tool = tool_key.replace("_", "").replace("-", "")
        params_lower = str(node.params).lower()

        if any(marker in compact_tool for marker in ("readtoolresponse", "readuntrustedinjection", "parseinjectedinstruction")):
            seen_untrusted = True

        if any(pattern in params_lower for pattern in ATTACK_TARGET_PATTERNS):
            return True

        if WAMIGateway._requires_explicit_authorization(tool_key):
            terms = WAMIGateway._sensitive_terms(tool_key)
            if seen_untrusted:
                return True
            if terms and not WAMIGateway._explicitly_authorizes(intent_lower, terms):
                return True

        if seen_untrusted and any(word in tool_key for word in ("send", "post", "write", "update", "delete", "transfer", "share")):
            return True

    return False


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_table(rows: list[Row]) -> str:
    lines = [
        "# WebAgentGuard No-API Method-Level Baseline",
        "",
        "This is a no-API method-level reproduction of WebAgentGuard's parallel pre-execution guard idea. It is not an official checkpoint reproduction.",
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
            "## Strictness",
            "",
            "- This row is useful as a no-API baseline for Table 1 development.",
            "- It should remain marked as method-level unless official WebAgentGuard weights/runtime are provided.",
        ]
    )
    return "\n".join(lines)


def write_outputs(rows: list[Row], md_path: Path, csv_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(format_table(rows) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
