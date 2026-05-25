#!/usr/bin/env python3
"""Run the simplified v6 main-effect specification.

Product similarity is used to define Top5/Top10 peer samples, not as the main
moderator. The main coefficient is Specificity x AIActivePeer within focal-event
fixed effects.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.sandwich_covariance import cov_cluster, cov_cluster_2groups


ROOT = Path(__file__).resolve().parents[1]
IN_PATH = (
    ROOT
    / "results"
    / "v6_csmar_peer_market_reaction_smoke_20260523"
    / "v6_peer_event_market_adjusted_car_panel.csv"
)
OUT_DIR = ROOT / "results" / "v6_simple_main_effect_20260523"

OUTCOMES = ["peer_ar0_ma", "peer_car_0_p1_ma", "peer_car_m1_p1_ma"]


def load_panel() -> pd.DataFrame:
    cols = [
        "event_id",
        "focal_code",
        "event_date",
        "peer_code",
        "peer_rank",
        "specificity",
        "product_similarity",
        "ai_active_peer_tminus5",
        "peer_ar0_ma",
        "peer_car_0_p1_ma",
        "peer_car_m1_p1_ma",
        "obs_peer_car_m1_p1_ma",
        "normal_trading_m1_p1",
        "no_limit_m1_p1",
    ]
    panel = pd.read_csv(
        IN_PATH,
        usecols=cols,
        dtype={"event_id": str, "focal_code": str, "peer_code": str},
    )
    panel["event_date"] = pd.to_datetime(panel["event_date"], errors="coerce")
    for col in [
        "peer_rank",
        "specificity",
        "product_similarity",
        "ai_active_peer_tminus5",
        *OUTCOMES,
    ]:
        panel[col] = pd.to_numeric(panel[col], errors="coerce")
    return panel


def add_first_focal_flag(panel: pd.DataFrame) -> pd.DataFrame:
    events = (
        panel[["focal_code", "event_id", "event_date"]]
        .drop_duplicates()
        .sort_values(["focal_code", "event_date", "event_id"])
    )
    first_ids = set(events.groupby("focal_code", sort=False).first()["event_id"])
    out = panel.copy()
    out["is_first_focal_event"] = out["event_id"].isin(first_ids).astype(int)
    return out


def add_specificity_variables(panel: pd.DataFrame) -> pd.DataFrame:
    out = panel.copy()
    event_spec = out[["event_id", "specificity"]].drop_duplicates()
    lo = event_spec["specificity"].quantile(0.01)
    hi = event_spec["specificity"].quantile(0.99)
    out["specificity_w"] = out["specificity"].clip(lo, hi)
    mean = out[["event_id", "specificity_w"]].drop_duplicates()["specificity_w"].mean()
    std = out[["event_id", "specificity_w"]].drop_duplicates()["specificity_w"].std()
    out["specificity_z"] = (out["specificity_w"] - mean) / std
    out["specz_ai_active"] = out["specificity_z"] * out["ai_active_peer_tminus5"]
    out["specraw_ai_active"] = out["specificity"] * out["ai_active_peer_tminus5"]
    return out


def clean_sample(panel: pd.DataFrame) -> pd.DataFrame:
    return panel[
        (panel["obs_peer_car_m1_p1_ma"] == 3)
        & (panel["normal_trading_m1_p1"] == 1)
        & (panel["no_limit_m1_p1"] == 1)
    ].copy()


def demean_by_event(data: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = data[["event_id", "peer_code", *cols]].copy()
    means = out.groupby("event_id", sort=False)[cols].transform("mean")
    for col in cols:
        out[col] = out[col] - means[col]
    return out


def fit_model(
    data: pd.DataFrame,
    outcome: str,
    xvars: list[str],
    model_name: str,
    sample_name: str,
    top_n: int,
    clean_label: str,
) -> list[dict[str, object]]:
    need = [outcome, *xvars, "event_id", "peer_code"]
    d = data.dropna(subset=need).copy()
    if d.empty:
        return []

    dm = demean_by_event(d, [outcome, *xvars])
    y = dm[outcome].to_numpy()
    x = dm[xvars].to_numpy()
    model = sm.OLS(y, x).fit()

    cov_event = cov_cluster(model, pd.Categorical(dm["event_id"]).codes)
    cov_two, _, _ = cov_cluster_2groups(
        model,
        pd.Categorical(dm["event_id"]).codes,
        pd.Categorical(dm["peer_code"]).codes,
    )

    rows: list[dict[str, object]] = []
    for cov_name, cov in [
        ("event_cluster", cov_event),
        ("twoway_event_peer", cov_two),
    ]:
        se = np.sqrt(np.diag(np.asarray(cov)))
        params = model.params
        for idx, term in enumerate(xvars):
            z = params[idx] / se[idx] if se[idx] > 0 else math.nan
            p = 2 * (1 - stats.norm.cdf(abs(z))) if math.isfinite(z) else math.nan
            rows.append(
                {
                    "model": model_name,
                    "sample_name": sample_name,
                    "top_n": top_n,
                    "clean": clean_label,
                    "outcome": outcome,
                    "covariance": cov_name,
                    "term": term,
                    "coef": params[idx],
                    "se": se[idx],
                    "z": z,
                    "p": p,
                    "nobs": int(model.nobs),
                    "events": int(d["event_id"].nunique()),
                    "focal_firms": int(d["focal_code"].nunique()),
                    "peer_firms": int(d["peer_code"].nunique()),
                    "mean_y": float(d[outcome].mean()),
                    "mean_ai_active": float(d["ai_active_peer_tminus5"].mean()),
                }
            )
    return rows


def summarize(data: pd.DataFrame, sample_name: str, top_n: int, clean_label: str) -> dict[str, object]:
    return {
        "sample_name": sample_name,
        "top_n": top_n,
        "clean": clean_label,
        "obs": len(data),
        "events": data["event_id"].nunique(),
        "focal_firms": data["focal_code"].nunique(),
        "peer_firms": data["peer_code"].nunique(),
        "mean_ai_active": data["ai_active_peer_tminus5"].mean(),
        "mean_specificity": data[["event_id", "specificity"]]
        .drop_duplicates()["specificity"]
        .mean(),
        "mean_ar0": data["peer_ar0_ma"].mean(),
        "mean_car_0_p1": data["peer_car_0_p1_ma"].mean(),
        "mean_car_m1_p1": data["peer_car_m1_p1_ma"].mean(),
    }


def run() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    panel = add_specificity_variables(add_first_focal_flag(load_panel()))

    reg_rows: list[dict[str, object]] = []
    sum_rows: list[dict[str, object]] = []

    for sample_name, sample in [
        ("all_events", panel),
        ("first_focal_event", panel[panel["is_first_focal_event"].eq(1)].copy()),
    ]:
        for top_n in [5, 10]:
            top = sample[sample["peer_rank"].le(top_n)].copy()
            samples = [("raw", top), ("clean_m1_p1", clean_sample(top))]
            for clean_label, d in samples:
                sum_rows.append(summarize(d, sample_name, top_n, clean_label))
                for outcome in OUTCOMES:
                    reg_rows.extend(
                        fit_model(
                            d,
                            outcome,
                            ["ai_active_peer_tminus5", "specz_ai_active"],
                            "M1_specz_x_ai_active",
                            sample_name,
                            top_n,
                            clean_label,
                        )
                    )
                    reg_rows.extend(
                        fit_model(
                            d,
                            outcome,
                            [
                                "ai_active_peer_tminus5",
                                "specz_ai_active",
                                "product_similarity",
                            ],
                            "M2_plus_similarity_control",
                            sample_name,
                            top_n,
                            clean_label,
                        )
                    )

    summary = pd.DataFrame(sum_rows)
    regs = pd.DataFrame(reg_rows)
    summary.to_csv(OUT_DIR / "v6_simple_main_effect_sample_summary.csv", index=False)
    regs.to_csv(OUT_DIR / "v6_simple_main_effect_regressions.csv", index=False)

    key = regs[
        regs["covariance"].eq("twoway_event_peer")
        & regs["clean"].eq("clean_m1_p1")
        & regs["term"].eq("specz_ai_active")
    ].copy()
    print(summary.to_string(index=False), flush=True)
    print(key.to_string(index=False), flush=True)


if __name__ == "__main__":
    run()
