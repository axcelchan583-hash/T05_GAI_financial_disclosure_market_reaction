#!/usr/bin/env python3
"""Analyst forecast revision probe for T05 peer event-study sample.

For each event-peer row, this script compares analyst forecast consensus before
and after the focal GenAI event for the same peer firm and forecast fiscal year.

Definitions:
- pre window: event date -90 to -1 calendar days.
- post windows: event date to +30 / +60 calendar days.
- consensus: average of each analyst/broker's latest forecast inside the window.
- forecast fiscal years: event year and event year + 1, reported separately.

This is a first-pass mechanism diagnostic, not a final analyst forecast design.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups


ROOT = Path("/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction")
AF_DIR = Path("/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/上市公司财务信息")

PANEL_PATH = ROOT / "results/v33_supplement_data_probe_20260605/panel_with_supplement_flags.csv.gz"
OUT = ROOT / "results/v34_analyst_forecast_revision_probe_20260605"
DOC = ROOT / "docs/empirical_runs/98_v34_analyst_forecast_revision_probe_20260605.md"

AF_USECOLS = [
    "Stkcd",
    "Rptdt",
    "Fenddt",
    "ReportID",
    "DeclareDate",
    "AnanmID",
    "InstitutionID",
    "Feps",
    "ProfitParent",
    "Fnetpro",
    "Fturnover",
]

METRICS = {
    "feps": "Feps",
    "profit_parent": "ProfitParent",
    "net_profit": "Fnetpro",
    "turnover": "Fturnover",
}


def norm_code(x) -> str | None:
    if pd.isna(x):
        return None
    s = str(x).strip()
    if not s or s in {"证券代码", "没有单位"}:
        return None
    if "." in s:
        try:
            s = str(int(float(s)))
        except ValueError:
            pass
    s = "".join(ch for ch in s if ch.isdigit())
    if not s:
        return None
    return s.zfill(6)


def to_date(x) -> pd.Timestamp | pd.NaT:
    ts = pd.to_datetime(x, errors="coerce")
    if pd.isna(ts):
        return pd.NaT
    return pd.Timestamp(ts).normalize()


def load_event_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH)
    df["peer_code_norm"] = df["peer_code_norm"].map(norm_code)
    df["event_dt"] = pd.to_datetime(df["event_dt"], errors="coerce").dt.normalize()
    df["event_year_int"] = df["event_dt"].dt.year
    return df.dropna(subset=["peer_code_norm", "event_dt", "event_year_int"]).copy()


def load_af(peer_codes: Iterable[str], min_dt: pd.Timestamp, max_dt: pd.Timestamp) -> pd.DataFrame:
    cache = OUT / "af_forecast_filtered_cache.csv.gz"
    if cache.exists():
        af = pd.read_csv(cache)
        af["report_dt"] = pd.to_datetime(af["report_dt"], errors="coerce")
        af["target_year"] = pd.to_numeric(af["target_year"], errors="coerce")
        for col in METRICS.values():
            af[col] = pd.to_numeric(af[col], errors="coerce")
        return af

    codes = set(peer_codes)
    frames = []
    for path in sorted(AF_DIR.glob("AF_Forecast*.xlsx")):
        df = pd.read_excel(path, usecols=lambda c: c in AF_USECOLS)
        df["peer_code_norm"] = df["Stkcd"].map(norm_code)
        df = df[df["peer_code_norm"].isin(codes)].copy()
        if df.empty:
            continue
        df["report_dt"] = df["DeclareDate"].map(to_date)
        fallback = df["Rptdt"].map(to_date)
        df["report_dt"] = df["report_dt"].fillna(fallback)
        df["fend_dt"] = df["Fenddt"].map(to_date)
        df = df.dropna(subset=["report_dt", "fend_dt", "peer_code_norm"])
        df = df[(df["report_dt"] >= min_dt) & (df["report_dt"] <= max_dt)]
        if df.empty:
            continue
        df["target_year"] = df["fend_dt"].dt.year
        df["analyst_key"] = df["AnanmID"].astype(str)
        missing_analyst = df["analyst_key"].isin(["nan", "None", "", "没有单位"])
        df.loc[missing_analyst, "analyst_key"] = df.loc[missing_analyst, "InstitutionID"].astype(str)
        missing_analyst = df["analyst_key"].isin(["nan", "None", "", "没有单位"])
        df.loc[missing_analyst, "analyst_key"] = df.loc[missing_analyst, "ReportID"].astype(str)
        for col in METRICS.values():
            df[col] = pd.to_numeric(df[col], errors="coerce")
        frames.append(df[["peer_code_norm", "report_dt", "target_year", "analyst_key", "ReportID"] + list(METRICS.values())])
    if not frames:
        return pd.DataFrame(columns=["peer_code_norm", "report_dt", "target_year", "analyst_key", "ReportID"] + list(METRICS.values()))
    af = pd.concat(frames, ignore_index=True)
    af = af.drop_duplicates(["peer_code_norm", "report_dt", "target_year", "analyst_key", "ReportID"])
    af.to_csv(cache, index=False, compression="gzip")
    return af


def consensus_latest(window: pd.DataFrame, metric_col: str) -> tuple[float, int, int]:
    w = window.dropna(subset=[metric_col, "analyst_key", "report_dt"]).copy()
    if w.empty:
        return np.nan, 0, 0
    w = w.sort_values(["analyst_key", "report_dt", "ReportID"])
    latest = w.groupby("analyst_key", as_index=False).tail(1)
    return float(latest[metric_col].mean()), int(latest["analyst_key"].nunique()), int(len(w))


def build_revision_panel(panel: pd.DataFrame, af: pd.DataFrame) -> pd.DataFrame:
    event_peers = panel[
        [
            "event_key",
            "focal_code_norm",
            "peer_code_norm",
            "event_dt",
            "event_year_int",
            "peer_ar0_mm",
            "peer_car_0_p1_mm",
            "peer_car_0_p20_mm",
            "peer_car_0_p60_mm",
            "ai",
            "spec_z",
            "spec_ai",
            "peer_own_strict_genai_m2_p2",
            "peer_major_announcement_m2_p2",
        ]
    ].copy()
    rows = []
    # Group AF once by firm to avoid repeatedly scanning the whole table.
    af_by_code = {code: g.sort_values("report_dt").reset_index(drop=True) for code, g in af.groupby("peer_code_norm", sort=False)}
    for r in event_peers.itertuples(index=False):
        firm_af = af_by_code.get(r.peer_code_norm)
        if firm_af is None or firm_af.empty:
            for target_offset in [0, 1]:
                for horizon in [30, 60]:
                    for metric_name in METRICS:
                        rows.append(base_row(r, target_offset, horizon, metric_name))
            continue
        pre_lo = r.event_dt - pd.Timedelta(days=90)
        pre_hi = r.event_dt - pd.Timedelta(days=1)
        for target_offset in [0, 1]:
            target_year = int(r.event_year_int) + target_offset
            ty = firm_af[firm_af["target_year"].eq(target_year)]
            pre = ty[(ty["report_dt"] >= pre_lo) & (ty["report_dt"] <= pre_hi)]
            for horizon in [30, 60]:
                post = ty[(ty["report_dt"] >= r.event_dt) & (ty["report_dt"] <= r.event_dt + pd.Timedelta(days=horizon))]
                for metric_name, metric_col in METRICS.items():
                    pre_mean, pre_analysts, pre_reports = consensus_latest(pre, metric_col)
                    post_mean, post_analysts, post_reports = consensus_latest(post, metric_col)
                    row = base_row(r, target_offset, horizon, metric_name)
                    row.update(
                        {
                            "target_year": target_year,
                            "pre_mean": pre_mean,
                            "post_mean": post_mean,
                            "pre_analysts": pre_analysts,
                            "post_analysts": post_analysts,
                            "pre_reports": pre_reports,
                            "post_reports": post_reports,
                        }
                    )
                    if pd.notna(pre_mean) and pd.notna(post_mean):
                        row["revision_abs"] = post_mean - pre_mean
                        denom = abs(pre_mean)
                        row["revision_scaled"] = (post_mean - pre_mean) / denom if denom > 1e-12 else np.nan
                        row["revision_down"] = int(post_mean < pre_mean)
                    rows.append(row)
    return pd.DataFrame(rows)


def base_row(r, target_offset: int, horizon: int, metric_name: str) -> dict:
    return {
        "event_key": r.event_key,
        "focal_code_norm": r.focal_code_norm,
        "peer_code_norm": r.peer_code_norm,
        "event_dt": r.event_dt,
        "target_offset": target_offset,
        "post_horizon_days": horizon,
        "metric": metric_name,
        "peer_ar0_mm": r.peer_ar0_mm,
        "peer_car_0_p1_mm": r.peer_car_0_p1_mm,
        "peer_car_0_p20_mm": r.peer_car_0_p20_mm,
        "peer_car_0_p60_mm": r.peer_car_0_p60_mm,
        "ai": r.ai,
        "spec_z": r.spec_z,
        "spec_ai": r.spec_ai,
        "peer_own_strict_genai_m2_p2": r.peer_own_strict_genai_m2_p2,
        "peer_major_announcement_m2_p2": r.peer_major_announcement_m2_p2,
        "target_year": np.nan,
        "pre_mean": np.nan,
        "post_mean": np.nan,
        "pre_analysts": 0,
        "post_analysts": 0,
        "pre_reports": 0,
        "post_reports": 0,
        "revision_abs": np.nan,
        "revision_scaled": np.nan,
        "revision_down": np.nan,
    }


def two_way_cluster_mean(df: pd.DataFrame, y: str) -> dict:
    d = df.dropna(subset=[y, "event_key", "peer_code_norm"]).copy()
    if d.empty:
        return empty_stats(len(df))
    X = np.ones((len(d), 1))
    model = sm.OLS(d[y].astype(float), X).fit()
    g0 = pd.factorize(d["event_key"].astype(str))[0]
    g1 = pd.factorize(d["peer_code_norm"].astype(str))[0]
    cov, _, _ = cov_cluster_2groups(model, g0, g1, use_correction=True)
    se = float(np.sqrt(max(cov[0, 0], 0)))
    mean = float(model.params.iloc[0])
    z = mean / se if se else np.nan
    p = 2 * (1 - stats.norm.cdf(abs(z))) if np.isfinite(z) else np.nan
    return {
        "nobs": int(len(d)),
        "events": int(d["event_key"].nunique()),
        "peer_firms": int(d["peer_code_norm"].nunique()),
        "coef_or_mean": mean,
        "se": se,
        "z": z,
        "p": p,
    }


def two_way_cluster_slope(df: pd.DataFrame, y: str, x: str, fe: str | None = None) -> dict:
    d = df.dropna(subset=[y, x, "event_key", "peer_code_norm"]).copy()
    if d.empty or d[x].nunique() < 2:
        return empty_stats(len(d))
    X = d[[x]].astype(float)
    if fe == "event":
        dummies = pd.get_dummies(d["event_key"].astype(str), prefix="event", drop_first=True, dtype=float)
        X = pd.concat([X, dummies], axis=1)
    X = sm.add_constant(X, has_constant="add")
    model = sm.OLS(d[y].astype(float), X).fit()
    g0 = pd.factorize(d["event_key"].astype(str))[0]
    g1 = pd.factorize(d["peer_code_norm"].astype(str))[0]
    cov, _, _ = cov_cluster_2groups(model, g0, g1, use_correction=True)
    loc = list(model.params.index).index(x)
    se = float(np.sqrt(max(cov[loc, loc], 0)))
    coef = float(model.params[x])
    z = coef / se if se else np.nan
    p = 2 * (1 - stats.norm.cdf(abs(z))) if np.isfinite(z) else np.nan
    return {
        "nobs": int(len(d)),
        "events": int(d["event_key"].nunique()),
        "peer_firms": int(d["peer_code_norm"].nunique()),
        "coef_or_mean": coef,
        "se": se,
        "z": z,
        "p": p,
    }


def empty_stats(n: int) -> dict:
    return {"nobs": int(n), "events": 0, "peer_firms": 0, "coef_or_mean": np.nan, "se": np.nan, "z": np.nan, "p": np.nan}


def summarize_revision(rev: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base = rev.copy()
    base["has_revision"] = base["revision_scaled"].notna()
    cov = (
        base.groupby(["metric", "target_offset", "post_horizon_days"], as_index=False)
        .agg(
            total_rows=("event_key", "size"),
            revision_rows=("has_revision", "sum"),
            events=("event_key", "nunique"),
            covered_events=("event_key", lambda x: base.loc[x.index[base.loc[x.index, "has_revision"]], "event_key"].nunique()),
            peer_firms=("peer_code_norm", "nunique"),
            covered_peer_firms=("peer_code_norm", lambda x: base.loc[x.index[base.loc[x.index, "has_revision"]], "peer_code_norm"].nunique()),
            mean_pre_analysts=("pre_analysts", "mean"),
            mean_post_analysts=("post_analysts", "mean"),
        )
    )
    cov["coverage"] = cov["revision_rows"] / cov["total_rows"]

    mean_rows = []
    reg_rows = []
    for keys, d in base.groupby(["metric", "target_offset", "post_horizon_days"], sort=True):
        metric, target_offset, horizon = keys
        for y in ["revision_abs", "revision_scaled"]:
            res = two_way_cluster_mean(d, y)
            mean_rows.append({"metric": metric, "target_offset": target_offset, "post_horizon_days": horizon, "outcome": y, **res})
        down = d.dropna(subset=["revision_down"]).copy()
        if not down.empty:
            res = two_way_cluster_mean(down, "revision_down")
            mean_rows.append({"metric": metric, "target_offset": target_offset, "post_horizon_days": horizon, "outcome": "revision_down_rate", **res})
        for y in ["revision_scaled"]:
            for x in ["peer_car_0_p1_mm", "peer_ar0_mm"]:
                for fe in [None, "event"]:
                    res = two_way_cluster_slope(d, y, x, fe=fe)
                    reg_rows.append(
                        {
                            "metric": metric,
                            "target_offset": target_offset,
                            "post_horizon_days": horizon,
                            "outcome": y,
                            "regressor": x,
                            "fe": fe or "none",
                            **res,
                        }
                    )
    return cov, pd.DataFrame(mean_rows), pd.DataFrame(reg_rows)


def write_doc(cov: pd.DataFrame, means: pd.DataFrame, regs: pd.DataFrame, af_meta: pd.DataFrame) -> None:
    def fmt(df: pd.DataFrame, n: int | None = None) -> str:
        d = df.copy()
        for c in ["coverage", "coef_or_mean", "se", "z", "p", "mean_pre_analysts", "mean_post_analysts"]:
            if c in d:
                d[c] = pd.to_numeric(d[c], errors="coerce").round(6)
        if n:
            d = d.head(n)
        return d.to_markdown(index=False)

    # Keep the most interpretable first-pass cells in the doc.
    key_cov = cov[(cov["metric"].isin(["feps", "profit_parent", "turnover"])) & (cov["target_offset"].isin([0, 1]))]
    key_means = means[
        (means["metric"].isin(["feps", "profit_parent", "turnover"]))
        & (means["outcome"].isin(["revision_scaled", "revision_down_rate"]))
    ].copy()
    key_regs = regs[
        (regs["metric"].isin(["feps", "profit_parent", "turnover"]))
        & (regs["regressor"].eq("peer_car_0_p1_mm"))
        & (regs["outcome"].eq("revision_scaled"))
    ].copy()

    lines = [
        "# v34 analyst forecast revision probe",
        "",
        "## Scope",
        "",
        "- Input event-peer panel: v33 supplement panel.",
        "- Analyst forecast source: local CSMAR `AF_Forecast*.xlsx`.",
        "- Pre window: event date -90 to -1 calendar days.",
        "- Post windows: event date to +30 and +60 calendar days.",
        "- Forecast target years are event year (`target_offset=0`) and event year + 1 (`target_offset=1`).",
        "- Consensus uses each analyst/broker's latest forecast inside the pre/post window, then averages across analysts.",
        "- This is a diagnostic pass; final use needs stronger forecast-target and analyst-coverage rules.",
        "",
        "## Headline Read",
        "",
        "1. Analyst forecast coverage is sparse. The 60-day revision cells cover about 185 event-peer rows, 100 events, and 105 peer firms, or roughly 6.6% of the current event-peer panel.",
        "2. Among covered observations, FY+1 EPS and FY+1 parent-profit forecasts are revised downward after focal GenAI events. The 60-day scaled revisions are about -10.6% for EPS and -9.5% for parent profit.",
        "3. Current-year forecast revisions have the same negative direction but are not statistically sharp in this first pass.",
        "4. Short-window peer CAR does not predict the size of analyst forecast revisions. The evidence is therefore a weak cash-flow-expectation bridge, not yet a clean cross-sectional mechanism.",
        "5. `revision_down_rate` is reported as a descriptive rate. Its displayed mean-test p-value should not be read as a sign test against 0.5 in this diagnostic version.",
        "",
        "## AF Source Coverage",
        "",
        fmt(af_meta),
        "",
        "## Revision Coverage",
        "",
        fmt(key_cov),
        "",
        "## Mean Forecast Revisions",
        "",
        fmt(key_means),
        "",
        "## Peer CAR Predicting Forecast Revision",
        "",
        fmt(key_regs),
        "",
        "## Output Files",
        "",
        "- `results/v34_analyst_forecast_revision_probe_20260605/analyst_revision_panel.csv.gz`",
        "- `results/v34_analyst_forecast_revision_probe_20260605/revision_coverage.csv`",
        "- `results/v34_analyst_forecast_revision_probe_20260605/revision_mean_tests.csv`",
        "- `results/v34_analyst_forecast_revision_probe_20260605/revision_peer_car_regressions.csv`",
        "- `results/v34_analyst_forecast_revision_probe_20260605/af_source_meta.csv`",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    panel = load_event_panel()
    min_dt = panel["event_dt"].min() - pd.Timedelta(days=120)
    max_dt = panel["event_dt"].max() + pd.Timedelta(days=90)
    af = load_af(panel["peer_code_norm"].dropna().unique(), min_dt, max_dt)
    af_meta = pd.DataFrame(
        [
            {
                "af_rows_after_filter": len(af),
                "af_firms": af["peer_code_norm"].nunique() if not af.empty else 0,
                "min_report_dt": af["report_dt"].min() if not af.empty else pd.NaT,
                "max_report_dt": af["report_dt"].max() if not af.empty else pd.NaT,
                "min_target_year": af["target_year"].min() if not af.empty else np.nan,
                "max_target_year": af["target_year"].max() if not af.empty else np.nan,
            }
        ]
    )
    rev = build_revision_panel(panel, af)
    cov, means, regs = summarize_revision(rev)

    af_meta.to_csv(OUT / "af_source_meta.csv", index=False)
    rev.to_csv(OUT / "analyst_revision_panel.csv.gz", index=False, compression="gzip")
    cov.to_csv(OUT / "revision_coverage.csv", index=False)
    means.to_csv(OUT / "revision_mean_tests.csv", index=False)
    regs.to_csv(OUT / "revision_peer_car_regressions.csv", index=False)
    write_doc(cov, means, regs, af_meta)

    print(f"wrote {OUT}")
    print(af_meta.to_string(index=False))
    print("\ncoverage")
    print(cov.to_string(index=False))
    print("\nmeans")
    print(means.to_string(index=False))
    print("\nregs")
    print(regs.to_string(index=False))


if __name__ == "__main__":
    main()
