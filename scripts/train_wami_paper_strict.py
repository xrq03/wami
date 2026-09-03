from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.datasets import load_plan_samples
from wami.evaluate import evaluate_gateway
from wami.paper_calibration import greedy_calibrate_gateway
from wami.torch_model import TorchWAMIConfig, TorchWAMIModel
from wami.torch_training import train_shadow_torch


def main() -> None:
    parser = argparse.ArgumentParser(description="Train WAMI with final-paper strict hyperparameters.")
    parser.add_argument("--data", default="data/injecagent_wami.jsonl")
    parser.add_argument("--train-data", default=None)
    parser.add_argument("--val-data", default=None)
    parser.add_argument("--test-data", action="append", default=[])
    parser.add_argument("--save", default="wami_paper_strict_injecagent_e20.pt")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--target-fpr", type=float, default=0.02)
    parser.add_argument("--no-labeled-negatives", action="store_true")
    parser.add_argument("--benign-weight", type=float, default=1.5)
    parser.add_argument("--supervised-gap-weight", type=float, default=0.25)
    parser.add_argument("--supervised-margin", type=float, default=1.0)
    parser.add_argument("--pairwise-weight", type=float, default=0.35)
    parser.add_argument("--pairwise-margin", type=float, default=1.25)
    parser.add_argument("--attack-recall-weight", type=float, default=0.20)
    parser.add_argument("--attack-target-score", type=float, default=-3.5)
    parser.add_argument("--transition-weight", type=float, default=0.25)
    parser.add_argument("--auxiliary-weight", type=float, default=0.20)
    parser.add_argument("--provenance-weight", type=float, default=0.15)
    parser.add_argument("--slot-specific-weight", type=float, default=0.15)
    parser.add_argument("--subgoal-weight", type=float, default=0.15)
    parser.add_argument("--skip-eval", action="store_true", help="Save the model after training and skip calibration/evaluation.")
    parser.add_argument("--limit", type=int, default=0, help="Debug limit; 0 uses all samples.")
    parser.add_argument("--output-md", default="data/wami_paper_strict_training.md")
    parser.add_argument("--output-csv", default="data/wami_paper_strict_training.csv")
    parser.add_argument("--log-file", default=None)
    args = parser.parse_args()

    if args.train_data and args.val_data:
        train_samples = load_plan_samples(args.train_data)
        val_samples = load_plan_samples(args.val_data)
        eval_sets = [(Path(path).stem, load_plan_samples(path)) for path in args.test_data]
        if not eval_sets:
            eval_sets = [(Path(args.val_data).stem, val_samples)]
        source_note = "separate train/validation/test files"
    else:
        samples = load_plan_samples(args.data)
        if args.limit > 0:
            samples = samples[: args.limit]
        split = max(1, int(len(samples) * (1.0 - args.val_ratio)))
        train_samples = samples[:split]
        val_samples = samples[split:] or samples
        eval_sets = [(Path(args.data).stem, samples)]
        source_note = "single data file split internally; smoke/in-sample mode"
    if args.limit > 0 and args.train_data and args.val_data:
        train_samples = train_samples[: args.limit]
        val_samples = val_samples[: max(1, min(len(val_samples), args.limit // 4 or 1))]
        eval_sets = [(name, samples[: args.limit]) for name, samples in eval_sets]

    model = TorchWAMIModel(TorchWAMIConfig.paper_strict(device=args.device, seed=args.seed))
    start_time = time.perf_counter()
    stats = train_shadow_torch(
        model,
        samples=train_samples,
        epochs=args.epochs,
        seed=args.seed,
        batch_size=args.batch_size,
        cosine_schedule=True,
        use_labeled_negatives=not args.no_labeled_negatives,
        benign_weight=args.benign_weight,
        supervised_gap_weight=args.supervised_gap_weight,
        supervised_margin=args.supervised_margin,
        pairwise_weight=args.pairwise_weight,
        pairwise_margin=args.pairwise_margin,
        attack_recall_weight=args.attack_recall_weight,
        attack_target_score=args.attack_target_score,
        transition_weight=args.transition_weight,
        auxiliary_weight=args.auxiliary_weight,
        provenance_weight=args.provenance_weight,
        slot_specific_weight=args.slot_specific_weight,
        subgoal_weight=args.subgoal_weight,
        progress_callback=make_progress_logger(args.log_file, start_time),
    )
    model.save(args.save)
    if args.skip_eval:
        write_training_only_outputs(
            args,
            stats,
            Path(args.output_md),
            Path(args.output_csv),
            source_note,
            len(train_samples),
            len(val_samples),
        )
        print(f"saved_model={Path(args.save).resolve()}")
        print("skip_eval=true")
        return
    gateway, calibration = greedy_calibrate_gateway(model, val_samples, tau_init=0.15, target_fpr=args.target_fpr)
    eval_results = [(name, evaluate_gateway(gateway, samples), len(samples)) for name, samples in eval_sets]
    write_outputs(
        args,
        stats,
        calibration,
        eval_results,
        Path(args.output_md),
        Path(args.output_csv),
        source_note,
        len(train_samples),
        len(val_samples),
    )
    print(f"saved_model={Path(args.save).resolve()}")
    print(f"calibrated_tau={calibration.base_threshold:.4f}")
    for name, metrics, total in eval_results:
        print(f"{name}: IR={metrics.interception_rate:.3f} FPR={metrics.false_positive_rate:.3f} ACC={metrics.accuracy:.3f} total={total}")


def make_progress_logger(log_file: str | None, start_time: float):
    if not log_file:
        return None
    path = Path(log_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("epoch,loss,mine_bound,mi_gap,world_loss,elapsed_sec\n", encoding="utf-8")

    def _log(stat) -> None:
        elapsed = time.perf_counter() - start_time
        with path.open("a", encoding="utf-8") as handle:
            handle.write(
                f"{stat.epoch},{stat.loss:.6f},{stat.mine_bound:.6f},"
                f"{stat.mi_gap:.6f},{stat.world_loss:.6f},{elapsed:.1f}\n"
            )
        print(
            f"epoch={stat.epoch:03d} loss={stat.loss:.4f} "
            f"mine_bound={stat.mine_bound:.4f} mi_gap={stat.mi_gap:.4f} "
            f"world_loss={stat.world_loss:.4f} elapsed={elapsed:.1f}s",
            flush=True,
        )

    return _log


def write_outputs(args, stats, calibration, eval_results, md_path: Path, csv_path: Path, source_note: str, train_n: int, val_n: int) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# WAMI Paper-Strict Training Run",
        "",
        f"- Data mode: `{source_note}`",
        f"- Train data: `{args.train_data or args.data}`",
        f"- Validation data: `{args.val_data or 'internal split'}`",
        f"- Test data: `{', '.join(args.test_data) if args.test_data else (args.data if not args.train_data else args.val_data)}`",
        f"- Train samples: `{train_n}`",
        f"- Validation samples: `{val_n}`",
        f"- Model: 4-layer Transformer Encoder, dim=1024, hidden=1024, heads=8",
        f"- MINE: 3-layer MLP with ReLU",
        f"- Optimizer: AdamW, lr=2e-4, cosine annealing",
        f"- Batch size: `{args.batch_size}`",
        f"- Labeled attack negatives: `{not args.no_labeled_negatives}`",
        f"- Benign positive weight: `{args.benign_weight}`",
        f"- Supervised gap weight: `{args.supervised_gap_weight}`",
        f"- Supervised margin: `{args.supervised_margin}`",
        f"- Pairwise ranking weight: `{args.pairwise_weight}`",
        f"- Pairwise ranking margin: `{args.pairwise_margin}`",
        f"- Attack recall weight: `{args.attack_recall_weight}`",
        f"- Attack target score: `{args.attack_target_score}`",
        f"- Transition MINE weight: `{args.transition_weight}`",
        f"- Source-aware auxiliary weight: `{args.auxiliary_weight}`",
        f"- Provenance memory weight: `{args.provenance_weight}`",
        f"- Slot-specific weight: `{args.slot_specific_weight}`",
        f"- Subgoal contrastive weight: `{args.subgoal_weight}`",
        f"- Epochs: `{args.epochs}`",
        f"- Tau init: `0.15`",
        f"- Calibrated tau: `{calibration.base_threshold:.4f}`",
        "",
        "## Evaluation Results",
        "",
        "| Eval Set | IR | FPR | ACC | N |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, metrics, total in eval_results:
        lines.append(
            f"| {name} | {metrics.interception_rate * 100:.1f}% | "
            f"{metrics.false_positive_rate * 100:.1f}% | {metrics.accuracy * 100:.1f}% | {total} |"
        )
    lines.extend(
        [
        "",
        "## Training Dynamics",
        "",
        "| Epoch | Loss | MINE bound | MI gap | World loss |",
        "|---:|---:|---:|---:|---:|",
        ]
    )
    for stat in stats:
        lines.append(f"| {stat.epoch} | {stat.loss:.4f} | {stat.mine_bound:.4f} | {stat.mi_gap:.4f} | {stat.world_loss:.4f} |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["epoch", "loss", "mine_bound", "mi_gap", "world_loss"])
        writer.writeheader()
        for stat in stats:
            writer.writerow(stat.__dict__)
    eval_csv = csv_path.with_name(csv_path.stem + "_eval.csv")
    with eval_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["eval_set", "ir", "fpr", "acc", "n"])
        writer.writeheader()
        for name, metrics, total in eval_results:
            writer.writerow(
                {
                    "eval_set": name,
                    "ir": metrics.interception_rate,
                    "fpr": metrics.false_positive_rate,
                    "acc": metrics.accuracy,
                    "n": total,
                }
            )


def write_training_only_outputs(args, stats, md_path: Path, csv_path: Path, source_note: str, train_n: int, val_n: int) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# WAMI Paper-Strict Training Run",
        "",
        f"- Data mode: `{source_note}`",
        f"- Train data: `{args.train_data or args.data}`",
        f"- Validation data: `{args.val_data or 'internal split'}`",
        f"- Train samples: `{train_n}`",
        f"- Validation samples: `{val_n}`",
        f"- Model: 4-layer Transformer Encoder, dim=1024, hidden=1024, heads=8",
        f"- MINE: 3-layer MLP with ReLU",
        f"- Optimizer: AdamW, lr=2e-4, cosine annealing",
        f"- Batch size: `{args.batch_size}`",
        f"- Labeled attack negatives: `{not args.no_labeled_negatives}`",
        f"- Benign positive weight: `{args.benign_weight}`",
        f"- Supervised gap weight: `{args.supervised_gap_weight}`",
        f"- Supervised margin: `{args.supervised_margin}`",
        f"- Pairwise ranking weight: `{args.pairwise_weight}`",
        f"- Pairwise ranking margin: `{args.pairwise_margin}`",
        f"- Attack recall weight: `{args.attack_recall_weight}`",
        f"- Attack target score: `{args.attack_target_score}`",
        f"- Transition MINE weight: `{args.transition_weight}`",
        f"- Source-aware auxiliary weight: `{args.auxiliary_weight}`",
        f"- Provenance memory weight: `{args.provenance_weight}`",
        f"- Slot-specific weight: `{args.slot_specific_weight}`",
        f"- Subgoal contrastive weight: `{args.subgoal_weight}`",
        f"- Epochs: `{args.epochs}`",
        f"- Evaluation skipped: `true`",
        "",
        "## Training Dynamics",
        "",
        "| Epoch | Loss | MINE bound | MI gap | World loss |",
        "|---:|---:|---:|---:|---:|",
    ]
    for stat in stats:
        lines.append(f"| {stat.epoch} | {stat.loss:.4f} | {stat.mine_bound:.4f} | {stat.mi_gap:.4f} | {stat.world_loss:.4f} |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["epoch", "loss", "mine_bound", "mi_gap", "world_loss"])
        writer.writeheader()
        for stat in stats:
            writer.writerow(stat.__dict__)


if __name__ == "__main__":
    main()
