from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    "scripts/run_qwen_full_live_wami_runtime.py",
    "scripts/run_qwen_live_wami_smoke_stable.py",
    "scripts/generate_self_training_data.py",
    "scripts/run_webagentguard_paper_method.py",
    "scripts/run_table2_official_erase_check.py",
    "scripts/run_smoothllm_qwen_judge_on_datasets.py",
    "scripts/run_toolemu_sandbox_table2.py",
    "scripts/run_llamaguard3_ollama_on_datasets.py",
    "scripts/run_bookagent_constraint_verifier.py",
    "scripts/run_guardreasoner_vl_table1.py",
    "wami/tdg.py",
    "wami/runtime_trace.py",
    "wami/paper_mine_gateway.py",
    "wami/torch_model.py",
    "wami/torch_training.py",
    "wami/datasets.py",
    "wami/evaluate.py",
]

ALLOW_TERMS = {
    "WAMI",
    "TDG",
    "MINE",
    "IR",
    "FPR",
    "ACC",
    "API",
    "CSV",
    "JSON",
    "Excel",
    "Ollama",
    "qwen",
    "qwen2",
    "safe",
    "unsafe",
    "block",
    "allow",
    "prompt",
    "plan",
    "agent",
    "baseline",
    "runtime",
    "trace",
    "world",
    "model",
    "latent",
    "live",
    "action",
    "observation",
    "intent",
    "label",
    "Row",
}


def strip_allowed(text: str) -> str:
    out = text
    for term in sorted(ALLOW_TERMS, key=len, reverse=True):
        out = re.sub(rf"\b{re.escape(term)}\b", "", out, flags=re.IGNORECASE)
    return out


def has_unwanted_english(text: str) -> bool:
    return bool(re.search(r"[A-Za-z]{3,}", strip_allowed(text)))


def docstrings(tree: ast.Module):
    if ast.get_docstring(tree, clean=False):
        yield ("module", 1, ast.get_docstring(tree, clean=False) or "")
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc:
                yield (getattr(node, "name", "node"), node.lineno, doc)


def main() -> None:
    problems = []
    for rel in TARGETS:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        for name, line, doc in docstrings(tree):
            if has_unwanted_english(doc):
                problems.append((rel, line, name, doc.splitlines()[0]))
        for idx, line_text in enumerate(text.splitlines(), start=1):
            stripped = line_text.strip()
            if stripped.startswith("#") and has_unwanted_english(stripped):
                problems.append((rel, idx, "comment", stripped))
    print(f"checked={len(TARGETS)}")
    print(f"problems={len(problems)}")
    for rel, line, name, preview in problems[:80]:
        print(f"{rel}:{line}:{name}: {preview}")


if __name__ == "__main__":
    main()
