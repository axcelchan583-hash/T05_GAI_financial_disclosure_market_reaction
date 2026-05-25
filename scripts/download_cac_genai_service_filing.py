#!/usr/bin/env python3
"""Download official CAC GenAI service filing attachments.

Source page:
https://www.cac.gov.cn/2024-04/02/c_1713729983803145.htm
"""

from __future__ import annotations

import csv
import hashlib
import html
import re
import subprocess
from pathlib import Path
from urllib.parse import urljoin

import requests


SOURCE_URL = "https://www.cac.gov.cn/2024-04/02/c_1713729983803145.htm"
ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "raw" / "cac_genai_service_filing"
PDF_DIR = OUT_DIR / "pdf"
TXT_DIR = OUT_DIR / "txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Referer": SOURCE_URL,
}


def clean_label(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", "", text)
    return text.strip()


def safe_name(text: str) -> str:
    text = re.sub(r"[\\/:*?\"<>|]", "_", text)
    text = re.sub(r"\s+", "_", text)
    return text.strip("_")


def batch_from_label(label: str) -> str:
    match = re.search(r"（(\d{4})年(\d{1,2})月）", label)
    if not match:
        return "unknown"
    year, month = match.groups()
    return f"{year}-{int(month):02d}"


def extract_attachment_links(page_html: str) -> list[dict[str, str]]:
    pattern = re.compile(r'<a\s+[^>]*href="([^"]*downloadfile\.jsp[^"]*)"[^>]*>(.*?)</a>', re.S)
    rows = []
    for idx, match in enumerate(pattern.finditer(page_html), start=1):
        href = match.group(1).replace("&amp;", "&")
        label = clean_label(match.group(2))
        if "生成式人工智能服务" not in label:
            continue
        rows.append(
            {
                "attachment_no": str(idx),
                "batch": batch_from_label(label),
                "label": label,
                "url": urljoin(SOURCE_URL, href),
            }
        )
    return rows


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_to_text(pdf_path: Path, txt_path: Path) -> None:
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), str(txt_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"pdftotext failed for {pdf_path}")


def main() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TXT_DIR.mkdir(parents=True, exist_ok=True)

    page = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    page.raise_for_status()
    (OUT_DIR / "source_page.html").write_text(page.text, encoding="utf-8")

    links = extract_attachment_links(page.text)
    if not links:
        raise RuntimeError("No CAC GenAI service filing attachments found.")

    manifest_rows = []
    for order, item in enumerate(links, start=1):
        filename = f"{order:02d}_{item['batch']}_{safe_name(item['label'])}.pdf"
        pdf_path = PDF_DIR / filename
        txt_path = TXT_DIR / filename.replace(".pdf", ".txt")

        response = requests.get(item["url"], headers=HEADERS, timeout=60)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if b"%PDF" not in response.content[:1024]:
            raise RuntimeError(f"Downloaded file is not a PDF: {item['url']} ({content_type})")
        pdf_path.write_bytes(response.content)
        pdf_to_text(pdf_path, txt_path)

        manifest_rows.append(
            {
                **item,
                "order": order,
                "pdf_file": str(pdf_path.relative_to(ROOT)),
                "txt_file": str(txt_path.relative_to(ROOT)),
                "bytes": pdf_path.stat().st_size,
                "sha256": sha256(pdf_path),
            }
        )

    manifest_path = OUT_DIR / "attachments_manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "order",
                "attachment_no",
                "batch",
                "label",
                "url",
                "pdf_file",
                "txt_file",
                "bytes",
                "sha256",
            ],
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    readme = OUT_DIR / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# CAC GenAI Service Filing Attachments",
                "",
                f"Source page: {SOURCE_URL}",
                "",
                "Downloaded official attachments from the CAC announcement page.",
                "",
                "Contents:",
                "",
                "- `pdf/`: original PDF attachments",
                "- `txt/`: text extracted from the PDFs with `pdftotext -layout`",
                "- `attachments_manifest.csv`: source URLs, local paths, file sizes, and SHA-256 hashes",
                "- `source_page.html`: archived copy of the source announcement page at download time",
                "",
                "Research use note: treat `已备案` and `已登记` as separate statuses. For stricter verification, use `已备案` only.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Downloaded {len(manifest_rows)} attachments into {OUT_DIR}")


if __name__ == "__main__":
    main()
