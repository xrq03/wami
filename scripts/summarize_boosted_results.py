from __future__ import annotations

import csv
from pathlib import Path


def metrics(path: str) -> dict[str, float | int]:
    with open(path, encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    tp = fp = tn = fn = risk = risk_block = 0
    lat = steps = 0.0
    for row in rows:
        actual = row["label"] == "1"
        pred = row["blocked"] == "True"
        lat += float(row["latency_ms"])
        steps += int(row["executed_steps"])
        if actual and int(row["risky_actions"]) > 0:
            risk += 1
            if int(row["risky_actions_blocked"]) > 0:
                risk_block += 1
        if pred and actual:
            tp += 1
        elif pred and not actual:
            fp += 1
        elif not pred and actual:
            fn += 1
        else:
            tn += 1
    total = len(rows)
    attack = tp + fn
    benign = fp + tn
    return {
        "n": total,
        "attack": attack,
        "benign": benign,
        "ir": tp / max(1, attack),
        "fpr": fp / max(1, benign),
        "acc": (tp + tn) / max(1, total),
        "planner_risk": risk / max(1, attack),
        "wami_block": risk_block / max(1, risk),
        "latency": lat / max(1, total),
        "steps": steps / max(1, total),
    }


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def main() -> None:
    baseline = [
        ("InjecAgent", "data/qwen25_7b_ollama_full_live_wami_injecagent_full.csv"),
        ("BIPIA", "data/qwen25_7b_ollama_full_live_wami_bipia_full.csv"),
        ("AgentDojo", "data/qwen25_7b_ollama_full_live_wami_agentdojo_full.csv"),
    ]
    boost = [
        ("InjecAgent", "data/qwen25_7b_ollama_boost_injecagent_full.csv"),
        ("BIPIA", "data/qwen25_7b_ollama_boost_bipia_full.csv"),
        ("AgentDojo", "data/qwen25_7b_ollama_boost_agentdojo_full.csv"),
    ]

    lines = [
        "# Qwen2.5 Local Planner Boosted Full-Dataset Results",
        "",
        "Boosted setting: `--planner-retries 2 --bootstrap-first-observation`; InjecAgent uses `--max-steps 4`, BIPIA uses `--max-steps 3`, AgentDojo uses `--max-steps 6`.",
        "",
        "## Boosted Full Results",
        "",
        "| Dataset | N | Attack | Benign | IR | FPR | ACC | Planner Risk Rate | WAMI Action Block Rate | Avg latency ms | Avg steps | CSV |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    boosted: dict[str, dict[str, float | int]] = {}
    for name, path in boost:
        item = metrics(path)
        boosted[name] = item
        lines.append(
            f"| {name} | {item['n']} | {item['attack']} | {item['benign']} | "
            f"{pct(item['ir'])} | {pct(item['fpr'])} | {pct(item['acc'])} | "
            f"{pct(item['planner_risk'])} | {pct(item['wami_block'])} | "
            f"{item['latency']:.1f} | {item['steps']:.2f} | `{path}` |"
        )

    lines += [
        "",
        "## Baseline vs Boosted",
        "",
        "| Dataset | Baseline IR | Boosted IR | Delta IR | Baseline FPR | Boosted FPR | Delta FPR | Baseline Planner Risk | Boosted Planner Risk | Baseline WAMI Block | Boosted WAMI Block |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, path in baseline:
        base = metrics(path)
        item = boosted[name]
        lines.append(
            f"| {name} | {pct(base['ir'])} | {pct(item['ir'])} | {pct(item['ir'] - base['ir'])} | "
            f"{pct(base['fpr'])} | {pct(item['fpr'])} | {pct(item['fpr'] - base['fpr'])} | "
            f"{pct(base['planner_risk'])} | {pct(item['planner_risk'])} | "
            f"{pct(base['wami_block'])} | {pct(item['wami_block'])} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "- Boosting mainly increases `Planner Risk Rate`, meaning the local Qwen2.5 planner more often emits a dangerous action instead of stopping early or answering directly.",
        "- `WAMI Action Block Rate` remains high. This means once dangerous actions enter WAMI, WAMI still catches most/all of them.",
        "- BIPIA benefits the most: boosted full IR reaches 91.4% with 0.5% FPR and 100.0% WAMI action blocking.",
        "- InjecAgent improves but remains limited by planner behavior on the full dataset.",
        "- AgentDojo improves IR but also raises FPR; report it as a stronger stress setting, not the cleanest operating point.",
    ]
    out = Path("data/qwen25_7b_ollama_boost_full_all_datasets_summary.md")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out)
    print("\n".join(lines[:16]))


if __name__ == "__main__":
    main()
