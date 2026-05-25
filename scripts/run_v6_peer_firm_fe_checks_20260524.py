#!/usr/bin/env python3
"""Peer-firm fixed-effect robustness for the v6 market-reaction design."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups

from run_v6_announcement_clean_checks_20260524 import (
    ROOT,
    absorb_fixed_effects,
    base_clean_sample,
)


OUTCOME = "peer_car_0_p1_mm"
OUT_DIR = ROOT / "results" / "v6_peer_firm_fe_checks_20260524"
ORIGINAL_PANEL = (
    ROOT
    / "results"
    / "v6_external_ai_active_checks_20260524"
    / "true_panel_with_external_ai_active.csv.gz"
)
LOW_PLACEBO_PANEL = (
    ROOT
    / "results"
    / "v6_external_ai_active_checks_20260524"
    / "placebo_panel_with_external_ai_active.csv.gz"
)
AI_STRIPPED_PANEL = (
    ROOT
    / "results"
    / "v6_external_ai_active_ai_stripped_checks_20260524"
    / "ai_stripped_panel_with_external_ai_active.csv.gz"
)


def prep_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    for col in ["event_date", "date_0", "date_m1", "date_p1"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    if "peer_industry_week" not in df.columns:
        df["peer_industry_d"] = df["peer_industry_d"].fillna("UNKNOWN").astype(str)
        df["event_week"] = df["date_0"].dt.strftime("%Y-%U")
        df["peer_industry_week"] = df["peer_industry_d"] + "|" + df["event_week"].fillna("")
    return df


def fit_one(data: pd.DataFrame, term: str, fe_cols: list[str]) -> dict[str, object]:
    d = data.dropna(subset=[OUTCOME, term, "event_id", "peer_code", *fe_cols]).copy()
    dm = absorb_fixed_effects(d, [OUTCOME, term], fe_cols)
    x = dm[[term]].to_numpy()
    y = dm[OUTCOME].to_numpy()
    model = sm.OLS(y, x).fit()
    cov_two, _, _ = cov_cluster_2groups(
        model, pd.Categorical(dm["event_id"]).codes, pd.Categorical(dm["peer_code"]).codes
    )
    se = float(np.sqrt(np.asarray(cov_two)[0, 0]))
    coef = float(model.params[0])
    z = coef / se if se > 0 else math.nan
    p = 2 * (1 - stats.norm.cdf(abs(z))) if math.isfinite(z) else math.nan
    return {
        "term": term,
        "coef": coef,
        "se": se,
        "z": z,
        "p": p,
        "nobs": int(model.nobs),
        "events": int(d["event_id"].nunique()),
        "peer_firms": int(d["peer_code"].nunique()),
        "mean_y": float(d[OUTCOME].mean()),
        "sd_term_after_fe": float(dm[term].std()),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    original = prep_panel(ORIGINAL_PANEL)
    low = prep_panel(LOW_PLACEBO_PANEL)
    stripped = prep_panel(AI_STRIPPED_PANEL)

    groups = [
        ("original_top5", original[original["peer_rank"].le(5)].copy()),
        ("original_top10", original[original["peer_rank"].le(10)].copy()),
        (
            "low_similarity_same_industry",
            low[low["peer_group"].eq("low_similarity_same_industry")].copy(),
        ),
        ("ai_stripped_top5", stripped[stripped["peer_rank"].le(5)].copy()),
        ("ai_stripped_top10", stripped[stripped["peer_rank"].le(10)].copy()),
    ]
    terms = [
        "specz_x_current_text_history",
        "specz_x_ext_any",
        "specz_x_ext_plus_history",
    ]
    fe_specs = [
        ("event_peer_firm_fe", ["event_id", "peer_code"]),
        ("event_peer_firm_peer_industry_week_fe", ["event_id", "peer_code", "peer_industry_week"]),
    ]

    rows: list[dict[str, object]] = []
    for group_name, panel in groups:
        sample = base_clean_sample(panel)
        sample = sample[sample["either_cleaning_ann"].eq(0)].copy()
        for term in terms:
            if term not in sample.columns:
                continue
            for fe_name, fe_cols in fe_specs:
                row = fit_one(sample, term, fe_cols)
                row.update(
                    {
                        "peer_group": group_name,
                        "sample": "drop_either_cleaning_ann",
                        "outcome": OUTCOME,
                        "fe_spec": fe_name,
                    }
                )
                rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(OUT_DIR / "v6_peer_firm_fe_regressions.csv", index=False)
    print(out.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
