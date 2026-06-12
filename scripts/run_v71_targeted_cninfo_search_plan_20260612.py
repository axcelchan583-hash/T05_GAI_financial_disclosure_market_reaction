#!/usr/bin/env python3
"""Build and optionally pilot targeted CNINFO searches for registry products."""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v69_registry_product_traceback_20260612 as v69  # noqa: E402


RUN_ID = "v71_targeted_cninfo_search_plan_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "131_v71_targeted_cninfo_search_plan_20260612.md"

V69_BEST = ROOT / "results/v69_registry_product_traceback_20260612/registry_product_traceback_best.csv"
V69_TERMS = ROOT / "results/v69_registry_product_traceback_20260612/registry_product_search_terms.csv"

QUERY_URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
STATIC_BASE = "https://static.cninfo.com.cn/"
START_DATE = "2023-01-01"
END_DATE = "2026-06-12"
PAGE_SIZE = 30
MAX_PAGES_PER_QUERY = 2
PILOT_HIT_COLUMNS = [
    "registry_product_id",
    "listed_code",
    "listed_name",
    "query_term",
    "query_kind",
    "query_scope",
    "hit_sec_code",
    "hit_sec_name",
    "announcement_id",
    "announcement_title",
    "announcement_date",
    "pdf_url",
    "adjunct_url",
    "same_firm",
    "routine_title",
    "event_ready_title",
]
PILOT_COUNT_COLUMNS = [
    "registry_product_id",
    "listed_code",
    "listed_name",
    "query_term",
    "query_kind",
    "query_scope",
    "total",
    "pages_checked",
    "error",
]

MARKET_SCOPES = [
    {"scope": "szse_a", "column": "szse", "plate": "sz"},
    {"scope": "sse_a", "column": "sse", "plate": "sh"},
    {"scope": "bse_a", "column": "third", "plate": "bj"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Referer": "http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search",
    "Origin": "http://www.cninfo.com.cn",
}

HIGH_NOISE_TITLE_RE = re.compile(
    r"年度报告|半年度报告|季度报告|股东大会|股东会|会议资料|会议材料|会议文件|"
    r"提质增效|行动方案|募集说明书|论证分析报告|审计报告|法律意见|保荐|"
    r"可转换公司债券|向特定对象发行|向不特定对象发行|业绩说明会|投资者关系|调研活动"
)
EVENT_READY_TITLE_RE = re.compile(
    r"发布|上线|成果|备案通过|算法备案|大模型备案|自愿性信息披露|自愿披露|"
    r"中标|合同|合作|投资|收购|增资|项目|应用|平台|模型"
)


def clean(value: object) -> str:
    return v69.clean(value)


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, low_memory=False).fillna("")


def strip_tags(value: object) -> str:
    text = clean(value)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def ts_to_date(value: object) -> str:
    text = clean(value)
    if not text:
        return ""
    try:
        return pd.to_datetime(int(float(text)), unit="ms").strftime("%Y-%m-%d")
    except Exception:
        parsed = pd.to_datetime(text, errors="coerce")
        return "" if pd.isna(parsed) else parsed.strftime("%Y-%m-%d")


def safe_bool(value: object) -> bool:
    return clean(value) in {"1", "1.0", "True", "true", "yes"}


def query_priority(row: pd.Series) -> str:
    has_d1 = safe_bool(row.get("has_formal_traceback_d1", ""))
    has_any = safe_bool(row.get("has_formal_any_traceback", ""))
    vtype = clean(row.get("verification_type", ""))
    if has_d1:
        return "P3_already_event_ready_d1"
    if vtype in {"self_filing", "app_registration"}:
        return "P0_no_d1_self_or_registration"
    if has_any:
        return "P1_routine_only_needs_backfill"
    if vtype == "deep_synthesis":
        return "P2_no_d1_deep_synthesis"
    return "P2_no_d1_other"


