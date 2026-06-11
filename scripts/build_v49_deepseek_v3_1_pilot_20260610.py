#!/usr/bin/env python3
"""Build a compact DeepSeek pilot batch for v3.1 GenAI announcement coding."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


BASE = Path("/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction")
MACHINE_CSV = Path("/Users/mac/Documents/Obsidian Vault/23-5/T05_GenAI公告_v3_1_machine.csv")
OUT_DIR = BASE / "results/v49_deepseek_v3_1_pilot_20260610"

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

SYSTEM_PROMPT = """你是严谨的金融/会计研究人工编码员。任务是按 T05 v3.1 规则给中国上市公司 GenAI 公告预编码。你只能根据给定文本判断，不要补充外部知识。

判定码：
A：主样本。首次、可信、公告日可用的 GenAI initiative。
B：真 GenAI，但当前公告日不能用，需要回填更早首次日期。
C：真 GenAI 相关，但非首次，或重复/进展披露。
D-fw：GenAI 话题/框架协议/无实质承诺；保留公告日作 placebo，不进主样本。
D：剔除，非有效 GenAI 行动、泛AI、否认、估值模型、非公司行动等。
U：待定，需要二次核验。

A 类附加字段：
OUT=1：GenAI 相关产出面向外部客户收费、销售或提供服务。
OUT=0：纯内部提效、自用算力储备、生态接入、能力储备等，不直接面对外部客户。
M=own：自己发布、上线、备案、部署。
M=ext：合作、投资、收购、算力承诺等借外力。
R=+：已发布、上线、交付或商业化。
R=-：计划、意向、框架或尚未落地。

合作/框架协议规则：
永远站在公告方判断。合作方有技术不够，必须看到公告方自己的 GenAI 动作或交付物。框架协议三标志中命中两项及以上，通常判 D-fw：1 自称框架性协议/框架协议/意向性文件；2 不涉及具体金额/无需董事会或股东大会审议；3 具体合作、费用、知识产权等另行签约、另行协商或另行确定。若同一公告已披露上线、交付、具体合同、明确金额订单或商业化收入，可以 override 为 A。

投资/增资规则：
只问两个 gate：1 承诺是否真实，正式协议、真金白银、支付安排，业绩对赌/补偿是强信号；2 标的是否明确 GenAI，大模型训练/推理、AIGC 服务、或服务具体大模型公司。两者成立且为首次，判 A | M=ext。参股比例低、不并表、焦点公司主业非 AI 不直接否决。

