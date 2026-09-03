from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

from official_env import env_str, load_env_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", default="config/official_baselines.local.env")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_env_file(args.env_file)
    root = Path("external/smooth-llm")
    if not root.exists():
        raise SystemExit("missing external/smooth-llm; run git clone first")
    _write_model_config(root)

    cmd = [
        sys.executable,
        "main.py",
        "--results_dir",
        _relative_to(root, env_str("SMOOTHLLM_RESULTS_DIR", "./results")),
        "--target_model",
        env_str("SMOOTHLLM_TARGET_MODEL", "llama2"),
        "--attack",
        "GCG",
        "--attack_logfile",
        _relative_to(root, env_str("SMOOTHLLM_ATTACK_LOGFILE", "data/GCG/llama2_behaviors.json")),
        "--smoothllm_pert_type",
        env_str("SMOOTHLLM_PERT_TYPE", "RandomSwapPerturbation"),
        "--smoothllm_pert_pct",
        env_str("SMOOTHLLM_PERT_PCT", "10"),
        "--smoothllm_num_copies",
        env_str("SMOOTHLLM_NUM_COPIES", "10"),
    ]
    print(" ".join(cmd))
    if args.dry_run:
        return
    subprocess.run(cmd, cwd=root, check=True)


def _write_model_config(root: Path) -> None:
    llama_model = env_str("SMOOTHLLM_LLAMA2_MODEL_PATH")
    llama_tok = env_str("SMOOTHLLM_LLAMA2_TOKENIZER_PATH", llama_model)
    vicuna_model = env_str("SMOOTHLLM_VICUNA_MODEL_PATH")
    vicuna_tok = env_str("SMOOTHLLM_VICUNA_TOKENIZER_PATH", vicuna_model)
    config = f"""MODELS = {{
    'llama2': {{
        'model_path': {llama_model!r},
        'tokenizer_path': {llama_tok!r},
        'conversation_template': 'llama-2'
    }},
    'vicuna': {{
        'model_path': {vicuna_model!r},
        'tokenizer_path': {vicuna_tok!r},
        'conversation_template': 'vicuna'
    }}
}}
"""
    (root / "lib" / "model_configs.py").write_text(config, encoding="utf-8")


def _relative_to(root: Path, value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        try:
            return str(path.relative_to(root.resolve()))
        except ValueError:
            return str(path)
    prefix = str(root).replace("\\", "/").rstrip("/") + "/"
    normalized = value.replace("\\", "/")
    return normalized[len(prefix) :] if normalized.startswith(prefix) else value


if __name__ == "__main__":
    main()
