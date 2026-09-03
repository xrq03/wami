from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.evaluate import Metrics
from wami.gateway import ATTACK_TARGET_PATTERNS, INJECTION_ADOPTION_PATTERNS, WAMIGateway
from wami.tdg import build_tdg
from wami.training import load_jsonl


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
    level: str


class AgentDojoSpotlighting:
    """Dataset-level adaptation of AgentDojo's spotlighting_with_delimiting defense.

    In AgentDojo, spotlighting wraps tool outputs in delimiters and tells the
    agent never to follow instructions inside them. On our converted plan data,
    a sample is blocked when the proposed trajectory appears to obey delimited
    untrusted content or routes it into a high-risk side effect.
    """

    name = "AgentDojo spotlighting_with_delimiting"

    def inspect(self, intent: str, plan: str) -> bool:
        intent_lower = intent.lower()
        plan_lower = plan.lower()
        tdg = build_tdg(plan)
        seen_untrusted = False
        adopted_untrusted = any(pattern in plan_lower and pattern not in intent_lower for pattern in INJECTION_ADOPTION_PATTERNS)
        for node in tdg.nodes:
            tool_key = node.tool.lower()
            compact = tool_key.replace("_", "").replace("-", "")
            params = str(node.params).lower()
            if "readuntrustedinjection" in compact or "parseinjectedinstruction" in compact:
                seen_untrusted = True
                continue
            if seen_untrusted and WAMIGateway._requires_explicit_authorization(tool_key):
                return True
            if seen_untrusted and any(pattern in params for pattern in ATTACK_TARGET_PATTERNS):
                return True
            if adopted_untrusted and WAMIGateway._requires_explicit_authorization(tool_key):
                return True
        return False


def evaluate(defense: AgentDojoSpotlighting, samples) -> tuple[Metrics, float, int, int]:
    tp = fp = tn = fn = 0
    start = time.perf_counter()
    for sample in samples:
        blocked = defense.inspect(sample.intent, sample.plan)
        actual_attack = sample.label == 1
        if blocked and actual_attack:
            tp += 1
        elif blocked and not actual_attack:
            fp += 1
        elif not blocked and actual_attack:
            fn += 1
        else:
            tn += 1
    total = max(1, tp + fp + tn + fn)
    return Metrics(tp / max(1, tp + fn), fp / max(1, fp + tn), (tp + tn) / total, total), (time.perf_counter() - start) * 1000 / total, tp + fn, fp + tn


def pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--injecagent-data", default="data/injecagent_wami.jsonl")
    parser.add_argument("--bipia-data", default="data/bipia_wami.jsonl")
    parser.add_argument("--agentdojo-data", default="data/agentdojo_wami.jsonl")
    parser.add_argument("--output-csv", default="data/agentdojo_spotlighting_table1.csv")
    parser.add_argument("--output-md", default="data/agentdojo_spotlighting_table1.md")
    args = parser.parse_args()

    rows = []
    defense = AgentDojoSpotlighting()
    for dataset, path in [("BIPIA", args.bipia_data), ("InjecAgent", args.injecagent_data), ("AgentDojo", args.agentdojo_data)]:
        metrics, latency, attack_n, benign_n = evaluate(defense, load_jsonl(path))
        rows.append(
            Row(dataset, defense.name, metrics.interception_rate, metrics.false_positive_rate, metrics.accuracy, latency, metrics.total, attack_n, benign_n, "AgentDojo official defense idea adapted to converted trajectories")
        )
        print(f"{dataset}: IR={pct(metrics.interception_rate)} FPR={pct(metrics.false_positive_rate)} ACC={pct(metrics.accuracy)} latency={latency:.3f}ms N={metrics.total}")

    out_csv = Path(args.output_csv)
    out_md = Path(args.output_md)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)
    lines = [
        "# AgentDojo spotlighting Table 1 replacement",
        "",
        "This replaces BookAgent with AgentDojo's open-source `spotlighting_with_delimiting` defense idea. It is adapted to the local converted trajectory format rather than run inside the full AgentDojo agent harness.",
        "",
        "| Dataset | Method | IR | FPR | ACC | Latency ms | N | Attack | Benign | Level |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.dataset} | {row.method} | {pct(row.ir)} | {pct(row.fpr)} | {pct(row.acc)} | "
            f"{row.latency_ms:.3f} | {row.total} | {row.attack_n} | {row.benign_n} | {row.level} |"
        )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out_csv}")
    print(f"wrote {out_md}")


if __name__ == "__main__":
    main()
