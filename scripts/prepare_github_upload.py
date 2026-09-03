"""在独立克隆目录准备可上传文件；不改原文件，也不执行提交或推送。"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = ("wami", "scripts", "tests")
SOURCE_SUFFIXES = {".py", ".ps1", ".bat", ".sh", ".md"}
DATA_SUFFIXES = {".jsonl", ".json", ".csv", ".md", ".png", ".pdf", ".docx", ".xlsx"}
DATA_SUBDIRS = ("method_audit_excels", "method_audit_excels_expanded")
MAINTENANCE_FILES = {
    "add_chinese_source_guides.py", "add_final_source_docstrings.py",
    "cleanup_english_comment_blocks.py", "restore_code_identifiers_after_comment_cleanup.py",
    "rewrite_final_docstrings_chinese.py",
}
SENSITIVE_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[A-Z0-9]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
LOG_OR_CACHE = re.compile(r"cache|(?:^|[_\-.])(?:log|logs|stdout|stderr|traj)(?:[_\-.]|$)", re.I)


def local_credentials() -> set[str]:
    """只在内存读取本地凭据，用于检查副本，不在报告或终端输出凭据。"""
    found: set[str] = set()
    for path in (ROOT / "config").glob("*.local.*"):
        text = path.read_text(encoding="utf-8-sig")
        if path.suffix == ".json":
            values = json.loads(text)
        else:
            values = dict(line.split("=", 1) for line in text.splitlines()
                          if "=" in line and not line.lstrip().startswith("#"))
        for key, value in values.items():
            if re.search(r"key|token|password|secret", key, re.I) and isinstance(value, str):
                value = value.strip().strip("\"'")
                if len(value) >= 16:
                    found.add(value)
    return found


def sensitive(text: str, credentials: set[str]) -> bool:
    """检查已知本机凭据及常见访问密钥格式，不输出命中原文。"""
    return any(value in text for value in credentials) or any(p.search(text) for p in SENSITIVE_PATTERNS)


def extract_text(path: Path) -> str:
    """提取办公文档中的连续文本，防止跨格式标签分割的密钥漏检。"""
    if path.suffix in {".docx", ".xlsx"}:
        chunks = []
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if name.endswith(".xml"):
                    xml = archive.read(name).decode("utf-8")
                    chunks.extend([xml, "".join(ET.fromstring(xml).itertext())])
        return "\n".join(chunks)
    if path.suffix == ".pdf":
        from pypdf import PdfReader
        return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    if path.suffix == ".png":
        from PIL import Image
        with Image.open(path) as picture:
            return str(picture.info)
    return path.read_text(encoding="utf-8-sig")


def candidates() -> list[Path]:
    """只选择项目文件，不遍历第三方仓库、虚拟环境或模型缓存。"""
    paths = [ROOT / p for p in ("README.md", "pyproject.toml", "requirements.txt", "uv.lock")]
    for folder in SOURCE_DIRS:
        paths.extend(p for p in (ROOT / folder).rglob("*") if p.is_file()
                     and p.suffix in SOURCE_SUFFIXES and "__pycache__" not in p.parts)
    paths.extend((ROOT / "config").glob("*.example.*"))
    paths.extend(p for p in (ROOT / "data").iterdir() if p.is_file() and p.suffix in DATA_SUFFIXES)
    for folder in DATA_SUBDIRS:
        paths.extend((ROOT / "data" / folder).glob("*.xlsx"))
    return sorted(set(paths))


def main() -> None:
    """先完整扫描，记录纳入与排除文件；仅复制通过检查且不会覆盖不同内容的文件。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--copy", action="store_true")
    args = parser.parse_args()
    destination = (ROOT / ".github-upload").resolve()
    if destination.parent != ROOT or not (destination / ".git").is_dir():
        raise SystemExit("必须先在项目下克隆 .github-upload 目录。")
    credentials = local_credentials()
    included, skipped = [], []
    for path in candidates():
        relative = path.relative_to(ROOT).as_posix()
        reason = ""
        if path.name in MAINTENANCE_FILES:
            reason = "一次性源码批处理工具，非实验运行入口"
        elif relative.startswith("data/") and (LOG_OR_CACHE.search(path.stem) or path.name.startswith("~$")):
            reason = "运行日志或缓存"
        elif path.stat().st_size > 90 * 1024 * 1024:
            reason = "超过本次普通 Git 上传单文件预算"
        else:
            try:
                text = extract_text(path)
                if sensitive(text, credentials):
                    reason = "包含凭据格式或本机凭据，未上传原文"
                elif path.suffix == ".py":
                    ast.parse(text, filename=relative)
            except Exception as error:
                reason = "无法完成内容检查: " + type(error).__name__
        if reason:
            skipped.append({"path": relative, "reason": reason})
            continue
        payload = path.read_bytes()
        target = destination / relative
        if args.copy:
            if target.exists() and target.read_bytes() != payload:
                if relative != "README.md" or target.read_text(encoding="utf-8").strip() != "# wami":
                    raise SystemExit("发现不同版本，停止覆盖: " + relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        included.append({"path": relative, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()})
    report = {"included": included, "skipped": skipped, "copied": args.copy}
    report_path = ROOT / "github_upload_report.local.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"included": len(included), "skipped": skipped,
                      "size_mb": round(sum(item["bytes"] for item in included) / 1024**2, 2),
                      "copied": args.copy}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
