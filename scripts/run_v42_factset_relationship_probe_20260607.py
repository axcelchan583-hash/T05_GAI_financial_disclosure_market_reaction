#!/usr/bin/env python3
"""FactSet Revere relationship probe for v36 GenAI events.

This run maps A-share firms to FactSet Revere company IDs, extracts pre-event
relationship rows involving v36 focal firms, maps related entities back to
A-share codes, and runs event-study summaries by relationship type.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_v38_wide_collaborator_competitor_probe_20260607 as v38  # noqa: E402


RUN_ID = "v42_factset_relationship_probe_20260607"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "106_v42_factset_relationship_probe_20260607.md"

FACTSET_ROOT = Path(
    "/Users/mac/computerscience/第三方资料/01_数据资源/FactSet/"
    "20250108_FactSet_Revere_SupplyChain_Relationships_dta"
)
FACTSET_COMPANY_ZIP = FACTSET_ROOT / "FactSet_Revere_Company_Basics_20250108_dta.zip"
FACTSET_REL_ZIP = FACTSET_ROOT / "FactSet_Revere_SupplyChain_Relationships_20250108_dta.zip"

REL_WINDOW_YEARS = 5
COMPANY_CHUNK = 300_000
REL_CHUNK = 300_000
OPEN_END_DATE = pd.Timestamp("2262-04-11")

PARTNER_HIGH_CONF_TYPES = {
    "PARTNER-RESCOLB",
    "PARTNER-JVENTUR",
    "PARTNER-TECHNGY",
    "PARTNER-INTPROD",
    "PARTNER-DISTRIB",
    "PARTNER-LICENIN",
    "PARTNER-LICENOT",
    "PARTNER-MANUFAC",
    "PARTNER-MARKTNG",
}

OUTCOMES = v38.OUTCOMES


def code6(value: object) -> str:
    return v38.code6(value)


def clean_id(value: object) -> str:
    return v38.clean_id(value)


def norm_factset_id(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text


def is_a_share_ticker(value: object) -> bool:
    if pd.isna(value):
        return False
    text = str(value).strip()
    return bool(re.fullmatch(r"\d{6}", text))


def p_from_z(z_value: float) -> float:
    return math.erfc(abs(z_value) / math.sqrt(2)) if math.isfinite(z_value) else math.nan


def fmt_coef(value: float, p_value: float) -> str:
    if pd.isna(value):
        return ""
    stars = "***" if p_value < 0.01 else "**" if p_value < 0.05 else "*" if p_value < 0.10 else ""
    return f"{value:.4f}{stars}"


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    return v38.md_table(df, max_rows=max_rows)


def load_events() -> pd.DataFrame:
    events = v38.load_v36_first_events()
    events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce")
    events = events[events["event_date"].notna() & events["focal_code"].ne("")].copy()
    return events.reset_index(drop=True)


def build_factset_a_share_history() -> pd.DataFrame:
    cols = ["start_", "end_", "id", "name", "active", "covered", "ticker", "isin", "country", "province_name", "city"]
    rows = []
    reader = pd.read_stata(
        FACTSET_COMPANY_ZIP,
        columns=cols,
        chunksize=COMPANY_CHUNK,
        convert_categoricals=False,
    )
    total = 0
    for chunk in reader:
        total += len(chunk)
        chunk = chunk[chunk["country"].fillna("").astype(str).str.upper().eq("CN")].copy()
        if chunk.empty:
            continue
        chunk["ticker"] = chunk["ticker"].fillna("").astype(str).str.strip()
        chunk = chunk[chunk["ticker"].map(is_a_share_ticker)].copy()
        if chunk.empty:
            continue
        chunk["a_share_code"] = chunk["ticker"].map(code6)
        chunk["factset_company_id"] = chunk["id"].map(norm_factset_id)
        chunk["fs_start"] = pd.to_datetime(chunk["start_"], errors="coerce")
        chunk["fs_end"] = pd.to_datetime(chunk["end_"], errors="coerce")
        chunk["fs_end"] = chunk["fs_end"].fillna(OPEN_END_DATE)
        keep = [
            "factset_company_id",
            "a_share_code",
            "name",
            "active",
            "covered",
            "ticker",
            "isin",
            "country",
            "province_name",
            "city",
            "fs_start",
            "fs_end",
        ]
        rows.append(chunk[keep])
        if total % 1_200_000 == 0:
            print(f"  company rows scanned={total:,}; mapped rows={sum(len(r) for r in rows):,}", flush=True)
    if not rows:
        return pd.DataFrame()
    hist = pd.concat(rows, ignore_index=True)
    hist = hist[hist["factset_company_id"].ne("") & hist["a_share_code"].ne("")].copy()
    hist = hist.sort_values(["a_share_code", "factset_company_id", "fs_start", "fs_end"])
    hist = hist.drop_duplicates(["factset_company_id", "a_share_code", "fs_start", "fs_end"], keep="last")
    return hist.reset_index(drop=True)


def map_events_to_factset(events: pd.DataFrame, company_hist: pd.DataFrame) -> pd.DataFrame:
    if company_hist.empty:
        return pd.DataFrame()
    merged = events.merge(company_hist, left_on="focal_code", right_on="a_share_code", how="left")
    merged = merged[
        merged["factset_company_id"].notna()
        & (merged["fs_start"] <= merged["event_date"])
        & (merged["event_date"] < merged["fs_end"])
    ].copy()
    if merged.empty:
        return merged
    merged["covered_score"] = merged["covered"].fillna("").eq("Y").astype(int)
    merged["active_score"] = merged["active"].fillna("").eq("Y").astype(int)
    merged = merged.sort_values(
        ["event_key", "covered_score", "active_score", "fs_start"],
        ascending=[True, False, False, False],
    )
    mapped = merged.drop_duplicates(["event_key"], keep="first").copy()
    mapped = mapped.rename(columns={"name": "factset_focal_name", "isin": "factset_focal_isin"})
    return mapped.reset_index(drop=True)


def map_related_to_a_share(candidates: pd.DataFrame, company_hist: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty or company_hist.empty:
        return pd.DataFrame()
    hist = company_hist.rename(
        columns={
            "factset_company_id": "related_factset_id",
            "a_share_code": "related_code",
            "name": "related_factset_name",
            "ticker": "related_ticker",
            "isin": "related_isin",
            "fs_start": "related_fs_start",
            "fs_end": "related_fs_end",
        }
    )
    merged = candidates.merge(hist, on="related_factset_id", how="left")
    merged = merged[
        merged["related_code"].notna()
        & (merged["related_fs_start"] <= merged["event_date"])
        & (merged["event_date"] < merged["related_fs_end"])
    ].copy()
    if merged.empty:
        return merged
    merged = merged[merged["related_code"].map(code6).ne(merged["focal_code"].map(code6))].copy()
    merged["related_code"] = merged["related_code"].map(code6)
    merged["related_valid_score"] = merged["related_fs_start"].notna().astype(int)
    merged = merged.sort_values(
        ["event_key", "related_code", "relation_group", "relation_start", "relation_end", "related_valid_score"],
        ascending=[True, True, True, False, False, False],
    )
    return merged.drop_duplicates(["event_key", "related_code", "relation_type"], keep="first").reset_index(drop=True)


def classify_relation(row: pd.Series, focal_side: str) -> tuple[str, str, str]:
    rel_type = str(row.get("rel_type") or "")
    if rel_type == "COMPETITOR":
        return "factset_competitor", "competitor", "competitor"
    if rel_type == "CUSTOMER":
        if focal_side == "source":
            return "factset_downstream_customer", "customer", "customer"
        return "factset_upstream_supplier", "supplier", "supplier"
    if rel_type == "SUPPLIER":
        if focal_side == "source":
            return "factset_upstream_supplier", "supplier", "supplier"
        return "factset_downstream_customer", "customer", "customer"
    if rel_type.startswith("PARTNER-"):
        subtype = rel_type.replace("PARTNER-", "").lower()
        if rel_type in PARTNER_HIGH_CONF_TYPES:
            return f"factset_partner_{subtype}", "partner_high_confidence", "partner"
        return f"factset_partner_{subtype}", "partner_other", "partner"
    return f"factset_{rel_type.lower()}", "other", "other"


def attach_focal_events(rel: pd.DataFrame, event_map: pd.DataFrame, focal_side: str) -> pd.DataFrame:
    key = "source_company_id" if focal_side == "source" else "target_company_id"
    related_key = "target_company_id" if focal_side == "source" else "source_company_id"
    merged = rel.merge(
        event_map[
            [
                "event_key",
                "sample_name",
                "event_id",
                "focal_code",
                "focal_name",
                "event_date",
                "event_year",
                "announcement_title",
                "auto_pdf_label",
                "candidate_row_type",
                "factset_company_id",
            ]
        ],
        left_on=key,
        right_on="factset_company_id",
        how="inner",
    )
    if merged.empty:
        return merged
    merged["relation_start"] = pd.to_datetime(merged["start_"], errors="coerce")
    merged["relation_end"] = pd.to_datetime(merged["end_"], errors="coerce").fillna(OPEN_END_DATE)
    window_start = merged["event_date"] - pd.DateOffset(years=REL_WINDOW_YEARS)
    merged = merged[
        (merged["relation_start"] < merged["event_date"])
        & (merged["relation_end"] >= window_start)
    ].copy()
    if merged.empty:
        return merged
    cls = merged.apply(lambda r: classify_relation(r, focal_side), axis=1)
    merged["relation_type"] = [x[0] for x in cls]
    merged["relation_group"] = [x[1] for x in cls]
    merged["relation_family"] = [x[2] for x in cls]
    merged["focal_side"] = focal_side
    merged["related_factset_id"] = merged[related_key].map(norm_factset_id)
    if focal_side == "source":
        merged["related_factset_reported_name"] = merged["TARGET_name"]
        merged["related_factset_reported_ticker"] = merged["TARGET_ticker"]
        merged["related_factset_reported_isin"] = merged["TARGET_isin"]
    else:
        merged["related_factset_reported_name"] = merged["SOURCE_name"]
        merged["related_factset_reported_ticker"] = merged["SOURCE_ticker"]
        merged["related_factset_reported_isin"] = merged["SOURCE_isin"]
    return merged


def extract_factset_event_relations(event_map: pd.DataFrame, company_hist: pd.DataFrame) -> pd.DataFrame:
    if event_map.empty:
        return pd.DataFrame()
    focal_ids = set(event_map["factset_company_id"].map(norm_factset_id))
    cols = [
        "start_",
        "end_",
        "id",
        "rel_type",
        "source_company_id",
        "target_company_id",
        "revenue_percent",
        "percent_estimated",
        "SOURCE_name",
        "SOURCE_ticker",
        "SOURCE_isin",
        "TARGET_name",
        "TARGET_ticker",
        "TARGET_isin",
        "keyword1",
        "keyword2",
        "keyword3",
        "keyword4",
        "keyword5",
    ]
    relation_parts = []
    total = 0
    kept_raw = 0
    reader = pd.read_stata(
        FACTSET_REL_ZIP,
        columns=cols,
        chunksize=REL_CHUNK,
        convert_categoricals=False,
    )
    for chunk in reader:
        total += len(chunk)
        chunk["source_company_id"] = chunk["source_company_id"].map(norm_factset_id)
        chunk["target_company_id"] = chunk["target_company_id"].map(norm_factset_id)
        source_hit = chunk["source_company_id"].isin(focal_ids)
        target_hit = chunk["target_company_id"].isin(focal_ids)
        if not source_hit.any() and not target_hit.any():
            continue
        source_rel = attach_focal_events(chunk[source_hit].copy(), event_map, "source") if source_hit.any() else pd.DataFrame()
        target_rel = attach_focal_events(chunk[target_hit].copy(), event_map, "target") if target_hit.any() else pd.DataFrame()
        rel = pd.concat([source_rel, target_rel], ignore_index=True)
        if rel.empty:
            continue
        kept_raw += len(rel)
        relation_parts.append(rel)
        if total % 1_500_000 == 0:
            print(f"  relationship rows scanned={total:,}; event-window rows={kept_raw:,}", flush=True)
    if not relation_parts:
        return pd.DataFrame()
    candidates = pd.concat(relation_parts, ignore_index=True)
    mapped = map_related_to_a_share(candidates, company_hist)
    if mapped.empty:
        return mapped
    mapped["source_doc_id"] = mapped["id"]
    mapped["source_doc_title"] = mapped["rel_type"]
    mapped["match_evidence"] = mapped[[c for c in ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"] if c in mapped.columns]].fillna("").agg("; ".join, axis=1)
    mapped["relation_year"] = mapped["relation_start"].dt.year
    mapped["relation_age_days"] = (mapped["event_date"] - mapped["relation_start"]).dt.days
    keep = [
        "sample_name",
        "event_id",
        "event_key",
        "focal_code",
        "focal_name",
        "event_date",
        "event_year",
        "announcement_title",
        "auto_pdf_label",
        "candidate_row_type",
        "factset_company_id",
        "related_factset_id",
        "related_code",
        "related_factset_name",
        "related_factset_reported_name",
        "related_ticker",
        "related_isin",
        "rel_type",
        "relation_type",
        "relation_group",
        "relation_family",
        "focal_side",
        "relation_start",
        "relation_end",
        "relation_year",
        "relation_age_days",
        "revenue_percent",
        "percent_estimated",
        "source_doc_id",
        "source_doc_title",
        "match_evidence",
    ]
    for col in keep:
        if col not in mapped.columns:
            mapped[col] = np.nan
    return mapped[keep].reset_index(drop=True)


def collapse_union(links: pd.DataFrame) -> pd.DataFrame:
    if links.empty:
        return links.copy()
    priority = {
        "partner_high_confidence": 5,
        "supplier": 4,
        "customer": 3,
        "competitor": 2,
        "partner_other": 1,
        "other": 0,
    }
    out = links.copy()
    out["relation_priority"] = out["relation_group"].map(priority).fillna(0)
    out = out.sort_values(
        ["event_key", "related_code", "relation_priority", "relation_start", "relation_end"],
        ascending=[True, True, False, False, False],
    )
    collapsed = out.drop_duplicates(["event_key", "related_code"], keep="first").copy()
    collapsed["relation_type"] = "factset_relationship_union"
    collapsed["relation_group"] = "factset_union"
    return collapsed.reset_index(drop=True)


def standardize_plus(df: pd.DataFrame, relation_group: str) -> pd.DataFrame:
    out = v38.standardize_relation_panel(df, relation_group)
    extra_cols = [
        "related_factset_id",
        "related_factset_name",
        "related_factset_reported_name",
        "rel_type",
        "relation_family",
        "focal_side",
        "relation_start",
        "relation_end",
        "relation_year",
        "relation_age_days",
        "revenue_percent",
        "percent_estimated",
        "match_evidence",
    ]
    for col in extra_cols:
        if col in df.columns and len(df) == len(out):
            out[col] = df[col].values
        elif col not in out.columns:
            out[col] = np.nan
    return out


def source_summary(events: pd.DataFrame, event_map: pd.DataFrame, links: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "layer": "v36_first_events",
            "rows": len(events),
            "events": events["event_key"].nunique(),
            "focal_firms": events["focal_code"].nunique(),
            "related_firms": np.nan,
            "clean_car0p1_rows": np.nan,
            "clean_car0p1_events": np.nan,
        },
        {
            "layer": "factset_mapped_focal_events",
            "rows": len(event_map),
            "events": event_map["event_key"].nunique() if not event_map.empty else 0,
            "focal_firms": event_map["focal_code"].nunique() if not event_map.empty else 0,
            "related_firms": np.nan,
            "clean_car0p1_rows": np.nan,
            "clean_car0p1_events": np.nan,
        },
        {
            "layer": "factset_a_share_relationship_links",
            "rows": len(links),
            "events": links["event_key"].nunique() if not links.empty else 0,
            "focal_firms": links["focal_code"].nunique() if not links.empty else 0,
            "related_firms": links["related_code"].nunique() if not links.empty else 0,
            "clean_car0p1_rows": np.nan,
            "clean_car0p1_events": np.nan,
        },
    ]
    if not returns.empty:
        for relation_type, df in returns.groupby("relation_type", dropna=False):
            clean = df[df["complete_clean_m1_p1"].eq(1) & df["peer_car_0_p1_mm"].notna()]
            rows.append(
                {
                    "layer": f"{relation_type}_returns",
                    "rows": len(df),
                    "events": df["event_key"].nunique(),
                    "focal_firms": df["focal_code"].nunique(),
                    "related_firms": df["related_code"].nunique(),
                    "clean_car0p1_rows": len(clean),
                    "clean_car0p1_events": clean["event_key"].nunique(),
                }
            )
    return pd.DataFrame(rows)


def group_summary(links: pd.DataFrame) -> pd.DataFrame:
    if links.empty:
        return pd.DataFrame()
    return (
        links.groupby(["relation_group", "relation_type"], as_index=False)
        .agg(
            rows=("related_code", "size"),
            events=("event_key", "nunique"),
            focal_firms=("focal_code", "nunique"),
            related_firms=("related_code", "nunique"),
            rel_types=("rel_type", lambda s: ";".join(sorted(set(s.astype(str))))),
        )
        .sort_values(["relation_group", "rows"], ascending=[True, False])
        .reset_index(drop=True)
    )


def prepare_stacked(product_competitor: pd.DataFrame, factset_returns: pd.DataFrame, relation_types: list[str]) -> pd.DataFrame:
    comp = standardize_plus(product_competitor, "product_competitor")
    comp["factset_group"] = "product_competitor"
    comp["factset_relation"] = "product_competitor"
    parts = [comp]
    for relation_type in relation_types:
        d = factset_returns[factset_returns["relation_type"].eq(relation_type)].copy()
        if d.empty:
            continue
        s = standardize_plus(d, "factset")
        s["factset_group"] = relation_type
        s["factset_relation"] = relation_type
        parts.append(s)
    stack = pd.concat(parts, ignore_index=True)
    for relation_type in relation_types:
        stack[f"is_{relation_type}"] = stack["factset_relation"].eq(relation_type).astype(int)
    factset_keys = set(zip(stack.loc[stack["factset_relation"].ne("product_competitor"), "event_key"], stack.loc[stack["factset_relation"].ne("product_competitor"), "related_code"]))
    is_overlap = pd.Series(list(zip(stack["event_key"], stack["related_code"])), index=stack.index).isin(factset_keys)
    stack = stack[~(stack["factset_relation"].eq("product_competitor") & is_overlap)].copy()
    return stack.reset_index(drop=True)


def fit_stack_models(stack: pd.DataFrame, regressors: list[str]) -> pd.DataFrame:
    rows = []
    for outcome, _ in OUTCOMES:
        rows.append(v38.fit_event_fe(stack, outcome, regressors, "factset_relation_vs_product_competitor"))
    return pd.concat([r for r in rows if not r.empty], ignore_index=True) if rows else pd.DataFrame()


def write_report(
    company_hist: pd.DataFrame,
    event_map: pd.DataFrame,
    summary: pd.DataFrame,
    group: pd.DataFrame,
    event_study: pd.DataFrame,
    regressions: pd.DataFrame,
    examples: pd.DataFrame,
) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    car = event_study[event_study["window"].eq("CAR[0,+1]")].copy()
    report = f"""# v42 FactSet Relationship Probe

