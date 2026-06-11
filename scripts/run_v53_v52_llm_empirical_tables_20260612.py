#!/usr/bin/env python3
"""Run v52/v3.3 LLM-coded GenAI announcement empirical tables."""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "measurement"))

import build_v23_cninfo_1055_peer_coverage_20260603 as cov  # noqa: E402
import run_v23_cninfo_1055_peer_event_study_20260603 as pe  # noqa: E402
import run_v24_cninfo_specificity_peer_grid_20260604 as v24  # noqa: E402
import run_v25_empirical_table_pack_20260604 as v25  # noqa: E402


RUN_ID = "v53_v52_llm_empirical_tables_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "115_v53_v52_llm_empirical_tables_20260612.md"

V52_DIR = ROOT / "results" / "v52_deepseek_v3_3_full1601_20260612"
V52_PARSED = V52_DIR / "siliconflow_parsed_outputs.csv"
MACHINE_CSV = Path("/Users/mac/Documents/Obsidian Vault/23-5/T05_GenAI公告_v3_1_machine.csv")

PREFERRED_METHOD = "liu_product_tfidf_same_industry_d_top10"
OUTCOMES = pe.OUTCOMES
MAIN_OUTCOME = "peer_car_0_p1_mm"
PRE_CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
AI_DEFS = ["ext_any", "current_text_history"]


