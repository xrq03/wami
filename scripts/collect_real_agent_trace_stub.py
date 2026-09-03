from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Stub for collecting real agent runtime traces into WAMI training JSONL.")
    parser.add_argument("--output", default="data/real_agent_traces_stub.jsonl")
    args = parser.parse_args()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    sample = {
        "intent": "stub user task",
        "plan": "Action: ToolA(input='stub')\nAction: RespondToUser(input=$0)",
        "label": 0,
        "trace_source": "stub",
    }
    Path(args.output).write_text(json.dumps(sample, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"created_stub={Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
