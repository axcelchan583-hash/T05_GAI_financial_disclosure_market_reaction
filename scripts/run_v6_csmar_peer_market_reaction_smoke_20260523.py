#!/usr/bin/env python3
"""v6 smoke test: GenAI disclosure and product-market peer market reaction.

This uses the full CSMAR GenAI event library and the CSMAR product-peer network
to estimate a first-pass market-adjusted peer CAR design. It is intentionally
lighter than a full market-model event study so we can quickly test whether the
v6 main outcome has any signal before optimizing the heavier version.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.sandwich_covariance import cov_cluster, cov_cluster_2groups


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "v6_csmar_peer_market_reaction_smoke_20260523"

EVENT_PATH = (
    ROOT
    / "results"
    / "csmar_v5_1_response_smoke_20260523"
    / "csmar_conservative_focal_events_2023_2026.csv"
)
PEER_PATH = (
    ROOT
    / "results"
    / "csmar_v5_1_response_smoke_20260523"
    / "csmar_product_peer_network_top10.csv"
)

DAILY_DTA_DIR = Path(
    "/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/"
    "上市公司财务信息/_daily_2026_02_14_2026_05_22_patch_dta"
)
INDEX_DTA_PATH = Path(
    "/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/"
    "上市公司财务信息/_idx_2026_02_14_2026_05_22_patch_dta/TRD_Index.dta"
)

START_DATE = pd.Timestamp("2023-01-01")
INDEX_CODE = "000001"


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = re.sub(r"\.0$", "", text)
    text = re.sub(r"\D", "", text)
    return text.zfill(6) if text else ""


def read_events() -> pd.DataFrame:
    events = pd.read_csv(EVENT_PATH, dtype={"focal_code": str, "stock_code": str})
    events["focal_code"] = events["focal_code"].map(code6)
    events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce")
    events["specificity"] = pd.to_numeric(events["specificity"], errors="coerce")
    events = events[
        events["focal_code"].ne("")
        & events["event_date"].notna()
        & events["event_date"].ge(START_DATE)
    ].copy()
    events["event_id"] = events["event_id"].astype(str)
    return events


def read_peer_network() -> pd.DataFrame:
    peers = pd.read_csv(PEER_PATH, dtype={"focal_code": str, "peer_code": str})
    peers["focal_code"] = peers["focal_code"].map(code6)
    peers["peer_code"] = peers["peer_code"].map(code6)
    peers["peer_rank"] = pd.to_numeric(peers["peer_rank"], errors="coerce")
    peers["product_similarity"] = pd.to_numeric(
        peers["product_similarity"], errors="coerce"
    )
    peers = peers[
        peers["focal_code"].ne("")
        & peers["peer_code"].ne("")
        & peers["product_similarity"].notna()
        & peers["peer_rank"].between(1, 10)
    ].copy()
    return peers


def build_event_peer_panel(events: pd.DataFrame, peers: pd.DataFrame) -> pd.DataFrame:
    base_cols = [
        "event_id",
        "focal_code",
        "event_date",
        "specificity",
        "sources",
        "answer_level_events",
        "sample_answer",
    ]
    panel = events[base_cols].merge(peers, on="focal_code", how="inner")
    panel = panel[panel["peer_code"].ne(panel["focal_code"])].copy()
    panel["x_spec_sim"] = panel["specificity"] * panel["product_similarity"]
    return panel


def dta_paths_daily() -> list[Path]:
    return sorted(
        p for p in DAILY_DTA_DIR.glob("TRD_Dalyr*.dta") if "[DES]" not in p.name
    )


def load_stock_returns(target_codes: set[str], refresh: bool = False) -> pd.DataFrame:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cache = OUT_DIR / "stock_returns_needed_2021_2026.csv"
    if cache.exists() and not refresh:
        out = pd.read_csv(cache, dtype={"peer_code": str})
        out["date"] = pd.to_datetime(out["date"])
        return out

    cols = [
        "Stkcd",
        "Trddt",
        "Dretwd",
        "Dretnd",
        "Dnvaltrd",
        "Dnshrtrd",
        "Markettype",
        "Trdsta",
        "LimitStatus",
    ]
    chunks: list[pd.DataFrame] = []
    for path in dta_paths_daily():
        print(f"Reading stock returns: {path.name}", flush=True)
        for chunk in pd.read_stata(path, columns=cols, chunksize=300_000):
            chunk = chunk.copy()
            chunk["peer_code"] = chunk["Stkcd"].map(code6)
            chunk = chunk[chunk["peer_code"].isin(target_codes)].copy()
            if chunk.empty:
                continue
            chunks.append(
                pd.DataFrame(
                    {
                        "peer_code": chunk["peer_code"],
                        "date": pd.to_datetime(chunk["Trddt"], errors="coerce"),
                        "ret": pd.to_numeric(chunk["Dretwd"], errors="coerce"),
                        "ret_nodiv": pd.to_numeric(chunk["Dretnd"], errors="coerce"),
                        "trading_value": pd.to_numeric(
                            chunk["Dnvaltrd"], errors="coerce"
                        ),
                        "trading_shares": pd.to_numeric(
                            chunk["Dnshrtrd"], errors="coerce"
                        ),
                        "market_type": pd.to_numeric(
                            chunk["Markettype"], errors="coerce"
                        ),
                        "trdsta": pd.to_numeric(chunk["Trdsta"], errors="coerce"),
                        "limit_status": pd.to_numeric(
                            chunk["LimitStatus"], errors="coerce"
                        ),
                    }
                )
            )
        print(f"  cached chunks: {len(chunks)}", flush=True)

    if not chunks:
        return pd.DataFrame()
    out = pd.concat(chunks, ignore_index=True)
    out = out.dropna(subset=["peer_code", "date", "ret"])
    out = out.drop_duplicates(["peer_code", "date"]).sort_values(["peer_code", "date"])
    out.to_csv(cache, index=False)
    return out


def load_market_returns() -> pd.DataFrame:
    cache = OUT_DIR / f"market_returns_{INDEX_CODE}.csv"
    if cache.exists():
        out = pd.read_csv(cache)
        out["date"] = pd.to_datetime(out["date"])
        return out

    raw = pd.read_stata(INDEX_DTA_PATH, columns=["Indexcd", "Trddt", "Retindex"])
    raw["index_code"] = raw["Indexcd"].map(code6)
    raw = raw[raw["index_code"].eq(INDEX_CODE)].copy()
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(raw["Trddt"], errors="coerce"),
            "mkt_ret": pd.to_numeric(raw["Retindex"], errors="coerce"),
        }
    )
    out = out.dropna(subset=["date", "mkt_ret"]).drop_duplicates("date")
    out = out.sort_values("date").reset_index(drop=True)
    out.to_csv(cache, index=False)
    return out


def add_event_trading_dates(panel: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:
    trading_dates = np.array(sorted(market["date"].dropna().unique()), dtype="datetime64[ns]")
    event_dates = panel["event_date"].dt.normalize().to_numpy(dtype="datetime64[ns]")
    pos0 = np.searchsorted(trading_dates, event_dates, side="left")
    valid = pos0 < len(trading_dates)
    out = panel.loc[valid].copy()
    pos0 = pos0[valid]
    out["trading_pos"] = pos0

    for offset, col in [(-1, "date_m1"), (0, "date_0"), (1, "date_p1")]:
        pos = pos0 + offset
        ok = (pos >= 0) & (pos < len(trading_dates))
        vals = np.full(len(out), np.datetime64("NaT"), dtype="datetime64[ns]")
        vals[ok] = trading_dates[pos[ok]]
        out[col] = pd.to_datetime(vals)
    return out


def attach_window_returns(panel: pd.DataFrame, stock: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:
    ret = stock.merge(market, on="date", how="inner")
    ret["abret"] = ret["ret"] - ret["mkt_ret"]
    ret = ret[
        [
            "peer_code",
            "date",
            "ret",
            "mkt_ret",
            "abret",
            "trading_value",
            "trading_shares",
            "trdsta",
            "limit_status",
        ]
    ].copy()

    out = panel.copy()
    for suffix, date_col in [("m1", "date_m1"), ("0", "date_0"), ("p1", "date_p1")]:
        tmp = ret.rename(
            columns={
                "date": date_col,
                "ret": f"ret_{suffix}",
                "mkt_ret": f"mkt_ret_{suffix}",
                "abret": f"abret_{suffix}",
                "trading_value": f"trading_value_{suffix}",
                "trading_shares": f"trading_shares_{suffix}",
                "trdsta": f"trdsta_{suffix}",
                "limit_status": f"limit_status_{suffix}",
            }
        )
        out = out.merge(tmp, on=["peer_code", date_col], how="left")

    for cols, outcome in [
        (["abret_0"], "peer_ar0_ma"),
        (["abret_0", "abret_p1"], "peer_car_0_p1_ma"),
        (["abret_m1", "abret_0", "abret_p1"], "peer_car_m1_p1_ma"),
    ]:
        out[f"obs_{outcome}"] = out[cols].notna().sum(axis=1)
        out[outcome] = out[cols].sum(axis=1, min_count=len(cols))

    out["normal_trading_m1_p1"] = (
        out[["trdsta_m1", "trdsta_0", "trdsta_p1"]].fillna(-999).astype(int).eq(1).all(axis=1)
    ).astype(int)
    out["no_limit_m1_p1"] = (
        out[["limit_status_m1", "limit_status_0", "limit_status_p1"]]
        .fillna(0)
        .astype(int)
        .eq(0)
        .all(axis=1)
    ).astype(int)
    return out


def add_pre_event_ai_active(panel: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    event_dates_by_code = {
        code: np.array(sorted(sub["event_date"].dropna().unique()), dtype="datetime64[ns]")
        for code, sub in events.groupby("focal_code", sort=False)
    }
    flags = []
    for peer, event_date in zip(panel["peer_code"], panel["event_date"], strict=False):
        dates = event_dates_by_code.get(peer)
        if dates is None or len(dates) == 0 or pd.isna(event_date):
            flags.append(0)
            continue
        cutoff = np.datetime64((pd.Timestamp(event_date) - pd.Timedelta(days=5)).normalize())
        flags.append(int(np.searchsorted(dates, cutoff, side="right") > 0))

    out = panel.copy()
    out["ai_active_peer_tminus5"] = flags
    out["sim_ai_active"] = out["product_similarity"] * out["ai_active_peer_tminus5"]
    out["x_spec_sim_ai_active"] = out["x_spec_sim"] * out["ai_active_peer_tminus5"]
    return out


def demean_by_event(data: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = data[["event_id", "peer_code", *cols]].copy()
    means = out.groupby("event_id", sort=False)[cols].transform("mean")
    for col in cols:
        out[col] = out[col] - means[col]
    return out


def fit_event_fe(
    data: pd.DataFrame,
    outcome: str,
    xvars: list[str],
    model_name: str,
    top_n: int,
    clean_label: str,
) -> list[dict[str, object]]:
    need = [outcome, *xvars, "event_id", "peer_code"]
    d = data.dropna(subset=need).copy()
    if d.empty:
        return [
            {
                "model": model_name,
                "top_n": top_n,
                "sample": clean_label,
                "outcome": outcome,
                "error": "empty sample",
            }
        ]

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
    covs = {"event_cluster": cov_event, "twoway_event_peer": cov_two}

    rows: list[dict[str, object]] = []
    for cov_name, cov in covs.items():
        se = np.sqrt(np.diag(np.asarray(cov)))
        params = model.params
        for idx, term in enumerate(xvars):
            z = params[idx] / se[idx] if se[idx] > 0 else math.nan
            p = 2 * (1 - stats.norm.cdf(abs(z))) if math.isfinite(z) else math.nan
            rows.append(
                {
                    "model": model_name,
                    "top_n": top_n,
                    "sample": clean_label,
                    "outcome": outcome,
                    "covariance": cov_name,
                    "term": term,
                    "coef": params[idx],
                    "se": se[idx],
                    "z": z,
                    "p": p,
                    "nobs": int(model.nobs),
                    "events": int(d["event_id"].nunique()),
                    "focal_firms": int(d["focal_code"].nunique()) if "focal_code" in d else np.nan,
                    "peer_firms": int(d["peer_code"].nunique()),
                    "mean_y": float(d[outcome].mean()),
                }
            )
    return rows


def summarize_panel(panel: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for top_n in [5, 10]:
        sub = panel[panel["peer_rank"].le(top_n)].copy()
        clean = sub[
            (sub["obs_peer_car_m1_p1_ma"] == 3)
            & (sub["normal_trading_m1_p1"] == 1)
            & (sub["no_limit_m1_p1"] == 1)
        ].copy()
        for label, d in [("raw", sub), ("clean_m1_p1", clean)]:
            rows.append(
                {
                    "top_n": top_n,
                    "sample": label,
                    "obs": len(d),
                    "events": d["event_id"].nunique(),
                    "focal_firms": d["focal_code"].nunique(),
                    "peer_firms": d["peer_code"].nunique(),
                    "mean_ai_active_peer": d["ai_active_peer_tminus5"].mean(),
                    "mean_ar0": d["peer_ar0_ma"].mean(),
                    "mean_car_0_p1": d["peer_car_0_p1_ma"].mean(),
                    "mean_car_m1_p1": d["peer_car_m1_p1_ma"].mean(),
                }
            )
    return pd.DataFrame(rows)


def run_regressions(panel: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    outcomes = ["peer_ar0_ma", "peer_car_0_p1_ma", "peer_car_m1_p1_ma"]
    for top_n in [5, 10]:
        sub = panel[panel["peer_rank"].le(top_n)].copy()
        samples = {
            "raw": sub,
            "clean_m1_p1": sub[
                (sub["obs_peer_car_m1_p1_ma"] == 3)
                & (sub["normal_trading_m1_p1"] == 1)
                & (sub["no_limit_m1_p1"] == 1)
            ].copy(),
        }
        for sample_name, d in samples.items():
            for outcome in outcomes:
                rows.extend(
                    fit_event_fe(
                        d,
                        outcome,
                        [
                            "product_similarity",
                            "ai_active_peer_tminus5",
                            "sim_ai_active",
                        ],
                        "M1_similarity_ai_active",
                        top_n,
                        sample_name,
                    )
                )
                rows.extend(
                    fit_event_fe(
                        d,
                        outcome,
                        [
                            "product_similarity",
                            "ai_active_peer_tminus5",
                            "sim_ai_active",
                            "x_spec_sim",
                            "x_spec_sim_ai_active",
                        ],
                        "M2_plus_specificity",
                        top_n,
                        sample_name,
                    )
                )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    events = read_events()
    peers = read_peer_network()
    panel = build_event_peer_panel(events, peers)
    target_codes = set(panel["peer_code"].dropna().unique())
    print(
        f"Event-peer panel before returns: {len(panel):,} obs, "
        f"{panel['event_id'].nunique():,} events, {len(target_codes):,} peer firms",
        flush=True,
    )

    stock = load_stock_returns(target_codes)
    market = load_market_returns()
    print(
        f"Returns loaded: {len(stock):,} stock-day rows, "
        f"{stock['peer_code'].nunique():,} peer firms; market days={len(market):,}",
        flush=True,
    )

    panel = add_event_trading_dates(panel, market)
    panel = attach_window_returns(panel, stock, market)
    panel = add_pre_event_ai_active(panel, events)
    panel.to_csv(OUT_DIR / "v6_peer_event_market_adjusted_car_panel.csv", index=False)

    summary = summarize_panel(panel)
    summary.to_csv(OUT_DIR / "v6_peer_market_reaction_sample_summary.csv", index=False)

    reg = run_regressions(panel)
    reg.to_csv(OUT_DIR / "v6_peer_market_reaction_event_fe_regressions.csv", index=False)

    print(summary.to_string(index=False), flush=True)
    key = reg[
        reg["covariance"].eq("twoway_event_peer")
        & reg["sample"].eq("clean_m1_p1")
        & reg["term"].isin(["sim_ai_active", "x_spec_sim_ai_active"])
    ].copy()
    print(key.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
