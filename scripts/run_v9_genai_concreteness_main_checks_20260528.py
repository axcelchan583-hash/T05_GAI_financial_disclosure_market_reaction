#!/usr/bin/env python3
"""Main-effect checks using the new GenAI disclosure concreteness X.

This script does not replace the existing v6/v7 runs. It asks whether the
fresh Hope/Cheng-style event-level concreteness measure can reproduce the
current peer-CAR main effect.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from run_v6_final_review_checks_20260525 import OUTCOME, ROOT, STRONG_FE
from run_v6_identification_strengthening_checks_20260524 import fit_absorbed


OUT_DIR = ROOT / "results" / "v9_genai_concreteness_main_checks_20260528"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "64_v9_genai_concreteness_main_checks_20260528.md"

TOP5_PANEL_PATH = ROOT / "results" / "v6_focal_good_news_pretrend_checks_20260525" / "analysis_sample_top5.csv.gz"
CONCRETENESS_PATH = ROOT / "results" / "genai_concreteness_measure_20260528" / "event_genai_concreteness.csv"

AI_DEFS = ["ext_any", "current_text_history"]
AI_LABEL = {"ext_any": "ext_any", "current_text_history": "text_history"}
CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
FOCAL_CONTROLS = ["focal_car_0_p1_mm", "focal_car_x_ai", *CONTROLS]

X_SPECS = [
    ("legacy_specificity_z", "specificity_z", "legacy Specificity_z"),
    ("genai_concreteness_z", "genai_concreteness_z", "new concreteness z"),
    ("genai_concreteness_resid_z", "genai_concreteness_resid_z", "new residualized concreteness z"),
]

CONTENT_FLAGS = [
    "competitive_risk_content",
    "category_validation_content",
    "speculative_or_generic_content",
    "substantive_or_existing_content",
]


def load_sample() -> pd.DataFrame:
    panel = pd.read_csv(TOP5_PANEL_PATH, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    x = pd.read_csv(
        CONCRETENESS_PATH,
        dtype={"event_id": str, "focal_code": str},
        usecols=[
            "event_id",
            "genai_concreteness_z",
            "genai_concreteness_z_by_year",
            "genai_concreteness_resid_z",
            "genai_concreteness_raw",
            "positive_genai_claim_content",
            "denial_or_no_exposure_content",
            *CONTENT_FLAGS,
            "content_category_primary",
        ],
    )
    out = panel.merge(x, on="event_id", how="left", validate="many_to_one")
    if out["genai_concreteness_resid_z"].isna().any():
        missing = out.loc[out["genai_concreteness_resid_z"].isna(), "event_id"].nunique()
        raise RuntimeError(f"Missing concreteness for {missing} events after merge")
    for col in [
        OUTCOME,
        "specificity_z",
        "genai_concreteness_z",
        "genai_concreteness_resid_z",
        "peer_car_pre10_m2_mm",
        "peer_car_pre20_m2_mm",
        "focal_car_0_p1_mm",
        *AI_DEFS,
        *CONTENT_FLAGS,
        "positive_genai_claim_content",
        "denial_or_no_exposure_content",
    ]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def add_terms(df: pd.DataFrame, ai_def: str, x_col: str) -> pd.DataFrame:
    out = df.copy()
    out["ai"] = out[ai_def].fillna(0).astype(float)
    out["x_main"] = pd.to_numeric(out[x_col], errors="coerce")
    out["x_ai"] = out["x_main"] * out["ai"]
    out["focal_car_x_ai"] = out["focal_car_0_p1_mm"] * out["ai"]
    for flag in CONTENT_FLAGS:
        label = flag.replace("_content", "")
        out[f"{label}_ai"] = out[flag].fillna(0).astype(float) * out["ai"]
        out[f"{label}_x_ai"] = out[flag].fillna(0).astype(float) * out["x_main"] * out["ai"]
    return out


def run_focus(
    data: pd.DataFrame,
    ai_def: str,
    x_key: str,
    x_col: str,
    outcome: str,
    model: str,
    xvars_extra: list[str],
    focus_terms: list[str] | None = None,
) -> list[dict[str, object]]:
    d = add_terms(data, ai_def, x_col)
    xvars = ["ai", "x_ai", *xvars_extra]
    rows = fit_absorbed(d, outcome, xvars, STRONG_FE, model=model, term_focus=None)
    out = []
    for row in rows:
        if focus_terms is not None and row["term"] not in focus_terms:
            continue
        row.update(
            {
                "ai_def": AI_LABEL[ai_def],
                "x_key": x_key,
                "x_col": x_col,
                "fe": "+".join(STRONG_FE),
                "cluster": "event_id + peer_code",
                "xvars": "|".join(xvars),
            }
        )
        out.append(row)
    return out


def residualize_y(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    y = pd.to_numeric(out[OUTCOME], errors="coerce").to_numpy(float)
    pre = pd.to_numeric(out["peer_car_pre10_m2_mm"], errors="coerce").to_numpy(float)
    valid = np.isfinite(y) & np.isfinite(pre)
    resid = np.full(len(out), np.nan)
    if valid.sum() >= 10:
        x = np.column_stack([np.ones(valid.sum()), pre[valid]])
        beta = np.linalg.lstsq(x, y[valid], rcond=None)[0]
        resid[valid] = y[valid] - x @ beta
    out["peer_car_0_p1_resid_pre10_newx"] = resid
    return out


def sample_summary(df: pd.DataFrame) -> pd.DataFrame:
    event = df.drop_duplicates("event_id").copy()
    rows = [
        {"metric": "rows", "value": len(df)},
        {"metric": "events", "value": df["event_id"].nunique()},
        {"metric": "focal_firms", "value": df["focal_code"].nunique()},
        {"metric": "peer_firms", "value": df["peer_code"].nunique()},
        {"metric": "ext_any_share_obs", "value": df["ext_any"].mean()},
        {"metric": "text_history_share_obs", "value": df["current_text_history"].mean()},
        {"metric": "competitive_risk_share_events", "value": event["competitive_risk_content"].mean()},
        {"metric": "category_validation_share_events", "value": event["category_validation_content"].mean()},
        {"metric": "speculative_generic_share_events", "value": event["speculative_or_generic_content"].mean()},
        {"metric": "substantive_existing_share_events", "value": event["substantive_or_existing_content"].mean()},
        {
            "metric": "corr_legacy_specificity_new_resid_event",
            "value": event[["specificity_z", "genai_concreteness_resid_z"]].corr().iloc[0, 1],
        },
        {
            "metric": "corr_legacy_specificity_new_z_event",
            "value": event[["specificity_z", "genai_concreteness_z"]].corr().iloc[0, 1],
        },
    ]
    return pd.DataFrame(rows)


def pstars(p: float) -> str:
    if pd.isna(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def table(df: pd.DataFrame, cols: list[str]) -> str:
    d = df.copy()
    d["coef_se"] = d.apply(
        lambda r: f"{r['coef']:.6f}{pstars(r['p'])} ({r['se']:.6f})" if pd.notna(r.get("coef")) else "",
        axis=1,
    )
    out = d[cols].copy()
    for c in ["p", "coef", "se", "z", "mean_y"]:
        if c in out.columns:
            out[c] = out[c].map(lambda x: "" if pd.isna(x) else f"{float(x):.4f}")
    return out.to_markdown(index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    sample = load_sample()
    sample = residualize_y(sample)
    sample.to_csv(OUT_DIR / "analysis_sample_top5_with_genai_concreteness.csv.gz", index=False, compression="gzip")
    sample_summary(sample).to_csv(OUT_DIR / "sample_summary.csv", index=False)

    rows: list[dict[str, object]] = []
    for ai_def in AI_DEFS:
        for x_key, x_col, _ in X_SPECS:
            rows.extend(
                run_focus(
                    sample,
                    ai_def,
                    x_key,
                    x_col,
                    OUTCOME,
                    "baseline_prewindow_controls",
                    CONTROLS,
                    focus_terms=["x_ai"],
                )
            )
            rows.extend(
                run_focus(
                    sample,
                    ai_def,
                    x_key,
                    x_col,
                    OUTCOME,
                    "add_focal_car_and_focal_car_x_ai",
                    FOCAL_CONTROLS,
                    focus_terms=["x_ai"],
                )
            )
            rows.extend(
                run_focus(
                    sample,
                    ai_def,
                    x_key,
                    x_col,
                    "peer_car_0_p1_resid_pre10_newx",
                    "residual_y_on_pre10_plus_focal_controls",
                    ["focal_car_0_p1_mm", "focal_car_x_ai", "peer_car_pre20_m2_mm"],
                    focus_terms=["x_ai"],
                )
            )

    main_results = pd.DataFrame(rows)
    main_results.to_csv(OUT_DIR / "main_x_horse_race.csv", index=False)

    # Content horse-race using the recommended residualized X.
    content_rows: list[dict[str, object]] = []
    content_ai_terms = [f"{flag.replace('_content', '')}_ai" for flag in CONTENT_FLAGS]
    content_x_ai_terms = [f"{flag.replace('_content', '')}_x_ai" for flag in CONTENT_FLAGS]
    for ai_def in AI_DEFS:
        content_rows.extend(
            run_focus(
                sample,
                ai_def,
                "genai_concreteness_resid_z",
                "genai_concreteness_resid_z",
                OUTCOME,
                "concreteness_plus_content_type_x_ai",
                [*content_ai_terms, *CONTROLS],
                focus_terms=["x_ai", *content_ai_terms],
            )
        )
        content_rows.extend(
            run_focus(
                sample,
                ai_def,
                "genai_concreteness_resid_z",
                "genai_concreteness_resid_z",
                OUTCOME,
                "content_specific_concreteness_x_ai",
                [*content_x_ai_terms, *CONTROLS],
                focus_terms=content_x_ai_terms,
            )
        )
    content_results = pd.DataFrame(content_rows)
    content_results.to_csv(OUT_DIR / "content_type_horserace_new_x.csv", index=False)

    # Subsample split by primary content flags, for interpretability.
    split_rows: list[dict[str, object]] = []
    for flag in CONTENT_FLAGS:
        sub = sample[sample[flag].fillna(0).astype(int).eq(1)].copy()
        for ai_def in AI_DEFS:
            split_rows.extend(
                run_focus(
                    sub,
                    ai_def,
                    "genai_concreteness_resid_z",
                    "genai_concreteness_resid_z",
                    OUTCOME,
                    f"subsample_{flag}",
                    CONTROLS,
                    focus_terms=["x_ai"],
                )
            )
    split_results = pd.DataFrame(split_rows)
    split_results.to_csv(OUT_DIR / "content_subsample_new_x.csv", index=False)

    summ = pd.read_csv(OUT_DIR / "sample_summary.csv")
    doc = f"""# V9 GenAI Concreteness Main-Effect Checks

