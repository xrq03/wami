from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.agent import ReActAgent, load_tool_names
from wami.calibration import calibrate_gateway
from wami.gateway import WAMIGateway
from wami.llm_client import LLMConfig, OpenAICompatibleClient
from wami.model import WAMIModel
from wami.training import load_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/llm_agent.example.json")
    parser.add_argument("--wami-model", default="wami_model.npz")
    parser.add_argument("--calibration-data", default="data/injecagent_wami.jsonl")
    parser.add_argument(
        "--tools-file",
        default="auto",
        help="Tool catalog path. Use 'auto' to pick by calibration data, or 'none' to avoid tool-name filtering.",
    )
    parser.add_argument("--intent", required=True)
    parser.add_argument("--context", default="")
    parser.add_argument("--dry-run", action="store_true", help="Print the LLM prompt without calling the API")
    args = parser.parse_args()

    model = WAMIModel.load(args.wami_model) if Path(args.wami_model).exists() else WAMIModel()
    samples = load_jsonl(args.calibration_data) if Path(args.calibration_data).exists() else []
    gateway = calibrate_gateway(model, samples) if samples else WAMIGateway(model)
    client = OpenAICompatibleClient(LLMConfig.from_file(args.config))
    tools_file = _resolve_tools_file(args.tools_file, args.calibration_data)
    tools = load_tool_names(tools_file)
    agent = ReActAgent(client, gateway, tools)
    if args.dry_run:
        print(f"=== TOOLS ({tools_file or 'none'}, {len(tools)}) ===")
        print("=== SYSTEM ===")
        print(agent._messages(args.intent, args.context)[0]["content"])
        print("\n=== USER ===")
        print(agent._messages(args.intent, args.context)[1]["content"])
        return
    run = agent.run(args.intent, args.context)

    print("=== LLM RESPONSE ===")
    print(run.raw_response)
    print("\n=== EXTRACTED PLAN ===")
    print(run.generated_plan)
    print("\n=== WAMI DECISION ===")
    print(
        f"allowed={run.decision.allowed} step={run.decision.step} tool={run.decision.tool} "
        f"score={run.decision.score:.4f} threshold={run.decision.threshold:.4f} "
        f"reason={run.decision.reason}"
    )


def _resolve_tools_file(tools_file: str | None, data_path: str) -> str | None:
    if tools_file is None:
        return None
    value = tools_file.strip()
    if not value or value.lower() in {"none", "off", "false", "no"}:
        return None
    if value.lower() != "auto":
        return value
    data_lower = data_path.lower()
    if "bipia" in data_lower:
        return None
    default_injecagent = "external/InjecAgent-main/data/tools.json"
    return default_injecagent if Path(default_injecagent).exists() else None


if __name__ == "__main__":
    main()
