from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wami.llm_client import LLMConfig, OpenAICompatibleClient
from wami.shadow_llm import attacks_to_jsonl_rows, generate_llm_shadow_attacks, local_shadow_attacks
from wami.training import load_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate diverse shadow adversarial plans.")
    parser.add_argument("--data", default="data/agentdojo_wami.jsonl")
    parser.add_argument("--out", default="data/llm_shadow_attacks_agentdojo.jsonl")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--per-sample", type=int, default=6)
    parser.add_argument("--use-llm", action="store_true")
    parser.add_argument("--llm-config", default="config/llm_agent.local.json")
    parser.add_argument("--model", default="")
    args = parser.parse_args()

    samples = [sample for sample in load_jsonl(ROOT / args.data) if sample.label == 0][: args.limit]
    client = None
    if args.use_llm:
        cfg = LLMConfig.from_file(ROOT / args.llm_config)
        if args.model:
            cfg.model = args.model
        cfg.temperature = 0.7
        cfg.max_tokens = 1800
        client = OpenAICompatibleClient(cfg)

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    started = time.perf_counter()
    with out_path.open("w", encoding="utf-8") as handle:
        for index, sample in enumerate(samples, 1):
            if client is None:
                attacks = local_shadow_attacks(sample)[: args.per_sample]
            else:
                try:
                    attacks = generate_llm_shadow_attacks(client, sample, count=args.per_sample)
                except Exception as exc:
                    print(f"{index:03d} warning=llm_failed fallback=local error={exc}")
                    attacks = local_shadow_attacks(sample)[: args.per_sample]
            rows = attacks_to_jsonl_rows(attacks)
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            total += len(rows)
            kinds = ", ".join(row["attack_kind"] for row in rows)
            print(f"{index:03d} attacks={len(rows)} kinds={kinds}")
    elapsed = (time.perf_counter() - started) * 1000.0
    print(f"saved={out_path}")
    print(f"samples={len(samples)} attacks={total} elapsed_ms={elapsed:.1f}")


if __name__ == "__main__":
    main()
