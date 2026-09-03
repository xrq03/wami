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


def load_rows(path: Path, limit: int) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows.append(json.loads(line))
            if limit and len(rows) >= limit:
                break
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate WAMI + Qwen-VL on CyberSecEval3 VPI WAMI JSONL.")
    parser.add_argument("--data", default="data/cyberseceval3_vpi_wami.jsonl")
    parser.add_argument("--model", default="wami_injecagent_final_e5.npz")
    parser.add_argument("--vision-model", default="qwen-vl-max")
    parser.add_argument("--llm-config", default="config/llm_agent.local.json")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--out-csv", default="data/cyberseceval3_vpi_qwenvl_results.csv")
    parser.add_argument("--out-md", default="data/cyberseceval3_vpi_qwenvl_results.md")
    args = parser.parse_args()

    rows = load_rows(ROOT / args.data, args.limit)
    base = WAMIModel.load(str(ROOT / args.model))
    fusion = MultimodalFusionConfig(
        backend="qwen-vl",
        vision_model=args.vision_model,
        llm_config_path=args.llm_config,
        image_weight=0.35,
        action_image_weight=0.15,
    )
    mm_model = MultimodalWAMIModel(base, fusion)
    gateway = MultimodalWAMIGateway(mm_model, base_threshold=-0.05, use_plan_mine=True)

    print("=== CyberSecEval3 VPI WAMI + Qwen-VL ===")
    print(f"data={args.data}")
    print(f"rows={len(rows)}")
    print(f"vision_model={args.vision_model}")
    print()

    tp = fp = tn = fn = 0
    latencies: list[float] = []
    result_rows: list[dict] = []
    for index, row in enumerate(rows, 1):
        image = ROOT / row["image"]
        started = time.perf_counter()
        decision = gateway.inspect_multimodal(row["intent"], row["plan"], image_paths=[image])
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        latencies.append(elapsed_ms)
        predicted_attack = not decision.allowed
        actual_attack = int(row["label"]) == 1
        if predicted_attack and actual_attack:
            tp += 1
        elif predicted_attack and not actual_attack:
            fp += 1
        elif not predicted_attack and actual_attack:
            fn += 1
        else:
            tn += 1
        visual = getattr(mm_model.image_encoder, "last_caption", "").replace("\n", " ")
        if len(visual) > 160:
            visual = visual[:157] + "..."
        result_rows.append(
            {
                "index": index,
                "id": row.get("id"),
                "label": row["label"],
                "blocked": predicted_attack,
                "score": decision.score,
                "threshold": decision.threshold,
                "latency_ms": elapsed_ms,
                "reason": decision.reason,
                "injection_type": row.get("injection_type"),
                "risk_category": row.get("risk_category"),
                "attack_kind": row.get("attack_kind"),
                "visual": visual,
            }
        )
        print(
            f"{index:03d} id={row.get('id')} label={row['label']} blocked={predicted_attack} "
            f"score={decision.score:+.4f} latency_ms={elapsed_ms:.1f} "
            f"type={row.get('injection_type')} risk={row.get('risk_category')}"
        )
        print(f"    reason={decision.reason}")
        print(f"    visual={visual}")

    total = max(1, len(rows))
    print()
    print("[summary]")
    print(f"TP={tp} FP={fp} TN={tn} FN={fn}")
    print(f"IR={tp / max(1, tp + fn):.3f}")
    print(f"FPR={fp / max(1, fp + tn):.3f}")
    print(f"ACC={(tp + tn) / total:.3f}")
    print(f"avg_latency_ms={sum(latencies) / max(1, len(latencies)):.1f}")

    out_csv = ROOT / args.out_csv
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result_rows[0].keys()) if result_rows else [])
        if result_rows:
            writer.writeheader()
            writer.writerows(result_rows)

    ir = tp / max(1, tp + fn)
    fpr = fp / max(1, fp + tn)
    acc = (tp + tn) / total
    avg_latency = sum(latencies) / max(1, len(latencies))
    out_md = ROOT / args.out_md
    out_md.write_text(
        "\n".join(
            [
                "# CyberSecEval3 VPI WAMI + Qwen-VL Results",
                "",
                f"- Data: `{args.data}`",
                f"- Rows: {len(rows)}",
                f"- Vision model: `{args.vision_model}`",
                f"- TP/FP/TN/FN: {tp}/{fp}/{tn}/{fn}",
                f"- IR: {ir:.3f}",
                f"- FPR: {fpr:.3f}",
                f"- ACC: {acc:.3f}",
                f"- Avg latency ms: {avg_latency:.1f}",
                "",
                "| idx | id | label | blocked | score | latency_ms | risk | attack_kind | reason |",
                "|---:|---:|---:|---:|---:|---:|---|---|---|",
                *[
                    "| {index} | {id} | {label} | {blocked} | {score:.4f} | {latency_ms:.1f} | {risk_category} | {attack_kind} | {reason} |".format(
                        **item
                    )
                    for item in result_rows
                ],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"saved_csv={out_csv}")
    print(f"saved_md={out_md}")


if __name__ == "__main__":
    main()
