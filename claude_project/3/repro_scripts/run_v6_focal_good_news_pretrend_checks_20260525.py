#!/usr/bin/env python3
"""Focused robustness checks requested on 2026-05-25.

Only runs:
1. Focal-firm good-news controls in the headline peer-CAR specification.
2. Pre-trend-adjusted outcome using PeerCAR[-10,-2] residualization.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from run_v6_final_review_checks_20260525 import (
    OUTCOME,
    ROOT,
    STRONG_FE,
    TRUE_EXT_PANEL,
    add_ai_terms,
    add_window_outcomes,
    clean_sample,
)
from run_v6_identification_strengthening_checks_20260524 import (
    build_return_lookup,
    fit_absorbed,
    load_panel,
    load_stock_model,
    window_sum,
)


OUT_DIR = ROOT / "results" / "v6_focal_good_news_pretrend_checks_20260525"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "54_v6_focal_good_news_pretrend_checks_20260525.md"

AI_DEFS = ["current_text_history", "ext_any"]
AI_LABELS = {
    "current_text_history": "text_history",
    "ext_any": "ext_any",
}


def add_focal_car(df: pd.DataFrame, lookup: dict[str, dict[str, np.ndarray]]) -> pd.DataFrame:
    out = df.copy()
    vals, obs, ok = [], [], []
    for code, date0 in zip(out["focal_code"], out["date_0"]):
        v, n, k = window_sum(lookup, code, pd.Timestamp(date0), 0, 1, 2)
        vals.append(v)
        obs.append(n)
        ok.append(k)
    out["focal_car_0_p1_mm"] = vals
    out["obs_focal_car_0_p1_mm"] = obs
    out["ok_focal_car_0_p1_mm"] = ok
    return out


def residualize_on_pretrend(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    y = pd.to_numeric(out[OUTCOME], errors="coerce").to_numpy(dtype=float)
    pre = pd.to_numeric(out["peer_car_pre10_m2_mm"], errors="coerce").to_numpy(dtype=float)
    valid = np.isfinite(y) & np.isfinite(pre)
    resid = np.full(len(out), np.nan)
    if valid.sum() >= 10:
        x = np.column_stack([np.ones(valid.sum()), pre[valid]])
        beta = np.linalg.lstsq(x, y[valid], rcond=None)[0]
        resid[valid] = y[valid] - x @ beta
    out["peer_car_0_p1_resid_pre10"] = resid
    return out


def add_interaction_terms(df: pd.DataFrame, ai_def: str) -> pd.DataFrame:
    out = add_ai_terms(df, ai_def)
    out["focal_car_x_ai"] = out["focal_car_0_p1_mm"] * out["ai"]
    return out


def run_one(
    data: pd.DataFrame,
    ai_def: str,
    outcome: str,
    spec_name: str,
    xvars_extra: list[str],
    controls_note: str,
) -> dict[str, object]:
    d = add_interaction_terms(data, ai_def)
    xvars = ["ai", "spec_ai", *xvars_extra]
    rows = fit_absorbed(
        d,
        outcome,
        xvars,
        STRONG_FE,
        model=spec_name,
        term_focus="spec_ai",
    )
    if not rows:
        return {
            "ai_def": AI_LABELS[ai_def],
            "spec": spec_name,
            "outcome": outcome,
            "term": "spec_ai",
            "coef": np.nan,
            "se": np.nan,
            "z": np.nan,
            "p": np.nan,
            "nobs": 0,
            "events": 0,
            "peer_firms": 0,
            "fe": "+".join(STRONG_FE),
            "cluster": "event_id + peer_code",
            "controls": controls_note,
        }
    row = rows[0]
    return {
        "ai_def": AI_LABELS[ai_def],
        "spec": spec_name,
        "outcome": outcome,
        "term": row["term"],
        "coef": row["coef"],
        "se": row["se"],
        "z": row["z"],
        "p": row["p"],
        "nobs": row["nobs"],
        "events": row["events"],
        "peer_firms": row["peer_firms"],
        "fe": "+".join(STRONG_FE),
        "cluster": "event_id + peer_code",
        "controls": controls_note,
    }


def p_stars(p: float) -> str:
    if pd.isna(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def make_markdown_table(df: pd.DataFrame) -> str:
    d = df.copy()
    d["coef_se"] = d.apply(
        lambda r: f"{r['coef']:.6f}{p_stars(r['p'])} ({r['se']:.6f})"
        if pd.notna(r["coef"])
        else "",
        axis=1,
    )
    cols = ["ai_def", "spec", "coef_se", "p", "nobs", "events", "peer_firms", "controls"]
    out = d[cols].copy()
    out["p"] = out["p"].map(lambda x: "" if pd.isna(x) else f"{x:.3f}")
    out = out.rename(
        columns={
            "ai_def": "AIActive",
            "spec": "Spec",
            "coef_se": "Spec_z x AIActive coef (SE)",
            "p": "p",
            "nobs": "N",
            "events": "Events",
            "peer_firms": "Peer firms",
            "controls": "Controls",
        }
    )
    return out.to_markdown(index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    ret = load_stock_model()
    lookup = build_return_lookup(ret)

    panel = load_panel(TRUE_EXT_PANEL)
    panel = add_window_outcomes(panel, lookup)
    panel = add_focal_car(panel, lookup)
    sample = clean_sample(panel, 1, 5)
    sample = sample.dropna(
        subset=[
            OUTCOME,
            "peer_car_pre10_m2_mm",
            "peer_car_pre20_m2_mm",
            "focal_car_0_p1_mm",
            "event_id",
            "peer_code",
            "peer_industry_week",
        ]
    ).copy()
    sample = residualize_on_pretrend(sample)
    sample.to_csv(OUT_DIR / "analysis_sample_top5.csv.gz", index=False, compression="gzip")

    task1_specs = [
        (
            "baseline_prewindow_controls",
            ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"],
            "PeerCAR[-10,-2], PeerCAR[-20,-2]",
        ),
        (
            "add_focal_car",
            ["focal_car_0_p1_mm", "peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"],
            "FocalCAR[0,+1], PeerCAR[-10,-2], PeerCAR[-20,-2]",
        ),
        (
            "add_focal_car_x_ai",
            [
                "focal_car_0_p1_mm",
                "focal_car_x_ai",
                "peer_car_pre10_m2_mm",
                "peer_car_pre20_m2_mm",
            ],
            "FocalCAR[0,+1], FocalCAR[0,+1] x AIActive, PeerCAR[-10,-2], PeerCAR[-20,-2]",
        ),
    ]

    task2_specs = [
        (
            "residual_y_baseline",
            ["peer_car_pre20_m2_mm"],
            "Outcome residualized on PeerCAR[-10,-2]; RHS controls PeerCAR[-20,-2]",
        ),
        (
            "residual_y_add_focal_car",
            ["focal_car_0_p1_mm", "peer_car_pre20_m2_mm"],
            "Outcome residualized on PeerCAR[-10,-2]; FocalCAR[0,+1], PeerCAR[-20,-2]",
        ),
        (
            "residual_y_add_focal_car_x_ai",
            ["focal_car_0_p1_mm", "focal_car_x_ai", "peer_car_pre20_m2_mm"],
            "Outcome residualized on PeerCAR[-10,-2]; FocalCAR[0,+1], FocalCAR[0,+1] x AIActive, PeerCAR[-20,-2]",
        ),
    ]

    task1_rows: list[dict[str, object]] = []
    task2_rows: list[dict[str, object]] = []
    for ai_def in AI_DEFS:
        for spec_name, xvars_extra, controls_note in task1_specs:
            task1_rows.append(run_one(sample, ai_def, OUTCOME, spec_name, xvars_extra, controls_note))
        for spec_name, xvars_extra, controls_note in task2_specs:
            task2_rows.append(
                run_one(
                    sample,
                    ai_def,
                    "peer_car_0_p1_resid_pre10",
                    spec_name,
                    xvars_extra,
                    controls_note,
                )
            )

    task1 = pd.DataFrame(task1_rows)
    task2 = pd.DataFrame(task2_rows)
    task1.to_csv(OUT_DIR / "task1_focal_good_news_controls.csv", index=False)
    task2.to_csv(OUT_DIR / "task2_pretrend_residualized_y.csv", index=False)

    doc = f"""# V6 Focal Good-News and Pre-Trend Checks

