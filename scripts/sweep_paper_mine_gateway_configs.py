from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_paper_mine_gateway import calibrate, evaluate
from wami.datasets import load_plan_samples
from wami.torch_model import TorchWAMIModel


@dataclass
class SweepRow:
    config: str
    dataset: str
    ir: float
    fpr: float
    acc: float
    latency_ms: float
    n: int
    tau: float
    target_fpr: float
    risk_margin: float
    passive_margin: float
    transition_fusion: float
    auxiliary_fusion: float
    provenance_fusion: float


class CalibArgs:
    def __init__(
        self,
        *,
        candidate_count: int,
        target_fpr: float,
        tau_init: float,
        candidate_radius: float,
        risk_margin: float,
        passive_margin: float,
        transition_fusion: float,
        auxiliary_fusion: float,
        provenance_fusion: float,
    ) -> None:
        self.candidate_count = candidate_count
        self.target_fpr = target_fpr
        self.tau_init = tau_init
        self.candidate_radius = candidate_radius
        self.risk_margin = risk_margin
        self.passive_margin = passive_margin
        self.use_transition_mine = True
        self.transition_fusion = transition_fusion
        self.use_auxiliary_heads = True
        self.auxiliary_fusion = auxiliary_fusion
        self.use_provenance_memory = True
        self.provenance_fusion = provenance_fusion


def main() -> None:
    parser = argparse.ArgumentParser(description="Sweep WAMI paper-MINE gateway margins without test-set calibration.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--val-data", required=True)
    parser.add_argument("--test-data", action="append", required=True)
    parser.add_argument("--limit-per-label", type=int, default=0)
    parser.add_argument("--output-md", default="data/wami_gateway_config_sweep.md")
    parser.add_argument("--output-csv", default="data/wami_gateway_config_sweep.csv")
    args = parser.parse_args()

    model = TorchWAMIModel.load(args.model)
    val = load_plan_samples(args.val_data)
    test_sets = [(Path(path).stem, maybe_limit(load_plan_samples(path), args.limit_per_label)) for path in args.test_data]
    configs = build_configs()
    rows: list[SweepRow] = []
    for name, cfg in configs:
        gateway, tau = calibrate(model, val, cfg)
        for dataset, samples in test_sets:
            started = time.perf_counter()
            metrics = evaluate(gateway, samples)
            latency = (time.perf_counter() - started) * 1000.0 / max(1, len(samples))
            row = SweepRow(
                config=name,
                dataset=dataset,
                ir=metrics.interception_rate,
                fpr=metrics.false_positive_rate,
                acc=metrics.accuracy,
                latency_ms=latency,
                n=len(samples),
                tau=tau,
                target_fpr=cfg.target_fpr,
                risk_margin=cfg.risk_margin,
                passive_margin=cfg.passive_margin,
                transition_fusion=cfg.transition_fusion,
                auxiliary_fusion=cfg.auxiliary_fusion,
                provenance_fusion=cfg.provenance_fusion,
            )
            rows.append(row)
            print(
                f"{name} {dataset}: IR={row.ir:.3f} FPR={row.fpr:.3f} "
                f"ACC={row.acc:.3f} tau={row.tau:.3f} latency={row.latency_ms:.3f}ms",
                flush=True,
            )
    write_outputs(rows, Path(args.output_md), Path(args.output_csv))


def build_configs() -> list[tuple[str, CalibArgs]]:
    configs = []
    for target_fpr in [0.02, 0.05, 0.08]:
        for passive_margin in [0.15, 0.25, 0.35]:
            configs.append(
                (
                    f"lowrisk_pf{target_fpr:.2f}_passive{passive_margin:.2f}",
                    CalibArgs(
                        candidate_count=41,
                        target_fpr=target_fpr,
                        tau_init=0.15,
                        candidate_radius=6.0,
                        risk_margin=0.0,
                        passive_margin=passive_margin,
                        transition_fusion=0.35,
                        auxiliary_fusion=0.20,
                        provenance_fusion=0.10,
                    ),
                )
            )
    for aux, prov in [(0.10, 0.05), (0.15, 0.05), (0.25, 0.15)]:
        configs.append(
            (
                f"fusion_aux{aux:.2f}_prov{prov:.2f}",
                CalibArgs(
                    candidate_count=41,
                    target_fpr=0.05,
                    tau_init=0.15,
                    candidate_radius=6.0,
                    risk_margin=0.0,
                    passive_margin=0.25,
                    transition_fusion=0.35,
                    auxiliary_fusion=aux,
                    provenance_fusion=prov,
                ),
            )
        )
    return configs


def maybe_limit(samples, limit_per_label: int):
    if limit_per_label <= 0:
        return samples
    benign = [sample for sample in samples if sample.label == 0][:limit_per_label]
    attack = [sample for sample in samples if sample.label == 1][:limit_per_label]
    return attack + benign


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def write_outputs(rows: list[SweepRow], md_path: Path, csv_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(SweepRow.__dataclass_fields__.keys()))
        writer.writeheader()
        writer.writerows([row.__dict__ for row in rows])
    lines = [
        "# WAMI Gateway Config Sweep",
        "",
        "Validation data is used for threshold selection. Test datasets are evaluation-only.",
        "",
        "| Config | Dataset | IR | FPR | ACC | Tau | Latency ms | N |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row.config} | {row.dataset} | {pct(row.ir)} | {pct(row.fpr)} | "
            f"{pct(row.acc)} | {row.tau:.3f} | {row.latency_ms:.3f} | {row.n} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved {md_path}")
    print(f"saved {csv_path}")


if __name__ == "__main__":
    main()
