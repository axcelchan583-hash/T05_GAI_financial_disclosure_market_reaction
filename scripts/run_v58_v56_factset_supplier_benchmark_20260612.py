#!/usr/bin/env python3
"""Run FactSet Revere supplier/customer benchmark for the v56 expanded sample."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v38_wide_collaborator_competitor_probe_20260607 as v38  # noqa: E402
import run_v42_factset_relationship_probe_20260607 as v42  # noqa: E402
import run_v43_factset_grouped_relationship_results_20260607 as v43  # noqa: E402


RUN_ID = "v58_v56_factset_supplier_benchmark_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "119_v58_v56_factset_supplier_benchmark_20260612.md"
V56_EVENTS = ROOT / "results/v56_v55_expanded_llm_empirical_tables_20260612/expanded_event_samples.csv"
V42_COMPANY_HISTORY = ROOT / "results/v42_factset_relationship_probe_20260607/factset_a_share_company_history.csv"
V57_COVERAGE = ROOT / "results/v57_v56_expanded_supplier_benchmark_20260612/supplier_coverage_summary.csv"
V57_T9 = ROOT / "results/v57_v56_expanded_supplier_benchmark_20260612/t9_supplier_event_study.csv"

SAMPLES = ["A_all", "A_first_firm", "A_old363_reaudited_first", "Dfw_all", "A_Dfw_stack"]
MAIN_RELATIONS = [
    "factset_upstream_supplier",
    "factset_downstream_customer",
    "factset_relationship_union",
]


def clean(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def md_table(df: pd.DataFrame, cols: list[str] | None = None, limit: int = 60) -> str:
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


def load_events() -> pd.DataFrame:
    events = pd.read_csv(V56_EVENTS, dtype=str, low_memory=False).fillna("")
    events = events[events["sample_name"].isin(SAMPLES)].copy()
    events["event_id"] = events["event_id"].map(clean)
    events["event_key"] = events["event_key"].map(clean)
    events["focal_code"] = events["focal_code"].map(v38.code6)
    events["focal_name"] = events.get("sec_name", "").map(clean)
    events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce")
    events["event_year"] = events["event_date"].dt.year
    events["candidate_row_type"] = events.get("source_batch", "").map(clean)
    events["auto_pdf_label"] = events.get("event_type", "").map(clean)
    events = events[events["focal_code"].ne("") & events["event_date"].notna() & events["event_key"].ne("")].copy()
    return events.drop_duplicates(["sample_name", "event_key"]).reset_index(drop=True)


def load_company_history() -> pd.DataFrame:
    if V42_COMPANY_HISTORY.exists():
        hist = pd.read_csv(V42_COMPANY_HISTORY, dtype=str, low_memory=False).fillna("")
    else:
        hist = v42.build_factset_a_share_history()
    for col in ["fs_start", "fs_end"]:
        hist[col] = pd.to_datetime(hist[col], errors="coerce")
    hist["factset_company_id"] = hist["factset_company_id"].map(v42.norm_factset_id)
    hist["a_share_code"] = hist["a_share_code"].map(v38.code6)
    return hist[hist["factset_company_id"].ne("") & hist["a_share_code"].ne("")].copy()


def coverage_table(events: pd.DataFrame, event_map: pd.DataFrame, grouped: pd.DataFrame, returns: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    inputs = events.groupby("sample_name", as_index=False).agg(input_events=("event_key", "nunique"), input_firms=("focal_code", "nunique"))
    mapped = event_map.groupby("sample_name", as_index=False).agg(mapped_events=("event_key", "nunique"), mapped_firms=("focal_code", "nunique"))
    mapping = inputs.merge(mapped, on="sample_name", how="left").fillna({"mapped_events": 0, "mapped_firms": 0})
    mapping["mapped_event_rate"] = mapping["mapped_events"] / mapping["input_events"]

    if grouped.empty:
        return mapping, pd.DataFrame()
    linked = (
        grouped[grouped["relation_type"].isin(MAIN_RELATIONS)]
        .groupby(["sample_name", "relation_type"], as_index=False)
        .agg(
            linked_rows=("related_code", "size"),
            linked_events=("event_key", "nunique"),
            linked_firms=("focal_code", "nunique"),
            related_firms=("related_code", "nunique"),
        )
        .merge(inputs, on="sample_name", how="left")
    )
    linked["event_link_rate"] = linked["linked_events"] / linked["input_events"]

    if not returns.empty:
        clean_returns = returns[
            returns["relation_type"].isin(MAIN_RELATIONS)
            & returns["complete_clean_m1_p1"].eq(1)
            & returns["peer_car_0_p1_mm"].notna()
        ]
        clean_summary = (
            clean_returns.groupby(["sample_name", "relation_type"], as_index=False)
            .agg(clean_car0p1_rows=("related_code", "size"), clean_car0p1_events=("event_key", "nunique"))
        )
        linked = linked.merge(clean_summary, on=["sample_name", "relation_type"], how="left")
    for col in ["clean_car0p1_rows", "clean_car0p1_events"]:
        if col not in linked.columns:
            linked[col] = 0
        linked[col] = linked[col].fillna(0).astype(int)
    return mapping, linked.sort_values(["sample_name", "relation_type"]).reset_index(drop=True)


def event_study_by_sample(returns: pd.DataFrame) -> pd.DataFrame:
    if returns.empty:
        return pd.DataFrame()
    clean_returns = returns[returns["complete_clean_m1_p1"].eq(1) & returns["relation_type"].isin(MAIN_RELATIONS)].copy()
    rows: list[dict[str, object]] = []
    for (sample_name, relation_type), d in clean_returns.groupby(["sample_name", "relation_type"], dropna=False):
        for outcome, label in v38.OUTCOMES:
            rows.append(
                {
                    "sample_name": sample_name,
                    "relation_type": relation_type,
                    "outcome": outcome,
                    "window": label,
                    **v38.clustered_mean(d, outcome),
                    **v38.event_weighted_mean(d, outcome),
                }
            )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["sample_name", "relation_type", "outcome"]).reset_index(drop=True)


def compare_csmar_factset(factset_study: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    if V57_T9.exists():
        csmar = pd.read_csv(V57_T9)
        sub = csmar[
            csmar["sample_name"].eq("A_all")
            & csmar["edge_family"].eq("union")
            & csmar["outcome"].eq("peer_car_0_p1_mm")
        ]
        if not sub.empty:
            r = sub.iloc[0]
            rows.append(
                {
                    "source": "CSMAR listed supplier union",
                    "sample_name": "A_all",
                    "relation_type": "supplier_union",
                    "window": "CAR[0,+1]",
                    "mean": r["estimate"],
                    "p": r["p"],
                    "nobs": r["nobs"],
                    "events": r["events"],
                    "related_firms": r["peer_firms"],
                    "event_weighted_mean": np.nan,
                    "event_weighted_p": np.nan,
                }
            )
    sub = factset_study[
        factset_study["sample_name"].eq("A_all")
        & factset_study["relation_type"].isin(["factset_upstream_supplier", "factset_downstream_customer"])
        & factset_study["outcome"].eq("peer_car_0_p1_mm")
    ]
    for _, r in sub.iterrows():
        rows.append(
            {
                "source": "FactSet Revere",
                "sample_name": r["sample_name"],
                "relation_type": r["relation_type"],
                "window": r["window"],
                "mean": r["mean"],
                "p": r["p"],
                "nobs": r["nobs"],
                "events": r["events"],
                "related_firms": r["related_firms"],
                "event_weighted_mean": r["event_weighted_mean"],
                "event_weighted_p": r["event_weighted_p"],
            }
        )
    return pd.DataFrame(rows)


def write_doc(
    events: pd.DataFrame,
    company_hist: pd.DataFrame,
    mapping: pd.DataFrame,
    coverage: pd.DataFrame,
    study: pd.DataFrame,
    compare: pd.DataFrame,
) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    main = study[
        study["sample_name"].isin(["A_all", "A_first_firm", "A_old363_reaudited_first"])
        & study["relation_type"].isin(["factset_upstream_supplier", "factset_downstream_customer"])
        & study["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
    ].sort_values(["sample_name", "relation_type", "outcome"])
    lines = [
        "# v58 v56 FactSet supplier/customer benchmark",
        "",
        "## Scope",
        "",
        "- Input events: v56 expanded v52+v55 LLM-coded samples.",
        "- Relationship source: FactSet Revere Supply Chain Relationships, already downloaded locally.",
        "- Mapping: reuse v42 conservative A-share FactSet company history, then keep relationships overlapping the five-year pre-event window.",
        "- Important distinction: this is broader FactSet Revere relationship coverage, not the narrow CSMAR/Qian-style listed supplier benchmark.",
        "",
        "## Input And Mapping",
        "",
        f"- Event rows across requested samples: `{len(events):,}`",
        f"- FactSet A-share company-history rows: `{len(company_hist):,}`",
        "",
        md_table(mapping, limit=20),
        "",
        "## FactSet Coverage",
        "",
        md_table(
            coverage,
            [
                "sample_name",
                "relation_type",
                "input_events",
                "linked_events",
                "event_link_rate",
                "linked_rows",
                "related_firms",
                "clean_car0p1_rows",
                "clean_car0p1_events",
            ],
            60,
        ),
        "",
        "## FactSet Event Study",
        "",
        md_table(
            main,
            [
                "sample_name",
                "relation_type",
                "window",
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
                "event_weighted_events",
            ],
            60,
        ),
        "",
        "## CSMAR vs FactSet",
        "",
        md_table(compare, limit=20),
        "",
        "## Output Files",
        "",
        f"- `results/{RUN_ID}/factset_event_focal_map.csv`",
        f"- `results/{RUN_ID}/factset_event_relationship_links.csv`",
        f"- `results/{RUN_ID}/factset_grouped_links.csv`",
        f"- `results/{RUN_ID}/factset_relation_panel.csv.gz`",
        f"- `results/{RUN_ID}/factset_coverage_summary.csv`",
        f"- `results/{RUN_ID}/factset_event_study.csv`",
        f"- `results/{RUN_ID}/csmar_vs_factset_supplier_check.csv`",
        f"- `results/{RUN_ID}/{RUN_ID}.xlsx`",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    events = load_events()
    print(f"events={len(events):,}, unique event_keys={events['event_key'].nunique():,}", flush=True)

    company_hist = load_company_history()
    print(f"factset A-share map rows={len(company_hist):,}, codes={company_hist['a_share_code'].nunique():,}", flush=True)

    event_map = v42.map_events_to_factset(events, company_hist)
    print(f"mapped focal events={len(event_map):,}/{len(events):,}", flush=True)

    links = v42.extract_factset_event_relations(event_map, company_hist)
    print(f"factset raw links={len(links):,}, events={links['event_key'].nunique() if not links.empty else 0:,}", flush=True)

    grouped = v43.build_grouped_links(links) if not links.empty else links.copy()
    print(f"factset grouped links={len(grouped):,}, events={grouped['event_key'].nunique() if not grouped.empty else 0:,}", flush=True)

    stock = v38.pe.load_stock_model()
    returns = v38.attach_returns(grouped, stock) if not grouped.empty else grouped.copy()
    mapping, coverage = coverage_table(events, event_map, grouped, returns)
    study = event_study_by_sample(returns)
    compare = compare_csmar_factset(study)

    relation_panel = v43.standardize_plus(returns, "factset_relation") if not returns.empty else returns.copy()

    event_map.to_csv(OUT_DIR / "factset_event_focal_map.csv", index=False, encoding="utf-8-sig")
    links.to_csv(OUT_DIR / "factset_event_relationship_links.csv", index=False, encoding="utf-8-sig")
    grouped.to_csv(OUT_DIR / "factset_grouped_links.csv", index=False, encoding="utf-8-sig")
    relation_panel.to_csv(OUT_DIR / "factset_relation_panel.csv.gz", index=False)
    mapping.to_csv(OUT_DIR / "factset_mapping_summary.csv", index=False, encoding="utf-8-sig")
    coverage.to_csv(OUT_DIR / "factset_coverage_summary.csv", index=False, encoding="utf-8-sig")
    study.to_csv(OUT_DIR / "factset_event_study.csv", index=False, encoding="utf-8-sig")
    compare.to_csv(OUT_DIR / "csmar_vs_factset_supplier_check.csv", index=False, encoding="utf-8-sig")

    xlsx = OUT_DIR / f"{RUN_ID}.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        mapping.to_excel(writer, sheet_name="Mapping", index=False)
        coverage.to_excel(writer, sheet_name="Coverage", index=False)
        study.to_excel(writer, sheet_name="FactSet_event_study", index=False)
        compare.to_excel(writer, sheet_name="CSMAR_vs_FactSet", index=False)

    write_doc(events, company_hist, mapping, coverage, study, compare)
    print(f"wrote {OUT_DIR}", flush=True)
    print(f"wrote {DOC_PATH}", flush=True)
    print("\nCSMAR vs FactSet A_all CAR[0,+1]:")
    print(compare.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
