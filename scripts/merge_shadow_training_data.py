from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge benign/original data with generated shadow attacks.")
    parser.add_argument("--base", default="data/agentdojo_wami.jsonl")
    parser.add_argument("--shadow", default="data/llm_shadow_attacks_agentdojo.jsonl")
    parser.add_argument("--out", default="data/agentdojo_with_llm_shadow.jsonl")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out.open("w", encoding="utf-8") as writer:
        for path in (Path(args.base), Path(args.shadow)):
            with path.open("r", encoding="utf-8") as reader:
                for line in reader:
                    if line.strip():
                        writer.write(line)
                        count += 1
    print(f"merged_rows={count}")
    print(f"out={out}")


if __name__ == "__main__":
    main()
