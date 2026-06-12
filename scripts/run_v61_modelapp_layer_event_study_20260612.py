#!/usr/bin/env python3
"""Run model/app-layer GenAI event-study checks from the v56 A sample."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import run_v60_core_clean_launch_event_study_20260612 as base


ROOT = base.ROOT
RUN_ID = "v61_modelapp_layer_event_study_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "121_v61_modelapp_layer_event_study_20260612.md"

PREFERRED_METHOD = base.PREFERRED_METHOD
MAIN_OUTCOME = base.MAIN_OUTCOME
SAMPLE_ORDER = [
    "ModelApp_own_out_all",
    "ModelApp_own_out_first_firm",
    "ModelApp_clean_title_all",
    "ModelApp_clean_title_first_firm",
    "ModelApp_realized_plus_all",
    "ModelApp_realized_plus_first_firm",
    "Model_only_own_out_all",
    "App_only_own_out_all",
]


def build_modelapp_samples(a: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    modelapp = a[
        a["model_verdict"].eq("A")
        & a["out"].eq("1")
        & a["mode"].eq("own")
        & a["layer"].isin(["model", "app"])
    ].copy()
    modelapp_first = modelapp.sort_values(["focal_code", "event_date", "event_id"]).drop_duplicates("focal_code")
    clean_title = modelapp[~modelapp["core_excluded_title_form"]].copy()
    clean_title_first = clean_title.sort_values(["focal_code", "event_date", "event_id"]).drop_duplicates("focal_code")
    realized = modelapp[modelapp["realized"].eq("+")].copy()
    realized_first = realized.sort_values(["focal_code", "event_date", "event_id"]).drop_duplicates("focal_code")
    model_only = modelapp[modelapp["layer"].eq("model")].copy()
    app_only = modelapp[modelapp["layer"].eq("app")].copy()

    sample_defs = [
        ("ModelApp_own_out_all", modelapp),
        ("ModelApp_own_out_first_firm", modelapp_first),
        ("ModelApp_clean_title_all", clean_title),
        ("ModelApp_clean_title_first_firm", clean_title_first),
        ("ModelApp_realized_plus_all", realized),
        ("ModelApp_realized_plus_first_firm", realized_first),
        ("Model_only_own_out_all", model_only),
        ("App_only_own_out_all", app_only),
    ]
    frames: list[pd.DataFrame] = []
    for sample_name, sub in sample_defs:
        if sub.empty:
            continue
        event = sub.copy()
        event["sample_name"] = sample_name
        event["event_key"] = sample_name + "::" + event["event_id"].astype(str)
        frames.append(event)
    samples = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return samples, modelapp


def ordered(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "sample_name" not in df.columns:
        return df
    out = df.copy()
    out["_sample_order"] = pd.Categorical(out["sample_name"], SAMPLE_ORDER, ordered=True)
    sort_cols = ["_sample_order"]
    if "outcome" in out.columns:
        sort_cols.append("outcome")
    return out.sort_values(sort_cols).drop(columns="_sample_order").reset_index(drop=True)


def category_summary(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame()
    return (
        events.groupby(["layer", "primary_pom_like_category"], dropna=False, as_index=False)
        .agg(events=("event_id", "nunique"), firms=("focal_code", "nunique"))
        .sort_values(["layer", "events"], ascending=[True, False])
    )


def write_doc(
    modelapp_events: pd.DataFrame,
    sample_counts: pd.DataFrame,
    category_counts: pd.DataFrame,
    focal_next: pd.DataFrame,
    focal_inclusive: pd.DataFrame,
    peer_summary: pd.DataFrame,
    csmar_summary: pd.DataFrame,
    factset_summary: pd.DataFrame,
    rel_summary: pd.DataFrame,
) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    focal_next_main = ordered(
        focal_next[
            focal_next["sample_name"].isin(SAMPLE_ORDER)
            & focal_next["outcome"].isin(["peer_ar0_mm", "peer_ar_p1_mm", "peer_car_0_p1_mm", "peer_car_m1_p1_mm"])
        ]
    )
    focal_inclusive_main = ordered(
        focal_inclusive[
            focal_inclusive["sample_name"].isin(SAMPLE_ORDER)
            & focal_inclusive["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
        ]
    )
    peer_main = ordered(
        peer_summary[
            peer_summary["method_variant"].eq(PREFERRED_METHOD)
            & peer_summary["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
        ]
    )
    csmar_main = ordered(
        csmar_summary[
            csmar_summary.get("edge_family", pd.Series(dtype=str)).eq("union")
            & csmar_summary["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
        ]
    ) if not csmar_summary.empty else csmar_summary
    factset_main = ordered(
        factset_summary[
            factset_summary["relation_type"].isin(["factset_upstream_supplier", "factset_downstream_customer"])
            & factset_summary["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
        ]
    ) if not factset_summary.empty else factset_summary

    event_cols = [
        "event_date",
        "focal_code",
        "sec_name",
        "announcement_title",
        "primary_pom_like_category",
        "layer",
        "realized",
        "core_launch_text_hit",
        "core_excluded_title_form",
    ]
    lines = [
        "# v61 Model/App-Layer GenAI Event Study",
        "",
        "## Scope",
        "",
        "- Input: v56 expanded A sample.",
        "- Main sample `ModelApp_own_out`: external-facing (`out=1`) own GenAI model/app-layer event, without requiring strict launch/release/filing wording.",
        "- This is wider than v60 strict core launch and keeps indirect but own model/app actions such as investment, project construction, contracts, subsidiary setup, and investor-record disclosures if the LLM coded them as credible A events.",
        "- Intermediate sample `ModelApp_clean_title`: the same model/app layer but excludes noisy title forms such as board resolutions, issuance plans, feasibility reports, investor records, contracts, M&A, cooperation agreements, and project construction.",
        "- Focal firm main timing uses strict next trading day because CNINFO disclosures are often released after market close. Peer and relation panels reuse v56/v57/v58 return panels, so they use the existing event-date-to-next-available-trading-day convention.",
        "",
        "## Sample Counts",
        "",
        base.md_table(ordered(sample_counts), limit=20),
        "",
        "## Layer and Category Composition",
        "",
        base.md_table(category_counts, limit=30),
        "",
        "## Model/App Events",
        "",
        base.md_table(modelapp_events[event_cols], limit=80),
        "",
        "## Focal Firm Returns, Strict Next Trading Day",
        "",
        base.md_table(
            focal_next_main,
            ["sample_name", "outcome_label", "estimate", "se", "p", "nobs", "events", "focal_firms", "median", "positive_share"],
            40,
        ),
        "",
        "## Focal Firm Returns, Existing Event Clock",
        "",
        base.md_table(
            focal_inclusive_main,
            ["sample_name", "outcome_label", "estimate", "se", "p", "nobs", "events", "focal_firms", "median", "positive_share"],
            30,
        ),
        "",
        "## Product-Market Peer Returns",
        "",
        base.md_table(
            peer_main,
            ["sample_name", "outcome_label", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"],
            30,
        ),
        "",
        "## Peer Minus Focal, Same Existing Event Clock",
        "",
        base.md_table(ordered(rel_summary), limit=20),
        "",
        "## CSMAR Listed Supplier Benchmark",
        "",
        base.md_table(
            csmar_main,
            ["sample_name", "edge_family", "outcome_label", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"],
            30,
        ),
        "",
        "## FactSet Supplier/Customer Benchmark",
        "",
        base.md_table(
            factset_main,
            [
                "sample_name",
                "relation_type",
                "outcome_label",
                "mean",
                "se",
                "p",
                "nobs",
                "events",
                "related_firms",
                "median",
                "positive_share",
                "event_weighted_mean",
                "event_weighted_p",
            ],
            40,
        ),
        "",
        "## Output Files",
        "",
        f"- `results/{RUN_ID}/modelapp_event_samples.csv`",
        f"- `results/{RUN_ID}/modelapp_classification_all_A.csv`",
        f"- `results/{RUN_ID}/modelapp_sample_counts.csv`",
        f"- `results/{RUN_ID}/modelapp_category_counts.csv`",
        f"- `results/{RUN_ID}/focal_returns_strict_next_day_summary.csv`",
        f"- `results/{RUN_ID}/peer_returns_summary.csv`",
        f"- `results/{RUN_ID}/csmar_supplier_summary.csv`",
        f"- `results/{RUN_ID}/factset_relation_summary.csv`",
        f"- `results/{RUN_ID}/peer_minus_focal_summary.csv`",
        f"- `results/{RUN_ID}/{RUN_ID}.xlsx`",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    a = base.load_a_events()
    samples, modelapp_events = build_modelapp_samples(a)
    if samples.empty:
        raise RuntimeError("No model/app samples were created.")

    counts = base.sample_summary(samples)
    counts = ordered(counts)
    category_counts = category_summary(modelapp_events)

    focal_next_panel = base.focal_panel(samples, use_strict_next_day=True)
    focal_inclusive_panel = base.focal_panel(samples, use_strict_next_day=False)
    focal_next_summary = base.summarize_pe_style(focal_next_panel, ["sample_name"])
    focal_inclusive_summary = base.summarize_pe_style(focal_inclusive_panel, ["sample_name"])

    peer_panel = base.build_peer_panel(samples)
    peer_summary = base.summarize_pe_style(peer_panel, ["sample_name", "method_variant", "method", "method_top_n", "time_valid_prior_year"])

    csmar_panel = base.build_csmar_supplier_panel(samples)
    csmar_summary = base.summarize_pe_style(csmar_panel, ["sample_name", "event_type", "edge_family"])

    factset_panel = base.build_factset_panel(samples)
    factset_summary = base.summarize_factset(factset_panel)

    rel_summary = base.peer_minus_focal(peer_panel, focal_inclusive_panel)

    a.to_csv(OUT_DIR / "modelapp_classification_all_A.csv", index=False, encoding="utf-8-sig")
    samples.to_csv(OUT_DIR / "modelapp_event_samples.csv", index=False, encoding="utf-8-sig")
    counts.to_csv(OUT_DIR / "modelapp_sample_counts.csv", index=False, encoding="utf-8-sig")
    category_counts.to_csv(OUT_DIR / "modelapp_category_counts.csv", index=False, encoding="utf-8-sig")
    focal_next_panel.to_csv(OUT_DIR / "focal_returns_strict_next_day_panel.csv.gz", index=False)
    focal_next_summary.to_csv(OUT_DIR / "focal_returns_strict_next_day_summary.csv", index=False, encoding="utf-8-sig")
    focal_inclusive_summary.to_csv(OUT_DIR / "focal_returns_existing_event_clock_summary.csv", index=False, encoding="utf-8-sig")
    peer_summary.to_csv(OUT_DIR / "peer_returns_summary.csv", index=False, encoding="utf-8-sig")
    csmar_summary.to_csv(OUT_DIR / "csmar_supplier_summary.csv", index=False, encoding="utf-8-sig")
    factset_summary.to_csv(OUT_DIR / "factset_relation_summary.csv", index=False, encoding="utf-8-sig")
    rel_summary.to_csv(OUT_DIR / "peer_minus_focal_summary.csv", index=False, encoding="utf-8-sig")

    xlsx = OUT_DIR / f"{RUN_ID}.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        counts.to_excel(writer, sheet_name="Sample_counts", index=False)
        category_counts.to_excel(writer, sheet_name="Category_counts", index=False)
        modelapp_events.to_excel(writer, sheet_name="ModelApp_events", index=False)
        focal_next_summary.to_excel(writer, sheet_name="Focal_next", index=False)
        focal_inclusive_summary.to_excel(writer, sheet_name="Focal_existing_clock", index=False)
        peer_summary.to_excel(writer, sheet_name="Peer", index=False)
        csmar_summary.to_excel(writer, sheet_name="CSMAR_supplier", index=False)
        factset_summary.to_excel(writer, sheet_name="FactSet", index=False)
        rel_summary.to_excel(writer, sheet_name="Peer_minus_focal", index=False)

    write_doc(
        modelapp_events,
        counts,
        category_counts,
        focal_next_summary,
        focal_inclusive_summary,
        peer_summary,
        csmar_summary,
        factset_summary,
        rel_summary,
    )

    print(f"wrote {OUT_DIR}", flush=True)
    print(f"wrote {DOC_PATH}", flush=True)
    print("\nModel/app sample counts:")
    print(counts.to_string(index=False), flush=True)
    print("\nModel/app focal strict-next CAR[0,+1]:")
    focal_car = ordered(focal_next_summary[focal_next_summary["outcome"].eq(MAIN_OUTCOME)])
    print(
        focal_car[["sample_name", "estimate", "se", "p", "nobs", "events", "focal_firms", "median", "positive_share"]]
        .to_string(index=False),
        flush=True,
    )
    print("\nPreferred product-peer CAR[0,+1]:")
    peer_car = ordered(
        peer_summary[
            peer_summary["method_variant"].eq(PREFERRED_METHOD)
            & peer_summary["outcome"].eq(MAIN_OUTCOME)
        ]
    )
    print(peer_car[["sample_name", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"]].to_string(index=False), flush=True)
    print("\nFactSet relation CAR[0,+1]:")
    factset_car = factset_summary[factset_summary["outcome"].eq(MAIN_OUTCOME)]
    print(
        factset_car[
            [
                "sample_name",
                "relation_type",
                "mean",
                "se",
                "p",
                "nobs",
                "events",
                "related_firms",
                "event_weighted_mean",
                "event_weighted_p",
            ]
        ].to_string(index=False),
        flush=True,
    )


if __name__ == "__main__":
    main()
