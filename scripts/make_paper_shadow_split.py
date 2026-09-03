from __future__ import annotations

import argparse
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.generate_self_training_data import generate_samples
from wami.datasets import write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic/shadow train-val data for zero-supervision WAMI.")
    parser.add_argument("--count", type=int, default=4000)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--train-output", default="data/paper_shadow_train.jsonl")
    parser.add_argument("--val-output", default="data/paper_shadow_val.jsonl")
    args = parser.parse_args()

    samples = generate_samples(args.count, args.seed)
    rng = random.Random(args.seed)
    rng.shuffle(samples)
    val_n = max(1, int(len(samples) * args.val_ratio))
    val = samples[:val_n]
    train = samples[val_n:]
    write_jsonl(train, args.train_output)
    write_jsonl(val, args.val_output)
    print(f"train={len(train)} saved={Path(args.train_output).resolve()}")
    print(f"val={len(val)} saved={Path(args.val_output).resolve()}")


if __name__ == "__main__":
    main()
