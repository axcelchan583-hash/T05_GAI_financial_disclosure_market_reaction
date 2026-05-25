#!/usr/bin/env python3
"""v6 supplementary tests: market-model CAR and placebo peers.

Supplements the simple main-effect design:
    Specificity_z x AIActivePeer -> peer CAR

This script:
1. Recomputes peer abnormal returns using rolling market-model alpha/beta.
2. Builds same-industry low-similarity and random-peer placebo networks.
3. Runs the same focal-event FE regressions for true peers and placebo peers.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "v6_supplement_market_model_placebo_20260524"

TRUE_PANEL_PATH = (
    ROOT
    / "results"
    / "v6_csmar_peer_market_reaction_smoke_20260523"
    / "v6_peer_event_market_adjusted_car_panel.csv"
)
STOCK_RET_PATH = (
    ROOT
    / "results"
    / "v6_csmar_peer_market_reaction_smoke_20260523"
    / "stock_returns_needed_2021_2026.csv"
)
MARKET_RET_PATH = (
    ROOT
    / "results"
    / "v6_csmar_peer_market_reaction_smoke_20260523"
    / "market_returns_000001.csv"
)
PRODUCT_TEXT_PATH = (
    ROOT
    / "results"
    / "v4_peer_spillover_x_pilot"
    / "v4_company_product_text_latest.csv"
)

OUTCOMES_MM = ["peer_ar0_mm", "peer_car_0_p1_mm", "peer_car_m1_p1_mm"]
ROLLING_WINDOW = 200
MIN_ESTIMATION_OBS = 120
SKIP_DAYS = 11


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = re.sub(r"\.0$", "", text)
    text = re.sub(r"\D", "", text)
    return text.zfill(6) if text else ""


def load_true_panel() -> pd.DataFrame:
    cols = [
        "event_id",
        "focal_code",
        "event_date",
        "specificity",
        "focal_name",
        "focal_industry_d",
        "peer_rank",
        "peer_code",
        "peer_name",
        "peer_industry_d",
        "product_similarity",
        "same_industry_d",
        "trading_pos",
        "date_m1",
        "date_0",
        "date_p1",
        "ret_m1",
        "mkt_ret_m1",
        "trdsta_m1",
        "limit_status_m1",
        "ret_0",
        "mkt_ret_0",
        "trdsta_0",
        "limit_status_0",
        "ret_p1",
        "mkt_ret_p1",
        "trdsta_p1",
        "limit_status_p1",
        "normal_trading_m1_p1",
        "no_limit_m1_p1",
        "obs_peer_car_m1_p1_ma",
        "ai_active_peer_tminus5",
    ]
    panel = pd.read_csv(
        TRUE_PANEL_PATH,
        usecols=cols,
        dtype={"event_id": str, "focal_code": str, "peer_code": str},
    )
    for col in ["event_date", "date_m1", "date_0", "date_p1"]:
        panel[col] = pd.to_datetime(panel[col], errors="coerce")
    panel["focal_code"] = panel["focal_code"].map(code6)
    panel["peer_code"] = panel["peer_code"].map(code6)
    for col in [
        "specificity",
        "peer_rank",
        "product_similarity",
        "ai_active_peer_tminus5",
        "trading_pos",
    ]:
        panel[col] = pd.to_numeric(panel[col], errors="coerce")
    panel["peer_group"] = "true_top10"
    return panel


def add_first_and_specificity(panel: pd.DataFrame) -> pd.DataFrame:
    events = (
        panel[["focal_code", "event_id", "event_date", "specificity"]]
        .drop_duplicates()
        .sort_values(["focal_code", "event_date", "event_id"])
    )
    first_ids = set(events.groupby("focal_code", sort=False).first()["event_id"])
    event_spec = events[["event_id", "specificity"]].drop_duplicates()
    lo = event_spec["specificity"].quantile(0.01)
    hi = event_spec["specificity"].quantile(0.99)
    spec_w = event_spec["specificity"].clip(lo, hi)
    spec_map = dict(zip(event_spec["event_id"], spec_w, strict=False))
    mean = float(spec_w.mean())
    std = float(spec_w.std())

    out = panel.copy()
    out["is_first_focal_event"] = out["event_id"].isin(first_ids).astype(int)
    out["specificity_w"] = out["event_id"].map(spec_map)
    out["specificity_z"] = (out["specificity_w"] - mean) / std
    out["specz_ai_active"] = out["specificity_z"] * out["ai_active_peer_tminus5"]
    return out


def load_stock_model_params(refresh: bool = False) -> pd.DataFrame:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cache = OUT_DIR / "stock_returns_with_market_model_params.csv"
    if cache.exists() and not refresh:
        out = pd.read_csv(cache, dtype={"peer_code": str})
        out["date"] = pd.to_datetime(out["date"])
        return out

    stock = pd.read_csv(STOCK_RET_PATH, dtype={"peer_code": str})
    market = pd.read_csv(MARKET_RET_PATH)
    stock["peer_code"] = stock["peer_code"].map(code6)
    stock["date"] = pd.to_datetime(stock["date"], errors="coerce")
    market["date"] = pd.to_datetime(market["date"], errors="coerce")
    market["mkt_ret"] = pd.to_numeric(market["mkt_ret"], errors="coerce")
    stock["ret"] = pd.to_numeric(stock["ret"], errors="coerce")
    ret = stock.merge(market, on="date", how="inner")
    ret = ret.dropna(subset=["peer_code", "date", "ret", "mkt_ret"])
    ret = ret.sort_values(["peer_code", "date"]).reset_index(drop=True)
    ret["ret_x_mkt"] = ret["ret"] * ret["mkt_ret"]
    ret["mkt_sq"] = ret["mkt_ret"] ** 2

    def roll_shift(s: pd.Series) -> pd.Series:
        return s.rolling(ROLLING_WINDOW, min_periods=MIN_ESTIMATION_OBS).mean().shift(SKIP_DAYS)

    grouped = ret.groupby("peer_code", sort=False)
    ret["mean_ret_est"] = grouped["ret"].transform(roll_shift)
    ret["mean_mkt_est"] = grouped["mkt_ret"].transform(roll_shift)
    ret["mean_ret_mkt_est"] = grouped["ret_x_mkt"].transform(roll_shift)
    ret["mean_mkt_sq_est"] = grouped["mkt_sq"].transform(roll_shift)
    ret["est_obs"] = grouped["ret"].transform(
        lambda s: s.rolling(ROLLING_WINDOW, min_periods=1).count().shift(SKIP_DAYS)
    )
    cov = ret["mean_ret_mkt_est"] - ret["mean_ret_est"] * ret["mean_mkt_est"]
    var = ret["mean_mkt_sq_est"] - ret["mean_mkt_est"] ** 2
    ret["beta_mm"] = cov / var.replace(0, np.nan)
    ret["alpha_mm"] = ret["mean_ret_est"] - ret["beta_mm"] * ret["mean_mkt_est"]
    keep = [
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
    out = ret[keep].copy()
    out.to_csv(cache, index=False)
    return out


def add_market_model_car(panel: pd.DataFrame, stock_model: pd.DataFrame) -> pd.DataFrame:
    params = stock_model[["peer_code", "date", "alpha_mm", "beta_mm", "est_obs"]].rename(
        columns={"date": "date_0"}
    )
    out = panel.merge(params, on=["peer_code", "date_0"], how="left")
    for suffix in ["m1", "0", "p1"]:
        out[f"abret_{suffix}_mm"] = out[f"ret_{suffix}"] - (
            out["alpha_mm"] + out["beta_mm"] * out[f"mkt_ret_{suffix}"]
        )
    out["peer_ar0_mm"] = out["abret_0_mm"]
    out["peer_car_0_p1_mm"] = out[["abret_0_mm", "abret_p1_mm"]].sum(axis=1, min_count=2)
    out["peer_car_m1_p1_mm"] = out[["abret_m1_mm", "abret_0_mm", "abret_p1_mm"]].sum(
        axis=1, min_count=3
    )
    out["obs_peer_car_m1_p1_mm"] = out[
        ["abret_m1_mm", "abret_0_mm", "abret_p1_mm"]
    ].notna().sum(axis=1)
    return out


def build_placebo_networks(true_panel: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    cache = OUT_DIR / "placebo_peer_networks_low_random.csv"
    if cache.exists():
        return pd.read_csv(cache, dtype={"focal_code": str, "peer_code": str})

    companies = pd.read_csv(PRODUCT_TEXT_PATH, dtype={"stock_code": str})
    companies["stock_code"] = companies["stock_code"].map(code6)
    companies["product_text"] = companies["product_text"].fillna("").astype(str)
    companies["industry_d"] = companies["industry_d"].fillna("").astype(str)
    companies = companies[companies["stock_code"].ne("") & companies["product_text"].ne("")]
    companies = companies.drop_duplicates("stock_code").reset_index(drop=True)

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 4),
        min_df=2,
        max_df=0.85,
        max_features=50000,
        sublinear_tf=True,
        norm="l2",
    )
    matrix = normalize(vectorizer.fit_transform(companies["product_text"]), norm="l2", copy=False)
    code_to_idx = {code: idx for idx, code in enumerate(companies["stock_code"])}
    true_peers = {
        code: set(sub["peer_code"])
        for code, sub in true_panel[["focal_code", "peer_code"]].drop_duplicates().groupby("focal_code")
    }
    focal_codes = sorted(true_panel["focal_code"].dropna().unique())
    rows: list[dict[str, object]] = []

    for focal_code in focal_codes:
        focal_idx = code_to_idx.get(focal_code)
        if focal_idx is None:
            continue
        focal_row = companies.iloc[focal_idx]
        industry = focal_row["industry_d"]
        if not industry:
            continue
        candidate_mask = companies["industry_d"].eq(industry).to_numpy()
        candidate_mask[focal_idx] = False
        candidate_idx = np.where(candidate_mask)[0]
        if len(candidate_idx) < top_n:
            continue
        sims = (matrix[focal_idx] @ matrix[candidate_idx].T).toarray().ravel()
        cand = pd.DataFrame(
            {
                "idx": candidate_idx,
                "peer_code": companies.iloc[candidate_idx]["stock_code"].to_numpy(),
                "product_similarity": sims,
            }
        )
        cand = cand[~cand["peer_code"].isin(true_peers.get(focal_code, set()))].copy()
        if len(cand) < top_n:
            continue

        low = cand.sort_values("product_similarity", ascending=True).head(top_n).copy()
        seed = int(focal_code[-5:]) if focal_code[-5:].isdigit() else 20260524
        random = cand.sample(n=top_n, random_state=seed).copy()
        for group, sub in [("low_similarity_same_industry", low), ("random_same_industry", random)]:
            for rank, row in enumerate(sub.itertuples(index=False), start=1):
                peer_row = companies.iloc[int(row.idx)]
                rows.append(
                    {
                        "focal_code": focal_code,
                        "peer_group": group,
                        "peer_rank": rank,
                        "peer_code": row.peer_code,
                        "peer_name": peer_row["company_name"],
                        "peer_industry_d": peer_row["industry_d"],
                        "product_similarity": float(row.product_similarity),
                        "same_industry_d": 1,
                    }
                )

    out = pd.DataFrame(rows)
    out.to_csv(cache, index=False)
    return out


def make_placebo_panel(true_panel: pd.DataFrame, placebo_network: pd.DataFrame) -> pd.DataFrame:
    event_cols = [
        "event_id",
        "focal_code",
        "event_date",
        "specificity",
        "focal_name",
        "focal_industry_d",
        "trading_pos",
        "date_m1",
        "date_0",
        "date_p1",
    ]
    events = true_panel[event_cols].drop_duplicates("event_id")
    panel = events.merge(placebo_network, on="focal_code", how="inner")
    return panel


def attach_window_returns(panel: pd.DataFrame, stock_model: pd.DataFrame) -> pd.DataFrame:
    out = panel.copy()
    ret_cols = ["peer_code", "date", "ret", "mkt_ret", "trdsta", "limit_status"]
    ret = stock_model[ret_cols].copy()
    for suffix, date_col in [("m1", "date_m1"), ("0", "date_0"), ("p1", "date_p1")]:
        tmp = ret.rename(
            columns={
                "date": date_col,
                "ret": f"ret_{suffix}",
                "mkt_ret": f"mkt_ret_{suffix}",
                "trdsta": f"trdsta_{suffix}",
                "limit_status": f"limit_status_{suffix}",
            }
        )
        out = out.merge(tmp, on=["peer_code", date_col], how="left")
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


def add_ai_active_flag(panel: pd.DataFrame, true_panel: pd.DataFrame) -> pd.DataFrame:
    events = (
        true_panel[["focal_code", "event_date"]]
        .drop_duplicates()
        .sort_values(["focal_code", "event_date"])
    )
    by_code = {
        code: np.array(sorted(sub["event_date"].dropna().unique()), dtype="datetime64[ns]")
        for code, sub in events.groupby("focal_code", sort=False)
    }
    flags: list[int] = []
    for peer, event_date in zip(panel["peer_code"], panel["event_date"], strict=False):
        dates = by_code.get(peer)
        if dates is None or len(dates) == 0 or pd.isna(event_date):
            flags.append(0)
            continue
        cutoff = np.datetime64((pd.Timestamp(event_date) - pd.Timedelta(days=5)).normalize())
        flags.append(int(np.searchsorted(dates, cutoff, side="right") > 0))
    out = panel.copy()
    out["ai_active_peer_tminus5"] = flags
    return out


def add_first_and_spec_from_true(panel: pd.DataFrame, true_augmented: pd.DataFrame) -> pd.DataFrame:
    event_meta = true_augmented[
        ["event_id", "is_first_focal_event", "specificity_w", "specificity_z"]
    ].drop_duplicates("event_id")
    out = panel.merge(event_meta, on="event_id", how="left")
    out["specz_ai_active"] = out["specificity_z"] * out["ai_active_peer_tminus5"]
    return out


def clean_sample(panel: pd.DataFrame) -> pd.DataFrame:
    return panel[
        (panel["obs_peer_car_m1_p1_mm"] == 3)
        & (panel["normal_trading_m1_p1"] == 1)
        & (panel["no_limit_m1_p1"] == 1)
        & panel["alpha_mm"].notna()
        & panel["beta_mm"].notna()
    ].copy()


def demean_by_event(data: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = data[["event_id", "peer_code", *cols]].copy()
    means = out.groupby("event_id", sort=False)[cols].transform("mean")
    for col in cols:
        out[col] = out[col] - means[col]
    return out


def fit_event_fe(data: pd.DataFrame, outcome: str, xvars: list[str]) -> list[dict[str, object]]:
    d = data.dropna(subset=[outcome, *xvars, "event_id", "peer_code"]).copy()
    if d.empty:
        return []
    dm = demean_by_event(d, [outcome, *xvars])
    model = sm.OLS(dm[outcome].to_numpy(), dm[xvars].to_numpy()).fit()
    cov_two, _, _ = cov_cluster_2groups(
        model,
        pd.Categorical(dm["event_id"]).codes,
        pd.Categorical(dm["peer_code"]).codes,
    )
    se = np.sqrt(np.diag(np.asarray(cov_two)))
    rows: list[dict[str, object]] = []
    for idx, term in enumerate(xvars):
        z = model.params[idx] / se[idx] if se[idx] > 0 else math.nan
        p = 2 * (1 - stats.norm.cdf(abs(z))) if math.isfinite(z) else math.nan
        rows.append(
            {
                "outcome": outcome,
                "term": term,
                "coef": float(model.params[idx]),
                "se": float(se[idx]),
                "z": float(z),
                "p": float(p),
                "nobs": int(model.nobs),
                "events": int(d["event_id"].nunique()),
                "focal_firms": int(d["focal_code"].nunique()),
                "peer_firms": int(d["peer_code"].nunique()),
                "mean_y": float(d[outcome].mean()),
                "mean_ai_active": float(d["ai_active_peer_tminus5"].mean()),
            }
        )
    return rows


def summarize(panel: pd.DataFrame, peer_group: str, sample_name: str, top_n: int) -> dict[str, object]:
    d = clean_sample(panel)
    return {
        "peer_group": peer_group,
        "sample_name": sample_name,
        "top_n": top_n,
        "obs": len(d),
        "events": d["event_id"].nunique(),
        "focal_firms": d["focal_code"].nunique(),
        "peer_firms": d["peer_code"].nunique(),
        "mean_ai_active": d["ai_active_peer_tminus5"].mean(),
        "mean_car_0_p1_mm": d["peer_car_0_p1_mm"].mean(),
        "mean_car_m1_p1_mm": d["peer_car_m1_p1_mm"].mean(),
        "mean_product_similarity": d["product_similarity"].mean(),
    }


def run_models(panel: pd.DataFrame, peer_group: str, sample_name: str, top_n: int) -> list[dict[str, object]]:
    d = clean_sample(panel)
    rows: list[dict[str, object]] = []
    for outcome in OUTCOMES_MM:
        for model_name, xvars in [
            ("M1_specz_x_ai_active", ["ai_active_peer_tminus5", "specz_ai_active"]),
            (
                "M2_plus_similarity_control",
                ["ai_active_peer_tminus5", "specz_ai_active", "product_similarity"],
            ),
        ]:
            for row in fit_event_fe(d, outcome, xvars):
                row.update(
                    {
                        "peer_group": peer_group,
                        "sample_name": sample_name,
                        "top_n": top_n,
                        "model": model_name,
                    }
                )
                rows.append(row)
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading true panel...", flush=True)
    true_panel = load_true_panel()
    true_aug = add_first_and_specificity(true_panel)

    print("Loading/building market-model parameters...", flush=True)
    stock_model = load_stock_model_params()

    print("Adding market-model CAR to true peers...", flush=True)
    true_mm = add_market_model_car(true_aug, stock_model)
    true_mm.to_csv(OUT_DIR / "true_peer_market_model_car_panel.csv", index=False)

    print("Building placebo peer networks...", flush=True)
    placebo_network = build_placebo_networks(true_panel)
    placebo_panel = make_placebo_panel(true_panel, placebo_network)
    placebo_panel = attach_window_returns(placebo_panel, stock_model)
    placebo_panel = add_ai_active_flag(placebo_panel, true_panel)
    placebo_panel = add_first_and_spec_from_true(placebo_panel, true_aug)
    placebo_panel = add_market_model_car(placebo_panel, stock_model)
    placebo_panel.to_csv(OUT_DIR / "placebo_peer_market_model_car_panel.csv", index=False)

    summary_rows: list[dict[str, object]] = []
    reg_rows: list[dict[str, object]] = []
    for peer_group, panel in [
        ("true_top5", true_mm[true_mm["peer_rank"].le(5)].copy()),
        ("true_top10", true_mm[true_mm["peer_rank"].le(10)].copy()),
        (
            "low_similarity_same_industry",
            placebo_panel[placebo_panel["peer_group"].eq("low_similarity_same_industry")].copy(),
        ),
        (
            "random_same_industry",
            placebo_panel[placebo_panel["peer_group"].eq("random_same_industry")].copy(),
        ),
    ]:
        top_n = 5 if peer_group == "true_top5" else 10
        for sample_name, sub in [
            ("all_events", panel),
            ("first_focal_event", panel[panel["is_first_focal_event"].eq(1)].copy()),
        ]:
            summary_rows.append(summarize(sub, peer_group, sample_name, top_n))
            reg_rows.extend(run_models(sub, peer_group, sample_name, top_n))

    summary = pd.DataFrame(summary_rows)
    regs = pd.DataFrame(reg_rows)
    summary.to_csv(OUT_DIR / "v6_supplement_sample_summary.csv", index=False)
    regs.to_csv(OUT_DIR / "v6_supplement_regressions.csv", index=False)

    key = regs[
        regs["sample_name"].eq("first_focal_event")
        & regs["term"].eq("specz_ai_active")
        & regs["outcome"].isin(["peer_car_0_p1_mm", "peer_car_m1_p1_mm"])
    ].copy()
    print(summary.to_string(index=False), flush=True)
    print(key.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
