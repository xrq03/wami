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
from wami.multimodal import MultimodalFusionConfig, MultimodalWAMIModel
from wami.paper_mine_gateway import PaperMINEConfig, PaperMultimodalMINEGateway


def main() -> None:
    parser = argparse.ArgumentParser(description="Paper-faithful multimodal MINE WAMI evaluation.")
    parser.add_argument("--data", default="data/cyberseceval3_vpi_wami.jsonl")
    parser.add_argument("--model", default="wami_injecagent_current_e3.npz")
    parser.add_argument("--backend", default="native")
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--tau", type=float, default=-1.85)
    parser.add_argument("--risk-margin", type=float, default=0.15)
    parser.add_argument("--passive-margin", type=float, default=0.10)
    parser.add_argument("--output-csv", default="data/paper_multimodal_mine_results.csv")
    parser.add_argument("--output-md", default="data/paper_multimodal_mine_results.md")
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
    gateway = PaperMultimodalMINEGateway(
        model,
        PaperMINEConfig(base_threshold=args.tau, plan_threshold=args.tau, risk_margin=args.risk_margin, passive_margin=args.passive_margin),
    )
    tp = fp = tn = fn = 0
    details = []
    for idx, row in enumerate(rows, 1):
        image = ROOT / row["image"]
        started = time.perf_counter()
        decision = gateway.inspect_multimodal(row["intent"], row["plan"], image_paths=[image])
        latency = (time.perf_counter() - started) * 1000.0
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
                "threshold": decision.threshold,
                "reason": decision.reason,
                "latency_ms": latency,
            }
        )

    total = max(1, len(rows))
    ir = tp / max(1, tp + fn)
    fpr = fp / max(1, fp + tn)
    acc = (tp + tn) / total
    avg_latency = sum(item["latency_ms"] for item in details) / max(1, len(details))

    out_csv = ROOT / args.output_csv
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(details[0].keys()))
        writer.writeheader()
        writer.writerows(details)

    lines = [
        "# Paper Multimodal MINE WAMI",
        "",
        f"- Rows: {len(rows)}",
        f"- Backend: `{args.backend}`",
        f"- Tau: `{args.tau}`",
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
