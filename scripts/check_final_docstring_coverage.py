from __future__ import annotations

import ast
from pathlib import Path


FILES = [
    "scripts/run_bookagent_constraint_verifier.py",
    "scripts/run_guardreasoner_vl_table1.py",
    "scripts/run_llamaguard3_ollama_on_datasets.py",
    "scripts/run_smoothllm_qwen_judge_on_datasets.py",
    "scripts/run_table2_official_erase_check.py",
    "scripts/run_toolemu_sandbox_table2.py",
    "scripts/run_webagentguard_paper_method.py",
    "scripts/generate_self_training_data.py",
    "scripts/run_qwen_live_wami_smoke_stable.py",
    "scripts/run_qwen_full_live_wami_runtime.py",
    "wami/tdg.py",
    "wami/datasets.py",
    "wami/runtime_trace.py",
    "wami/paper_mine_gateway.py",
    "wami/torch_model.py",
    "wami/torch_training.py",
    "wami/evaluate.py",
]


def main() -> None:
    missing = []
    total = 0
    for file_name in FILES:
        tree = ast.parse(Path(file_name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                total += 1
                if ast.get_docstring(node) is None:
                    missing.append(f"{file_name}:{node.lineno}:{node.name}")
    print(f"total={total}")
    print(f"missing={len(missing)}")
    for item in missing:
        print(item)


if __name__ == "__main__":
    main()