Date: 2026-06-07

## Scope

This run connects the v36 first GenAI events to FactSet Revere Supply Chain Relationships. The conservative mapping keeps FactSet companies whose `country=CN` and primary `ticker` is a six-digit A-share code. Relationships are kept when they involve a mapped focal firm and overlap the five-year window before the GenAI event date. Related firms are then mapped back to A-share codes before calculating AR/CAR.

## Mapping Summary

- FactSet A-share history rows: `{len(company_hist):,}`
- Unique mapped A-share codes: `{company_hist['a_share_code'].nunique() if not company_hist.empty else 0:,}`
- v36 events mapped to FactSet IDs: `{len(event_map):,}` / 363

This is a conservative first pass. It may miss firms whose FactSet primary ticker is an H-share or overseas listing.

## Sample Flow

{md_table(summary, max_rows=120)}

## FactSet Relation Coverage

{md_table(group, max_rows=120)}

## CAR[0,+1] by Relation Type

{md_table(
        car[
            [
                "relation_type",
                "mean",
                "se",
                "p",
                "nobs",
                "events",
                "related_firms",
                "positive_share",
                "event_weighted_mean",
                "event_weighted_p",
                "event_weighted_events",
            ]
        ]
        if not car.empty
        else car,
        max_rows=120,
    )}

