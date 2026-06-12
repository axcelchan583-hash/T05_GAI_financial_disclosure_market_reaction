#!/usr/bin/env python3
"""Build a v3.3 LLM-coding batch for filing-recall candidates outside v56."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path


BASE = Path("/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction")
PROMPT_MD = BASE / "docs/prompts/57_genai_announcement_llm_precoding_prompt_v3_3_20260612.md"
V62_CANDIDATES = BASE / "results/v62_filing_recall_probe_20260612/filing_recall_candidates.csv"
DEFAULT_OUT_DIR = BASE / "results/v62_filing_eventlike_v3_3_20260612"

sys.path.insert(0, str(BASE / "scripts"))
from build_v55_v36_missing_v3_3_batch_20260612 import (  # noqa: E402
    BOUNDARY_TERMS,
    FIRSTNESS_TERMS,
    GENAI_TERMS,
    LEGAL_TERMS,
    clean,
    extract_system_prompt,
    keyword_windows,
    normalize_text,
)

FILING_TERMS = [
    "备案",
    "备案通过",
    "通过备案",
    "备案成功",
    "已备案",
    "完成备案",
    "算法备案",
    "大模型备案",
    "备案号",
    "网信办",
    "国家互联网信息办公室",
    "生成式人工智能服务备案",
    "生成式人工智能服务登记",
    "深度合成服务算法备案",
    "备案许可",
    "备案资格",
    "备案审核",
    "备案中",
    "申报",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return [{k: clean(v) for k, v in row.items()} for row in csv.DictReader(f)]


def truthy(value: object) -> bool:
    return clean(value).lower() in {"true", "1", "yes", "y"}


def filing_status(text: str) -> str:
    text = normalize_text(text)
    if re.search(r"备案通过|通过.{0,8}备案|备案成功|已.{0,8}备案|完成.{0,8}备案|获.{0,8}备案|取得.{0,8}备案|备案号|备案许可|备案资格|备案审核|告知书|双备案", text):
        return "passed_or_obtained"
    if re.search(r"申报.{0,8}备案|拟.{0,8}备案|备案中|推进.{0,8}备案|尚处于备案|进入备案审核", text):
        return "pending_or_applying"
    if re.search(r"备案评测|协助完成.{0,10}备案", text):
        return "service_or_testing"
    return "unclear"


def build_case(idx: int, row: dict[str, str]) -> tuple[dict[str, object], dict[str, str]]:
    case_id = f"V62F_{idx:05d}"
    title = clean(row.get("announcement_title"))
    matched_window = clean(row.get("matched_filing_window"))
    text_parts = [
        title,
        clean(row.get("short_title")),
        matched_window,
        clean(row.get("action_snippet")),
        clean(row.get("announcement_content")),
    ]
    analysis_text = normalize_text("\n\n".join(part for part in text_parts if part))
    if not analysis_text:
        analysis_text = title

    status = filing_status(matched_window or analysis_text)
    case: dict[str, object] = {
        "id": case_id,
        "announcement_id": clean(row.get("announcement_id")),
        "date": clean(row.get("announcement_date")),
        "sec_code": clean(row.get("sec_code")),
        "sec_name": clean(row.get("sec_name")),
        "title": title,
        "recall_source": "v62_filing_eventlike_outside_v56",
        "filing_recall_score": clean(row.get("filing_recall_score")),
        "hit_source": clean(row.get("hit_source")),
        "filing_status_rule": status,
        "matched_terms": ";".join(
            x
            for x in [
                clean(row.get("cac_matched_terms")),
                clean(row.get("matched_filing_window"))[:300],
            ]
            if x
        ),
        "old_query_terms": clean(row.get("source_universes")),
        "old_candidate_tier": clean(row.get("candidate_tier")),
        "old_qian_recall_score": clean(row.get("qian_recall_score")),
        "text_source": "v62_cninfo_fulltext_fields",
        "text_char_count": len(analysis_text),
        "filing_windows": keyword_windows(
            analysis_text,
            FILING_TERMS,
            radius=360,
            max_windows=8,
            max_snippet_chars=1200,
        ),
        "genai_keyword_windows": keyword_windows(
            analysis_text,
            GENAI_TERMS + FILING_TERMS,
            radius=300,
            max_windows=8,
            max_snippet_chars=1100,
        ),
        "legal_commitment_windows": keyword_windows(
            analysis_text,
            LEGAL_TERMS + BOUNDARY_TERMS + FILING_TERMS,
            radius=360,
            max_windows=8,
            max_snippet_chars=1100,
        ),
        "boundary_windows": keyword_windows(
            analysis_text,
            BOUNDARY_TERMS,
            radius=520,
            max_windows=6,
            max_snippet_chars=1200,
        ),
        "firstness_windows": keyword_windows(
            analysis_text,
            FIRSTNESS_TERMS,
            radius=360,
            max_windows=4,
            max_snippet_chars=900,
        ),
    }
    if not any(case["genai_keyword_windows"]):
        case["fallback_context"] = analysis_text[:2200]

    manifest = {
        "id": case_id,
        "announcement_id": clean(row.get("announcement_id")),
        "focal_code": clean(row.get("sec_code")),
        "focal_name": clean(row.get("sec_name")),
        "event_date": clean(row.get("announcement_date")),
        "announcement_title": title,
        "filing_status_rule": status,
        "filing_recall_score": clean(row.get("filing_recall_score")),
        "hit_source": clean(row.get("hit_source")),
        "cac_model_or_entity_window_hit": clean(row.get("cac_model_or_entity_window_hit")),
        "cac_matched_terms": clean(row.get("cac_matched_terms")),
        "source_universes": clean(row.get("source_universes")),
        "text_source": str(case["text_source"]),
        "text_char_count": str(case["text_char_count"]),
        "pdf_url": clean(row.get("pdf_url")),
    }
    return case, manifest


def build_web_prompt_lines(system_prompt: str, cases: list[dict[str, object]]) -> list[str]:
    lines = [
        "# DeepSeek v3.3 filing-recall announcement-coding prompt",
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


def write_batch(
    out_dir: Path,
    cases: list[dict[str, object]],
    manifest_rows: list[dict[str, str]],
    system_prompt: str,
    chunk_size: int,
) -> None:
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

    status_counts = Counter(row["filing_status_rule"] for row in manifest_rows)
    char_count = sum(len(json.dumps(c, ensure_ascii=False)) for c in cases) + len(system_prompt)
    summary = [
        "# v62 filing-recall v3.3 batch",
        "",
        f"cases: {len(cases)}",
        f"approx_chars: {char_count}",
        f"rough_input_tokens: {round(char_count * 0.9)} - {round(char_count * 1.2)}",
        "",
        "filing_status_rule_counts:",
    ]
    summary.extend(f"- `{k}`: {v}" for k, v in sorted(status_counts.items()))
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
    parser.add_argument("--all-high-precision", action="store_true")
    args = parser.parse_args()

    rows = read_csv(V62_CANDIDATES)
    if args.all_high_precision:
        selected = [row for row in rows if truthy(row.get("high_precision_outside_v56"))]
    else:
        selected = [row for row in rows if truthy(row.get("eventlike_outside_v56"))]
    if args.limit is not None:
        selected = selected[: args.limit]

    cases: list[dict[str, object]] = []
    manifest_rows: list[dict[str, str]] = []
    for idx, row in enumerate(selected, 1):
        case, manifest = build_case(idx, row)
        cases.append(case)
        manifest_rows.append(manifest)

    system_prompt = extract_system_prompt(PROMPT_MD)
    write_batch(args.out_dir, cases, manifest_rows, system_prompt, args.chunk_size)


if __name__ == "__main__":
    main()
