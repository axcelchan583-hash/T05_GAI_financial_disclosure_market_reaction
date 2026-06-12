#!/usr/bin/env python3
"""Attach CAC registry verification timing to GenAI disclosure events."""

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


RUN_ID = "v68_disclosure_registry_verification_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "128_v68_disclosure_registry_verification_20260612.md"

V56_EVENTS = ROOT / "results/v56_v55_expanded_llm_empirical_tables_20260612/expanded_event_samples.csv"
V56_PEER_PANEL = ROOT / "results/v56_v55_expanded_llm_empirical_tables_20260612/analysis_panel_with_returns_ai.csv.gz"
V59_FOCAL_STRICT = ROOT / "results/v59_focal_own_return_check_20260612/focal_own_return_panel_strict_next_trading_day.csv.gz"
V63_FILING_LLM = ROOT / "results/v63_filing_v3_3_summary_20260612/v62_filing_llm_merged.csv"
V67_MASTER = ROOT / "results/v67_registry_firm_product_master_20260612/registry_firm_product_master.csv"

PREFERRED_METHOD = "liu_product_tfidf_same_industry_d_top10"
MAIN_OUTCOME = "peer_car_0_p1_mm"
SAMPLE_END = pd.Timestamp("2026-06-12")
CENSOR_DAYS = 180


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, low_memory=False).fillna("")


def clean(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def code6(value: object) -> str:
    return v65.z6(clean(value))


def normal_p(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2.0))


def md_table(df: pd.DataFrame, limit: int = 40) -> str:
    if df.empty:
        return "_No rows._"
    show = df.head(limit).copy()
    lines = ["| " + " | ".join(show.columns) + " |", "|" + "|".join("---" for _ in show.columns) + "|"]
    for _, row in show.iterrows():
        lines.append("| " + " | ".join(clean(row[c]).replace("|", "\\|") for c in show.columns) + " |")
    return "\n".join(lines)


def event_text(row: pd.Series) -> str:
    cols = [
        "announcement_title",
        "matched_genai_terms",
        "evidence",
        "reason",
        "priority_evidence",
        "metadata_snippet",
    ]
    return " ".join(clean(row.get(c, "")) for c in cols)


SPLIT_RE = re.compile(r"[、,，;；/／\s]+")


def product_match_score(text: str, product: pd.Series) -> tuple[int, str, str]:
    haystack = clean(text)
    filing_no = clean(product.get("filing_no", ""))
    if filing_no and filing_no in haystack:
        return 4, "filing_no_exact", filing_no

    item_name = clean(product.get("item_name", ""))
    if item_name and item_name not in {"--", "-"} and len(item_name) >= 3 and item_name in haystack:
        return 3, "item_name_exact", item_name

    app = clean(product.get("application_product", ""))
    app = app.replace("(APP)", "").replace("(网站)", "").replace("(小程序)", "").replace("(其他)", "")
    terms = [t.strip("()（）[]【】") for t in SPLIT_RE.split(app) if len(t.strip("()（）[]【】")) >= 3]
    for term in terms:
        if term and term in haystack:
            return 2, "application_product_exact", term
    return 0, "firm_only_no_product_text_hit", ""


def verification_rank(value: str) -> int:
    return {
        "self_filing": 4,
        "app_registration": 3,
        "deep_synthesis": 2,
        "ordinary_algorithm_genai_keyword": 1,
    }.get(value, 0)


