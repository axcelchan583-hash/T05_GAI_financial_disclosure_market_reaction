#!/usr/bin/env python3
"""Summarize v62 filing-recall candidates after v3.3 LLM coding."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "v63_filing_v3_3_summary_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "123_v63_filing_v3_3_summary_20260612.md"

V62_RECALL_DIR = ROOT / "results/v62_filing_recall_probe_20260612"
V62_LLM_DIR = ROOT / "results/v62_filing_eventlike_v3_3_20260612"
V56_EVENTS = ROOT / "results/v56_v55_expanded_llm_empirical_tables_20260612/expanded_event_samples.csv"


def clean(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


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


def load_merge() -> pd.DataFrame:
    manifest = pd.read_csv(V62_LLM_DIR / "manifest.csv", dtype=str).fillna("")
    parsed = pd.read_csv(V62_LLM_DIR / "siliconflow_parsed_outputs.csv", dtype=str).fillna("")
    candidates = pd.read_csv(V62_RECALL_DIR / "filing_recall_candidates.csv", dtype=str).fillna("")
    merged = manifest.merge(parsed, on="id", how="left", suffixes=("", "_llm"))
    merged = merged.merge(
        candidates[
            [
                "announcement_id",
                "announcement_year",
                "matched_filing_window",
                "eventlike_outside_v56",
                "high_precision_outside_v56",
                "outside_v56_A_all",
            ]
        ],
        on="announcement_id",
        how="left",
    )
    for col in ["model_verdict", "out", "mode", "layer", "realized", "review_priority"]:
        merged[col] = merged[col].map(clean)
    return merged


def summarize_samples(merged: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    v56 = pd.read_csv(V56_EVENTS, dtype=str, low_memory=False).fillna("")
    v56a = v56[v56["sample_name"].eq("A_all")].copy()
    v56a["event_date_dt"] = pd.to_datetime(v56a["event_date"], errors="coerce")
    v56_first = v56a.sort_values(["focal_code", "event_date_dt", "event_id"]).drop_duplicates("focal_code")

    m = merged.copy()
    m["is_A"] = m["model_verdict"].eq("A")
    m["event_date_dt"] = pd.to_datetime(m["event_date"], errors="coerce")
    m["firm_in_v56_A_all"] = m["focal_code"].isin(set(v56a["focal_code"]))
    m["event_in_v56_A_all"] = m["announcement_id"].isin(set(v56a["event_id"]))

    a = m[m["is_A"]].copy()
    combined = pd.concat(
        [
            v56a.rename(columns={"event_id": "announcement_id"})[
                ["announcement_id", "focal_code", "sec_name", "event_date", "announcement_title"]
            ],
            a.rename(columns={"focal_name": "sec_name"})[
                ["announcement_id", "focal_code", "sec_name", "event_date", "announcement_title"]
            ],
        ],
        ignore_index=True,
    ).drop_duplicates("announcement_id")
    combined["event_date_dt"] = pd.to_datetime(combined["event_date"], errors="coerce")
    combined_first = combined.sort_values(["focal_code", "event_date_dt", "announcement_id"]).drop_duplicates("focal_code")

    rows = [
        {
            "sample": "v56_A_all_baseline",
            "events": v56a["event_id"].nunique(),
            "firms": v56a["focal_code"].nunique(),
        },
        {
            "sample": "v62_eventlike_outside_v56_LLM_coded",
            "events": merged["announcement_id"].nunique(),
            "firms": merged["focal_code"].nunique(),
        },
        {
            "sample": "v62_LLM_A_increment_events",
            "events": a["announcement_id"].nunique(),
            "firms": a["focal_code"].nunique(),
        },
        {
            "sample": "v56_plus_v62_A_all",
            "events": combined["announcement_id"].nunique(),
            "firms": combined["focal_code"].nunique(),
        },
        {
            "sample": "v56_A_first_firm_baseline",
            "events": len(v56_first),
            "firms": v56_first["focal_code"].nunique(),
        },
        {
            "sample": "v56_plus_v62_A_first_firm",
            "events": len(combined_first),
            "firms": combined_first["focal_code"].nunique(),
        },
    ]
    summary = pd.DataFrame(rows)
    verdict = (
        merged.groupby(["model_verdict", "out", "mode", "layer", "realized"], dropna=False)
        .agg(events=("announcement_id", "nunique"), firms=("focal_code", "nunique"))
        .reset_index()
        .sort_values(["model_verdict", "out", "mode", "layer", "realized"])
    )
    a["new_firm_vs_v56_A"] = ~a["firm_in_v56_A_all"]
    a_first_new = a[a["new_firm_vs_v56_A"]].sort_values(["focal_code", "event_date_dt", "id"]).drop_duplicates("focal_code")
    return summary, verdict, a_first_new


def write_doc(merged: pd.DataFrame, sample_summary: pd.DataFrame, verdict: pd.DataFrame, first_new: pd.DataFrame) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    a = merged[merged["model_verdict"].eq("A")].copy()
    a_cols = [
        "event_date",
        "focal_code",
        "focal_name",
        "announcement_title",
        "model_verdict",
        "out",
        "mode",
        "layer",
        "realized",
        "review_priority",
        "filing_status_rule",
        "reason",
    ]
    first_cols = [
        "event_date",
        "focal_code",
        "focal_name",
        "announcement_title",
        "out",
        "mode",
        "layer",
        "realized",
        "reason",
    ]
    lines = [
        "# v63 Filing Recall v3.3 LLM Summary",
        "",
        "## Scope",
        "",
        "- Input: v62 event-like filing candidates outside the current v56 A sample.",
        "- Coding prompt: v3.3 GenAI announcement coding prompt.",
        "- API runner: existing SiliconFlow-compatible batch runner.",
        "",
        "## Sample Impact",
        "",
        md_table(sample_summary),
        "",
        "## LLM Verdict Breakdown",
        "",
        md_table(verdict, limit=80),
        "",
        "## v62 Filing Candidates Coded as A",
        "",
        md_table(a[a_cols], limit=40),
        "",
        "## New First-Firm A Candidates Versus v56",
        "",
        md_table(first_new[first_cols], limit=40),
        "",
        "## Interpretation",
        "",
        "- Filing recall does recover real missed GenAI disclosures: 8 of 32 event-like v56-outside filing candidates were coded as A.",
        "- The actual first-firm sample gain is small: v56 A first-firm moves from 160 to 164 firms after adding these A events, because some A filing events belong to firms already present in v56.",
        "- Therefore CAC/algorithm filing is a useful high-precision auxiliary recall arm, not the missing channel that explains the gap between 203 and a 300+ sample.",
        "- The larger `high_precision_outside_v56` queue remains useful for completeness auditing, but many rows are annual reports, shareholder meeting files, ESG/internal-control reports, or progress reports and should not be appended without first-event verification.",
        "",
        "## Outputs",
        "",
        f"- `{OUT_DIR / 'v62_filing_llm_merged.csv'}`",
        f"- `{OUT_DIR / 'v62_filing_llm_sample_impact.csv'}`",
        f"- `{OUT_DIR / 'v62_filing_llm_verdict_breakdown.csv'}`",
        f"- `{OUT_DIR / 'v62_filing_llm_new_first_firm_A.csv'}`",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    merged = load_merge()
    sample_summary, verdict, first_new = summarize_samples(merged)
    merged.to_csv(OUT_DIR / "v62_filing_llm_merged.csv", index=False)
    sample_summary.to_csv(OUT_DIR / "v62_filing_llm_sample_impact.csv", index=False)
    verdict.to_csv(OUT_DIR / "v62_filing_llm_verdict_breakdown.csv", index=False)
    first_new.to_csv(OUT_DIR / "v62_filing_llm_new_first_firm_A.csv", index=False)
    write_doc(merged, sample_summary, verdict, first_new)
    print(sample_summary.to_string(index=False))
    print(f"Wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
