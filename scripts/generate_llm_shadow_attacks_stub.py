from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Stub for future LLM-generated WAMI shadow attacks.")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--model", default="qwen-turbo")
    parser.add_argument("--seed-data", default="data/paper_shadow_train_triplet_seed4071.jsonl")
    parser.add_argument("--output", default="data/llm_shadow_attacks.jsonl")
    args = parser.parse_args()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(
        "# This file is a placeholder. Fill API settings and implement provider calls before using.\n"
        f"# model={args.model}\n"
        f"# seed_data={args.seed_data}\n",
        encoding="utf-8",
    )
    print(f"created_stub={Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