def load_events() -> pd.DataFrame:
    events = read_csv(V56_EVENTS)
    events["focal_code"] = events["focal_code"].map(code6)
    events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce")
    events["source_universe"] = "v56_expanded_disclosure_pool"

    if V63_FILING_LLM.exists():
        filing = read_csv(V63_FILING_LLM)
        filing = filing[filing["model_verdict"].eq("A")].copy()
        if not filing.empty:
            keep_cols = sorted(set(events.columns).union(filing.columns))
            for col in keep_cols:
                if col not in events.columns:
                    events[col] = ""
                if col not in filing.columns:
                    filing[col] = ""
            filing["event_id"] = filing["announcement_id"].where(filing["announcement_id"].ne(""), filing["id"])
            filing["focal_code"] = filing["focal_code"].map(code6)
            filing["sec_name"] = filing["focal_name"].where(filing["focal_name"].ne(""), filing["sec_name"])
            filing["event_date"] = pd.to_datetime(filing["event_date"], errors="coerce")
            filing["event_year"] = filing["event_date"].dt.year.astype("Int64").astype(str).replace("<NA>", "")
            filing["announcement_date"] = filing["event_date"].dt.strftime("%Y-%m-%d")
            filing["sample_name"] = "v62_filing_A_increment_all"
            filing["event_type"] = "A"
            filing["event_key"] = filing["sample_name"] + "::" + filing["event_id"].map(clean)
            filing["credible_A"] = 1
            filing["source_batch"] = "v62_filing_recall_v3_3"
            filing["source_universe"] = "v62_filing_recall_outside_v56"
            filing["primary_pom_like_category"] = "filing_recall"
            filing["evidence"] = filing["evidence"].where(filing["evidence"].ne(""), filing["cac_matched_terms"])
            events = pd.concat([events[keep_cols], filing[keep_cols]], ignore_index=True, sort=False)

    events = events[events["focal_code"].ne("") & events["event_date"].notna()].copy()
    events["event_date_str"] = events["event_date"].dt.strftime("%Y-%m-%d")
    return events


def load_registry_master() -> pd.DataFrame:
    master = read_csv(V67_MASTER)
    master["listed_code"] = master["listed_code"].map(code6)
    master["batch_public_datetime"] = pd.to_datetime(master["batch_public_datetime"], errors="coerce")
    master["batch_public_date"] = master["batch_public_datetime"].dt.strftime("%Y-%m-%d").where(
        master["batch_public_datetime"].notna(), master["batch_public_date"]
    )
    master["verification_rank"] = master["verification_type"].map(verification_rank)
    return master


