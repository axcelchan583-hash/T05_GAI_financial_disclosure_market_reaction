#!/usr/bin/env python3
"""Announcement-cleaned repeated random same-industry placebo for v6."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from run_v6_announcement_clean_checks_20260524 import (
    OUTCOMES,
    ROOT,
    attach_announcement_flags,
    base_clean_sample,
    build_announcement_stock_day_flags,
    code6,
    fit_absorbed_model,
)


BASE_DIR = ROOT / "results" / "v6_announcement_clean_checks_20260524"
MM_DIR = ROOT / "results" / "v6_supplement_market_model_placebo_20260524"
OUT_DIR = ROOT / "results" / "v6_announcement_clean_random_placebo_20260524"

TRUE_PANEL = BASE_DIR / "true_peer_market_model_car_panel_with_ann_flags.csv.gz"
STOCK_MODEL = MM_DIR / "stock_returns_with_market_model_params.csv"
PRODUCT_TEXT = ROOT / "results" / "v4_peer_spillover_x_pilot" / "v4_company_product_text_latest.csv"

RANDOM_DRAWS = 100
RANDOM_TOP_N = 5


def load_true_panel() -> pd.DataFrame:
    df = pd.read_csv(TRUE_PANEL, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    for col in ["event_date", "date_m1", "date_0", "date_p1"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["focal_code"] = df["focal_code"].map(code6)
    df["peer_code"] = df["peer_code"].map(code6)
    df["event_week"] = df["date_0"].dt.strftime("%Y-%U")
    df["peer_industry_d"] = df["peer_industry_d"].fillna("UNKNOWN").astype(str)
    df["peer_industry_week"] = df["peer_industry_d"] + "|" + df["event_week"].fillna("")
    return df


def build_stock_lookup() -> pd.DataFrame:
    stock = pd.read_csv(STOCK_MODEL, dtype={"peer_code": str})
    stock["peer_code"] = stock["peer_code"].map(code6)
    stock["date"] = pd.to_datetime(stock["date"], errors="coerce")
    cols = ["ret", "mkt_ret", "trdsta", "limit_status", "alpha_mm", "beta_mm"]
    return stock.set_index(["peer_code", "date"])[cols].sort_index()


def attach_returns(panel: pd.DataFrame, stock_idx: pd.DataFrame) -> pd.DataFrame:
    out = panel.copy()
    for suffix, date_col in [("m1", "date_m1"), ("0", "date_0"), ("p1", "date_p1")]:
        idx = pd.MultiIndex.from_arrays([out["peer_code"], out[date_col]])
        vals = stock_idx[["ret", "mkt_ret", "trdsta", "limit_status"]].reindex(idx).reset_index(drop=True)
        for col in ["ret", "mkt_ret", "trdsta", "limit_status"]:
            out[f"{col}_{suffix}"] = vals[col].to_numpy()
    idx0 = pd.MultiIndex.from_arrays([out["peer_code"], out["date_0"]])
    params = stock_idx[["alpha_mm", "beta_mm"]].reindex(idx0).reset_index(drop=True)
    out["alpha_mm"] = params["alpha_mm"].to_numpy()
    out["beta_mm"] = params["beta_mm"].to_numpy()
    for suffix in ["m1", "0", "p1"]:
        out[f"abret_{suffix}_mm"] = out[f"ret_{suffix}"] - (
            out["alpha_mm"] + out["beta_mm"] * out[f"mkt_ret_{suffix}"]
        )
    out["peer_car_0_p1_mm"] = out[["abret_0_mm", "abret_p1_mm"]].sum(axis=1, min_count=2)
    out["peer_car_m1_p1_mm"] = out[["abret_m1_mm", "abret_0_mm", "abret_p1_mm"]].sum(axis=1, min_count=3)
    out["obs_peer_car_m1_p1_mm"] = out[["abret_m1_mm", "abret_0_mm", "abret_p1_mm"]].notna().sum(axis=1)
    out["normal_trading_m1_p1"] = (
        out[["trdsta_m1", "trdsta_0", "trdsta_p1"]].fillna(-999).astype(int).eq(1).all(axis=1)
    ).astype(int)
    out["no_limit_m1_p1"] = (
        out[["limit_status_m1", "limit_status_0", "limit_status_p1"]].fillna(0).astype(int).eq(0).all(axis=1)
    ).astype(int)
    return out


def load_company_candidates(true: pd.DataFrame) -> dict[str, list[str]]:
    companies = pd.read_csv(PRODUCT_TEXT, dtype={"stock_code": str})
    companies["stock_code"] = companies["stock_code"].map(code6)
    companies["industry_d"] = companies["industry_d"].fillna("").astype(str)
    companies = companies[companies["stock_code"].ne("") & companies["industry_d"].ne("")]
    by_industry = {
        industry: sub["stock_code"].drop_duplicates().tolist()
        for industry, sub in companies.groupby("industry_d", sort=False)
    }
    true_peers = {
        code: set(sub["peer_code"])
        for code, sub in true[["focal_code", "peer_code"]].drop_duplicates().groupby("focal_code")
    }
    focal_industry = (
        true[["focal_code", "focal_industry_d"]]
        .drop_duplicates("focal_code")
        .set_index("focal_code")["focal_industry_d"]
        .to_dict()
    )
    out: dict[str, list[str]] = {}
    for focal_code, industry in focal_industry.items():
        pool = [
            code
            for code in by_industry.get(str(industry), [])
            if code != focal_code and code not in true_peers.get(focal_code, set())
        ]
        if len(pool) >= RANDOM_TOP_N:
            out[focal_code] = pool
    return out


def add_ai_active(panel: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    event_dates_by_code = {
        code: np.array(sorted(sub["event_date"].dropna().unique()), dtype="datetime64[ns]")
        for code, sub in events[["focal_code", "event_date"]].drop_duplicates().groupby("focal_code")
    }
    flags: list[int] = []
    for peer, event_date in zip(panel["peer_code"], panel["event_date"]):
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


def event_base(true: pd.DataFrame, candidates: dict[str, list[str]]) -> pd.DataFrame:
    cols = [
        "event_id",
        "focal_code",
        "event_date",
        "focal_industry_d",
        "date_m1",
        "date_0",
        "date_p1",
        "specificity_z",
    ]
    events = true[true["is_first_focal_event"].eq(1)][cols].drop_duplicates("event_id").copy()
    events = events[events["focal_code"].isin(candidates.keys())].copy()
    return events


def true_top5_clean_results(true: pd.DataFrame) -> pd.DataFrame:
    panel = true[true["peer_rank"].le(5)].copy()
    sample = base_clean_sample(panel)
    sample = sample[sample["either_cleaning_ann"].eq(0)].copy()
    rows: list[dict[str, object]] = []
    for outcome in OUTCOMES:
        for fe_name, fe_cols in [
            ("event_fe", ["event_id"]),
            ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
        ]:
            for row in fit_absorbed_model(
                sample, outcome, ["ai_active_peer_tminus5", "specz_ai_active"], fe_cols
            ):
                if row["term"] == "specz_ai_active":
                    row.update({"peer_group": "true_top5", "sample": "drop_either_cleaning_ann", "fe_spec": fe_name})
                    rows.append(row)
    return pd.DataFrame(rows)


def repeated_random_placebo(true: pd.DataFrame, draws: int = RANDOM_DRAWS) -> pd.DataFrame:
    candidates = load_company_candidates(true)
    events = event_base(true, candidates)
    stock_idx = build_stock_lookup()
    ann_flags = build_announcement_stock_day_flags()
    rng = np.random.default_rng(20260524)
    rows: list[dict[str, object]] = []
    sample_rows: list[dict[str, object]] = []

    for draw in range(1, draws + 1):
        sampled: list[dict[str, object]] = []
        for ev in events.itertuples(index=False):
            pool = candidates.get(ev.focal_code, [])
            if len(pool) < RANDOM_TOP_N:
                continue
            peers = rng.choice(pool, size=RANDOM_TOP_N, replace=False)
            event_week = pd.Timestamp(ev.date_0).strftime("%Y-%U")
            for rank, peer in enumerate(peers, start=1):
                sampled.append(
                    {
                        "event_id": ev.event_id,
                        "focal_code": ev.focal_code,
                        "event_date": ev.event_date,
                        "focal_industry_d": ev.focal_industry_d,
                        "date_m1": ev.date_m1,
                        "date_0": ev.date_0,
                        "date_p1": ev.date_p1,
                        "specificity_z": ev.specificity_z,
                        "is_first_focal_event": 1,
                        "peer_code": peer,
                        "peer_rank": rank,
                        "peer_industry_d": str(ev.focal_industry_d),
                        "peer_industry_week": str(ev.focal_industry_d) + "|" + event_week,
                    }
                )
        panel = pd.DataFrame(sampled)
        panel = attach_returns(panel, stock_idx)
        panel = add_ai_active(panel, true)
        panel = attach_announcement_flags(panel, ann_flags)
        sample0 = base_clean_sample(panel)
        sample = sample0[sample0["either_cleaning_ann"].eq(0)].copy()
        sample_rows.append(
            {
                "draw": draw,
                "obs": len(sample),
                "events": sample["event_id"].nunique(),
                "peer_firms": sample["peer_code"].nunique(),
                "mean_ai_active": sample["ai_active_peer_tminus5"].mean(),
                "mean_car_0_p1_mm": sample["peer_car_0_p1_mm"].mean(),
                "mean_car_m1_p1_mm": sample["peer_car_m1_p1_mm"].mean(),
            }
        )
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
        if draw % 10 == 0:
            print(f"finished random announcement-cleaned placebo draw {draw}/{draws}", flush=True)

    pd.DataFrame(sample_rows).to_csv(OUT_DIR / "v6_announcement_clean_random_placebo_sample_by_draw.csv", index=False)
    return pd.DataFrame(rows)


def summarize_random(random_df: pd.DataFrame, true_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (outcome, fe_spec), sub in random_df.groupby(["outcome", "fe_spec"], sort=False):
        true_match = true_df[true_df["outcome"].eq(outcome) & true_df["fe_spec"].eq(fe_spec)]["coef"]
        true_coef = float(true_match.iloc[0]) if len(true_match) else math.nan
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
                "true_top5_coef": true_coef,
                "share_random_le_true": float((coefs <= true_coef).mean()) if math.isfinite(true_coef) else math.nan,
                "share_random_negative_p10": float(((sub["coef"] < 0) & (sub["p"] < 0.10)).mean()),
                "share_random_negative_p05": float(((sub["coef"] < 0) & (sub["p"] < 0.05)).mean()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    true = load_true_panel()
    true_df = true_top5_clean_results(true)
    true_df.to_csv(OUT_DIR / "v6_announcement_clean_true_top5_reference.csv", index=False)
    random_df = repeated_random_placebo(true, draws=RANDOM_DRAWS)
    random_df.to_csv(OUT_DIR / "v6_announcement_clean_repeated_random_placebo_draws.csv", index=False)
    summary = summarize_random(random_df, true_df)
    summary.to_csv(OUT_DIR / "v6_announcement_clean_repeated_random_placebo_summary.csv", index=False)
    print(true_df.to_string(index=False), flush=True)
    print(summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
