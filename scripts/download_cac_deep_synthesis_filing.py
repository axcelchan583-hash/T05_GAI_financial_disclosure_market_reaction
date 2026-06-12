#!/usr/bin/env python3
"""Download official CAC deep-synthesis algorithm filing list attachments."""

from __future__ import annotations

import csv
import hashlib
import html
import re
from pathlib import Path
from urllib.parse import urljoin

import requests


NOTICE_API = "https://beian.cac.gov.cn/api/notice/list"
ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "raw" / "cac_deep_synthesis_filing"
DOCX_DIR = OUT_DIR / "docx"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Referer": "https://beian.cac.gov.cn/",
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


def batch_order(title: str) -> int:
    zh_digits = {
        "一": 1,
        "二": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
        "十": 10,
    }
    match = re.search(r"第([一二三四五六七八九十]+)批", title)
    if not match:
        return 1
    text = match.group(1)
    if text == "十":
        return 10
    if text.startswith("十"):
        return 10 + zh_digits.get(text[-1], 0)
    if text.endswith("十"):
        return zh_digits.get(text[0], 0) * 10
    if "十" in text:
        left, right = text.split("十", 1)
        return zh_digits.get(left, 1) * 10 + zh_digits.get(right, 0)
    return zh_digits.get(text, 0)


def infer_extension(content: bytes) -> str:
    if content[:4] == b"%PDF":
        return ".pdf"
    if content[:4] == b"PK\x03\x04":
        return ".docx"
    return ".bin"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def notice_pages() -> list[dict[str, str]]:
    response = requests.get(NOTICE_API, headers=HEADERS, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if payload.get("errno") != 0:
        raise RuntimeError(f"Notice API failed: {payload}")
    rows = []
    for item in payload.get("datas", []):
        title = item.get("title", "")
        if "深度合成服务算法备案信息" not in title:
            continue
        source_url = item.get("content", "").strip()
        if not source_url:
            continue
        rows.append(
            {
                "batch_order": str(batch_order(title)),
                "notice_id": item.get("noticeId", ""),
                "notice_title": title,
                "notice_create_time": item.get("createTime", ""),
                "source_page_url": source_url.replace("http://", "https://"),
            }
        )
    return sorted(rows, key=lambda row: int(row["batch_order"]))


def extract_attachment_link(page_html: str, source_url: str) -> dict[str, str]:
    pattern = re.compile(r'<a\s+[^>]*href="([^"]*downloadfile\.jsp[^"]*)"[^>]*>(.*?)</a>', re.S)
    matches = []
    for match in pattern.finditer(page_html):
        href = match.group(1).replace("&amp;", "&")
        label = clean_label(match.group(2))
        if "境内深度合成服务算法备案清单" not in label:
            continue
        matches.append(
            {
                "label": label,
                "batch": batch_from_label(label),
                "url": urljoin(source_url, href),
            }
        )
    if len(matches) != 1:
        raise RuntimeError(f"Expected one deep-synthesis attachment on {source_url}, got {len(matches)}")
    return matches[0]


def main() -> None:
    DOCX_DIR.mkdir(parents=True, exist_ok=True)
    pages = notice_pages()
    if not pages:
        raise RuntimeError("No CAC deep-synthesis filing notice pages found.")

    manifest_rows = []
    for order, page_item in enumerate(pages, start=1):
        source_url = page_item["source_page_url"]
        page = requests.get(source_url, headers={**HEADERS, "Referer": source_url}, timeout=30)
        page.raise_for_status()
        attachment = extract_attachment_link(page.text, source_url)

        response = requests.get(attachment["url"], headers={**HEADERS, "Referer": source_url}, timeout=60)
        response.raise_for_status()
        extension = infer_extension(response.content)
        filename = f"{order:02d}_{attachment['batch']}_{safe_name(attachment['label'])}{extension}"
        out_path = DOCX_DIR / filename
        out_path.write_bytes(response.content)

        manifest_rows.append(
            {
                **page_item,
                **attachment,
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
                "batch_order",
                "batch",
                "notice_id",
                "notice_title",
                "notice_create_time",
                "source_page_url",
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
                "# CAC Deep-Synthesis Algorithm Filing Attachments",
                "",
                f"Notice API: {NOTICE_API}",
                "",
                "Downloaded official domestic deep-synthesis service algorithm filing list attachments linked from CAC notices.",
                "",
                "Contents:",
                "",
                "- `docx/`: original Office attachments from CAC notice pages",
                "- `attachments_manifest.csv`: notice pages, attachment URLs, local paths, file sizes, and SHA-256 hashes",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Downloaded {len(manifest_rows)} attachments into {OUT_DIR}")


if __name__ == "__main__":
    main()
