from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wami.model import WAMIModel
from wami.multimodal import MultimodalFusionConfig, MultimodalWAMIGateway, MultimodalWAMIModel


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CyberSecEval3 VPI with a selected non-API multimodal backend.")
    parser.add_argument("--data", default="data/cyberseceval3_vpi_wami.jsonl")
    parser.add_argument("--model", default="wami_injecagent_current_e3.npz")
    parser.add_argument("--backend", default="native")
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    rows = []
    with (ROOT / args.data).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
            if args.limit and len(rows) >= args.limit:
                break

    model = MultimodalWAMIModel(
        WAMIModel.load(str(ROOT / args.model)),
        MultimodalFusionConfig(backend=args.backend),
    )
    gateway = MultimodalWAMIGateway(model, base_threshold=-0.05, use_plan_mine=True)
    tp = fp = tn = fn = 0
    latencies = []
    details = []
    for idx, row in enumerate(rows, 1):
        image = ROOT / row["image"]
        start = time.perf_counter()
        decision = gateway.inspect_multimodal(row["intent"], row["plan"], image_paths=[image])
        elapsed = (time.perf_counter() - start) * 1000.0
        latencies.append(elapsed)
        pred = not decision.allowed
        actual = int(row["label"]) == 1
        if pred and actual:
            tp += 1
        elif pred and not actual:
            fp += 1
        elif not pred and actual:
            fn += 1
        else:
            tn += 1
        details.append(
            {
                "idx": idx,
                "id": row.get("id"),
                "label": row["label"],
                "blocked": pred,
                "score": decision.score,
                "reason": decision.reason,
                "latency_ms": elapsed,
            }
        )

    total = max(1, len(rows))
    ir = tp / max(1, tp + fn)
    fpr = fp / max(1, fp + tn)
    acc = (tp + tn) / total
    avg_latency = sum(latencies) / max(1, len(latencies))

    out_csv = ROOT / args.output_csv
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(details[0].keys()))
        writer.writeheader()
        writer.writerows(details)

    lines = [
        f"# CyberSecEval3 VPI Backend Ablation: {args.backend}",
        "",
        f"- Rows: {len(rows)}",
        f"- Backend: `{args.backend}`",
        f"- TP/FP/TN/FN: {tp}/{fp}/{tn}/{fn}",
        f"- IR: {ir:.3f}",
        f"- FPR: {fpr:.3f}",
        f"- ACC: {acc:.3f}",
        f"- Avg latency ms: {avg_latency:.3f}",
    ]
    (ROOT / args.output_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
