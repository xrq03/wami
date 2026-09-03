from __future__ import annotations

from docx import Document


def main() -> None:
    doc = Document("data/WAMI最终实验结果汇总.docx")
    for idx in [1, 2, 3, 4]:
        print("TABLE", idx)
        table = doc.tables[idx]
        for row in table.rows[-4:]:
            print([cell.text for cell in row.cells])


if __name__ == "__main__":
    main()
