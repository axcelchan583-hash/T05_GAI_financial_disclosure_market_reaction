#!/usr/bin/env python3
"""Specification-grid audit for CNINFO GenAI specificity x product-market peers."""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "measurement"))

import build_genai_disclosure_concreteness as conc  # noqa: E402
import run_specificity_machine_coding_20260525 as machine  # noqa: E402
from run_v23_cninfo_1055_peer_event_study_20260603 import (  # noqa: E402
    build_return_lookup,
    load_stock_model,
    window_sum,
)


RUN_ID = "v24_cninfo_specificity_peer_grid_20260604"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "88_v24_cninfo_specificity_peer_grid_20260604.md"

QIAN_ROOT = ROOT.parent / "T05-qian-supplier-replication-cn"
EVENT_PATH = (
    QIAN_ROOT
    / "results"
    / "v27_cninfo_priority_pdf_audit_2023_2026_20260603"
    / "manual_review_priority_pdf_all.csv"
)
COVERAGE_DIR = ROOT / "results" / "v23_cninfo_1055_peer_coverage_20260603"
EVENT_STUDY_DIR = ROOT / "results" / "v23_cninfo_1055_peer_event_study_20260603"
PEER_PANEL_PATH = COVERAGE_DIR / "peer_link_panel.csv.gz"
RET_PANEL_PATH = EVENT_STUDY_DIR / "peer_event_study_panel_light.csv.gz"
FIRST_DATES_PATH = ROOT / "results" / "v6_external_ai_active_20260524" / "external_ai_evidence_first_dates_by_firm.csv"
HIRING_DAY_PATH = ROOT / "results" / "v6_external_ai_active_20260524" / "external_ai_hiring_firm_day_counts.csv.gz"

OUTCOME = "peer_car_0_p1_mm"
PRE_CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
AI_DEFS = ["ext_any", "current_text_history"]

SPEC_SPECS = [
    ("legacy_detail_density", "legacy_detail_density_raw", "legacy objective detail-density proxy"),
    ("genai_concreteness_raw", "genai_concreteness_raw", "Hope/Cheng-style positive GenAI concreteness density"),
    ("genai_concreteness_resid", "genai_concreteness_resid_z", "Hope/Cheng-style concreteness residualized on text length/month"),
    ("machine_component_sum", "machine_component_sum", "codebook component count"),
    ("machine_specificity_score", "machine_specificity_score_0_4", "codebook 0-4 specificity score"),
    ("auto_action_score", "auto_action_score", "CNINFO action/actor screening score; diagnostic only"),
]

EVENT_DEFS = [
    ("E0_all_1055", "all 1055 CNINFO PDF candidates"),
    ("E1_reviewable_no_denial", "exclude no-fulltext, pure mention, and denial/uncertain labels"),
    ("E2_likely_or_possible", "auto likely Qian initiative or possible initiative"),
    ("E3_likely_only", "auto likely Qian initiative only"),
    ("E4_first_likely_or_possible", "first event per focal firm within E2"),
    ("E5_first_reviewable_no_denial", "first event per focal firm within E1"),
]


DETAIL_PATTERNS = {
    "dates": r"(?:20[2-9]\d年\d{0,2}月?\d{0,2}日?|20[2-9]\d[-/]\d{1,2}[-/]\d{1,2}|[一二三四1234]季度|Q[1-4])",
    "money": r"\d+(?:\.\d+)?(?:亿元|万元|元|万美元|美元|人民币)",
    "percent": r"\d+(?:\.\d+)?(?:%|％)",
    "numbers": r"\d+(?:\.\d+)?(?:个|项|款|台|套|人|家|年|月|日|亿|万|次|小时|天|倍|G|GB|TB|亿参数|参数)?",
    "quoted_names": r"[“《][^”》]{2,40}[”》]",
    "orgs": r"[\u4e00-\u9fa5A-Za-z0-9]{2,35}(?:公司|集团|大学|研究院|实验室|中心|平台|科技|智能|网络|银行|医院)",
    "partners": r"(?:华为|百度|阿里|腾讯|科大讯飞|智谱|商汤|字节|DeepSeek|OpenAI|微软|英伟达|通义|文心|Kimi|月之暗面|百川|MiniMax|芒果超媒)",
    "stage": r"(?:已上线|已发布|已备案|已通过|已落地|已部署|已接入|签署|合作|共建|推出|发布|升级|备案通过|内测|公测|商业化|量产|交付)",
}


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if "." in text:
        text = text.split(".", 1)[0]
    digits = "".join(ch for ch in text if ch.isdigit())
    return digits.zfill(6)[-6:] if digits else ""


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def zscore(series: pd.Series) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce").astype(float)
    std = x.std(ddof=0)
    if not np.isfinite(std) or std == 0:
        return pd.Series(np.nan, index=series.index)
    return (x - x.mean()) / std