def local_traceback_status(row: pd.Series) -> str:
    if safe_bool(row.get("has_formal_traceback_d1", "")):
        return "event_ready_formal_d1"
    if safe_bool(row.get("has_formal_any_traceback", "")):
        return "routine_formal_mention_only"
    if safe_bool(row.get("has_interactive_traceback_d1_prime", "")):
        return "interactive_only"
    return "no_local_traceback"


def load_product_plan() -> pd.DataFrame:
    best = read_csv(V69_BEST)
    best["listed_code"] = best["listed_code"].map(v69.code6)
    best["query_priority"] = best.apply(query_priority, axis=1)
    best["local_traceback_status"] = best.apply(local_traceback_status, axis=1)
    cols = [
        "registry_product_id",
        "listed_code",
        "listed_name",
        "verification_type",
        "registry_source",
        "registry_status",
        "entity_name",
        "item_name",
        "application_product",
        "filing_no",
        "batch_public_date",
        "has_formal_traceback_d1",
        "has_formal_any_traceback",
        "has_interactive_traceback_d1_prime",
        "formal_first_date",
        "formal_first_title",
        "formal_any_first_date",
        "formal_any_first_title",
        "query_priority",
        "local_traceback_status",
    ]
    return best[cols].copy()


def is_useful_term(term: str, basis: str) -> bool:
    norm = v69.normalize_for_match(term)
    if len(norm) < 3:
        return False
    if basis == "product_core_exact" and len(norm) < 4:
        return False
    if norm in v69.GENERIC_TERMS:
        return False
    return True


def add_query(rows: list[dict[str, object]], base: dict[str, object], query: str, query_kind: str, priority: int) -> None:
    query = clean(query)
    if not query:
        return
    rows.append({**base, "query_term": query, "query_kind": query_kind, "query_priority_rank": priority})


def build_query_terms(product_plan: pd.DataFrame) -> pd.DataFrame:
    terms = read_csv(V69_TERMS)
    terms["listed_code"] = terms["listed_code"].map(v69.code6)
    terms = terms.merge(
        product_plan[
            [
                "registry_product_id",
                "verification_type",
                "query_priority",
                "local_traceback_status",
                "has_formal_traceback_d1",
            ]
        ],
        on="registry_product_id",
        how="left",
    )
    rows: list[dict[str, object]] = []
    for product_id, group in terms.groupby("registry_product_id"):
        group = group.copy()
        group["base_score_num"] = pd.to_numeric(group["base_score"], errors="coerce").fillna(0)
        group["term_len_num"] = pd.to_numeric(group["term_len"], errors="coerce").fillna(0)
        group = group.sort_values(["base_score_num", "term_len_num"], ascending=[False, False])
        first = group.iloc[0]
        base = {
            "registry_product_id": product_id,
            "listed_code": clean(first.get("listed_code", "")),
            "listed_name": clean(first.get("listed_name", "")),
            "registry_item_name": clean(first.get("registry_item_name", "")),
            "registry_application_product": clean(first.get("registry_application_product", "")),
            "verification_type": clean(first.get("verification_type", "")),
            "query_priority": clean(first.get("query_priority", "")),
            "local_traceback_status": clean(first.get("local_traceback_status", "")),
        }
        added_norms: set[str] = set()
        for _, term_row in group.iterrows():
            term = clean(term_row.get("term", ""))
            basis = clean(term_row.get("basis", ""))
            if not is_useful_term(term, basis):
                continue
            norm = v69.normalize_for_match(term)
            if norm in added_norms:
                continue
            added_norms.add(norm)
            priority = {
                "filing_no_exact": 1,
                "item_name_exact": 2,
                "application_product_exact": 3,
                "product_core_exact": 4,
            }.get(basis, 9)
            add_query(rows, base, term, basis, priority)
            if basis in {"item_name_exact", "application_product_exact"}:
                add_query(rows, base, f"{term} 备案", f"{basis}_plus_filing", priority + 10)
                if "大模型" not in term and ("AI" in term or "智能" in term or "GPT" in term):
                    add_query(rows, base, f"{term} 大模型", f"{basis}_plus_model", priority + 11)
                add_query(rows, base, f"{term} 发布", f"{basis}_plus_launch", priority + 12)
        # Keep the plan bounded but preserve exact IDs and names first.
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["query_norm"] = out["query_term"].map(v69.normalize_for_match)
    out = out.drop_duplicates(["registry_product_id", "query_norm"]).copy()
    out = out.sort_values(["query_priority", "listed_code", "registry_product_id", "query_priority_rank", "query_term"])
    out["product_query_order"] = out.groupby("registry_product_id").cumcount() + 1
    out = out[out["product_query_order"].le(8)].copy()
    return out.reset_index(drop=True)


