#!/usr/bin/env python3
"""Stacked event-DID for AI supply-chain GenAI disclosures.

Treatment is focal-event level: whether the focal firm's GenAI disclosure is
coded as AI supply-chain exposure. The outcome is peer daily market-model
abnormal return around the focal event. This is a diagnostic branch and does
not replace the v6 headline Specificity x AIActive peer-revaluation design.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from run_v6_identification_strengthening_checks_20260524 import fit_absorbed


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "v7_ai_supply_chain_stacked_did_20260527"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "58_v7_ai_supply_chain_stacked_did_20260527.md"

TOP5_SUPPLY_PATH = (
    ROOT
    / "results"
    / "v7_ai_supply_chain_disclosure_diagnostic_20260527"
    / "analysis_sample_top5_with_supply_chain_codes.csv.gz"
)
LOW_SIM_PANEL_PATH = (
    ROOT
    / "results"
    / "v6_external_ai_active_checks_20260524"
    / "placebo_panel_with_external_ai_active.csv.gz"
)
EVENT_CODES_PATH = (
    ROOT
    / "results"
    / "v7_ai_supply_chain_disclosure_diagnostic_20260527"
    / "all_focal_events_supply_chain_codes.csv"
)
RETURNS_PATH = (
    ROOT
    / "results"
    / "v6_supplement_market_model_placebo_20260524"
    / "stock_returns_with_market_model_params.csv"
)


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    digits = "".join(ch for ch in text if ch.isdigit())
    return digits.zfill(6) if digits else ""


def ensure_base_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["event_id"] = out["event_id"].astype(str)
    out["focal_code"] = out["focal_code"].map(code6)
    out["peer_code"] = out["peer_code"].map(code6)
    out["date_0"] = pd.to_datetime(out["date_0"], errors="coerce")
    out["ai_supply_chain_exposure"] = (
        pd.to_numeric(out["ai_supply_chain_exposure"], errors="coerce").fillna(0).astype(int)
    )
    return out.dropna(subset=["event_id", "peer_code", "date_0"]).drop_duplicates(
        ["event_id", "peer_code"]
    )


def load_true_top5() -> pd.DataFrame:
    df = pd.read_csv(TOP5_SUPPLY_PATH, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    df = df[df["peer_rank"].le(5)].copy()
    df["peer_set"] = "true_top5"
    df["true_peer"] = 1
    return ensure_base_columns(df)


def load_low_similarity(event_ids: set[str]) -> pd.DataFrame:
    usecols = [
        "event_id",
        "focal_code",
        "event_date",
        "focal_name",
        "focal_industry_d",
        "trading_pos",
        "date_0",
        "peer_group",
        "peer_rank",
        "peer_code",
        "peer_name",
        "peer_industry_d",
        "product_similarity",
        "same_industry_d",
        "is_first_focal_event",
        "normal_trading_m1_p1",
        "no_limit_m1_p1",
        "obs_peer_car_m1_p1_mm",
        "either_cleaning_ann",
    ]
    low = pd.read_csv(
        LOW_SIM_PANEL_PATH,
        usecols=lambda c: c in set(usecols),
        dtype={"event_id": str, "focal_code": str, "peer_code": str},
    )
    low = low[
        low["event_id"].isin(event_ids)
        & low["peer_group"].eq("low_similarity_same_industry")
        & low["peer_rank"].le(5)
        & low["is_first_focal_event"].eq(1)
        & low["normal_trading_m1_p1"].eq(1)
        & low["no_limit_m1_p1"].eq(1)
        & low["obs_peer_car_m1_p1_mm"].eq(3)
        & low["either_cleaning_ann"].eq(0)
    ].copy()

    codes = pd.read_csv(
        EVENT_CODES_PATH,
        usecols=[
            "event_id",
            "ai_supply_chain_exposure",
            "supply_subtype_count",
            "own_genai_implementation_regex",
            "generic_ai_attention_regex",
        ],
        dtype={"event_id": str},
    ).drop_duplicates("event_id")
    low = low.merge(codes, on="event_id", how="left")
    low["peer_set"] = "low_similarity_same_industry"
    low["true_peer"] = 0
    return ensure_base_columns(low)


def load_returns_for_panel(base: pd.DataFrame, taus: range) -> pd.DataFrame:
    codes = set(base["peer_code"].dropna().map(code6))
    min_date = base["date_0"].min() + pd.tseries.offsets.BDay(min(taus) - 5)
    max_date = base["date_0"].max() + pd.tseries.offsets.BDay(max(taus) + 5)

    chunks: list[pd.DataFrame] = []
    usecols = [
        "peer_code",
        "date",
        "ret",
        "mkt_ret",
        "trdsta",
        "limit_status",
        "alpha_mm",
        "beta_mm",
        "est_obs",
    ]
    for chunk in pd.read_csv(RETURNS_PATH, usecols=usecols, chunksize=1_000_000):
        chunk["peer_code"] = chunk["peer_code"].map(code6)
        chunk = chunk[chunk["peer_code"].isin(codes)]
        if chunk.empty:
            continue
        chunk["date"] = pd.to_datetime(chunk["date"], errors="coerce")
        chunk = chunk[(chunk["date"] >= min_date) & (chunk["date"] <= max_date)]
        if chunk.empty:
            continue
        for col in ["ret", "mkt_ret", "trdsta", "limit_status", "alpha_mm", "beta_mm", "est_obs"]:
            chunk[col] = pd.to_numeric(chunk[col], errors="coerce")
        chunk["abret_mm"] = chunk["ret"] - (chunk["alpha_mm"] + chunk["beta_mm"] * chunk["mkt_ret"])
        chunk = chunk[
            chunk["abret_mm"].notna()
            & chunk["trdsta"].eq(1)
            & chunk["limit_status"].fillna(0).eq(0)
            & chunk["alpha_mm"].notna()
            & chunk["beta_mm"].notna()
        ].copy()
        chunks.append(chunk[["peer_code", "date", "abret_mm", "ret", "mkt_ret", "est_obs"]])

    if not chunks:
        return pd.DataFrame(columns=["peer_code", "date", "abret_mm", "ret", "mkt_ret", "est_obs"])
    ret = pd.concat(chunks, ignore_index=True).drop_duplicates(["peer_code", "date"])
    return ret.sort_values(["peer_code", "date"])


def make_daily_panel(base: pd.DataFrame, returns: pd.DataFrame, taus: range) -> pd.DataFrame:
    lookup: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for code, sub in returns.groupby("peer_code", sort=False):
        sub = sub.sort_values("date")
        lookup[code] = (
            sub["date"].to_numpy(dtype="datetime64[ns]"),
            sub["abret_mm"].to_numpy(dtype=float),
        )

    rows: list[dict[str, object]] = []
    keep_cols = [
        "event_id",
        "focal_code",
        "focal_name",
        "focal_industry_d",
        "peer_code",
        "peer_name",
        "peer_industry_d",
        "peer_rank",
        "product_similarity",
        "same_industry_d",
        "date_0",
        "ai_supply_chain_exposure",
        "supply_subtype_count",
        "own_genai_implementation_regex",
        "generic_ai_attention_regex",
        "peer_set",
        "true_peer",
    ]
    for rec in base[keep_cols].itertuples(index=False):
        recd = rec._asdict()
        code = code6(recd["peer_code"])
        item = lookup.get(code)
        if item is None:
            continue
        dates, abrets = item
        date0 = np.datetime64(pd.Timestamp(recd["date_0"]).normalize())
        pos0 = int(np.searchsorted(dates, date0, side="left"))
        if pos0 >= len(dates) or dates[pos0] != date0:
            continue
        pair_id = f"{recd['event_id']}|{code}|{recd['peer_set']}"
        for tau in taus:
            pos = pos0 + tau
            if pos < 0 or pos >= len(dates):
                continue
            val = abrets[pos]
            if not np.isfinite(val):
                continue
            rows.append(
                {
                    **recd,
                    "peer_code": code,
                    "pair_id": pair_id,
                    "tau": int(tau),
                    "date": pd.Timestamp(dates[pos]),
                    "date_str": str(pd.Timestamp(dates[pos]).date()),
                    "post01": int(tau in (0, 1)),
                    "post010": int(tau >= 0),
                    "abret_mm": float(val),
                }
            )
    daily = pd.DataFrame(rows)
    if daily.empty:
        return daily
    daily["supply"] = daily["ai_supply_chain_exposure"].fillna(0).astype(float)
    daily["true_peer"] = daily["true_peer"].fillna(0).astype(float)
    daily["tau_fe"] = daily["tau"].astype(str)
    daily["supply_post01"] = daily["supply"] * daily["post01"]
    daily["supply_post010"] = daily["supply"] * daily["post010"]
    daily["true_post01"] = daily["true_peer"] * daily["post01"]
    daily["supply_true"] = daily["supply"] * daily["true_peer"]
    daily["supply_true_post01"] = daily["supply"] * daily["true_peer"] * daily["post01"]
    daily["event_week"] = pd.to_datetime(daily["date_0"]).dt.strftime("%Y-%U")
    return daily


def run_models(daily_true: pd.DataFrame, daily_low: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    # Main DID: treatment event versus non-treatment event, around event day.
    true_main = daily_true[daily_true["tau"].between(-10, 1)].copy()
    specs = [
        ("top5_pair_tau_fe", true_main, ["supply_post01"], ["pair_id", "tau_fe"], "supply_post01"),
        (
            "top5_pair_tau_calendar_date_fe",
            true_main,
            ["supply_post01"],
            ["pair_id", "tau_fe", "date_str"],
            "supply_post01",
        ),
    ]

    # Pre-trend placebo: only pre-event days, fake post is [-5,-2].
    pre = daily_true[daily_true["tau"].between(-10, -2)].copy()
    pre["fake_post_m5_m2"] = pre["tau"].between(-5, -2).astype(int)
    pre["supply_fake_post_m5_m2"] = pre["supply"] * pre["fake_post_m5_m2"]
    specs.extend(
        [
            (
                "pretrend_placebo_m5_m2_pair_tau_fe",
                pre,
                ["supply_fake_post_m5_m2"],
                ["pair_id", "tau_fe"],
                "supply_fake_post_m5_m2",
            ),
            (
                "pretrend_placebo_m5_m2_pair_tau_calendar_date_fe",
                pre,
                ["supply_fake_post_m5_m2"],
                ["pair_id", "tau_fe", "date_str"],
                "supply_fake_post_m5_m2",
            ),
        ]
    )

    # Formal close-peer DDD: true Top5 versus low-similarity same-industry placebo peers.
    both = pd.concat([daily_true, daily_low], ignore_index=True, sort=False)
    both_main = both[both["tau"].between(-10, 1)].copy()
    specs.extend(
        [
            (
                "ddd_true_top5_vs_low_sim_pair_tau_fe",
                both_main,
                ["supply_post01", "true_post01", "supply_true_post01"],
                ["pair_id", "tau_fe"],
                "supply_true_post01",
            ),
            (
                "ddd_true_top5_vs_low_sim_pair_tau_calendar_date_fe",
                both_main,
                ["supply_post01", "true_post01", "supply_true_post01"],
                ["pair_id", "tau_fe", "date_str"],
                "supply_true_post01",
            ),
        ]
    )

    # Low-similarity placebo alone.
    low_main = daily_low[daily_low["tau"].between(-10, 1)].copy()
    specs.extend(
        [
            ("low_sim_pair_tau_fe", low_main, ["supply_post01"], ["pair_id", "tau_fe"], "supply_post01"),
            (
                "low_sim_pair_tau_calendar_date_fe",
                low_main,
                ["supply_post01"],
                ["pair_id", "tau_fe", "date_str"],
                "supply_post01",
            ),
        ]
    )

    for model, data, xvars, fe_cols, focus in specs:
        fit_rows = fit_absorbed(
            data,
            "abret_mm",
            xvars,
            fe_cols,
            model=model,
            term_focus=focus,
        )
        for row in fit_rows:
            row["fe"] = "+".join(fe_cols)
            row["window"] = "tau[-10,+1]" if "pretrend" not in model else "tau[-10,-2]"
            row["two_day_equivalent"] = row["coef"] * 2 if focus.endswith("post01") else math.nan
            rows.append(row)
    return pd.DataFrame(rows)


def run_dynamic(daily: pd.DataFrame, prefix: str) -> pd.DataFrame:
    d = daily[daily["tau"].between(-10, 10)].copy()
    base_tau = -2
    xvars = []
    for tau in range(-10, 11):
        if tau == base_tau:
            continue
        col = f"supply_tau_{tau:+d}".replace("+", "p").replace("-", "m")
        d[col] = d["supply"] * d["tau"].eq(tau).astype(float)
        xvars.append(col)
    rows = fit_absorbed(
        d,
        "abret_mm",
        xvars,
        ["pair_id", "tau_fe"],
        model=f"{prefix}_dynamic_pair_tau_fe_base_m2",
        term_focus=None,
    )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["tau"] = out["term"].str.extract(r"supply_tau_([mp]\d+)")[0].map(
        lambda x: int(x.replace("p", "").replace("m", "-")) if isinstance(x, str) else np.nan
    )
    out["base_tau"] = base_tau
    return out.sort_values("tau")


def summarize_sample(name: str, panel: pd.DataFrame) -> dict[str, object]:
    return {
        "panel": name,
        "daily_obs": int(len(panel)),
        "event_peer_pairs": int(panel["pair_id"].nunique()) if not panel.empty else 0,
        "events": int(panel["event_id"].nunique()) if not panel.empty else 0,
        "peer_firms": int(panel["peer_code"].nunique()) if not panel.empty else 0,
        "treated_events": int(panel.loc[panel["supply"].eq(1), "event_id"].nunique()) if not panel.empty else 0,
        "treated_pair_share": float(
            panel.drop_duplicates("pair_id")["supply"].mean()
        )
        if not panel.empty
        else math.nan,
        "mean_daily_abret": float(panel["abret_mm"].mean()) if not panel.empty else math.nan,
    }


def md_table(df: pd.DataFrame, cols: list[str] | None = None, digits: int = 4) -> str:
    if df.empty:
        return "_No rows._"
    out = df.copy()
    if cols is not None:
        out = out[cols]
    for col in out.select_dtypes(include=[np.number]).columns:
        out[col] = out[col].map(lambda x: round(float(x), digits) if pd.notna(x) else x)
    return out.to_markdown(index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Loading base panels...", flush=True)
    true = load_true_top5()
    low = load_low_similarity(set(true["event_id"]))
    base_all = pd.concat([true, low], ignore_index=True, sort=False)

    taus = range(-10, 11)
    print("Loading daily returns for needed peer codes...", flush=True)
    returns = load_returns_for_panel(base_all, taus)
    returns.to_csv(OUT_DIR / "needed_peer_daily_abret_mm.csv.gz", index=False, compression="gzip")

    print("Building stacked daily panels...", flush=True)
    daily_true = make_daily_panel(true, returns, taus)
    daily_low = make_daily_panel(low, returns, taus)
    daily_true.to_csv(OUT_DIR / "stacked_daily_true_top5.csv.gz", index=False, compression="gzip")
    daily_low.to_csv(OUT_DIR / "stacked_daily_low_similarity.csv.gz", index=False, compression="gzip")

    print("Running DID models...", flush=True)
    main_results = run_models(daily_true, daily_low)
    dynamic = run_dynamic(daily_true, "true_top5")

    sample_summary = pd.DataFrame(
        [
            summarize_sample("true_top5", daily_true),
            summarize_sample("low_similarity_same_industry", daily_low),
        ]
    )

    main_results.to_csv(OUT_DIR / "stacked_did_main_results.csv", index=False)
    dynamic.to_csv(OUT_DIR / "stacked_did_dynamic_true_top5.csv", index=False)
    sample_summary.to_csv(OUT_DIR / "stacked_did_sample_summary.csv", index=False)

    doc = f"""# V7 AI Supply-Chain Disclosure Stacked Event-DID