输出必须是严格 JSON，不要 Markdown。字段：
id, verdict, out, mode, realized, event_date, evidence, reason, uncertainty, review_priority。
out/mode/realized 非 A 类可留空。evidence 摘一句原文或最短关键证据。uncertainty 取 low/medium/high。review_priority 取 must_review/sample_ok。"""


def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def read_rows() -> list[dict[str, str]]:
    with MACHINE_CSV.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_text(path: str, limit: int = 180000) -> str:
    p = Path(clean(path))
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")[:limit]


def normalize_text(text: str) -> str:
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def keyword_windows(
    text: str,
    terms: list[str],
    radius: int = 260,
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

    windows = []
    for start, end, terms_hit in merged[:max_windows]:
        snippet = text[start:end]
        snippet = re.sub(r"\s+", " ", snippet).strip()
        if len(snippet) > max_snippet_chars:
            snippet = snippet[: max_snippet_chars - 1] + "…"
        windows.append(f"[命中: {';'.join(sorted(terms_hit))}] {snippet}")
    return windows


def select_pilot(rows: list[dict[str, str]], limit: int = 18) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    wanted = [
        ("A", 7),
        ("D-fw", 5),
        ("B", 3),
        ("D", 3),
    ]
    for verdict, n in wanted:
        subset = [r for r in rows if clean(r.get("machine_pred_verdict")) == verdict]
        if verdict == "D":
            subset = [r for r in subset if clean(r.get("manual_priority_group")) in {"Q1_reject_qc_sample_frame", "B1_low_priority_frame", ""}]
        selected.extend(subset[:n])
    return selected[:limit]


def build_case(row: dict[str, str]) -> dict[str, object]:
    full_text = read_text(row.get("txt_local_path", ""))
    genai_windows = keyword_windows(full_text, GENAI_TERMS, max_windows=5)
    legal_windows = keyword_windows(full_text, LEGAL_TERMS, max_windows=5)
    priority_evidence = clean(row.get("priority_evidence")) or clean(row.get("metadata_snippet"))

    context = {
        "id": clean(row.get("pack_row_id")),
        "date": clean(row.get("announcement_date")),
        "sec_code": clean(row.get("sec_code")),
        "sec_name": clean(row.get("sec_name")),
        "title": clean(row.get("announcement_title")),
        "category": clean(row.get("primary_pom_like_category")),
        "matched_terms": clean(row.get("matched_genai_terms")) or clean(row.get("query_terms")),
        "machine_pred": clean(row.get("machine_pred_verdict")),
        "machine_reason": clean(row.get("machine_pred_reason")),
        "framework_flags": clean(row.get("framework_flags")),
        "priority_evidence": priority_evidence,
        "genai_keyword_windows": genai_windows,
        "legal_commitment_windows": legal_windows,
    }
    return context


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = read_rows()
    pilot_rows = select_pilot(rows)
    cases = [build_case(r) for r in pilot_rows]

    jsonl_path = OUT_DIR / "deepseek_pilot_cases.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for case in cases:
            user_payload = {
                "instruction": "请按 T05 v3.1 规则预编码这一条公告，只输出严格 JSON。",
                "case": case,
            }
            f.write(json.dumps({"system": SYSTEM_PROMPT, "user": user_payload}, ensure_ascii=False) + "\n")

    combined_path = OUT_DIR / "deepseek_web_prompt_pilot.md"
    lines = build_web_prompt_lines(cases)
    combined_path.write_text("\n".join(lines), encoding="utf-8")

    chunk_paths = []
    chunk_size = 6
    for i in range(0, len(cases), chunk_size):
        chunk = cases[i : i + chunk_size]
        chunk_path = OUT_DIR / f"deepseek_web_prompt_pilot_chunk_{i // chunk_size + 1:02d}.md"
        chunk_path.write_text("\n".join(build_web_prompt_lines(chunk)), encoding="utf-8")
        chunk_paths.append(chunk_path)

    manifest_path = OUT_DIR / "manifest.csv"
    fields = [
        "id",
        "date",
        "sec_code",
        "sec_name",
        "machine_pred",
        "framework_flags",
        "title",
        "category",
    ]
    with manifest_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for case in cases:
            writer.writerow({k: case.get(k, "") for k in fields})

    char_count = sum(len(json.dumps(c, ensure_ascii=False)) for c in cases) + len(SYSTEM_PROMPT)
    summary = [
        "# v49 DeepSeek v3.1 pilot",
        "",
        f"cases: {len(cases)}",
        f"approx_chars: {char_count}",
        f"rough_input_tokens: {round(char_count * 0.9)} - {round(char_count * 1.2)}",
        "",
        "files:",
        f"- {jsonl_path}",
        f"- {combined_path}",
    ]
    summary.extend(f"- {p}" for p in chunk_paths)
    summary.extend(
        [
            f"- {manifest_path}",
            "",
            "note: no DeepSeek API call is made by this script. It builds a compact web/API pilot batch.",
        ]
    )
    (OUT_DIR / "README.md").write_text("\n".join(summary) + "\n", encoding="utf-8")

    print("\n".join(summary))


def build_web_prompt_lines(cases: list[dict[str, object]]) -> list[str]:
    lines = [
        "# DeepSeek v3.1 pilot prompt",
        "",
        "## System / rules",
        "",
        SYSTEM_PROMPT,
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


if __name__ == "__main__":
    main()
