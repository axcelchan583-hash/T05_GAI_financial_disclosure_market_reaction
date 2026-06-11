#!/usr/bin/env python3
"""POM-analog cross-sectional regressions for the peer-reaction setting."""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v25_empirical_table_pack_20260604 as v25  # noqa: E402
import run_v28_v36_peer_main_effect_tables_20260605 as v28  # noqa: E402


RUN_ID = "v31_pom_analog_cross_section_20260605"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "95_v31_pom_analog_cross_section_20260605.md"

V29_SAMPLE = ROOT / "results" / "v29_pom_style_peer_results_20260605" / "analysis_sample_used_in_table3.csv"
SPEC_PATH = ROOT / "results" / "v26_v36_x_peer_retest_20260604" / "v36_specificity_measures.csv"
FIN_PATH = ROOT / "results" / "v13_peer_validity_gate_20260531" / "financials_fs_comins_annual_metrics.csv.gz"
EXT_AI_PATH = ROOT / "results" / "v6_external_ai_active_20260524" / "external_ai_evidence_first_dates_by_firm.csv"
NETWORK_PATH = ROOT / "results" / "v22_chinese_literature_product_peers_20260601" / "liu_product_tfidf_same_industry_d_peer_network_top20.csv"

PRE_CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]

VAR_LABELS = {
    "peer_prior_ai_patent": "Prior AI patent evidence",
    "peer_sales_growth_z": "Peer sales growth",
    "product_distance_z": "Product-market distance",
    "peer_industry_hhi_z": "Peer industry concentration",
    "product_oriented": "Product-oriented announcement",
    "qian_recall_z": "Qian initiative score",
    "spec_z": "Disclosure specificity",
    "ai": "AIActivePeer",
    "spec_ai": "Specificity x AIActivePeer",
    "product_oriented_x_ai": "Product-oriented x AIActivePeer",
    "qian_recall_x_ai": "Qian score x AIActivePeer",
    "peer_log_revenue_z": "Peer size",
    "peer_gross_margin_z": "Peer gross margin",
    "peer_car_pre10_m2_mm": "PeerCAR[-10,-2]",
    "peer_car_pre20_m2_mm": "PeerCAR[-20,-2]",
}


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = re.sub(r"\.0$", "", str(value).strip())
    digits = re.sub(r"\D", "", text)
    return digits.zfill(6)[-6:] if digits else ""


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


def z_col(df: pd.DataFrame, col: str, out_col: str | None = None) -> pd.Series:
    return v25.zscore(v25.winsorize(pd.to_numeric(df[col], errors="coerce"))).rename(out_col or f"{col}_z")


def load_base_sample() -> pd.DataFrame:
    d = pd.read_csv(
        V29_SAMPLE,
        dtype={"event_id": str, "event_key": str, "focal_code": str, "peer_code": str},
        low_memory=False,
    )
    for col in ["event_date", "date_0"]:
        d[col] = pd.to_datetime(d[col], errors="coerce")
    for col in [
        "peer_ar0_mm",
        "peer_car_0_p1_mm",
        "peer_similarity",
        "peer_rank",
        "spec_z",
        "ai",
        "spec_ai",
        *PRE_CONTROLS,
    ]:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    d["focal_code"] = d["focal_code"].map(code6)
    d["peer_code"] = d["peer_code"].map(code6)
    d["event_year"] = d["date_0"].dt.year.astype("Int64").astype(str)
    d["fiscal_year_pre"] = (d["date_0"].dt.year - 1).astype("Int64")
    d["snapshot_report_year_int"] = pd.to_numeric(d["snapshot_report_year"], errors="coerce").astype("Int64")
    d["product_distance"] = 1.0 - d["peer_similarity"]
    d["product_distance_z"] = z_col(d, "product_distance", "product_distance_z")
    return d


