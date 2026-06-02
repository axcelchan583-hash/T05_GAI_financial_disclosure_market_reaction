#!/usr/bin/env python3
"""Data-processing sensitivity checks for the T05 peer-CAR main effect.

This is a diagnostic run, not a new research design. It asks whether the
existing Specificity_z x AIActivePeer peer-CAR result is sensitive to:

1. sample cleaning and data-quality filters;
2. outcome outlier handling;
3. variable transformations;
4. event windows and pre-window lag controls;
5. alternative pre-observable AIActive definitions.
"""

from __future__ import annotations

import math
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


TRUE_EXT_PANEL = (
    ROOT
    / "results"
    / "v6_external_ai_active_checks_20260524"
    / "true_panel_with_external_ai_active.csv.gz"
)

OUT_DIR = ROOT / "results" / "v14_data_processing_sensitivity_20260531"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "77_v14_data_processing_sensitivity_20260531.md"

MAIN_OUTCOME = "peer_car_0_p1_mm"
PRE_CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
STRONG_FE = ["event_id", "peer_industry_week"]
AI_DEFS = ["ext_any", "current_text_history"]


def zscore(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").astype(float)
    sd = x.std(ddof=0)
    if not np.isfinite(sd) or sd == 0:
        return pd.Series(np.nan, index=s.index, dtype=float)
    return (x - x.mean()) / sd


def winsor(s: pd.Series, lo: float, hi: float) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").astype(float)
    qlo, qhi = x.quantile([lo, hi])
    return x.clip(qlo, qhi)


def add_window_outcomes(df: pd.DataFrame, lookup: dict[str, dict[str, np.ndarray]]) -> pd.DataFrame:
    specs = [
        ("peer_car_pre20_m11_mm", -20, -11, 7),
        ("peer_car_pre10_m2_mm", -10, -2, 7),
        ("peer_car_pre5_m2_mm", -5, -2, 3),
        ("peer_car_pre20_m2_mm", -20, -2, 15),
        ("peer_car_m1_0_mm", -1, 0, 2),
        ("peer_car_p1_p2_mm", 1, 2, 2),
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


def add_ai_terms(df: pd.DataFrame, ai_def: str, spec_col: str = "specificity_z") -> pd.DataFrame:
    out = df.copy()
    out["ai"] = pd.to_numeric(out[ai_def], errors="coerce").fillna(0).astype(float)
    out["spec_var"] = pd.to_numeric(out[spec_col], errors="coerce").astype(float)
    out["spec_ai"] = out["spec_var"] * out["ai"]
    return out


def run_reg(
    df: pd.DataFrame,
    outcome: str,
    ai_def: str,
    spec_col: str,
    controls: list[str],
    model: str,
    family: str,
    note: str,
    fe_cols: list[str] | None = None,
) -> dict[str, object]:
    fe_cols = fe_cols or STRONG_FE
    d = add_ai_terms(df, ai_def, spec_col)
    xvars = ["ai", "spec_ai", *controls]
    rows = fit_absorbed(d, outcome, xvars, fe_cols, model=model, term_focus="spec_ai")
    if not rows:
        return {
            "family": family,
            "model": model,
            "outcome": outcome,
            "ai_def": ai_def,
            "spec_col": spec_col,
            "coef": math.nan,
            "se": math.nan,
            "z": math.nan,
            "p": math.nan,
            "nobs": 0,
            "events": 0,
            "peer_firms": 0,
            "mean_y": math.nan,
            "controls": "+".join(controls) if controls else "none",
            "fe": "+".join(fe_cols),
            "note": note,
        }
    r = rows[0]
    r.update(
        {
            "family": family,
            "ai_def": ai_def,
            "spec_col": spec_col,
            "controls": "+".join(controls) if controls else "none",
            "fe": "+".join(fe_cols),
            "note": note,
        }
    )
    return r


def first_top5_raw(df: pd.DataFrame) -> pd.DataFrame:
    return df[(df["is_first_focal_event"].eq(1)) & (df["peer_rank"].between(1, 5))].copy()


def standard_sample(df: pd.DataFrame) -> pd.DataFrame:
    d = base_clean_sample(df)
    d = d[d["peer_rank"].between(1, 5)].copy()
    d = d[d["either_cleaning_ann"].eq(0)].copy()
    return d


def drop_st_like(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    name = (
        d["peer_name"].fillna("").astype(str)
        + " "
        + d["focal_name"].fillna("").astype(str)
    )
    return d[~name.str.contains(r"\*?ST|退市|退\b", regex=True)].copy()


def add_transforms(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["specificity_raw_z"] = zscore(out["specificity"])
    nonneg = pd.to_numeric(out["specificity"], errors="coerce").clip(lower=0)
    out["specificity_log1p_z"] = zscore(np.log1p(nonneg))
    out["specificity_rank_z"] = zscore(out["specificity"].rank(pct=True))
    out["specificity_w_p1p99_z"] = zscore(winsor(out["specificity"], 0.01, 0.99))
    out["specificity_z_w_p1p99"] = zscore(winsor(out["specificity_z"], 0.01, 0.99))
    year = pd.to_datetime(out["event_date"], errors="coerce").dt.year
    out["specificity_z_by_year_recalc"] = out.groupby(year)["specificity"].transform(zscore)

    out["peer_car_0_p1_w1p99"] = winsor(out[MAIN_OUTCOME], 0.01, 0.99)
    out["peer_car_0_p1_w25p975"] = winsor(out[MAIN_OUTCOME], 0.025, 0.975)
    out["peer_car_0_p1_asinh"] = np.arcsinh(pd.to_numeric(out[MAIN_OUTCOME], errors="coerce"))
    out["peer_car_0_p1_rank_z"] = out.groupby("event_id")[MAIN_OUTCOME].transform(
        lambda s: zscore(s.rank(pct=True))
    )
    out["peer_car_0_p1_date_z"] = out.groupby("date_0")[MAIN_OUTCOME].transform(zscore)

    # Alternative pre-observable AIActive definitions from existing components.
    out["ext_any_hiring180"] = (
        out["prior_cac"].fillna(0).astype(int).eq(1)
        | out["prior_ai_patent_grant"].fillna(0).astype(int).eq(1)
        | (pd.to_numeric(out["prior_broad_ai_hiring_180_count"], errors="coerce").fillna(0) >= 1)
    ).astype(int)
    out["ext_genai_any"] = (
        out["prior_cac"].fillna(0).astype(int).eq(1)
        | out["prior_genai_patent_grant"].fillna(0).astype(int).eq(1)
        | out["prior_genai_hiring_365_ge1"].fillna(0).astype(int).eq(1)
    ).astype(int)
    out["ext_ai_hiring_ge3"] = (
        out["prior_cac"].fillna(0).astype(int).eq(1)
        | out["prior_ai_patent_grant"].fillna(0).astype(int).eq(1)
        | out["prior_broad_ai_hiring_365_ge3"].fillna(0).astype(int).eq(1)
    ).astype(int)
    return out


def summarize_quality(panel: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, d in [("full_true_panel", panel), ("standard_top5_sample", sample)]:
        rows.append(
            {
                "sample": name,
                "rows": len(d),
                "events": d["event_id"].nunique(),
                "focal_firms": d["focal_code"].nunique(),
                "peer_firms": d["peer_code"].nunique(),
                "duplicate_event_peer_rows": int(d.duplicated(["event_id", "peer_code"]).sum()),
                "missing_peer_car_0_p1": int(d[MAIN_OUTCOME].isna().sum()),
                "missing_specificity_z": int(d["specificity_z"].isna().sum()),
                "missing_ext_any": int(d["ext_any"].isna().sum()),
                "mean_peer_car_0_p1": float(d[MAIN_OUTCOME].mean()),
                "sd_peer_car_0_p1": float(d[MAIN_OUTCOME].std()),
                "p01_peer_car_0_p1": float(d[MAIN_OUTCOME].quantile(0.01)),
                "p99_peer_car_0_p1": float(d[MAIN_OUTCOME].quantile(0.99)),
                "mean_specificity_z": float(d["specificity_z"].mean()),
                "sd_specificity_z": float(d["specificity_z"].std()),
                "mean_ext_any": float(d["ext_any"].mean()),
                "mean_text_history": float(d["current_text_history"].mean()),
            }
        )
    return pd.DataFrame(rows)


def trim_by_quantile(df: pd.DataFrame, col: str, lo: float, hi: float) -> pd.DataFrame:
    qlo, qhi = df[col].quantile([lo, hi])
    return df[df[col].between(qlo, qhi)].copy()


def make_markdown_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    d = df.head(max_rows).copy()
    for col in ["coef", "se", "z", "p", "mean_y"]:
        if col in d.columns:
            d[col] = d[col].map(lambda x: "" if pd.isna(x) else f"{x:.4f}")
    return d.to_markdown(index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    panel = load_panel(TRUE_EXT_PANEL)
    lookup = build_return_lookup(load_stock_model())
    panel = add_window_outcomes(panel, lookup)
    panel = add_transforms(panel)

    raw_top5 = first_top5_raw(panel)
    std = standard_sample(panel)
    std = add_transforms(std)

    quality = summarize_quality(panel, std)
    quality.to_csv(OUT_DIR / "data_quality_summary.csv", index=False)

    rows: list[dict[str, object]] = []

    # 1. Data cleaning variants.
    cleaning_variants = {
        "raw_first_top5": raw_top5,
        "base_clean_no_ann_filter": base_clean_sample(panel)[lambda d: d["peer_rank"].between(1, 5)].copy(),
        "headline_standard": std,
        "drop_any_focal_or_peer_ann": std[
            std["peer_any_ann_m1_p1"].eq(0) & std["focal_any_ann_event_or_0"].eq(0)
        ].copy(),
        "drop_st_like_names": drop_st_like(std),
        "same_industry_only": std[std["same_industry_d"].eq(1)].copy(),
        "est_obs_ge200": std[pd.to_numeric(std["est_obs"], errors="coerce").ge(200)].copy(),
        "positive_similarity": std[pd.to_numeric(std["product_similarity"], errors="coerce").gt(0)].copy(),
    }
    for model, d in cleaning_variants.items():
        for ai_def in AI_DEFS:
            rows.append(
                run_reg(
                    d,
                    MAIN_OUTCOME,
                    ai_def,
                    "specificity_z",
                    PRE_CONTROLS,
                    model,
                    "data_cleaning",
                    "Top5 first focal events; cleaning variant",
                )
            )

    # 2. Outlier handling on Y.
    outlier_variants = {
        "headline_unmodified_y": (std, MAIN_OUTCOME),
        "winsor_y_1_99": (std, "peer_car_0_p1_w1p99"),
        "winsor_y_2p5_97p5": (std, "peer_car_0_p1_w25p975"),
        "trim_y_1_99": (trim_by_quantile(std, MAIN_OUTCOME, 0.01, 0.99), MAIN_OUTCOME),
        "trim_y_2p5_97p5": (trim_by_quantile(std, MAIN_OUTCOME, 0.025, 0.975), MAIN_OUTCOME),
        "asinh_y": (std, "peer_car_0_p1_asinh"),
        "within_event_rank_y": (std, "peer_car_0_p1_rank_z"),
        "calendar_date_z_y": (std, "peer_car_0_p1_date_z"),
    }
    for model, (d, ycol) in outlier_variants.items():
        for ai_def in AI_DEFS:
            rows.append(
                run_reg(
                    d,
                    ycol,
                    ai_def,
                    "specificity_z",
                    PRE_CONTROLS,
                    model,
                    "outlier_and_y_transform",
                    "Outcome outlier handling / transformation",
                )
            )

    # 3. Specificity transformations.
    spec_variants = [
        "specificity_z",
        "specificity_raw_z",
        "specificity_log1p_z",
        "specificity_rank_z",
        "specificity_w_p1p99_z",
        "specificity_z_w_p1p99",
        "specificity_z_by_year_recalc",
    ]
    for spec_col in spec_variants:
        for ai_def in AI_DEFS:
            rows.append(
                run_reg(
                    std,
                    MAIN_OUTCOME,
                    ai_def,
                    spec_col,
                    PRE_CONTROLS,
                    f"spec_transform_{spec_col}",
                    "x_transform",
                    "Specificity variable transformation",
                )
            )

    # 4. Windows and pre-window lag controls.
    window_outcomes = [
        "peer_ar0_mm",
        "peer_car_0_p1_mm",
        "peer_car_m1_0_mm",
        "peer_car_m1_p1_mm",
        "peer_car_p1_p2_mm",
        "peer_car_post2_p5_mm",
        "peer_car_post2_p10_mm",
        "peer_car_pre5_m2_mm",
        "peer_car_pre10_m2_mm",
        "peer_car_pre20_m11_mm",
    ]
    for ycol in window_outcomes:
        for ai_def in AI_DEFS:
            rows.append(
                run_reg(
                    std,
                    ycol,
                    ai_def,
                    "specificity_z",
                    [] if ycol.startswith("peer_car_pre") else PRE_CONTROLS,
                    f"window_{ycol}",
                    "window_and_lag",
                    "Alternative event or placebo window",
                )
            )

    lag_control_specs = {
        "no_pre_controls": [],
        "control_pre5_m2": ["peer_car_pre5_m2_mm"],
        "control_pre10_m2": ["peer_car_pre10_m2_mm"],
        "control_pre20_m11": ["peer_car_pre20_m11_mm"],
        "control_pre10_and_pre20": ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"],
        "control_pre5_pre10_pre20": [
            "peer_car_pre5_m2_mm",
            "peer_car_pre10_m2_mm",
            "peer_car_pre20_m2_mm",
        ],
    }
    for model, controls in lag_control_specs.items():
        for ai_def in AI_DEFS:
            rows.append(
                run_reg(
                    std,
                    MAIN_OUTCOME,
                    ai_def,
                    "specificity_z",
                    controls,
                    model,
                    "prewindow_lag_controls",
                    "Alternative lagged peer-CAR controls",
                )
            )

    # 5. Alternative AIActive lag/source definitions.
    ai_lag_defs = [
        "ext_any",
        "ext_any_hiring180",
        "ext_ai_hiring_ge3",
        "ext_no_hiring",
        "ext_genai_any",
        "ext_plus_history",
        "current_text_history",
    ]
    for ai_def in ai_lag_defs:
        rows.append(
            run_reg(
                std,
                MAIN_OUTCOME,
                ai_def,
                "specificity_z",
                PRE_CONTROLS,
                f"ai_def_{ai_def}",
                "ai_active_lag_definition",
                "Alternative pre-observable AIActive source / lag definition",
            )
        )

    results = pd.DataFrame(rows)
    result_cols = [
        "family",
        "model",
        "outcome",
        "ai_def",
        "spec_col",
        "coef",
        "se",
        "z",
        "p",
        "nobs",
        "events",
        "peer_firms",
        "mean_y",
        "controls",
        "fe",
        "note",
    ]
    results = results[[c for c in result_cols if c in results.columns]]
    results.to_csv(OUT_DIR / "data_processing_sensitivity_all.csv", index=False)
    for fam, sub in results.groupby("family", sort=False):
        sub.to_csv(OUT_DIR / f"{fam}.csv", index=False)

    # Compact decision matrix for the current headline ext_any path.
    focus = results[
        (results["ai_def"].isin(["ext_any", "current_text_history"]))
        & (
            results["model"].isin(
                [
                    "headline_standard",
                    "winsor_y_1_99",
                    "trim_y_1_99",
                    "spec_transform_specificity_rank_z",
                    "window_peer_car_0_p1_mm",
                    "window_peer_car_m1_p1_mm",
                    "window_peer_ar0_mm",
                    "control_pre10_and_pre20",
                    "drop_any_focal_or_peer_ann",
                    "drop_st_like_names",
                ]
            )
        )
    ].copy()
    focus.to_csv(OUT_DIR / "decision_focus_results.csv", index=False)

    # Markdown report.
    ext_focus = results[results["ai_def"].eq("ext_any")].copy()
    text_focus = results[results["ai_def"].eq("current_text_history")].copy()
    stable_ext = ext_focus[(ext_focus["coef"] < 0) & (ext_focus["p"] < 0.10)]
    stable_text = text_focus[(text_focus["coef"] < 0) & (text_focus["p"] < 0.10)]

    md = f"""# v14 Data-Processing Sensitivity Checks

Date: 2026-05-31

Purpose: diagnose whether the current peer-CAR main effect is driven by data
quality filters, outliers, variable scaling, event windows, or lag controls.

This run does **not** change the research design or introduce a new Y.

## Input

- Panel: `{TRUE_EXT_PANEL.relative_to(ROOT)}`
- Main sample: first focal GenAI event x old CSMAR-scope Top5 peers
- Main outcome: `PeerCAR[0,+1]` (`peer_car_0_p1_mm`)
- Main term: `Specificity_z x AIActivePeer`
- Main FE: `event_id + peer_industry_week`
- SE: inherited from `fit_absorbed`, two-way clustered by event and peer firm

## Data Quality Summary

{quality.to_markdown(index=False)}

## Main Cleaning Variants

{make_markdown_table(results[results['family'].eq('data_cleaning')][['model','ai_def','coef','se','p','nobs','events','peer_firms','mean_y']], 30)}

## Outlier and Y-Transformation Variants

{make_markdown_table(results[results['family'].eq('outlier_and_y_transform')][['model','ai_def','outcome','coef','se','p','nobs','events','peer_firms']], 40)}

## Specificity Transformations

{make_markdown_table(results[results['family'].eq('x_transform')][['model','ai_def','spec_col','coef','se','p','nobs','events','peer_firms']], 40)}

## Event Windows and Lag Controls

{make_markdown_table(results[results['family'].eq('window_and_lag')][['model','ai_def','outcome','coef','se','p','nobs','events','peer_firms']], 40)}

## Alternative Pre-Window Controls

{make_markdown_table(results[results['family'].eq('prewindow_lag_controls')][['model','ai_def','coef','se','p','nobs','events','peer_firms','controls']], 40)}

## Alternative AIActive Lag / Source Definitions

{make_markdown_table(results[results['family'].eq('ai_active_lag_definition')][['model','ai_def','coef','se','p','nobs','events','peer_firms']], 30)}

## Mechanical Summary

- ext_any negative at p < 0.10 in {len(stable_ext)} of {len(ext_focus)} diagnostic specifications.
- text-history negative at p < 0.10 in {len(stable_text)} of {len(text_focus)} diagnostic specifications.

## Interpretation Rules

1. If the coefficient only survives untrimmed / unwinsorized Y, the result is
   outlier-sensitive.
2. If it only survives `PeerCAR[0,+1]` but not adjacent windows, the event-time
   interpretation should stay short-window and cautious.
3. If it disappears under rank / log specificity transformations, the X is
   scale-sensitive.
4. If it disappears under stricter source-lag AIActive definitions, the
   external AIActive claim should be softened.

"""
    DOC_PATH.write_text(md, encoding="utf-8")
    print(f"Wrote {OUT_DIR}")
    print(f"Wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
