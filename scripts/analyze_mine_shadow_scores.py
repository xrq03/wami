from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.model import WAMIModel
from wami.tdg import build_tdg
from wami.training import load_jsonl


@dataclass
class Row:
    dataset: str
    scorer: str
    benign_mean: float
    attack_mean: float
    score_gap: float
    auc_attack_low_score: float
    benign_n: int
    attack_n: int


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/agentdojo_wami.jsonl")
    parser.add_argument("--trained-model", default="wami_agentdojo_final_tuned_e5.npz")
    parser.add_argument("--dataset-name", default="")
    parser.add_argument("--output-md", default="data/mine_shadow_score_analysis.md")
    parser.add_argument("--output-csv", default="data/mine_shadow_score_analysis.csv")
    args = parser.parse_args()

    samples = load_jsonl(args.data)
    trained = WAMIModel.load(args.trained_model) if Path(args.trained_model).exists() else WAMIModel()
    untrained = WAMIModel()
    dataset = args.dataset_name or Path(args.data).stem.replace("_wami", "")

    rows = [
        summarize(dataset, "trained MINE score", score_samples(samples, trained, "mine")),
        summarize(dataset, "untrained MINE score", score_samples(samples, untrained, "mine")),
        summarize(dataset, "cosine similarity", score_samples(samples, trained, "cosine")),
    ]
    table = format_table(rows)
    print(table)
    write_outputs(rows, table, Path(args.output_md), Path(args.output_csv))
    print(f"saved markdown to {args.output_md}")
    print(f"saved csv to {args.output_csv}")


def score_samples(samples, model: WAMIModel, mode: str) -> list[tuple[int, float]]:
    out = []
    for sample in samples:
        tdg = build_tdg(sample.plan)
        intent_vec = model.encode_intent(sample.intent)
        step_scores = []
        if mode == "plan_cosine":
            plan_vec = model.encode_plan(sample.plan)
            step_scores.append(cosine(intent_vec, plan_vec))
        else:
            for _node, state in model.rollout(sample.intent, tdg):
                if mode == "mine":
                    step_scores.append(model.mine_score(intent_vec, state))
                elif mode == "cosine":
                    step_scores.append(cosine(intent_vec, state))
                else:
                    raise ValueError(mode)
        # Lower alignment means more suspicious, so use the minimum score along
        # the trajectory as the sample-level risk signal.
        out.append((sample.label, min(step_scores) if step_scores else 0.0))
    return out


def summarize(dataset: str, scorer: str, scored: list[tuple[int, float]]) -> Row:
    benign = [score for label, score in scored if label == 0]
    attack = [score for label, score in scored if label == 1]
    return Row(
        dataset=dataset,
        scorer=scorer,
        benign_mean=float(np.mean(benign)) if benign else 0.0,
        attack_mean=float(np.mean(attack)) if attack else 0.0,
        score_gap=(float(np.mean(benign)) - float(np.mean(attack))) if benign and attack else 0.0,
        auc_attack_low_score=auc_attack_lower(scored),
        benign_n=len(benign),
        attack_n=len(attack),
    )


def auc_attack_lower(scored: list[tuple[int, float]]) -> float:
    attacks = [score for label, score in scored if label == 1]
    benign = [score for label, score in scored if label == 0]
    if not attacks or not benign:
        return 0.0
    wins = ties = 0
    total = len(attacks) * len(benign)
    for attack_score in attacks:
        for benign_score in benign:
            if attack_score < benign_score:
                wins += 1
            elif attack_score == benign_score:
                ties += 1
    return (wins + 0.5 * ties) / total


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(a @ b / denom) if denom else 0.0


def format_table(rows: list[Row]) -> str:
    lines = [
        "| Dataset | Scorer | Benign Mean | Attack Mean | Gap | AUC | Benign N | Attack N |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row.dataset} | {row.scorer} | {row.benign_mean:.4f} | {row.attack_mean:.4f} | "
            f"{row.score_gap:.4f} | {row.auc_attack_low_score:.3f} | {row.benign_n} | {row.attack_n} |"
        )
    return "\n".join(lines)


def write_outputs(rows: list[Row], table: str, md_path: Path, csv_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(table + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
