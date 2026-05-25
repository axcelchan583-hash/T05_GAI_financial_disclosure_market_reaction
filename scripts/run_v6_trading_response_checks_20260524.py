#!/usr/bin/env python3
"""Trading-activity response checks for the v6 design.

Constructs abnormal log trading value / shares using a rolling pre-event
baseline, then runs the same first-focal-event peer regressions as the CAR
tests.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from run_v6_announcement_clean_checks_20260524 import (
    OUTCOMES,
    ROOT,
    code6,
    fit_absorbed_model,
)


OUT_DIR = ROOT / "results" / "v6_trading_response_checks_20260524"
ANN_CLEAN_DIR = ROOT / "results" / "v6_announcement_clean_checks_20260524"
STOCK_RET_PATH = (
    ROOT
    / "results"
    / "v6_csmar_peer_market_reaction_smoke_20260523"
    / "stock_returns_needed_2021_2026.csv"
)

TRADING_OUTCOMES = [
    "peer_ablog_value_0_p1",
    "peer_ablog_shares_0_p1",
    "peer_ablog_value_m1_p1",
    "peer_ablog_shares_m1_p1",
]
ROLLING_WINDOW = 60
MIN_BASE_OBS = 30
SKIP_DAYS = 11


def build_trading_baseline(refresh: bool = False) -> pd.DataFrame:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cache = OUT_DIR / "stock_trading_activity_baseline.csv.gz"
    if cache.exists() and not refresh:
        out = pd.read_csv(cache, dtype={"peer_code": str})
        out["date"] = pd.to_datetime(out["date"], errors="coerce")
        return out

    stock = pd.read_csv(
        STOCK_RET_PATH,
        usecols=["peer_code", "date", "trading_value", "trading_shares", "trdsta", "limit_status"],
        dtype={"peer_code": str},
    )
    stock["peer_code"] = stock["peer_code"].map(code6)
    stock["date"] = pd.to_datetime(stock["date"], errors="coerce")
    stock["log_value"] = np.log1p(pd.to_numeric(stock["trading_value"], errors="coerce"))
    stock["log_shares"] = np.log1p(pd.to_numeric(stock["trading_shares"], errors="coerce"))
    stock = stock.sort_values(["peer_code", "date"]).reset_index(drop=True)

    def rolling_base(s: pd.Series) -> pd.Series:
        return s.rolling(ROLLING_WINDOW, min_periods=MIN_BASE_OBS).mean().shift(SKIP_DAYS)

    grouped = stock.groupby("peer_code", sort=False)
    stock["base_log_value"] = grouped["log_value"].transform(rolling_base)
    stock["base_log_shares"] = grouped["log_shares"].transform(rolling_base)
    stock["base_obs_value"] = grouped["log_value"].transform(
        lambda s: s.rolling(ROLLING_WINDOW, min_periods=1).count().shift(SKIP_DAYS)
    )
    keep = [
        "peer_code",
        "date",
        "log_value",
        "log_shares",
        "base_log_value",
        "base_log_shares",
        "base_obs_value",
        "trdsta",
        "limit_status",
    ]
    out = stock[keep].copy()
    out.to_csv(cache, index=False, compression="gzip")
    return out


def load_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    for col in ["event_date", "date_m1", "date_0", "date_p1"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["peer_industry_d"] = df["peer_industry_d"].fillna("UNKNOWN").astype(str)
    df["event_week"] = df["date_0"].dt.strftime("%Y-%U")
    df["peer_industry_week"] = df["peer_industry_d"] + "|" + df["event_week"].fillna("")
    return df


def attach_trading(panel: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    out = panel.copy()
    idx_base = base.set_index(["peer_code", "date"]).sort_index()
    cols = ["log_value", "log_shares", "base_log_value", "base_log_shares", "base_obs_value"]
    for suffix, date_col in [("m1", "date_m1"), ("0", "date_0"), ("p1", "date_p1")]:
        idx = pd.MultiIndex.from_arrays([out["peer_code"].astype(str), out[date_col]])
        vals = idx_base[cols].reindex(idx).reset_index(drop=True)
        for col in cols:
            out[f"{col}_{suffix}"] = vals[col].to_numpy()
        out[f"ablog_value_{suffix}"] = out[f"log_value_{suffix}"] - out[f"base_log_value_{suffix}"]
        out[f"ablog_shares_{suffix}"] = out[f"log_shares_{suffix}"] - out[f"base_log_shares_{suffix}"]

    out["peer_ablog_value_0_p1"] = out[["ablog_value_0", "ablog_value_p1"]].mean(axis=1)
    out["peer_ablog_shares_0_p1"] = out[["ablog_shares_0", "ablog_shares_p1"]].mean(axis=1)
    out["peer_ablog_value_m1_p1"] = out[
        ["ablog_value_m1", "ablog_value_0", "ablog_value_p1"]
    ].mean(axis=1)
    out["peer_ablog_shares_m1_p1"] = out[
        ["ablog_shares_m1", "ablog_shares_0", "ablog_shares_p1"]
    ].mean(axis=1)
    out["obs_ablog_m1_p1"] = out[
        ["ablog_value_m1", "ablog_value_0", "ablog_value_p1"]
    ].notna().sum(axis=1)
    return out


def base_sample(df: pd.DataFrame) -> pd.DataFrame:
    return df[
        (df["is_first_focal_event"].eq(1))
        & (df["obs_ablog_m1_p1"].eq(3))
        & (df["normal_trading_m1_p1"].eq(1))
        & (df["no_limit_m1_p1"].eq(1))
    ].copy()


def run_group(panel: pd.DataFrame, peer_group: str, top_n: int) -> tuple[list[dict], list[dict]]:
    sample0 = base_sample(panel)
    samples = [
        ("base_no_announcement_filter", sample0),
        ("drop_either_cleaning_ann", sample0[sample0["either_cleaning_ann"].eq(0)].copy()),
    ]
    fe_specs = [
        ("event_fe", ["event_id"]),
        ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
    ]
    summaries: list[dict] = []
    regs: list[dict] = []
    for sample_name, sample in samples:
        summaries.append(
            {
                "peer_group": peer_group,
                "top_n": top_n,
                "sample": sample_name,
                "obs": len(sample),
                "events": sample["event_id"].nunique(),
                "focal_firms": sample["focal_code"].nunique(),
                "peer_firms": sample["peer_code"].nunique(),
                "mean_ai_active": sample["ai_active_peer_tminus5"].mean(),
                "mean_ablog_value_0_p1": sample["peer_ablog_value_0_p1"].mean(),
                "mean_ablog_shares_0_p1": sample["peer_ablog_shares_0_p1"].mean(),
            }
        )
        for fe_name, fe_cols in fe_specs:
            for outcome in TRADING_OUTCOMES:
                for row in fit_absorbed_model(
                    sample, outcome, ["ai_active_peer_tminus5", "specz_ai_active"], fe_cols
                ):
                    row.update(
                        {
                            "peer_group": peer_group,
                            "top_n": top_n,
                            "sample": sample_name,
                            "fe_spec": fe_name,
                            "model": "M1_specz_x_ai_active",
                        }
                    )
                    regs.append(row)
    return summaries, regs


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base = build_trading_baseline()
    true = load_panel(ANN_CLEAN_DIR / "true_peer_market_model_car_panel_with_ann_flags.csv.gz")
    placebo = load_panel(ANN_CLEAN_DIR / "placebo_peer_market_model_car_panel_with_ann_flags.csv.gz")
    true = attach_trading(true, base)
    placebo = attach_trading(placebo, base)

    summaries: list[dict] = []
    regs: list[dict] = []
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
    for peer_group, panel, top_n in groups:
        s, r = run_group(panel, peer_group, top_n)
        summaries.extend(s)
        regs.extend(r)
    summary = pd.DataFrame(summaries)
    reg = pd.DataFrame(regs)
    summary.to_csv(OUT_DIR / "v6_trading_response_sample_summary.csv", index=False)
    reg.to_csv(OUT_DIR / "v6_trading_response_regressions.csv", index=False)
    key = reg[reg["term"].eq("specz_ai_active")].copy()
    print(summary.to_string(index=False), flush=True)
    print(key.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
