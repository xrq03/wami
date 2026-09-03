from __future__ import annotations

from pathlib import Path

import pandas as pd


DIR = Path("data/method_audit_excels")


def main() -> None:
    for path in sorted(DIR.glob("*.xlsx")):
        if path.name.startswith("00_"):
            continue
        summary = pd.read_excel(path, sheet_name="Summary")
        print("---", path.name)
        print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