def winsorize(series: pd.Series, lo: float = 0.01, hi: float = 0.99) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce").astype(float)
    if x.notna().sum() < 10:
        return x
    return x.clip(x.quantile(lo), x.quantile(hi))


def p_from_z(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2)) if math.isfinite(z) else math.nan


def markdown_table(df: pd.DataFrame, cols: list[str], limit: int = 12) -> str:
    if df.empty:
        return "_No rows._"
    out = df[cols].head(limit).copy()
    for col in out.select_dtypes(include=[np.number]).columns:
        out[col] = out[col].map(lambda x: round(float(x), 6) if pd.notna(x) else x)
    rows = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, row in out.iterrows():
        rows.append("| " + " | ".join("" if pd.isna(row[c]) else str(row[c]) for c in cols) + " |")
    return "\n".join(rows)


def legacy_detail_density(text: str) -> dict[str, float | int]:
    genai_sentences = conc.extract_genai_sentences(text)
    span = " ".join(genai_sentences) if genai_sentences else text[:1500]
    compact = re.sub(r"\s+", "", span)
    token_count = max(1, len(re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9]+", compact)))
    counts = {k: len(re.findall(pat, compact, flags=re.I)) for k, pat in DETAIL_PATTERNS.items()}
    specific_items = int(sum(counts.values()))
    return {
        **counts,
        "legacy_specific_items": specific_items,
        "legacy_genai_span_tokens": int(token_count),
        "legacy_detail_density_raw": 100 * specific_items / token_count,
    }


def choose_event_text(row: pd.Series) -> str:
    pieces = [
        clean_text(row.get("pdf_genai_context", "")),
        clean_text(row.get("action_snippet", "")),
        clean_text(row.get("announcement_content", "")),
        clean_text(row.get("announcement_title", "")),
    ]
    return next((p for p in pieces if p), "")


def concreteness_one(event_id: str, focal_code: str, event_date: pd.Timestamp, text: str) -> dict[str, object]:
    genai_sentences = conc.extract_genai_sentences(text)
    genai_text = " ".join(genai_sentences)
    counted_sentences = [s for s in genai_sentences if conc.has_positive_genai_claim(s)]
    counted_genai_text = " ".join(counted_sentences)
    tokens = conc.tokenize(counted_genai_text)
    token_count = len(tokens)
    char_count = len(re.sub(r"\s+", "", counted_genai_text))
    ai_keyword_count = conc.count_ai_keywords(genai_text)
    entity_terms = conc.entity_concrete_terms(counted_genai_text)
    entity_count = len(entity_terms)
    operational_count = conc.operational_concrete_count(counted_genai_text)
    quant_count = conc.quant_concrete_count(counted_genai_text)
    positive_genai_claim = int(bool(counted_sentences))
    denial_or_no_exposure = int(conc.has_denial_or_no_exposure(genai_text) and not positive_genai_claim)
    if denial_or_no_exposure or not positive_genai_claim:
        entity_terms = []
        entity_count = 0
        operational_count = 0
        quant_count = 0
    total_count = entity_count + operational_count + quant_count
    classifications = conc.classify_content(
        genai_text,
        entity_count,
        operational_count,
        quant_count,
        denial_or_no_exposure=denial_or_no_exposure,
        positive_genai_claim=positive_genai_claim,
    )
    return {
        "event_id": event_id,
        "focal_code": focal_code,
        "event_date": event_date.strftime("%Y-%m-%d") if pd.notna(event_date) else "",
        "genai_text": genai_text,
        "counted_genai_text": counted_genai_text,
        "genai_sentence_count": len(genai_sentences),
        "positive_genai_sentence_count": len(counted_sentences),
        "genai_token_count": token_count,
        "genai_char_count": char_count,
        "ai_keyword_count": ai_keyword_count,
        "entity_concrete_count": entity_count,
        "operational_concrete_count": operational_count,
        "quant_concrete_count": quant_count,
        "total_concrete_count": total_count,
        "entity_terms": ";".join(entity_terms),
        "entity_concrete_density": entity_count / max(token_count, 1),
        "operational_concrete_density": operational_count / max(token_count, 1),
        "quant_concrete_density": quant_count / max(token_count, 1),
        "genai_concreteness_raw": total_count / max(token_count, 1),
        "genai_concreteness_char_density": total_count / max(char_count, 1),
        **classifications,
    }


def machine_one(event_id: str, text: str) -> dict[str, object]:
    row = pd.Series({"validation_id": event_id, "event_id": event_id, "sample_answer": text})
    out = machine.code_one(row)
    keep = [
        "machine_component_sum",
        "machine_specificity_score_0_4",
        "machine_uncertain_flag",
        "machine_evidence_snippet",
        "machine_coder_notes",
    ]
    return {k: out.get(k) for k in keep}


def load_events_with_specificity() -> pd.DataFrame:
    raw = pd.read_csv(EVENT_PATH, dtype=str, low_memory=False)
    raw["event_id"] = raw["announcement_id"].fillna("").astype(str)
    raw["focal_code"] = raw["sec_code"].map(code6)
    raw["event_date"] = pd.to_datetime(raw["manual_event_date_corrected"].where(
        raw["manual_event_date_corrected"].notna() & raw["manual_event_date_corrected"].astype(str).str.strip().ne(""),
        raw["announcement_date"],
    ), errors="coerce")
    raw["event_key"] = "all_1055::" + raw["event_id"].astype(str)
    raw["event_text_for_specificity"] = raw.apply(choose_event_text, axis=1)
    raw["auto_pdf_label"] = raw["auto_pdf_label"].fillna("unknown")
    for col in [
        "auto_keep_likely_qian",
        "title_event_flag",
        "context_action_flag",
        "full_action_flag",
        "company_actor_flag",
        "denial_or_uncertain_flag",
        "attention_only_flag",
        "qian_recall_score",
    ]:
        raw[col] = pd.to_numeric(raw.get(col, 0), errors="coerce").fillna(0)
    raw["auto_action_score"] = (
        raw["auto_keep_likely_qian"]
        + raw["title_event_flag"]
        + raw["context_action_flag"]
        + raw["full_action_flag"]
        + raw["company_actor_flag"]
        - raw["denial_or_uncertain_flag"]
        - raw["attention_only_flag"]
        + raw["qian_recall_score"] / 10.0
    )

    rows: list[dict[str, object]] = []
    for _, row in raw.iterrows():
        text = clean_text(row["event_text_for_specificity"])
        event_id = clean_text(row["event_id"])
        focal_code = clean_text(row["focal_code"])
        event_date = row["event_date"]
        rows.append(
            {
                "event_id": event_id,
                **legacy_detail_density(text),
                **concreteness_one(event_id, focal_code, event_date, text),
                **machine_one(event_id, text),
            }
        )
    measures = pd.DataFrame(rows)
    measures["event_year"] = pd.to_datetime(measures["event_date"], errors="coerce").dt.year
    measures["event_year_month"] = pd.to_datetime(measures["event_date"], errors="coerce").dt.to_period("M").astype(str)
    measures["genai_concreteness_z"] = zscore(measures["genai_concreteness_raw"])
    measures["genai_concreteness_z_by_year"] = measures.groupby("event_year", dropna=False)["genai_concreteness_raw"].transform(zscore)
    measures["genai_concreteness_resid_z"] = conc.residualized_z(measures)

    keep_cols = [
        "event_id",
        "event_key",
        "focal_code",
        "sec_name",
        "event_date",
        "announcement_title",
        "auto_pdf_label",
        "auto_action_score",
        "auto_keep_likely_qian",
        "title_event_flag",
        "context_action_flag",
        "full_action_flag",
        "company_actor_flag",
        "denial_or_uncertain_flag",
        "attention_only_flag",
        "event_text_for_specificity",
    ]
    event_info = raw[keep_cols].merge(measures.drop(columns=["focal_code", "event_date"]), on="event_id", how="left")
    for name, raw_col, _ in SPEC_SPECS:
        event_info[f"{name}_z_global"] = zscore(winsorize(event_info[raw_col]))
    return event_info


def event_definition_mask(events: pd.DataFrame, definition: str) -> pd.Series:
    label = events["auto_pdf_label"].fillna("unknown")
    reviewable = ~label.isin(
        [
            "review_denial_or_uncertain",
            "exclude_mention_without_initiative",
            "exclude_no_fulltext_genai",
        ]
    )
    likely_possible = label.isin(["likely_qian_initiative", "review_possible_initiative"])
    likely = label.eq("likely_qian_initiative")
    if definition == "E0_all_1055":
        return pd.Series(True, index=events.index)
    if definition == "E1_reviewable_no_denial":
        return reviewable
    if definition == "E2_likely_or_possible":
        return likely_possible
    if definition == "E3_likely_only":
        return likely
    if definition == "E4_first_likely_or_possible":
        base = likely_possible
    elif definition == "E5_first_reviewable_no_denial":
        base = reviewable
    else:
        raise ValueError(definition)
    tmp = events[base].sort_values(["focal_code", "event_date", "event_id"]).drop_duplicates("focal_code")
    return events["event_key"].isin(tmp["event_key"])


def load_peer_return_panel(events: pd.DataFrame) -> pd.DataFrame:
    ret = pd.read_csv(RET_PANEL_PATH, dtype={"focal_code": str, "peer_code": str, "event_id": str}, low_memory=False)
    ret = ret[ret["sample_name"].eq("all_1055")].copy()
    cov = pd.read_csv(
        PEER_PANEL_PATH,
        usecols=[
            "sample_name",
            "method_variant",
            "event_key",
            "peer_code",
            "peer_industry_d",
            "focal_industry_d",
        ],
        dtype={"peer_code": str},
        low_memory=False,
    )
    cov = cov[cov["sample_name"].eq("all_1055")].drop_duplicates(["method_variant", "event_key", "peer_code"])
    panel = ret.merge(
        cov[["method_variant", "event_key", "peer_code", "peer_industry_d", "focal_industry_d"]],
        on=["method_variant", "event_key", "peer_code"],
        how="left",
    )
    panel = panel.merge(
        events[
            [
                "event_key",
                "auto_pdf_label",
                "legacy_detail_density_raw",
                "genai_concreteness_raw",
                "genai_concreteness_resid_z",
                "machine_component_sum",
                "machine_specificity_score_0_4",
                "auto_action_score",
            ]
        ],
        on="event_key",
        how="left",
        suffixes=("", "_event"),
    )
    panel["date_0"] = pd.to_datetime(panel["date_0"], errors="coerce")
    panel["event_date"] = pd.to_datetime(panel["event_date"], errors="coerce")
    panel["event_week"] = panel["date_0"].dt.strftime("%Y-%U")
    panel["peer_industry_d"] = panel["peer_industry_d"].fillna("UNKNOWN").astype(str)
    panel["peer_industry_week"] = panel["peer_industry_d"] + "|" + panel["event_week"].fillna("")
    panel["focal_industry_d"] = panel["focal_industry_d"].fillna("UNKNOWN").astype(str)
    panel["focal_industry_week"] = panel["focal_industry_d"] + "|" + panel["event_week"].fillna("")
    return panel


def add_prewindows(panel: pd.DataFrame) -> pd.DataFrame:
    stock = load_stock_model()
    lookup = build_return_lookup(stock)
    pairs = panel[["peer_code", "date_0"]].drop_duplicates().copy()
    rows = []
    for code, date0 in zip(pairs["peer_code"], pairs["date_0"]):
        pre10, obs10, ok10 = window_sum(lookup, code, pd.Timestamp(date0), -10, -2, 7)
        pre20, obs20, ok20 = window_sum(lookup, code, pd.Timestamp(date0), -20, -2, 15)
        rows.append(
            {
                "peer_code": code,
                "date_0": date0,
                "peer_car_pre10_m2_mm": pre10,
                "peer_car_pre20_m2_mm": pre20,
                "obs_peer_car_pre10_m2_mm": obs10,
                "obs_peer_car_pre20_m2_mm": obs20,
                "ok_peer_car_pre10_m2_mm": ok10,
                "ok_peer_car_pre20_m2_mm": ok20,
            }
        )
    return panel.merge(pd.DataFrame(rows), on=["peer_code", "date_0"], how="left")


def load_first_dates() -> pd.DataFrame:
    df = pd.read_csv(FIRST_DATES_PATH, dtype={"stock_code": str})
    df["stock_code"] = df["stock_code"].map(code6)
    for col in [c for c in df.columns if c.endswith("_date")]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df.set_index("stock_code")


def load_hiring_lookup() -> dict[str, dict[str, np.ndarray]]:
    df = pd.read_csv(HIRING_DAY_PATH, dtype={"stock_code": str}, parse_dates=["post_date"])
    df["stock_code"] = df["stock_code"].map(code6)
    out: dict[str, dict[str, np.ndarray]] = {}
    for code, sub in df.sort_values(["stock_code", "post_date"]).groupby("stock_code", sort=False):
        dates = sub["post_date"].to_numpy(dtype="datetime64[ns]")
        broad = pd.to_numeric(sub["broad_ai_hiring_count"], errors="coerce").fillna(0).to_numpy(dtype=float)
        genai = pd.to_numeric(sub["genai_hiring_count"], errors="coerce").fillna(0).to_numpy(dtype=float)
        out[code] = {"dates": dates, "broad_cum": np.cumsum(broad), "genai_cum": np.cumsum(genai)}
    return out


def count_between(rec: dict[str, np.ndarray] | None, start: np.datetime64, end: np.datetime64, key: str) -> float:
    if rec is None:
        return 0.0
    dates = rec["dates"]
    if len(dates) == 0:
        return 0.0
    cum = rec[key]
    right = np.searchsorted(dates, end, side="right")
    left = np.searchsorted(dates, start, side="left")
    if right <= left:
        return 0.0
    return float(cum[right - 1] - (cum[left - 1] if left > 0 else 0.0))


def add_ai_active(panel: pd.DataFrame) -> pd.DataFrame:
    first_dates = load_first_dates()
    hiring = load_hiring_lookup()
    out = panel.copy()
    peer = out["peer_code"].astype(str).str.zfill(6)
    cutoff = pd.to_datetime(out["event_date"], errors="coerce") - pd.Timedelta(days=5)
    joined = first_dates.reindex(peer.to_numpy())
    for flag, date_col in {
        "prior_cac": "cac_first_date",
        "prior_ai_patent_grant": "ai_patent_grant_first_date",
        "prior_genai_patent_grant": "genai_patent_grant_first_date",
        "current_text_history": "history_genai_disclosure_first_date",
    }.items():
        dates = pd.to_datetime(joined[date_col], errors="coerce").reset_index(drop=True)
        out[flag] = (dates.notna() & dates.le(cutoff.reset_index(drop=True))).astype(int).to_numpy()
    broad365 = []
    genai365 = []
    for code, cut in zip(peer, cutoff):
        if pd.isna(cut):
            broad365.append(0.0)
            genai365.append(0.0)
            continue
        end = np.datetime64(pd.Timestamp(cut).normalize())
        start365 = np.datetime64((pd.Timestamp(cut) - pd.Timedelta(days=365)).normalize())
        rec = hiring.get(code)
        broad365.append(count_between(rec, start365, end, "broad_cum"))
        genai365.append(count_between(rec, start365, end, "genai_cum"))
    out["prior_broad_ai_hiring_365_count"] = broad365
    out["prior_genai_hiring_365_count"] = genai365
    out["prior_broad_ai_hiring_365_ge1"] = (out["prior_broad_ai_hiring_365_count"] >= 1).astype(int)
    out["prior_broad_ai_hiring_365_ge3"] = (out["prior_broad_ai_hiring_365_count"] >= 3).astype(int)
    out["prior_genai_hiring_365_ge1"] = (out["prior_genai_hiring_365_count"] >= 1).astype(int)
    out["ext_no_hiring"] = (out["prior_cac"].eq(1) | out["prior_ai_patent_grant"].eq(1)).astype(int)
    out["ext_any"] = (
        out["prior_cac"].eq(1) | out["prior_ai_patent_grant"].eq(1) | out["prior_broad_ai_hiring_365_ge1"].eq(1)
    ).astype(int)
    out["ext_plus_history"] = (out["ext_any"].eq(1) | out["current_text_history"].eq(1)).astype(int)
    return out


def absorb_frame(df: pd.DataFrame, cols: list[str], fe_cols: list[str], iterations: int = 8) -> pd.DataFrame:
    mat = df[cols].astype(float).copy()
    for _ in range(iterations):
        for fe in fe_cols:
            codes = df[fe].fillna("MISSING").astype(str)
            mat = mat - mat.groupby(codes).transform("mean")
    return mat


def cluster_meat(x: np.ndarray, resid: np.ndarray, groups: pd.Series) -> np.ndarray:
    score = pd.DataFrame(x * resid[:, None])
    score["_g"] = groups.fillna("MISSING").astype(str).to_numpy()
    summed = score.groupby("_g").sum().to_numpy()
    return summed.T @ summed


def fit_absorbed_ols(
    data: pd.DataFrame,
    outcome: str,
    xvars: list[str],
    fe_cols: list[str],
    term_focus: str,
) -> dict[str, object] | None:
    need = [outcome, *xvars, "event_key", "peer_code", *fe_cols]
    d = data.dropna(subset=need).copy()
    if len(d) < 80 or d["event_key"].nunique() < 8 or d["peer_code"].nunique() < 20:
        return None
    dm = absorb_frame(d, [outcome, *xvars], fe_cols)
    y = dm[outcome].to_numpy(dtype=float)
    x = dm[xvars].to_numpy(dtype=float)
    focus_idx = xvars.index(term_focus)
    if np.nanstd(x[:, focus_idx]) < 1e-12:
        return None
    xtx = x.T @ x
    bread = np.linalg.pinv(xtx)
    beta = bread @ (x.T @ y)
    resid = y - x @ beta
    meat_event = cluster_meat(x, resid, d["event_key"])
    meat_peer = cluster_meat(x, resid, d["peer_code"])
    pair_group = d["event_key"].astype(str) + "|" + d["peer_code"].astype(str)
    meat_pair = cluster_meat(x, resid, pair_group)
    cov = bread @ (meat_event + meat_peer - meat_pair) @ bread
    var = float(cov[focus_idx, focus_idx])
    se = math.sqrt(var) if var >= 0 else math.nan
    coef = float(beta[focus_idx])
    z = coef / se if se and se > 0 else math.nan
    return {
        "coef": coef,
        "se": se,
        "z": z,
        "p": p_from_z(z),
        "nobs": int(len(d)),
        "events": int(d["event_key"].nunique()),
        "focal_firms": int(d["focal_code"].nunique()),
        "peer_firms": int(d["peer_code"].nunique()),
        "mean_y": float(d[outcome].mean()),
        "sd_focus": float(d[term_focus].std(ddof=0)),
        "mean_focus": float(d[term_focus].mean()),
    }


def bh_qvalues(pvals: pd.Series) -> pd.Series:
    p = pd.to_numeric(pvals, errors="coerce")
    q = pd.Series(np.nan, index=p.index)
    valid = p.dropna().sort_values()
    m = len(valid)
    if m == 0:
        return q
    vals = valid.to_numpy()
    adjusted = np.empty(m)
    running = 1.0
    for i in range(m - 1, -1, -1):
        running = min(running, vals[i] * m / (i + 1))
        adjusted[i] = running
    q.loc[valid.index] = adjusted
    return q


def build_event_definitions(events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, label in EVENT_DEFS:
        mask = event_definition_mask(events, name)
        sub = events[mask].copy()
        rows.append(
            {
                "event_def": name,
                "event_def_label": label,
                "events": int(sub["event_key"].nunique()),
                "focal_firms": int(sub["focal_code"].nunique()),
                "likely_events": int(sub["auto_pdf_label"].eq("likely_qian_initiative").sum()),
                "possible_events": int(sub["auto_pdf_label"].eq("review_possible_initiative").sum()),
                "denial_events": int(sub["auto_pdf_label"].eq("review_denial_or_uncertain").sum()),
            }
        )
    return pd.DataFrame(rows)


def run_grid(panel: pd.DataFrame, events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sample_rows = []
    hetero_rows = []
    average_rows = []
    methods = sorted(panel["method_variant"].dropna().unique())
    event_sets = {name: set(events.loc[event_definition_mask(events, name), "event_key"]) for name, _ in EVENT_DEFS}
    for event_def, event_keys in event_sets.items():
        event_sub = events[events["event_key"].isin(event_keys)].copy()
        spec_z: dict[str, pd.Series] = {}
        for spec_name, raw_col, _ in SPEC_SPECS:
            spec_z[spec_name] = zscore(winsorize(event_sub[raw_col]))
        z_map = {
            spec_name: pd.Series(vals.to_numpy(), index=event_sub["event_key"]).to_dict()
            for spec_name, vals in spec_z.items()
        }
        for method in methods:
            d0 = panel[panel["method_variant"].eq(method) & panel["event_key"].isin(event_keys)].copy()
            d0 = d0[d0["complete_clean_m1_p1"].eq(1)].copy()
            d0 = d0.dropna(subset=[OUTCOME, *PRE_CONTROLS, "peer_industry_week", "event_week"])
            if d0.empty:
                continue
            sample_rows.append(
                {
                    "event_def": event_def,
                    "method_variant": method,
                    "time_valid_prior_year": int(d0["time_valid_prior_year"].max()),
                    "nobs": int(len(d0)),
                    "events": int(d0["event_key"].nunique()),
                    "focal_firms": int(d0["focal_code"].nunique()),
                    "peer_firms": int(d0["peer_code"].nunique()),
                    "mean_y": float(d0[OUTCOME].mean()),
                    "mean_ext_any": float(d0["ext_any"].mean()),
                    "mean_text_history": float(d0["current_text_history"].mean()),
                }
            )
            for spec_name, _, spec_label in SPEC_SPECS:
                d = d0.copy()
                d["spec_z"] = d["event_key"].map(z_map[spec_name])
                if d["spec_z"].notna().sum() < 30 or d["spec_z"].std(ddof=0) == 0:
                    continue
                avg = fit_absorbed_ols(
                    d,
                    OUTCOME,
                    ["spec_z", *PRE_CONTROLS],
                    ["event_week", "peer_industry_week"],
                    term_focus="spec_z",
                )
                if avg is not None:
                    average_rows.append(
                        {
                            "event_def": event_def,
                            "method_variant": method,
                            "specificity": spec_name,
                            "specificity_label": spec_label,
                            "model": "average_specificity_week_peerindustry_fe",
                            "term": "spec_z",
                            **avg,
                        }
                    )
                for ai_def in AI_DEFS:
                    d["ai"] = d[ai_def].fillna(0).astype(float)
                    d["spec_ai"] = d["spec_z"] * d["ai"]
                    res = fit_absorbed_ols(
                        d,
                        OUTCOME,
                        ["ai", "spec_ai", *PRE_CONTROLS],
                        ["event_key", "peer_industry_week"],
                        term_focus="spec_ai",
                    )
                    if res is None:
                        continue
                    hetero_rows.append(
                        {
                            "event_def": event_def,
                            "method_variant": method,
                            "time_valid_prior_year": int(d0["time_valid_prior_year"].max()),
                            "specificity": spec_name,
                            "specificity_label": spec_label,
                            "ai_def": ai_def,
                            "model": "specificity_x_ai_event_peerindustry_fe",
                            "term": "spec_ai",
                            **res,
                        }
                    )
    sample = pd.DataFrame(sample_rows)
    hetero = pd.DataFrame(hetero_rows)
    average = pd.DataFrame(average_rows)
    if not hetero.empty:
        hetero["q_bh_all"] = bh_qvalues(hetero["p"])
        hetero["abs_t"] = (hetero["coef"] / hetero["se"]).abs()
    if not average.empty:
        average["q_bh_all"] = bh_qvalues(average["p"])
        average["abs_t"] = (average["coef"] / average["se"]).abs()
    return sample, hetero, average


def write_doc(
    event_defs: pd.DataFrame,
    sample: pd.DataFrame,
    hetero: pd.DataFrame,
    average: pd.DataFrame,
    spec_summary: pd.DataFrame,
) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    main_prior = hetero[hetero["time_valid_prior_year"].eq(1)].copy()
    main_prior = main_prior.sort_values(["p", "event_def", "method_variant"])
    stable = (
        main_prior.groupby(["event_def", "specificity", "ai_def"], as_index=False)
        .agg(
            tests=("p", "size"),
            sig_10=("p", lambda x: int((x < 0.10).sum())),
            sig_05=("p", lambda x: int((x < 0.05).sum())),
            median_coef=("coef", "median"),
            positive_share=("coef", lambda x: float((x > 0).mean())),
            min_p=("p", "min"),
            median_p=("p", "median"),
        )
        .sort_values(["sig_05", "sig_10", "min_p"], ascending=[False, False, True])
    )
    avg_prior = average.sort_values(["p", "event_def", "method_variant"])

    lines = [
        "# v24 CNINFO specificity x peer grid",
        "",
        "## Purpose",
        "",
        "This run tests combinations of GenAI-event definitions, product-market peer definitions, and event-level specificity measures on the CNINFO 1055 PDF event library.",
        "The headline grid is `Specificity_z x AIActivePeer -> PeerCAR[0,+1]` with event fixed effects and peer-industry-week fixed effects.",
        "",
        "## Event Definitions",
        "",
        markdown_table(event_defs, ["event_def", "events", "focal_firms", "likely_events", "possible_events", "denial_events"], 10),
        "",
        "## Specificity Measures",
        "",
        markdown_table(
            spec_summary,
            ["specificity", "mean", "sd", "p05", "p50", "p95", "nonmissing"],
            10,
        ),
        "",
        "## Best Strict Prior-Year Heterogeneity Results",
        "",
        markdown_table(
            main_prior,
            ["event_def", "method_variant", "specificity", "ai_def", "coef", "se", "p", "q_bh_all", "nobs", "events", "peer_firms"],
            20,
        ),
        "",
        "## Current Verdict",
        "",
        "- The peer lane has enough sample after switching to CNINFO events; the core issue is measurement choice, not coverage.",
        "- The most interpretable strict prior-year signal is `legacy_detail_density x ext_any` under `E2_likely_or_possible` and `E4_first_likely_or_possible`: coefficients are mostly negative and appear across several product-peer variants.",
        "- `auto_action_score x current_text_history` is often positive and significant, but it overlaps with event-screening rules and should stay diagnostic rather than become the paper's publishable specificity measure.",
        "- `E3_likely_only` is too small for model selection: it produces very sharp results, but signs flip across specificity measures and peer systems.",
        "- Event-level average-effect tables are not the main design because they cannot use event fixed effects and even placebo peer systems can become significant.",
        "",
        "## Stability by Event Definition and X",
        "",
        markdown_table(
            stable,
            ["event_def", "specificity", "ai_def", "tests", "sig_05", "sig_10", "median_coef", "positive_share", "min_p", "median_p"],
            24,
        ),
        "",
        "## Event-Level Specificity Average Effect",
        "",
        markdown_table(
            avg_prior,
            ["event_def", "method_variant", "specificity", "coef", "se", "p", "q_bh_all", "nobs", "events", "peer_firms"],
            20,
        ),
        "",
        "## Reading",
        "",
        "- Treat this as a specification audit, not a final model-selection exercise.",
        "- A usable T05 main effect should survive across event definitions and peer definitions, not merely appear in one high-dimensional combination.",
        "- `auto_action_score` is diagnostic because it partly overlaps with event screening; it should not be the publishable specificity X.",
        "- Static LLM/semantic peer networks remain diagnostics unless rebuilt as rolling/as-of peer sets.",
        "",
        "## Output Files",
        "",
        f"- `{OUT_DIR.relative_to(ROOT)}/event_specificity_measures.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/grid_sample_summary.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/grid_heterogeneity_regressions.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/grid_average_regressions.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/grid_stability_by_x.csv`",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def specificity_summary(events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for spec_name, raw_col, _ in SPEC_SPECS:
        x = pd.to_numeric(events[raw_col], errors="coerce")
        rows.append(
            {
                "specificity": spec_name,
                "mean": float(x.mean()),
                "sd": float(x.std(ddof=0)),
                "p05": float(x.quantile(0.05)),
                "p50": float(x.quantile(0.50)),
                "p95": float(x.quantile(0.95)),
                "nonmissing": int(x.notna().sum()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Building event-level specificity measures...", flush=True)
    events = load_events_with_specificity()
    event_defs = build_event_definitions(events)
    spec_sum = specificity_summary(events)
    events.to_csv(OUT_DIR / "event_specificity_measures.csv", index=False)
    event_defs.to_csv(OUT_DIR / "event_definition_summary.csv", index=False)
    spec_sum.to_csv(OUT_DIR / "specificity_measure_summary.csv", index=False)
    print(event_defs.to_string(index=False), flush=True)

    print("Loading peer return panel...", flush=True)
    panel = load_peer_return_panel(events)
    print(f"Panel before prewindows: {len(panel):,} rows, {panel['method_variant'].nunique()} peer variants", flush=True)
    panel = add_prewindows(panel)
    print("Attaching AIActivePeer definitions...", flush=True)
    panel = add_ai_active(panel)

    light_cols = [
        "sample_name",
        "method_variant",
        "method",
        "method_top_n",
        "time_valid_prior_year",
        "event_id",
        "event_key",
        "focal_code",
        "event_date",
        "date_0",
        "event_week",
        "peer_code",
        "peer_name",
        "peer_rank",
        "peer_industry_d",
        "peer_industry_week",
        "focal_industry_d",
        "focal_industry_week",
        "auto_pdf_label",
        "complete_clean_m1_p1",
        OUTCOME,
        *PRE_CONTROLS,
        *AI_DEFS,
        "ext_no_hiring",
        "ext_plus_history",
    ]
    panel[light_cols].to_csv(OUT_DIR / "analysis_panel_with_specificity_ai.csv.gz", index=False)

    print("Running specification grid...", flush=True)
    sample, hetero, average = run_grid(panel, events)
    sample.to_csv(OUT_DIR / "grid_sample_summary.csv", index=False)
    hetero.to_csv(OUT_DIR / "grid_heterogeneity_regressions.csv", index=False)
    average.to_csv(OUT_DIR / "grid_average_regressions.csv", index=False)

    if not hetero.empty:
        stability = (
            hetero[hetero["time_valid_prior_year"].eq(1)]
            .groupby(["event_def", "specificity", "ai_def"], as_index=False)
            .agg(
                tests=("p", "size"),
                sig_10=("p", lambda x: int((x < 0.10).sum())),
                sig_05=("p", lambda x: int((x < 0.05).sum())),
                median_coef=("coef", "median"),
                positive_share=("coef", lambda x: float((x > 0).mean())),
                min_p=("p", "min"),
                median_p=("p", "median"),
            )
            .sort_values(["sig_05", "sig_10", "min_p"], ascending=[False, False, True])
        )
    else:
        stability = pd.DataFrame()
    stability.to_csv(OUT_DIR / "grid_stability_by_x.csv", index=False)

    write_doc(event_defs, sample, hetero, average, spec_sum)
    if not hetero.empty:
        print(
            hetero[hetero["time_valid_prior_year"].eq(1)]
            .sort_values("p")
            [["event_def", "method_variant", "specificity", "ai_def", "coef", "se", "p", "q_bh_all", "nobs", "events"]]
            .head(20)
            .to_string(index=False),
            flush=True,
        )
    print(f"wrote {OUT_DIR}", flush=True)
    print(f"wrote {DOC_PATH}", flush=True)


if __name__ == "__main__":
    main()
