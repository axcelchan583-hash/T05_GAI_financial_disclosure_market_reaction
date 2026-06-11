#!/usr/bin/env python3
"""Publication-style tables with peer event-study main effect first."""

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


RUN_ID = "v28_v36_peer_main_effect_tables_20260605"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "92_v28_v36_peer_main_effect_tables_20260605.md"

V26_DIR = ROOT / "results" / "v26_v36_x_peer_retest_20260604"
PANEL_PATH = V26_DIR / "v36_peer_event_study_panel_light.csv.gz"
SPEC_PATH = V26_DIR / "v36_specificity_measures.csv"

SAMPLE_NAME = "combined_first_event_per_firm"
METHOD_VARIANT = "liu_product_tfidf_same_industry_d_top10"
METHOD_LABEL = "Product-word TF-IDF same-industry Top10"
SPEC_RAW = "legacy_detail_density_raw"
MAIN_OUTCOME = "peer_car_0_p1_mm"
PRE_CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]


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


def markdown_table(df: pd.DataFrame) -> str:
    rows = ["| " + " | ".join(df.columns) + " |", "|" + "|".join("---" for _ in df.columns) + "|"]
    for _, row in df.iterrows():
        rows.append("| " + " | ".join("" if pd.isna(row[c]) else str(row[c]) for c in df.columns) + " |")
    return "\n".join(rows)


