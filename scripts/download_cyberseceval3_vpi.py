from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ID = "facebook/cyberseceval3-visual-prompt-injection"


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a capped CyberSecEval3 VPI subset.")
    parser.add_argument("--out", default="data/cyberseceval3_vpi")
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    try:
        from huggingface_hub import hf_hub_download
    except ImportError as exc:
        raise SystemExit("Install huggingface_hub first: uv run --with huggingface_hub ...") from exc

    out_dir = Path(args.out)
    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"repo={REPO_ID}")
    print(f"out={out_dir.resolve()}")
    print(f"limit={args.limit}")

    test_cases_path = Path(
        hf_hub_download(
            repo_id=REPO_ID,
            repo_type="dataset",
            filename="test_cases.json",
            local_dir=out_dir,
        )
    )
    records = json.loads(test_cases_path.read_text(encoding="utf-8"))
    if isinstance(records, dict):
        records = records.get("test_cases") or records.get("data") or list(records.values())
    selected = records[: args.limit]

    downloaded = 0
    for item in selected:
        image_id = int(item["id"])
        filename = f"images/{image_id}.png"
        target = images_dir / f"{image_id}.png"
        if target.exists():
            downloaded += 1
            continue
        hf_hub_download(
            repo_id=REPO_ID,
            repo_type="dataset",
            filename=filename,
            local_dir=out_dir,
        )
        if target.exists():
            downloaded += 1
        else:
            print(f"warning=missing_after_download image_id={image_id}", file=sys.stderr)

    subset_path = out_dir / f"test_cases_first_{len(selected)}.json"
    subset_path.write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"test_cases={test_cases_path}")
    print(f"subset={subset_path}")
    print(f"images_downloaded_or_present={downloaded}")


if __name__ == "__main__":
    main()
