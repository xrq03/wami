from __future__ import annotations

import importlib
import json
from pathlib import Path
import sys
import traceback


OFFICIAL_BASELINES = [
    {
        "name": "Erase-and-Check",
        "repo": "https://github.com/aounon/certified-llm-safety",
        "path": "external/certified-llm-safety",
        "imports": [("defenses", "erase_and_check")],
        "runtime_requirements": [
            "A safety filter: Llama-2/3, GPT-3.5, or trained DistilBERT classifier",
            "Tokenizer compatible with the safety filter",
            "Optional official DistilBERT weights from the authors' Dropbox link",
            "GPU recommended by the official README",
        ],
    },
    {
        "name": "SmoothLLM",
        "repo": "https://github.com/arobey1/smooth-llm",
        "path": "external/smooth-llm",
        "imports": [("lib.perturbations", "RandomSwapPerturbation")],
        "runtime_requirements": [
            "Vicuna or Llama-2 weights configured in lib/model_configs.py",
            "llm-attacks / FastChat stack required by the official experiment runner",
            "GPU for local target-model inference",
        ],
    },
    {
        "name": "ToolEmu",
        "repo": "https://github.com/ryoungj/ToolEmu",
        "path": "external/ToolEmu",
        "imports": [("toolemu", None)],
        "runtime_requirements": [
            "PromptCoder/procoder from https://github.com/dhh1995/PromptCoder",
            "ToolEmu Python dependencies such as langchain==0.0.277, transformers, torch, openai, anthropic",
            "OPENAI_API_KEY or ANTHROPIC_API_KEY for official emulation/evaluation",
            "Its own ToolEmu benchmark assets, not a direct InjecAgent/BIPIA drop-in defense",
        ],
    },
    {
        "name": "PromptCoder dependency for ToolEmu",
        "repo": "https://github.com/dhh1995/PromptCoder",
        "path": "external/PromptCoder",
        "imports": [("procoder", None)],
        "runtime_requirements": ["Installed or on PYTHONPATH before running ToolEmu"],
    },
]


def main() -> None:
    results = []
    root = Path.cwd()
    for item in OFFICIAL_BASELINES:
        repo_path = root / item["path"]
        if repo_path.exists():
            sys.path.insert(0, str(repo_path))
    for item in OFFICIAL_BASELINES:
        repo_path = root / item["path"]
        entry = dict(item)
        entry["exists"] = repo_path.exists()
        entry["import_results"] = []
        for module_name, attr in item["imports"]:
            try:
                module = importlib.import_module(module_name)
                if attr is not None and not hasattr(module, attr):
                    raise AttributeError(f"{module_name}.{attr} not found")
                entry["import_results"].append({"module": module_name, "attr": attr, "ok": True, "error": ""})
            except Exception as exc:
                entry["import_results"].append(
                    {
                        "module": module_name,
                        "attr": attr,
                        "ok": False,
                        "error": f"{type(exc).__name__}: {exc}",
                        "trace": traceback.format_exc(limit=2),
                    }
                )
        entry["ready_for_official_table2"] = entry["exists"] and all(r["ok"] for r in entry["import_results"])
        results.append(entry)

    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    json_path = out_dir / "official_baseline_status.json"
    md_path = out_dir / "official_baseline_status.md"
    json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(_format_markdown(results), encoding="utf-8")
    print(_format_markdown(results))
    print(f"\nsaved json to {json_path}")
    print(f"saved markdown to {md_path}")


def _format_markdown(results: list[dict]) -> str:
    lines = [
        "# Official Baseline Status",
        "",
        "| Method | Official Repo | Local Path | Import Status | Ready for Official Table 2 | Missing Runtime Pieces |",
        "|---|---|---|---|---|---|",
    ]
    for item in results:
        import_status = "; ".join(
            f"{res['module']}={'ok' if res['ok'] else res['error']}" for res in item["import_results"]
        )
        missing = "<br>".join(item["runtime_requirements"])
        ready = "yes" if item["ready_for_official_table2"] else "no"
        lines.append(
            f"| {item['name']} | {item['repo']} | {item['path']} | {import_status} | {ready} | {missing} |"
        )
    lines.extend(
        [
            "",
            "Note: `Ready for Official Table 2` here only means the official code can be imported locally.",
            "A faithful result still requires the official model weights, API keys, and benchmark protocol listed above.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
