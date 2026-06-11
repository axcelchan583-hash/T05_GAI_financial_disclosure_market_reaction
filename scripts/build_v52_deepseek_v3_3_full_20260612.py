#!/usr/bin/env python3
"""Build the full 1,601-case DeepSeek v3.3 announcement-coding batch."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


BASE = Path("/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction")
DEFAULT_OUT_DIR = BASE / "results/v52_deepseek_v3_3_full1601_20260612"
PROMPT_MD = BASE / "docs/prompts/57_genai_announcement_llm_precoding_prompt_v3_3_20260612.md"

sys.path.insert(0, str(BASE / "scripts"))
from build_v49_deepseek_v3_1_pilot_20260610 import (  # noqa: E402
    LEGAL_TERMS,
    build_case,
    clean,
    keyword_windows,
    normalize_text,
    read_rows,
    read_text,
)


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


def build_v33_case(row: dict[str, str]) -> dict[str, object]:
    case = build_case(row)
    full_text = normalize_text(read_text(row.get("txt_local_path", "")))
    case["boundary_windows"] = keyword_windows(
        full_text,
        BOUNDARY_TERMS,
        radius=520,
        max_windows=6,
        max_snippet_chars=1200,
    )
    case["firstness_windows"] = keyword_windows(
        full_text,
        FIRSTNESS_TERMS,
        radius=360,
        max_windows=4,
        max_snippet_chars=900,
    )
    case["legal_commitment_windows"] = keyword_windows(
        full_text,
        LEGAL_TERMS + BOUNDARY_TERMS,
        radius=320,
        max_windows=7,
        max_snippet_chars=1000,
    )
    return case


def build_web_prompt_lines(system_prompt: str, cases: list[dict[str, object]]) -> list[str]:
    lines = [
        "# DeepSeek v3.3 full announcement-coding prompt",
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
    for case in cases:
        lines.append(json.dumps(case, ensure_ascii=False))
    lines.extend(["```", ""])
    return lines


def write_manifest(out_dir: Path, cases: list[dict[str, object]]) -> None:
    fields = [
        "id",
        "date",
        "sec_code",
        "sec_name",
        "machine_pred",
        "framework_flags",
        "title",
        "category",
        "matched_terms",
    ]
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for case in cases:
            writer.writerow({k: case.get(k, "") for k in fields})


def write_cases(out_dir: Path, cases: list[dict[str, object]], system_prompt: str, chunk_size: int) -> None:
    jsonl_path = out_dir / "deepseek_cases.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for case in cases:
            user_payload = {
                "instruction": "请按 T05 v3.3 规则预编码这一条公告，只输出严格 JSON。",
                "case": case,
            }
            f.write(json.dumps({"system": system_prompt, "user": user_payload}, ensure_ascii=False) + "\n")

    chunk_paths = []
    for i in range(0, len(cases), chunk_size):
        chunk = cases[i : i + chunk_size]
        path = out_dir / f"deepseek_web_prompt_chunk_{i // chunk_size + 1:03d}.md"
        path.write_text("\n".join(build_web_prompt_lines(system_prompt, chunk)), encoding="utf-8")
        chunk_paths.append(path)

    write_manifest(out_dir, cases)

    char_count = sum(len(json.dumps(c, ensure_ascii=False)) for c in cases) + len(system_prompt)
    summary = [
        "# v52 DeepSeek v3.3 full 1,601-case batch",
        "",
        f"cases: {len(cases)}",
        f"approx_chars: {char_count}",
        f"rough_input_tokens: {round(char_count * 0.9)} - {round(char_count * 1.2)}",
        "",
        "files:",
        f"- {jsonl_path}",
        f"- {out_dir / 'manifest.csv'}",
        f"- prompt chunks: {len(chunk_paths)} files",
        "",
        "note: no API call is made by this script.",
    ]
    (out_dir / "README.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--chunk-size", type=int, default=20)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    system_prompt = extract_system_prompt(PROMPT_MD)
    rows = read_rows()
    if args.limit is not None:
        rows = rows[: args.limit]
    cases = [build_v33_case(row) for row in rows]
    write_cases(args.out_dir, cases, system_prompt, args.chunk_size)


if __name__ == "__main__":
    main()