def load_event_features() -> pd.DataFrame:
    s = pd.read_csv(SPEC_PATH, dtype={"event_id": str, "event_key": str, "focal_code": str}, low_memory=False)
    s = s[s["sample_name"].eq(v28.SAMPLE_NAME)].copy()
    keep = [
        "event_key",
        "announcement_title",
        "auto_pdf_label",
        "candidate_row_type",
        "qian_recall_score",
        "llm_reason",
        "llm_evidence",
        "machine_component_sum",
        "auto_action_score",
        "specificity_source",
    ]
    s = s[keep].drop_duplicates("event_key")
    for col in ["qian_recall_score", "machine_component_sum", "auto_action_score"]:
        s[col] = pd.to_numeric(s[col], errors="coerce")
    text = (
        s["announcement_title"].fillna("")
        + " "
        + s["llm_reason"].fillna("")
        + " "
        + s["llm_evidence"].fillna("")
    )
    product_pat = r"产品|服务|平台|系统|软件|应用|客户|用户|商业化|销售|订单|合同|解决方案|模型|机器人|功能|上线|发布|推出|合作"
    process_pat = r"内部|办公|管理|流程|降本|增效|生产效率|经营效率|内部管理|数字化转型|运营"
    s["product_hit"] = text.str.contains(product_pat, regex=True).astype(int)
    s["process_hit"] = text.str.contains(process_pat, regex=True).astype(int)
    s["product_oriented"] = (s["product_hit"].eq(1) & s["process_hit"].eq(0) | text.str.contains(r"产品|服务|平台|应用|客户|商业化|订单|上线|发布|推出", regex=True)).astype(int)
    s["direct_event_candidate"] = s["candidate_row_type"].fillna("").str.contains("direct", case=False).astype(int)
    s["qian_recall_z"] = z_col(s, "qian_recall_score", "qian_recall_z")
    s["auto_action_z"] = z_col(s, "auto_action_score", "auto_action_z")
    return s


def load_industry_map() -> pd.DataFrame:
    net = pd.read_csv(NETWORK_PATH, dtype=str, encoding="utf-8-sig", low_memory=False)
    net["snapshot_report_year"] = pd.to_numeric(net["snapshot_report_year"], errors="coerce").astype("Int64")
    focal = net[["focal_code", "snapshot_report_year", "focal_industry_d"]].rename(
        columns={"focal_code": "stock_code", "focal_industry_d": "industry_d"}
    )
    peer = net[["peer_code", "snapshot_report_year", "peer_industry_d"]].rename(
        columns={"peer_code": "stock_code", "peer_industry_d": "industry_d"}
    )
    out = pd.concat([focal, peer], ignore_index=True)
    out["stock_code"] = out["stock_code"].map(code6)
    out = out.dropna(subset=["stock_code", "snapshot_report_year", "industry_d"])
    out = (
        out.groupby(["stock_code", "snapshot_report_year"])["industry_d"]
        .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0])
        .reset_index()
        .rename(columns={"snapshot_report_year": "fiscal_year"})
    )
    return out


def load_financials_with_hhi() -> pd.DataFrame:
    fin = pd.read_csv(FIN_PATH, dtype={"stock_code": str}, low_memory=False)
    fin["stock_code"] = fin["stock_code"].map(code6)
    fin["fiscal_year"] = pd.to_numeric(fin["fiscal_year"], errors="coerce").astype("Int64")
    for col in ["revenue", "sales_growth", "gross_margin"]:
        fin[col] = pd.to_numeric(fin[col], errors="coerce")
    ind = load_industry_map()
    fin = fin.merge(ind, on=["stock_code", "fiscal_year"], how="left")
    hhi_base = fin.dropna(subset=["industry_d", "revenue"]).copy()
    hhi_base = hhi_base[hhi_base["revenue"].gt(0)].copy()
    hhi_base["industry_revenue"] = hhi_base.groupby(["industry_d", "fiscal_year"])["revenue"].transform("sum")
    hhi_base["revenue_share"] = hhi_base["revenue"] / hhi_base["industry_revenue"]
    hhi = (
        hhi_base.groupby(["industry_d", "fiscal_year"])
        .agg(peer_industry_hhi=("revenue_share", lambda x: float(np.sum(np.square(x)))), industry_firm_count=("stock_code", "nunique"))
        .reset_index()
    )
    fin = fin.merge(hhi, on=["industry_d", "fiscal_year"], how="left")
    fin["peer_log_revenue"] = np.log1p(fin["revenue"].clip(lower=0))
    return fin[
        [
            "stock_code",
            "fiscal_year",
            "revenue",
            "sales_growth",
            "gross_margin",
            "peer_log_revenue",
            "industry_d",
            "peer_industry_hhi",
            "industry_firm_count",
        ]
    ]