def clean(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def code6(value: object) -> str:
    out = cov.code6(value)
    return out or ""


def p_from_z(z_value: float) -> float:
    return math.erfc(abs(z_value) / math.sqrt(2)) if math.isfinite(z_value) else math.nan


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


def fmt(value: object, digits: int = 4) -> str:
    if value is None or pd.isna(value):
        return ""
    return f"{float(value):.{digits}f}"


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


def read_text(path: object, limit: int = 180_000) -> str:
    p = Path(clean(path))
    if not p.exists() or p.is_dir():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")[:limit]


def load_coded_rows() -> pd.DataFrame:
    machine = pd.read_csv(MACHINE_CSV, dtype=str, low_memory=False)
    parsed = pd.read_csv(V52_PARSED, dtype=str, low_memory=False)
    machine["id"] = machine["pack_row_id"].map(clean)
    parsed["id"] = parsed["id"].map(clean)
    df = machine.merge(parsed, on="id", how="inner", validate="one_to_one")
    if len(df) != len(parsed):
        raise RuntimeError(f"v52 merge lost rows: parsed={len(parsed)}, merged={len(df)}")
    df["focal_code"] = df["sec_code"].map(code6)
    df["event_id"] = df["id"]
    model_date = pd.to_datetime(df["event_date"], errors="coerce")
    manual_date = pd.to_datetime(df.get("manual_correct_event_date", ""), errors="coerce")
    announce_date = pd.to_datetime(df["announcement_date"], errors="coerce")
    df["event_date"] = model_date.where(model_date.notna(), manual_date.where(manual_date.notna(), announce_date))
    df["event_year"] = df["event_date"].dt.year
    df["announcement_date"] = announce_date.dt.strftime("%Y-%m-%d")
    df["event_date_str"] = df["event_date"].dt.strftime("%Y-%m-%d")
    for col in ["qian_recall_score", "manual_priority_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["out", "mode", "layer", "realized", "model_verdict", "review_priority", "uncertainty"]:
        df[col] = df[col].fillna("").map(clean)
    df["out_num"] = pd.to_numeric(df["out"], errors="coerce")
    df["credible_A"] = df["model_verdict"].eq("A").astype(int)
    return df[df["focal_code"].ne("") & df["event_date"].notna()].copy()


def is_nonai_investment_placebo(df: pd.DataFrame) -> pd.Series:
    text = (
        df["primary_pom_like_category"].fillna("")
        + " "
        + df["announcement_title"].fillna("")
        + " "
        + df["machine_pred_reason"].fillna("")
    )
    pattern = r"投资|建设|增资|收购|项目|合同|产业园|数据中心|算力|服务器|芯片|光模块|光芯片"
    return df["model_verdict"].eq("D") & text.str.contains(pattern, regex=True, na=False)


def build_event_samples(coded: pd.DataFrame) -> pd.DataFrame:
    definitions: list[tuple[str, pd.DataFrame]] = []
    a_all = coded[coded["model_verdict"].eq("A")].copy()
    dfw = coded[coded["model_verdict"].eq("D-fw")].copy()
    a_first = a_all.sort_values(["focal_code", "event_date", "event_id"]).drop_duplicates("focal_code")
    stack = pd.concat([a_all, dfw], ignore_index=True)
    placebo = coded[is_nonai_investment_placebo(coded)].copy()

    definitions.extend(
        [
            ("A_all", a_all),
            ("A_first_firm", a_first),
            ("Dfw_all", dfw),
            ("A_Dfw_stack", stack),
            ("D_nonai_investment_placebo", placebo),
        ]
    )

    frames = []
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
    ]
    for sample_name, sub in definitions:
        if sub.empty:
            continue
        event = sub[keep_cols].copy()
        event["sample_name"] = sample_name
        event["event_type"] = np.where(event["model_verdict"].eq("A"), "A", event["model_verdict"])
        event["event_key"] = sample_name + "::" + event["event_id"].astype(str)
        event["sec_name"] = event["sec_name"].fillna("")
        frames.append(event)
    events = pd.concat(frames, ignore_index=True)
    events["auto_pdf_label"] = events["event_type"]
    events["candidate_tier"] = events["model_verdict"]
    return events


def add_specificity(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = events.drop_duplicates("event_id").copy()
    rows = []
    for _, row in base.iterrows():
        text = read_text(row["txt_local_path"])
        if not text:
            text = " ".join(
                clean(row.get(c, ""))
                for c in ["announcement_title", "evidence", "reason", "priority_evidence", "metadata_snippet"]
            )
        spec = v24.legacy_detail_density(text)
        rows.append({"event_id": row["event_id"], **spec})
    measures = pd.DataFrame(rows)
    out = events.merge(measures, on="event_id", how="left")
    out["qian_recall_score"] = pd.to_numeric(out["qian_recall_score"], errors="coerce")
    out["qian_recall_score"] = out["qian_recall_score"].fillna(out["qian_recall_score"].median())
    return out, measures


def sample_summary(events: pd.DataFrame) -> pd.DataFrame:
    return (
        events.groupby(["sample_name", "event_type"], dropna=False)
        .agg(
            events=("event_key", "nunique"),
            focal_firms=("focal_code", "nunique"),
            first_date=("event_date", "min"),
            last_date=("event_date", "max"),
        )
        .reset_index()
        .sort_values(["sample_name", "event_type"])
    )


def coding_distribution(coded: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    verdict = coded.groupby("model_verdict", as_index=False).size().rename(columns={"size": "rows"})
    a_fields = (
        coded[coded["model_verdict"].eq("A")]
        .groupby(["out", "mode", "layer", "realized"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values("rows", ascending=False)
    )
    year = (
        coded.groupby(["event_year", "model_verdict"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["event_year", "model_verdict"])
    )
    return verdict, a_fields, year


def link_peer_panel(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    panels = []
    for spec in cov.NETWORK_SPECS:
        linked = cov.link_network(events, spec)
        if linked.empty:
            print(f"{spec.method}: no linked rows", flush=True)
            continue
        panels.append(linked)
        print(
            f"{spec.method}: rows={len(linked):,}, events={linked['event_key'].nunique():,}",
            flush=True,
        )
    if not panels:
        raise RuntimeError("No peer links were created.")
    panel = pd.concat(panels, ignore_index=True)
    coverage = cov.summarize_panel(events, panel)
    return panel, coverage


def add_returns_ai(panel: pd.DataFrame) -> pd.DataFrame:
    stock = pe.load_stock_model()
    out = pe.attach_event_trading_dates(panel, stock)
    out = pe.build_return_measures(out, stock)
    out = v24.add_prewindows(out)
    out = v24.add_ai_active(out)
    out["date_0"] = pd.to_datetime(out["date_0"], errors="coerce")
    out["event_date"] = pd.to_datetime(out["event_date"], errors="coerce")
    out["event_week"] = out["date_0"].dt.strftime("%Y-%U")
    out["peer_industry_d"] = out["peer_industry_d"].fillna("UNKNOWN").astype(str)
    out["focal_industry_d"] = out["focal_industry_d"].fillna("UNKNOWN").astype(str)
    out["peer_industry_week"] = out["peer_industry_d"] + "|" + out["event_week"].fillna("")
    out["focal_industry_week"] = out["focal_industry_d"] + "|" + out["event_week"].fillna("")
    for col in ["credible_A", "out_num"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def clean_panel(panel: pd.DataFrame, sample_name: str | None = None, method: str | None = None) -> pd.DataFrame:
    d = panel[panel["complete_clean_m1_p1"].eq(1)].copy()
    if sample_name is not None:
        d = d[d["sample_name"].eq(sample_name)].copy()
    if method is not None:
        d = d[d["method_variant"].eq(method)].copy()
    return d


def mean_event_study(panel: pd.DataFrame, samples: list[str] | None = None) -> pd.DataFrame:
    d0 = clean_panel(panel)
    if samples is not None:
        d0 = d0[d0["sample_name"].isin(samples)].copy()
    rows = []
    group_cols = ["sample_name", "method_variant", "method", "method_top_n", "time_valid_prior_year"]
    for key, d in d0.groupby(group_cols, dropna=False):
        base = dict(zip(group_cols, key))
        for outcome, label in OUTCOMES:
            rows.append({**base, "outcome": outcome, "outcome_label": label, **pe.clustered_mean(d, outcome)})
    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["sample_name", "outcome", "time_valid_prior_year", "p", "method_variant"])
    return out


def grouped_mean(panel: pd.DataFrame, sample_name: str, group_col: str, method: str = PREFERRED_METHOD) -> pd.DataFrame:
    d0 = clean_panel(panel, sample_name, method)
    rows = []
    for group, d in d0.groupby(group_col, dropna=False):
        for outcome, label in OUTCOMES:
            rows.append(
                {
                    "sample_name": sample_name,
                    "method_variant": method,
                    "group_col": group_col,
                    "group_value": group,
                    "outcome": outcome,
                    "outcome_label": label,
                    **pe.clustered_mean(d, outcome),
                }
            )
    return pd.DataFrame(rows)


def spec_z_map(events: pd.DataFrame, sample_name: str, raw_col: str = "legacy_detail_density_raw") -> dict[str, float]:
    ev = events[events["sample_name"].eq(sample_name)].drop_duplicates("event_key").copy()
    ev["spec_z"] = v25.zscore(v25.winsorize(ev[raw_col]))
    return dict(zip(ev["event_key"], ev["spec_z"]))


def regression_rows(panel: pd.DataFrame, events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    contrast_rows = []
    stack = clean_panel(panel, "A_Dfw_stack", PREFERRED_METHOD)
    stack = stack.dropna(subset=[MAIN_OUTCOME, *PRE_CONTROLS, "credible_A", "peer_industry_week"])
    if not stack.empty:
        stack["ai"] = pd.to_numeric(stack["ext_any"], errors="coerce").fillna(0.0)
        stack["credible_x_ai"] = stack["credible_A"] * stack["ai"]
        for label, xvars, term in [
            ("A_vs_Dfw_peer_car", ["credible_A", *PRE_CONTROLS], "credible_A"),
            ("A_vs_Dfw_x_AIActive", ["credible_A", "ai", "credible_x_ai", *PRE_CONTROLS], "credible_x_ai"),
        ]:
            res = v25.fit_absorbed_ols(stack, MAIN_OUTCOME, xvars, ["peer_industry_week"])
            if res and f"{term}_coef" in res:
                contrast_rows.append(
                    {
                        "model": label,
                        "term": term,
                        "coef": res[f"{term}_coef"],
                        "se": res[f"{term}_se"],
                        "z": res[f"{term}_z"],
                        "p": res[f"{term}_p"],
                        "nobs": res["nobs"],
                        "events": res["events"],
                        "focal_firms": res["focal_firms"],
                        "peer_firms": res["peer_firms"],
                        "overall_r2": res["overall_r2"],
                        "within_r2": res["within_r2"],
                    }
                )

    spec_rows = []
    for sample_name in ["A_all", "A_first_firm"]:
        zmap = spec_z_map(events, sample_name)
        for method in sorted(panel["method_variant"].dropna().unique()):
            d0 = clean_panel(panel, sample_name, method)
            d0 = d0.dropna(subset=[MAIN_OUTCOME, *PRE_CONTROLS, "peer_industry_week"])
            if d0.empty:
                continue
            d0["spec_z"] = d0["event_key"].map(zmap)
            if d0["spec_z"].notna().sum() < 40 or d0["spec_z"].std(ddof=0) == 0:
                continue
            for ai_def in AI_DEFS:
                d = d0.copy()
                d["ai"] = pd.to_numeric(d[ai_def], errors="coerce").fillna(0.0)
                d["spec_ai"] = d["spec_z"] * d["ai"]
                res = v25.fit_absorbed_ols(
                    d,
                    MAIN_OUTCOME,
                    ["ai", "spec_ai", *PRE_CONTROLS],
                    ["event_key", "peer_industry_week"],
                )
                if res and "spec_ai_coef" in res:
                    spec_rows.append(
                        {
                            "sample_name": sample_name,
                            "method_variant": method,
                            "ai_def": ai_def,
                            "term": "spec_ai",
                            "coef": res["spec_ai_coef"],
                            "se": res["spec_ai_se"],
                            "z": res["spec_ai_z"],
                            "p": res["spec_ai_p"],
                            "nobs": res["nobs"],
                            "events": res["events"],
                            "focal_firms": res["focal_firms"],
                            "peer_firms": res["peer_firms"],
                            "overall_r2": res["overall_r2"],
                            "within_r2": res["within_r2"],
                        }
                    )

    cut_rows = []
    d0 = clean_panel(panel, "A_all", PREFERRED_METHOD)
    d0 = d0.dropna(subset=[MAIN_OUTCOME, *PRE_CONTROLS, "peer_industry_week"])
    cut_defs = {
        "OUT_1": d0["out"].eq("1"),
        "M_ext": d0["mode"].eq("ext"),
        "R_plus": d0["realized"].eq("+"),
        "L_model_app": d0["layer"].isin(["model", "app"]),
        "L_compute": d0["layer"].eq("compute"),
    }
    for cut_name, mask in cut_defs.items():
        d = d0.copy()
        d["ai"] = pd.to_numeric(d["ext_any"], errors="coerce").fillna(0.0)
        d["cut"] = mask.astype(int)
        d["cut_x_ai"] = d["cut"] * d["ai"]
        if d["cut"].nunique() < 2 or d["cut_x_ai"].std(ddof=0) == 0:
            continue
        res = v25.fit_absorbed_ols(
            d,
            MAIN_OUTCOME,
            ["ai", "cut_x_ai", *PRE_CONTROLS],
            ["event_key", "peer_industry_week"],
        )
        if res and "cut_x_ai_coef" in res:
            cut_rows.append(
                {
                    "cut": cut_name,
                    "term": "cut_x_ai",
                    "coef": res["cut_x_ai_coef"],
                    "se": res["cut_x_ai_se"],
                    "z": res["cut_x_ai_z"],
                    "p": res["cut_x_ai_p"],
                    "nobs": res["nobs"],
                    "events": res["events"],
                    "focal_firms": res["focal_firms"],
                    "peer_firms": res["peer_firms"],
                    "overall_r2": res["overall_r2"],
                    "within_r2": res["within_r2"],
                }
            )
    return pd.DataFrame(contrast_rows), pd.DataFrame(spec_rows), pd.DataFrame(cut_rows)


def validation_table(events: pd.DataFrame) -> pd.DataFrame:
    first_dates = v24.load_first_dates()
    hiring = v24.load_hiring_lookup()
    base = events[events["sample_name"].eq("A_Dfw_stack")].drop_duplicates("event_key").copy()
    rows = []
    for _, row in base.iterrows():
        code = code6(row["focal_code"])
        event_date = pd.Timestamp(row["event_date"])
        fd = first_dates.reindex([code])
        rec = hiring.get(code)
        post_end = event_date + pd.Timedelta(days=365)
        item: dict[str, object] = {
            "event_key": row["event_key"],
            "event_type": row["event_type"],
            "focal_code": code,
            "event_date": event_date,
            "layer": row["layer"],
        }
        for flag, date_col in {
            "cac": "cac_first_date",
            "ai_patent": "ai_patent_grant_first_date",
            "genai_patent": "genai_patent_grant_first_date",
            "history": "history_genai_disclosure_first_date",
        }.items():
            dt = pd.to_datetime(fd[date_col].iloc[0], errors="coerce") if not fd.empty else pd.NaT
            item[f"{flag}_by_event"] = int(pd.notna(dt) and dt <= event_date)
            item[f"{flag}_by_event_p365"] = int(pd.notna(dt) and dt <= post_end)
            item[f"{flag}_post365_new"] = int(pd.notna(dt) and event_date < dt <= post_end)
        start = np.datetime64((event_date + pd.Timedelta(days=1)).normalize())
        end = np.datetime64(post_end.normalize())
        item["post365_broad_ai_hiring"] = v24.count_between(rec, start, end, "broad_cum")
        item["post365_genai_hiring"] = v24.count_between(rec, start, end, "genai_cum")
        rows.append(item)
    detail = pd.DataFrame(rows)
    agg_cols = [c for c in detail.columns if c.endswith("_by_event_p365") or c.endswith("_post365_new")]
    agg_cols += ["post365_broad_ai_hiring", "post365_genai_hiring"]
    summary = (
        detail.groupby("event_type", as_index=False)
        .agg(events=("event_key", "nunique"), **{col: (col, "mean") for col in agg_cols})
        .sort_values("event_type")
    )
    detail.to_csv(OUT_DIR / "t7_validation_event_detail.csv", index=False)
    return summary


def write_doc(
    verdict: pd.DataFrame,
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
        & t2["sample_name"].isin(["A_all", "A_first_firm"])
        & t2["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
    ].sort_values(["sample_name", "outcome"])
    preferred_t8 = t8[
        t8["method_variant"].eq(PREFERRED_METHOD)
        & t8["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
    ].sort_values("outcome")
    lines = [
        "# v53 v52/v3.3 LLM empirical tables",
        "",
        "## Scope",
        "",
        "- Input coding: v52 DeepSeek V4-Pro v3.3 full 1,601-case run.",
        "- Main A sample is model pre-coding only; human review is still required for paper-final claims.",
        f"- Preferred peer method: `{PREFERRED_METHOD}`.",
        "- T1-T8 are produced here. T9 supplier benchmark is produced separately by `scripts/run_v54_v52_supplier_benchmark_20260612.py`.",
        "",
        "## T1 Coding Distribution",
        "",
        md_table(verdict),
        "",
        "A-field distribution:",
        "",
        md_table(a_fields, limit=12),
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
            10,
        ),
        "",
        "## T2 A-Sample Peer Main Effect",
        "",
        md_table(
            preferred_t2,
            ["sample_name", "outcome_label", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"],
            10,
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
        md_table(t4),
        "",
        "## T5 Specificity x AIActive",
        "",
        md_table(t5.sort_values(["sample_name", "p"]), limit=20),
        "",
        "## T6 OUT/M/R/Layer x AIActive Cuts",
        "",
        md_table(t6.sort_values("p"), limit=20),
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
        f"- `{OUT_DIR.relative_to(ROOT)}/v52_coded_rows_enriched.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/v52_event_samples.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/peer_link_panel.csv.gz`",
        f"- `{OUT_DIR.relative_to(ROOT)}/analysis_panel_with_returns_ai.csv.gz`",
        f"- `{OUT_DIR.relative_to(ROOT)}/t1_coding_verdict_distribution.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/t2_peer_main_effect.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/t3_layer_heterogeneity.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/t4_a_vs_dfw_contrast.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/t5_specificity_x_ai.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/t6_out_m_r_layer_cuts.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/t7_validation_summary.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/t8_nonai_investment_placebo.csv`",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    coded = load_coded_rows()
    verdict, a_fields, year = coding_distribution(coded)
    events = build_event_samples(coded)
    events, spec_measures = add_specificity(events)
    counts = sample_summary(events)

    coded.to_csv(OUT_DIR / "v52_coded_rows_enriched.csv", index=False)
    events.to_csv(OUT_DIR / "v52_event_samples.csv", index=False)
    spec_measures.to_csv(OUT_DIR / "v52_specificity_measures.csv", index=False)
    verdict.to_csv(OUT_DIR / "t1_coding_verdict_distribution.csv", index=False)
    a_fields.to_csv(OUT_DIR / "t1_A_field_distribution.csv", index=False)
    year.to_csv(OUT_DIR / "t1_year_verdict_distribution.csv", index=False)
    counts.to_csv(OUT_DIR / "sample_construction_summary.csv", index=False)

    peer_panel, coverage = link_peer_panel(events)
    peer_panel.to_csv(OUT_DIR / "peer_link_panel.csv.gz", index=False)
    coverage.to_csv(OUT_DIR / "peer_coverage_summary.csv", index=False)

    panel = add_returns_ai(peer_panel)
    panel.to_csv(OUT_DIR / "analysis_panel_with_returns_ai.csv.gz", index=False)

    t2 = mean_event_study(panel, ["A_all", "A_first_firm"])
    t3 = grouped_mean(panel, "A_all", "layer")
    t4_means = grouped_mean(panel, "A_Dfw_stack", "event_type")
    t4_reg, t5, t6 = regression_rows(panel, events)
    t4 = pd.concat(
        [
            t4_means[t4_means["outcome"].eq(MAIN_OUTCOME)].assign(model="mean_by_event_type"),
            t4_reg.assign(sample_name="A_Dfw_stack", method_variant=PREFERRED_METHOD),
        ],
        ignore_index=True,
        sort=False,
    )
    t7 = validation_table(events)
    t8 = mean_event_study(panel, ["D_nonai_investment_placebo"])

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
            ("T1_verdict", verdict),
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

    write_doc(verdict, a_fields, counts, coverage, t2, t3, t4, t5, t6, t7, t8)

    print(f"wrote {OUT_DIR}", flush=True)
    print(f"wrote {DOC_PATH}", flush=True)
    print("\nT1 verdict:")
    print(verdict.to_string(index=False), flush=True)
    print("\nPreferred T2:")
    pref = t2[
        t2["method_variant"].eq(PREFERRED_METHOD)
        & t2["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
    ]
    print(pref[["sample_name", "outcome_label", "estimate", "se", "p", "nobs", "events", "peer_firms"]].to_string(index=False), flush=True)
    print("\nT4 regressions:")
    print(t4_reg.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
