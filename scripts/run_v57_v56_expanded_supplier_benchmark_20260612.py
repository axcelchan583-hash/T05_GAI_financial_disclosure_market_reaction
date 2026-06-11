#!/usr/bin/env python3
"""Run supplier-return benchmark for the v56 expanded GenAI sample."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v54_v52_supplier_benchmark_20260612 as v54  # noqa: E402


RUN_ID = "v57_v56_expanded_supplier_benchmark_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "118_v57_v56_expanded_supplier_benchmark_20260612.md"
V56_EVENTS = ROOT / "results/v56_v55_expanded_llm_empirical_tables_20260612/expanded_event_samples.csv"
V56_T2 = ROOT / "results/v56_v55_expanded_llm_empirical_tables_20260612/t2_peer_main_effect.csv"
SAMPLES = ["A_all", "A_first_firm", "A_old363_reaudited_first", "Dfw_all", "A_Dfw_stack"]


def md_table(df: pd.DataFrame, cols: list[str] | None = None, limit: int = 20) -> str:
    return v54.md_table(df, cols, limit)


def write_doc(coverage: pd.DataFrame, t9: pd.DataFrame, contrast: pd.DataFrame) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    main = t9[
        t9["edge_family"].eq("union")
        & t9["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
    ].sort_values(["sample_name", "event_type", "outcome"])
    lines = [
        "# v57 v56 expanded supplier benchmark",
        "",
        "## Scope",
        "",
        "- Input events: v56 expanded v52+v55 LLM-coded samples.",
        "- Supplier links: CSMAR supply-chain network plus top-five supplier/customer tables, event-year minus 1 to minus 5.",
        "- Return measure: same market-model abnormal returns as the competitor event study.",
        "- This remains a benchmark because listed-supplier coverage is sparse.",
        "",
        "## Supplier Coverage",
        "",
        md_table(
            coverage.sort_values(["sample_name", "event_type", "edge_family"]),
            [
                "sample_name",
                "event_type",
                "edge_family",
                "input_events",
                "events_with_suppliers",
                "event_link_rate",
                "supplier_event_obs",
                "supplier_firms",
                "customer_firms_with_suppliers",
            ],
            60,
        ),
        "",
        "## T9 Supplier Event Study",
        "",
        md_table(
            main,
            [
                "sample_name",
                "event_type",
                "edge_family",
                "outcome_label",
                "estimate",
                "se",
                "p",
                "nobs",
                "events",
                "peer_firms",
                "median",
                "positive_share",
            ],
            60,
        ),
        "",
        "## Competitor vs Supplier Sign Check",
        "",
        md_table(
            contrast,
            ["side", "sample_name", "edge_family", "outcome_label", "estimate", "se", "p", "events", "firms"],
            10,
        ),
        "",
        "## Output Files",
        "",
        f"- `{OUT_DIR.relative_to(ROOT)}/supplier_coverage_summary.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/supplier_event_panel.csv.gz`",
        f"- `{OUT_DIR.relative_to(ROOT)}/supplier_event_panel_with_returns.csv.gz`",
        f"- `{OUT_DIR.relative_to(ROOT)}/t9_supplier_event_study.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/competitor_vs_supplier_sign_check.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/{RUN_ID}.xlsx`",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    v54.OUT_DIR = OUT_DIR
    v54.V53_EVENTS = V56_EVENTS
    v54.V53_T2 = V56_T2
    v54.SAMPLES = SAMPLES

    events = v54.load_events()
    panel, coverage = v54.build_supplier_panel(events)
    panel.to_csv(OUT_DIR / "supplier_event_panel.csv.gz", index=False)
    coverage.to_csv(OUT_DIR / "supplier_coverage_summary.csv", index=False)

    with_returns = v54.add_supplier_returns(panel)
    with_returns.to_csv(OUT_DIR / "supplier_event_panel_with_returns.csv.gz", index=False)

    t9 = v54.mean_event_study(with_returns)
    contrast = v54.compare_competitor_supplier(t9)
    t9.to_csv(OUT_DIR / "t9_supplier_event_study.csv", index=False)
    contrast.to_csv(OUT_DIR / "competitor_vs_supplier_sign_check.csv", index=False)

    xlsx = OUT_DIR / f"{RUN_ID}.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        coverage.to_excel(writer, sheet_name="Coverage", index=False)
        t9.to_excel(writer, sheet_name="T9_supplier", index=False)
        contrast.to_excel(writer, sheet_name="Sign_check", index=False)

    write_doc(coverage, t9, contrast)

    main_rows = t9[
        t9["sample_name"].eq("A_all")
        & t9["edge_family"].eq("union")
        & t9["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
    ]
    print(f"wrote {OUT_DIR}", flush=True)
    print(f"wrote {DOC_PATH}", flush=True)
    print("\nA_all supplier benchmark:")
    print(main_rows.to_string(index=False), flush=True)
    print("\nCompetitor vs supplier:")
    print(contrast.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