def load_event_panel() -> pd.DataFrame:
    panel = pd.read_csv(
        PANEL_PATH,
        dtype={"event_id": str, "event_key": str, "focal_code": str, "peer_code": str},
        low_memory=False,
    )
    out = panel[
        panel["sample_name"].eq(SAMPLE_NAME)
        & panel["method_variant"].eq(METHOD_VARIANT)
        & panel["time_valid_prior_year"].eq(1)
        & panel["complete_clean_m1_p1"].eq(1)
    ].copy()
    numeric_cols = [
        "peer_ar_m1_mm",
        "peer_ar0_mm",
        "peer_ar_p1_mm",
        "peer_car_0_p1_mm",
        "peer_car_m1_p1_mm",
        *PRE_CONTROLS,
        "peer_rank",
        "peer_similarity",
        "ext_any",
        "current_text_history",
    ]
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def attach_specificity(panel: pd.DataFrame) -> pd.DataFrame:
    specs = pd.read_csv(SPEC_PATH, dtype={"event_id": str, "event_key": str, "focal_code": str}, low_memory=False)
    specs = specs[specs["sample_name"].eq(SAMPLE_NAME)].copy()
    specs["spec_z"] = v25.zscore(v25.winsorize(specs[SPEC_RAW]))
    keep = [
        "event_key",
        "legacy_detail_density_raw",
        "spec_z",
        "specificity_source",
        "qian_recall_score",
    ]
    specs = specs[keep].drop_duplicates("event_key")
    out = panel.merge(specs, on="event_key", how="left")
    for col in ["legacy_detail_density_raw", "spec_z", "qian_recall_score"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["ai"] = out["ext_any"].fillna(0.0).astype(float)
    out["text_history"] = out["current_text_history"].fillna(0.0).astype(float)
    out["spec_ai"] = out["spec_z"] * out["ai"]
    out["spec_text_history"] = out["spec_z"] * out["text_history"]
    out["snippet_fallback"] = out["specificity_source"].eq("v36_snippet").astype(int)
    return out


def desc_table(d: pd.DataFrame) -> pd.DataFrame:
    variables = [
        ("PeerAR[-1]", "peer_ar_m1_mm"),
        ("PeerAR[0]", "peer_ar0_mm"),
        ("PeerAR[+1]", "peer_ar_p1_mm"),
        ("PeerCAR[0,+1]", "peer_car_0_p1_mm"),
        ("PeerCAR[-1,+1]", "peer_car_m1_p1_mm"),
        ("DetailDensity", "legacy_detail_density_raw"),
        ("Spec", "spec_z"),
        ("AIActive", "ai"),
        ("Spec x AIActive", "spec_ai"),
        ("PeerCAR[-10,-2]", "peer_car_pre10_m2_mm"),
        ("PeerCAR[-20,-2]", "peer_car_pre20_m2_mm"),
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
    out = pd.DataFrame(rows)
    for col in ["均值", "标准差", "最小值", "中位数", "最大值"]:
        out[col] = out[col].map(lambda x: fmt_num(x, 4))
    return out


def event_study_table(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for outcome, label in pe.OUTCOMES:
        rows.append({"outcome": outcome, "窗口": label, **pe.clustered_mean(panel, outcome)})
    raw = pd.DataFrame(rows)
    formatted = pd.DataFrame(
        {
            "窗口": raw["窗口"],
            "均值": [f"{fmt_num(r.estimate)}{stars(r.p)}" for r in raw.itertuples(index=False)],
            "标准误": raw["se"].map(lambda x: f"({fmt_num(x)})"),
            "p值": raw["p"].map(lambda x: fmt_num(x, 4)),
            "中位数": raw["median"].map(lambda x: fmt_num(x, 4)),
            "正收益比例": raw["positive_share"].map(lambda x: fmt_num(x, 4)),
            "观测值": raw["nobs"].astype(int),
            "事件数": raw["events"].astype(int),
            "同行公司数": raw["peer_firms"].astype(int),
        }
    )
    return formatted, raw


def mechanism_sample(d: pd.DataFrame) -> pd.DataFrame:
    return d.dropna(
        subset=[
            MAIN_OUTCOME,
            *PRE_CONTROLS,
            "spec_z",
            "ai",
            "spec_ai",
            "peer_industry_week",
            "event_key",
            "peer_code",
        ]
    ).copy()


def fit_absorbed_ols(data: pd.DataFrame, outcome: str, xvars: list[str], fe_cols: list[str]) -> dict[str, object] | None:
    need = [outcome, *xvars, *fe_cols, "event_key", "peer_code", "focal_code"]
    d = data.dropna(subset=list(dict.fromkeys(need))).copy()
    if len(d) < 80 or d["event_key"].nunique() < 8 or d["peer_code"].nunique() < 20:
        return None
    dm = v25.absorb_frame(d, [outcome, *xvars], fe_cols)
    y = dm[outcome].to_numpy(dtype=float)
    x = dm[xvars].to_numpy(dtype=float)
    keep = np.nanstd(x, axis=0) > 1e-12
    if not keep.all():
        xvars = [var for var, ok in zip(xvars, keep) if ok]
        x = x[:, keep]
        if x.shape[1] == 0:
            return None
    xtx = x.T @ x
    bread = np.linalg.pinv(xtx)
    beta = bread @ (x.T @ y)
    resid = y - x @ beta

    meat_event = v25.cluster_meat(x, resid, d["event_key"])
    meat_peer = v25.cluster_meat(x, resid, d["peer_code"])
    pair_group = d["event_key"].astype(str) + "|" + d["peer_code"].astype(str)
    meat_pair = v25.cluster_meat(x, resid, pair_group)
    cov = bread @ (meat_event + meat_peer - meat_pair) @ bread

    within_tss = float(np.sum((y - y.mean()) ** 2))
    rss = float(np.sum(resid**2))
    raw_y = d[outcome].to_numpy(dtype=float)
    overall_tss = float(np.sum((raw_y - raw_y.mean()) ** 2))
    out: dict[str, object] = {
        "nobs": int(len(d)),
        "events": int(d["event_key"].nunique()),
        "focal_firms": int(d["focal_code"].nunique()),
        "peer_firms": int(d["peer_code"].nunique()),
        "within_r2": 1.0 - rss / within_tss if within_tss > 0 else math.nan,
        "overall_r2": 1.0 - rss / overall_tss if overall_tss > 0 else math.nan,
        "fe_cols": ",".join(fe_cols),
    }
    for i, var in enumerate(xvars):
        var_se = math.sqrt(float(cov[i, i])) if float(cov[i, i]) >= 0 else math.nan
        coef = float(beta[i])
        z_value = coef / var_se if var_se and var_se > 0 else math.nan
        out[f"{var}_coef"] = coef
        out[f"{var}_se"] = var_se
        out[f"{var}_z"] = z_value
        out[f"{var}_p"] = v25.p_from_z(z_value)
    return out


def run_mechanism_models(d: pd.DataFrame) -> list[dict[str, object]]:
    specs = [
        {
            "col": "(1)",
            "dep": "PeerCAR[0,+1]",
            "title": "事件固定效应",
            "data": d,
            "outcome": MAIN_OUTCOME,
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
            "outcome": MAIN_OUTCOME,
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
            "outcome": MAIN_OUTCOME,
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
            "outcome": MAIN_OUTCOME,
            "xvars": ["ai_alt", "spec_ai_alt", *PRE_CONTROLS],
            "fe": ["event_key"],
            "interaction": "spec_ai_alt",
            "ai_var": "ai_alt",
        },
    ]
    rows = []
    for spec in specs:
        res = fit_absorbed_ols(spec["data"], spec["outcome"], spec["xvars"], spec["fe"])
        row = {k: v for k, v in spec.items() if k != "data"}
        if res:
            row.update(res)
        rows.append(row)
    return rows


def mechanism_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    cols = [r["col"] for r in rows]
    table_rows: list[dict[str, str]] = []
    table_rows.append({"变量": "", **{r["col"]: r["dep"] for r in rows}})
    table_rows.append({"变量": "", **{r["col"]: r["title"] for r in rows}})
    table_rows.append({"变量": "Spec", **{r["col"]: "-" for r in rows}})
    table_rows.append(
        {
            "变量": "Spec x AIActive",
            **{r["col"]: fmt_coef(r, str(r["interaction"])) for r in rows},
        }
    )
    table_rows.append(
        {
            "变量": "",
            **{r["col"]: fmt_se(r, str(r["interaction"])) for r in rows},
        }
    )
    table_rows.append(
        {
            "变量": "AIActive / TextHistory",
            **{r["col"]: fmt_coef(r, str(r["ai_var"])) for r in rows},
        }
    )
    table_rows.append(
        {
            "变量": "",
            **{r["col"]: fmt_se(r, str(r["ai_var"])) for r in rows},
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
            {"变量": "Peer Firm FE", **{r["col"]: "YES" if "peer_code" in r["fe"] else "NO" for r in rows}},
            {"变量": "N", **{r["col"]: str(r.get("nobs", "")) for r in rows}},
            {"变量": "Events", **{r["col"]: str(r.get("events", "")) for r in rows}},
            {"变量": "Peer firms", **{r["col"]: str(r.get("peer_firms", "")) for r in rows}},
            {"变量": "Overall R2", **{r["col"]: fmt_num(r.get("overall_r2"), 3) for r in rows}},
            {"变量": "Within R2", **{r["col"]: fmt_num(r.get("within_r2"), 3) for r in rows}},
        ]
    )
    return pd.DataFrame(table_rows, columns=["变量", *cols])


def save_outputs(
    desc: pd.DataFrame,
    event_study: pd.DataFrame,
    event_study_raw: pd.DataFrame,
    mech_table: pd.DataFrame,
    mech_rows: list[dict[str, object]],
    event_panel: pd.DataFrame,
    mech_panel: pd.DataFrame,
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    raw_mech = pd.DataFrame(mech_rows).drop(columns=["xvars", "fe"], errors="ignore")
    meta = pd.DataFrame(
        [
            {
                "sample_name": SAMPLE_NAME,
                "method_variant": METHOD_VARIANT,
                "method_label": METHOD_LABEL,
                "event_study_rows": int(len(event_panel)),
                "event_study_events": int(event_panel["event_key"].nunique()),
                "event_study_peer_firms": int(event_panel["peer_code"].nunique()),
                "mechanism_rows": int(len(mech_panel)),
                "mechanism_events": int(mech_panel["event_key"].nunique()),
                "mechanism_peer_firms": int(mech_panel["peer_code"].nunique()),
                "snippet_fallback_rows": int(mech_panel["snippet_fallback"].sum()),
                "snippet_fallback_events": int(mech_panel.loc[mech_panel["snippet_fallback"].eq(1), "event_key"].nunique()),
            }
        ]
    )

    desc.to_csv(OUT_DIR / "table1_descriptive_statistics.csv", index=False)
    event_study.to_csv(OUT_DIR / "table2_peer_event_study_main_effect.csv", index=False)
    event_study_raw.to_csv(OUT_DIR / "table2_peer_event_study_main_effect_raw.csv", index=False)
    mech_table.to_csv(OUT_DIR / "table3_specificity_mechanism_regressions.csv", index=False)
    raw_mech.to_csv(OUT_DIR / "table3_specificity_mechanism_regressions_raw.csv", index=False)
    meta.to_csv(OUT_DIR / "sample_metadata.csv", index=False)

    xlsx_path = OUT_DIR / f"{RUN_ID}.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        for sheet, df in [
            ("Table1_Desc", desc),
            ("Table2_EventStudy", event_study),
            ("Table2_Raw", event_study_raw),
            ("Table3_Specificity", mech_table),
            ("Table3_Raw", raw_mech),
            ("Metadata", meta),
        ]:
            df.to_excel(writer, sheet_name=sheet, index=False)
            ws = writer.book[sheet]
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 10), 45)

    lines = [
        "# v28 v36 peer main-effect tables",
        "",
        "## Scope",
        "",
        f"- Sample: `{SAMPLE_NAME}`.",
        f"- Peer construction: `{METHOD_VARIANT}` ({METHOD_LABEL}).",
        "- Table 2 treats the average peer abnormal return around focal-firm GenAI disclosures as the main effect.",
        "- Table 3 treats disclosure specificity as mechanism-like heterogeneity, not a formal mediation test.",
        "- Standard errors are clustered by event and peer firm.",
        "",
        "## Sample Metadata",
        "",
        markdown_table(meta),
        "",
        "## Table 1 Descriptive Statistics",
        "",
        markdown_table(desc),
        "",
        "## Table 2 Peer-Firm Event Study Main Effect",
        "",
        markdown_table(event_study),
        "",
        "## Table 3 Disclosure Specificity Mechanism/Heterogeneity",
        "",
        markdown_table(mech_table),
        "",
        "## Notes",
        "",
        "- `Spec` is the winsorized and standardized `DetailDensity` measure.",
        "- `Spec` itself is absorbed by event fixed effects in Table 3 because specificity is event-level.",
        "- `Overall R2` includes the explanatory power of fixed effects; `Within R2` is the incremental explanatory power after absorbing fixed effects.",
        "- The main interpretation is: GenAI disclosures reduce product-market peer valuations on average; more specific disclosures further reduce returns of AI-active product-market peers.",
        "- `***`, `**`, and `*` indicate significance at 1%, 5%, and 10%.",
        "",
        "## Output Files",
        "",
        f"- `{OUT_DIR.relative_to(ROOT)}/table1_descriptive_statistics.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/table2_peer_event_study_main_effect.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/table2_peer_event_study_main_effect_raw.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/table3_specificity_mechanism_regressions.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/table3_specificity_mechanism_regressions_raw.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/sample_metadata.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/{RUN_ID}.xlsx`",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    event_panel = load_event_panel()
    with_spec = attach_specificity(event_panel)
    mech_panel = mechanism_sample(with_spec)

    desc = desc_table(with_spec)
    table2, table2_raw = event_study_table(event_panel)
    mech_rows = run_mechanism_models(mech_panel)
    table3 = mechanism_table(mech_rows)

    save_outputs(desc, table2, table2_raw, table3, mech_rows, event_panel, mech_panel)
    print(
        f"event study rows={len(event_panel):,}, events={event_panel['event_key'].nunique():,}, "
        f"peers={event_panel['peer_code'].nunique():,}",
        flush=True,
    )
    print(
        f"mechanism rows={len(mech_panel):,}, events={mech_panel['event_key'].nunique():,}, "
        f"peers={mech_panel['peer_code'].nunique():,}",
        flush=True,
    )
    print(table2.to_string(index=False), flush=True)
    print(table3.to_string(index=False), flush=True)
    print(f"wrote {OUT_DIR}", flush=True)
    print(f"wrote {DOC_PATH}", flush=True)


if __name__ == "__main__":
    main()
