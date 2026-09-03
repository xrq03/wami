"""检查实验文件，并按需从本仓库Release下载WAMI权重。"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ("all", "external", "vpi-images", "wami-main", "wami-live", "legacy")


def safe_target(root: Path, relative: str) -> Path:
    """清单只能引用项目内的普通相对路径。"""
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or ":" in relative or "\\" in relative:
        raise ValueError(f"清单路径不安全：{relative}")
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError(f"清单路径越界：{relative}")
    return target


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_state(path: Path, item: dict, verify_hashes: bool) -> str:
    """存在、长度和可选SHA256都符合才视为资源就绪。"""
    if not path.is_file():
        return "missing"
    if path.stat().st_size != item["bytes"]:
        return "size-mismatch"
    if verify_hashes and sha256(path) != item["sha256"]:
        return "hash-mismatch"
    return "ready"


def download_asset(root: Path, manifest: dict, item: dict) -> None:
    """下载到临时目录，校验通过才写入目标；不覆盖已有权重。"""
    if manifest["repository"] != "xrq03/wami":
        raise ValueError("下载仅允许来自xrq03/wami。")
    target = safe_target(root, item["path"])
    if target.exists():
        raise FileExistsError(f"目标已存在，不覆盖：{target}")
    if item["delivery"] != "release" or target.name != item["path"]:
        raise ValueError("只有清单中的根目录Release权重可以自动下载。")
    gh = shutil.which("gh")
    if not gh:
        raise RuntimeError("请安装GitHub CLI并运行gh auth login，或在Release页面手动下载权重。")
    cache = root / "data" / "runtime-downloads"
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="asset-", dir=cache) as directory:
        subprocess.run([
            gh, "release", "download", manifest["release_tag"], "--repo", manifest["repository"],
            "--pattern", target.name, "--dir", directory,
        ], check=True)
        downloaded = Path(directory) / target.name
        if file_state(downloaded, item, True) != "ready":
            raise ValueError(f"下载校验失败：{target.name}")
        # xb避免另一个进程同时下载时覆盖已经就绪的文件。
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as output, downloaded.open("rb") as source:
            shutil.copyfileobj(source, output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=GROUPS, default="all")
    parser.add_argument("--verify-hashes", action="store_true")
    parser.add_argument("--download", action="store_true", help="仅下载缺失的Release权重，需要GitHub CLI登录。")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "config/runtime_assets.json").read_text(encoding="utf-8"))
    items = [x for x in manifest["files"] if args.group == "all" or x["group"] == args.group]
    if not items:
        raise ValueError("所选资源组为空，无法检查。")
    problems = []
    for item in items:
        target = safe_target(ROOT, item["path"])
        state = file_state(target, item, args.verify_hashes)
        if state == "missing" and args.download and item["delivery"] == "release":
            print(f"下载 {item['path']} ({item['bytes'] / 2**20:.1f} MiB)", flush=True)
            download_asset(ROOT, manifest, item)
            state = file_state(target, item, True)
        if state != "ready":
            problems.append((item["path"], state, item["delivery"]))
    print(f"资源组 {args.group}：{len(items) - len(problems)}/{len(items)} 个文件就绪。")
    for path, state, delivery in problems[:30]:
        print(f"{state}: {path} ({delivery})")
    if len(problems) > 30:
        print(f"另有 {len(problems) - 30} 个文件需要检查。")
    if any(delivery == "release" for _, _, delivery in problems):
        print("缺失权重可加 --download 下载；现有但不匹配的文件不会自动覆盖。")
    print("本检查不安装Python依赖，不检查Ollama模型，也不运行实验。")
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())
