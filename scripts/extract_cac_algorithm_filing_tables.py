#!/usr/bin/env python3
"""Extract CAC algorithm filing tables from downloaded official attachments."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "cac_algorithm_filing"
MANIFEST = RAW_DIR / "attachments_manifest.csv"
OUT_DIR = ROOT / "data" / "interim"
OUT_CSV = OUT_DIR / "cac_algorithm_filing_records.csv"
SUMMARY_CSV = OUT_DIR / "cac_algorithm_filing_summary_by_batch.csv"


def clean_cell(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    text = text.replace("\u3000", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_manifest() -> list[dict[str, str]]:
    with MANIFEST.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def extract_docx_rows(item: dict[str, str]) -> list[dict[str, str]]:
    path = ROOT / item["file"]
    doc = Document(path)
    rows: list[dict[str, str]] = []

    for table_no, table in enumerate(doc.tables, start=1):
        for row_no, row in enumerate(table.rows, start=1):
            cells = [clean_cell(cell.text) for cell in row.cells]
            if len(cells) < 8:
                continue
            sequence_no = cells[0] or str(row_no - 1)
            if "网信算备" not in cells[6]:
                continue
            rows.append(
                {
                    "sequence_no": sequence_no,
                    "algorithm_name": cells[1],
                    "algorithm_type": cells[2],
                    "filing_entity": cells[3],
                    "application_product": cells[4],
                    "main_purpose": cells[5],
                    "record_no": cells[6],
                    "comments": cells[7],
                    "source_batch": item["batch"],
                    "source_label": item["label"],
                    "source_url": item["url"],
                    "source_file": item["file"],
                    "source_table": table_no,
                    "source_row": row_no,
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    all_rows: list[dict[str, str]] = []
    for item in load_manifest():
        if item["extension"] != ".docx":
            raise RuntimeError(f"Unsupported CAC algorithm attachment type: {item['file']}")
        all_rows.extend(extract_docx_rows(item))

    fields = [
        "sequence_no",
        "algorithm_name",
        "algorithm_type",
        "filing_entity",
        "application_product",
        "main_purpose",
        "record_no",
        "comments",
        "source_batch",
        "source_label",
        "source_url",
        "source_file",
        "source_table",
        "source_row",
    ]
    write_csv(OUT_CSV, all_rows, fields)

    summary: dict[tuple[str, str], int] = {}
    for row in all_rows:
        key = (row["source_batch"], row["algorithm_type"])
        summary[key] = summary.get(key, 0) + 1
    summary_rows = [
        {"source_batch": batch, "algorithm_type": algorithm_type, "n": n}
        for (batch, algorithm_type), n in sorted(summary.items())
    ]
    write_csv(SUMMARY_CSV, summary_rows, ["source_batch", "algorithm_type", "n"])

    print(f"Extracted {len(all_rows)} records into {OUT_CSV}")


if __name__ == "__main__":
    main()
