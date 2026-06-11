#!/usr/bin/env python3
"""Publication-style descriptive and baseline tables for the v36 main peer specification."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v25_empirical_table_pack_20260604 as v25  # noqa: E402


RUN_ID = "v27_v36_main_tables_20260605"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "91_v27_v36_main_tables_20260605.md"

V26_DIR = ROOT / "results" / "v26_v36_x_peer_retest_20260604"
PANEL_PATH = V26_DIR / "v36_peer_event_study_panel_light.csv.gz"
SPEC_PATH = V26_DIR / "v36_specificity_measures.csv"
GRID_PATH = V26_DIR / "v36_specificity_x_ai_peer_regressions.csv"

SAMPLE_NAME = "combined_first_event_per_firm"
METHOD_VARIANT = "liu_product_tfidf_same_industry_d_top10"
METHOD_LABEL = "Liu product-word TF-IDF same-industry Top10"
SPEC_RAW = "legacy_detail_density_raw"
OUTCOME = "peer_car_0_p1_mm"
PRE_CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]


def load_main_sample() -> pd.DataFrame:
    panel = pd.read_csv(
        PANEL_PATH,
        dtype={"event_id": str, "event_key": str, "focal_code": str, "peer_code": str},
        low_memory=False,
    )
    specs = pd.read_csv(SPEC_PATH, dtype={"event_id": str, "event_key": str, "focal_code": str}, low_memory=False)
    specs = specs[specs["sample_name"].eq(SAMPLE_NAME)].copy()
    specs["spec_z"] = v25.zscore(v25.winsorize(specs[SPEC_RAW]))
    specs = specs[
        [
            "event_key",
            "legacy_detail_density_raw",
            "spec_z",
            "specificity_source",
            "qian_recall_score",
        ]
    ].drop_duplicates("event_key")

    d = panel[
        panel["sample_name"].eq(SAMPLE_NAME)
        & panel["method_variant"].eq(METHOD_VARIANT)
        & panel["time_valid_prior_year"].eq(1)
        & panel["complete_clean_m1_p1"].eq(1)
    ].copy()
    d = d.merge(specs, on="event_key", how="left")
    for col in [
        OUTCOME,
        "peer_ar0_mm",
        "peer_car_m1_p1_mm",
        *PRE_CONTROLS,
        "peer_rank",
        "peer_similarity",
        "ext_any",
        "current_text_history",
        "legacy_detail_density_raw",
        "spec_z",
        "qian_recall_score",
    ]:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    d["ai"] = d["ext_any"].fillna(0.0).astype(float)
    d["text_history"] = d["current_text_history"].fillna(0.0).astype(float)
    d["spec_ai"] = d["spec_z"] * d["ai"]
    d["spec_text_history"] = d["spec_z"] * d["text_history"]
    d["snippet_fallback"] = d["specificity_source"].eq("v36_snippet").astype(int)
    d = d.dropna(
        subset=[
            OUTCOME,
            *PRE_CONTROLS,
            "spec_z",
            "ai",
            "spec_ai",
            "peer_industry_week",
            "event_key",
            "peer_code",
        ]
    ).copy()
    return d


def desc_table(d: pd.DataFrame) -> pd.DataFrame:
    variables = [
        ("PeerCAR[0,+1]", OUTCOME),
        ("DetailDensity", "legacy_detail_density_raw"),
        ("Spec", "spec_z"),
        ("AIActive", "ai"),
        ("Spec x AIActive", "spec_ai"),
        ("PeerCAR[-10,-2]", "peer_car_pre10_m2_mm"),
        ("PeerCAR[-20,-2]", "peer_car_pre20_m2_mm"),
        ("PeerAR[0]", "peer_ar0_mm"),
        ("PeerCAR[-1,+1]", "peer_car_m1_p1_mm"),
        ("PeerRank", "peer_rank"),
        ("PeerSimilarity", "peer_similarity"),
        ("TextHistory", "text_history"),
        ("SnippetFallback", "snippet_fallback"),
    ]
    rows = []
    for label, col in variables:
        x = pd.to_numeric(d[col], errors="coerce")
        rows.append(
            {
                "变量": label,
                "观测值": int(x.notna().sum()),
                "均值": x.mean(),
                "标准差": x.std(ddof=0),
                "最小值": x.min(),
                "中位数": x.median(),
                "最大值": x.max(),
            }
        )
    return pd.DataFrame(rows)


def stars(p_value: object) -> str:
    if p_value is None or pd.isna(p_value):
        return ""
    p = float(p_value)
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def fmt_num(value: object, digits: int = 4) -> str:
    if value is None or pd.isna(value):
        return ""
    return f"{float(value):.{digits}f}"


def fmt_coef(res: dict[str, object], var: str) -> str:
    coef = res.get(f"{var}_coef")
    if coef is None or pd.isna(coef):
        return ""
    return f"{fmt_num(coef)}{stars(res.get(f'{var}_p'))}"


def fmt_se(res: dict[str, object], var: str) -> str:
    se = res.get(f"{var}_se")
    if se is None or pd.isna(se):
        return ""
    return f"({fmt_num(se)})"


def run_models(d: pd.DataFrame) -> list[dict[str, object]]:
    specs = [
        {
            "col": "(1)",
            "dep": "PeerCAR[0,+1]",
            "title": "事件固定效应",
            "data": d,
            "outcome": OUTCOME,
            "xvars": ["ai", "spec_ai"],
            "fe": ["event_key"],
            "interaction": "spec_ai",
            "ai_var": "ai",
        },
        {
            "col": "(2)",
            "dep": "PeerCAR[0,+1]",
            "title": "加入预收益控制",
            "data": d,
            "outcome": OUTCOME,
            "xvars": ["ai", "spec_ai", *PRE_CONTROLS],
            "fe": ["event_key"],
            "interaction": "spec_ai",
            "ai_var": "ai",
        },
        {
            "col": "(3)",
            "dep": "PeerCAR[0,+1]",
            "title": "Peer公司固定效应",
            "data": d,
            "outcome": OUTCOME,
            "xvars": ["ai", "spec_ai", *PRE_CONTROLS],
            "fe": ["event_key", "peer_code"],
            "interaction": "spec_ai",
            "ai_var": "ai",
        },
        {
            "col": "(4)",
            "dep": "PeerAR[0]",
            "title": "替换被解释变量",
            "data": d,
            "outcome": "peer_ar0_mm",
            "xvars": ["ai", "spec_ai", *PRE_CONTROLS],
            "fe": ["event_key"],
            "interaction": "spec_ai",
            "ai_var": "ai",
        },
        {
            "col": "(5)",
            "dep": "PeerCAR[-1,+1]",
            "title": "替换被解释变量",
            "data": d,
            "outcome": "peer_car_m1_p1_mm",
            "xvars": ["ai", "spec_ai", *PRE_CONTROLS],
            "fe": ["event_key"],
            "interaction": "spec_ai",
            "ai_var": "ai",
        },
        {
            "col": "(6)",
            "dep": "PeerCAR[0,+1]",
            "title": "替换AI口径",
            "data": d.rename(columns={"text_history": "ai_alt", "spec_text_history": "spec_ai_alt"}),
            "outcome": OUTCOME,
            "xvars": ["ai_alt", "spec_ai_alt", *PRE_CONTROLS],
            "fe": ["event_key"],
            "interaction": "spec_ai_alt",
            "ai_var": "ai_alt",
        },
    ]
    rows = []
    for spec in specs:
        res = v25.fit_absorbed_ols(spec["data"], spec["outcome"], spec["xvars"], spec["fe"])
        row = {k: v for k, v in spec.items() if k != "data"}
        if res:
            row.update(res)
        rows.append(row)
    return rows


def baseline_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    cols = [r["col"] for r in rows]
    table_rows: list[dict[str, str]] = []
    table_rows.append({"变量": "", **{r["col"]: r["dep"] for r in rows}})
    table_rows.append({"变量": "", **{r["col"]: r["title"] for r in rows}})

    table_rows.append({"变量": "Spec", **{r["col"]: "-" for r in rows}})
    table_rows.append(
        {
            "变量": "Spec x AIActive",
            **{
                r["col"]: fmt_coef(r, str(r["interaction"]))
                for r in rows
            },
        }
    )
    table_rows.append(
        {
            "变量": "",
            **{
                r["col"]: fmt_se(r, str(r["interaction"]))
                for r in rows
            },
        }
    )
    table_rows.append(
        {
            "变量": "AIActive / TextHistory",
            **{
                r["col"]: fmt_coef(r, str(r["ai_var"]))
                for r in rows
            },
        }
    )
    table_rows.append(
        {
            "变量": "",
            **{
                r["col"]: fmt_se(r, str(r["ai_var"]))
                for r in rows
            },
        }
    )
    for var, label in [
        ("peer_car_pre10_m2_mm", "PeerCAR[-10,-2]"),
        ("peer_car_pre20_m2_mm", "PeerCAR[-20,-2]"),
    ]:
        table_rows.append({"变量": label, **{r["col"]: fmt_coef(r, var) for r in rows}})
        table_rows.append({"变量": "", **{r["col"]: fmt_se(r, var) for r in rows}})

    table_rows.extend(
        [
            {"变量": "Event FE", **{r["col"]: "YES" if "event_key" in r["fe"] else "NO" for r in rows}},
            {
                "变量": "PeerInd x Week FE",
                **{r["col"]: "YES" if "peer_industry_week" in r["fe"] else "NO" for r in rows},
            },
            {"变量": "Peer Firm FE", **{r["col"]: "YES" if "peer_code" in r["fe"] else "NO" for r in rows}},
            {"变量": "N", **{r["col"]: str(r.get("nobs", "")) for r in rows}},
            {"变量": "Events", **{r["col"]: str(r.get("events", "")) for r in rows}},
            {"变量": "Peer firms", **{r["col"]: str(r.get("peer_firms", "")) for r in rows}},
            {"变量": "Overall R2", **{r["col"]: fmt_num(r.get("overall_r2", r.get("r2")), 3) for r in rows}},
            {"变量": "Within R2", **{r["col"]: fmt_num(r.get("within_r2"), 3) for r in rows}},
        ]
    )
    return pd.DataFrame(table_rows, columns=["变量", *cols])


def format_desc(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["均值", "标准差", "最小值", "中位数", "最大值"]:
        out[col] = out[col].map(lambda x: fmt_num(x, 4))
    return out


def markdown_table(df: pd.DataFrame) -> str:
    rows = ["| " + " | ".join(df.columns) + " |", "|" + "|".join("---" for _ in df.columns) + "|"]
    for _, row in df.iterrows():
        rows.append("| " + " | ".join("" if pd.isna(row[c]) else str(row[c]) for c in df.columns) + " |")
    return "\n".join(rows)


def save_outputs(desc: pd.DataFrame, baseline: pd.DataFrame, d: pd.DataFrame, rows: list[dict[str, object]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    desc.to_csv(OUT_DIR / "table1_descriptive_statistics.csv", index=False)
    baseline.to_csv(OUT_DIR / "table2_baseline_regressions.csv", index=False)
    pd.DataFrame(rows).drop(columns=["xvars", "fe"], errors="ignore").to_csv(
        OUT_DIR / "table2_baseline_regression_raw_results.csv", index=False
    )
    meta = pd.DataFrame(
        [
            {
                "sample_name": SAMPLE_NAME,
                "method_variant": METHOD_VARIANT,
                "method_label": METHOD_LABEL,
                "main_model_column": "(2)",
                "nobs_main_model": int(rows[1].get("nobs", 0)),
                "events_main_model": int(rows[1].get("events", 0)),
                "peer_firms_main_model": int(rows[1].get("peer_firms", 0)),
                "focal_firms_main_model": int(rows[1].get("focal_firms", 0)),
                "snippet_fallback_rows": int(d["snippet_fallback"].sum()),
                "snippet_fallback_events": int(d.loc[d["snippet_fallback"].eq(1), "event_key"].nunique()),
            }
        ]
    )
    meta.to_csv(OUT_DIR / "main_spec_sample_metadata.csv", index=False)
    xlsx_path = OUT_DIR / f"{RUN_ID}.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        for sheet, df in [
            ("Table1_Desc", desc),
            ("Table2_Baseline", baseline),
            ("RawResults", pd.DataFrame(rows).drop(columns=["xvars", "fe"], errors="ignore")),
            ("Metadata", meta),
        ]:
            df.to_excel(writer, sheet_name=sheet, index=False)
            ws = writer.book[sheet]
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 10), 45)

    lines = [
        "# v27 v36 main tables",
        "",
        "## Scope",
        "",
        f"- Sample: `{SAMPLE_NAME}`.",
        f"- Peer construction: `{METHOD_VARIANT}` ({METHOD_LABEL}).",
        "- X: `legacy_detail_density` standardized within the first-event sample.",
        "- AI-active peer proxy: `ext_any` in columns (1)-(5); `current_text_history` in column (6).",
        "- Outcome: `PeerCAR[0,+1]` from the market-model event-study panel.",
        "- Standard errors are two-way clustered by event and peer firm.",
        "",
        "## Sample Metadata",
        "",
        markdown_table(meta),
        "",
        "## 表 1 变量的描述性统计",
        "",
        markdown_table(desc),
        "",
        "## 表 2 基准回归检验",
        "",
        markdown_table(baseline),
        "",
        "## Notes",
        "",
        "- `Spec` is omitted because event fixed effects absorb event-level disclosure specificity.",
        "- Since the main peer construction already restricts peers to the same CSRC broad industry, peer-industry-week fixed effects are collinear with event fixed effects and are not separately reported in the main baseline table.",
        "- `Overall R2` includes the explanatory power of fixed effects; `Within R2` is the incremental explanatory power after absorbing fixed effects.",
        "- `***`, `**`, and `*` indicate significance at 1%, 5%, and 10%.",
        "- Column (2) is the intended main baseline specification.",
        "",
        "## Output Files",
        "",
        f"- `{OUT_DIR.relative_to(ROOT)}/table1_descriptive_statistics.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/table2_baseline_regressions.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/table2_baseline_regression_raw_results.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/main_spec_sample_metadata.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/{RUN_ID}.xlsx`",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    d = load_main_sample()
    desc = format_desc(desc_table(d))
    rows = run_models(d)
    baseline = baseline_table(rows)
    save_outputs(desc, baseline, d, rows)
    print(f"main sample rows={len(d):,}, events={d['event_key'].nunique():,}, peers={d['peer_code'].nunique():,}", flush=True)
    print(baseline.to_string(index=False), flush=True)
    print(f"wrote {OUT_DIR}", flush=True)
    print(f"wrote {DOC_PATH}", flush=True)


if __name__ == "__main__":
    main()
