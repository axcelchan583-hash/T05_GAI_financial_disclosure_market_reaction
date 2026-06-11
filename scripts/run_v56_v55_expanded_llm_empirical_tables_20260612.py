#!/usr/bin/env python3
"""Run expanded empirical tables after v55 recodes old v36-missing events."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v53_v52_llm_empirical_tables_20260612 as v53  # noqa: E402


RUN_ID = "v56_v55_expanded_llm_empirical_tables_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "117_v56_v55_expanded_llm_empirical_tables_20260612.md"

V52_CODED = ROOT / "results/v53_v52_llm_empirical_tables_20260612/v52_coded_rows_enriched.csv"
V55_DIR = ROOT / "results/v55_v36_missing197_v3_3_20260612"
V55_PARSED = V55_DIR / "siliconflow_parsed_outputs.csv"
V55_MANIFEST = V55_DIR / "manifest.csv"
QIAN_ROOT = Path("/Users/mac/computerscience/23实证选题探索/T05-qian-supplier-replication-cn")
V36_FIRST = QIAN_ROOT / "results/v36_candidate_x_supplier_replication_20260604/v36_candidate_x_first_event_per_firm.csv"

PREFERRED_METHOD = v53.PREFERRED_METHOD
MAIN_OUTCOME = v53.MAIN_OUTCOME


def clean(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def ensure_cols(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for col in cols:
        if col not in df.columns:
            df[col] = ""
    return df


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, low_memory=False).fillna("")


def load_v52_rows(v36_ids: set[str]) -> pd.DataFrame:
    df = read_csv(V52_CODED)
    df["source_batch"] = "v52_pom_like_1601"
    df["announcement_id"] = df["announcement_id"].map(clean)
    df["in_old_v36_first363"] = df["announcement_id"].isin(v36_ids).astype(int)
    df["focal_code"] = df["focal_code"].map(v53.code6)
    df["event_id"] = df["announcement_id"].where(df["announcement_id"].ne(""), df["event_id"].map(clean))
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df["announcement_date"] = pd.to_datetime(df["announcement_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["event_year"] = df["event_date"].dt.year
    return df


def load_v55_rows(v36: pd.DataFrame) -> pd.DataFrame:
    parsed = read_csv(V55_PARSED)
    manifest = read_csv(V55_MANIFEST)
    parsed["id"] = parsed["id"].map(clean)
    manifest["id"] = manifest["id"].map(clean)
    df = manifest.merge(parsed, on="id", how="inner", validate="one_to_one", suffixes=("_manifest", "_model"))
    if len(df) != len(parsed):
        raise RuntimeError(f"v55 merge lost rows: parsed={len(parsed)}, merged={len(df)}")
    df = df.merge(v36.add_prefix("v36_"), left_on="announcement_id", right_on="v36_event_id", how="left")

    df["source_batch"] = "v55_old_v36_missing197"
    df["pack_row_id"] = df["id"]
    df["announcement_id"] = df["announcement_id"].map(clean)
    df["sec_code"] = df["focal_code"].map(v53.code6)
    df["focal_code"] = df["sec_code"]
    df["sec_name"] = df["focal_name"].map(clean).where(df["focal_name"].map(clean).ne(""), df["v36_focal_name"].map(clean))
    df["announcement_title"] = df["announcement_title"].map(clean).where(
        df["announcement_title"].map(clean).ne(""), df["v36_announcement_title"].map(clean)
    )
    df["announcement_date"] = df["event_date_manifest"].map(clean)
    model_date = pd.to_datetime(df["event_date_model"], errors="coerce")
    manifest_date = pd.to_datetime(df["event_date_manifest"], errors="coerce")
    df["event_date"] = model_date.where(model_date.notna(), manifest_date)
    df["event_year"] = df["event_date"].dt.year
    df["event_date_str"] = df["event_date"].dt.strftime("%Y-%m-%d")
    df["event_id"] = df["announcement_id"]
    df["primary_pom_like_category"] = (
        df["old_auto_pdf_label"].map(clean) + " / " + df["old_sample_source"].map(clean)
    ).str.strip(" /")
    df["matched_genai_terms"] = (
        df["v36_matched_genai_terms"].map(clean)
        .where(df["v36_matched_genai_terms"].map(clean).ne(""), df["v36_fulltext_matched_genai_terms"].map(clean))
        .where(lambda s: s.ne(""), df["v36_backfill_matched_keywords"].map(clean))
    )
    df["query_terms"] = df["v36_query_terms"].map(clean)
    df["priority_evidence"] = df["v36_llm_evidence"].map(clean)
    df["metadata_snippet"] = df["v36_llm_reason"].map(clean)
    df["candidate_tier"] = df["old_candidate_tier"].map(clean)
    df["v34_llm_category"] = df["v36_llm_category"].map(clean)
    df["machine_pred_verdict"] = df["v36_llm_category"].map(clean)
    df["machine_pred_reason"] = df["v36_llm_reason"].map(clean)
    df["txt_local_path"] = df["text_path"].map(clean)
    df["qian_recall_score"] = pd.to_numeric(df["v36_qian_recall_score"], errors="coerce")
    df["model_verdict"] = df["model_verdict"].map(clean)
    for col in ["out", "mode", "layer", "realized", "review_priority", "uncertainty", "evidence", "reason"]:
        df[col] = df[col].map(clean)
    df["out_num"] = pd.to_numeric(df["out"], errors="coerce")
    df["credible_A"] = df["model_verdict"].eq("A").astype(int)
    df["in_old_v36_first363"] = 1
    return df


def load_expanded_coded_rows() -> tuple[pd.DataFrame, pd.DataFrame]:
    v36 = read_csv(V36_FIRST)
    v36_ids = set(v36["event_id"].map(clean))
    v52 = load_v52_rows(v36_ids)
    v55 = load_v55_rows(v36)
    cols = sorted(set(v52.columns).union(v55.columns))
    v52 = ensure_cols(v52, cols)
    v55 = ensure_cols(v55, cols)
    coded = pd.concat([v52[cols], v55[cols]], ignore_index=True, sort=False)
    coded = coded[coded["focal_code"].map(clean).ne("") & coded["event_date"].notna()].copy()
    coded["model_verdict"] = coded["model_verdict"].map(clean)
    coded["credible_A"] = coded["model_verdict"].eq("A").astype(int)
    coded["out_num"] = pd.to_numeric(coded["out"], errors="coerce")
    coded["qian_recall_score"] = pd.to_numeric(coded["qian_recall_score"], errors="coerce")
    return coded, v36


def is_nonai_investment_placebo(df: pd.DataFrame) -> pd.Series:
    return df["source_batch"].eq("v52_pom_like_1601") & v53.is_nonai_investment_placebo(df)


def build_event_samples(coded: pd.DataFrame) -> pd.DataFrame:
    a_all = coded[coded["model_verdict"].eq("A")].copy()
    dfw = coded[coded["model_verdict"].eq("D-fw")].copy()
    a_first = a_all.sort_values(["focal_code", "event_date", "event_id"]).drop_duplicates("focal_code")
    old_a = coded[coded["in_old_v36_first363"].eq(1) & coded["model_verdict"].eq("A")].copy()
    old_a = old_a.sort_values(["focal_code", "event_date", "event_id"]).drop_duplicates("focal_code")
    stack = pd.concat([a_all, dfw], ignore_index=True)
    placebo = coded[is_nonai_investment_placebo(coded)].copy()

    definitions: list[tuple[str, pd.DataFrame]] = [
        ("A_all", a_all),
        ("A_first_firm", a_first),
        ("A_old363_reaudited_first", old_a),
        ("Dfw_all", dfw),
        ("A_Dfw_stack", stack),
        ("D_nonai_investment_placebo", placebo),
    ]

    keep_cols = [
        "event_id",
        "focal_code",
        "sec_name",
        "event_date",
        "event_year",
        "announcement_date",
        "announcement_title",
        "primary_pom_like_category",
        "matched_genai_terms",
        "query_terms",
        "model_verdict",
        "credible_A",
        "out",
        "out_num",
        "mode",
        "layer",
        "realized",
        "review_priority",
        "uncertainty",
        "evidence",
        "reason",
        "priority_evidence",
        "metadata_snippet",
        "txt_local_path",
        "qian_recall_score",
        "source_batch",
        "in_old_v36_first363",
    ]
    coded = ensure_cols(coded, keep_cols)
    frames: list[pd.DataFrame] = []
    for sample_name, sub in definitions:
        if sub.empty:
            continue
        event = ensure_cols(sub.copy(), keep_cols)[keep_cols].copy()
        event["sample_name"] = sample_name
        event["event_type"] = np.where(event["model_verdict"].eq("A"), "A", event["model_verdict"])
        event["event_key"] = sample_name + "::" + event["event_id"].astype(str)
        event["sec_name"] = event["sec_name"].fillna("")
        frames.append(event)
    events = pd.concat(frames, ignore_index=True)
    events["auto_pdf_label"] = events["event_type"]
    events["candidate_tier"] = events["model_verdict"]
    return events


def coding_distribution(coded: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    verdict = (
        coded.groupby(["source_batch", "model_verdict"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["source_batch", "model_verdict"])
    )
    old363 = (
        coded[coded["in_old_v36_first363"].eq(1)]
        .groupby("model_verdict", dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values("model_verdict")
    )
    a_fields = (
        coded[coded["model_verdict"].eq("A")]
        .groupby(["source_batch", "out", "mode", "layer", "realized"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["source_batch", "rows"], ascending=[True, False])
    )
    year = (
        coded.groupby(["event_year", "source_batch", "model_verdict"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["event_year", "source_batch", "model_verdict"])
    )
    return verdict, old363, a_fields, year


def md_table(df: pd.DataFrame, cols: list[str] | None = None, limit: int = 20) -> str:
    return v53.md_table(df, cols, limit)


def write_doc(
    verdict: pd.DataFrame,
    old363: pd.DataFrame,
    a_fields: pd.DataFrame,
    sample_counts: pd.DataFrame,
    coverage: pd.DataFrame,
    t2: pd.DataFrame,
    t3: pd.DataFrame,
    t4: pd.DataFrame,
    t5: pd.DataFrame,
    t6: pd.DataFrame,
    t7: pd.DataFrame,
    t8: pd.DataFrame,
) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    preferred_t2 = t2[
        t2["method_variant"].eq(PREFERRED_METHOD)
        & t2["sample_name"].isin(["A_all", "A_first_firm", "A_old363_reaudited_first"])
        & t2["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
    ].sort_values(["sample_name", "outcome"])
    preferred_t8 = t8[
        t8["method_variant"].eq(PREFERRED_METHOD)
        & t8["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
    ].sort_values("outcome")
    lines = [
        "# v56 expanded v55/v52 LLM empirical tables",
        "",
        "## Scope",
        "",
        "- Input coding: v52 POM-like 1,601-case v3.3 run plus v55 recoding of the 197 old-v36 first-firm events missing from v52.",
        "- `A_old363_reaudited_first` answers how many of the old 363 first-firm events survive the stricter v3.3 rules.",
        "- `A_first_firm` is the preferred expanded first-firm sample over the union of v52 and v55.",
        f"- Preferred peer method: `{PREFERRED_METHOD}`.",
        "",
        "## T1 Coding Distribution",
        "",
        md_table(verdict),
        "",
        "Old 363 reaudited distribution:",
        "",
        md_table(old363),
        "",
        "A-field distribution:",
        "",
        md_table(a_fields, limit=20),
        "",
        "Event samples:",
        "",
        md_table(sample_counts),
        "",
        "## Peer Coverage",
        "",
        md_table(
            coverage[coverage["method_variant"].eq(PREFERRED_METHOD)],
            [
                "sample_name",
                "method_variant",
                "input_events",
                "events_with_peers",
                "event_link_rate",
                "peer_event_obs",
                "unique_peer_firms",
            ],
            20,
        ),
        "",
        "## T2 A-Sample Peer Main Effect",
        "",
        md_table(
            preferred_t2,
            ["sample_name", "outcome_label", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"],
            20,
        ),
        "",
        "## T3 Layer Heterogeneity",
        "",
        md_table(
            t3[t3["outcome"].eq(MAIN_OUTCOME)].sort_values(["group_value"]),
            ["group_value", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"],
            20,
        ),
        "",
        "## T4 A vs D-fw Contrast",
        "",
        md_table(t4, limit=30),
        "",
        "## T5 Specificity x AIActive",
        "",
        md_table(t5.sort_values(["sample_name", "p"]), limit=30),
        "",
        "## T6 OUT/M/R/Layer x AIActive Cuts",
        "",
        md_table(t6.sort_values("p"), limit=30),
        "",
        "## T7 Ex-Post Validation Readout",
        "",
        md_table(t7),
        "",
        "## T8 Non-GenAI Investment Placebo",
        "",
        md_table(
            preferred_t8,
            ["sample_name", "outcome_label", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"],
            10,
        ),
        "",
        "## Output Files",
        "",
        f"- `{OUT_DIR.relative_to(ROOT)}/expanded_coded_rows_enriched.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/expanded_event_samples.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/peer_link_panel.csv.gz`",
        f"- `{OUT_DIR.relative_to(ROOT)}/analysis_panel_with_returns_ai.csv.gz`",
        f"- `{OUT_DIR.relative_to(ROOT)}/t2_peer_main_effect.csv`",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    v53.OUT_DIR = OUT_DIR
    coded, _ = load_expanded_coded_rows()
    verdict, old363, a_fields, year = coding_distribution(coded)
    events = build_event_samples(coded)
    events, spec_measures = v53.add_specificity(events)
    counts = v53.sample_summary(events)

    coded.to_csv(OUT_DIR / "expanded_coded_rows_enriched.csv", index=False)
    events.to_csv(OUT_DIR / "expanded_event_samples.csv", index=False)
    spec_measures.to_csv(OUT_DIR / "expanded_specificity_measures.csv", index=False)
    verdict.to_csv(OUT_DIR / "t1_source_verdict_distribution.csv", index=False)
    old363.to_csv(OUT_DIR / "t1_old363_reaudited_verdict_distribution.csv", index=False)
    a_fields.to_csv(OUT_DIR / "t1_A_field_distribution.csv", index=False)
    year.to_csv(OUT_DIR / "t1_year_source_verdict_distribution.csv", index=False)
    counts.to_csv(OUT_DIR / "sample_construction_summary.csv", index=False)

    peer_panel, coverage = v53.link_peer_panel(events)
    peer_panel.to_csv(OUT_DIR / "peer_link_panel.csv.gz", index=False)
    coverage.to_csv(OUT_DIR / "peer_coverage_summary.csv", index=False)

    panel = v53.add_returns_ai(peer_panel)
    panel.to_csv(OUT_DIR / "analysis_panel_with_returns_ai.csv.gz", index=False)

    t2 = v53.mean_event_study(panel, ["A_all", "A_first_firm", "A_old363_reaudited_first"])
    t3 = v53.grouped_mean(panel, "A_all", "layer")
    t4_means = v53.grouped_mean(panel, "A_Dfw_stack", "event_type")
    t4_reg, t5, t6 = v53.regression_rows(panel, events)
    t4 = pd.concat(
        [
            t4_means[t4_means["outcome"].eq(MAIN_OUTCOME)].assign(model="mean_by_event_type"),
            t4_reg.assign(sample_name="A_Dfw_stack", method_variant=PREFERRED_METHOD),
        ],
        ignore_index=True,
        sort=False,
    )
    t7 = v53.validation_table(events)
    t8 = v53.mean_event_study(panel, ["D_nonai_investment_placebo"])

    t2.to_csv(OUT_DIR / "t2_peer_main_effect.csv", index=False)
    t3.to_csv(OUT_DIR / "t3_layer_heterogeneity.csv", index=False)
    t4.to_csv(OUT_DIR / "t4_a_vs_dfw_contrast.csv", index=False)
    t5.to_csv(OUT_DIR / "t5_specificity_x_ai.csv", index=False)
    t6.to_csv(OUT_DIR / "t6_out_m_r_layer_cuts.csv", index=False)
    t7.to_csv(OUT_DIR / "t7_validation_summary.csv", index=False)
    t8.to_csv(OUT_DIR / "t8_nonai_investment_placebo.csv", index=False)

    xlsx = OUT_DIR / f"{RUN_ID}.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        for sheet, df in [
            ("T1_source_verdict", verdict),
            ("T1_old363", old363),
            ("T1_A_fields", a_fields),
            ("Samples", counts),
            ("Coverage", coverage),
            ("T2_main", t2),
            ("T3_layer", t3),
            ("T4_A_Dfw", t4),
            ("T5_spec_ai", t5),
            ("T6_cuts", t6),
            ("T7_validation", t7),
            ("T8_placebo", t8),
        ]:
            df.to_excel(writer, sheet_name=sheet[:31], index=False)

    write_doc(verdict, old363, a_fields, counts, coverage, t2, t3, t4, t5, t6, t7, t8)

    print(f"wrote {OUT_DIR}", flush=True)
    print(f"wrote {DOC_PATH}", flush=True)
    print("\nOld 363 reaudited verdict:")
    print(old363.to_string(index=False), flush=True)
    print("\nSample counts:")
    print(counts.to_string(index=False), flush=True)
    print("\nPreferred T2:")
    pref = t2[
        t2["method_variant"].eq(PREFERRED_METHOD)
        & t2["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
    ]
    print(pref[["sample_name", "outcome_label", "estimate", "se", "p", "nobs", "events", "peer_firms"]].to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
