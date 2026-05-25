#!/usr/bin/env python3
"""Final review checks after the 2026-05-25 external review.

This script focuses on the current paper shape:
conditional peer revaluation, not new outcomes.

Outputs:
1. headline peer-CAR table with pre-window controls;
2. specificity validation regressions and event-level feature diagnostics;
3. product-market proximity gradient;
4. lead/lag window checks;
5. external AIActive component breakdown with pre-window controls;
6. peer disclosure diffusion mechanism with baseline peer disclosure-rate control.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

from run_v6_announcement_clean_checks_20260524 import ROOT, base_clean_sample
from run_v6_identification_strengthening_checks_20260524 import (
    build_return_lookup,
    fit_absorbed,
    load_panel,
    load_stock_model,
    window_sum,
)


OUT_DIR = ROOT / "results" / "v6_final_review_checks_20260525"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "53_v6_final_review_checks_20260525.md"

TRUE_EXT_PANEL = (
    ROOT
    / "results"
    / "v6_external_ai_active_checks_20260524"
    / "true_panel_with_external_ai_active.csv.gz"
)
PLACEBO_EXT_PANEL = (
    ROOT
    / "results"
    / "v6_external_ai_active_checks_20260524"
    / "placebo_panel_with_external_ai_active.csv.gz"
)
FOCAL_EVENTS_PATH = (
    ROOT
    / "results"
    / "csmar_v5_1_response_smoke_20260523"
    / "csmar_conservative_focal_events_2023_2026.csv"
)
ALL_EVENTS_PATH = (
    ROOT
    / "results"
    / "csmar_genai_event_library_20260523"
    / "combined_firm_day_genai_events.csv"
)
MECHANISM_PANEL_PATH = (
    ROOT
    / "results"
    / "csmar_peer_diffusion_main_effect_20260523"
    / "peer_first_response_panel_first_focal_event.csv"
)

OUTCOME = "peer_car_0_p1_mm"
STRONG_FE = ["event_id", "peer_industry_week"]


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = re.sub(r"\.0$", "", str(value).strip())
    digits = re.sub(r"\D", "", text)
    return digits.zfill(6) if digits else ""


def zscore(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").astype(float)
    std = x.std(ddof=0)
    if not np.isfinite(std) or std == 0:
        return pd.Series(np.zeros(len(x)), index=s.index, dtype=float)
    return (x - x.mean()) / std


def load_true_and_placebo() -> tuple[pd.DataFrame, pd.DataFrame]:
    true = load_panel(TRUE_EXT_PANEL)
    placebo = load_panel(PLACEBO_EXT_PANEL)
    return true, placebo


def add_window_outcomes(df: pd.DataFrame, lookup: dict[str, dict[str, np.ndarray]]) -> pd.DataFrame:
    specs = [
        ("peer_car_pre20_m2_mm", -20, -2, 15),
        ("peer_car_pre20_m11_mm", -20, -11, 7),
        ("peer_car_pre10_m2_mm", -10, -2, 7),
        ("peer_car_pre5_m2_mm", -5, -2, 3),
        ("peer_car_post2_p5_mm", 2, 5, 3),
        ("peer_car_post2_p10_mm", 2, 10, 7),
    ]
    out = df.copy()
    for name, start, end, min_valid in specs:
        vals, obs, ok = [], [], []
        for code, date0 in zip(out["peer_code"], out["date_0"]):
            v, n, k = window_sum(lookup, code, pd.Timestamp(date0), start, end, min_valid)
            vals.append(v)
            obs.append(n)
            ok.append(k)
        out[name] = vals
        out[f"obs_{name}"] = obs
        out[f"ok_{name}"] = ok
    return out


def clean_sample(df: pd.DataFrame, rank_min: int | None = None, rank_max: int | None = None) -> pd.DataFrame:
    d = base_clean_sample(df)
    d = d[d["either_cleaning_ann"].eq(0)].copy()
    if rank_min is not None:
        d = d[d["peer_rank"].ge(rank_min)].copy()
    if rank_max is not None:
        d = d[d["peer_rank"].le(rank_max)].copy()
    return d


def add_ai_terms(df: pd.DataFrame, ai_def: str) -> pd.DataFrame:
    out = df.copy()
    out["ai"] = out[ai_def].fillna(0).astype(float)
    out["spec_ai"] = out["specificity_z"] * out["ai"]
    return out


def run_model(
    data: pd.DataFrame,
    outcome: str,
    ai_def: str,
    xvars_extra: list[str] | None,
    fe_cols: list[str],
    model: str,
    meta: dict[str, object],
    focus: str = "spec_ai",
) -> list[dict[str, object]]:
    d = add_ai_terms(data, ai_def)
    xvars = ["ai", "spec_ai", *(xvars_extra or [])]
    rows = fit_absorbed(d, outcome, xvars, fe_cols, model=model, term_focus=focus)
    for row in rows:
        row.update(meta)
        row["ai_def"] = ai_def
        row["fe_spec"] = "+".join(fe_cols)
        row["xvars"] = "|".join(xvars)
    return rows


def load_event_features() -> pd.DataFrame:
    ev = pd.read_csv(FOCAL_EVENTS_PATH, dtype={"event_id": str, "stock_code": str, "focal_code": str})
    ev["focal_code"] = ev["focal_code"].map(code6)
    ev["event_date"] = pd.to_datetime(ev["event_date"], errors="coerce")
    for col in ["sample_answer", "sample_question", "answer_terms", "question_terms", "sources"]:
        ev[col] = ev[col].fillna("").astype(str)
    for col in [
        "source_count",
        "answer_level_events",
        "total_specific_items",
        "total_genai_span_tokens",
        "total_genai_mentions",
        "specificity",
    ]:
        ev[col] = pd.to_numeric(ev[col], errors="coerce")

    text = ev["sample_answer"].fillna("")
    qtext = ev["sample_question"].fillna("")
    ev["answer_len"] = text.str.len()
    ev["question_len"] = qtext.str.len()
    ev["answer_digit_count"] = text.str.count(r"\d")
    ev["answer_percent_or_money"] = text.str.contains(r"%|％|元|万元|亿元|美元|人民币|收入|成本|费用", regex=True).astype(int)
    ev["answer_date_or_time"] = text.str.contains(r"\d{4}年|\d{1,2}月|\d{1,2}日|季度|上半年|下半年|年内|未来|已经|目前", regex=True).astype(int)

    patterns = {
        "comp_product_service": r"产品|服务|平台|系统|软件|APP|应用|方案|工具|机器人|芯片|模型|模块|解决方案",
        "comp_model_platform": r"ChatGPT|GPT|DeepSeek|通义|文心|Kimi|智谱|豆包|混元|盘古|星火|百川|大模型|LLM|AIGC|MaaS",
        "comp_use_case": r"客服|营销|研发|生产|办公|教育|医疗|金融|汽车|智能座舱|风控|质检|设计|代码|问答|搜索|推荐|训练|诊断",
        "comp_customer_industry": r"客户|用户|行业|企业|医院|银行|学校|政府|C端|B端|ToB|ToC|场景",
        "comp_partner": r"合作|伙伴|联合|阿里|百度|腾讯|华为|微软|OpenAI|商汤|讯飞|京东|字节",
        "comp_deployment": r"已|已经|上线|落地|部署|接入|应用|推出|发布|投入|试点|内测|形成|完成|开展",
        "comp_commercialization": r"收入|订单|合同|商业化|付费|销售|收费|降本|增效|规模化|推广|市场",
    }
    for name, pat in patterns.items():
        ev[name] = text.str.contains(pat, regex=True, case=False).astype(int)
    comp_cols = list(patterns.keys()) + ["answer_percent_or_money", "answer_date_or_time"]
    ev["component_count"] = ev[comp_cols].sum(axis=1)

    z_cols = [
        "answer_len",
        "question_len",
        "total_genai_mentions",
        "total_genai_span_tokens",
        "source_count",
        "answer_level_events",
        "answer_digit_count",
        "component_count",
    ]
    for col in z_cols:
        ev[f"{col}_z"] = zscore(ev[col])
    return ev


def attach_event_features(panel: pd.DataFrame, event_features: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "event_id",
        "answer_len_z",
        "question_len_z",
        "total_genai_mentions_z",
        "total_genai_span_tokens_z",
        "source_count_z",
        "answer_level_events_z",
        "answer_digit_count_z",
        "component_count_z",
        "comp_product_service",
        "comp_model_platform",
        "comp_use_case",
        "comp_customer_industry",
        "comp_partner",
        "comp_deployment",
        "comp_commercialization",
        "answer_percent_or_money",
        "answer_date_or_time",
    ]
    out = panel.merge(event_features[cols], on="event_id", how="left")
    return out


def run_headline(true: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    specs = [
        ("top5", 1, 5),
        ("top10", 1, 10),
    ]
    controls = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
    for sample_name, lo, hi in specs:
        d = clean_sample(true, lo, hi)
        for ai_def in ["current_text_history", "ext_any", "ext_plus_history"]:
            for control_name, extra in [
                ("no_prewindow_controls", []),
                ("with_prewindow_controls", controls),
            ]:
                for fe_name, fe_cols in [
                    ("event_fe", ["event_id"]),
                    ("event_fe_peer_industry_week_fe", STRONG_FE),
                ]:
                    rows.extend(
                        run_model(
                            d,
                            OUTCOME,
                            ai_def,
                            extra,
                            fe_cols,
                            model="headline_peer_car",
                            meta={"sample": sample_name, "control_spec": control_name, "fe_name": fe_name},
                        )
                    )
    return pd.DataFrame(rows)


def run_specificity_validation(true: pd.DataFrame, event_features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    panel = attach_event_features(true, event_features)
    d = clean_sample(panel, 1, 5)
    rows: list[dict[str, object]] = []
    control_sets = {
        "baseline": [],
        "length_question": ["answer_len_z", "question_len_z"],
        "ai_keyword_intensity": ["total_genai_mentions_z", "total_genai_span_tokens_z"],
        "attention_source": ["source_count_z", "answer_level_events_z"],
        "numeric_component": ["answer_digit_count_z", "component_count_z"],
        "full_observable_text_controls": [
            "answer_len_z",
            "question_len_z",
            "total_genai_mentions_z",
            "total_genai_span_tokens_z",
            "source_count_z",
            "answer_level_events_z",
            "answer_digit_count_z",
            "component_count_z",
        ],
    }
    for ai_def in ["current_text_history", "ext_any"]:
        base = add_ai_terms(d, ai_def)
        for spec_name, controls in control_sets.items():
            work = base.copy()
            interaction_controls: list[str] = []
            for col in controls:
                new_col = f"{col}_x_ai"
                work[new_col] = work[col] * work["ai"]
                interaction_controls.append(new_col)
            rows.extend(
                run_model(
                    work,
                    OUTCOME,
                    ai_def,
                    interaction_controls + ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"],
                    STRONG_FE,
                    model="specificity_validation",
                    meta={"sample": "top5", "control_spec": spec_name},
                )
            )

    unique_events = event_features.drop_duplicates("event_id").copy()
    corr_cols = [
        "specificity",
        "answer_len",
        "question_len",
        "total_genai_mentions",
        "total_genai_span_tokens",
        "source_count",
        "answer_level_events",
        "answer_digit_count",
        "component_count",
    ]
    corr = unique_events[corr_cols].corr(numeric_only=True)["specificity"].reset_index()
    corr.columns = ["feature", "corr_with_specificity"]

    comp_cols = [
        "comp_product_service",
        "comp_model_platform",
        "comp_use_case",
        "comp_customer_industry",
        "comp_partner",
        "comp_deployment",
        "comp_commercialization",
        "answer_percent_or_money",
        "answer_date_or_time",
    ]
    comp_summary = (
        unique_events[comp_cols + ["specificity"]]
        .agg(["mean", "std"])
        .T.reset_index()
        .rename(columns={"index": "component"})
    )
    return pd.DataFrame(rows), corr, comp_summary


def run_proximity_gradient(true: pd.DataFrame, placebo: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    groups = [
        ("true_top1_3", true, 1, 3),
        ("true_top4_5", true, 4, 5),
        ("true_top6_10", true, 6, 10),
        ("low_similarity_top5", placebo[placebo["peer_group"].eq("low_similarity_same_industry")], 1, 5),
        ("random_same_industry_top5", placebo[placebo["peer_group"].eq("random_same_industry")], 1, 5),
    ]
    controls = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
    for group, panel, lo, hi in groups:
        d = clean_sample(panel, lo, hi)
        for ai_def in ["current_text_history", "ext_any"]:
            rows.extend(
                run_model(
                    d,
                    OUTCOME,
                    ai_def,
                    controls,
                    STRONG_FE,
                    model="product_market_proximity_gradient",
                    meta={"peer_group": group, "rank_min": lo, "rank_max": hi},
                )
            )
    return pd.DataFrame(rows)


def run_lead_lag(true: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    d = clean_sample(true, 1, 5)
    outcomes = [
        "peer_car_pre20_m11_mm",
        "peer_car_pre10_m2_mm",
        "peer_car_pre5_m2_mm",
        "peer_car_0_p1_mm",
        "peer_car_post2_p5_mm",
        "peer_car_post2_p10_mm",
    ]
    for ai_def in ["current_text_history", "ext_any"]:
        for outcome in outcomes:
            rows.extend(
                run_model(
                    d,
                    outcome,
                    ai_def,
                    [],
                    STRONG_FE,
                    model="lead_lag_windows",
                    meta={"sample": "top5", "window": outcome},
                )
            )
    return pd.DataFrame(rows)


def run_external_breakdown(true: pd.DataFrame, placebo: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    controls = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
    ai_defs = [
        "prior_cac",
        "prior_ai_patent_grant",
        "prior_broad_ai_hiring_365_ge1",
        "prior_broad_ai_hiring_365_ge3",
        "ext_no_hiring",
        "ext_any",
        "ext_strict",
        "ext_plus_history",
    ]
    groups = [
        ("true_top5", true, 1, 5),
        ("true_top10", true, 1, 10),
        ("low_similarity_top5", placebo[placebo["peer_group"].eq("low_similarity_same_industry")], 1, 5),
    ]
    for group, panel, lo, hi in groups:
        d = clean_sample(panel, lo, hi)
        for ai_def in ai_defs:
            if ai_def not in d.columns:
                continue
            rows.extend(
                run_model(
                    d,
                    OUTCOME,
                    ai_def,
                    controls,
                    STRONG_FE,
                    model="external_aiactive_breakdown",
                    meta={"peer_group": group, "rank_min": lo, "rank_max": hi},
                )
            )
    return pd.DataFrame(rows)


def disclosure_dates_by_firm() -> dict[str, np.ndarray]:
    ev = pd.read_csv(ALL_EVENTS_PATH, dtype={"stock_code": str})
    ev["stock_code"] = ev["stock_code"].map(code6)
    ev["event_date"] = pd.to_datetime(ev["event_date_str"], errors="coerce")
    ev = ev.dropna(subset=["event_date"])
    out: dict[str, np.ndarray] = {}
    for code, sub in ev.groupby("stock_code"):
        dates = np.array(sorted(sub["event_date"].dt.normalize().unique()), dtype="datetime64[ns]")
        out[code] = dates
    return out


def prior_event_count(dates: np.ndarray | None, event_date: pd.Timestamp, days: int) -> int:
    if dates is None or len(dates) == 0 or pd.isna(event_date):
        return 0
    end = np.datetime64((pd.Timestamp(event_date) - pd.Timedelta(days=1)).normalize())
    start = np.datetime64((pd.Timestamp(event_date) - pd.Timedelta(days=days)).normalize())
    left = np.searchsorted(dates, start, side="left")
    right = np.searchsorted(dates, end, side="right")
    return max(0, int(right - left))


def run_mechanism(event_features: pd.DataFrame) -> pd.DataFrame:
    panel = pd.read_csv(MECHANISM_PANEL_PATH, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    panel["event_date"] = pd.to_datetime(panel["event_date"], errors="coerce")
    panel["focal_code"] = panel["focal_code"].map(code6)
    panel["peer_code"] = panel["peer_code"].map(code6)
    event_key = (
        event_features[["focal_code", "event_date", "specificity"]]
        .dropna(subset=["focal_code", "event_date"])
        .sort_values(["focal_code", "event_date"])
        .drop_duplicates(["focal_code", "event_date"], keep="first")
    )
    panel = panel.merge(event_key, on=["focal_code", "event_date"], how="left")
    by_firm = disclosure_dates_by_firm()
    panel["peer_prior_genai_events_365"] = [
        prior_event_count(by_firm.get(code), date, 365)
        for code, date in zip(panel["peer_code"], panel["event_date"])
    ]
    rows: list[dict[str, object]] = []
    for top_n in [5, 10]:
        for window in [60, 90, 180]:
            y = f"first_response_{window}"
            full = f"full_window_{window}"
            d = panel[panel["peer_rank"].le(top_n) & panel[full].eq(True)].copy()
            if d.empty:
                continue
            d["similarity_z"] = zscore(d["product_similarity"])
            d["specificity_z"] = zscore(d["specificity"])
            d["spec_similarity"] = d["similarity_z"] * d["specificity_z"]
            d["baseline_rate_z"] = zscore(np.log1p(d["peer_prior_genai_events_365"]))
            model_rows = fit_absorbed(
                d,
                y,
                ["similarity_z", "spec_similarity", "baseline_rate_z"],
                ["event_id"],
                model="peer_disclosure_diffusion_mechanism",
                term_focus="spec_similarity",
            )
            for row in model_rows:
                row.update(
                    {
                        "top_n": top_n,
                        "window_days": window,
                        "response_rate": float(d[y].mean()),
                        "baseline_rate_mean": float(d["peer_prior_genai_events_365"].mean()),
                    }
                )
                rows.append(row)
    return pd.DataFrame(rows)


def write_doc(outputs: dict[str, pd.DataFrame]) -> None:
    lines: list[str] = []
    lines.append("# v6 Final Review Checks\n")
    lines.append("Date: 2026-05-25\n")
    lines.append("## Purpose\n")
    lines.append(
        "This run implements the post-review go/no-go checks: headline peer-CAR with pre-window controls, specificity validation, product-market proximity gradient, lead/lag windows, external AIActive breakdown, and peer disclosure diffusion mechanism.\n"
    )

    def add_section(title: str, df: pd.DataFrame, key_cols: list[str] | None = None) -> None:
        lines.append(f"## {title}\n")
        if df.empty:
            lines.append("No rows produced.\n")
            return
        show = df.copy()
        if key_cols:
            show = show[key_cols]
        lines.append("```text")
        lines.append(show.to_string(index=False))
        lines.append("```\n")

    headline = outputs["headline"]
    hkey = headline[
        (headline["control_spec"].eq("with_prewindow_controls"))
        & (headline["fe_name"].eq("event_fe_peer_industry_week_fe"))
        & (headline["sample"].isin(["top5", "top10"]))
    ].copy()
    add_section(
        "1. Headline Peer-CAR Results with Pre-Window Controls",
        hkey,
        ["sample", "ai_def", "coef", "se", "z", "p", "nobs", "events", "peer_firms"],
    )

    spec = outputs["specificity_validation"]
    add_section(
        "2. Specificity Validation Regressions",
        spec,
        ["ai_def", "control_spec", "coef", "se", "z", "p", "nobs", "events"],
    )

    prox = outputs["proximity_gradient"]
    add_section(
        "3. Product-Market Proximity Gradient",
        prox,
        ["peer_group", "ai_def", "coef", "se", "z", "p", "nobs", "events", "peer_firms"],
    )

    lead = outputs["lead_lag"]
    add_section(
        "4. Lead/Lag Window Checks",
        lead,
        ["window", "ai_def", "coef", "se", "z", "p", "nobs", "events"],
    )

    ext = outputs["external_breakdown"]
    add_section(
        "5. External AIActive Breakdown",
        ext,
        ["peer_group", "ai_def", "coef", "se", "z", "p", "nobs", "events"],
    )

    mech = outputs["mechanism"]
    add_section(
        "6. Peer Disclosure Diffusion Mechanism",
        mech,
        ["top_n", "window_days", "coef", "se", "z", "p", "nobs", "events", "response_rate", "baseline_rate_mean"],
    )

    lines.append("## Output Files\n")
    for name in outputs:
        lines.append(f"- `{OUT_DIR / (name + '.csv')}`")
    lines.append("")
    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    true, placebo = load_true_and_placebo()
    stock_model = load_stock_model()
    lookup = build_return_lookup(stock_model)
    true = add_window_outcomes(true, lookup)
    placebo = add_window_outcomes(placebo, lookup)
    event_features = load_event_features()

    outputs: dict[str, pd.DataFrame] = {}
    outputs["headline"] = run_headline(true)
    spec_regs, spec_corr, spec_components = run_specificity_validation(true, event_features)
    outputs["specificity_validation"] = spec_regs
    outputs["specificity_feature_correlations"] = spec_corr
    outputs["specificity_component_summary"] = spec_components
    outputs["proximity_gradient"] = run_proximity_gradient(true, placebo)
    outputs["lead_lag"] = run_lead_lag(true)
    outputs["external_breakdown"] = run_external_breakdown(true, placebo)
    outputs["mechanism"] = run_mechanism(event_features)

    for name, df in outputs.items():
        df.to_csv(OUT_DIR / f"{name}.csv", index=False)

    write_doc(outputs)
    print(f"Wrote outputs to {OUT_DIR}", flush=True)
    print(f"Wrote doc to {DOC_PATH}", flush=True)
    print(outputs["headline"].to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
