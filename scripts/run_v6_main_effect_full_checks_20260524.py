#!/usr/bin/env python3
"""Full main-effect checks for v6.

Builds on the market-model CAR panels and runs:
1. Event FE vs Event FE + peer-industry-week FE.
2. True Top5/Top10 and placebo peer regressions.
3. Repeated random same-industry placebo draws.

The main term remains:
    Specificity_z x AIActivePeer
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups


ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = ROOT / "results" / "v6_supplement_market_model_placebo_20260524"
OUT_DIR = ROOT / "results" / "v6_main_effect_full_checks_20260524"

TRUE_PANEL = BASE_DIR / "true_peer_market_model_car_panel.csv"
PLACEBO_PANEL = BASE_DIR / "placebo_peer_market_model_car_panel.csv"
STOCK_MODEL = BASE_DIR / "stock_returns_with_market_model_params.csv"
PRODUCT_TEXT = ROOT / "results" / "v4_peer_spillover_x_pilot" / "v4_company_product_text_latest.csv"

OUTCOMES = ["peer_car_0_p1_mm", "peer_car_m1_p1_mm"]
RANDOM_DRAWS = 100


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().replace(".0", "")
    digits = "".join(ch for ch in text if ch.isdigit())
    return digits.zfill(6) if digits else ""


def load_panels() -> tuple[pd.DataFrame, pd.DataFrame]:
    true = pd.read_csv(TRUE_PANEL, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    placebo = pd.read_csv(
        PLACEBO_PANEL, dtype={"event_id": str, "focal_code": str, "peer_code": str}
    )
    for df in [true, placebo]:
        df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
        df["date_0"] = pd.to_datetime(df["date_0"], errors="coerce")
        df["focal_code"] = df["focal_code"].map(code6)
        df["peer_code"] = df["peer_code"].map(code6)
        df["event_week"] = df["date_0"].dt.strftime("%Y-%U")
        df["peer_industry_d"] = df["peer_industry_d"].fillna("UNKNOWN").astype(str)
        df["peer_industry_week"] = df["peer_industry_d"] + "|" + df["event_week"].fillna("")
        df["peer_group"] = df["peer_group"].fillna("true_top10")
    return true, placebo


def clean_sample(df: pd.DataFrame, first_only: bool = True) -> pd.DataFrame:
    out = df.copy()
    if first_only:
        out = out[out["is_first_focal_event"].eq(1)].copy()
    out = out[
        (out["obs_peer_car_m1_p1_mm"] == 3)
        & (out["normal_trading_m1_p1"] == 1)
        & (out["no_limit_m1_p1"] == 1)
        & out["alpha_mm"].notna()
        & out["beta_mm"].notna()
    ].copy()
    return out


def absorb_fixed_effects(data: pd.DataFrame, cols: list[str], fe_cols: list[str]) -> pd.DataFrame:
    # Alternating projections. This is enough for our diagnostic sample sizes.
    arr = data[cols].astype(float).to_numpy(copy=True)
    codes = [pd.Categorical(data[fe]).codes for fe in fe_cols]
    for _ in range(25):
        old = arr.copy()
        for code in codes:
            tmp = pd.DataFrame(arr, columns=cols)
            tmp["_fe"] = code
            means = tmp.groupby("_fe", sort=False)[cols].transform("mean").to_numpy()
            arr -= means
        if np.nanmax(np.abs(arr - old)) < 1e-10:
            break
    out = data[["event_id", "peer_code"]].copy()
    for idx, col in enumerate(cols):
        out[col] = arr[:, idx]
    return out


def fit_absorbed_model(
    data: pd.DataFrame,
    outcome: str,
    xvars: list[str],
    fe_cols: list[str],
) -> list[dict[str, object]]:
    d = data.dropna(subset=[outcome, *xvars, "event_id", "peer_code", *fe_cols]).copy()
    if d.empty:
        return []
    dm = absorb_fixed_effects(d, [outcome, *xvars], fe_cols)
    model = sm.OLS(dm[outcome].to_numpy(), dm[xvars].to_numpy()).fit()
    cov_two, _, _ = cov_cluster_2groups(
        model,
        pd.Categorical(dm["event_id"]).codes,
        pd.Categorical(dm["peer_code"]).codes,
    )
    se = np.sqrt(np.diag(np.asarray(cov_two)))
    rows: list[dict[str, object]] = []
    for i, term in enumerate(xvars):
        z = model.params[i] / se[i] if se[i] > 0 else math.nan
        p = 2 * (1 - stats.norm.cdf(abs(z))) if math.isfinite(z) else math.nan
        rows.append(
            {
                "outcome": outcome,
                "term": term,
                "coef": float(model.params[i]),
                "se": float(se[i]),
                "z": float(z),
                "p": float(p),
                "nobs": int(model.nobs),
                "events": int(d["event_id"].nunique()),
                "peer_firms": int(d["peer_code"].nunique()),
                "mean_y": float(d[outcome].mean()),
                "mean_ai_active": float(d["ai_active_peer_tminus5"].mean()),
            }
        )
    return rows


def run_core_models(true: pd.DataFrame, placebo: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    groups = [
        ("true_top5", true[true["peer_rank"].le(5)].copy(), 5),
        ("true_top10", true[true["peer_rank"].le(10)].copy(), 10),
        (
            "low_similarity_same_industry",
            placebo[placebo["peer_group"].eq("low_similarity_same_industry")].copy(),
            10,
        ),
        (
            "random_same_industry_one_draw",
            placebo[placebo["peer_group"].eq("random_same_industry")].copy(),
            10,
        ),
    ]
    fe_specs = [
        ("event_fe", ["event_id"]),
        ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
    ]
    for peer_group, panel, top_n in groups:
        sample = clean_sample(panel, first_only=True)
        for fe_name, fe_cols in fe_specs:
            for outcome in OUTCOMES:
                for model_name, xvars in [
                    ("M1", ["ai_active_peer_tminus5", "specz_ai_active"]),
                    ("M2_plus_similarity", ["ai_active_peer_tminus5", "specz_ai_active", "product_similarity"]),
                ]:
                    for row in fit_absorbed_model(sample, outcome, xvars, fe_cols):
                        row.update(
                            {
                                "peer_group": peer_group,
                                "top_n": top_n,
                                "sample": "first_focal_event_clean",
                                "fe_spec": fe_name,
                                "model": model_name,
                            }
                        )
                        rows.append(row)
    return pd.DataFrame(rows)


def load_company_candidates(true: pd.DataFrame) -> dict[str, list[str]]:
    companies = pd.read_csv(PRODUCT_TEXT, dtype={"stock_code": str})
    companies["stock_code"] = companies["stock_code"].map(code6)
    companies["industry_d"] = companies["industry_d"].fillna("").astype(str)
    companies = companies[companies["stock_code"].ne("") & companies["industry_d"].ne("")]
    true_peers = {
        code: set(sub["peer_code"])
        for code, sub in true[["focal_code", "peer_code"]].drop_duplicates().groupby("focal_code")
    }
    by_industry = {
        industry: sub["stock_code"].drop_duplicates().tolist()
        for industry, sub in companies.groupby("industry_d", sort=False)
    }
    focal_industry = (
        true[["focal_code", "focal_industry_d"]]
        .drop_duplicates("focal_code")
        .set_index("focal_code")["focal_industry_d"]
        .to_dict()
    )
    candidates: dict[str, list[str]] = {}
    for focal, industry in focal_industry.items():
        pool = [
            code
            for code in by_industry.get(str(industry), [])
            if code != focal and code not in true_peers.get(focal, set())
        ]
        if len(pool) >= 10:
            candidates[focal] = pool
    return candidates


def build_stock_lookup() -> pd.DataFrame:
    stock = pd.read_csv(STOCK_MODEL, dtype={"peer_code": str})
    stock["peer_code"] = stock["peer_code"].map(code6)
    stock["date"] = pd.to_datetime(stock["date"], errors="coerce")
    stock = stock[
        [
            "peer_code",
            "date",
            "ret",
            "mkt_ret",
            "trdsta",
            "limit_status",
            "alpha_mm",
            "beta_mm",
        ]
    ].copy()
    return stock.set_index(["peer_code", "date"]).sort_index()


def attach_returns_fast(panel: pd.DataFrame, stock_idx: pd.DataFrame) -> pd.DataFrame:
    out = panel.copy()
    for suffix, date_col in [("m1", "date_m1"), ("0", "date_0"), ("p1", "date_p1")]:
        idx = pd.MultiIndex.from_arrays([out["peer_code"], out[date_col]])
        vals = stock_idx.reindex(idx)
        vals = vals.reset_index(drop=True)
        for col in ["ret", "mkt_ret", "trdsta", "limit_status"]:
            out[f"{col}_{suffix}"] = vals[col].to_numpy()
    idx0 = pd.MultiIndex.from_arrays([out["peer_code"], out["date_0"]])
    params = stock_idx.reindex(idx0).reset_index(drop=True)
    out["alpha_mm"] = params["alpha_mm"].to_numpy()
    out["beta_mm"] = params["beta_mm"].to_numpy()
    for suffix in ["m1", "0", "p1"]:
        out[f"abret_{suffix}_mm"] = out[f"ret_{suffix}"] - (
            out["alpha_mm"] + out["beta_mm"] * out[f"mkt_ret_{suffix}"]
        )
    out["peer_car_0_p1_mm"] = out[["abret_0_mm", "abret_p1_mm"]].sum(axis=1, min_count=2)
    out["peer_car_m1_p1_mm"] = out[["abret_m1_mm", "abret_0_mm", "abret_p1_mm"]].sum(
        axis=1, min_count=3
    )
    out["obs_peer_car_m1_p1_mm"] = out[
        ["abret_m1_mm", "abret_0_mm", "abret_p1_mm"]
    ].notna().sum(axis=1)
    out["normal_trading_m1_p1"] = (
        out[["trdsta_m1", "trdsta_0", "trdsta_p1"]]
        .fillna(-999)
        .astype(int)
        .eq(1)
        .all(axis=1)
    ).astype(int)
    out["no_limit_m1_p1"] = (
        out[["limit_status_m1", "limit_status_0", "limit_status_p1"]]
        .fillna(0)
        .astype(int)
        .eq(0)
        .all(axis=1)
    ).astype(int)
    return out


def add_ai_active(panel: pd.DataFrame, event_dates_by_code: dict[str, np.ndarray]) -> pd.DataFrame:
    flags: list[int] = []
    for peer, event_date in zip(panel["peer_code"], panel["event_date"], strict=False):
        dates = event_dates_by_code.get(peer)
        if dates is None or len(dates) == 0 or pd.isna(event_date):
            flags.append(0)
            continue
        cutoff = np.datetime64((pd.Timestamp(event_date) - pd.Timedelta(days=5)).normalize())
        flags.append(int(np.searchsorted(dates, cutoff, side="right") > 0))
    out = panel.copy()
    out["ai_active_peer_tminus5"] = flags
    out["specz_ai_active"] = out["specificity_z"] * out["ai_active_peer_tminus5"]
    return out


def repeated_random_placebo(true: pd.DataFrame, draws: int = RANDOM_DRAWS) -> pd.DataFrame:
    candidates = load_company_candidates(true)
    stock_idx = build_stock_lookup()
    event_dates_by_code = {
        code: np.array(sorted(sub["event_date"].dropna().unique()), dtype="datetime64[ns]")
        for code, sub in true[["focal_code", "event_date"]].drop_duplicates().groupby("focal_code")
    }
    base_events = (
        true[true["is_first_focal_event"].eq(1)][
            [
                "event_id",
                "focal_code",
                "event_date",
                "focal_industry_d",
                "date_m1",
                "date_0",
                "date_p1",
                "specificity_z",
            ]
        ]
        .drop_duplicates("event_id")
        .copy()
    )
    base_events = base_events[base_events["focal_code"].isin(candidates.keys())].copy()
    rng = np.random.default_rng(20260524)
    rows: list[dict[str, object]] = []

    for draw in range(1, draws + 1):
        sampled_rows: list[dict[str, object]] = []
        for ev in base_events.itertuples(index=False):
            pool = candidates.get(ev.focal_code, [])
            if len(pool) < 10:
                continue
            peers = rng.choice(pool, size=10, replace=False)
            for rank, peer in enumerate(peers, start=1):
                sampled_rows.append(
                    {
                        "event_id": ev.event_id,
                        "focal_code": ev.focal_code,
                        "event_date": ev.event_date,
                        "focal_industry_d": ev.focal_industry_d,
                        "date_m1": ev.date_m1,
                        "date_0": ev.date_0,
                        "date_p1": ev.date_p1,
                        "specificity_z": ev.specificity_z,
                        "peer_code": peer,
                        "peer_rank": rank,
                        "peer_industry_d": ev.focal_industry_d,
                        "peer_industry_week": str(ev.focal_industry_d) + "|" + pd.Timestamp(ev.date_0).strftime("%Y-%U"),
                        "product_similarity": np.nan,
                    }
                )
        panel = pd.DataFrame(sampled_rows)
        panel = attach_returns_fast(panel, stock_idx)
        panel = add_ai_active(panel, event_dates_by_code)
        sample = clean_sample(panel, first_only=False)
        for outcome in OUTCOMES:
            for fe_name, fe_cols in [
                ("event_fe", ["event_id"]),
                ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
            ]:
                fitted = fit_absorbed_model(
                    sample,
                    outcome,
                    ["ai_active_peer_tminus5", "specz_ai_active"],
                    fe_cols,
                )
                for row in fitted:
                    if row["term"] != "specz_ai_active":
                        continue
                    row.update({"draw": draw, "outcome": outcome, "fe_spec": fe_name})
                    rows.append(row)
    return pd.DataFrame(rows)


def summarize_random_distribution(random_df: pd.DataFrame, core: pd.DataFrame) -> pd.DataFrame:
    true_key = core[
        core["peer_group"].eq("true_top5")
        & core["sample"].eq("first_focal_event_clean")
        & core["model"].eq("M1")
        & core["term"].eq("specz_ai_active")
    ][["outcome", "fe_spec", "coef"]].rename(columns={"coef": "true_top5_coef"})
    rows: list[dict[str, object]] = []
    for (outcome, fe_spec), sub in random_df.groupby(["outcome", "fe_spec"], sort=False):
        true_coef = true_key[
            true_key["outcome"].eq(outcome) & true_key["fe_spec"].eq(fe_spec)
        ]["true_top5_coef"]
        true_val = float(true_coef.iloc[0]) if len(true_coef) else np.nan
        coefs = sub["coef"].dropna()
        rows.append(
            {
                "outcome": outcome,
                "fe_spec": fe_spec,
                "draws": int(coefs.size),
                "random_mean_coef": float(coefs.mean()),
                "random_p05": float(coefs.quantile(0.05)),
                "random_p50": float(coefs.quantile(0.50)),
                "random_p95": float(coefs.quantile(0.95)),
                "true_top5_coef": true_val,
                "share_random_le_true": float((coefs <= true_val).mean()) if math.isfinite(true_val) else np.nan,
                "share_random_negative_p10": float(((sub["coef"] < 0) & (sub["p"] < 0.10)).mean()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    true, placebo = load_panels()

    print("Running core FE checks...", flush=True)
    core = run_core_models(true, placebo)
    core.to_csv(OUT_DIR / "v6_main_effect_core_hdfe_checks.csv", index=False)

    print(f"Running {RANDOM_DRAWS} repeated random placebo draws...", flush=True)
    random_df = repeated_random_placebo(true, draws=RANDOM_DRAWS)
    random_df.to_csv(OUT_DIR / "v6_main_effect_repeated_random_placebo_draws.csv", index=False)

    random_summary = summarize_random_distribution(random_df, core)
    random_summary.to_csv(OUT_DIR / "v6_main_effect_repeated_random_placebo_summary.csv", index=False)

    key = core[
        core["term"].eq("specz_ai_active")
        & core["sample"].eq("first_focal_event_clean")
        & core["outcome"].isin(OUTCOMES)
    ].copy()
    print(key.to_string(index=False), flush=True)
    print(random_summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
