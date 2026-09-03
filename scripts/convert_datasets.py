from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.datasets import convert_agentdojo, convert_bipia, convert_injecagent, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--external-root", default="external")
    parser.add_argument("--output-dir", default="data")
    parser.add_argument("--dataset", choices=["all", "injecagent", "bipia", "agentdojo"], default="all")
    parser.add_argument("--bipia-max-pairs-per-task", type=int, default=None)
    parser.add_argument("--agentdojo-version", default="v1")
    parser.add_argument("--agentdojo-max-attack-pairs-per-suite", type=int, default=300)
    args = parser.parse_args()

    external = Path(args.external_root)
    out = Path(args.output_dir)
    if args.dataset in {"all", "injecagent"}:
        samples = convert_injecagent(external / "InjecAgent-main")
        count = write_jsonl(samples, out / "injecagent_wami.jsonl")
        print(f"wrote {count} InjecAgent samples -> {out / 'injecagent_wami.jsonl'}")
    if args.dataset in {"all", "bipia"}:
        samples = convert_bipia(external / "BIPIA-main", max_pairs_per_task=args.bipia_max_pairs_per_task)
        count = write_jsonl(samples, out / "bipia_wami.jsonl")
        print(f"wrote {count} BIPIA samples -> {out / 'bipia_wami.jsonl'}")
    if args.dataset in {"all", "agentdojo"}:
        root = external / "AgentDojo"
        if not root.exists():
            root = external / "agentdojo-main"
        samples = convert_agentdojo(
            root,
            version=args.agentdojo_version,
            max_attack_pairs_per_suite=args.agentdojo_max_attack_pairs_per_suite,
        )
        count = write_jsonl(samples, out / "agentdojo_wami.jsonl")
        print(f"wrote {count} AgentDojo samples -> {out / 'agentdojo_wami.jsonl'}")


if __name__ == "__main__":
    main()