def build_labels(events: pd.DataFrame, registry: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    groups = {code: group.copy() for code, group in registry.groupby("listed_code")}
    rows: list[dict[str, object]] = []
    review_rows: list[pd.DataFrame] = []
    censor_start = SAMPLE_END - pd.Timedelta(days=CENSOR_DAYS)

    for _, event in events.iterrows():
        code = event["focal_code"]
        event_dt = pd.Timestamp(event["event_date"])
        text = event_text(event)
        matches = groups.get(code, pd.DataFrame()).copy()

        base = {
            "sample_name": event["sample_name"],
            "event_type": event["event_type"],
            "event_id": clean(event["event_id"]),
            "event_key": clean(event.get("event_key", "")),
            "focal_code": code,
            "sec_name": clean(event.get("sec_name", "")),
            "event_date": event_dt.strftime("%Y-%m-%d"),
            "announcement_title": clean(event.get("announcement_title", "")),
            "out": clean(event.get("out", "")),
            "mode": clean(event.get("mode", "")),
            "layer": clean(event.get("layer", "")),
            "realized": clean(event.get("realized", "")),
            "source_universe": clean(event.get("source_universe", "")),
            "registry_firm_product_count": 0,
            "registry_products_at_event_count": 0,
            "registry_products_later_count": 0,
            "verified_at_event_date": 0,
            "verified_ex_post": 0,
            "verification_timing": "",
            "verification_type": "",
            "registry_source": "",
            "registry_status": "",
            "registry_product_id": "",
            "registry_entity_name": "",
            "registry_item_name": "",
            "registry_application_product": "",
            "registry_filing_no": "",
            "registry_batch_public_date": "",
            "registry_batch_public_date_precision": "",
            "registry_relation_to_listed": "",
            "registry_match_method": "",
            "registry_match_confidence": "",
            "product_text_match_score": 0,
            "product_text_match_basis": "",
            "product_text_match_term": "",
            "event_to_registry_days": np.nan,
            "event_after_recent_censor_start": int(event_dt > censor_start),
        }

        if matches.empty:
            base["verification_timing"] = "unmatched_ambiguous" if event_dt > censor_start else "never_verified"
            rows.append(base)
            continue

        matches["event_date"] = event_dt
        matches["public_date_valid"] = matches["batch_public_datetime"].notna()
        matches["event_to_registry_days"] = (matches["batch_public_datetime"] - event_dt).dt.days
        matches["is_at_event"] = matches["public_date_valid"] & matches["batch_public_datetime"].le(event_dt)
        matches["is_later"] = matches["public_date_valid"] & matches["batch_public_datetime"].gt(event_dt)
        scores = matches.apply(lambda r: product_match_score(text, r), axis=1)
        matches["product_text_match_score"] = [s[0] for s in scores]
        matches["product_text_match_basis"] = [s[1] for s in scores]
        matches["product_text_match_term"] = [s[2] for s in scores]
        matches["timing_rank"] = np.select([matches["is_at_event"], matches["is_later"]], [2, 1], default=0)
        matches["abs_days"] = matches["event_to_registry_days"].abs()
        matches["abs_days"] = matches["abs_days"].fillna(999999)
        matches = matches.sort_values(
            ["product_text_match_score", "timing_rank", "verification_rank", "abs_days"],
            ascending=[False, False, False, True],
        )
        best = matches.iloc[0]

        at_count = int(matches["is_at_event"].sum())
        later_count = int(matches["is_later"].sum())
        if at_count > 0:
            timing = "verified_at_event"
        elif later_count > 0:
            timing = "later_verified"
        else:
            timing = "unmatched_ambiguous"

        base.update(
            {
                "registry_firm_product_count": len(matches),
                "registry_products_at_event_count": at_count,
                "registry_products_later_count": later_count,
                "verified_at_event_date": int(at_count > 0),
                "verified_ex_post": 1,
                "verification_timing": timing,
                "verification_type": clean(best.get("verification_type", "")),
                "registry_source": clean(best.get("registry_source", "")),
                "registry_status": clean(best.get("registry_status", "")),
                "registry_product_id": clean(best.get("registry_product_id", "")),
                "registry_entity_name": clean(best.get("entity_name", "")),
                "registry_item_name": clean(best.get("item_name", "")),
                "registry_application_product": clean(best.get("application_product", "")),
                "registry_filing_no": clean(best.get("filing_no", "")),
                "registry_batch_public_date": clean(best.get("batch_public_date", "")),
                "registry_batch_public_date_precision": clean(best.get("batch_public_date_precision", "")),
                "registry_relation_to_listed": clean(best.get("relation_to_listed", "")),
                "registry_match_method": clean(best.get("match_method", "")),
                "registry_match_confidence": clean(best.get("match_confidence", "")),
                "product_text_match_score": int(best.get("product_text_match_score", 0) or 0),
                "product_text_match_basis": clean(best.get("product_text_match_basis", "")),
                "product_text_match_term": clean(best.get("product_text_match_term", "")),
                "event_to_registry_days": best.get("event_to_registry_days", np.nan),
            }
        )
        rows.append(base)

        if clean(event.get("event_type", "")) in {"A", "D-fw"} and int(best.get("product_text_match_score", 0) or 0) == 0:
            q = matches.head(8).copy()
            q = q.drop(
                columns=["event_id", "sample_name", "event_type", "focal_code", "sec_name", "event_date", "announcement_title"],
                errors="ignore",
            )
            q.insert(0, "event_id", clean(event["event_id"]))
            q.insert(1, "sample_name", clean(event["sample_name"]))
            q.insert(2, "event_type", clean(event["event_type"]))
            q.insert(3, "focal_code", code)
            q.insert(4, "sec_name", clean(event.get("sec_name", "")))
            q.insert(5, "event_date", event_dt.strftime("%Y-%m-%d"))
            q.insert(6, "announcement_title", clean(event.get("announcement_title", "")))
            review_rows.append(q)

    labels = pd.DataFrame(rows)
    labels["verification_matrix_cell"] = (
        labels["event_type"].map(clean)
        + "__"
        + labels["verification_timing"].map(clean)
        + "__"
        + labels["verification_type"].map(lambda x: clean(x) if clean(x) else "no_registry")
    )
    review = pd.concat(review_rows, ignore_index=True, sort=False) if review_rows else pd.DataFrame()
    return labels, review


def event_counts(labels: pd.DataFrame) -> pd.DataFrame:
    return (
        labels.groupby(["sample_name", "event_type", "verification_timing", "verification_type"], dropna=False)
        .agg(events=("event_id", "nunique"), firms=("focal_code", "nunique"), product_text_exact=("product_text_match_score", lambda s: int((pd.to_numeric(s, errors="coerce").fillna(0) > 0).sum())))
        .reset_index()
        .sort_values(["sample_name", "event_type", "verification_timing", "verification_type"])
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
                "events": group["event_id"].nunique(),
                "focal_firms": group["focal_code"].nunique(),
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
    key_cols = [
        "sample_name",
        "event_type",
        "event_id",
        "focal_code",
        "verification_timing",
        "verification_type",
        "verified_at_event_date",
        "verified_ex_post",
    ]
    event_labels = labels[key_cols].drop_duplicates(["sample_name", "event_id"])

    peer = pd.read_csv(
        V56_PEER_PANEL,
        dtype=str,
        low_memory=False,
        usecols=[
            "sample_name",
            "event_type",
            "event_id",
            "focal_code",
            "peer_code",
            "method_variant",
            "peer_car_0_p1_mm",
            "peer_ar0_mm",
        ],
    ).fillna("")
    peer = peer[peer["method_variant"].eq(PREFERRED_METHOD)].copy()
    peer = peer.merge(event_labels, on=["sample_name", "event_id", "focal_code", "event_type"], how="inner")
    peer_summary = summarize_values(peer, ["sample_name", "event_type", "verification_timing", "verification_type"], MAIN_OUTCOME)
    event_peer_mean = (
        peer.assign(peer_car_0_p1_mm=pd.to_numeric(peer["peer_car_0_p1_mm"], errors="coerce"))
        .groupby(["sample_name", "event_type", "event_id", "focal_code", "verification_timing", "verification_type"], as_index=False)
        .agg(event_mean_peer_car=("peer_car_0_p1_mm", "mean"), peer_obs=("peer_code", "size"))
    )
    event_weighted = summarize_values(
        event_peer_mean,
        ["sample_name", "event_type", "verification_timing", "verification_type"],
        "event_mean_peer_car",
    )
    event_weighted = event_weighted.rename(
        columns={
            "nobs": "event_weighted_nobs",
            "mean": "event_weighted_mean",
            "se": "event_weighted_se",
            "z": "event_weighted_z",
            "p": "event_weighted_p",
            "median": "event_weighted_median",
            "positive_share": "event_weighted_positive_share",
        }
    )
    peer_summary = peer_summary.merge(
        event_weighted[
            [
                "sample_name",
                "event_type",
                "verification_timing",
                "verification_type",
                "event_weighted_nobs",
                "event_weighted_mean",
                "event_weighted_se",
                "event_weighted_p",
                "event_weighted_median",
                "event_weighted_positive_share",
            ]
        ],
        on=["sample_name", "event_type", "verification_timing", "verification_type"],
        how="left",
    )

    focal = pd.read_csv(
        V59_FOCAL_STRICT,
        dtype=str,
        low_memory=False,
        usecols=["sample_name", "event_type", "event_id", "focal_code", "peer_car_0_p1_mm", "date_0"],
    ).fillna("")
    focal = focal.rename(columns={"peer_car_0_p1_mm": "focal_car_0_p1_mm"})
    focal = focal.merge(event_labels, on=["sample_name", "event_id", "focal_code", "event_type"], how="inner")
    focal_summary = summarize_values(focal, ["sample_name", "event_type", "verification_timing", "verification_type"], "focal_car_0_p1_mm")

    peer_minus = event_peer_mean.merge(
        focal[["sample_name", "event_type", "event_id", "focal_code", "focal_car_0_p1_mm"]],
        on=["sample_name", "event_type", "event_id", "focal_code"],
        how="inner",
    )
    peer_minus["focal_car_0_p1_mm"] = pd.to_numeric(peer_minus["focal_car_0_p1_mm"], errors="coerce")
    peer_minus["peer_minus_focal"] = peer_minus["event_mean_peer_car"] - peer_minus["focal_car_0_p1_mm"]
    peer_minus_summary = summarize_values(
        peer_minus,
        ["sample_name", "event_type", "verification_timing", "verification_type"],
        "peer_minus_focal",
    )
    peer_minus_summary = peer_minus_summary.rename(columns={"mean": "peer_minus_focal_mean"})
    return peer_summary, focal_summary, peer_minus_summary


def write_doc(
    labels: pd.DataFrame,
    counts: pd.DataFrame,
    peer_summary: pd.DataFrame,
    focal_summary: pd.DataFrame,
    peer_minus_summary: pd.DataFrame,
    review: pd.DataFrame,
) -> None:
    a_counts = counts[counts["sample_name"].isin(["A_all", "A_first_firm", "v62_filing_A_increment_all"])].copy()
    peer_focus = peer_summary[
        peer_summary["sample_name"].isin(["A_all", "A_first_firm", "A_Dfw_stack"])
        & peer_summary["event_type"].isin(["A", "D-fw"])
    ].copy()
    focal_focus = focal_summary[
        focal_summary["sample_name"].isin(["A_all", "A_first_firm", "A_Dfw_stack"])
        & focal_summary["event_type"].isin(["A", "D-fw"])
    ].copy()
    minus_focus = peer_minus_summary[
        peer_minus_summary["sample_name"].isin(["A_all", "A_first_firm", "A_Dfw_stack"])
        & peer_minus_summary["event_type"].isin(["A", "D-fw"])
    ].copy()

    lines = [
        "# v68 Disclosure-Registry Verification Labels",
        "",
        "## Scope",
        "",
        "- Implements the first executable join after `v67_registry_firm_product_master_20260612`.",
        "- Adds event-level `verification_timing`: `verified_at_event`, `later_verified`, `never_verified`, or `unmatched_ambiguous`.",
        "- Uses firm-level registry linkage as the first-pass administrative verification tag.",
        "- Separately flags exact product-text hits; firm-level matches without product-text hits remain in the review queue.",
        "- Applies the 180-day right-censor rule for unmatched events near the sample end.",
        "",
        "## Outputs",
        "",
        f"- `results/{RUN_ID}/event_registry_verification_labels.csv`",
        f"- `results/{RUN_ID}/event_registry_verification_counts.csv`",
        f"- `results/{RUN_ID}/peer_car_by_verification_timing.csv`",
        f"- `results/{RUN_ID}/focal_car_by_verification_timing.csv`",
        f"- `results/{RUN_ID}/peer_minus_focal_by_verification_timing.csv`",
        f"- `results/{RUN_ID}/event_registry_product_review_queue.csv`",
        "",
        "## Event Verification Counts",
        "",
        md_table(a_counts, limit=80),
        "",
        "## Peer CAR By Verification Timing",
        "",
        md_table(peer_focus, limit=80),
        "",
        "## Focal CAR By Verification Timing",
        "",
        md_table(focal_focus, limit=80),
        "",
        "## Peer Minus Focal By Verification Timing",
        "",
        md_table(minus_focus, limit=80),
        "",
        "## Review Queue",
        "",
        f"- Firm-level event-product candidate rows needing product correspondence review: {len(review)}",
        f"- A/D-fw event rows in labels: {len(labels[labels['event_type'].isin(['A', 'D-fw'])])}",
        "",
        "## Caveat",
        "",
        "This run does not claim product-level identity unless the product name, application name, or filing number appears exactly in the event text fields. The main first-pass label is firm-level administrative verification timing.",
        "",
    ]
    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    events = load_events()
    registry = load_registry_master()
    labels, review = build_labels(events, registry)
    counts = event_counts(labels)
    peer_summary, focal_summary, peer_minus_summary = build_return_summaries(labels)

    labels.to_csv(OUT_DIR / "event_registry_verification_labels.csv", index=False, encoding="utf-8-sig")
    counts.to_csv(OUT_DIR / "event_registry_verification_counts.csv", index=False, encoding="utf-8-sig")
    peer_summary.to_csv(OUT_DIR / "peer_car_by_verification_timing.csv", index=False, encoding="utf-8-sig")
    focal_summary.to_csv(OUT_DIR / "focal_car_by_verification_timing.csv", index=False, encoding="utf-8-sig")
    peer_minus_summary.to_csv(OUT_DIR / "peer_minus_focal_by_verification_timing.csv", index=False, encoding="utf-8-sig")
    review.to_csv(OUT_DIR / "event_registry_product_review_queue.csv", index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(OUT_DIR / f"{RUN_ID}.xlsx") as writer:
        labels.head(200000).to_excel(writer, sheet_name="Event_labels", index=False)
        counts.to_excel(writer, sheet_name="Counts", index=False)
        peer_summary.to_excel(writer, sheet_name="Peer_CAR", index=False)
        focal_summary.to_excel(writer, sheet_name="Focal_CAR", index=False)
        peer_minus_summary.to_excel(writer, sheet_name="Peer_minus_focal", index=False)
        review.head(200000).to_excel(writer, sheet_name="Review_queue", index=False)

    write_doc(labels, counts, peer_summary, focal_summary, peer_minus_summary, review)

    main_a = labels[(labels["sample_name"].eq("A_all")) & (labels["event_type"].eq("A"))]
    print("run_id", RUN_ID)
    print("A_all_events", main_a["event_id"].nunique())
    print(main_a.groupby("verification_timing")["event_id"].nunique().to_string())
    print("review_queue_rows", len(review))
    print("doc", DOC_PATH)


if __name__ == "__main__":
    main()
