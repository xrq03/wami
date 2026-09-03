from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import os
import datetime

from official_env import env_int, env_str, load_env_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", default="config/official_baselines.local.env")
    parser.add_argument("--input-path", default="assets/all_cases.json")
    parser.add_argument("--trunc-num", type=int, default=None)
    parser.add_argument("--max-iterations", type=int, default=5)
    parser.add_argument("--simulator-type", default="adv_thought")
    parser.add_argument("--agent-max-tokens", type=int, default=1024)
    parser.add_argument("--simulator-max-tokens", type=int, default=1024)
    parser.add_argument("--evaluator-max-tokens", type=int, default=1024)
    parser.add_argument("--request-timeout", type=int, default=90)
    parser.add_argument("--max-retries", type=int, default=1)
    parser.add_argument("--num-retries", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_env_file(args.env_file)
    root = Path("external/ToolEmu")
    promptcoder = Path("external/PromptCoder").resolve()
    if not root.exists():
        raise SystemExit("missing external/ToolEmu; run git clone first")
    if not promptcoder.exists():
        raise SystemExit("missing external/PromptCoder; run git clone first")

    agent_model = env_str("TOOL_EMU_AGENT_MODEL", "gpt-4")
    simulator_model = env_str("TOOL_EMU_SIMULATOR_MODEL", agent_model)
    evaluator_model = env_str("TOOL_EMU_EVALUATOR_MODEL", agent_model)
    trunc_num = args.trunc_num or env_int("TOOL_EMU_TRUNC_NUM", 3)
    batch_size = str(env_int("TOOL_EMU_BATCH_SIZE", 1))
    python_exe = env_str(
        "TOOL_EMU_PYTHON",
        str((root / ".venv" / "Scripts" / "python.exe").resolve()),
    )
    suffix = datetime.datetime.now().strftime("_wami_%Y_%m_%d__%H_%M_%S")
    dump_dir = "dumps/trajectories"
    output_prefix = (
        f"{dump_dir}/traj_sim_{args.simulator_type}_agent_{agent_model}_naive{suffix}"
    )
    commands = [
        [
            python_exe,
            "scripts/emulate.py",
            "--input-path",
            args.input_path,
            "--agent-model-name",
            agent_model,
            "--simulator-model-name",
            simulator_model,
            "--agent-max-tokens",
            str(args.agent_max_tokens),
            "--simulator-max-tokens",
            str(args.simulator_max_tokens),
            "--agent-request-timeout",
            str(args.request_timeout),
            "--simulator-request-timeout",
            str(args.request_timeout),
            "--agent-max-retries",
            str(args.max_retries),
            "--simulator-max-retries",
            str(args.max_retries),
            "--trunc-num",
            str(trunc_num),
            "--batch-size",
            batch_size,
            "--num-retries",
            str(args.num_retries),
            "--agent-type",
            "naive",
            "--simulator-type",
            args.simulator_type,
            "--max-iterations",
            str(args.max_iterations),
            "--output-file-suffix",
            suffix,
            "--dump-dir",
            dump_dir,
        ],
        [
            python_exe,
            "scripts/evaluate.py",
            "--input-path",
            f"{output_prefix}.jsonl",
            "--eval-type",
            "agent_safe",
            "--evaluator-model-name",
            evaluator_model,
            "--evaluator-max-tokens",
            str(args.evaluator_max_tokens),
            "--evaluator-request-timeout",
            str(args.request_timeout),
            "--evaluator-max-retries",
            str(args.max_retries),
            "--batch-size",
            batch_size,
            "--num-retries",
            str(args.num_retries),
        ],
        [
            python_exe,
            "scripts/helper/read_eval_results.py",
            output_prefix,
        ],
    ]
    for cmd in commands:
        print(" ".join(cmd))
    if args.dry_run:
        return
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    paths = [str(promptcoder), str(root.resolve())]
    env["PYTHONPATH"] = os.pathsep.join(paths + ([existing] if existing else []))
    for cmd in commands:
        subprocess.run(cmd, cwd=root, check=True, env=env)


if __name__ == "__main__":
    main()