def http_post_json(url: str, data: dict[str, str], timeout: int = 30) -> dict:
    body = urlencode(data).encode("utf-8")
    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            req = Request(
                url,
                data=body,
                headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
                method="POST",
            )
            with urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8", errors="ignore"))
        except Exception as exc:
            last_exc = exc
            time.sleep(0.8 + attempt * 0.5)
    return {"error": str(last_exc), "announcements": [], "totalRecordNum": 0}


def query_cninfo(term: str, scope: dict[str, str], page_num: int) -> dict:
    data = {
        "pageNum": str(page_num),
        "pageSize": str(PAGE_SIZE),
        "column": scope["column"],
        "tabName": "fulltext",
        "plate": scope["plate"],
        "stock": "",
        "searchkey": term,
        "secid": "",
        "category": "",
        "trade": "",
        "seDate": f"{START_DATE}~{END_DATE}",
        "sortName": "",
        "sortType": "",
        "isHLtitle": "true",
    }
    return http_post_json(QUERY_URL, data)


def normalize_announcement(row: dict, query_row: pd.Series, scope: str) -> dict[str, object]:
    adjunct = row.get("adjunctUrl") or ""
    sec_code_raw = str(row.get("secCode") or "")
    title = strip_tags(row.get("announcementTitle") or "")
    return {
        "registry_product_id": clean(query_row.get("registry_product_id", "")),
        "listed_code": clean(query_row.get("listed_code", "")),
        "listed_name": clean(query_row.get("listed_name", "")),
        "query_term": clean(query_row.get("query_term", "")),
        "query_kind": clean(query_row.get("query_kind", "")),
        "query_scope": scope,
        "hit_sec_code": sec_code_raw.zfill(6) if sec_code_raw else "",
        "hit_sec_name": strip_tags(row.get("secName") or ""),
        "announcement_id": str(row.get("announcementId") or ""),
        "announcement_title": title,
        "announcement_date": ts_to_date(row.get("announcementTime")),
        "pdf_url": urljoin(STATIC_BASE, adjunct) if adjunct else "",
        "adjunct_url": adjunct,
        "same_firm": int((sec_code_raw.zfill(6) if sec_code_raw else "") == clean(query_row.get("listed_code", ""))),
        "routine_title": int(bool(HIGH_NOISE_TITLE_RE.search(title))),
        "event_ready_title": int(bool(EVENT_READY_TITLE_RE.search(title)) and not bool(HIGH_NOISE_TITLE_RE.search(title))),
    }


