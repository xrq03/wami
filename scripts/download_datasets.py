from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import urllib.request
import zipfile


SOURCES = {
    "injecagent": {
        "url": "https://github.com/uiuc-kang-lab/InjecAgent/archive/refs/heads/main.zip",
        "zip": "InjecAgent.zip",
        "dir": "InjecAgent-main",
    },
    "bipia": {
        "url": "https://github.com/microsoft/BIPIA/archive/refs/heads/main.zip",
        "zip": "BIPIA.zip",
        "dir": "BIPIA-main",
    },
    "agentdojo": {
        "url": "https://github.com/ethz-spylab/agentdojo/archive/refs/heads/main.zip",
        "zip": "AgentDojo.zip",
        "dir": "agentdojo-main",
    },
}


def download(name: str, root: Path, force: bool = False) -> Path:
    spec = SOURCES[name]
    root.mkdir(parents=True, exist_ok=True)
    zip_path = root / spec["zip"]
    out_dir = root / spec["dir"]
    if force and out_dir.exists():
        shutil.rmtree(out_dir)
    if force and zip_path.exists():
        zip_path.unlink()
    if not zip_path.exists():
        print(f"downloading {name}: {spec['url']}")
        urllib.request.urlretrieve(spec["url"], zip_path)
    if not out_dir.exists():
        print(f"extracting {zip_path}")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(root)
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="external")
    parser.add_argument("--dataset", choices=["all", "injecagent", "bipia", "agentdojo"], default="all")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = Path(args.root)
    names = ["injecagent", "bipia", "agentdojo"] if args.dataset == "all" else [args.dataset]
    for name in names:
        out = download(name, root, force=args.force)
        print(f"{name} ready at {out}")


if __name__ == "__main__":
    main()
