#!/usr/bin/env python3
"""Extract CAC GenAI service filing tables from downloaded official PDFs."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "cac_genai_service_filing"
MANIFEST = RAW_DIR / "attachments_manifest.csv"
OUT_DIR = ROOT / "data" / "interim"
OUT_CSV = OUT_DIR / "cac_genai_service_filing_records.csv"
SUMMARY_CSV = OUT_DIR / "cac_genai_service_filing_summary_by_batch.csv"


def clean_cell(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    text = text.replace("\u3000", " ")
    text = re.sub(r"\s+", "", text)
    return text.strip()


def page_status(text: str) -> str:
    if "生成式人工智能服务已登记信息" in text:
        return "已登记"
    if "生成式人工智能服务已备案信息" in text:
        return "已备案"
    return ""


def infer_status(filing_no: str, current_status: str) -> str:
    if current_status:
        return current_status
    if re.search(r"\d{8}S\d+", filing_no):
        return "已登记"
    return "已备案"


def load_manifest() -> list[dict[str, str]]:
    with MANIFEST.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def extract_rows(item: dict[str, str]) -> list[dict[str, str]]:
    pdf_path = ROOT / item["pdf_file"]
    rows: list[dict[str, str]] = []

    current_status = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            detected_status = page_status(text)
            if detected_status:
                current_status = detected_status

            for table_no, table in enumerate(page.extract_tables(), start=1):
                if not table:
                    continue
                for row in table[1:]:
                    if not row or len(row) < 6:
                        continue
                    sequence_no = clean_cell(row[0])
                    if not sequence_no.isdigit():
                        continue
                    filing_no = clean_cell(row[4])
                    rows.append(
                        {
                            "status": infer_status(filing_no, current_status),
                            "sequence_no": sequence_no,
                            "jurisdiction": clean_cell(row[1]),
                            "model_name": clean_cell(row[2]),
                            "filing_entity": clean_cell(row[3]),
                            "filing_no": filing_no,
                            "filing_date": clean_cell(row[5]),
                            "source_batch": item["batch"],
                            "source_label": item["label"],
                            "source_url": item["url"],
                            "source_pdf_file": item["pdf_file"],
                            "source_page": page_no,
                            "source_table": table_no,
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
        all_rows.extend(extract_rows(item))

    fields = [
        "status",
        "sequence_no",
        "jurisdiction",
        "model_name",
        "filing_entity",
        "filing_no",
        "filing_date",
        "source_batch",
        "source_label",
        "source_url",
        "source_pdf_file",
        "source_page",
        "source_table",
    ]
    write_csv(OUT_CSV, all_rows, fields)

    summary: dict[tuple[str, str], int] = {}
    for row in all_rows:
        key = (row["source_batch"], row["status"])
        summary[key] = summary.get(key, 0) + 1
    summary_rows = [
        {"source_batch": batch, "status": status, "n": n}
        for (batch, status), n in sorted(summary.items())
    ]
    write_csv(SUMMARY_CSV, summary_rows, ["source_batch", "status", "n"])

    print(f"Extracted {len(all_rows)} records into {OUT_CSV}")


if __name__ == "__main__":
    main()