def attach_financials(d: pd.DataFrame) -> pd.DataFrame:
    fin = load_financials_with_hhi()
    prev = fin.rename(columns={c: f"{c}_pre" for c in fin.columns if c not in ["stock_code", "fiscal_year"]})
    out = d.merge(
        prev,
        left_on=["peer_code", "fiscal_year_pre"],
        right_on=["stock_code", "fiscal_year"],
        how="left",
    ).drop(columns=["stock_code", "fiscal_year"], errors="ignore")
    snap = fin.rename(columns={c: f"{c}_snap" for c in fin.columns if c not in ["stock_code", "fiscal_year"]})
    out = out.merge(
        snap,
        left_on=["peer_code", "snapshot_report_year_int"],
        right_on=["stock_code", "fiscal_year"],
        how="left",
    ).drop(columns=["stock_code", "fiscal_year"], errors="ignore")
    for base in [
        "revenue",
        "sales_growth",
        "gross_margin",
        "peer_log_revenue",
        "industry_d",
        "peer_industry_hhi",
        "industry_firm_count",
    ]:
        if base.startswith("peer_"):
            target = base
        elif base == "industry_d":
            target = "peer_industry_d_fin"
        elif base == "industry_firm_count":
            target = "peer_industry_firm_count"
        else:
            target = f"peer_{base}"
        out[target] = out[f"{base}_pre"].combine_first(out[f"{base}_snap"])
    out["peer_financial_source"] = np.select(
        [out["sales_growth_pre"].notna(), out["sales_growth_snap"].notna()],
        ["event_year_minus_1", "snapshot_report_year"],
        default="missing",
    )
    for col in ["peer_sales_growth", "peer_gross_margin", "peer_log_revenue", "peer_industry_hhi"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["peer_sales_growth_z"] = z_col(out, "peer_sales_growth", "peer_sales_growth_z")
    out["peer_gross_margin_z"] = z_col(out, "peer_gross_margin", "peer_gross_margin_z")
    out["peer_log_revenue_z"] = z_col(out, "peer_log_revenue", "peer_log_revenue_z")
    out["peer_industry_hhi_z"] = z_col(out, "peer_industry_hhi", "peer_industry_hhi_z")
    return out


def attach_ai_innovation(d: pd.DataFrame) -> pd.DataFrame:
    ai = pd.read_csv(EXT_AI_PATH, dtype={"stock_code": str}, low_memory=False)
    ai["stock_code"] = ai["stock_code"].map(code6)
    for col in [
        "cac_first_date",
        "ai_patent_grant_first_date",
        "genai_patent_grant_first_date",
        "ai_patent_application_first_date",
        "genai_patent_application_first_date",
    ]:
        ai[col] = pd.to_datetime(ai[col], errors="coerce")
    for col in ["ai_patent_title_count_total", "genai_patent_title_count_total"]:
        ai[col] = pd.to_numeric(ai[col], errors="coerce")
    out = d.merge(ai, left_on="peer_code", right_on="stock_code", how="left").drop(columns=["stock_code"], errors="ignore")
    cutoff = out["date_0"] - pd.Timedelta(days=5)
    out["peer_prior_ai_patent"] = out["ai_patent_grant_first_date"].notna() & out["ai_patent_grant_first_date"].le(cutoff)
    out["peer_prior_genai_patent"] = out["genai_patent_grant_first_date"].notna() & out["genai_patent_grant_first_date"].le(cutoff)
    out["peer_prior_cac"] = out["cac_first_date"].notna() & out["cac_first_date"].le(cutoff)
    for col in ["peer_prior_ai_patent", "peer_prior_genai_patent", "peer_prior_cac"]:
        out[col] = out[col].astype(int)
    out["peer_ai_patent_log_count_total"] = np.log1p(out["ai_patent_title_count_total"].fillna(0).clip(lower=0))
    out["peer_ai_patent_log_count_z"] = z_col(out, "peer_ai_patent_log_count_total", "peer_ai_patent_log_count_z")
    return out


def build_analysis_panel() -> pd.DataFrame:
    d = load_base_sample()
    d = d.merge(load_event_features(), on="event_key", how="left", suffixes=("", "_event"))
    d = attach_financials(d)
    d = attach_ai_innovation(d)
    d["product_oriented_x_ai"] = d["product_oriented"] * d["ai"]
    d["qian_recall_x_ai"] = d["qian_recall_z"] * d["ai"]
    d["focal_industry_year"] = d["focal_industry_d"].fillna("UNKNOWN").astype(str) + "|" + d["event_year"].astype(str)
    return d


def run_models(d: pd.DataFrame) -> list[dict[str, object]]:
    specs = [
        {
            "col": "(1)",
            "dep": "PeerAR[0]",
            "title": "POM peer controls, Event FE",
            "outcome": "peer_ar0_mm",
            "xvars": [
                "peer_prior_ai_patent",
                "peer_sales_growth_z",
                "product_distance_z",
                "peer_industry_hhi_z",
                "peer_log_revenue_z",
                "peer_gross_margin_z",
                *PRE_CONTROLS,
            ],
            "fe": ["event_key"],
        },
        {
            "col": "(2)",
            "dep": "PeerCAR[0,+1]",
            "title": "POM peer controls, Event FE",
            "outcome": "peer_car_0_p1_mm",
            "xvars": [
                "peer_prior_ai_patent",
                "peer_sales_growth_z",
                "product_distance_z",
                "peer_industry_hhi_z",
                "peer_log_revenue_z",
                "peer_gross_margin_z",
                *PRE_CONTROLS,
            ],
            "fe": ["event_key"],
        },
        {
            "col": "(3)",
            "dep": "PeerAR[0]",
            "title": "Announcement features, Year + industry FE",
            "outcome": "peer_ar0_mm",
            "xvars": [
                "spec_z",
                "product_oriented",
                "qian_recall_z",
                "peer_prior_ai_patent",
                "peer_sales_growth_z",
                "product_distance_z",
                "peer_industry_hhi_z",
                "peer_log_revenue_z",
                *PRE_CONTROLS,
            ],
            "fe": ["event_year", "focal_industry_d"],
        },
        {
            "col": "(4)",
            "dep": "PeerCAR[0,+1]",
            "title": "Announcement features, Year + industry FE",
            "outcome": "peer_car_0_p1_mm",
            "xvars": [
                "spec_z",
                "product_oriented",
                "qian_recall_z",
                "peer_prior_ai_patent",
                "peer_sales_growth_z",
                "product_distance_z",
                "peer_industry_hhi_z",
                "peer_log_revenue_z",
                *PRE_CONTROLS,
            ],
            "fe": ["event_year", "focal_industry_d"],
        },
        {
            "col": "(5)",
            "dep": "PeerAR[0]",
            "title": "Specificity mechanism, Event FE",
            "outcome": "peer_ar0_mm",
            "xvars": [
                "ai",
                "spec_ai",
                "peer_prior_ai_patent",
                "peer_sales_growth_z",
                "product_distance_z",
                "peer_industry_hhi_z",
                "peer_log_revenue_z",
                *PRE_CONTROLS,
            ],
            "fe": ["event_key"],
        },
        {
            "col": "(6)",
            "dep": "PeerCAR[0,+1]",
            "title": "Specificity mechanism, Event FE",
            "outcome": "peer_car_0_p1_mm",
            "xvars": [
                "ai",
                "spec_ai",
                "peer_prior_ai_patent",
                "peer_sales_growth_z",
                "product_distance_z",
                "peer_industry_hhi_z",
                "peer_log_revenue_z",
                *PRE_CONTROLS,
            ],
            "fe": ["event_key"],
        },
        {
            "col": "(7)",
            "dep": "PeerAR[0]",
            "title": "Announcement category x AIActive, Event FE",
            "outcome": "peer_ar0_mm",
            "xvars": [
                "ai",
                "product_oriented_x_ai",
                "qian_recall_x_ai",
                "peer_prior_ai_patent",
                "peer_sales_growth_z",
                "product_distance_z",
                "peer_industry_hhi_z",
                "peer_log_revenue_z",
                *PRE_CONTROLS,
            ],
            "fe": ["event_key"],
        },
        {
            "col": "(8)",
            "dep": "PeerCAR[0,+1]",
            "title": "Announcement category x AIActive, Event FE",
            "outcome": "peer_car_0_p1_mm",
            "xvars": [
                "ai",
                "product_oriented_x_ai",
                "qian_recall_x_ai",
                "peer_prior_ai_patent",
                "peer_sales_growth_z",
                "product_distance_z",
                "peer_industry_hhi_z",
                "peer_log_revenue_z",
                *PRE_CONTROLS,
            ],
            "fe": ["event_key"],
        },
    ]
    rows: list[dict[str, object]] = []
    for spec in specs:
        res = v28.fit_absorbed_ols(d, spec["outcome"], spec["xvars"], spec["fe"])
        row = {k: v for k, v in spec.items() if k not in ["xvars", "fe"]}
        row["xvars"] = "|".join(spec["xvars"])
        row["fe"] = "|".join(spec["fe"])
        if res:
            row.update(res)
        rows.append(row)
    return rows


def formatted_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    table_rows: list[dict[str, str]] = []
    cols = [r["col"] for r in rows]
    table_rows.append({"Variables": "", **{r["col"]: r["dep"] for r in rows}})
    table_rows.append({"Variables": "", **{r["col"]: r["title"] for r in rows}})
    for var in [
        "peer_prior_ai_patent",
        "peer_sales_growth_z",
        "product_distance_z",
        "peer_industry_hhi_z",
        "product_oriented",
        "qian_recall_z",
        "spec_z",
        "ai",
        "spec_ai",
        "product_oriented_x_ai",
        "qian_recall_x_ai",
        "peer_log_revenue_z",
        "peer_gross_margin_z",
        "peer_car_pre10_m2_mm",
        "peer_car_pre20_m2_mm",
    ]:
        table_rows.append({"Variables": VAR_LABELS[var], **{r["col"]: fmt_coef(r, var) for r in rows}})
        table_rows.append({"Variables": "", **{r["col"]: fmt_se(r, var) for r in rows}})
    table_rows.extend(
        [
            {"Variables": "Event FE", **{r["col"]: "YES" if "event_key" in str(r.get("fe", "")) else "NO" for r in rows}},
            {"Variables": "Year FE", **{r["col"]: "YES" if "event_year" in str(r.get("fe", "")) else "NO" for r in rows}},
            {
                "Variables": "Focal industry FE",
                **{r["col"]: "YES" if "focal_industry_d" in str(r.get("fe", "")) else "NO" for r in rows},
            },
            {"Variables": "Observations", **{r["col"]: str(r.get("nobs", "")) for r in rows}},
            {"Variables": "Events", **{r["col"]: str(r.get("events", "")) for r in rows}},
            {"Variables": "Peer firms", **{r["col"]: str(r.get("peer_firms", "")) for r in rows}},
            {"Variables": "Overall R2", **{r["col"]: fmt_num(r.get("overall_r2"), 3) for r in rows}},
            {"Variables": "Within R2", **{r["col"]: fmt_num(r.get("within_r2"), 3) for r in rows}},
        ]
    )
    return pd.DataFrame(table_rows, columns=["Variables", *cols])


def sample_coverage(d: pd.DataFrame) -> pd.DataFrame:
    variables = [
        "peer_prior_ai_patent",
        "peer_sales_growth",
        "peer_gross_margin",
        "peer_log_revenue",
        "peer_industry_hhi",
        "product_distance",
        "product_oriented",
        "qian_recall_score",
        "spec_z",
        "ai",
    ]
    rows = []
    for var in variables:
        x = d[var]
        rows.append(
            {
                "variable": var,
                "nonmissing_rows": int(x.notna().sum()),
                "nonmissing_events": int(d.loc[x.notna(), "event_key"].nunique()),
                "mean": float(pd.to_numeric(x, errors="coerce").mean()) if pd.to_numeric(x, errors="coerce").notna().any() else math.nan,
            }
        )
    rows.append(
        {
            "variable": "peer_financial_source:event_year_minus_1",
            "nonmissing_rows": int(d["peer_financial_source"].eq("event_year_minus_1").sum()),
            "nonmissing_events": int(d.loc[d["peer_financial_source"].eq("event_year_minus_1"), "event_key"].nunique()),
            "mean": math.nan,
        }
    )
    rows.append(
        {
            "variable": "peer_financial_source:snapshot_report_year",
            "nonmissing_rows": int(d["peer_financial_source"].eq("snapshot_report_year").sum()),
            "nonmissing_events": int(d.loc[d["peer_financial_source"].eq("snapshot_report_year"), "event_key"].nunique()),
            "mean": math.nan,
        }
    )
    return pd.DataFrame(rows)


def mapping_table() -> pd.DataFrame:
    rows = [
        {
            "POM variable": "Supplier R&D Intensity",
            "Peer-setting analog": "Prior AI patent evidence",
            "variable": "peer_prior_ai_patent",
            "note": "True R&D intensity is not in the current repo data; this is a pre-event innovation-evidence proxy, not a one-for-one R&D measure.",
        },
        {
            "POM variable": "Supplier Sales Growth",
            "Peer-setting analog": "Peer sales growth",
            "variable": "peer_sales_growth_z",
            "note": "Uses prior fiscal-year revenue growth from the available CSMAR-derived annual income metrics.",
        },
        {
            "POM variable": "Supplier-Customer Distance",
            "Peer-setting analog": "Product-market distance",
            "variable": "product_distance_z",
            "note": "Defined as 1 minus product-text similarity; larger values indicate weaker product-market proximity.",
        },
        {
            "POM variable": "Supplier Industry Concentration",
            "Peer-setting analog": "Peer industry concentration",
            "variable": "peer_industry_hhi_z",
            "note": "HHI computed from listed-firm revenue by industry-year where industry mapping is available.",
        },
        {
            "POM variable": "Product-Oriented Announcement",
            "Peer-setting analog": "Product-oriented GenAI announcement",
            "variable": "product_oriented",
            "note": "Rule-coded from announcement title and LLM evidence; should be manually audited before final paper use.",
        },
        {
            "POM variable": "Announcement intensity/category",
            "Peer-setting analog": "Qian initiative score / disclosure specificity",
            "variable": "qian_recall_z / spec_z",
            "note": "Specificity has already been used in v29; event fixed effects absorb its main effect, so the preferred mechanism uses Spec x AIActivePeer.",
        },
    ]
    return pd.DataFrame(rows)


def save_outputs(d: pd.DataFrame, rows: list[dict[str, object]], table: pd.DataFrame) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    raw = pd.DataFrame(rows)
    coverage = sample_coverage(d)
    mapping = mapping_table()
    d.to_csv(OUT_DIR / "analysis_panel_pom_analog.csv.gz", index=False, compression="gzip")
    raw.to_csv(OUT_DIR / "pom_analog_cross_section_regressions_raw.csv", index=False)
    table.to_csv(OUT_DIR / "pom_analog_cross_section_regressions.csv", index=False)
    coverage.to_csv(OUT_DIR / "pom_analog_variable_coverage.csv", index=False)
    mapping.to_csv(OUT_DIR / "pom_variable_mapping.csv", index=False)
    with pd.ExcelWriter(OUT_DIR / f"{RUN_ID}.xlsx", engine="openpyxl") as writer:
        for sheet, frame in [
            ("Mapping", mapping),
            ("Coverage", coverage),
            ("Regressions", table),
            ("Regressions_Raw", raw),
        ]:
            frame.to_excel(writer, sheet_name=sheet, index=False)
            ws = writer.book[sheet]
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 10), 55)

    key = raw[raw["col"].isin(["(5)", "(6)"])][["col", "dep", "spec_ai_coef", "spec_ai_se", "spec_ai_p", "nobs", "events"]]
    lines = [
        "# v31 POM-analog cross-sectional regressions",
        "",
        "## Scope",
        "",
        "- Purpose: test POM-style cross-sectional factors in the product-market peer setting.",
        "- Input sample: v29 Table 3 analysis sample.",
        "- Important distinction: event-level variables such as disclosure specificity and announcement category are absorbed by event fixed effects. Columns without event fixed effects are exploratory POM-style analogs, not the preferred identification specification.",
        "",
        "## POM Variable Mapping",
        "",
        markdown_table(mapping),
        "",
        "## Variable Coverage",
        "",
        markdown_table(coverage.assign(mean=coverage["mean"].map(lambda x: "" if pd.isna(x) else fmt_num(x, 4)))),
        "",
        "## Regression Table",
        "",
        markdown_table(table),
        "",
        "## Specificity Mechanism Columns",
        "",
        markdown_table(key.assign(
            spec_ai_coef=key["spec_ai_coef"].map(lambda x: fmt_num(x, 6)),
            spec_ai_se=key["spec_ai_se"].map(lambda x: fmt_num(x, 6)),
            spec_ai_p=key["spec_ai_p"].map(lambda x: fmt_num(x, 4)),
        )),
        "",
        "## Notes",
        "",
        "- `Supplier R&D Intensity` from POM is not directly available in the current local data. The closest current proxy is prior AI patent evidence.",
        "- `Product-oriented announcement` is rule-coded and must be manually audited before it is used as a final paper variable.",
        "- `Disclosure specificity` has already been built. Under event fixed effects, its main effect is absorbed; the credible specification is the interaction `Specificity x AIActivePeer`.",
        "- Standard errors are two-way clustered by event and peer firm, following the v29 implementation.",
        "",
        "## Output Files",
        "",
        f"- `{OUT_DIR.relative_to(ROOT)}/pom_variable_mapping.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/pom_analog_variable_coverage.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/pom_analog_cross_section_regressions.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/pom_analog_cross_section_regressions_raw.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/analysis_panel_pom_analog.csv.gz`",
        f"- `{OUT_DIR.relative_to(ROOT)}/{RUN_ID}.xlsx`",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    d = build_analysis_panel()
    rows = run_models(d)
    table = formatted_table(rows)
    save_outputs(d, rows, table)
    print(f"rows={len(d):,}, events={d['event_key'].nunique():,}, peers={d['peer_code'].nunique():,}")
    print(table.to_string(index=False))
    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
