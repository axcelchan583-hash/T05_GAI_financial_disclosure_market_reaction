#!/usr/bin/env python3
"""Build a unified official CAC registry list for GenAI-related sample work."""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "v64_official_registry_master_20260612"

GENAI_SOURCE_URL = "https://www.cac.gov.cn/2024-04/02/c_1713729983803145.htm"
ALGORITHM_SOURCE_URL = "https://www.cac.gov.cn/2022-08/12/c_1661927474338504.htm"
DEEP_SYNTHESIS_NOTICE_API = "https://beian.cac.gov.cn/api/notice/list"

GENAI_RECORDS = ROOT / "data" / "interim" / "cac_genai_service_filing_records.csv"
ALGORITHM_RECORDS = ROOT / "data" / "interim" / "cac_algorithm_filing_records.csv"
DEEP_SYNTHESIS_RECORDS = ROOT / "data" / "interim" / "cac_deep_synthesis_filing_records.csv"
CSMAR_RECORDS = ROOT / "data" / "interim" / "csmar_algorithm_info_records.csv"

GENAI_KEYWORDS = [
    "大模型",
    "生成式",
    "生成",
    "合成",
    "深度合成",
    "AIGC",
    "GPT",
    "ChatGPT",
    "智能体",
    "智能问答",
    "多模态",
    "文本生成",
    "图像生成",
    "图片生成",
    "视频生成",
    "语音生成",
    "数字人",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_space(text: object) -> str:
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def month_from_date(raw: str) -> str:
    raw = normalize_space(raw)
    match = re.search(r"(\d{4})[/-](\d{1,2})", raw)
    if not match:
        return ""
    year, month = match.groups()
    return f"{year}-{int(month):02d}"


def algorithm_relevance(row: dict[str, str]) -> tuple[str, str]:
    text = " ".join(
        normalize_space(row.get(col, ""))
        for col in [
            "algorithm_name",
            "algorithm_type",
            "application_product",
            "main_purpose",
            "comments",
        ]
    )
    reasons: list[str] = []
    algorithm_type = normalize_space(row.get("algorithm_type", ""))
    if "生成" in algorithm_type or "合成" in algorithm_type or "深度合成" in algorithm_type:
        reasons.append("algorithm_type_generation_synthesis")
    hits = [kw for kw in GENAI_KEYWORDS if kw.lower() in text.lower()]
    if hits:
        reasons.append("keyword:" + ";".join(hits[:8]))
    return ("1" if reasons else "0", "|".join(reasons))


def genai_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output = []
    for row in rows:
        filing_date = normalize_space(row.get("filing_date", ""))
        output.append(
            {
                "registry_source": "cac_genai_service",
                "registry_source_label": "生成式人工智能服务备案/登记",
                "source_batch": row.get("source_batch", ""),
                "registry_status": row.get("status", ""),
                "registry_role": "",
                "entity_name": row.get("filing_entity", ""),
                "item_name": row.get("model_name", ""),
                "item_type": "生成式人工智能服务",
                "application_product": "",
                "main_purpose": "",
                "filing_no": row.get("filing_no", ""),
                "filing_date": filing_date,
                "filing_month": month_from_date(filing_date) or row.get("source_batch", ""),
                "date_precision": "day_with_possible_note",
                "jurisdiction": row.get("jurisdiction", ""),
                "comments": "",
                "is_genai_relevant": "1",
                "genai_relevance_reason": "source_is_genai_service_registry",
                "source_label": row.get("source_label", ""),
                "source_url": row.get("source_url", ""),
                "source_file": row.get("source_pdf_file", ""),
                "source_locator": f"page={row.get('source_page', '')};table={row.get('source_table', '')}",
            }
        )
    return output


def algorithm_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output = []
    for row in rows:
        is_relevant, reason = algorithm_relevance(row)
        output.append(
            {
                "registry_source": "cac_algorithm_filing",
                "registry_source_label": "互联网信息服务算法备案",
                "source_batch": row.get("source_batch", ""),
                "registry_status": "备案清单",
                "registry_role": "",
                "entity_name": row.get("filing_entity", ""),
                "item_name": row.get("algorithm_name", ""),
                "item_type": row.get("algorithm_type", ""),
                "application_product": row.get("application_product", ""),
                "main_purpose": row.get("main_purpose", ""),
                "filing_no": row.get("record_no", ""),
                "filing_date": "",
                "filing_month": row.get("source_batch", ""),
                "date_precision": "source_batch_month_only",
                "jurisdiction": "",
                "comments": row.get("comments", ""),
                "is_genai_relevant": is_relevant,
                "genai_relevance_reason": reason,
                "source_label": row.get("source_label", ""),
                "source_url": row.get("source_url", ""),
                "source_file": row.get("source_file", ""),
                "source_locator": f"table={row.get('source_table', '')};row={row.get('source_row', '')}",
            }
        )
    return output


def deep_synthesis_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output = []
    for row in rows:
        output.append(
            {
                "registry_source": "cac_deep_synthesis_filing",
                "registry_source_label": "深度合成服务算法备案",
                "source_batch": row.get("source_batch", ""),
                "registry_status": "备案清单",
                "registry_role": row.get("role", ""),
                "entity_name": row.get("filing_entity", ""),
                "item_name": row.get("algorithm_name", ""),
                "item_type": "深度合成服务算法",
                "application_product": row.get("application_product", ""),
                "main_purpose": row.get("main_purpose", ""),
                "filing_no": row.get("record_no", ""),
                "filing_date": "",
                "filing_month": row.get("source_batch", ""),
                "date_precision": "source_batch_month_only",
                "jurisdiction": "",
                "comments": row.get("comments", ""),
                "is_genai_relevant": "1",
                "genai_relevance_reason": "source_is_deep_synthesis_registry",
                "source_label": row.get("source_label", ""),
                "source_url": row.get("source_url", ""),
                "source_file": row.get("source_file", ""),
                "source_locator": f"table={row.get('source_table', '')};row={row.get('source_row', '')}",
            }
        )
    return output


def csmar_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output = []
    for row in rows:
        is_relevant, reason = algorithm_relevance(row)
        filing_date = normalize_space(row.get("distribution_date", ""))
        output.append(
            {
                "registry_source": "csmar_algorithm_system_snapshot",
                "registry_source_label": "互联网信息服务算法备案系统快照",
                "source_batch": row.get("source_batch", ""),
                "registry_status": "备案系统快照",
                "registry_role": "",
                "entity_name": row.get("filing_entity", ""),
                "item_name": row.get("algorithm_name", ""),
                "item_type": row.get("algorithm_type", ""),
                "application_product": row.get("application_product", ""),
                "main_purpose": row.get("main_purpose", ""),
                "filing_no": row.get("record_no", ""),
                "filing_date": filing_date,
                "filing_month": month_from_date(filing_date) or row.get("source_batch", ""),
                "date_precision": "day",
                "jurisdiction": "",
                "comments": row.get("comments", ""),
                "is_genai_relevant": is_relevant,
                "genai_relevance_reason": reason,
                "source_label": "AI_AlgorithmInfo.xlsx",
                "source_url": "",
                "source_file": f"{row.get('source_zip_basename', '')}/AI_AlgorithmInfo.xlsx",
                "source_locator": f"record_no={row.get('record_no', '')}",
            }
        )
    return output


def build_summary(master: list[dict[str, str]]) -> list[dict[str, object]]:
    counts: Counter[tuple[str, str, str]] = Counter()
    for row in master:
        counts[(row["registry_source"], row["source_batch"], row["is_genai_relevant"])] += 1
    return [
        {
            "registry_source": source,
            "source_batch": batch,
            "is_genai_relevant": relevant,
            "n": n,
        }
        for (source, batch, relevant), n in sorted(counts.items())
    ]


def build_coverage(
    genai: list[dict[str, str]],
    algorithm: list[dict[str, str]],
    deep_synthesis: list[dict[str, str]],
    csmar: list[dict[str, str]] | None = None,
) -> list[dict[str, object]]:
    rows = [
        {
            "source_key": "cac_genai_service",
            "source_name": "CAC GenAI service filing / registration attachments",
            "source_url": GENAI_SOURCE_URL,
            "local_record_file": str(GENAI_RECORDS.relative_to(ROOT)),
            "record_count": len(genai),
            "latest_source_batch": max(row["source_batch"] for row in genai) if genai else "",
            "run_date": date.today().isoformat(),
            "coverage_note": "Official source page had 11 attachments at refresh time; latest attachment was 2026-04, no 2026-06 attachment.",
        },
        {
            "source_key": "cac_algorithm_filing",
            "source_name": "CAC domestic internet information service algorithm filing list attachments",
            "source_url": ALGORITHM_SOURCE_URL,
            "local_record_file": str(ALGORITHM_RECORDS.relative_to(ROOT)),
            "record_count": len(algorithm),
            "latest_source_batch": max(row["source_batch"] for row in algorithm) if algorithm else "",
            "run_date": date.today().isoformat(),
            "coverage_note": "Official source page had 18 ordinary algorithm filing attachments at refresh time; latest attachment was 2026-05, no 2026-06 attachment or attachment 19.",
        },
        {
            "source_key": "cac_deep_synthesis_filing",
            "source_name": "CAC domestic deep-synthesis service algorithm filing list attachments",
            "source_url": DEEP_SYNTHESIS_NOTICE_API,
            "local_record_file": str(DEEP_SYNTHESIS_RECORDS.relative_to(ROOT)),
            "record_count": len(deep_synthesis),
            "latest_source_batch": max(row["source_batch"] for row in deep_synthesis) if deep_synthesis else "",
            "run_date": date.today().isoformat(),
            "coverage_note": "Official notice list had 17 deep-synthesis filing batches at refresh time; latest attachment was 2026-05, no 2026-06 notice.",
        },
    ]
    if csmar is not None:
        rows.append(
            {
                "source_key": "csmar_algorithm_system_snapshot",
                "source_name": "CSMAR local algorithm-info system snapshot",
                "source_url": "",
                "local_record_file": str(CSMAR_RECORDS.relative_to(ROOT)),
                "record_count": len(csmar),
                "latest_source_batch": max(row["source_batch"] for row in csmar) if csmar else "",
                "run_date": date.today().isoformat(),
                "coverage_note": "Local authorized system snapshot from AI_AlgorithmInfo.xlsx; workbook itself is proprietary and not copied into the repo. Latest snapshot batch is used as complete algorithm-registry coverage through that month.",
            }
        )
    return rows


def write_master_outputs(stem: str, master: list[dict[str, str]], fields: list[str]) -> None:
    write_csv(OUT_DIR / f"{stem}.csv", master, fields)
    write_csv(
        OUT_DIR / f"{stem}_genai_relevant_subset.csv",
        [row for row in master if row["is_genai_relevant"] == "1"],
        fields,
    )


def main() -> None:
    genai_raw = read_csv(GENAI_RECORDS)
    algorithm_raw = read_csv(ALGORITHM_RECORDS)
    deep_synthesis_raw = read_csv(DEEP_SYNTHESIS_RECORDS)
    csmar_raw = read_csv(CSMAR_RECORDS) if CSMAR_RECORDS.exists() else None

    master = genai_rows(genai_raw) + algorithm_rows(algorithm_raw) + deep_synthesis_rows(deep_synthesis_raw)
    fields = [
        "registry_source",
        "registry_source_label",
        "source_batch",
        "registry_status",
        "registry_role",
        "entity_name",
        "item_name",
        "item_type",
        "application_product",
        "main_purpose",
        "filing_no",
        "filing_date",
        "filing_month",
        "date_precision",
        "jurisdiction",
        "comments",
        "is_genai_relevant",
        "genai_relevance_reason",
        "source_label",
        "source_url",
        "source_file",
        "source_locator",
    ]
    write_master_outputs("official_registry_master", master, fields)
    # Backward-compatible filename for the main official GenAI-relevant subset.
    write_csv(
        OUT_DIR / "genai_relevant_registry_subset.csv",
        [row for row in master if row["is_genai_relevant"] == "1"],
        fields,
    )
    if csmar_raw is not None:
        latest_csmar_batch = max(row["source_batch"] for row in csmar_raw)
        official_post_csmar = [
            row
            for row in algorithm_rows(algorithm_raw) + deep_synthesis_rows(deep_synthesis_raw)
            if row["source_batch"] > latest_csmar_batch
        ]
        expanded = genai_rows(genai_raw) + csmar_rows(csmar_raw) + official_post_csmar
        write_master_outputs("expanded_registry_master_with_csmar", expanded, fields)
    write_csv(
        OUT_DIR / "summary_by_source_batch.csv",
        build_summary(master),
        ["registry_source", "source_batch", "is_genai_relevant", "n"],
    )
    write_csv(
        OUT_DIR / "coverage_manifest.csv",
        build_coverage(genai_raw, algorithm_raw, deep_synthesis_raw, csmar_raw),
        [
            "source_key",
            "source_name",
            "source_url",
            "local_record_file",
            "record_count",
            "latest_source_batch",
            "run_date",
            "coverage_note",
        ],
    )

    print(f"Wrote {len(master)} registry rows into {OUT_DIR}")
    print(f"Wrote {sum(row['is_genai_relevant'] == '1' for row in master)} GenAI-relevant registry rows")
    if csmar_raw is not None:
        print("Wrote expanded_registry_master_with_csmar.csv using local CSMAR algorithm snapshot")


if __name__ == "__main__":
    main()
