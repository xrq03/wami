from __future__ import annotations

from docx import Document


def main() -> None:
    doc = Document("data/WAMI最终实验结果汇总.docx")
    for i, table in enumerate(doc.tables):
        headers = [cell.text for cell in table.rows[0].cells]
        print(i, len(table.rows), headers[:10])


if __name__ == "__main__":
    main()
