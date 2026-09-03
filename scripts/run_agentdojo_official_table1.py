from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTDOJO_ROOT = ROOT / "external" / "AgentDojo"
AGENTDOJO_SRC = AGENTDOJO_ROOT / "src"
sys.path.insert(0, str(AGENTDOJO_SRC))

import openai  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from openai.types.chat import ChatCompletionSystemMessageParam  # noqa: E402

from agentdojo.agent_pipeline.agent_pipeline import AgentPipeline, PipelineConfig  # noqa: E402
import agentdojo.agent_pipeline.llms.openai_llm as agentdojo_openai_llm  # noqa: E402
from agentdojo.agent_pipeline.llms.openai_llm import OpenAILLM  # noqa: E402
from agentdojo.attacks.attack_registry import load_attack  # noqa: E402
from agentdojo.benchmark import SuiteResults, benchmark_suite_with_injections  # noqa: E402
from agentdojo.logging import OutputLogger  # noqa: E402
from agentdojo.task_suite.load_suites import get_suite  # noqa: E402


@dataclass
class Row:
    suite: str
    defense: str
    attack: str
    model: str
    user_tasks: str
    injection_tasks: str
    security_rate: float
    attack_success_rate: float
    utility_rate: float
    injection_task_utility_rate: float
    ir: float
    fpr_proxy: float
    acc_proxy: float
    n_security: int
    n_utility: int
    latency_ms: float
    status: str
    note: str


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AgentDojo's original benchmark harness for Table 1 replacement.")
    parser.add_argument("--env-file", default="config/official_baselines.local.env")
    parser.add_argument(
        "--model",
        default=None,
        help="OpenAI-compatible model name. Defaults to AGENTDOJO_MODEL or qwen-plus-2025-09-11.",
    )
    parser.add_argument("--suite", action="append", default=None, help="AgentDojo suite. Repeat for multiple.")
    parser.add_argument("--defense", default="spotlighting_with_delimiting")
    parser.add_argument("--attack", default="injecagent")
    parser.add_argument("--user-task", action="append", default=None)
    parser.add_argument("--injection-task", action="append", default=None)
    parser.add_argument("--user-task-count", type=int, default=0, help="Use first N native user tasks per suite.")
    parser.add_argument("--injection-task-count", type=int, default=0, help="Use first N native injection tasks per suite.")
    parser.add_argument("--benchmark-version", default="v1.2.2")
    parser.add_argument("--logdir", default="data/agentdojo_official_runs")
    parser.add_argument("--force-rerun", action="store_true")
    parser.add_argument("--output-md", default="data/agentdojo_official_table1.md")
    parser.add_argument("--output-csv", default="data/agentdojo_official_table1.csv")
    args = parser.parse_args()

    load_dotenv(ROOT / args.env_file)
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE")
    model = args.model or os.environ.get("AGENTDOJO_MODEL") or "qwen-plus-2025-09-11"
    if not api_key or not base_url:
        raise SystemExit("OPENAI_API_KEY and OPENAI_BASE_URL/OPENAI_API_BASE are required in the env file.")
    if args.suite is None:
        args.suite = ["workspace"]
    if args.user_task is None:
        args.user_task = []
    if args.injection_task is None:
        args.injection_task = []

    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    patch_system_role_for_openai_compatible_backends()
    rows = []
    for suite_name in args.suite:
        rows.append(run_one(args, suite_name, client, model))

    write_outputs(rows, resolve_output(args.output_md), resolve_output(args.output_csv))
    print(format_table(rows))
    print(f"saved markdown to {args.output_md}")
    print(f"saved csv to {args.output_csv}")


def resolve_output(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def patch_system_role_for_openai_compatible_backends() -> None:
    original_message = agentdojo_openai_llm._message_to_openai
    original_tool_call = agentdojo_openai_llm._openai_to_tool_call
    original_chat_completion = agentdojo_openai_llm.chat_completion_request

    def patched(message, model_name: str):
        if message["role"] == "system":
            return ChatCompletionSystemMessageParam(
                role="system",
                content=agentdojo_openai_llm._content_blocks_to_openai_content_blocks(message),
            )
        return original_message(message, model_name)

    def patched_tool_call(tool_call):
        try:
            return original_tool_call(tool_call)
        except json.JSONDecodeError:
            from agentdojo.functions_runtime import FunctionCall

            return FunctionCall(
                function=tool_call.function.name,
                args={},
                id=tool_call.id,
            )

    agentdojo_openai_llm._message_to_openai = patched
    agentdojo_openai_llm._openai_to_tool_call = patched_tool_call

    def patched_chat_completion_request(client, model, messages, tools, reasoning_effort, temperature=0.0):
        if str(model).startswith("qwen3"):
            return client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools or agentdojo_openai_llm.NOT_GIVEN,
                tool_choice="auto" if tools else agentdojo_openai_llm.NOT_GIVEN,
                temperature=temperature if temperature is not None else agentdojo_openai_llm.NOT_GIVEN,
                reasoning_effort=reasoning_effort or agentdojo_openai_llm.NOT_GIVEN,
                extra_body={"enable_thinking": False},
            )
        return original_chat_completion(client, model, messages, tools, reasoning_effort, temperature)

    agentdojo_openai_llm.chat_completion_request = patched_chat_completion_request


