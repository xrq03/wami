from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.ablation import run_ablation
from wami.adapters import load_flexible_json, load_flexible_jsonl
from wami.calibration import calibrate_gateway
from wami.evaluate import evaluate_gateway
from wami.gateway import WAMIGateway
from wami.model import WAMIConfig, WAMIModel
from wami.shadow import synthetic_samples
from wami.training import load_jsonl, train_shadow


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=None, help="JSONL file with intent, plan, optional label")
    parser.add_argument("--format", choices=["wami", "flex-jsonl", "flex-json"], default="wami")
    parser.add_argument("--backend", choices=["numpy", "torch"], default="numpy")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--dim", type=int, default=128)
    parser.add_argument("--hidden-dim", type=int, default=512)
    parser.add_argument("--layers", type=int, default=2)
    parser.add_argument("--heads", type=int, default=4)
    parser.add_argument("--lr", type=float, default=0.03)
    parser.add_argument("--save", default="wami_model.npz")
    parser.add_argument("--eval", action="store_true")
    parser.add_argument("--ablate", action="store_true")
    parser.add_argument("--no-calibrate", action="store_true")
    parser.add_argument("--calibration-quantile", type=float, default=0.05)
    parser.add_argument("--calibration-margin", type=float, default=0.02)
    parser.add_argument("--score-margin", type=float, default=0.0)
    args = parser.parse_args()

    if args.data and args.format == "flex-jsonl":
        samples = load_flexible_jsonl(args.data)
    elif args.data and args.format == "flex-json":
        samples = load_flexible_json(args.data)
    else:
        samples = load_jsonl(args.data) if args.data else synthetic_samples()

    if args.backend == "torch":
        from wami.torch_model import TorchWAMIConfig, TorchWAMIModel
        from wami.torch_training import train_shadow_torch

        model = TorchWAMIModel(
            TorchWAMIConfig(
                dim=args.dim,
                hidden_dim=args.hidden_dim,
                layers=args.layers,
                heads=args.heads,
                learning_rate=args.lr,
            )
        )
        stats = train_shadow_torch(model, samples=samples, epochs=args.epochs)
        for stat in stats:
            print(
                f"epoch={stat.epoch:03d} loss={stat.loss:.4f} "
                f"mine_bound={stat.mine_bound:.4f} mi_gap={stat.mi_gap:.4f} "
                f"world_loss={stat.world_loss:.4f}"
            )
    else:
        model = WAMIModel(WAMIConfig(dim=args.dim, learning_rate=args.lr))
        stats = train_shadow(model, samples=samples, epochs=args.epochs)
        for stat in stats:
            print(
                f"epoch={stat.epoch:03d} loss={stat.loss:.4f} "
                f"mi_gap={stat.mi_gap:.4f} world_loss={stat.world_loss:.4f}"
            )

    model.save(args.save)
    print(f"saved={args.save}")
    gateway = (
        WAMIGateway(model)
        if args.no_calibrate
        else calibrate_gateway(
            model,
            samples,
            quantile=args.calibration_quantile,
            margin=args.calibration_margin,
        )
    )
    gateway.score_margin = args.score_margin
    if args.eval:
        metrics = evaluate_gateway(gateway, samples)
        print(
            f"IR={metrics.interception_rate:.3f} "
            f"FPR={metrics.false_positive_rate:.3f} "
            f"ACC={metrics.accuracy:.3f} total={metrics.total}"
        )
    if args.ablate:
        for result in run_ablation(model, samples):
            m = result.metrics
            print(
                f"{result.name}: IR={m.interception_rate:.3f} "
                f"FPR={m.false_positive_rate:.3f} ACC={m.accuracy:.3f} "
                f"latency_ms={result.latency_ms:.2f}"
            )


if __name__ == "__main__":
    main()
