#!/usr/bin/env python3
"""Exploratory event-study run from official CAC registry events.

This run treats official registry records as a separate rescue path from the
CNINFO GenAI-announcement sample. It intentionally uses high-confidence A-share
name matching and keeps the event-clock caveat visible in the outputs.
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

import run_v23_cninfo_1055_peer_event_study_20260603 as pe  # noqa: E402


RUN_ID = "v65_registry_based_event_study_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "125_v65_registry_based_event_study_20260612.md"

REGISTRY_PATH = ROOT / "results/v64_official_registry_master_20260612/official_registry_master_genai_relevant_subset.csv"
DEEP_RAW_PATH = ROOT / "data/interim/cac_deep_synthesis_filing_records.csv"
COMPANY_INFO_PATH = (
    Path("/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源")
    / "上市公司财务信息/STK_LISTEDCOINFOANL.xlsx"
)
PEER_NETWORK_PATH = (
    ROOT
    / "results/v22_chinese_literature_product_peers_20260601"
    / "liu_product_tfidf_same_industry_d_peer_network_top20.csv"
)

PREFERRED_METHOD = "liu_product_tfidf_same_industry_d_top10"
MAIN_OUTCOME = "peer_car_0_p1_mm"
MODEL_KEYWORD_RE = re.compile(
    r"大模型|基础模型|语言模型|多模态|AIGC|GPT|ChatGPT|ChatGLM|LLM|DeepSeek|Kimi|"
    r"文心|星火|通义|混元|盘古|豆包|百川|智谱|日日新|天工|MaaS",
    re.I,
)
BAD_PREFIX_NEXT_CHARS = set("市省县区州盟旗镇乡村")
A_SHARE_PREFIXES = ("000", "001", "002", "003", "300", "301", "600", "601", "603", "605", "688")


def z6(value: object) -> str:
    if pd.isna(value):
        return ""
    digits = "".join(ch for ch in str(value).strip().split(".", 1)[0] if ch.isdigit())
    return digits.zfill(6)[-6:] if digits else ""


def clean_name(value: object) -> str:
    text = "" if value is None or pd.isna(value) else str(value)
    text = text.replace("＊", "*")
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[（）()【】\\[\\]·•,，。；;：:、/\\-—_]", "", text)
    return text.strip()


def clean_short(value: object) -> str:
    text = clean_name(value)
    text = re.sub(r"^(?:\\*?ST|S\\*?ST|PT)", "", text, flags=re.I)
    text = re.sub(r"(?:A|B|股份)$", "", text, flags=re.I)
    return text


def p_from_z(z_value: float) -> float:
    return math.erfc(abs(z_value) / math.sqrt(2)) if math.isfinite(z_value) else math.nan


def md_table(df: pd.DataFrame, cols: list[str] | None = None, limit: int = 40) -> str:
    if df.empty:
        return "_No rows._"
    out = df.copy()
    if cols is not None:
        out = out[cols]
    out = out.head(limit).copy()
    for col in out.select_dtypes(include=[np.number]).columns:
        out[col] = out[col].map(lambda x: round(float(x), 6) if pd.notna(x) else x)
    lines = ["| " + " | ".join(out.columns) + " |", "|" + "|".join("---" for _ in out.columns) + "|"]
    for _, row in out.iterrows():
        lines.append("| " + " | ".join("" if pd.isna(row[c]) else str(row[c]).replace("|", "\\|") for c in out.columns) + " |")
    return "\n".join(lines)


def load_company_info() -> pd.DataFrame:
    raw = pd.read_excel(COMPANY_INFO_PATH, dtype=str)
    raw = raw[~raw["Symbol"].isin(["股票代码", "没有单位"])].copy()
    raw["stock_code"] = raw["Symbol"].map(z6)
    raw = raw[raw["stock_code"].str.startswith(A_SHARE_PREFIXES, na=False)].copy()
    raw["info_date"] = pd.to_datetime(raw["EndDate"], errors="coerce")
    raw = raw[raw["stock_code"].ne("")].copy()
    latest = raw.sort_values(["stock_code", "info_date"]).groupby("stock_code", as_index=False).tail(1).copy()
    latest["full_key"] = latest["FullName"].map(clean_name)
    latest["short_key"] = latest["ShortName"].map(clean_short)
    return latest[
        [
            "stock_code",
            "ShortName",
            "FullName",
            "IndustryNameC",
            "IndustryNameD",
            "LISTINGSTATE",
            "full_key",
            "short_key",
        ]
    ].rename(
        columns={
            "ShortName": "stock_name",
            "FullName": "full_name",
            "IndustryNameC": "industry_c",
            "IndustryNameD": "industry_d",
            "LISTINGSTATE": "listing_state",
        }
    )


def load_registry() -> pd.DataFrame:
    reg = pd.read_csv(REGISTRY_PATH, dtype=str, low_memory=False).fillna("")
    if DEEP_RAW_PATH.exists():
        deep = pd.read_csv(DEEP_RAW_PATH, dtype=str, low_memory=False).fillna("")
        deep = deep[["record_no", "notice_create_time", "notice_title"]].drop_duplicates("record_no")
        reg = reg.merge(deep, left_on="filing_no", right_on="record_no", how="left")
    else:
        reg["notice_create_time"] = ""
        reg["notice_title"] = ""
    reg["entity_key"] = reg["entity_name"].map(clean_name)
    reg["filing_date_dt"] = pd.to_datetime(reg["filing_date"], errors="coerce")
    reg["notice_date_dt"] = pd.to_datetime(reg["notice_create_time"], errors="coerce")
    reg["batch_month_dt"] = pd.to_datetime(reg["source_batch"] + "-01", errors="coerce")

    conditions = [
        reg["registry_source"].eq("cac_genai_service") & reg["filing_date_dt"].notna(),
        reg["registry_source"].eq("cac_deep_synthesis_filing") & reg["notice_date_dt"].notna(),
        reg["batch_month_dt"].notna(),
    ]
    choices = [reg["filing_date_dt"], reg["notice_date_dt"], reg["batch_month_dt"]]
    reg["event_date"] = np.select(conditions, choices, default=pd.NaT)
    reg["event_date"] = pd.to_datetime(reg["event_date"], errors="coerce").dt.normalize()
    reg["event_clock"] = np.select(
        conditions,
        ["filing_date_day", "notice_public_day", "batch_month_start_proxy"],
        default="missing",
    )
    text = reg[["item_name", "application_product", "main_purpose", "comments"]].agg(" ".join, axis=1)
    reg["model_keyword_hit"] = text.str.contains(MODEL_KEYWORD_RE, na=False)
    reg["registry_row_id"] = [f"REGROW{i + 1:05d}" for i in range(len(reg))]
    return reg


def candidate_matches(reg: pd.DataFrame, companies: pd.DataFrame) -> pd.DataFrame:
    full_lookup: dict[str, list[dict[str, object]]] = {}
    short_lookup: dict[str, list[dict[str, object]]] = {}
    max_full_len = 0
    max_short_len = 0
    company_records = companies.to_dict("records")
    for c in company_records:
        full_key = str(c.get("full_key") or "")
        short_key = str(c.get("short_key") or "")
        if full_key:
            full_lookup.setdefault(full_key, []).append(c)
            max_full_len = max(max_full_len, len(full_key))
        if short_key:
            short_lookup.setdefault(short_key, []).append(c)
            max_short_len = max(max_short_len, len(short_key))

    def add_candidate(
        out: list[dict[str, object]],
        row_id: str,
        c: dict[str, object],
        method: str,
        rank: int,
        match_len: int,
    ) -> None:
        out.append(
            {
                "registry_row_id": row_id,
                "stock_code": c["stock_code"],
                "stock_name": c["stock_name"],
                "full_name": c["full_name"],
                "industry_c": c["industry_c"],
                "industry_d": c["industry_d"],
                "listing_state": c["listing_state"],
                "match_method": method,
                "match_rank": rank,
                "match_len": match_len,
            }
        )

    rows: list[dict[str, object]] = []
    for r in reg[["registry_row_id", "entity_key"]].to_dict("records"):
        row_id = str(r["registry_row_id"])
        entity = str(r["entity_key"] or "")
        if not entity:
            continue
        for c in full_lookup.get(entity, []):
            add_candidate(rows, row_id, c, "full_name_exact", 100, len(entity))

        seen_full_substrings: set[str] = set()
        full_upper = min(max_full_len, len(entity))
        for length in range(6, full_upper + 1):
            for start in range(0, len(entity) - length + 1):
                part = entity[start : start + length]
                if part in seen_full_substrings:
                    continue
                seen_full_substrings.add(part)
                if part == entity:
                    continue
                for c in full_lookup.get(part, []):
                    add_candidate(rows, row_id, c, "full_name_contained", 90, len(part))

        short_upper = min(max_short_len, len(entity))
        for length in range(3, short_upper + 1):
            prefix = entity[:length]
            next_char = entity[length : length + 1]
            if next_char in BAD_PREFIX_NEXT_CHARS:
                continue
            for c in short_lookup.get(prefix, []):
                add_candidate(rows, row_id, c, "short_name_prefix", 80, length)

        seen_short_substrings: set[str] = set()
        for length in range(4, short_upper + 1):
            for start in range(0, len(entity) - length + 1):
                part = entity[start : start + length]
                if part in seen_short_substrings:
                    continue
                seen_short_substrings.add(part)
                if start == 0:
                    continue
                for c in short_lookup.get(part, []):
                    add_candidate(rows, row_id, c, "short_name_contained_len4", 70, len(part))
    if not rows:
        return pd.DataFrame()
    candidates = pd.DataFrame(rows)
    candidates = candidates.sort_values(["registry_row_id", "match_rank", "match_len"], ascending=[True, False, False])
    best = candidates.groupby("registry_row_id", as_index=False).head(1).copy()
    tied = (
        candidates.merge(best[["registry_row_id", "match_rank", "match_len"]], on=["registry_row_id", "match_rank", "match_len"], how="inner")
        .groupby("registry_row_id")["stock_code"]
        .nunique()
        .rename("best_tie_candidates")
        .reset_index()
    )
    best = best.merge(tied, on="registry_row_id", how="left")
    best = best[best["best_tie_candidates"].eq(1)].copy()
    return best


def build_matched_registry() -> tuple[pd.DataFrame, pd.DataFrame]:
    reg = load_registry()
    companies = load_company_info()
    matches = candidate_matches(reg, companies)
    matched = reg.merge(matches, on="registry_row_id", how="inner")
    matched = matched[matched["event_date"].notna()].copy()
    matched["focal_code"] = matched["stock_code"].map(z6)
    matched["event_year"] = matched["event_date"].dt.year
    matched["snapshot_report_year"] = (matched["event_year"] - 1).clip(lower=2021, upper=2025).astype(int).astype(str)
    matched["source_item_key"] = matched[["registry_source", "filing_no", "item_name", "event_date"]].astype(str).agg("::".join, axis=1)
    return reg, matched


def collapse_events(rows: pd.DataFrame, sample_name: str, first_firm: bool = False) -> pd.DataFrame:
    if rows.empty:
        return pd.DataFrame()
    group_cols = ["focal_code", "event_date"]
    agg = (
        rows.sort_values(["focal_code", "event_date", "registry_source", "filing_no"])
        .groupby(group_cols, as_index=False)
        .agg(
            sec_name=("stock_name", "first"),
            full_name=("full_name", "first"),
            industry_c=("industry_c", "first"),
            industry_d=("industry_d", "first"),
            event_year=("event_year", "first"),
            snapshot_report_year=("snapshot_report_year", "first"),
            filing_rows=("registry_row_id", "nunique"),
            registry_sources=("registry_source", lambda s: ";".join(sorted(set(s)))),
            event_clocks=("event_clock", lambda s: ";".join(sorted(set(s)))),
            match_methods=("match_method", lambda s: ";".join(sorted(set(s)))),
            min_match_rank=("match_rank", "min"),
            item_names=("item_name", lambda s: "；".join(list(dict.fromkeys([str(x) for x in s if str(x)]))[:8])),
            entity_names=("entity_name", lambda s: "；".join(list(dict.fromkeys([str(x) for x in s if str(x)]))[:5])),
            filing_nos=("filing_no", lambda s: "；".join(list(dict.fromkeys([str(x) for x in s if str(x)]))[:8])),
            source_batches=("source_batch", lambda s: ";".join(sorted(set(s)))),
            model_keyword_any=("model_keyword_hit", "max"),
        )
        .copy()
    )
    if first_firm:
        agg = agg.sort_values(["focal_code", "event_date"]).drop_duplicates("focal_code").copy()
    agg = agg.sort_values(["event_date", "focal_code"]).reset_index(drop=True)
    agg["sample_name"] = sample_name
    agg["event_id"] = [f"V65_{sample_name}_{i + 1:04d}_{row.focal_code}_{row.event_date:%Y%m%d}" for i, row in agg.iterrows()]
    agg["event_key"] = agg["sample_name"] + "::" + agg["event_id"]
    return agg


def build_samples(matched: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    defs: list[tuple[str, pd.DataFrame, bool]] = []
    exact = matched[matched["match_method"].eq("full_name_exact")].copy()
    exact_model_like = exact[exact["registry_source"].eq("cac_genai_service") | exact["model_keyword_hit"]].copy()
    genai_service = matched[matched["registry_source"].eq("cac_genai_service") & matched["registry_status"].eq("已备案")].copy()
    deep = matched[matched["registry_source"].eq("cac_deep_synthesis_filing")].copy()
    official = matched.copy()
    model_like = matched[matched["registry_source"].eq("cac_genai_service") | matched["model_keyword_hit"]].copy()
    defs.extend(
        [
            ("S0_exact_official_all", exact, False),
            ("S0_exact_official_first_firm", exact, True),
            ("S0_exact_model_keyword_all", exact_model_like, False),
            ("S0_exact_model_keyword_first_firm", exact_model_like, True),
            ("S1_genai_service_filing_day_all", genai_service, False),
            ("S1_genai_service_filing_day_first_firm", genai_service, True),
            ("S2_deep_synthesis_notice_all", deep, False),
            ("S2_deep_synthesis_notice_first_firm", deep, True),
            ("S3_official_genai_relevant_all", official, False),
            ("S3_official_genai_relevant_first_firm", official, True),
            ("S4_model_keyword_registry_all", model_like, False),
            ("S4_model_keyword_registry_first_firm", model_like, True),
        ]
    )
    events = [collapse_events(df, name, first_firm) for name, df, first_firm in defs]
    events = [e for e in events if not e.empty]
    sample = pd.concat(events, ignore_index=True) if events else pd.DataFrame()
    counts = sample_summary(sample)
    return sample, counts


def sample_summary(sample: pd.DataFrame) -> pd.DataFrame:
    if sample.empty:
        return pd.DataFrame()
    out = (
        sample.groupby("sample_name", as_index=False)
        .agg(
            events=("event_id", "nunique"),
            focal_firms=("focal_code", "nunique"),
            first_date=("event_date", "min"),
            last_date=("event_date", "max"),
            filing_rows=("filing_rows", "sum"),
            model_keyword_events=("model_keyword_any", "sum"),
        )
        .sort_values("sample_name")
    )
    return out


def summarize_returns(panel: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if panel.empty:
        return pd.DataFrame()
    clean = panel[panel["complete_clean_m1_p1"].eq(1)].copy()
    rows: list[dict[str, object]] = []
    for key, d in clean.groupby(group_cols, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        base = dict(zip(group_cols, key))
        for outcome, label in pe.OUTCOMES:
            rows.append({**base, "outcome": outcome, "outcome_label": label, **pe.clustered_mean(d, outcome)})
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(group_cols + ["outcome"]).reset_index(drop=True)


def strict_next_trading_day(date: pd.Timestamp, trading_dates: np.ndarray) -> pd.Timestamp | pd.NaT:
    if pd.isna(date):
        return pd.NaT
    target = np.datetime64(pd.Timestamp(date).normalize())
    pos = int(np.searchsorted(trading_dates, target, side="right"))
    if pos >= len(trading_dates):
        return pd.NaT
    return pd.Timestamp(trading_dates[pos])


def focal_panel(sample: pd.DataFrame, strict_next_day: bool) -> pd.DataFrame:
    stock = pe.load_stock_model()
    out = sample.copy()
    out["peer_code"] = out["focal_code"]
    if strict_next_day:
        trading_dates = np.array(sorted(stock["date"].dropna().unique()), dtype="datetime64[ns]")
        out["date_0"] = out["event_date"].map(lambda x: strict_next_trading_day(x, trading_dates))
    else:
        out = pe.attach_event_trading_dates(out, stock)
    return pe.build_return_measures(out, stock)


def build_peer_panel(sample: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if sample.empty:
        return pd.DataFrame()
    network = pd.read_csv(PEER_NETWORK_PATH, dtype=str)
    network = network[network["peer_rank"].astype(float).le(top_n)].copy()
    network = network.rename(columns={"product_similarity": "peer_similarity"})
    panel = sample.merge(network, on=["snapshot_report_year", "focal_code"], how="inner", suffixes=("", "_net"))
    if panel.empty:
        return panel
    panel["method"] = "liu_product_tfidf_same_industry_d"
    panel["method_top_n"] = top_n
    panel["method_variant"] = PREFERRED_METHOD
    panel["time_valid_prior_year"] = 1
    panel["focal_name"] = panel["sec_name"]
    stock = pe.load_stock_model()
    panel = pe.attach_event_trading_dates(panel, stock)
    panel = pe.build_return_measures(panel, stock)
    return panel


def peer_minus_focal(peer_panel: pd.DataFrame, focal_inclusive: pd.DataFrame) -> pd.DataFrame:
    if peer_panel.empty or focal_inclusive.empty:
        return pd.DataFrame()
    peer = peer_panel[
        peer_panel["method_variant"].eq(PREFERRED_METHOD)
        & peer_panel["complete_clean_m1_p1"].eq(1)
    ].copy()
    foc = focal_inclusive[focal_inclusive["complete_clean_m1_p1"].eq(1)][
        ["sample_name", "event_id", "peer_car_0_p1_mm"]
    ].rename(columns={"peer_car_0_p1_mm": "focal_car"})
    if peer.empty or foc.empty:
        return pd.DataFrame()
    event_peer = (
        peer.groupby(["sample_name", "event_id"], as_index=False)
        .agg(peer_mean_car=("peer_car_0_p1_mm", "mean"), peer_obs=("peer_code", "size"), peer_firms=("peer_code", "nunique"))
    )
    merged = event_peer.merge(foc, on=["sample_name", "event_id"], how="inner")
    merged["peer_minus_focal"] = merged["peer_mean_car"] - merged["focal_car"]
    rows: list[dict[str, object]] = []
    for sample_name, d in merged.groupby("sample_name"):
        vals = d["peer_minus_focal"].astype(float)
        mean = float(vals.mean())
        se = float(vals.std(ddof=1) / math.sqrt(len(vals))) if len(vals) > 1 else math.nan
        z = mean / se if se and se > 0 else math.nan
        rows.append(
            {
                "sample_name": sample_name,
                "events": int(len(vals)),
                "peer_minus_focal_mean": mean,
                "se": se,
                "p": p_from_z(z),
                "median": float(vals.median()),
                "positive_share": float((vals > 0).mean()),
                "mean_peer_car": float(d["peer_mean_car"].mean()),
                "mean_focal_car": float(d["focal_car"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("sample_name")


def matching_summary(reg: pd.DataFrame, matched: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    total = (
        reg.groupby("registry_source", as_index=False)
        .agg(registry_rows=("registry_row_id", "size"), registry_entities=("entity_name", "nunique"))
    )
    got = (
        matched.groupby("registry_source", as_index=False)
        .agg(matched_rows=("registry_row_id", "nunique"), matched_firms=("focal_code", "nunique"))
    )
    summary = total.merge(got, on="registry_source", how="left").fillna({"matched_rows": 0, "matched_firms": 0})
    methods = (
        matched.groupby(["registry_source", "match_method"], as_index=False)
        .agg(rows=("registry_row_id", "nunique"), firms=("focal_code", "nunique"))
        .sort_values(["registry_source", "rows"], ascending=[True, False])
    )
    return summary, methods


def write_doc(
    matched: pd.DataFrame,
    match_cov: pd.DataFrame,
    match_methods: pd.DataFrame,
    sample: pd.DataFrame,
    counts: pd.DataFrame,
    focal_next_summary: pd.DataFrame,
    focal_inclusive_summary: pd.DataFrame,
    peer_summary: pd.DataFrame,
    rel_summary: pd.DataFrame,
) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    main_samples = [
        "S0_exact_official_all",
        "S0_exact_official_first_firm",
        "S0_exact_model_keyword_all",
        "S0_exact_model_keyword_first_firm",
        "S1_genai_service_filing_day_all",
        "S1_genai_service_filing_day_first_firm",
        "S2_deep_synthesis_notice_all",
        "S2_deep_synthesis_notice_first_firm",
        "S3_official_genai_relevant_all",
        "S3_official_genai_relevant_first_firm",
        "S4_model_keyword_registry_all",
        "S4_model_keyword_registry_first_firm",
    ]
    focal_main = focal_next_summary[
        focal_next_summary["sample_name"].isin(main_samples)
        & focal_next_summary["outcome"].isin(["peer_ar0_mm", "peer_ar_p1_mm", "peer_car_0_p1_mm", "peer_car_m1_p1_mm"])
    ].copy()
    focal_incl_main = focal_inclusive_summary[
        focal_inclusive_summary["sample_name"].isin(main_samples)
        & focal_inclusive_summary["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
    ].copy()
    peer_main = peer_summary[
        peer_summary["method_variant"].eq(PREFERRED_METHOD)
        & peer_summary["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
    ].copy()
    example_cols = [
        "sample_name",
        "event_date",
        "focal_code",
        "sec_name",
        "registry_sources",
        "event_clocks",
        "filing_rows",
        "item_names",
        "entity_names",
        "match_methods",
    ]
    lines = [
        "# v65 Registry-Based Official CAC Event Study",
        "",
        "## Scope",
        "",
        "- Input: v64 official CAC GenAI-relevant registry master.",
        "- Matching: high-confidence A-share match from CSMAR listed-company full names and short names. Full legal-name exact matches dominate; short-name matches require prefix or length>=4 containment.",
        "- Event clocks: GenAI service uses record-level filing date; deep-synthesis uses CAC notice publication day; ordinary algorithm uses source-batch month-start proxy. The GenAI service filing-date clock is not necessarily the public disclosure date.",
        "- Returns: same market-model abnormal returns cache as v23/v60/v61.",
        "- Peer network: v22 Liu-style product-text TF-IDF same-industry-d Top10, using prior-year annual-report snapshots capped at 2025.",
        "",
        "## Registry Matching Coverage",
        "",
        md_table(match_cov, limit=20),
        "",
        "## Matching Methods",
        "",
        md_table(match_methods, limit=30),
        "",
        "## Sample Counts",
        "",
        md_table(counts, limit=20),
        "",
        "## Example Events",
        "",
        md_table(sample[example_cols].sort_values(["sample_name", "event_date", "focal_code"]), limit=80),
        "",
        "## Focal Firm Returns, Strict Next Trading Day",
        "",
        md_table(
            focal_main,
            ["sample_name", "outcome_label", "estimate", "se", "p", "nobs", "events", "focal_firms", "median", "positive_share"],
            60,
        ),
        "",
        "## Focal Firm Returns, Existing Event Clock",
        "",
        md_table(
            focal_incl_main,
            ["sample_name", "outcome_label", "estimate", "se", "p", "nobs", "events", "focal_firms", "median", "positive_share"],
            40,
        ),
        "",
        "## Product-Market Peer Returns",
        "",
        md_table(
            peer_main,
            ["sample_name", "outcome_label", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"],
            60,
        ),
        "",
        "## Peer Minus Focal",
        "",
        md_table(rel_summary, limit=30),
        "",
        "## Output Files",
        "",
        f"- `results/{RUN_ID}/registry_matched_a_share_high_confidence.csv`",
        f"- `results/{RUN_ID}/registry_event_samples.csv`",
        f"- `results/{RUN_ID}/focal_returns_strict_next_day_summary.csv`",
        f"- `results/{RUN_ID}/peer_returns_summary.csv`",
        f"- `results/{RUN_ID}/peer_minus_focal_summary.csv`",
        f"- `results/{RUN_ID}/{RUN_ID}.xlsx`",
        "",
        "## Immediate Read",
        "",
        "This is a rescue-path diagnostic, not yet the final paper design. The first useful question is whether a registry event is a credible public information event. Deep-synthesis notice dates are cleaner for that purpose than GenAI service filing dates, because the latter are record-level filing dates inside a periodically updated public attachment.",
        "",
    ]
    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reg, matched = build_matched_registry()
    match_cov, match_methods = matching_summary(reg, matched)
    sample, counts = build_samples(matched)
    if sample.empty:
        raise RuntimeError("No registry event sample could be built.")

    focal_next_panel = focal_panel(sample, strict_next_day=True)
    focal_inclusive_panel = focal_panel(sample, strict_next_day=False)
    focal_next_summary = summarize_returns(focal_next_panel, ["sample_name"])
    focal_inclusive_summary = summarize_returns(focal_inclusive_panel, ["sample_name"])

    peer_panel = build_peer_panel(sample, top_n=10)
    peer_summary = summarize_returns(peer_panel, ["sample_name", "method_variant", "method", "method_top_n", "time_valid_prior_year"])
    rel_summary = peer_minus_focal(peer_panel, focal_inclusive_panel)

    matched.to_csv(OUT_DIR / "registry_matched_a_share_high_confidence.csv", index=False, encoding="utf-8-sig")
    match_cov.to_csv(OUT_DIR / "registry_matching_coverage.csv", index=False, encoding="utf-8-sig")
    match_methods.to_csv(OUT_DIR / "registry_matching_methods.csv", index=False, encoding="utf-8-sig")
    sample.to_csv(OUT_DIR / "registry_event_samples.csv", index=False, encoding="utf-8-sig")
    counts.to_csv(OUT_DIR / "registry_sample_counts.csv", index=False, encoding="utf-8-sig")
    focal_next_panel.to_csv(OUT_DIR / "focal_returns_strict_next_day_panel.csv.gz", index=False)
    focal_next_summary.to_csv(OUT_DIR / "focal_returns_strict_next_day_summary.csv", index=False, encoding="utf-8-sig")
    focal_inclusive_summary.to_csv(OUT_DIR / "focal_returns_existing_event_clock_summary.csv", index=False, encoding="utf-8-sig")
    peer_panel.to_csv(OUT_DIR / "peer_event_panel_with_returns.csv.gz", index=False)
    peer_summary.to_csv(OUT_DIR / "peer_returns_summary.csv", index=False, encoding="utf-8-sig")
    rel_summary.to_csv(OUT_DIR / "peer_minus_focal_summary.csv", index=False, encoding="utf-8-sig")

    xlsx = OUT_DIR / f"{RUN_ID}.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        match_cov.to_excel(writer, sheet_name="Matching_coverage", index=False)
        match_methods.to_excel(writer, sheet_name="Matching_methods", index=False)
        counts.to_excel(writer, sheet_name="Sample_counts", index=False)
        sample.to_excel(writer, sheet_name="Events", index=False)
        focal_next_summary.to_excel(writer, sheet_name="Focal_next", index=False)
        focal_inclusive_summary.to_excel(writer, sheet_name="Focal_inclusive", index=False)
        peer_summary.to_excel(writer, sheet_name="Peer", index=False)
        rel_summary.to_excel(writer, sheet_name="Peer_minus_focal", index=False)

    write_doc(
        matched,
        match_cov,
        match_methods,
        sample,
        counts,
        focal_next_summary,
        focal_inclusive_summary,
        peer_summary,
        rel_summary,
    )

    print(f"wrote {OUT_DIR}", flush=True)
    print(f"wrote {DOC_PATH}", flush=True)
    print("\nMatching coverage:")
    print(match_cov.to_string(index=False), flush=True)
    print("\nSample counts:")
    print(counts.to_string(index=False), flush=True)
    print("\nFocal strict-next CAR[0,+1]:")
    focal_car = focal_next_summary[focal_next_summary["outcome"].eq(MAIN_OUTCOME)]
    print(focal_car[["sample_name", "estimate", "se", "p", "nobs", "events", "focal_firms", "median", "positive_share"]].to_string(index=False), flush=True)
    print("\nProduct-peer CAR[0,+1]:")
    peer_car = peer_summary[peer_summary["outcome"].eq(MAIN_OUTCOME)]
    print(peer_car[["sample_name", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"]].to_string(index=False), flush=True)
    print("\nPeer minus focal:")
    print(rel_summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