## Stacked Event-FE Regressions

Baseline group is the existing product-market competitor panel. Product-competitor rows overlapping with FactSet relation rows are removed.

{md_table(
        regressions[
            [
                "sample",
                "outcome",
                "regressor",
                "coef_event_fmt",
                "p_event_cluster",
                "coef_two_way_fmt",
                "p_two_way",
                "nobs",
                "events",
                "related_firms",
                "r2",
            ]
        ]
        if not regressions.empty
        else regressions,
        max_rows=120,
    )}

## Examples

{md_table(
        examples[
            [
                "event_date",
                "focal_code",
                "focal_name",
                "related_code",
                "related_factset_name",
                "relation_type",
                "rel_type",
                "focal_side",
                "relation_start",
                "relation_end",
                "match_evidence",
            ]
        ]
        if not examples.empty
        else examples,
        max_rows=40,
    )}

## Reading

- This is a data-availability probe, not a final table.
- `CUSTOMER` and `SUPPLIER` are converted relative to the focal firm, so the output labels `factset_upstream_supplier` and `factset_downstream_customer` are focal-relative.
- Partner rows are split into granular `factset_partner_*` types and can be collapsed later into a high-confidence collaborator group.
- The next improvement is to add an H-share/name-based crosswalk for dual-listed firms whose FactSet primary ticker is not the A-share code.