Date: 2026-05-25

Scope: only the two requested robustness checks. Sample is the current headline sample: first focal GenAI event, Top5 product-market peers, announcement-cleaned observations.

Fixed effects: `event_id + peer_industry_week`.

Standard errors: two-way clustered by `event_id` and `peer_code`.

## Task 1: Add Focal-Firm Good-News Controls

Coefficient reported: `Spec_z x AIActive`.

{make_markdown_table(task1)}

Note: `FocalCAR[0,+1]` is event-level and is absorbed by event fixed effects. The informative added control is `FocalCAR[0,+1] x AIActive`.

## Task 2: Pre-Trend-Adjusted Outcome

Outcome is residualized from a first-stage regression of `PeerCAR[0,+1]` on `PeerCAR[-10,-2]`; coefficient reported remains `Spec_z x AIActive`.

{make_markdown_table(task2)}

## Files

- `results/v6_focal_good_news_pretrend_checks_20260525/task1_focal_good_news_controls.csv`
- `results/v6_focal_good_news_pretrend_checks_20260525/task2_pretrend_residualized_y.csv`
- `results/v6_focal_good_news_pretrend_checks_20260525/analysis_sample_top5.csv.gz`
"""
    DOC_PATH.write_text(doc, encoding="utf-8")
    print(f"Wrote {OUT_DIR}")
    print(f"Wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