def run_one(args: argparse.Namespace, suite_name: str, client: openai.OpenAI, model: str) -> Row:
    suite = get_suite(args.benchmark_version, suite_name)
    user_tasks = args.user_task or list(suite.user_tasks.keys())[: max(1, args.user_task_count or 1)]
    injection_tasks = args.injection_task or list(suite.injection_tasks.keys())[: max(1, args.injection_task_count or 1)]
    llm = OpenAILLM(client, model)
    llm.name = model
    pipeline = AgentPipeline.from_config(
        PipelineConfig(
            llm=llm,
            model_id=None,
            defense=args.defense,
            system_message_name=None,
            system_message=None,
        )
    )
    attack = load_attack(args.attack, suite, pipeline)
    started = time.perf_counter()
    with OutputLogger(str(ROOT / args.logdir)):
        results = benchmark_suite_with_injections(
            pipeline,
            suite,
            attack,
            logdir=ROOT / args.logdir,
            force_rerun=args.force_rerun,
            user_tasks=user_tasks,
            injection_tasks=injection_tasks,
            benchmark_version=args.benchmark_version,
        )
    latency_ms = (time.perf_counter() - started) * 1000.0 / max(1, len(results["security_results"]))
    security_rate = mean_bool(results["security_results"])
    utility_rate = mean_bool(results["utility_results"])
    injection_utility = mean_bool(results["injection_tasks_utility_results"])
    return Row(
        suite=suite_name,
        defense=args.defense,
        attack=args.attack,
        model=model,
        user_tasks=",".join(user_tasks),
        injection_tasks=",".join(injection_tasks),
        security_rate=security_rate,
        attack_success_rate=1.0 - security_rate,
        utility_rate=utility_rate,
        injection_task_utility_rate=injection_utility,
        ir=security_rate,
        fpr_proxy=1.0 - utility_rate,
        acc_proxy=(security_rate * len(results["security_results"]) + utility_rate * len(results["utility_results"]))
        / max(1, len(results["security_results"]) + len(results["utility_results"])),
        n_security=len(results["security_results"]),
        n_utility=len(results["utility_results"]),
        latency_ms=latency_ms,
        status="official-harness",
        note="AgentDojo original suite/attack/defense harness; model backend is OpenAI-compatible endpoint from local env.",
    )


def mean_bool(values: dict | SuiteResults) -> float:
    vals = list(values.values())
    if not vals:
        return 0.0
    return sum(bool(v) for v in vals) / len(vals)


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_table(rows: list[Row]) -> str:
    lines = [
        "# AgentDojo Official Harness Table 1 Replacement",
        "",
        "| Suite | Defense | Attack | Model | Security Rate | ASR | Utility | Injection Utility | N | Latency ms | Status |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---|",
        "",
        "## WAMI-style Metrics",
        "",
        "| Suite | Defense | IR | FPR proxy | ACC proxy | Attack N | Benign N | Latency ms |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row.suite} | {row.defense} | {pct(row.ir)} | {pct(row.fpr_proxy)} | "
            f"{pct(row.acc_proxy)} | {row.n_security} | {row.n_utility} | {row.latency_ms:.1f} |"
        )
    lines.extend(
        [
            "",
            "## AgentDojo Native Metrics",
            "",
            "| Suite | Defense | Attack | Model | Security Rate | ASR | Utility | Injection Utility | N | Latency ms | Status |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row.suite} | {row.defense} | {row.attack} | {row.model} | {pct(row.security_rate)} | "
            f"{pct(row.attack_success_rate)} | {pct(row.utility_rate)} | {pct(row.injection_task_utility_rate)} | "
            f"{row.n_security} | {row.latency_ms:.1f} | {row.status} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Security Rate is AgentDojo's official `security_results` success rate; higher means better defense.",
            "- ASR is `1 - Security Rate`.",
            "- WAMI-style IR is mapped from Security Rate.",
            "- FPR proxy is `1 - Utility Rate`; this is a task-level false-positive proxy, not a per-sample classifier FPR.",
            "- ACC proxy combines attack security successes and benign utility successes.",
            "- This is an official AgentDojo harness run, not the converted-trajectory adaptation.",
        ]
    )
    return "\n".join(lines)


def write_outputs(rows: list[Row], md_path: Path, csv_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(format_table(rows) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Row.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


if __name__ == "__main__":
    main()
