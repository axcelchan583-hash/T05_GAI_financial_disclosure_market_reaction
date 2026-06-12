#!/usr/bin/env python3
"""Trace CAC registry products back to first firm disclosures.

This run implements the missing product-level bridge after v67/v68:
for each listed firm-product in the official registry master, search local
formal-announcement and interaction/QA corpora for the first mention of the
registered product name, application name, or filing number.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v65_registry_based_event_study_20260612 as v65  # noqa: E402


RUN_ID = "v69_registry_product_traceback_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "129_v69_registry_product_traceback_20260612.md"

V67_MASTER = ROOT / "results/v67_registry_firm_product_master_20260612/registry_firm_product_master.csv"

PROJECT_DATA = Path("/Users/mac/computerscience/第三方资料/04_项目专用资料/T05_GAI_financial_disclosure_market_reaction")
POM_ROOT = PROJECT_DATA / "cninfo_pom_like_active_announcements_20260609"
POM_REVIEW = POM_ROOT / "tables/pom_like_active_announcements_review.csv"
POM_TEXT_DIR = POM_ROOT / "text"

RAW_GENAI_TEXT_DIR = ROOT / "data/raw/cninfo_genai_announcements_20260522/text"

IR_ACTIVITY_ROOT = PROJECT_DATA / "ir_interaction_data_20260519"
CNINFO_IR_ROOT = IR_ACTIVITY_ROOT / "cninfo_ir_activity"
CNINFO_IR_TEXT_DIR = CNINFO_IR_ROOT / "text"
CNINFO_IR_MATCHES = CNINFO_IR_ROOT / "interim/cninfo_ir_activity_full_genai_matches_2023_2026.csv"
CNINFO_IR_SNIPPETS = CNINFO_IR_ROOT / "interim/cninfo_ir_activity_full_genai_sentence_snippets_2023_2026.csv"

CSMAR_EVENT_ROOT = ROOT / "results/csmar_genai_event_library_20260523"
IIP_ANSWER_EVENTS = CSMAR_EVENT_ROOT / "iip_answer_level_genai_events.csv"
IRQA_ANSWER_EVENTS = CSMAR_EVENT_ROOT / "irqa_answer_level_genai_events.csv"

QIAN_RAW_ROOT = Path("/Users/mac/computerscience/23实证选题探索/T05-qian-supplier-replication-cn/data/raw")
EXTRA_CNINFO_TEXT_DIRS = [
    (QIAN_RAW_ROOT / "cninfo_formal_event_rebuild_20260602/text", "cninfo_formal_qian_event_rebuild"),
    (QIAN_RAW_ROOT / "cninfo_priority_pdf_audit_2023_2026_20260603/text", "cninfo_formal_qian_priority_2023_2026"),
    (QIAN_RAW_ROOT / "cninfo_priority_pdf_audit_20260603/text", "cninfo_formal_qian_priority"),
]

CNINFO_NAME_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})_(?P<code>\d{6})_(?P<name>.+?)_(?P<announcement_id>\d{8,})_(?P<title>.+)\.txt$"
)
HTML_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")
SPLIT_RE = re.compile(r"[、,，;；/／|｜\s]+")
BRACKET_RE = re.compile(r"[（(][^（）()]{0,12}?(?:APP|App|app|网站|小程序|其他|应用|平台)[）)]")

CONTEXT_KEYWORDS = [
    "备案",
    "登记",
    "通过",
    "获批",
    "公示",
    "发布",
    "上线",
    "推出",
    "接入",
    "部署",
    "应用",
    "研发",
    "自研",
    "大模型",
    "算法",
]
PRODUCT_MARKERS = [
    "ai",
    "aigc",
    "gpt",
    "llm",
    "deep",
    "sense",
    "大模型",
    "模型",
    "智能",
    "生成",
    "合成",
    "算法",
    "认知",
    "助手",
    "搜索",
    "医生",
    "问答",
    "图像",
    "视频",
    "音乐",
    "语音",
]
ROUTINE_FORMAL_PATTERNS = [
    "年度报告",
    "半年度报告",
    "季度报告",
    "年度股东",
    "股东大会会议",
    "股东会会议",
    "会议资料",
    "会议材料",
    "会议文件",
    "董事会工作报告",
    "监事会工作报告",
    "总经理工作报告",
    "工作报告",
    "财务决算报告",
    "社会责任报告",
    "环境、社会及治理",
    "esg",
    "sustainabilityreport",
    "sustainability report",
    "提质增效重回报",
    "行动方案",
    "现金分红说明会",
    "未弥补亏损",
    "业绩预盈",
    "业绩快报",
    "发行股票预案",
    "向特定对象发行",
    "向不特定对象发行",
    "可转换公司债券",
    "募集说明书",
    "论证分析报告",
    "报告书",
    "草案",
    "审计报告",
    "法律意见书",
]
GENERIC_TERMS = {
    "ai",
    "aigc",
    "gpt",
    "llm",
    "rag",
    "maas",
    "app",
    "chatgpt",
    "deepseek",
    "openai",
    "agent",
    "office",
    "wps",
    "大模型",
    "模型",
    "算法",
    "平台",
    "系统",
    "应用",
    "网站",
    "小程序",
    "人工智能",
    "生成式人工智能",
    "文本生成",
    "图像生成",
    "内容生成",
    "智能体",
}
CORE_SUFFIXES = [
    "生成式人工智能服务",
    "深度合成服务算法",
    "大模型算法",
    "文本生成算法",
    "文本生成类算法",
    "图像生成算法",
    "图像生成类算法",
    "图生文算法",
    "文生图算法",
    "语音生成算法",
    "视频生成算法",
    "对话生成算法",
    "智能对话算法",
    "生成合成类算法",
    "深度合成算法",
    "内容生成算法",
    "生成算法",
    "大模型",
    "算法",
    "模型",
    "系统",
    "平台",
    "应用",
]
ACCEPT_MIN = 60
CORP_SUFFIX_RE = re.compile(
    r"(?:股份有限公司|有限责任公司|集团股份有限公司|集团有限公司|控股集团有限公司|控股有限公司|有限公司|股份|集团|控股|公司)$"
)


def clean(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    text = HTML_RE.sub("", text)
    text = text.replace("_em_", "")
    text = text.replace("&nbsp;", " ")
    return SPACE_RE.sub(" ", text).strip()


def code6(value: object) -> str:
    return v65.z6(clean(value))


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str, low_memory=False).fillna("")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def normalize_for_match(value: object) -> str:
    text = clean(value).lower()
    text = text.replace("（", "(").replace("）", ")")
    text = text.replace("【", "").replace("】", "")
    text = text.replace("[", "").replace("]", "")
    text = SPACE_RE.sub("", text)
    return text


def normalized_len(term: str) -> int:
    return len(normalize_for_match(term))


def parse_date(value: object) -> pd.Timestamp:
    text = clean(value)
    if not text:
        return pd.NaT
    text = re.sub(r"(\d{4})年(\d{1,2})月(\d{1,2})日", r"\1-\2-\3", text)
    return pd.to_datetime(text, errors="coerce")


def clean_app_product(value: object) -> str:
    text = clean(value)
    text = BRACKET_RE.sub("", text)
    text = text.replace("(APP)", "").replace("(app)", "")
    text = text.replace("(网站)", "").replace("(小程序)", "").replace("(其他)", "")
    return clean(text)


def is_generic(term: str) -> bool:
    norm = normalize_for_match(term)
    if norm.isdigit():
        return True
    return not norm or norm in GENERIC_TERMS


def firm_alias_norms(row: pd.Series) -> set[str]:
    aliases: set[str] = set()
    for col in ["listed_name", "full_name", "entity_name"]:
        raw = clean(row.get(col, ""))
        if not raw:
            continue
        candidates = {raw, re.sub(r"^(?:\*?ST|S\*?ST|PT)", "", raw, flags=re.I)}
        for candidate in list(candidates):
            candidate = re.sub(r"[AB]$", "", candidate, flags=re.I)
            candidates.add(candidate)
            stripped = CORP_SUFFIX_RE.sub("", candidate)
            if stripped:
                candidates.add(stripped)
        for candidate in candidates:
            norm = normalize_for_match(candidate)
            if norm:
                aliases.add(norm)
    return aliases


def is_firm_alias_term(term: str, aliases: set[str]) -> bool:
    norm = normalize_for_match(term)
    if not norm:
        return False
    if norm in aliases:
        return True
    if len(norm) <= 3 and any(alias.startswith(norm) or norm in alias for alias in aliases if len(alias) > len(norm)):
        return True
    has_product_marker = any(marker in norm for marker in PRODUCT_MARKERS)
    if not has_product_marker and any(alias in norm for alias in aliases if len(alias) >= 3):
        return True
    return False


def add_term(
    terms: list[dict[str, object]],
    seen: set[str],
    term: object,
    basis: str,
    base_score: int,
    firm_aliases: set[str],
) -> None:
    raw = clean(term).strip(" -—_/\\|｜:：;；,，。.!！?？[]【】()（）")
    if not raw:
        return
    norm = normalize_for_match(raw)
    if len(norm) < 2 or is_generic(raw) or is_firm_alias_term(raw, firm_aliases):
        return
    if norm in seen:
        return
    seen.add(norm)
    terms.append(
        {
            "term": raw,
            "term_norm": norm,
            "basis": basis,
            "base_score": base_score,
            "term_len": len(norm),
        }
    )


def core_variants(value: object) -> list[str]:
    text = clean_app_product(value)
    if not text or text in {"--", "-", "无", "无。"}:
        return []
    variants: set[str] = set()
    base = re.sub(r"[-_—－]?\d+$", "", text).strip()
    base = re.sub(r"[Vv]\d+(?:\.\d+)*$", "", base).strip()
    if base:
        variants.add(base)
    changed = True
    while changed:
        changed = False
        for suffix in CORE_SUFFIXES:
            for item in list(variants):
                if item.endswith(suffix) and len(item) > len(suffix):
                    stripped = item[: -len(suffix)].strip(" -—_/\\")
                    if stripped and stripped not in variants:
                        variants.add(stripped)
                        changed = True
    return sorted(variants, key=lambda x: (-normalized_len(x), x))


def product_terms(row: pd.Series) -> pd.DataFrame:
    terms: list[dict[str, object]] = []
    seen: set[str] = set()
    firm_aliases = firm_alias_norms(row)

    filing_no = clean(row.get("filing_no", ""))
    if filing_no and len(normalize_for_match(filing_no)) >= 8:
        add_term(terms, seen, filing_no, "filing_no_exact", 120, set())

    item_name = clean(row.get("item_name", ""))
    if item_name and item_name not in {"--", "-", "无"}:
        add_term(terms, seen, item_name, "item_name_exact", 95, firm_aliases)
        for variant in core_variants(item_name):
            if normalize_for_match(variant) != normalize_for_match(item_name):
                add_term(terms, seen, variant, "product_core_exact", 60, firm_aliases)

    app = clean_app_product(row.get("application_product", ""))
    if app and app not in {"--", "-", "无"}:
        add_term(terms, seen, app, "application_product_exact", 80, firm_aliases)
        for part in SPLIT_RE.split(app):
            add_term(terms, seen, part, "application_product_exact", 78, firm_aliases)
            for variant in core_variants(part):
                add_term(terms, seen, variant, "product_core_exact", 60, firm_aliases)

    return pd.DataFrame(terms)


def path_from_maybe_relative(value: object, base: Path) -> Path:
    text = clean(value)
    if not text:
        return Path("")
    path = Path(text)
    if path.is_absolute():
        return path
    return base / path


def parse_cninfo_filename(path: Path) -> dict[str, str]:
    match = CNINFO_NAME_RE.match(path.name)
    if not match:
        return {
            "doc_date": "",
            "sec_code": "",
            "sec_name": "",
            "announcement_id": "",
            "title": path.stem,
        }
    data = match.groupdict()
    return {
        "doc_date": data["date"],
        "sec_code": data["code"],
        "sec_name": clean(data["name"]),
        "announcement_id": data["announcement_id"],
        "title": clean(data["title"]),
    }


def build_text_doc(
    *,
    doc_id: str,
    source_type: str,
    venue: str,
    sec_code: object,
    sec_name: object,
    doc_date: object,
    title: object = "",
    text_path: object = "",
    text: object = "",
    announcement_id: object = "",
    pdf_url: object = "",
    metadata_text: object = "",
) -> dict[str, object]:
    path = Path(clean(text_path)) if clean(text_path) else Path("")
    body = clean(text)
    if path and path.exists():
        body = read_text(path)
    if not body:
        body = clean(metadata_text)
    title_clean = clean(title)
    full_text = "\n".join(part for part in [title_clean, body, clean(metadata_text)] if part)
    date = parse_date(doc_date)
    return {
        "doc_id": doc_id,
        "source_type": source_type,
        "venue": venue,
        "formal_doc_class": formal_doc_class(title_clean) if venue == "formal_announcement" else "interactive_or_qa",
        "event_ready_formal": int(venue == "formal_announcement" and formal_doc_class(title_clean) == "event_ready_formal"),
        "sec_code": code6(sec_code),
        "sec_name": clean(sec_name),
        "doc_date": date.strftime("%Y-%m-%d") if pd.notna(date) else "",
        "announcement_id": clean(announcement_id),
        "title": title_clean,
        "text_path": str(path) if path else "",
        "pdf_url": clean(pdf_url),
        "text": body,
        "search_text": full_text,
        "text_len": len(body),
    }


def formal_doc_class(title: object) -> str:
    title_norm = normalize_for_match(title)
    if any(normalize_for_match(pattern) in title_norm for pattern in ROUTINE_FORMAL_PATTERNS):
        return "routine_filing_or_financing"
    return "event_ready_formal"


def load_pom_docs() -> list[dict[str, object]]:
    df = read_csv(POM_REVIEW)
    docs: list[dict[str, object]] = []
    for i, row in df.iterrows():
        path = path_from_maybe_relative(row.get("txt_local_path", ""), POM_ROOT)
        doc_id = clean(row.get("announcement_id", "")) or clean(row.get("pack_row_id", "")) or f"pom_row_{i + 1}"
        doc_date = clean(row.get("manual_correct_event_date", "")) or clean(row.get("announcement_date", ""))
        meta = " ".join(
            clean(row.get(col, ""))
            for col in [
                "matched_genai_terms",
                "query_terms",
                "metadata_snippet",
                "priority_evidence",
                "manual_counterparty_or_project",
                "manual_notes",
            ]
        )
        docs.append(
            build_text_doc(
                doc_id=f"cninfo_pom::{doc_id}",
                source_type="cninfo_formal_pom_like",
                venue="formal_announcement",
                sec_code=row.get("sec_code", ""),
                sec_name=row.get("sec_name", ""),
                doc_date=doc_date,
                title=row.get("announcement_title", ""),
                text_path=path,
                announcement_id=row.get("announcement_id", ""),
                pdf_url=row.get("pdf_url", ""),
                metadata_text=meta,
            )
        )
    return docs


def pom_announcement_date_overrides() -> dict[str, str]:
    df = read_csv(POM_REVIEW)
    if df.empty or "announcement_id" not in df.columns:
        return {}
    out: dict[str, str] = {}
    for _, row in df.iterrows():
        aid = clean(row.get("announcement_id", ""))
        date = clean(row.get("manual_correct_event_date", "")) or clean(row.get("announcement_date", ""))
        if aid and date:
            out[aid] = date
    return out


def load_raw_genai_docs() -> list[dict[str, object]]:
    docs: list[dict[str, object]] = []
    if not RAW_GENAI_TEXT_DIR.exists():
        return docs
    date_overrides = pom_announcement_date_overrides()
    for i, path in enumerate(sorted(RAW_GENAI_TEXT_DIR.glob("*.txt")), start=1):
        info = parse_cninfo_filename(path)
        doc_date = date_overrides.get(info["announcement_id"], info["doc_date"])
        docs.append(
            build_text_doc(
                doc_id=f"cninfo_raw::{info['announcement_id'] or path.stem or i}",
                source_type="cninfo_formal_raw_genai",
                venue="formal_announcement",
                sec_code=info["sec_code"],
                sec_name=info["sec_name"],
                doc_date=doc_date,
                title=info["title"],
                text_path=path,
                announcement_id=info["announcement_id"],
            )
        )
    return docs


def load_extra_cninfo_text_docs() -> list[dict[str, object]]:
    docs: list[dict[str, object]] = []
    date_overrides = pom_announcement_date_overrides()
    for text_dir, source_type in EXTRA_CNINFO_TEXT_DIRS:
        if not text_dir.exists():
            continue
        for i, path in enumerate(sorted(text_dir.glob("*.txt")), start=1):
            info = parse_cninfo_filename(path)
            if not info["sec_code"]:
                continue
            doc_date = date_overrides.get(info["announcement_id"], info["doc_date"])
            docs.append(
                build_text_doc(
                    doc_id=f"{source_type}::{info['announcement_id'] or path.stem or i}",
                    source_type=source_type,
                    venue="formal_announcement",
                    sec_code=info["sec_code"],
                    sec_name=info["sec_name"],
                    doc_date=doc_date,
                    title=info["title"],
                    text_path=path,
                    announcement_id=info["announcement_id"],
                )
            )
    return docs


def load_cninfo_ir_docs() -> list[dict[str, object]]:
    docs: list[dict[str, object]] = []
    meta = read_csv(CNINFO_IR_MATCHES)
    snippet = read_csv(CNINFO_IR_SNIPPETS)
    snippet_map: dict[str, str] = {}
    if not snippet.empty and "txt_file" in snippet.columns:
        snippet_map = (
            snippet.groupby("txt_file")["sentence"]
            .apply(lambda s: " ".join(clean(x) for x in s.head(12)))
            .to_dict()
        )
    meta_map: dict[str, dict[str, object]] = {}
    if not meta.empty and "txt_file" in meta.columns:
        for _, row in meta.iterrows():
            meta_map[clean(row.get("txt_file", ""))] = row.to_dict()

    if CNINFO_IR_TEXT_DIR.exists():
        for i, path in enumerate(sorted(CNINFO_IR_TEXT_DIR.glob("*.txt")), start=1):
            rel = f"cninfo_ir_activity/text/{path.name}"
            row = meta_map.get(rel, {})
            info = parse_cninfo_filename(path)
            meta_text = " ".join(
                [
                    clean(row.get("matched_terms", "")),
                    clean(snippet_map.get(rel, "")),
                ]
            )
            docs.append(
                build_text_doc(
                    doc_id=f"cninfo_ir::{clean(row.get('announcement_id', '')) or info['announcement_id'] or path.stem or i}",
                    source_type="cninfo_ir_activity",
                    venue="cninfo_ir_activity",
                    sec_code=row.get("sec_code", "") or info["sec_code"],
                    sec_name=row.get("sec_name", "") or info["sec_name"],
                    doc_date=row.get("announcement_date", "") or info["doc_date"],
                    title=row.get("announcement_title", "") or info["title"],
                    text_path=path,
                    announcement_id=row.get("announcement_id", "") or info["announcement_id"],
                    pdf_url=row.get("pdf_url", ""),
                    metadata_text=meta_text,
                )
            )
    return docs


def load_csmar_answer_docs(path: Path, source_type: str, venue: str) -> list[dict[str, object]]:
    df = read_csv(path)
    docs: list[dict[str, object]] = []
    if df.empty:
        return docs
    for i, row in df.iterrows():
        source_id = clean(row.get("source_id", "")) or f"{source_type}_{i + 1}"
        title = clean(row.get("Title", ""))
        text = "\n".join(
            clean(row.get(col, ""))
            for col in ["Title", "question_text", "answer_text", "QuestionContent", "ReplyContent", "Question", "Answer", "genai_span"]
            if clean(row.get(col, ""))
        )
        docs.append(
            build_text_doc(
                doc_id=f"{source_type}::{source_id}",
                source_type=source_type,
                venue=venue,
                sec_code=row.get("stock_code", ""),
                sec_name=row.get("company_name", ""),
                doc_date=row.get("event_date", ""),
                title=title,
                text=text,
                announcement_id=row.get("ReportID", ""),
                metadata_text=" ".join([clean(row.get("answer_terms", "")), clean(row.get("question_terms", ""))]),
            )
        )
    return docs


def load_doc_index() -> pd.DataFrame:
    docs: list[dict[str, object]] = []
    docs.extend(load_pom_docs())
    docs.extend(load_raw_genai_docs())
    docs.extend(load_extra_cninfo_text_docs())
    docs.extend(load_cninfo_ir_docs())
    docs.extend(load_csmar_answer_docs(IIP_ANSWER_EVENTS, "csmar_iip_answer", "iip"))
    docs.extend(load_csmar_answer_docs(IRQA_ANSWER_EVENTS, "csmar_irqa_answer", "irqa"))

    if not docs:
        return pd.DataFrame()
    out = pd.DataFrame(docs)
    out = out[out["sec_code"].ne("") & out["doc_date"].ne("")].copy()
    out["doc_date_dt"] = pd.to_datetime(out["doc_date"], errors="coerce")
    out = out[out["doc_date_dt"].notna()].copy()
    out["title_norm"] = out["title"].map(normalize_for_match)
    out["search_norm"] = out["search_text"].map(normalize_for_match)
    formal_key = (
        "formal::"
        + out["sec_code"].map(clean)
        + "::"
        + out["doc_date"].map(clean)
        + "::"
        + out["announcement_id"].map(clean)
        + "::"
        + out["title"].map(clean)
    )
    nonformal_key = out["source_type"].map(clean) + "::" + out["doc_id"].map(clean)
    out["doc_key"] = np.where(out["venue"].eq("formal_announcement"), formal_key, nonformal_key)
    out = out.drop_duplicates("doc_key").reset_index(drop=True)
    return out


def match_term_in_doc(term: dict[str, object], doc: pd.Series) -> dict[str, object] | None:
    term_norm = clean(term["term_norm"])
    search_norm = clean(doc.get("search_norm", ""))
    if not term_norm or term_norm not in search_norm:
        return None
    pos = search_norm.find(term_norm)
    title_hit = int(term_norm in clean(doc.get("title_norm", "")))
    window = search_norm[max(0, pos - 60) : min(len(search_norm), pos + len(term_norm) + 60)]
    context_hit = int(any(normalize_for_match(k) in window for k in CONTEXT_KEYWORDS))
    score = int(term["base_score"]) + 8 * title_hit + 6 * context_hit
    score = min(score, 130)
    basis = clean(term["basis"])
    accepted = score >= ACCEPT_MIN
    if basis == "product_core_exact" and int(term["term_len"]) <= 2 and score < 74:
        accepted = False
    if basis == "product_core_exact" and int(term["term_len"]) >= 3 and score < 66:
        accepted = False
    return {
        "match_score": score,
        "match_basis": basis,
        "matched_term": clean(term["term"]),
        "matched_term_len": int(term["term_len"]),
        "title_hit": title_hit,
        "context_keyword_hit": context_hit,
        "accepted_for_traceback": int(accepted),
    }


def excerpt_for_match(text: str, title: str, term: str, width: int = 140) -> str:
    haystack = clean("\n".join([title, text]))
    if not haystack:
        return ""
    pos = haystack.find(term)
    if pos < 0:
        pos = haystack.lower().find(term.lower())
    if pos < 0:
        return haystack[: width * 2]
    start = max(0, pos - width)
    end = min(len(haystack), pos + len(term) + width)
    return haystack[start:end]


def load_registry_master() -> pd.DataFrame:
    master = read_csv(V67_MASTER)
    master["listed_code"] = master["listed_code"].map(code6)
    master["batch_public_datetime"] = pd.to_datetime(master["batch_public_datetime"], errors="coerce")
    master["batch_public_date_dt"] = pd.to_datetime(master["batch_public_date"], errors="coerce")
    master["batch_public_dt"] = master["batch_public_datetime"].where(
        master["batch_public_datetime"].notna(), master["batch_public_date_dt"]
    )
    return master


def search_products(registry: pd.DataFrame, docs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    doc_groups = {code: group.copy() for code, group in docs.groupby("sec_code")}
    hit_rows: list[dict[str, object]] = []
    term_rows: list[dict[str, object]] = []

    for _, product in registry.iterrows():
        product_id = clean(product.get("registry_product_id", ""))
        terms = product_terms(product)
        if not terms.empty:
            tr = terms.copy()
            tr.insert(0, "registry_product_id", product_id)
            tr.insert(1, "listed_code", clean(product.get("listed_code", "")))
            tr.insert(2, "listed_name", clean(product.get("listed_name", "")))
            tr.insert(3, "registry_item_name", clean(product.get("item_name", "")))
            tr.insert(4, "registry_application_product", clean(product.get("application_product", "")))
            term_rows.append(tr)

        code_docs = doc_groups.get(clean(product.get("listed_code", "")), pd.DataFrame())
        if terms.empty or code_docs.empty:
            continue

        for _, doc in code_docs.iterrows():
            matches: list[dict[str, object]] = []
            for term in terms.to_dict("records"):
                match = match_term_in_doc(term, doc)
                if match:
                    matches.append(match)
            if not matches:
                continue
            matches = sorted(matches, key=lambda x: (x["match_score"], x["matched_term_len"]), reverse=True)
            best = matches[0]
            all_terms = "; ".join(
                f"{m['match_basis']}:{m['matched_term']}:{m['match_score']}" for m in matches[:8]
            )
            hit_rows.append(
                {
                    "registry_product_id": product_id,
                    "registry_source": clean(product.get("registry_source", "")),
                    "registry_status": clean(product.get("registry_status", "")),
                    "verification_type": clean(product.get("verification_type", "")),
                    "listed_code": clean(product.get("listed_code", "")),
                    "listed_name": clean(product.get("listed_name", "")),
                    "entity_name": clean(product.get("entity_name", "")),
                    "item_name": clean(product.get("item_name", "")),
                    "application_product": clean(product.get("application_product", "")),
                    "filing_no": clean(product.get("filing_no", "")),
                    "batch_public_date": clean(product.get("batch_public_date", "")),
                    "batch_public_date_precision": clean(product.get("batch_public_date_precision", "")),
                    "relation_to_listed": clean(product.get("relation_to_listed", "")),
                    "match_confidence": clean(product.get("match_confidence", "")),
                    "doc_id": clean(doc.get("doc_id", "")),
                    "source_type": clean(doc.get("source_type", "")),
                    "venue": clean(doc.get("venue", "")),
                    "formal_doc_class": clean(doc.get("formal_doc_class", "")),
                    "event_ready_formal": int(doc.get("event_ready_formal", 0) or 0),
                    "doc_date": clean(doc.get("doc_date", "")),
                    "announcement_id": clean(doc.get("announcement_id", "")),
                    "title": clean(doc.get("title", "")),
                    "pdf_url": clean(doc.get("pdf_url", "")),
                    "text_path": clean(doc.get("text_path", "")),
                    "match_score": best["match_score"],
                    "match_basis": best["match_basis"],
                    "matched_term": best["matched_term"],
                    "matched_term_len": best["matched_term_len"],
                    "title_hit": best["title_hit"],
                    "context_keyword_hit": best["context_keyword_hit"],
                    "accepted_for_traceback": best["accepted_for_traceback"],
                    "all_term_matches": all_terms,
                    "excerpt": excerpt_for_match(clean(doc.get("text", "")), clean(doc.get("title", "")), best["matched_term"]),
                }
            )

    hits = pd.DataFrame(hit_rows)
    term_index = pd.concat(term_rows, ignore_index=True, sort=False) if term_rows else pd.DataFrame()
    if not hits.empty:
        hits["doc_date_dt"] = pd.to_datetime(hits["doc_date"], errors="coerce")
        hits = hits.sort_values(
            ["registry_product_id", "accepted_for_traceback", "doc_date_dt", "match_score", "matched_term_len"],
            ascending=[True, False, True, False, False],
        ).reset_index(drop=True)
    return hits, term_index


def first_hit(
    accepted: pd.DataFrame,
    product_id: str,
    venues: set[str] | None = None,
    require_event_ready_formal: bool = False,
) -> pd.Series | None:
    group = accepted[accepted["registry_product_id"].eq(product_id)].copy()
    if venues is not None:
        group = group[group["venue"].isin(venues)].copy()
    if require_event_ready_formal:
        group = group[group["event_ready_formal"].astype(str).eq("1")].copy()
    if group.empty:
        return None
    group = group.sort_values(["doc_date_dt", "match_score", "matched_term_len"], ascending=[True, False, False])
    return group.iloc[0]


def timing(first_date: object, batch_date: object) -> tuple[str, float]:
    first = pd.to_datetime(first_date, errors="coerce")
    batch = pd.to_datetime(batch_date, errors="coerce")
    if pd.isna(first) or pd.isna(batch):
        return "", np.nan
    days = float((first.normalize() - batch.normalize()).days)
    if days < 0:
        return "disclosure_before_registry_publication", days
    if days == 0:
        return "same_day_as_registry_publication", days
    return "disclosure_after_registry_publication", days


def build_best(registry: pd.DataFrame, hits: pd.DataFrame, term_index: pd.DataFrame) -> pd.DataFrame:
    accepted = hits[hits["accepted_for_traceback"].eq(1)].copy() if not hits.empty else pd.DataFrame()
    term_counts = (
        term_index.groupby("registry_product_id")["term_norm"].nunique().rename("search_term_count").reset_index()
        if not term_index.empty
        else pd.DataFrame(columns=["registry_product_id", "search_term_count"])
    )
    hit_counts = (
        hits.groupby("registry_product_id")
        .agg(raw_hit_docs=("doc_id", "nunique"), accepted_hit_docs=("accepted_for_traceback", "sum"))
        .reset_index()
        if not hits.empty
        else pd.DataFrame(columns=["registry_product_id", "raw_hit_docs", "accepted_hit_docs"])
    )

    rows: list[dict[str, object]] = []
    for _, product in registry.iterrows():
        product_id = clean(product.get("registry_product_id", ""))
        formal = first_hit(accepted, product_id, {"formal_announcement"}, require_event_ready_formal=True)
        formal_any = first_hit(accepted, product_id, {"formal_announcement"})
        interactive = first_hit(accepted, product_id, {"cninfo_ir_activity", "iip", "irqa"})
        any_pool = accepted[
            accepted["registry_product_id"].eq(product_id)
            & (
                accepted["venue"].isin(["cninfo_ir_activity", "iip", "irqa"])
                | (accepted["venue"].eq("formal_announcement") & accepted["event_ready_formal"].astype(str).eq("1"))
            )
        ].copy()
        any_hit = first_hit(any_pool, product_id, None)
        row = product.to_dict()
        row["has_any_traceback"] = int(any_hit is not None)
        row["has_formal_traceback_d1"] = int(formal is not None)
        row["has_formal_any_traceback"] = int(formal_any is not None)
        row["has_interactive_traceback_d1_prime"] = int(interactive is not None)
        for prefix, hit in [("formal", formal), ("formal_any", formal_any), ("interactive", interactive), ("any", any_hit)]:
            if hit is None:
                row[f"{prefix}_first_date"] = ""
                row[f"{prefix}_first_timing_vs_registry"] = ""
                row[f"{prefix}_first_days_from_registry_publication"] = np.nan
                row[f"{prefix}_first_source_type"] = ""
                row[f"{prefix}_first_venue"] = ""
                row[f"{prefix}_first_formal_doc_class"] = ""
                row[f"{prefix}_first_title"] = ""
                row[f"{prefix}_first_match_score"] = np.nan
                row[f"{prefix}_first_match_basis"] = ""
                row[f"{prefix}_first_matched_term"] = ""
                row[f"{prefix}_first_announcement_id"] = ""
                row[f"{prefix}_first_text_path"] = ""
                row[f"{prefix}_first_excerpt"] = ""
                continue
            t, days = timing(hit["doc_date"], product.get("batch_public_dt", ""))
            row[f"{prefix}_first_date"] = clean(hit["doc_date"])
            row[f"{prefix}_first_timing_vs_registry"] = t
            row[f"{prefix}_first_days_from_registry_publication"] = days
            row[f"{prefix}_first_source_type"] = clean(hit.get("source_type", ""))
            row[f"{prefix}_first_venue"] = clean(hit.get("venue", ""))
            row[f"{prefix}_first_formal_doc_class"] = clean(hit.get("formal_doc_class", ""))
            row[f"{prefix}_first_title"] = clean(hit.get("title", ""))
            row[f"{prefix}_first_match_score"] = hit.get("match_score", np.nan)
            row[f"{prefix}_first_match_basis"] = clean(hit.get("match_basis", ""))
            row[f"{prefix}_first_matched_term"] = clean(hit.get("matched_term", ""))
            row[f"{prefix}_first_announcement_id"] = clean(hit.get("announcement_id", ""))
            row[f"{prefix}_first_text_path"] = clean(hit.get("text_path", ""))
            row[f"{prefix}_first_excerpt"] = clean(hit.get("excerpt", ""))
        rows.append(row)

    best = pd.DataFrame(rows)
    best = best.merge(term_counts, on="registry_product_id", how="left")
    best = best.merge(hit_counts, on="registry_product_id", how="left")
    best["search_term_count"] = pd.to_numeric(best["search_term_count"], errors="coerce").fillna(0).astype(int)
    best["raw_hit_docs"] = pd.to_numeric(best["raw_hit_docs"], errors="coerce").fillna(0).astype(int)
    best["accepted_hit_docs"] = pd.to_numeric(best["accepted_hit_docs"], errors="coerce").fillna(0).astype(int)
    return best


def summarize(best: pd.DataFrame, hits: pd.DataFrame, docs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    event_ready_hits = (
        hits[
            hits["accepted_for_traceback"].eq(1)
            & (
                hits["venue"].isin(["cninfo_ir_activity", "iip", "irqa"])
                | (hits["venue"].eq("formal_announcement") & hits["event_ready_formal"].astype(str).eq("1"))
            )
        ]
        if not hits.empty
        else pd.DataFrame()
    )
    metrics = {
        "registry_products_input": len(best),
        "listed_firms_input": best["listed_code"].nunique(),
        "doc_index_rows": len(docs),
        "doc_index_firms": docs["sec_code"].nunique() if not docs.empty else 0,
        "raw_hit_rows": len(hits),
        "accepted_hit_rows": int(hits["accepted_for_traceback"].sum()) if not hits.empty else 0,
        "accepted_event_ready_or_interactive_hit_rows": len(event_ready_hits),
        "products_any_traceback": int(best["has_any_traceback"].sum()),
        "products_formal_d1": int(best["has_formal_traceback_d1"].sum()),
        "products_formal_any_mention": int(best["has_formal_any_traceback"].sum()),
        "products_interactive_d1_prime": int(best["has_interactive_traceback_d1_prime"].sum()),
        "firms_any_traceback": best.loc[best["has_any_traceback"].eq(1), "listed_code"].nunique(),
        "firms_formal_d1": best.loc[best["has_formal_traceback_d1"].eq(1), "listed_code"].nunique(),
        "firms_formal_any_mention": best.loc[best["has_formal_any_traceback"].eq(1), "listed_code"].nunique(),
        "firms_interactive_d1_prime": best.loc[best["has_interactive_traceback_d1_prime"].eq(1), "listed_code"].nunique(),
    }
    summary = pd.DataFrame([{"metric": k, "value": v} for k, v in metrics.items()])
    by_type = (
        best.groupby("verification_type", dropna=False)
        .agg(
            products=("registry_product_id", "nunique"),
            firms=("listed_code", "nunique"),
            any_traceback=("has_any_traceback", "sum"),
            formal_d1=("has_formal_traceback_d1", "sum"),
            formal_any_mention=("has_formal_any_traceback", "sum"),
            interactive_d1_prime=("has_interactive_traceback_d1_prime", "sum"),
        )
        .reset_index()
        .sort_values("products", ascending=False)
    )
    timing_counts = (
        best.groupby(["verification_type", "any_first_timing_vs_registry"], dropna=False)
        .agg(products=("registry_product_id", "nunique"), firms=("listed_code", "nunique"))
        .reset_index()
        .sort_values(["verification_type", "any_first_timing_vs_registry"])
    )
    return summary, by_type, timing_counts


def build_review_queue(best: pd.DataFrame, hits: pd.DataFrame) -> pd.DataFrame:
    low = pd.DataFrame()
    if not hits.empty:
        accepted = hits[hits["accepted_for_traceback"].eq(1)].copy()
        low = accepted[
            (accepted["match_score"].lt(90))
            | (accepted["matched_term_len"].le(2))
            | (accepted["match_basis"].eq("product_core_exact"))
        ].copy()
        low["review_reason"] = np.select(
            [
                low["match_basis"].eq("product_core_exact"),
                low["matched_term_len"].le(2),
                low["match_score"].lt(90),
            ],
            ["core_term_match", "short_term_match", "score_below_90"],
            default="manual_check",
        )
    no_hit = best[best["has_any_traceback"].eq(0)].copy()
    no_hit = no_hit[
        [
            "registry_product_id",
            "verification_type",
            "listed_code",
            "listed_name",
            "entity_name",
            "item_name",
            "application_product",
            "filing_no",
            "batch_public_date",
            "match_confidence",
        ]
    ].copy()
    no_hit["doc_id"] = ""
    no_hit["source_type"] = ""
    no_hit["venue"] = ""
    no_hit["doc_date"] = ""
    no_hit["title"] = ""
    no_hit["match_score"] = np.nan
    no_hit["match_basis"] = ""
    no_hit["matched_term"] = ""
    no_hit["excerpt"] = ""
    no_hit["review_reason"] = "no_product_traceback_hit"
    keep_cols = [
        "review_reason",
        "registry_product_id",
        "verification_type",
        "listed_code",
        "listed_name",
        "entity_name",
        "item_name",
        "application_product",
        "filing_no",
        "batch_public_date",
        "match_confidence",
        "doc_id",
        "source_type",
        "venue",
        "doc_date",
        "title",
        "match_score",
        "match_basis",
        "matched_term",
        "excerpt",
    ]
    if low.empty:
        return no_hit[keep_cols]
    for col in keep_cols:
        if col not in low.columns:
            low[col] = ""
    review = pd.concat([low[keep_cols], no_hit[keep_cols]], ignore_index=True, sort=False)
    return review.sort_values(["review_reason", "listed_code", "doc_date", "match_score"], ascending=[True, True, True, False])


def fmt_int(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return clean(value)


def md_table(df: pd.DataFrame, limit: int = 40) -> str:
    if df.empty:
        return "_No rows._"
    show = df.head(limit).copy()
    for col in show.columns:
        if pd.api.types.is_numeric_dtype(show[col]):
            show[col] = show[col].map(lambda x: "" if pd.isna(x) else (f"{x:.4f}" if isinstance(x, float) and not x.is_integer() else fmt_int(x)))
        else:
            show[col] = show[col].map(lambda x: clean(x)[:180])
    lines = ["| " + " | ".join(show.columns) + " |", "|" + "|".join("---" for _ in show.columns) + "|"]
    for _, row in show.iterrows():
        lines.append("| " + " | ".join(clean(row[c]).replace("|", "\\|") for c in show.columns) + " |")
    return "\n".join(lines)


def write_doc(
    summary: pd.DataFrame,
    by_type: pd.DataFrame,
    timing_counts: pd.DataFrame,
    best: pd.DataFrame,
    hits: pd.DataFrame,
    review: pd.DataFrame,
) -> None:
    showcase_cols = [
        "listed_code",
        "listed_name",
        "verification_type",
        "item_name",
        "application_product",
        "batch_public_date",
        "any_first_date",
        "any_first_timing_vs_registry",
        "any_first_source_type",
        "any_first_match_basis",
        "any_first_matched_term",
        "any_first_title",
    ]
    showcase = best[best["has_any_traceback"].eq(1)][showcase_cols].head(25).copy()

    high_hits = pd.DataFrame()
    if not hits.empty:
        high_hits = hits[hits["accepted_for_traceback"].eq(1)].copy()
        high_hits = high_hits.sort_values(["match_score", "doc_date"], ascending=[False, True])[
            [
                "listed_code",
                "listed_name",
                "verification_type",
                "item_name",
                "doc_date",
                "source_type",
                "match_score",
                "match_basis",
                "matched_term",
                "title",
            ]
        ].head(25)

    lines = [
        "# v69 Registry Product Traceback",
        "",
        "## Purpose",
        "",
        "- Implements the missing reverse-location step after v67/v68.",
        "- Searches each listed firm-product from the CAC registry master against local CNINFO formal announcements, CNINFO investor-relation activity records, and CSMAR IIP/IRQA GenAI answer-level corpora.",
        "- Uses same-firm product-level terms only: filing number, registry item name, application/product name, and conservative core-name variants.",
        "- Firm name alone is never sufficient for a traceback hit.",
        "",
        "## Outputs",
        "",
        f"- `results/{RUN_ID}/registry_product_traceback_hits.csv`",
        f"- `results/{RUN_ID}/registry_product_traceback_best.csv`",
        f"- `results/{RUN_ID}/registry_product_traceback_summary.csv`",
        f"- `results/{RUN_ID}/registry_product_traceback_by_type.csv`",
        f"- `results/{RUN_ID}/registry_product_traceback_timing_counts.csv`",
        f"- `results/{RUN_ID}/registry_product_search_terms.csv`",
        f"- `results/{RUN_ID}/registry_product_traceback_review_queue.csv`",
        f"- `results/{RUN_ID}/{RUN_ID}.xlsx`",
        "",
        "## Main Counts",
        "",
        md_table(summary, limit=40),
        "",
        "## Counts By Registry Type",
        "",
        md_table(by_type, limit=40),
        "",
        "## Timing Relative To Registry Publication",
        "",
        md_table(timing_counts, limit=80),
        "",
        "## Example Product-Level Tracebacks",
        "",
        md_table(showcase, limit=25),
        "",
        "## Highest-Score Hits",
        "",
        md_table(high_hits, limit=25),
        "",
        "## Review Queue",
        "",
        f"- Rows needing manual/LLM confirmation or no-hit diagnosis: {fmt_int(len(review))}",
        "",
        "## Interpretation Caveat",
        "",
        "This run is an executable traceback index, not a final causal sample. Low-score core-name hits and no-hit products are intentionally separated into the review queue before v70 product-level relabeling.",
        "",
    ]
    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    registry = load_registry_master()
    docs = load_doc_index()
    hits, term_index = search_products(registry, docs)
    best = build_best(registry, hits, term_index)
    summary, by_type, timing_counts = summarize(best, hits, docs)
    review = build_review_queue(best, hits)

    docs_meta = docs.drop(columns=["text", "search_text", "search_norm"], errors="ignore")
    docs_meta.to_csv(OUT_DIR / "traceback_doc_index.csv", index=False, encoding="utf-8-sig")
    term_index.to_csv(OUT_DIR / "registry_product_search_terms.csv", index=False, encoding="utf-8-sig")
    hits.drop(columns=["doc_date_dt"], errors="ignore").to_csv(
        OUT_DIR / "registry_product_traceback_hits.csv", index=False, encoding="utf-8-sig"
    )
    best.drop(columns=["batch_public_date_dt", "batch_public_dt"], errors="ignore").to_csv(
        OUT_DIR / "registry_product_traceback_best.csv", index=False, encoding="utf-8-sig"
    )
    summary.to_csv(OUT_DIR / "registry_product_traceback_summary.csv", index=False, encoding="utf-8-sig")
    by_type.to_csv(OUT_DIR / "registry_product_traceback_by_type.csv", index=False, encoding="utf-8-sig")
    timing_counts.to_csv(OUT_DIR / "registry_product_traceback_timing_counts.csv", index=False, encoding="utf-8-sig")
    review.to_csv(OUT_DIR / "registry_product_traceback_review_queue.csv", index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(OUT_DIR / f"{RUN_ID}.xlsx") as writer:
        best.drop(columns=["batch_public_date_dt", "batch_public_dt"], errors="ignore").to_excel(writer, sheet_name="Best", index=False)
        summary.to_excel(writer, sheet_name="Summary", index=False)
        by_type.to_excel(writer, sheet_name="By_type", index=False)
        timing_counts.to_excel(writer, sheet_name="Timing", index=False)
        hits.drop(columns=["doc_date_dt"], errors="ignore").head(200000).to_excel(writer, sheet_name="Hits", index=False)
        review.head(200000).to_excel(writer, sheet_name="Review_queue", index=False)
        term_index.to_excel(writer, sheet_name="Search_terms", index=False)
        docs_meta.head(200000).to_excel(writer, sheet_name="Doc_index", index=False)

    write_doc(summary, by_type, timing_counts, best, hits, review)

    print("run_id", RUN_ID)
    print(summary.to_string(index=False))
    print("by_type")
    print(by_type.to_string(index=False))
    print("doc", DOC_PATH)


if __name__ == "__main__":
    main()