Date: 2026-05-28

## Purpose

Re-estimate the current Top5 peer-CAR main effect using the new Hope/Cheng-style event-level X:

`genai_concreteness_resid_z`

This run is deliberately a measurement handoff check. The old `specificity_z` result should not be assumed to carry over because the new X is only weakly correlated with the legacy variable.

## Sample

Input panel:

`results/v6_focal_good_news_pretrend_checks_20260525/analysis_sample_top5.csv.gz`

Event-level X:

`results/genai_concreteness_measure_20260528/event_genai_concreteness.csv`

Sample summary:

{summ.to_markdown(index=False)}

## Main X Horse-Race

Outcome: `PeerCAR[0,+1]`.

FE: `event_id + peer_industry_week`.

SE: two-way clustered by `event_id + peer_code`.

Controls:

- baseline: `PeerCAR[-10,-2] + PeerCAR[-20,-2]`
- focal-control version: baseline + `FocalCAR[0,+1] + FocalCAR[0,+1] x AIActive`
- residual-y version: outcome residualized on `PeerCAR[-10,-2]`, then controls `FocalCAR[0,+1] + FocalCAR[0,+1] x AIActive + PeerCAR[-20,-2]`

{table(main_results, ["ai_def", "x_key", "model", "outcome", "coef_se", "p", "nobs", "events", "peer_firms"])}

## Content-Type Horse-Race With New X

Outcome: `PeerCAR[0,+1]`.

Main X: `genai_concreteness_resid_z x AIActive`.

{table(content_results, ["ai_def", "model", "term", "coef_se", "p", "nobs", "events", "peer_firms"])}

## Content-Flag Subsamples

Each row estimates the main `genai_concreteness_resid_z x AIActive` coefficient within events carrying the listed content flag.

{table(split_results, ["ai_def", "model", "coef_se", "p", "nobs", "events", "peer_firms"])}

## Interpretation Note

If `genai_concreteness_resid_z x AIActive` is weak or unstable while the old `specificity_z x AIActive` remains significant, the existing peer-revaluation result is not yet secured by the new Hope/Cheng-style X. In that case the paper should either:

1. keep the legacy `specificity_z` as the empirical X and use this new measure as a validation/robustness branch, or
2. revise the new measure before treating it as the headline X.

"""
    DOC_PATH.write_text(doc, encoding="utf-8")

    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
