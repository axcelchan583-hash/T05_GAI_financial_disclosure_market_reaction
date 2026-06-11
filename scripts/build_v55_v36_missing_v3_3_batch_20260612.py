#!/usr/bin/env python3
"""Build a v3.3 LLM-coding batch for old v36 first events missing from v52."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path


BASE = Path("/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction")
QIAN_ROOT = Path("/Users/mac/computerscience/23实证选题探索/T05-qian-supplier-replication-cn")
V36_FIRST = QIAN_ROOT / "results/v36_candidate_x_supplier_replication_20260604/v36_candidate_x_first_event_per_firm.csv"
QIAN_PRIORITY = QIAN_ROOT / "results/v27_cninfo_priority_pdf_audit_2023_2026_20260603/manual_review_priority_pdf_all.csv"
V52_CODED = BASE / "results/v53_v52_llm_empirical_tables_20260612/v52_coded_rows_enriched.csv"
PROMPT_MD = BASE / "docs/prompts/57_genai_announcement_llm_precoding_prompt_v3_3_20260612.md"
DEFAULT_OUT_DIR = BASE / "results/v55_v36_missing197_v3_3_20260612"

GENAI_TERMS = [
    "生成式人工智能",
    "生成式AI",
    "AIGC",
    "大模型",
    "大语言模型",
    "ChatGPT",
    "GPT",
    "DeepSeek",
    "讯飞星火",
    "文心",
    "通义",
    "智谱",
    "Kimi",
    "GPU",
    "算力",
    "训练",
    "推理",
]

LEGAL_TERMS = [
    "特别提示",
    "重要提示",
    "风险提示",
    "框架性协议",
    "框架协议",
    "意向性",
    "不涉及具体金额",
    "无需提交董事会",
    "无需提交股东大会",
    "另行签订",
    "另行协商",
    "另行确定",
    "知识产权",
    "费用",
    "合同",
    "金额",
    "上线",
    "发布",
    "交付",
    "商业化",
    "收入",
    "订单",
    "增资协议",
    "支付",
    "业绩承诺",
    "补偿",
]

BOUNDARY_TERMS = [
    "光模块",
    "光芯片",
    "光互联",
    "硅光",
    "CPO",
    "800G",
    "1.6T",
    "AI数据中心",
    "AI 数据中心",
    "智算中心",
    "AI服务器",
    "AI 服务器",
    "GPU",
    "算力集群",
    "高速互联",
    "少数股东权益",
    "少数股东",
    "控股子公司",
    "进一步提升持股比例",
    "前次收购",
    "2023年收购",
    "2023 年收购",
    "51%股权",
    "取得控制权",
]

FIRSTNESS_TERMS = [
    "首次",
    "此前",
    "前次",
    "自公司",
    "以来",
    "进展",
    "延期",
    "补充协议",
    "已披露",
    "已公告",
    "曾",
    "2022",
    "2023",
    "2024",
    "2025",
]


def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_text(text: str) -> str:
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return [{k: clean(v) for k, v in row.items()} for row in csv.DictReader(f)]


def read_text(path: str, limit: int = 180000) -> str:
    path = clean(path)
    if not path:
        return ""
    p = Path(path)
    if not p.exists() or p.is_dir():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")[:limit]


def keyword_windows(
    text: str,
    terms: list[str],
    radius: int = 300,
    max_windows: int = 5,
    max_snippet_chars: int = 900,
) -> list[str]:
    text = normalize_text(text)
    spans: list[tuple[int, int, str]] = []
    for term in terms:
        for m in re.finditer(re.escape(term), text, flags=re.I):
            start = max(0, m.start() - radius)
            end = min(len(text), m.end() + radius)
            spans.append((start, end, term))
    spans.sort(key=lambda x: x[0])

    merged: list[tuple[int, int, set[str]]] = []
    for start, end, term in spans:
        if not merged or start > merged[-1][1] + 120:
            merged.append((start, end, {term}))
        else:
            old_start, old_end, old_terms = merged[-1]
            old_terms.add(term)
            merged[-1] = (old_start, max(old_end, end), old_terms)

    windows: list[str] = []
    for start, end, terms_hit in merged[:max_windows]:
        snippet = re.sub(r"\s+", " ", text[start:end]).strip()
        if len(snippet) > max_snippet_chars:
            snippet = snippet[: max_snippet_chars - 1] + "..."
        windows.append(f"[命中: {';'.join(sorted(terms_hit))}] {snippet}")
    return windows


def extract_system_prompt(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    marker = "## SYSTEM PROMPT"
    start = text.find(marker)
    if start < 0:
        raise RuntimeError(f"Cannot find SYSTEM PROMPT marker in {path}")
    match = re.search(r"```text\n(.*?)\n```", text[start:], flags=re.S)
    if not match:
        raise RuntimeError(f"Cannot find fenced text prompt in {path}")
    return match.group(1).strip()


def resolve_qian_text_path(row: dict[str, str]) -> str:
    txt_file = clean(row.get("txt_file"))
    if not txt_file:
        return ""
    p = Path(txt_file)
    if not p.is_absolute():
        p = QIAN_ROOT / p
    return str(p) if p.exists() else ""


def build_case(
    idx: int,
    v36_row: dict[str, str],
    qian_row: dict[str, str] | None,
) -> tuple[dict[str, object], dict[str, str]]:
    announcement_id = clean(v36_row.get("event_id"))
    case_id = f"V36M_{idx:05d}"
    text_path = resolve_qian_text_path(qian_row or {})
    full_text = normalize_text(read_text(text_path)) if text_path else ""
    qian_context = normalize_text(
        "\n\n".join(
            clean((qian_row or {}).get(k))
            for k in ["action_snippet", "announcement_content", "pdf_genai_context"]
            if clean((qian_row or {}).get(k))
        )
    )
    fallback_context = normalize_text(
        "\n\n".join(
            clean(v36_row.get(k))
            for k in ["llm_evidence", "llm_reason", "backfill_match_reasons", "matched_genai_terms", "fulltext_matched_genai_terms"]
            if clean(v36_row.get(k))
        )
    )
    analysis_text = full_text or qian_context or fallback_context
    if not analysis_text:
        analysis_text = clean(v36_row.get("announcement_title"))

    case: dict[str, object] = {
        "id": case_id,
        "announcement_id": announcement_id,
        "date": clean(v36_row.get("event_date")),
        "sec_code": clean(v36_row.get("focal_code")),
        "sec_name": clean(v36_row.get("focal_name")),
        "title": clean(v36_row.get("announcement_title")),
        "old_sample_source": clean(v36_row.get("sample_source")),
        "old_candidate_row_type": clean(v36_row.get("candidate_row_type")),
        "old_auto_pdf_label": clean(v36_row.get("auto_pdf_label")),
        "old_candidate_tier": clean(v36_row.get("candidate_tier")),
        "old_qian_recall_score": clean(v36_row.get("qian_recall_score")),
        "old_query_terms": clean(v36_row.get("query_terms")),
        "matched_terms": clean(v36_row.get("matched_genai_terms"))
        or clean(v36_row.get("fulltext_matched_genai_terms"))
        or clean(v36_row.get("backfill_matched_keywords")),
        "old_llm_category": clean(v36_row.get("llm_category")),
        "old_llm_reason": clean(v36_row.get("llm_reason")),
        "old_llm_evidence": clean(v36_row.get("llm_evidence")),
        "old_backfill_source_event_id": clean(v36_row.get("backfill_source_event_id")),
        "old_backfill_doc_date": clean(v36_row.get("backfill_doc_date")),
        "old_backfill_match_strength": clean(v36_row.get("backfill_match_strength")),
        "old_backfill_match_score": clean(v36_row.get("backfill_match_score")),
        "qian_action_snippet": clean((qian_row or {}).get("action_snippet")),
        "qian_pdf_genai_context": clean((qian_row or {}).get("pdf_genai_context")),
        "text_source": "qian_txt" if full_text else ("qian_context" if qian_context else ("old_v36_evidence" if fallback_context else "title_only")),
        "text_char_count": len(analysis_text),
        "genai_keyword_windows": keyword_windows(analysis_text, GENAI_TERMS, radius=300, max_windows=6, max_snippet_chars=1000),
        "legal_commitment_windows": keyword_windows(
            analysis_text,
            LEGAL_TERMS + BOUNDARY_TERMS,
            radius=360,
            max_windows=7,
            max_snippet_chars=1000,
        ),
        "boundary_windows": keyword_windows(analysis_text, BOUNDARY_TERMS, radius=520, max_windows=6, max_snippet_chars=1200),
        "firstness_windows": keyword_windows(analysis_text, FIRSTNESS_TERMS, radius=360, max_windows=4, max_snippet_chars=900),
    }
    if not any(case["genai_keyword_windows"]):
        case["fallback_context"] = analysis_text[:2000]

    manifest = {
        "id": case_id,
        "announcement_id": announcement_id,
        "focal_code": clean(v36_row.get("focal_code")),
        "focal_name": clean(v36_row.get("focal_name")),
        "event_date": clean(v36_row.get("event_date")),
        "announcement_title": clean(v36_row.get("announcement_title")),
        "old_sample_source": clean(v36_row.get("sample_source")),
        "old_auto_pdf_label": clean(v36_row.get("auto_pdf_label")),
        "old_candidate_tier": clean(v36_row.get("candidate_tier")),
        "old_llm_category": clean(v36_row.get("llm_category")),
        "text_source": str(case["text_source"]),
        "text_path": text_path,
        "text_char_count": str(case["text_char_count"]),
        "pdf_url": clean(v36_row.get("pdf_url")) or clean((qian_row or {}).get("pdf_url")),
    }
    return case, manifest


def build_web_prompt_lines(system_prompt: str, cases: list[dict[str, object]]) -> list[str]:
    lines = [
        "# DeepSeek v3.3 old-v36-missing announcement-coding prompt",
        "",
        "## System / rules",
        "",
        system_prompt,
        "",
        "## Cases",
        "",
        "请对下面每个 case 分别输出一行严格 JSON。",
        "",
        "```jsonl",
    ]
    lines.extend(json.dumps(case, ensure_ascii=False) for case in cases)
    lines.extend(["```", ""])
    return lines


def write_batch(out_dir: Path, cases: list[dict[str, object]], manifest_rows: list[dict[str, str]], system_prompt: str, chunk_size: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "deepseek_cases.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for case in cases:
            user_payload = {
                "instruction": "请按 T05 v3.3 规则预编码这一条公告，只输出严格 JSON。",
                "case": case,
            }
            f.write(json.dumps({"system": system_prompt, "user": user_payload}, ensure_ascii=False) + "\n")

    chunk_paths: list[Path] = []
    for i in range(0, len(cases), chunk_size):
        chunk = cases[i : i + chunk_size]
        path = out_dir / f"deepseek_web_prompt_chunk_{i // chunk_size + 1:03d}.md"
        path.write_text("\n".join(build_web_prompt_lines(system_prompt, chunk)), encoding="utf-8")
        chunk_paths.append(path)

    manifest_path = out_dir / "manifest.csv"
    fields = list(manifest_rows[0].keys()) if manifest_rows else []
    with manifest_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(manifest_rows)

    text_counts = Counter(row["text_source"] for row in manifest_rows)
    source_counts = Counter(row["old_auto_pdf_label"] for row in manifest_rows)
    char_count = sum(len(json.dumps(c, ensure_ascii=False)) for c in cases) + len(system_prompt)
    summary = [
        "# v55 old-v36-missing v3.3 batch",
        "",
        f"cases: {len(cases)}",
        f"approx_chars: {char_count}",
        f"rough_input_tokens: {round(char_count * 0.9)} - {round(char_count * 1.2)}",
        "",
        "text_source_counts:",
    ]
    summary.extend(f"- `{k}`: {v}" for k, v in sorted(text_counts.items()))
    summary.extend(["", "old_auto_pdf_label_counts:"])
    summary.extend(f"- `{k}`: {v}" for k, v in sorted(source_counts.items()))
    summary.extend(
        [
            "",
            "files:",
            f"- {jsonl_path}",
            f"- {manifest_path}",
            f"- prompt chunks: {len(chunk_paths)} files",
            "",
            "note: no API call is made by this script.",
        ]
    )
    (out_dir / "README.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--chunk-size", type=int, default=20)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    v36_rows = read_csv(V36_FIRST)
    v52_rows = read_csv(V52_CODED)
    qian_rows = read_csv(QIAN_PRIORITY)
    v52_ids = {clean(row.get("announcement_id")) for row in v52_rows if clean(row.get("announcement_id"))}
    qian_by_id: dict[str, dict[str, str]] = {}
    for row in qian_rows:
        qian_by_id.setdefault(clean(row.get("announcement_id")), row)

    missing_rows = [row for row in v36_rows if clean(row.get("event_id")) not in v52_ids]
    if args.limit is not None:
        missing_rows = missing_rows[: args.limit]

    cases: list[dict[str, object]] = []
    manifest_rows: list[dict[str, str]] = []
    for idx, row in enumerate(missing_rows, 1):
        case, manifest = build_case(idx, row, qian_by_id.get(clean(row.get("event_id"))))
        cases.append(case)
        manifest_rows.append(manifest)

    system_prompt = extract_system_prompt(PROMPT_MD)
    write_batch(args.out_dir, cases, manifest_rows, system_prompt, args.chunk_size)


if __name__ == "__main__":
    main()
