from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "data" / "method_audit_excels"


def main() -> None:
    rows = []
    for path in sorted(DIR.glob("*.xlsx")):
        try:
            summary = pd.read_excel(path, sheet_name="Summary")
            sheets = pd.ExcelFile(path).sheet_names
            rows.append(
                {
                    "file": path.name,
                    "summary_rows": len(summary),
                    "sheets": ", ".join(sheets),
                }
            )
        except Exception as exc:
            rows.append({"file": path.name, "summary_rows": "ERROR", "sheets": str(exc)})
    report = pd.DataFrame(rows)
    report.to_csv(DIR / "audit_excel_verification.csv", index=False, encoding="utf-8-sig")
    print(report.to_string(max_colwidth=120, index=False))


if __name__ == "__main__":
    main()
