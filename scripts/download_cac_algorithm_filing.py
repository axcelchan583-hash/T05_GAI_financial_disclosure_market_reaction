#!/usr/bin/env python3
"""Download official CAC algorithm filing list attachments.

Source page:
https://www.cac.gov.cn/2022-08/12/c_1661927474338504.htm
"""

from __future__ import annotations

import csv
import hashlib
import html
import re
from pathlib import Path
from urllib.parse import urljoin

import requests


SOURCE_URL = "https://www.cac.gov.cn/2022-08/12/c_1661927474338504.htm"
ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "raw" / "cac_algorithm_filing"
DOCX_DIR = OUT_DIR / "docx"

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
        if "境内互联网信息服务算法备案清单" not in label:
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


def infer_extension(content: bytes) -> str:
    if content[:4] == b"%PDF":
        return ".pdf"
    if content[:4] == b"PK\x03\x04":
        return ".docx"
    return ".bin"


def main() -> None:
    DOCX_DIR.mkdir(parents=True, exist_ok=True)

    page = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    page.raise_for_status()
    (OUT_DIR / "source_page.html").write_text(page.text, encoding="utf-8")

    links = extract_attachment_links(page.text)
    if not links:
        raise RuntimeError("No CAC algorithm filing attachments found.")

    manifest_rows = []
    for order, item in enumerate(links, start=1):
        response = requests.get(item["url"], headers=HEADERS, timeout=60)
        response.raise_for_status()

        extension = infer_extension(response.content)
        filename = f"{order:02d}_{item['batch']}_{safe_name(item['label'])}{extension}"
        out_path = DOCX_DIR / filename
        out_path.write_bytes(response.content)

        manifest_rows.append(
            {
                **item,
                "order": order,
                "file": str(out_path.relative_to(ROOT)),
                "bytes": out_path.stat().st_size,
                "sha256": sha256(out_path),
                "content_type": response.headers.get("content-type", ""),
                "extension": extension,
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
                "file",
                "bytes",
                "sha256",
                "content_type",
                "extension",
            ],
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    readme = OUT_DIR / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# CAC Algorithm Filing Attachments",
                "",
                f"Source page: {SOURCE_URL}",
                "",
                "Downloaded official domestic internet information service algorithm filing list attachments.",
                "",
                "Contents:",
                "",
                "- `docx/`: original attachment files; CAC serves current files as Office documents",
                "- `attachments_manifest.csv`: source URLs, local paths, file sizes, and SHA-256 hashes",
                "- `source_page.html`: archived copy of the source announcement page at download time",
                "",
                "Research use note: these lists are algorithm filing records, not the narrower GenAI service filing registry.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Downloaded {len(manifest_rows)} attachments into {OUT_DIR}")


if __name__ == "__main__":
    main()
