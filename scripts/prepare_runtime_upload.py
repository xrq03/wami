"""为上传副本补齐实验资源；只复制清单内文件，不上传模型服务或凭据。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_github_upload import local_credentials, sensitive

REPOSITORIES = (
    "AgentDojo", "BIPIA-main", "InjecAgent-main", "certified-llm-safety",
    "smooth-llm", "ToolBench", "AgentBench", "ToolEmu", "PromptCoder", "GuardReasoner-VL",
)
SKIP_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".cache", ".pytest_cache",
    "runs", "logs", "results", "results_qwen05b", "notebooks", "wandb",
    "node_modules", ".idea", ".vscode", "checkpoints",
}
TEXT_SUFFIXES = {
    ".py", ".toml", ".yaml", ".yml", ".json", ".jsonl", ".md", ".txt",
    ".csv", ".sh", ".ps1", ".bat", ".j2", ".jinja", ".jinja2", ".cfg",
    ".ini", ".rst", ".typed",
}
WEIGHTS = {
    "wami_paper_mine_sourceaware_recall_seed2061_e4_cuda.pt": "wami-main",
    "wami_paper_mine_triplet_slot_seed4071_e4_cuda.pt": "wami-main",
    "wami_paper_strict_shadowv2_b70_e3_cuda.pt": "wami-live",
    "wami_paper_strict_shadowv3_targeted_e2_cuda.pt": "wami-live",
    "wami_injecagent_final_e5.npz": "legacy",
    "wami_bipia_final_e5.npz": "legacy",
    "wami_agentdojo_final_tuned_e5.npz": "legacy",
}


def file_hash(path: Path) -> str:
    """分块计算校验和，大权重不一次性读入内存。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def external_files():
    """收集运行代码、数据和许可证，排除上游运行记录及论文附件。"""
    for name in REPOSITORIES:
        base = ROOT / "external" / name
        if not base.is_dir():
            raise FileNotFoundError(base)
        for directory, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".hf")]
            parent = Path(directory)
            if name == "GuardReasoner-VL" and "data" in parent.relative_to(base).parts:
                dirs[:] = []
                continue
            for filename in files:
                path = parent / filename
                if path.is_symlink() or not path.resolve().is_relative_to(base.resolve()):
                    continue
                if ".local." in filename or filename.startswith(".env") or "cache" in filename.lower():
                    continue
                if path.suffix.lower() in TEXT_SUFFIXES or filename.upper().startswith(("LICENSE", "COPYING", "NOTICE")):
                    yield path


def source_revision(name: str) -> str | None:
    """记录第三方代码的提交；解压得到的数据目录没有Git版本。"""
    path = ROOT / "external" / name
    if not (path / ".git").exists():
        return None
    return subprocess.check_output(
        ["git", "-c", f"safe.directory={path.as_posix()}", "-C", str(path), "rev-parse", "HEAD"],
        text=True,
    ).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--copy", action="store_true")
    parser.add_argument("--release-tag", default="runtime-assets-20260903")
    args = parser.parse_args()
    destination = ROOT / ".github-upload"
    if not (destination / ".git").is_dir():
        raise SystemExit("请先准备.github-upload仓库副本。")
    credentials = local_credentials()
    records, skipped = [], []
    candidates = [(path, "external", "git") for path in external_files()]
    vpi = ROOT / "data/cyberseceval3_vpi_wami.jsonl"
    images = {json.loads(line)["image"] for line in vpi.read_text(encoding="utf-8-sig").splitlines() if line.strip()}
    candidates.extend((ROOT / image.replace("\\", "/"), "vpi-images", "git") for image in sorted(images))
    candidates.extend((ROOT / name, group, "release" if name.endswith(".pt") else "git") for name, group in WEIGHTS.items())

    # 完成整批检查后才复制，发现目标版本不一致时保留双方文件。
    for path, group, delivery in candidates:
        if not path.is_file() or not path.resolve().is_relative_to(ROOT):
            raise FileNotFoundError(path)
        relative = path.relative_to(ROOT).as_posix()
        if group == "external":
            if path.stat().st_size > 90 * 1024 * 1024:
                raise ValueError(f"普通Git文件过大：{relative}")
            content = path.read_text(encoding="utf-8-sig")
            if sensitive(content, credentials):
                skipped.append({"path": relative, "reason": "凭据检查命中，未复制，不输出原文"})
                continue
        sha = file_hash(path)
        target = destination / relative
        if delivery == "git" and target.exists() and file_hash(target) != sha:
            raise ValueError(f"目标已有不同版本，停止覆盖：{relative}")
        records.append({"path": relative, "group": group, "delivery": delivery,
                        "bytes": path.stat().st_size, "sha256": sha})

    manifest = {
        "repository": "xrq03/wami", "release_tag": args.release_tag,
        "external_revisions": {name: source_revision(name) for name in REPOSITORIES},
        "files": records, "excluded_sensitive_files": skipped,
    }
    if args.copy:
        for item in records:
            if item["delivery"] != "git":
                continue
            target = destination / item["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / item["path"], target)
        for base in (ROOT, destination):
            (base / "config/runtime_assets.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
            )
    print(json.dumps({
        "copy": args.copy, "file_count": len(records),
        "git_mib": round(sum(x["bytes"] for x in records if x["delivery"] == "git") / 2**20, 2),
        "release_mib": round(sum(x["bytes"] for x in records if x["delivery"] == "release") / 2**20, 2),
        "excluded_sensitive_files": skipped,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
