from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.datasets import load_plan_samples  # noqa: E402
from wami.paper_mine_gateway import PaperMINEConfig, PaperMINEGateway  # noqa: E402
from wami.torch_model import TorchWAMIModel  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Export per-sample accepted WAMI paper-faithful decisions.")
    parser.add_argument("--model-a", default="wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt")
    parser.add_argument("--model-b", default="wami_paper_mine_triplet_slot_seed4071_e4_cuda.pt")
    parser.add_argument("--output-csv", default="data/wami_paper_faithful_accepted_audit_details.csv")
    args = parser.parse_args()

    gateway_a = make_gateway(TorchWAMIModel.load(resolve(args.model_a)), -4.5, 0.35, 0.10, False, 0.0)
    gateway_b = make_gateway(TorchWAMIModel.load(resolve(args.model_b)), -5.0, 0.35, 0.10, False, 0.0)
    rows = []
    for dataset, path, final_mode in [
        ("BIPIA", ROOT / "data" / "bipia_wami.jsonl", "or"),
        ("InjecAgent", ROOT / "data" / "injecagent_wami.jsonl", "or"),
        ("AgentDojo", ROOT / "data" / "agentdojo_wami.jsonl", "b"),
    ]:
        samples = load_plan_samples(path)
        for index, sample in enumerate(samples):
            start = time.perf_counter()
            da = gateway_a.inspect(sample.intent, sample.plan)
            db = gateway_b.inspect(sample.intent, sample.plan)
            latency_ms = (time.perf_counter() - start) * 1000.0
            a_blocked = not da.allowed
            b_blocked = not db.allowed
            blocked = (a_blocked or b_blocked) if final_mode == "or" else b_blocked
            reason = f"final_mode={final_mode}; A={da.reason}; B={db.reason}"
            rows.append(
                {
                    "method": "WAMI paper-faithful",
                    "dataset": dataset,
                    "index": index,
                    "label": int(sample.label),
                    "blocked": blocked,
                    "final_mode": final_mode,
                    "a_sourceaware_blocked": a_blocked,
                    "b_triplet_blocked": b_blocked,
                    "a_score": da.score,
                    "a_threshold": da.threshold,
                    "a_tool": da.tool or "",
                    "b_score": db.score,
                    "b_threshold": db.threshold,
                    "b_tool": db.tool or "",
                    "latency_ms": latency_ms,
                    "reason": reason,
                    "intent": sample.intent,
                    "plan": sample.plan,
                    "source_file": str(path),
                }
            )
        print(f"[ok] {dataset}: {len(samples)} samples")
    write_csv(resolve(args.output_csv), rows)
    print(f"saved {args.output_csv}")


def resolve(path_text: str | Path) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def make_gateway(model, tau: float, transition_fusion: float, auxiliary_fusion: float, use_provenance: bool, provenance_fusion: float):
    return PaperMINEGateway(
        model,
        PaperMINEConfig(
            base_threshold=tau,
            plan_threshold=tau,
            use_transition_mine=True,
            transition_fusion=transition_fusion,
            use_auxiliary_heads=True,
            auxiliary_fusion=auxiliary_fusion,
            use_provenance_memory=use_provenance,
            provenance_fusion=provenance_fusion,
        ),
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