def run_online_pilot(query_terms: pd.DataFrame, limit: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    if limit <= 0 or query_terms.empty:
        return pd.DataFrame(), pd.DataFrame()
    pilot_pool = query_terms[
        query_terms["query_priority"].isin(["P0_no_d1_self_or_registration", "P1_routine_only_needs_backfill", "P2_no_d1_deep_synthesis"])
        & query_terms["query_kind"].isin(["filing_no_exact", "item_name_exact", "application_product_exact", "item_name_exact_plus_filing", "application_product_exact_plus_filing"])
    ].copy()
    pilot_pool = pilot_pool.sort_values(["query_priority", "listed_code", "registry_product_id", "query_priority_rank"]).head(limit)
    hit_rows: list[dict[str, object]] = []
    count_rows: list[dict[str, object]] = []
    for _, query_row in pilot_pool.iterrows():
        term = clean(query_row["query_term"])
        for scope in MARKET_SCOPES:
            first = query_cninfo(term, scope, 1)
            total = int(first.get("totalRecordNum") or 0)
            pages = min(math.ceil(total / PAGE_SIZE), MAX_PAGES_PER_QUERY) if total else 0
            count_rows.append(
                {
                    "registry_product_id": clean(query_row.get("registry_product_id", "")),
                    "listed_code": clean(query_row.get("listed_code", "")),
                    "listed_name": clean(query_row.get("listed_name", "")),
                    "query_term": term,
                    "query_kind": clean(query_row.get("query_kind", "")),
                    "query_scope": scope["scope"],
                    "total": total,
                    "pages_checked": pages,
                    "error": clean(first.get("error", "")),
                }
            )
            payloads = [first] if pages else []
            for page in range(2, pages + 1):
                time.sleep(0.15)
                payloads.append(query_cninfo(term, scope, page))
            for payload in payloads:
                for ann in payload.get("announcements") or []:
                    hit_rows.append(normalize_announcement(ann, query_row, scope["scope"]))
            time.sleep(0.12)
    hits = pd.DataFrame(hit_rows)
    if hits.empty:
        hits = pd.DataFrame(columns=PILOT_HIT_COLUMNS)
    else:
        hits = hits.reindex(columns=PILOT_HIT_COLUMNS)
    if not hits.empty:
        hits = hits.drop_duplicates(["registry_product_id", "announcement_id", "query_term"]).sort_values(
            ["same_firm", "event_ready_title", "announcement_date", "listed_code"],
            ascending=[False, False, True, True],
        )
    counts = pd.DataFrame(count_rows)
    if counts.empty:
        counts = pd.DataFrame(columns=PILOT_COUNT_COLUMNS)
    else:
        counts = counts.reindex(columns=PILOT_COUNT_COLUMNS)
    return hits, counts


def summarize(product_plan: pd.DataFrame, query_terms: pd.DataFrame, pilot_hits: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary = pd.DataFrame(
        [
            {"metric": "registry_products", "value": len(product_plan)},
            {"metric": "listed_firms", "value": product_plan["listed_code"].nunique()},
            {"metric": "query_terms", "value": len(query_terms)},
            {"metric": "products_with_query_terms", "value": query_terms["registry_product_id"].nunique() if not query_terms.empty else 0},
            {"metric": "pilot_raw_hits", "value": len(pilot_hits)},
            {"metric": "pilot_same_firm_hits", "value": int(pilot_hits["same_firm"].sum()) if not pilot_hits.empty else 0},
            {
                "metric": "pilot_same_firm_event_ready_title_hits",
                "value": int(((pilot_hits["same_firm"].eq(1)) & (pilot_hits["event_ready_title"].eq(1))).sum()) if not pilot_hits.empty else 0,
            },
        ]
    )
    by_status = (
        product_plan.groupby(["query_priority", "local_traceback_status", "verification_type"], dropna=False)
        .agg(products=("registry_product_id", "nunique"), firms=("listed_code", "nunique"))
        .reset_index()
        .sort_values(["query_priority", "local_traceback_status", "verification_type"])
    )
    return summary, by_status


def md_table(df: pd.DataFrame, limit: int = 60) -> str:
    if df.empty:
        return "_No rows._"
    show = df.head(limit).copy()
    lines = ["| " + " | ".join(show.columns) + " |", "|" + "|".join("---" for _ in show.columns) + "|"]
    for _, row in show.iterrows():
        lines.append("| " + " | ".join(clean(row[c]).replace("|", "\\|")[:220] for c in show.columns) + " |")
    return "\n".join(lines)


def table_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=columns)
    return df.reindex(columns=columns)


def write_doc(summary: pd.DataFrame, by_status: pd.DataFrame, pilot_hits: pd.DataFrame, query_terms: pd.DataFrame) -> None:
    same_firm = pilot_hits[pilot_hits["same_firm"].eq(1)].copy()
    event_ready = same_firm[same_firm["event_ready_title"].eq(1)].copy()
    lines = [
        "# v71 Targeted CNINFO Search Plan",
        "",
        "## Purpose",
        "",
        "- Creates a bounded targeted CNINFO search plan for all v67 registry firm-products.",
        "- Prioritizes products without event-ready D1 from v69.",
        "- Optional online pilot checks whether exact product queries produce same-firm formal announcements before downloading PDFs.",
        "",
        "## Outputs",
        "",
        f"- `results/{RUN_ID}/targeted_cninfo_product_plan.csv`",
        f"- `results/{RUN_ID}/targeted_cninfo_search_terms.csv`",
        f"- `results/{RUN_ID}/targeted_cninfo_online_pilot_hits.csv`",
        f"- `results/{RUN_ID}/targeted_cninfo_online_pilot_same_firm_hits.csv`",
        f"- `results/{RUN_ID}/targeted_cninfo_online_pilot_query_counts.csv`",
        f"- `results/{RUN_ID}/{RUN_ID}.xlsx`",
        "",
        "## Summary",
        "",
        md_table(summary),
        "",
        "## Product Plan By Status",
        "",
        md_table(by_status, limit=100),
        "",
        "## Pilot Same-Firm Event-Ready Title Hits",
        "",
        md_table(table_columns(event_ready, ["listed_code", "listed_name", "query_term", "query_kind", "announcement_date", "announcement_title", "pdf_url"]), limit=80),
        "",
        "## Pilot Same-Firm Hits",
        "",
        md_table(table_columns(same_firm, ["listed_code", "listed_name", "query_term", "query_kind", "announcement_date", "announcement_title", "event_ready_title", "routine_title", "pdf_url"]), limit=80),
        "",
        "## Query-Term Sample",
        "",
        md_table(query_terms.head(80), limit=80),
        "",
        "## Interpretation",
        "",
        "The pilot is a discovery gate. Same-firm event-ready title hits should be downloaded and passed through the v69 traceback classifier; routine-title hits are useful only as backfill evidence, not event-study dates.",
        "",
    ]
    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--online-pilot", type=int, default=0, help="number of targeted product-query rows to test online")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    product_plan = load_product_plan()
    query_terms = build_query_terms(product_plan)
    pilot_hits, pilot_counts = run_online_pilot(query_terms, args.online_pilot)
    summary, by_status = summarize(product_plan, query_terms, pilot_hits)

    product_plan.to_csv(OUT_DIR / "targeted_cninfo_product_plan.csv", index=False, encoding="utf-8-sig")
    query_terms.to_csv(OUT_DIR / "targeted_cninfo_search_terms.csv", index=False, encoding="utf-8-sig")
    pilot_hits.to_csv(OUT_DIR / "targeted_cninfo_online_pilot_hits.csv", index=False, encoding="utf-8-sig")
    same = pilot_hits[pilot_hits["same_firm"].eq(1)].copy()
    same.to_csv(OUT_DIR / "targeted_cninfo_online_pilot_same_firm_hits.csv", index=False, encoding="utf-8-sig")
    pilot_counts.to_csv(OUT_DIR / "targeted_cninfo_online_pilot_query_counts.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT_DIR / "targeted_cninfo_search_summary.csv", index=False, encoding="utf-8-sig")
    by_status.to_csv(OUT_DIR / "targeted_cninfo_product_plan_by_status.csv", index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(OUT_DIR / f"{RUN_ID}.xlsx") as writer:
        product_plan.to_excel(writer, sheet_name="Product_plan", index=False)
        query_terms.to_excel(writer, sheet_name="Search_terms", index=False)
        summary.to_excel(writer, sheet_name="Summary", index=False)
        by_status.to_excel(writer, sheet_name="By_status", index=False)
        pilot_counts.to_excel(writer, sheet_name="Pilot_counts", index=False)
        pilot_hits.to_excel(writer, sheet_name="Pilot_hits", index=False)
        same.to_excel(writer, sheet_name="Same_firm_hits", index=False)

    write_doc(summary, by_status, pilot_hits, query_terms)
    print("run_id", RUN_ID)
    print(summary.to_string(index=False))
    print("doc", DOC_PATH)


if __name__ == "__main__":
    main()
