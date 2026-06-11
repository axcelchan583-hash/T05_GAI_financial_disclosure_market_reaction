#!/usr/bin/env python3
"""POM-style peer event-study and cross-sectional regression tables."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v23_cninfo_1055_peer_event_study_20260603 as pe  # noqa: E402
import run_v25_empirical_table_pack_20260604 as v25  # noqa: E402
import run_v28_v36_peer_main_effect_tables_20260605 as v28  # noqa: E402


RUN_ID = "v29_pom_style_peer_results_20260605"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "93_v29_pom_style_peer_results_20260605.md"

SAMPLE_NAME = v28.SAMPLE_NAME
METHOD_VARIANT = v28.METHOD_VARIANT
METHOD_LABEL = v28.METHOD_LABEL
PRE_CONTROLS = v28.PRE_CONTROLS

DAY_OUTCOMES = [
    ("Day -1 (1)", "peer_ar_m1_mm"),
    ("Day 0 (2)", "peer_ar0_mm"),
    ("Day 1 (3)", "peer_ar_p1_mm"),
]

MODEL_XVARS = [
    "ai",
    "spec_ai",
    "peer_rank",
    "peer_similarity",
    *PRE_CONTROLS,
]

ROW_LABELS = {
    "spec_z": "Spec",
    "spec_ai": "Spec x AIActivePeer",
    "ai": "AIActivePeer",
    "peer_rank": "PeerRank",
    "peer_similarity": "PeerSimilarity",
    "peer_car_pre10_m2_mm": "PeerCAR[-10,-2]",
    "peer_car_pre20_m2_mm": "PeerCAR[-20,-2]",
}


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


def markdown_table(df: pd.DataFrame) -> str:
    rows = ["| " + " | ".join(df.columns) + " |", "|" + "|".join("---" for _ in df.columns) + "|"]
    for _, row in df.iterrows():
        rows.append("| " + " | ".join("" if pd.isna(row[c]) else str(row[c]) for c in df.columns) + " |")
    return "\n".join(rows)


def wilcoxon_signed_rank(x: pd.Series) -> dict[str, float]:
    y = pd.to_numeric(x, errors="coerce").dropna().astype(float)
    nonzero = y[y.ne(0)]
    if len(nonzero) == 0:
        return {"wilcoxon_z": math.nan, "wilcoxon_p": math.nan}
    abs_rank = nonzero.abs().rank(method="average")
    w_plus = float(abs_rank[nonzero > 0].sum())
    n = int(len(nonzero))
    mean = n * (n + 1) / 4.0
    var = n * (n + 1) * (2 * n + 1) / 24.0
    z_value = (w_plus - mean) / math.sqrt(var) if var > 0 else math.nan
    return {"wilcoxon_z": float(z_value), "wilcoxon_p": v25.p_from_z(float(z_value))}


def binomial_sign_test(x: pd.Series) -> dict[str, float]:
    y = pd.to_numeric(x, errors="coerce").dropna().astype(float)
    n = int(len(y))
    if n == 0:
        return {"positive_share": math.nan, "binomial_z": math.nan, "binomial_p": math.nan}
    positives = int((y > 0).sum())
    z_value = (positives - 0.5 * n) / math.sqrt(0.25 * n) if n > 0 else math.nan
    return {
        "positive_share": positives / n,
        "binomial_z": float(z_value),
        "binomial_p": v25.p_from_z(float(z_value)),
    }


def pom_event_study(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_rows: list[dict[str, object]] = []
    formatted: dict[str, dict[str, str]] = {
        "Average abnormal return": {},
        "t-test (clustered t-statistic)": {},
        "Median abnormal return": {},
        "Wilcoxon signed rank test (Z-statistic)": {},
        "Positive rate of the abnormal returns": {},
        "Binomial sign test (Z-statistic)": {},
        "Observations": {},
    }
    for col_label, outcome in DAY_OUTCOMES:
        d = panel.dropna(subset=[outcome, "event_key", "peer_code"]).copy()
        y = pd.to_numeric(d[outcome], errors="coerce").dropna()
        mean_stats = pe.clustered_mean(d, outcome)
        wilcox = wilcoxon_signed_rank(y)
        sign = binomial_sign_test(y)
        raw = {
            "window": col_label.replace("\n", " "),
            "outcome": outcome,
            **mean_stats,
            **wilcox,
            **sign,
        }
        raw_rows.append(raw)
        formatted["Average abnormal return"][col_label] = f"{fmt_num(raw['estimate'])}{stars(raw['p'])}"
        formatted["t-test (clustered t-statistic)"][col_label] = f"({fmt_num(raw['z'], 4)})"
        formatted["Median abnormal return"][col_label] = f"{fmt_num(raw['median'])}{stars(raw['wilcoxon_p'])}"
        formatted["Wilcoxon signed rank test (Z-statistic)"][col_label] = f"({fmt_num(raw['wilcoxon_z'], 4)})"
        formatted["Positive rate of the abnormal returns"][col_label] = (
            f"{fmt_num(raw['positive_share'])}{stars(raw['binomial_p'])}"
        )
        formatted["Binomial sign test (Z-statistic)"][col_label] = f"({fmt_num(raw['binomial_z'], 4)})"
        formatted["Observations"][col_label] = str(int(raw["nobs"]))

    table = pd.DataFrame([{"Variables": key, **values} for key, values in formatted.items()])
    raw_table = pd.DataFrame(raw_rows)
    return table, raw_table


def regression_sample() -> tuple[pd.DataFrame, pd.DataFrame]:
    event_panel = v28.load_event_panel()
    with_spec = v28.attach_specificity(event_panel)
    model_panel = v28.mechanism_sample(with_spec)
    return event_panel, model_panel


def fit_model(data: pd.DataFrame, outcome: str, xvars: list[str], fe_cols: list[str]) -> dict[str, object]:
    res = v28.fit_absorbed_ols(data, outcome, xvars, fe_cols)
    if res is None:
        raise RuntimeError(f"model failed: outcome={outcome}, fe={fe_cols}")
    res["outcome"] = outcome
    res["xvars"] = ",".join(xvars)
    res["fe_cols"] = ",".join(fe_cols)
    return res


def run_cross_section_models(model_panel: pd.DataFrame) -> list[dict[str, object]]:
    specs = [
        {
            "col": "(1)",
            "dep": "PeerAR[0]",
            "title": "Event FE",
            "outcome": "peer_ar0_mm",
            "xvars": MODEL_XVARS,
            "fe": ["event_key"],
        },
        {
            "col": "(2)",
            "dep": "PeerAR[0]",
            "title": "Event + industry-week FE",
            "outcome": "peer_ar0_mm",
            "xvars": MODEL_XVARS,
            "fe": ["event_key", "peer_industry_week"],
        },
        {
            "col": "(3)",
            "dep": "PeerAR[0]",
            "title": "Event + peer-firm FE",
            "outcome": "peer_ar0_mm",
            "xvars": MODEL_XVARS,
            "fe": ["event_key", "peer_code"],
        },
        {
            "col": "(4)",
            "dep": "PeerCAR[0,+1]",
            "title": "Event FE",
            "outcome": "peer_car_0_p1_mm",
            "xvars": MODEL_XVARS,
            "fe": ["event_key"],
        },
        {
            "col": "(5)",
            "dep": "PeerCAR[0,+1]",
            "title": "Event + industry-week FE",
            "outcome": "peer_car_0_p1_mm",
            "xvars": MODEL_XVARS,
            "fe": ["event_key", "peer_industry_week"],
        },
        {
            "col": "(6)",
            "dep": "PeerCAR[0,+1]",
            "title": "Event + peer-firm FE",
            "outcome": "peer_car_0_p1_mm",
            "xvars": MODEL_XVARS,
            "fe": ["event_key", "peer_code"],
        },
    ]
    rows: list[dict[str, object]] = []
    for spec in specs:
        res = fit_model(model_panel, spec["outcome"], spec["xvars"], spec["fe"])
        rows.append({**spec, **res})
    return rows


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


def cross_section_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    table_rows: list[dict[str, str]] = []
    table_rows.append({"Variables": "", **{r["col"]: r["dep"] for r in rows}})
    table_rows.append({"Variables": "", **{r["col"]: r["title"] for r in rows}})
    table_rows.append({"Variables": "Spec", **{r["col"]: "-" for r in rows}})
    for var in [
        "spec_ai",
        "ai",
        "peer_rank",
        "peer_similarity",
        "peer_car_pre10_m2_mm",
        "peer_car_pre20_m2_mm",
    ]:
        table_rows.append({"Variables": ROW_LABELS[var], **{r["col"]: fmt_coef(r, var) for r in rows}})
        table_rows.append({"Variables": "", **{r["col"]: fmt_se(r, var) for r in rows}})
    table_rows.extend(
        [
            {"Variables": "Event FE", **{r["col"]: "YES" if "event_key" in r["fe"] else "NO" for r in rows}},
            {
                "Variables": "Peer industry-week FE",
                **{r["col"]: "YES" if "peer_industry_week" in r["fe"] else "NO" for r in rows},
            },
            {"Variables": "Peer firm FE", **{r["col"]: "YES" if "peer_code" in r["fe"] else "NO" for r in rows}},
            {"Variables": "Observations", **{r["col"]: str(r.get("nobs", "")) for r in rows}},
            {"Variables": "Events", **{r["col"]: str(r.get("events", "")) for r in rows}},
            {"Variables": "Peer firms", **{r["col"]: str(r.get("peer_firms", "")) for r in rows}},
            {"Variables": "Overall R2", **{r["col"]: fmt_num(r.get("overall_r2"), 3) for r in rows}},
            {"Variables": "Within R2", **{r["col"]: fmt_num(r.get("within_r2"), 3) for r in rows}},
        ]
    )
    return pd.DataFrame(table_rows, columns=["Variables", *[r["col"] for r in rows]])


def descriptive_table(event_panel: pd.DataFrame, model_panel: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "sample": "Event-study sample",
            "observations": int(len(event_panel)),
            "events": int(event_panel["event_key"].nunique()),
            "focal_firms": int(event_panel["focal_code"].nunique()),
            "peer_firms": int(event_panel["peer_code"].nunique()),
        },
        {
            "sample": "Cross-sectional regression sample",
            "observations": int(len(model_panel)),
            "events": int(model_panel["event_key"].nunique()),
            "focal_firms": int(model_panel["focal_code"].nunique()),
            "peer_firms": int(model_panel["peer_code"].nunique()),
        },
    ]
    return pd.DataFrame(rows)


def save_outputs(
    desc: pd.DataFrame,
    table2: pd.DataFrame,
    table2_raw: pd.DataFrame,
    table3: pd.DataFrame,
    table3_raw: pd.DataFrame,
    event_panel: pd.DataFrame,
    model_panel: pd.DataFrame,
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    desc.to_csv(OUT_DIR / "table1_sample_summary.csv", index=False)
    table2.to_csv(OUT_DIR / "table2_pom_style_peer_event_study.csv", index=False)
    table2_raw.to_csv(OUT_DIR / "table2_pom_style_peer_event_study_raw.csv", index=False)
    table3.to_csv(OUT_DIR / "table3_pom_style_cross_section_regressions.csv", index=False)
    table3_raw.to_csv(OUT_DIR / "table3_pom_style_cross_section_regressions_raw.csv", index=False)
    event_panel.to_csv(OUT_DIR / "analysis_sample_used_in_table2.csv", index=False)
    model_panel.to_csv(OUT_DIR / "analysis_sample_used_in_table3.csv", index=False)

    xlsx_path = OUT_DIR / f"{RUN_ID}.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        for sheet_name, df in [
            ("Table1_Sample", desc),
            ("Table2_EventStudy", table2),
            ("Table2_Raw", table2_raw),
            ("Table3_Regressions", table3),
            ("Table3_Raw", table3_raw),
        ]:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            ws = writer.book[sheet_name]
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 10), 48)

    table2_raw_day0 = table2_raw.loc[table2_raw["outcome"].eq("peer_ar0_mm")].iloc[0]
    table3_key = table3_raw.loc[table3_raw["col"].eq("(1)")].iloc[0]
    table3_car_key = table3_raw.loc[table3_raw["col"].eq("(4)")].iloc[0]

    lines = [
        "# v29 POM-style peer results",
        "",
        "## Scope",
        "",
        f"- Sample: `{SAMPLE_NAME}`.",
        f"- Peer construction: `{METHOD_VARIANT}` ({METHOD_LABEL}).",
        "- Table 2 is the POM-style event-study table: it tests whether product-market peers have abnormal stock returns around focal-firm GenAI disclosures.",
        "- Table 3 is the POM-style cross-sectional regression table: it tests which observable characteristics explain or moderate those peer reactions.",
        "- Mean-return t-statistics in Table 2 and regression standard errors in Table 3 are two-way clustered by event and peer firm.",
        "- Wilcoxon signed-rank and binomial sign-test Z-statistics in Table 2 use normal approximations.",
        "- `Spec` is event-level disclosure specificity, so it is absorbed by event fixed effects; `Spec x AIActivePeer` remains identified by within-event differences across peers.",
        "- Other event-level source controls are also absorbed by event fixed effects and therefore are not displayed in Table 3.",
        "",
        "## Table 1 Sample Summary",
        "",
        markdown_table(desc),
        "",
        "## Table 2 Event Study Results on Peers' Stock Market Reaction",
        "",
        markdown_table(table2),
        "",
        "## Table 3 Cross-Sectional Regression Results on Factors Influencing Peer Reactions",
        "",
        markdown_table(table3),
        "",
        "## Headline Read",
        "",
        (
            f"- Peer AR on day 0 is {fmt_num(table2_raw_day0['estimate'])}{stars(table2_raw_day0['p'])}; "
            f"the day-0 clustered statistic is {fmt_num(table2_raw_day0['z'])}."
        ),
        (
            f"- In the AR0 regression, `Spec x AIActivePeer` is "
            f"{fmt_num(table3_key['spec_ai_coef'])}{stars(table3_key['spec_ai_p'])} "
            f"({fmt_num(table3_key['spec_ai_se'])}) in column (1)."
        ),
        (
            f"- In the CAR[0,+1] regression, `Spec x AIActivePeer` is "
            f"{fmt_num(table3_car_key['spec_ai_coef'])}{stars(table3_car_key['spec_ai_p'])} "
            f"({fmt_num(table3_car_key['spec_ai_se'])}) in column (4)."
        ),
        "",
        "## Output Files",
        "",
        f"- `{OUT_DIR.relative_to(ROOT)}/table1_sample_summary.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/table2_pom_style_peer_event_study.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/table2_pom_style_peer_event_study_raw.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/table3_pom_style_cross_section_regressions.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/table3_pom_style_cross_section_regressions_raw.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/analysis_sample_used_in_table2.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/analysis_sample_used_in_table3.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/{RUN_ID}.xlsx`",
        "",
        "## Notes",
        "",
        "- `***`, `**`, and `*` indicate significance at 1%, 5%, and 10% in two-sided tests.",
        "- Wilcoxon signed-rank and binomial sign-test Z-statistics in Table 2 use normal approximations.",
        "- `Overall R2` includes fixed-effect explanatory power; `Within R2` is the incremental explanatory power after absorbing fixed effects.",
        "- Column (3) and column (6) add peer-firm fixed effects, so they are strict robustness checks rather than the preferred mechanism specification.",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    event_panel, model_panel = regression_sample()
    desc = descriptive_table(event_panel, model_panel)
    table2, table2_raw = pom_event_study(event_panel)
    model_rows = run_cross_section_models(model_panel)
    table3 = cross_section_table(model_rows)
    table3_raw = pd.DataFrame(model_rows)
    save_outputs(desc, table2, table2_raw, table3, table3_raw, event_panel, model_panel)

    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")
    print(table2.to_string(index=False))
    print(table3.to_string(index=False))


if __name__ == "__main__":
    main()