Date: 2026-05-27

## Purpose

This run tests a DID-style version of the AI supply-chain branch:

`DailyPeerAR_{{j,tau}} = beta * AI_supply_chain_event_i * Post[0,+1] + pair FE + event-time FE + error`

The treatment is focal-event level. The outcome is peer daily market-model abnormal return. The primary window is trading days `[-10,+1]`, where `Post[0,+1]` equals one on event day and the next trading day. Standard errors are two-way clustered by focal event and peer firm through the existing v6 regression utility.

This is a diagnostic, not the headline v6 `Specificity_z x AIActivePeer` design.

## Sample

{md_table(sample_summary)}

## Main DID Results

`coef` is the daily abnormal-return effect on `Post[0,+1]`. `two_day_equivalent` is `2 * coef`, roughly comparable to a two-day CAR effect.

{md_table(main_results, ["model", "term", "coef", "se", "z", "p", "two_day_equivalent", "nobs", "events", "peer_firms", "fe"])}

## Dynamic Lead-Lag Check

Coefficients are `AI_supply_chain_event x event_time_tau`, with tau = -2 as the omitted base day, pair FE and event-time FE.

{md_table(dynamic, ["tau", "coef", "se", "z", "p", "nobs", "events", "peer_firms"])}

## Interpretation Guide

- A positive and significant Top5 DID coefficient means AI supply-chain GenAI disclosures are followed by positive close-peer abnormal returns relative to the same pair's pre-event days.
- A null pretrend placebo is required for a defensible DID interpretation.
- A positive Top5 result that does not appear in low-similarity peers supports a product-market network interpretation.
- A weak or wrong-signed DDD means the result is closer to broad category validation than a close-competitor-specific effect.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")
    print(f"Wrote {DOC_PATH}", flush=True)
    print(f"Wrote outputs under {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
