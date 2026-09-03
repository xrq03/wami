from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ExperimentItem:
    experiment: str
    item: str
    implementation: str
    status: str
    output: str
    command: tuple[str, ...]
    missing: str
    note: str


def py(*args: str) -> tuple[str, ...]:
    return (sys.executable, *args)


ITEMS: tuple[ExperimentItem, ...] = (
    ExperimentItem(
        "Table 1",
        "WAMI on InjecAgent/BIPIA",
        "Paper-faithful MINE/world-model ensemble over official converted datasets",
        "implemented",
        "data/paper_mine_ensemble_sourceaware_triplet_taua45_taub50_results.md",
        py(
            "scripts/run_paper_mine_ensemble.py",
            "--model-a",
            "wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt",
            "--model-b",
            "wami_paper_mine_triplet_slot_seed4071_e4_cuda.pt",
            "--test-data",
            "data/injecagent_wami.jsonl",
            "--test-data",
            "data/bipia_wami.jsonl",
            "--test-data",
            "data/agentdojo_wami.jsonl",
            "--tau-a",
            "-4.5",
            "--tau-b",
            "-5.0",
            "--output-md",
            "data/paper_mine_ensemble_sourceaware_triplet_taua45_taub50_results.md",
            "--output-csv",
            "data/paper_mine_ensemble_sourceaware_triplet_taua45_taub50_results.csv",
        ),
        "",
        "This is the current most faithful WAMI run without direct hard-rule vetoes.",
    ),
    ExperimentItem(
        "Table 1",
        "GuardReasoner-VL baseline",
        "",
        "blank",
        "",
        (),
        "GuardReasoner-VL weights/runtime or API, exact prompt, and benchmark adapter.",
        "Leave blank until the official model/runtime is supplied.",
    ),
    ExperimentItem(
        "Table 1",
        "WebAgentGuard baseline",
        "Paper-method local proxy exists",
        "partial",
        "data/webagentguard_paper_method_sample.md",
        py(
            "scripts/run_webagentguard_paper_method.py",
            "--limit-attack",
            "10",
            "--limit-benign",
            "10",
            "--output-md",
            "data/webagentguard_paper_method_sample.md",
            "--output-csv",
            "data/webagentguard_paper_method_sample.csv",
        ),
        "Official WebAgentGuard checkpoint or exact reasoning guard prompt/model for strict reproduction.",
        "Current code can run a method-shaped proxy, not the official baseline.",
    ),
    ExperimentItem(
        "Table 1",
        "AgentDojo official replacement for BookAgent",
        "AgentDojo original benchmark harness with official defenses",
        "implemented-official-smoke",
        "data/agentdojo_official_spotlighting_workspace_2x2.md",
        py(
            "scripts/run_agentdojo_official_table1.py",
            "--suite",
            "workspace",
            "--user-task",
            "user_task_0",
            "--user-task",
            "user_task_1",
            "--injection-task",
            "injection_task_0",
            "--injection-task",
            "injection_task_1",
            "--defense",
            "spotlighting_with_delimiting",
            "--attack",
            "injecagent",
            "--output-md",
            "data/agentdojo_official_spotlighting_workspace_2x2.md",
            "--output-csv",
            "data/agentdojo_official_spotlighting_workspace_2x2.csv",
        ),
        "For full official AgentDojo reproduction, expand beyond workspace 2x2 to all selected suites/user tasks/injection tasks and decide which official metric maps into Table 1.",
        "This is now an official AgentDojo harness smoke/small run, not the converted-trajectory adaptation.",
    ),
    ExperimentItem(
        "Table 2",
        "No Defense",
        "Metric baseline",
        "implemented",
        "data/table2_lite_results.md",
        py(
            "scripts/run_table2.py",
            "--limit",
            "0",
            "--output-md",
            "data/table2_lite_results.md",
            "--output-csv",
            "data/table2_lite_results.csv",
        ),
        "",
        "No Defense is deterministic and needs no external model.",
    ),
    ExperimentItem(
        "Table 2",
        "Erase-and-Check",
        "Qwen/API compatible official-style runner",
        "partial",
        "data/table2_official_erase_check_qwen_max_raw.md",
        py(
            "scripts/run_table2_official_erase_check.py",
            "--limit",
            "100",
            "--output-md",
            "data/table2_official_erase_check_qwen_max_raw.md",
            "--output-csv",
            "data/table2_official_erase_check_qwen_max_raw.csv",
        ),
        "API model/base URL/key and exact mask/reconstruction settings if strict Erase-and-Check is required.",
        "Runnable when API configuration is present; capped by default to protect tokens.",
    ),
    ExperimentItem(
        "Table 2",
        "SmoothVLM",
        "SmoothLLM/SmoothVLM-style runner",
        "partial",
        "data/smoothllm_qwen_judge_random50.md",
        py(
            "scripts/run_official_smoothllm.py",
            "--limit",
            "50",
            "--output-md",
            "data/smoothllm_qwen_judge_random50.md",
            "--output-csv",
            "data/smoothllm_qwen_judge_random50.csv",
        ),
        "Official SmoothVLM visual perturbation code/model for strict multimodal reproduction.",
        "Current runner is a compatible approximation unless official SmoothVLM assets are supplied.",
    ),
    ExperimentItem(
        "Table 2",
        "ToolEmu-Sandbox",
        "Placeholder runner",
        "blank",
        "",
        (),
        "ToolEmu official runtime, sandbox LLM/API, tool environment adapter, and scoring config.",
        "Do not fill numbers until the official ToolEmu harness is executable.",
    ),
    ExperimentItem(
        "Table 2",
        "Llama-Guard 3 8B",
        "",
        "blank",
        "",
        (),
        "Llama-Guard 3 8B weights or endpoint, tokenizer, GPU inference config, and score-to-decision mapping.",
        "Left blank because the user previously asked to skip Llama-Guard 3.",
    ),
    ExperimentItem(
        "Table 3",
        "Cross-backbone GPT-4V",
        "",
        "blank",
        "",
        (),
        "GPT-4V-compatible API, exact agent prompt, and generated action trajectories.",
        "WAMI can evaluate trajectories after the backbone produces them.",
    ),
    ExperimentItem(
        "Table 3",
        "Cross-backbone Llama-3-8B",
        "",
        "blank",
        "",
        (),
        "Llama-3-8B or multimodal wrapper endpoint/weights and exact agent prompt.",
        "Needs a backbone trajectory collection run before WAMI scoring.",
    ),
    ExperimentItem(
        "Table 3",
        "Cross-backbone Qwen-VL-Max",
        "Qwen-compatible live/runtime and VPI runners exist",
        "partial",
        "data/current_cyberseceval3_vpi_qwenvl_40.md",
        py(
            "scripts/run_cyberseceval3_vpi_wami_qwenvl.py",
            "--limit",
            "40",
            "--output-md",
            "data/current_cyberseceval3_vpi_qwenvl_40.md",
            "--output-csv",
            "data/current_cyberseceval3_vpi_qwenvl_40.csv",
        ),
        "Qwen-VL-Max API config and exact InjecAgent/BIPIA agent trajectory generation for strict Table 3.",
        "Current Qwen-VL run is multimodal VPI adaptation, not full Table 3.",
    ),
    ExperimentItem(
        "Figure 4",
        "ROC curves",
        "WAMI score export and ROC/threshold files",
        "implemented",
        "data/paper_mine_v3fast_e4_threshold_curve.md",
        py(
            "scripts/export_paper_mine_scores.py",
            "--model",
            "wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt",
            "--test-data",
            "data/injecagent_wami.jsonl",
            "--test-data",
            "data/bipia_wami.jsonl",
            "--test-data",
            "data/agentdojo_wami.jsonl",
            "--output-md",
            "data/paper_mine_v3fast_e4_threshold_curve.md",
            "--output-csv",
            "data/paper_mine_v3fast_e4_scores.csv",
        ),
        "Baseline raw scores for Llama-Guard/ToolEmu/SmoothVLM/Erase are blank until those runs exist.",
        "WAMI ROC is available; baseline ROC rows remain blank.",
    ),
    ExperimentItem(
        "Figure 5",
        "Dynamic threshold sensitivity",
        "Threshold sweep over WAMI scores",
        "implemented",
        "data/current_wami_extra_injecagent_threshold_sensitivity.md",
        py(
            "scripts/run_wami_paper_extra_experiments.py",
            "--data",
            "data/injecagent_wami.jsonl",
            "--model",
            "wami_injecagent_current_e3.npz",
            "--dataset-name",
            "InjecAgent",
            "--out-prefix",
            "data/current_wami_extra_injecagent",
            "--epochs",
            "20",
        ),
        "",
        "Score scale differs from the PDF unless the paper-sized torch model is used.",
    ),
    ExperimentItem(
        "Figure 6",
        "Latency decomposition",
        "TDG/world/MINE component profiler",
        "implemented",
        "data/current_wami_extra_injecagent_latency_breakdown.md",
        py(
            "scripts/run_wami_paper_extra_experiments.py",
            "--data",
            "data/injecagent_wami.jsonl",
            "--model",
            "wami_injecagent_current_e3.npz",
            "--dataset-name",
            "InjecAgent",
            "--out-prefix",
            "data/current_wami_extra_injecagent",
            "--epochs",
            "20",
        ),
        "Comparable GPU/server if the exact 85 ms paper latency is required.",
        "Current local latency is a real measurement but not the same hardware/model scale.",
    ),
    ExperimentItem(
        "Figure 7",
        "VRAM/resource overhead",
        "Local process resource profiler",
        "implemented",
        "data/wami_resource_profile.md",
        py(
            "scripts/run_wami_resource_profile.py",
            "--limit",
            "1000",
            "--output-md",
            "data/wami_resource_profile.md",
            "--output-csv",
            "data/wami_resource_profile.csv",
        ),
        "CUDA memory profiling and baseline model memory require the corresponding GPU models.",
        "This fills WAMI local resource usage; baseline VRAM stays blank until models exist.",
    ),
    ExperimentItem(
        "Table 4",
        "ToolBench/AgentBench capability",
        "Capability proxy and small ToolBench adapter exist",
        "partial",
        "data/table4_capability_proxy.md",
        py(
            "scripts/run_table4_capability_proxy.py",
        ),
        "Official ToolBench/AgentBench harness, base model, tools, scorer, and answer logs.",
        "Proxy can be reported as proxy only; official SR fields must remain blank.",
    ),
    ExperimentItem(
        "Table 5",
        "WAMI ablation",
        "TDG/world/MINE/shadow ablation suite",
        "implemented",
        "data/current_wami_paper_ablation_injecagent.md",
        py(
            "scripts/run_wami_ablation_suite.py",
            "--data",
            "data/injecagent_wami.jsonl",
            "--model",
            "wami_injecagent_current_e3.npz",
            "--dataset-name",
            "InjecAgent",
            "--output-md",
            "data/current_wami_paper_ablation_injecagent.md",
            "--output-csv",
            "data/current_wami_paper_ablation_injecagent.csv",
        ),
        "",
        "For final paper, rerun with one chosen paper-faithful checkpoint and fixed protocol.",
    ),
    ExperimentItem(
        "Figure 8",
        "Shadow adversarial training dynamics",
        "Training-dynamics exporter",
        "implemented",
        "data/current_wami_extra_injecagent_training_dynamics.md",
        py(
            "scripts/run_wami_training_dynamics.py",
            "--data",
            "data/injecagent_wami.jsonl",
            "--epochs",
            "30",
            "--output-md",
            "data/current_wami_extra_injecagent_training_dynamics.md",
            "--output-csv",
            "data/current_wami_extra_injecagent_training_dynamics.csv",
        ),
        "",
        "Uses local WAMI training dynamics; exact paper-sized torch dynamics require the 4-layer/1024 model run.",
    ),
    ExperimentItem(
        "Multimodal extension",
        "CyberSecEval3 VPI/Qwen-VL",
        "Adapted multimodal benchmark runner",
        "partial",
        "data/current_cyberseceval3_vpi_qwenvl_40.md",
        py(
            "scripts/run_cyberseceval3_vpi_wami_qwenvl.py",
            "--limit",
            "40",
            "--output-md",
            "data/current_cyberseceval3_vpi_qwenvl_40.md",
            "--output-csv",
            "data/current_cyberseceval3_vpi_qwenvl_40.csv",
        ),
        "Native BIPIA multimodal images or a paper-native multimodal split.",
        "Useful supporting experiment, but not a native paper Table 1/2 row.",
    ),
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run or document every experiment mentioned in the WAMI paper.")
    parser.add_argument("--execute", action="store_true", help="Run implemented/partial commands that have commands.")
    parser.add_argument("--only", default="", help="Comma-separated experiment labels, e.g. Table 5,Figure 7.")
    parser.add_argument("--skip-api", action="store_true", help="Skip known API/token-consuming partial experiments.")
    parser.add_argument("--output-md", default="data/paper_experiment_matrix.md")
    parser.add_argument("--output-csv", default="data/paper_experiment_matrix.csv")
    args = parser.parse_args()

    selected = select_items(args.only)
    run_rows = []
    if args.execute:
        for item in selected:
            if not item.command:
                run_rows.append((item, "blank", "no command; waiting for missing requirement"))
                continue
            if args.skip_api and may_use_api(item):
                run_rows.append((item, "skipped", "skipped by --skip-api"))
                continue
            code, message = run_command(item.command)
            run_rows.append((item, "ok" if code == 0 else "failed", message))

    write_outputs(selected, run_rows, Path(args.output_md), Path(args.output_csv))
    print(format_markdown(selected, run_rows))
    print(f"\nsaved markdown to {args.output_md}")
    print(f"saved csv to {args.output_csv}")


def select_items(only: str) -> list[ExperimentItem]:
    if not only.strip():
        return list(ITEMS)
    wanted = {part.strip().lower() for part in only.split(",") if part.strip()}
    return [item for item in ITEMS if item.experiment.lower() in wanted or item.item.lower() in wanted]


def may_use_api(item: ExperimentItem) -> bool:
    text = " ".join((item.item, item.implementation, " ".join(item.command))).lower()
    return any(token in text for token in ("qwen", "api", "gpt-4v", "vl", "webagentguard"))


def run_command(command: tuple[str, ...]) -> tuple[int, str]:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    output = (proc.stdout + "\n" + proc.stderr).strip()
    if len(output) > 800:
        output = output[-800:]
    return proc.returncode, output.replace("\n", " | ")


def output_exists(path_text: str) -> bool:
    return bool(path_text) and (ROOT / path_text).exists()


def status_with_file(item: ExperimentItem) -> str:
    if item.status == "blank":
        return "blank"
    return item.status if output_exists(item.output) else f"{item.status}, output missing"


def format_markdown(items: list[ExperimentItem], run_rows: list[tuple[ExperimentItem, str, str]]) -> str:
    run_map = {(row[0].experiment, row[0].item): (row[1], row[2]) for row in run_rows}
    lines = [
        "# Paper Experiment Implementation Matrix",
        "",
        "| Experiment | Item | Status | Output | Missing / Blank To Fill | Note | Run Result |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in items:
        run_status, run_msg = run_map.get((item.experiment, item.item), ("", ""))
        output = f"`{item.output}`" if item.output else ""
        if output and not output_exists(item.output):
            output += " (not generated yet)"
        lines.append(
            "| "
            + " | ".join(
                clean(cell)
                for cell in [
                    item.experiment,
                    item.item,
                    status_with_file(item),
                    output,
                    item.missing,
                    item.note,
                    f"{run_status}: {run_msg}" if run_status else "",
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def clean(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ").strip()


def write_outputs(
    items: list[ExperimentItem],
    run_rows: list[tuple[ExperimentItem, str, str]],
    md_path: Path,
    csv_path: Path,
) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(format_markdown(items, run_rows) + "\n", encoding="utf-8")
    run_map = {(row[0].experiment, row[0].item): (row[1], row[2]) for row in run_rows}
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "experiment",
                "item",
                "implementation",
                "status",
                "output",
                "output_exists",
                "command",
                "missing",
                "note",
                "run_status",
                "run_message",
            ],
        )
        writer.writeheader()
        for item in items:
            run_status, run_message = run_map.get((item.experiment, item.item), ("", ""))
            writer.writerow(
                {
                    "experiment": item.experiment,
                    "item": item.item,
                    "implementation": item.implementation,
                    "status": status_with_file(item),
                    "output": item.output,
                    "output_exists": output_exists(item.output),
                    "command": " ".join(item.command),
                    "missing": item.missing,
                    "note": item.note,
                    "run_status": run_status,
                    "run_message": run_message,
                }
            )


if __name__ == "__main__":
    main()
