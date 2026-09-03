from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import os

from official_env import env_bool, env_int, env_str, load_env_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", default="config/official_baselines.local.env")
    parser.add_argument("--eval-type", choices=["safe", "harmful", "empirical"], default=None)
    parser.add_argument("--num-prompts", type=int, default=None)
    parser.add_argument("--mode", choices=["suffix", "insertion", "infusion"], default=None)
    parser.add_argument("--max-erase", type=int, default=None)
    parser.add_argument("--use-classifier", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_env_file(args.env_file)
    root = Path("external/certified-llm-safety")
    if not root.exists():
        raise SystemExit("missing external/certified-llm-safety; run git clone first")

    use_classifier = args.use_classifier or env_bool("ERASE_CHECK_USE_CLASSIFIER", False)
    cmd = [
        sys.executable,
        "main.py",
        "--num_prompts",
        str(args.num_prompts or env_int("ERASE_CHECK_NUM_PROMPTS", 20)),
        "--eval_type",
        args.eval_type or "safe",
        "--mode",
        args.mode or env_str("ERASE_CHECK_MODE", "suffix"),
        "--max_erase",
        str(args.max_erase or env_int("ERASE_CHECK_MAX_ERASE", 20)),
        "--results_dir",
        "../../data/official_erase_check_results",
    ]
    if use_classifier:
        cmd.extend(["--use_classifier", "--model_wt_path", env_str("ERASE_CHECK_MODEL_WT_PATH")])
    else:
        cmd.extend(["--llm_name", env_str("ERASE_CHECK_LLM_NAME", "GPT-3.5")])

    print(" ".join(cmd))
    if args.dry_run:
        return
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    subprocess.run(cmd, cwd=root, check=True, env=env)


if __name__ == "__main__":
    main()
