#!/usr/bin/env python3
"""Retest T05 product-peer effects using the v36 corrected GenAI X event set."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_v23_cninfo_1055_peer_coverage_20260603 as cov  # noqa: E402
import run_v23_cninfo_1055_peer_event_study_20260603 as pe  # noqa: E402
import run_v24_cninfo_specificity_peer_grid_20260604 as v24  # noqa: E402
import run_v25_empirical_table_pack_20260604 as v25  # noqa: E402


RUN_ID = "v26_v36_x_peer_retest_20260604"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "90_v26_v36_x_peer_retest_20260604.md"

QIAN_ROOT = ROOT.parent / "T05-qian-supplier-replication-cn"
V36_DIR = QIAN_ROOT / "results" / "v36_candidate_x_supplier_replication_20260604"
V36_UNIQUE_PATH = V36_DIR / "v36_candidate_x_unique_events.csv"
V36_FIRST_PATH = V36_DIR / "v36_candidate_x_first_event_per_firm.csv"
OLD_SPEC_PATH = ROOT / "results" / "v24_cninfo_specificity_peer_grid_20260604" / "event_specificity_measures.csv"

OUTCOME = "peer_car_0_p1_mm"
PRE_CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
AI_DEFS = ["ext_any", "current_text_history"]
SPEC_DEFS = [
    ("legacy_detail_density", "legacy_detail_density_raw"),
    ("qian_recall_score", "qian_recall_score"),
]
MAIN_METHODS = [
    "ren_wang_binary_global_top10",
    "liu_product_tfidf_global_top5",
    "liu_product_tfidf_global_top10",
    "ren_wang_binary_global_top5",
]
MAIN_SAMPLES = [
    "combined_first_event_per_firm",
    "combined487_unique",
    "direct414_unique",
    "backfill73_keyword_unique",
]


def code6(value: object) -> str:
    out = cov.code6(value)
    return out or ""


def clean_id(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text


def p_from_z(z_value: float) -> float:
    return math.erfc(abs(z_value) / math.sqrt(2)) if math.isfinite(z_value) else math.nan


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


def md_table(df: pd.DataFrame, cols: list[str] | None = None, limit: int = 20) -> str:
    if df.empty:
        return "_No rows._"
    out = df.copy()
    if cols is not None:
        out = out[cols]
    out = out.head(limit).copy()
    for col in out.select_dtypes(include=[np.number]).columns:
        out[col] = out[col].map(lambda x: round(float(x), 6) if pd.notna(x) else x)
    rows = ["| " + " | ".join(out.columns) + " |", "|" + "|".join("---" for _ in out.columns) + "|"]
    for _, row in out.iterrows():
        rows.append("| " + " | ".join("" if pd.isna(row[c]) else str(row[c]) for c in out.columns) + " |")
    return "\n".join(rows)


def load_v36_samples() -> pd.DataFrame:
    unique = pd.read_csv(V36_UNIQUE_PATH, dtype=str, low_memory=False)
    first = pd.read_csv(V36_FIRST_PATH, dtype=str, low_memory=False)
    direct = unique[unique["candidate_row_type"].eq("direct_event_date_candidate")].copy()
    backfill = unique[unique["candidate_row_type"].eq("keyword_recovered_first_event_candidate")].copy()
    definitions = [
        ("direct414_unique", direct),
        ("backfill73_keyword_unique", backfill),
        ("combined487_unique", unique),
        ("combined_first_event_per_firm", first),
    ]
    frames = []
    for sample_name, df in definitions:
        sub = df.copy()
        sub["sample_name"] = sample_name
        frames.append(sub)
    events = pd.concat(frames, ignore_index=True)
    events["event_id"] = events["event_id"].map(clean_id)
    events["event_key"] = events["sample_name"] + "::" + events["event_id"]
    events["focal_code"] = events["focal_code"].map(code6)
    events["sec_name"] = events["focal_name"].fillna("")
    events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce")
    events["event_year"] = events["event_date"].dt.year
    events["announcement_date"] = events["event_date"].dt.strftime("%Y-%m-%d")
    for col in ["auto_keep_likely_qian", "candidate_tier"]:
        if col not in events.columns:
            events[col] = ""
    events = events[events["focal_code"].ne("") & events["event_date"].notna()].copy()
    return events


def link_peer_panel(events: pd.DataFrame) -> pd.DataFrame:
    panels: list[pd.DataFrame] = []
    for spec in cov.NETWORK_SPECS:
        linked = cov.link_network(events, spec)
        if not linked.empty:
            panels.append(linked)
            print(f"{spec.method}: rows={len(linked):,}, events={linked['event_key'].nunique():,}", flush=True)
        else:
            print(f"{spec.method}: no linked rows", flush=True)
    if not panels:
        raise RuntimeError("No peer links were created.")
    return pd.concat(panels, ignore_index=True)


def add_returns_and_ai(panel: pd.DataFrame) -> pd.DataFrame:
    stock = pe.load_stock_model()
    out = pe.attach_event_trading_dates(panel, stock)
    out = pe.build_return_measures(out, stock)
    out["date_0"] = pd.to_datetime(out["date_0"], errors="coerce")
    out["event_date"] = pd.to_datetime(out["event_date"], errors="coerce")
    out["event_week"] = out["date_0"].dt.strftime("%Y-%U")
    out["peer_industry_d"] = out["peer_industry_d"].fillna("UNKNOWN").astype(str)
    out["focal_industry_d"] = out["focal_industry_d"].fillna("UNKNOWN").astype(str)
    out["peer_industry_week"] = out["peer_industry_d"] + "|" + out["event_week"].fillna("")
    out["focal_industry_week"] = out["focal_industry_d"] + "|" + out["event_week"].fillna("")
    out = v24.add_prewindows(out)
    out = v24.add_ai_active(out)
    return out


def build_specificity(events: pd.DataFrame) -> pd.DataFrame:
    base_cols = [
        "event_id",
        "event_key",
        "sample_name",
        "focal_code",
        "sec_name",
        "event_date",
        "announcement_title",
        "auto_pdf_label",
        "candidate_row_type",
        "qian_recall_score",
        "llm_reason",
        "llm_evidence",
        "matched_genai_terms",
        "fulltext_matched_genai_terms",
        "query_terms",
    ]
    for col in base_cols:
        if col not in events.columns:
            events[col] = ""
    event_base = events[base_cols].drop_duplicates(["sample_name", "event_id"]).copy()
    old = pd.read_csv(OLD_SPEC_PATH, dtype=str, low_memory=False)
    old["event_id"] = old["event_id"].map(clean_id)
    old_keep = old[
        [
            "event_id",
            "legacy_detail_density_raw",
            "genai_concreteness_raw",
            "machine_component_sum",
            "machine_specificity_score_0_4",
            "auto_action_score",
        ]
    ].drop_duplicates("event_id")
    out = event_base.merge(old_keep, on="event_id", how="left")
    out["specificity_source"] = np.where(out["legacy_detail_density_raw"].notna(), "old_1055_fulltext", "v36_snippet")
    text_cols = [
        "announcement_title",
        "llm_evidence",
        "llm_reason",
        "matched_genai_terms",
        "fulltext_matched_genai_terms",
        "query_terms",
    ]
    snippet = out[text_cols].fillna("").agg(" ".join, axis=1)
    missing = out["legacy_detail_density_raw"].isna()
    if missing.any():
        fallback = snippet[missing].map(lambda text: v24.legacy_detail_density(text)["legacy_detail_density_raw"])
        out.loc[missing, "legacy_detail_density_raw"] = fallback
    out["qian_recall_score"] = pd.to_numeric(out["qian_recall_score"], errors="coerce")
    out["qian_recall_score"] = out["qian_recall_score"].fillna(out["qian_recall_score"].median())
    for col in [
        "legacy_detail_density_raw",
        "genai_concreteness_raw",
        "machine_component_sum",
        "machine_specificity_score_0_4",
        "auto_action_score",
    ]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def sample_counts(events: pd.DataFrame) -> pd.DataFrame:
    return (
        events.groupby("sample_name", as_index=False)
        .agg(events=("event_key", "nunique"), focal_firms=("focal_code", "nunique"))
        .sort_values("events", ascending=False)
    )


def run_mean_event_study(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    clean = panel[panel["complete_clean_m1_p1"].eq(1)].copy()
    group_cols = ["sample_name", "method_variant", "method", "method_top_n", "time_valid_prior_year"]
    for key, d in clean.groupby(group_cols, dropna=False):
        base = dict(zip(group_cols, key))
        for outcome, label in pe.OUTCOMES:
            rows.append({**base, "outcome": outcome, "outcome_label": label, **pe.clustered_mean(d, outcome)})
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["sample_name", "outcome", "time_valid_prior_year", "p", "method_variant"])


def run_heterogeneity(panel: pd.DataFrame, spec_events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    methods = sorted(panel.loc[panel["time_valid_prior_year"].eq(1), "method_variant"].dropna().unique())
    for sample_name in MAIN_SAMPLES:
        sample_specs = spec_events[spec_events["sample_name"].eq(sample_name)].copy()
        if sample_specs.empty:
            continue
        for spec_name, raw_col in SPEC_DEFS:
            sample_specs["spec_z"] = v25.zscore(v25.winsorize(sample_specs[raw_col]))
            z_map = sample_specs.set_index("event_key")["spec_z"].to_dict()
            for method in methods:
                d0 = panel[
                    panel["sample_name"].eq(sample_name)
                    & panel["method_variant"].eq(method)
                    & panel["complete_clean_m1_p1"].eq(1)
                ].copy()
                d0 = d0.dropna(subset=[OUTCOME, *PRE_CONTROLS, "peer_industry_week"])
                if d0.empty:
                    continue
                d0["spec_z"] = d0["event_key"].map(z_map)
                if d0["spec_z"].notna().sum() < 80 or d0["spec_z"].std(ddof=0) == 0:
                    continue
                for ai_def in AI_DEFS:
                    d = d0.copy()
                    d["ai"] = pd.to_numeric(d[ai_def], errors="coerce").fillna(0.0).astype(float)
                    d["spec_ai"] = d["spec_z"] * d["ai"]
                    res = v25.fit_absorbed_ols(
                        d,
                        OUTCOME,
                        ["ai", "spec_ai", *PRE_CONTROLS],
                        ["event_key", "peer_industry_week"],
                    )
                    if res is None or "spec_ai_coef" not in res:
                        continue
                    rows.append(
                        {
                            "sample_name": sample_name,
                            "method_variant": method,
                            "method_top_n": int(d["method_top_n"].dropna().iloc[0]),
                            "time_valid_prior_year": int(d["time_valid_prior_year"].dropna().iloc[0]),
                            "specificity": spec_name,
                            "ai_def": ai_def,
                            "coef": res["spec_ai_coef"],
                            "se": res["spec_ai_se"],
                            "z": res["spec_ai_z"],
                            "p": res["spec_ai_p"],
                            "nobs": res["nobs"],
                            "events": res["events"],
                            "focal_firms": res["focal_firms"],
                            "peer_firms": res["peer_firms"],
                            "r2": res["r2"],
                        }
                    )
    out = pd.DataFrame(rows)
    if not out.empty:
        out["q_bh_all"] = bh_qvalues(out["p"])
        out["q_bh_sample_spec_ai"] = (
            out.groupby(["sample_name", "specificity", "ai_def"], group_keys=False)["p"].apply(bh_qvalues)
        )
        out["abs_t"] = (out["coef"] / out["se"]).abs()
    return out


def write_doc(
    events: pd.DataFrame,
    coverage_summary: pd.DataFrame,
    mean_summary: pd.DataFrame,
    hetero: pd.DataFrame,
    spec_audit: pd.DataFrame,
) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    strict_car = mean_summary[
        mean_summary["time_valid_prior_year"].eq(1) & mean_summary["outcome"].eq(OUTCOME)
    ].sort_values(["sample_name", "p", "method_variant"])
    first_hetero = hetero[
        hetero["sample_name"].eq("combined_first_event_per_firm")
        & hetero["specificity"].eq("legacy_detail_density")
        & hetero["ai_def"].eq("ext_any")
    ].sort_values(["p", "method_variant"])
    key_methods = hetero[
        hetero["method_variant"].isin(MAIN_METHODS)
        & hetero["specificity"].eq("legacy_detail_density")
        & hetero["ai_def"].eq("ext_any")
    ].sort_values(["sample_name", "p", "method_variant"])
    source_counts = (
        spec_audit.groupby(["sample_name", "specificity_source"], as_index=False)
        .agg(events=("event_key", "nunique"))
        .sort_values(["sample_name", "specificity_source"])
    )
    lines = [
        "# v26 v36-X peer retest",
        "",
        "## Purpose",
        "",
        "This run replaces the old CNINFO 1055 event library with the frozen v36 corrected GenAI X event set and reruns product-peer event-study and specificity x AI-active-peer tests.",
        "",
        "## v36 Event Samples",
        "",
        md_table(sample_counts(events)),
        "",
        "## Specificity Source Audit",
        "",
        "Most v36 events reuse the old full-text specificity measures. Backfill events not present in the old 1055 library use a short v36 snippet fallback for `legacy_detail_density`; treat those fallback rows as provisional.",
        "",
        md_table(source_counts),
        "",
        "## Peer Coverage",
        "",
        md_table(
            coverage_summary[coverage_summary["time_valid_prior_year"].eq(1)].sort_values(
                ["sample_name", "event_link_rate", "peer_event_obs"], ascending=[True, False, False]
            ),
            [
                "sample_name",
                "method_variant",
                "input_events",
                "events_with_peers",
                "event_link_rate",
                "peer_event_obs",
                "unique_peer_firms",
            ],
            24,
        ),
        "",
        "## Mean Peer CAR[0,+1], Strict Prior-Year Networks",
        "",
        md_table(
            strict_car,
            ["sample_name", "method_variant", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"],
            30,
        ),
        "",
        "## Specificity x AIActivePeer: First Event Per Firm",
        "",
        md_table(
            first_hetero,
            [
                "method_variant",
                "coef",
                "se",
                "p",
                "q_bh_sample_spec_ai",
                "q_bh_all",
                "nobs",
                "events",
                "peer_firms",
                "r2",
            ],
            24,
        ),
        "",
        "## Key Method Comparison Across v36 Samples",
        "",
        md_table(
            key_methods,
            [
                "sample_name",
                "method_variant",
                "coef",
                "se",
                "p",
                "q_bh_sample_spec_ai",
                "q_bh_all",
                "nobs",
                "events",
                "peer_firms",
                "r2",
            ],
            40,
        ),
        "",
        "## Reading",
        "",
        "- Supplier links remain very sparse in v36; product peers provide much larger event-peer panels.",
        "- The first-event sample is closest to Qian/POM treatment timing, but it is also the strictest test.",
        "- Backfill rows need manual inspection because they materially affect signs in the supplier run and use snippet-based specificity fallback when not present in the old 1055 library.",
        "",
        "## Output Files",
        "",
        f"- `{OUT_DIR.relative_to(ROOT)}/v36_peer_link_panel.csv.gz`",
        f"- `{OUT_DIR.relative_to(ROOT)}/v36_peer_event_study_panel_light.csv.gz`",
        f"- `{OUT_DIR.relative_to(ROOT)}/v36_peer_coverage_summary.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/v36_peer_event_study_summary.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/v36_specificity_measures.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/v36_specificity_x_ai_peer_regressions.csv`",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    events = load_v36_samples()
    print(f"Loaded v36 events: {len(events):,} sample-event rows, {events['event_id'].nunique():,} unique event ids", flush=True)
    panel = link_peer_panel(events)
    coverage_summary = cov.summarize_panel(events, panel)
    panel = add_returns_and_ai(panel)
    spec_events = build_specificity(events)
    mean_summary = run_mean_event_study(panel)
    hetero = run_heterogeneity(panel, spec_events)

    light_cols = [
        "sample_name",
        "method_variant",
        "method",
        "method_top_n",
        "time_valid_prior_year",
        "event_id",
        "event_key",
        "focal_code",
        "sec_name",
        "event_date",
        "date_0",
        "event_week",
        "auto_pdf_label",
        "candidate_row_type",
        "peer_code",
        "peer_name",
        "peer_rank",
        "peer_similarity",
        "snapshot_report_year",
        "peer_industry_d",
        "peer_industry_week",
        "focal_industry_d",
        "focal_industry_week",
        "complete_clean_m1_p1",
        "peer_ar_m1_mm",
        "peer_ar0_mm",
        "peer_ar_p1_mm",
        OUTCOME,
        "peer_car_m1_p1_mm",
        *PRE_CONTROLS,
        *AI_DEFS,
        "ext_no_hiring",
        "ext_plus_history",
    ]
    panel.to_csv(OUT_DIR / "v36_peer_link_panel.csv.gz", index=False)
    panel[light_cols].to_csv(OUT_DIR / "v36_peer_event_study_panel_light.csv.gz", index=False)
    events.to_csv(OUT_DIR / "v36_event_samples.csv", index=False)
    coverage_summary.to_csv(OUT_DIR / "v36_peer_coverage_summary.csv", index=False)
    mean_summary.to_csv(OUT_DIR / "v36_peer_event_study_summary.csv", index=False)
    spec_events.to_csv(OUT_DIR / "v36_specificity_measures.csv", index=False)
    hetero.to_csv(OUT_DIR / "v36_specificity_x_ai_peer_regressions.csv", index=False)
    write_doc(events, coverage_summary, mean_summary, hetero, spec_events)

    print(
        hetero[
            hetero["sample_name"].eq("combined_first_event_per_firm")
            & hetero["specificity"].eq("legacy_detail_density")
            & hetero["ai_def"].eq("ext_any")
        ]
        .sort_values("p")
        [["method_variant", "coef", "se", "p", "q_bh_sample_spec_ai", "q_bh_all", "nobs", "events", "peer_firms"]]
        .head(20)
        .to_string(index=False),
        flush=True,
    )
    print(f"wrote {OUT_DIR}", flush=True)
    print(f"wrote {DOC_PATH}", flush=True)


if __name__ == "__main__":
    main()
