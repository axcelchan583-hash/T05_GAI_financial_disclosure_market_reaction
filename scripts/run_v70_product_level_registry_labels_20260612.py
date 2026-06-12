#!/usr/bin/env python3
"""Build product-level registry verification labels for disclosure events.

v68 attached registry timing at the firm level. v69 traced registry products
back to local disclosure corpora. This run applies the v69 product search terms
to each disclosure event's full text and separates three layers:

1. firm-level administrative verification from v68;
2. product-level text match to a registry product in the event itself;
3. strict event-ready product D1 dates from v69.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v68_disclosure_registry_verification_20260612 as v68  # noqa: E402
import run_v69_registry_product_traceback_20260612 as v69  # noqa: E402


RUN_ID = "v70_product_level_registry_labels_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "130_v70_product_level_registry_labels_20260612.md"

V68_LABELS = ROOT / "results/v68_disclosure_registry_verification_20260612/event_registry_verification_labels.csv"
V69_BEST = ROOT / "results/v69_registry_product_traceback_20260612/registry_product_traceback_best.csv"
V69_TERMS = ROOT / "results/v69_registry_product_traceback_20260612/registry_product_search_terms.csv"

SAMPLE_END = pd.Timestamp("2026-06-12")
CENSOR_DAYS = 180


def clean(value: object) -> str:
    return v69.clean(value)


def code6(value: object) -> str:
    return v69.code6(value)


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, low_memory=False).fillna("")


def normal_p(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2.0))


def read_text(path_text: object) -> str:
    text = clean(path_text)
    if not text:
        return ""
    path = Path(text)
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def event_blob(row: pd.Series) -> str:
    text_path_body = read_text(row.get("txt_local_path", ""))
    parts = [
        clean(row.get("announcement_title", "")),
        text_path_body,
        clean(row.get("matched_genai_terms", "")),
        clean(row.get("query_terms", "")),
        clean(row.get("evidence", "")),
        clean(row.get("reason", "")),
        clean(row.get("priority_evidence", "")),
        clean(row.get("metadata_snippet", "")),
        clean(row.get("cac_matched_terms", "")),
    ]
    return "\n".join(part for part in parts if part)


def verification_rank(value: str) -> int:
    return {
        "self_filing": 4,
        "app_registration": 3,
        "deep_synthesis": 2,
        "ordinary_algorithm_genai_keyword": 1,
    }.get(clean(value), 0)


def match_term_in_event(term: dict[str, object], event: pd.Series, text_norm: str, title_norm: str) -> dict[str, object] | None:
    term_norm = clean(term.get("term_norm", ""))
    if not term_norm or term_norm not in text_norm:
        return None
    pos = text_norm.find(term_norm)
    window = text_norm[max(0, pos - 60) : min(len(text_norm), pos + len(term_norm) + 60)]
    title_hit = int(term_norm in title_norm)
    context_hit = int(any(v69.normalize_for_match(k) in window for k in v69.CONTEXT_KEYWORDS))
    basis = clean(term.get("basis", ""))
    term_len = int(float(clean(term.get("term_len", "0")) or 0))
    base = int(float(clean(term.get("base_score", "0")) or 0))
    score = min(base + 8 * title_hit + 6 * context_hit, 130)

    accepted = score >= v69.ACCEPT_MIN
    if basis == "product_core_exact" and term_len <= 2 and not title_hit:
        accepted = False
    if basis == "product_core_exact" and term_len <= 2 and score < 74:
        accepted = False
    if basis == "product_core_exact" and term_len >= 3 and score < 66:
        accepted = False
    if basis == "application_product_exact" and term_len <= 2 and not title_hit:
        accepted = False

    return {
        "event_product_match_score": score,
        "event_product_match_basis": basis,
        "event_product_matched_term": clean(term.get("term", "")),
        "event_product_matched_term_len": term_len,
        "event_product_title_hit": title_hit,
        "event_product_context_hit": context_hit,
        "event_product_match_accepted": int(accepted),
    }


def timing_for_event(product: pd.Series, event_dt: pd.Timestamp) -> tuple[str, float]:
    public_dt = pd.to_datetime(product.get("batch_public_datetime", ""), errors="coerce")
    if pd.isna(public_dt):
        public_dt = pd.to_datetime(product.get("batch_public_date", ""), errors="coerce")
    if pd.isna(public_dt):
        return "product_verified_unknown_public_date", np.nan
    days = float((public_dt.normalize() - event_dt.normalize()).days)
    if days <= 0:
        return "product_verified_at_event", days
    return "product_later_verified", days


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    events = v68.load_events()
    events["focal_code"] = events["focal_code"].map(code6)
    events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce")
    events = events[events["focal_code"].ne("") & events["event_date"].notna()].copy()

    firm_labels = read_csv(V68_LABELS)
    firm_labels["focal_code"] = firm_labels["focal_code"].map(code6)

    products = read_csv(V69_BEST)
    products["listed_code"] = products["listed_code"].map(code6)
    products["batch_public_dt"] = pd.to_datetime(products["batch_public_datetime"], errors="coerce")
    products["batch_public_dt"] = products["batch_public_dt"].where(
        products["batch_public_dt"].notna(), pd.to_datetime(products["batch_public_date"], errors="coerce")
    )

    terms = read_csv(V69_TERMS)
    terms["listed_code"] = terms["listed_code"].map(code6)
    terms = terms[terms["term_norm"].ne("")].copy()
    terms = terms.merge(
        products[
            [
                "registry_product_id",
                "registry_source",
                "registry_status",
                "verification_type",
                "entity_name",
                "item_name",
                "application_product",
                "filing_no",
                "batch_public_date",
                "batch_public_datetime",
                "batch_public_date_precision",
                "relation_to_listed",
                "match_confidence",
                "has_formal_traceback_d1",
                "has_formal_any_traceback",
                "has_interactive_traceback_d1_prime",
                "formal_first_date",
                "formal_first_title",
                "formal_first_match_basis",
                "formal_first_matched_term",
                "formal_first_announcement_id",
                "formal_any_first_date",
                "formal_any_first_title",
            ]
        ],
        on="registry_product_id",
        how="left",
        suffixes=("", "_product"),
    )
    return events, firm_labels, products, terms


def build_event_product_matches(events: pd.DataFrame, terms: pd.DataFrame) -> pd.DataFrame:
    term_groups = {code: group.copy() for code, group in terms.groupby("listed_code")}
    rows: list[dict[str, object]] = []
    for _, event in events.iterrows():
        code = clean(event["focal_code"])
        group = term_groups.get(code, pd.DataFrame())
        if group.empty:
            continue
        blob = event_blob(event)
        text_norm = v69.normalize_for_match(blob)
        title_norm = v69.normalize_for_match(event.get("announcement_title", ""))
        if not text_norm:
            continue
        for term in group.to_dict("records"):
            match = match_term_in_event(term, event, text_norm, title_norm)
            if not match or not match["event_product_match_accepted"]:
                continue
            event_dt = pd.Timestamp(event["event_date"])
            timing, days = timing_for_event(pd.Series(term), event_dt)
            strict_same_day = int(
                clean(term.get("has_formal_traceback_d1", "")) in {"1", "1.0", "True", "true"}
                and clean(term.get("formal_first_date", "")) == event_dt.strftime("%Y-%m-%d")
            )
            rows.append(
                {
                    "sample_name": clean(event.get("sample_name", "")),
                    "event_type": clean(event.get("event_type", "")),
                    "event_id": clean(event.get("event_id", "")),
                    "event_key": clean(event.get("event_key", "")),
                    "focal_code": code,
                    "sec_name": clean(event.get("sec_name", "")),
                    "event_date": event_dt.strftime("%Y-%m-%d"),
                    "announcement_title": clean(event.get("announcement_title", "")),
                    "registry_product_id": clean(term.get("registry_product_id", "")),
                    "product_verification_type": clean(term.get("verification_type", "")),
                    "registry_source": clean(term.get("registry_source", "")),
                    "registry_status": clean(term.get("registry_status", "")),
                    "registry_entity_name": clean(term.get("entity_name", "")),
                    "registry_item_name": clean(term.get("item_name", "")),
                    "registry_application_product": clean(term.get("application_product", "")),
                    "registry_filing_no": clean(term.get("filing_no", "")),
                    "registry_batch_public_date": clean(term.get("batch_public_date", "")),
                    "registry_batch_public_date_precision": clean(term.get("batch_public_date_precision", "")),
                    "product_public_days_after_event": days,
                    "product_verification_timing_raw": timing,
                    "strict_product_d1_same_day": strict_same_day,
                    "formal_first_date": clean(term.get("formal_first_date", "")),
                    "formal_first_title": clean(term.get("formal_first_title", "")),
                    "formal_first_match_basis": clean(term.get("formal_first_match_basis", "")),
                    "formal_first_matched_term": clean(term.get("formal_first_matched_term", "")),
                    "formal_first_announcement_id": clean(term.get("formal_first_announcement_id", "")),
                    "formal_any_first_date": clean(term.get("formal_any_first_date", "")),
                    "formal_any_first_title": clean(term.get("formal_any_first_title", "")),
                    **match,
                }
            )
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows)
    out["verification_rank"] = out["product_verification_type"].map(verification_rank)
    out["timing_rank"] = out["product_verification_timing_raw"].map(
        {"product_verified_at_event": 3, "product_later_verified": 2, "product_verified_unknown_public_date": 1}
    ).fillna(0)
    out["strict_rank"] = pd.to_numeric(out["strict_product_d1_same_day"], errors="coerce").fillna(0)
    out = out.sort_values(
        [
            "sample_name",
            "event_id",
            "strict_rank",
            "event_product_match_score",
            "timing_rank",
            "verification_rank",
            "event_product_matched_term_len",
        ],
        ascending=[True, True, False, False, False, False, False],
    ).reset_index(drop=True)
    return out


def collapse_event_labels(events: pd.DataFrame, firm_labels: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    key_cols = ["sample_name", "event_type", "event_id", "event_key", "focal_code", "sec_name", "event_date", "announcement_title"]
    base_cols = key_cols + ["out", "mode", "layer", "realized", "source_universe", "txt_local_path"]
    base = events.copy()
    for col in base_cols:
        if col not in base.columns:
            base[col] = ""
    base = base[base_cols].drop_duplicates(["sample_name", "event_id", "event_key"]).copy()
    base["event_date"] = pd.to_datetime(base["event_date"], errors="coerce").dt.strftime("%Y-%m-%d")

    firm_keep = [
        "sample_name",
        "event_type",
        "event_id",
        "focal_code",
        "verification_timing",
        "verification_type",
        "registry_firm_product_count",
        "registry_products_at_event_count",
        "registry_products_later_count",
        "product_text_match_score",
        "product_text_match_basis",
        "product_text_match_term",
    ]
    firm = firm_labels[[c for c in firm_keep if c in firm_labels.columns]].drop_duplicates(
        ["sample_name", "event_type", "event_id", "focal_code"]
    )
    firm = firm.rename(
        columns={
            "verification_timing": "firm_level_verification_timing_v68",
            "verification_type": "firm_level_verification_type_v68",
            "product_text_match_score": "v68_metadata_product_text_match_score",
            "product_text_match_basis": "v68_metadata_product_text_match_basis",
            "product_text_match_term": "v68_metadata_product_text_match_term",
        }
    )
    labels = base.merge(firm, on=["sample_name", "event_type", "event_id", "focal_code"], how="left")

    if matches.empty:
        labels["product_level_match"] = 0
        labels["product_level_verification_timing"] = "no_product_text_match"
        return labels

    best = matches.groupby(["sample_name", "event_type", "event_id", "focal_code"], as_index=False).head(1).copy()
    best = best.rename(
        columns={
            "product_verification_timing_raw": "product_level_verification_timing",
            "product_verification_type": "product_level_verification_type",
        }
    )
    attach_cols = [
        "sample_name",
        "event_type",
        "event_id",
        "focal_code",
        "registry_product_id",
        "product_level_verification_type",
        "product_level_verification_timing",
        "product_public_days_after_event",
        "strict_product_d1_same_day",
        "registry_item_name",
        "registry_application_product",
        "registry_filing_no",
        "registry_batch_public_date",
        "registry_batch_public_date_precision",
        "event_product_match_score",
        "event_product_match_basis",
        "event_product_matched_term",
        "event_product_title_hit",
        "event_product_context_hit",
        "formal_first_date",
        "formal_first_title",
        "formal_first_match_basis",
        "formal_first_matched_term",
        "formal_any_first_date",
        "formal_any_first_title",
    ]
    labels = labels.merge(best[attach_cols], on=["sample_name", "event_type", "event_id", "focal_code"], how="left")
    labels["product_level_match"] = labels["registry_product_id"].map(clean).ne("").astype(int)
    censor_start = SAMPLE_END - pd.Timedelta(days=CENSOR_DAYS)
    labels["event_after_recent_censor_start"] = (
        pd.to_datetime(labels["event_date"], errors="coerce").gt(censor_start)
    ).astype(int)
    labels["product_level_verification_timing"] = labels["product_level_verification_timing"].where(
        labels["product_level_match"].eq(1),
        np.where(labels["event_after_recent_censor_start"].eq(1), "no_product_match_recent_censored", "no_product_text_match"),
    )
    labels["product_level_verification_type"] = labels["product_level_verification_type"].where(
        labels["product_level_match"].eq(1), "no_product_match"
    )
    labels["strict_product_d1_same_day"] = pd.to_numeric(labels["strict_product_d1_same_day"], errors="coerce").fillna(0).astype(int)
    labels["product_registry_matrix_cell"] = (
        labels["event_type"].map(clean)
        + "__"
        + labels["product_level_verification_timing"].map(clean)
        + "__"
        + labels["product_level_verification_type"].map(clean)
    )
    return labels


def strict_d1_firm_dates(products: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    strict = products[products["has_formal_traceback_d1"].astype(str).eq("1")].copy()
    if strict.empty:
        return pd.DataFrame()
    grouped = (
        strict.groupby(["formal_first_date", "listed_code", "listed_name"], dropna=False)
        .agg(
            products=("registry_product_id", "nunique"),
            verification_types=("verification_type", lambda s: ";".join(sorted(set(clean(x) for x in s if clean(x))))),
            matched_terms=("formal_first_matched_term", lambda s: ";".join(sorted(set(clean(x) for x in s if clean(x))))),
            item_names=("item_name", lambda s: ";".join(sorted(set(clean(x) for x in s if clean(x)))[:10])),
            title=("formal_first_title", "first"),
            announcement_id=("formal_first_announcement_id", "first"),
        )
        .reset_index()
    )
    old = labels[labels["sample_name"].eq("A_all") & labels["event_type"].eq("A")][
        ["focal_code", "event_date", "event_id", "announcement_title", "product_level_verification_timing"]
    ].drop_duplicates()
    grouped = grouped.merge(
        old,
        left_on=["listed_code", "formal_first_date"],
        right_on=["focal_code", "event_date"],
        how="left",
        indicator=True,
    )
    grouped["in_old_A_all_same_firm_date"] = grouped["_merge"].eq("both").astype(int)
    grouped = grouped.drop(columns=["_merge", "focal_code", "event_date"], errors="ignore")
    return grouped.sort_values(["formal_first_date", "listed_code"])


def count_events(labels: pd.DataFrame) -> pd.DataFrame:
    return (
        labels.groupby(
            [
                "sample_name",
                "event_type",
                "firm_level_verification_timing_v68",
                "product_level_verification_timing",
                "product_level_verification_type",
            ],
            dropna=False,
        )
        .agg(
            events=("event_id", "nunique"),
            firms=("focal_code", "nunique"),
            strict_product_d1_events=("strict_product_d1_same_day", "sum"),
        )
        .reset_index()
        .sort_values(["sample_name", "event_type", "product_level_verification_timing", "product_level_verification_type"])
    )


def firm_vs_product_counts(labels: pd.DataFrame) -> pd.DataFrame:
    focus = labels[labels["sample_name"].isin(["A_all", "A_first_firm", "A_Dfw_stack"])].copy()
    return (
        focus.groupby(["sample_name", "event_type", "firm_level_verification_timing_v68", "product_level_match"], dropna=False)
        .agg(events=("event_id", "nunique"), firms=("focal_code", "nunique"))
        .reset_index()
        .sort_values(["sample_name", "event_type", "firm_level_verification_timing_v68", "product_level_match"])
    )


def summarize_values(df: pd.DataFrame, group_cols: list[str], value_col: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for keys, group in df.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        vals = pd.to_numeric(group[value_col], errors="coerce").dropna()
        n = len(vals)
        mean = float(vals.mean()) if n else np.nan
        se = float(vals.std(ddof=1) / math.sqrt(n)) if n > 1 else np.nan
        z = mean / se if se and not pd.isna(se) and se != 0 else np.nan
        row = {col: key for col, key in zip(group_cols, keys)}
        row.update(
            {
                "nobs": n,
                "events": group["event_id"].nunique() if "event_id" in group.columns else n,
                "focal_firms": group["focal_code"].nunique() if "focal_code" in group.columns else np.nan,
                "mean": mean,
                "se": se,
                "z": z,
                "p": normal_p(z) if not pd.isna(z) else np.nan,
                "median": float(vals.median()) if n else np.nan,
                "positive_share": float((vals > 0).mean()) if n else np.nan,
            }
        )
        rows.append(row)
    return pd.DataFrame(rows).sort_values(group_cols)


def build_return_summaries(labels: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ret_labels = labels.copy()
    ret_labels["verification_timing"] = ret_labels["product_level_verification_timing"]
    ret_labels["verification_type"] = ret_labels["product_level_verification_type"]
    ret_labels["verified_at_event_date"] = ret_labels["product_level_verification_timing"].eq("product_verified_at_event").astype(int)
    ret_labels["verified_ex_post"] = ret_labels["product_level_match"].astype(int)
    return v68.build_return_summaries(ret_labels)


def md_table(df: pd.DataFrame, limit: int = 60) -> str:
    if df.empty:
        return "_No rows._"
    show = df.head(limit).copy()
    for col in show.columns:
        if pd.api.types.is_numeric_dtype(show[col]):
            show[col] = show[col].map(lambda x: "" if pd.isna(x) else (f"{float(x):.4f}" if isinstance(x, float) else str(x)))
        else:
            show[col] = show[col].map(lambda x: clean(x)[:220])
    lines = ["| " + " | ".join(show.columns) + " |", "|" + "|".join("---" for _ in show.columns) + "|"]
    for _, row in show.iterrows():
        lines.append("| " + " | ".join(clean(row[c]).replace("|", "\\|") for c in show.columns) + " |")
    return "\n".join(lines)


def write_doc(
    event_counts: pd.DataFrame,
    firm_product_counts: pd.DataFrame,
    strict_dates: pd.DataFrame,
    peer_summary: pd.DataFrame,
    focal_summary: pd.DataFrame,
) -> None:
    focus_counts = event_counts[event_counts["sample_name"].isin(["A_all", "A_first_firm", "A_Dfw_stack"])].copy()
    peer_focus = peer_summary[
        peer_summary["sample_name"].isin(["A_all", "A_first_firm", "A_Dfw_stack"])
        & peer_summary["event_type"].isin(["A", "D-fw"])
    ].copy()
    focal_focus = focal_summary[
        focal_summary["sample_name"].isin(["A_all", "A_first_firm", "A_Dfw_stack"])
        & focal_summary["event_type"].isin(["A", "D-fw"])
    ].copy()
    lines = [
        "# v70 Product-Level Registry Labels",
        "",
        "## Purpose",
        "",
        "- Re-labels disclosure events using product-level registry text matches, not only firm-level registry existence.",
        "- Preserves v68 firm-level timing for comparison.",
        "- Separates strict event-ready product D1 dates from routine formal-file mentions.",
        "",
        "## Outputs",
        "",
        f"- `results/{RUN_ID}/event_product_level_registry_labels.csv`",
        f"- `results/{RUN_ID}/event_product_match_rows.csv`",
        f"- `results/{RUN_ID}/strict_product_d1_firm_dates.csv`",
        f"- `results/{RUN_ID}/product_level_event_counts.csv`",
        f"- `results/{RUN_ID}/firm_vs_product_level_counts.csv`",
        f"- `results/{RUN_ID}/peer_car_by_product_level_timing.csv`",
        f"- `results/{RUN_ID}/focal_car_by_product_level_timing.csv`",
        f"- `results/{RUN_ID}/{RUN_ID}.xlsx`",
        "",
        "## Product-Level Event Counts",
        "",
        md_table(focus_counts, limit=120),
        "",
        "## Firm-Level v68 vs Product-Level Match",
        "",
        md_table(firm_product_counts, limit=120),
        "",
        "## Strict Product D1 Firm-Dates",
        "",
        md_table(strict_dates, limit=40),
        "",
        "## Peer CAR Diagnostic",
        "",
        md_table(peer_focus, limit=80),
        "",
        "## Focal CAR Diagnostic",
        "",
        md_table(focal_focus, limit=80),
        "",
        "## Interpretation",
        "",
        "Product-level verification is much stricter than v68's firm-level administrative tag. The strict D1 dates are suitable as validation or supplementary event evidence, not as the main sample unless additional targeted CNINFO retrieval raises the cell size materially.",
        "",
    ]
    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    events, firm_labels, products, terms = load_inputs()
    matches = build_event_product_matches(events, terms)
    labels = collapse_event_labels(events, firm_labels, matches)
    event_counts = count_events(labels)
    fp_counts = firm_vs_product_counts(labels)
    strict_dates = strict_d1_firm_dates(products, labels)
    peer_summary, focal_summary, peer_minus_summary = build_return_summaries(labels)

    labels.to_csv(OUT_DIR / "event_product_level_registry_labels.csv", index=False, encoding="utf-8-sig")
    matches.to_csv(OUT_DIR / "event_product_match_rows.csv", index=False, encoding="utf-8-sig")
    strict_dates.to_csv(OUT_DIR / "strict_product_d1_firm_dates.csv", index=False, encoding="utf-8-sig")
    event_counts.to_csv(OUT_DIR / "product_level_event_counts.csv", index=False, encoding="utf-8-sig")
    fp_counts.to_csv(OUT_DIR / "firm_vs_product_level_counts.csv", index=False, encoding="utf-8-sig")
    peer_summary.to_csv(OUT_DIR / "peer_car_by_product_level_timing.csv", index=False, encoding="utf-8-sig")
    focal_summary.to_csv(OUT_DIR / "focal_car_by_product_level_timing.csv", index=False, encoding="utf-8-sig")
    peer_minus_summary.to_csv(OUT_DIR / "peer_minus_focal_by_product_level_timing.csv", index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(OUT_DIR / f"{RUN_ID}.xlsx") as writer:
        labels.head(200000).to_excel(writer, sheet_name="Event_labels", index=False)
        matches.head(200000).to_excel(writer, sheet_name="Match_rows", index=False)
        strict_dates.to_excel(writer, sheet_name="Strict_D1_dates", index=False)
        event_counts.to_excel(writer, sheet_name="Counts", index=False)
        fp_counts.to_excel(writer, sheet_name="Firm_vs_product", index=False)
        peer_summary.to_excel(writer, sheet_name="Peer_CAR", index=False)
        focal_summary.to_excel(writer, sheet_name="Focal_CAR", index=False)
        peer_minus_summary.to_excel(writer, sheet_name="Peer_minus_focal", index=False)

    write_doc(event_counts, fp_counts, strict_dates, peer_summary, focal_summary)

    focus = labels[labels["sample_name"].eq("A_all") & labels["event_type"].eq("A")]
    print("run_id", RUN_ID)
    print("A_all_events", focus["event_id"].nunique())
    print(focus.groupby("product_level_verification_timing")["event_id"].nunique().to_string())
    print("strict_d1_firm_dates", len(strict_dates))
    print("doc", DOC_PATH)


if __name__ == "__main__":
    main()