## Output Files

- `results/{RUN_ID}/factset_a_share_company_history.csv`
- `results/{RUN_ID}/factset_event_focal_map.csv`
- `results/{RUN_ID}/factset_event_relationship_links.csv`
- `results/{RUN_ID}/factset_relation_event_study.csv`
- `results/{RUN_ID}/factset_stacked_regressions.csv`
- `results/{RUN_ID}/factset_relation_panel.csv.gz`
"""
    DOC_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    events = load_events()
    print(f"events={len(events):,}", flush=True)

    company_hist = build_factset_a_share_history()
    print(
        f"factset A-share map rows={len(company_hist):,}, codes={company_hist['a_share_code'].nunique() if not company_hist.empty else 0:,}",
        flush=True,
    )
    event_map = map_events_to_factset(events, company_hist)
    print(f"mapped focal events={len(event_map):,}/{len(events):,}", flush=True)

    links = extract_factset_event_relations(event_map, company_hist)
    union = collapse_union(links)
    links_all = pd.concat([links, union], ignore_index=True) if not union.empty else links.copy()
    print(
        f"factset A-share relation links={len(links):,}, events={links['event_key'].nunique() if not links.empty else 0:,}",
        flush=True,
    )

    stock_model = v38.pe.load_stock_model()
    returns = v38.attach_returns(links_all, stock_model) if not links_all.empty else links_all.copy()
    product_competitor, _ = v38.load_competitor_panel()

    summary = source_summary(events, event_map, links, returns)
    group = group_summary(links)
    relation_panel = pd.concat(
        [
            standardize_plus(returns, "factset_relation"),
        ],
        ignore_index=True,
    )
    event_study = v38.relation_event_study(relation_panel)

    main_relation_types = [
        "factset_competitor",
        "factset_upstream_supplier",
        "factset_downstream_customer",
        "factset_relationship_union",
    ]
    partner_types = sorted([t for t in links["relation_type"].unique() if str(t).startswith("factset_partner_")]) if not links.empty else []
    stack_relation_types = main_relation_types + partner_types[:8]
    stack = prepare_stacked(product_competitor, returns, stack_relation_types)
    regressors = [f"is_{t}" for t in stack_relation_types if f"is_{t}" in stack.columns]
    regressions = fit_stack_models(stack, regressors) if regressors else pd.DataFrame()

    examples = links.sort_values(["relation_group", "event_date", "relation_start"], ascending=[True, True, False]).head(200).copy() if not links.empty else pd.DataFrame()

    company_hist.to_csv(OUT_DIR / "factset_a_share_company_history.csv", index=False, encoding="utf-8-sig")
    event_map.to_csv(OUT_DIR / "factset_event_focal_map.csv", index=False, encoding="utf-8-sig")
    links.to_csv(OUT_DIR / "factset_event_relationship_links.csv", index=False, encoding="utf-8-sig")
    links_all.to_csv(OUT_DIR / "factset_event_relationship_links_with_union.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT_DIR / "sample_flow.csv", index=False, encoding="utf-8-sig")
    group.to_csv(OUT_DIR / "factset_relation_coverage.csv", index=False, encoding="utf-8-sig")
    event_study.to_csv(OUT_DIR / "factset_relation_event_study.csv", index=False, encoding="utf-8-sig")
    regressions.to_csv(OUT_DIR / "factset_stacked_regressions.csv", index=False, encoding="utf-8-sig")
    relation_panel.to_csv(OUT_DIR / "factset_relation_panel.csv.gz", index=False)
    stack.to_csv(OUT_DIR / "factset_stack_panel.csv.gz", index=False)

    write_report(company_hist, event_map, summary, group, event_study, regressions, examples)
    car = event_study[event_study["window"].eq("CAR[0,+1]")]
    print(car[["relation_type", "mean", "p", "nobs", "events", "related_firms", "event_weighted_mean", "event_weighted_p"]].to_string(index=False))
    if not regressions.empty:
        print(regressions[["outcome", "regressor", "coef", "p_event_cluster", "p_two_way", "nobs", "events"]].to_string(index=False))
    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
