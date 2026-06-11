#!/usr/bin/env python3
"""Mechanism closure checks after v36.

Two small but important checks:

1. Close the focal-peer mirror line with the exact specification requested by
   Claude: no event FE, industry-week FE, event-level cluster, and
   FocalCAR x PeerSimilarity.
2. Re-run the short-window peer main effect in the analyst-covered subsample
   used by v34 analyst forecast revision diagnostics.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.sandwich_covariance import cov_cluster
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups


ROOT = Path("/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction")
OUT = ROOT / "results/v37_mechanism_closure_20260605"
DOC = ROOT / "docs/empirical_runs/101_v37_mechanism_closure_20260605.md"

V33_PANEL = ROOT / "results/v33_supplement_data_probe_20260605/panel_with_supplement_flags.csv.gz"
V31_PANEL = ROOT / "results/v31_pom_analog_cross_section_20260605/analysis_panel_pom_analog.csv.gz"
V34_REVISION = ROOT / "results/v34_analyst_forecast_revision_probe_20260605/analyst_revision_panel.csv.gz"


def zscore(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    sd = x.std(ddof=0)
    if not sd or pd.isna(sd):
        return x * np.nan
    return (x - x.mean()) / sd


def p_norm(z: float) -> float:
    return 2 * (1 - stats.norm.cdf(abs(z))) if np.isfinite(z) else np.nan


def stars(p: object) -> str:
    if p is None or pd.isna(p):
        return ""
    p = float(p)
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def fmt(x: object, digits: int = 4) -> str:
    if x is None or pd.isna(x):
        return ""
    return f"{float(x):.{digits}f}"


def load_two_component_panel() -> pd.DataFrame:
    df = pd.read_csv(V33_PANEL)
    cols = [
        "event_key",
        "peer_code",
        "peer_industry_hhi_z",
        "peer_sales_growth_z",
        "peer_log_revenue_z",
        "peer_gross_margin_z",
        "product_distance_z",
    ]
    v31 = pd.read_csv(V31_PANEL, usecols=lambda c: c in cols)
    v31 = v31.drop_duplicates(["event_key", "peer_code"])
    df = df.merge(v31, on=["event_key", "peer_code"], how="left")
    df["peer_similarity_z"] = zscore(df["peer_similarity"])
    df["focal_car_z"] = zscore(df["focal_car_0_p1_mm"])
    df["focal_x_similarity"] = df["focal_car_z"] * df["peer_similarity_z"]
    df["ai"] = pd.to_numeric(df["ai"], errors="coerce")
    return df


def fit_ols_cluster(
    df: pd.DataFrame,
    dep: str,
    xvars: list[str],
    fe_cols: list[str],
    cluster: str = "event",
) -> dict[str, object]:
    needed = [dep, *xvars, *fe_cols, "event_key", "peer_code_norm"]
    d = df.dropna(subset=needed).copy()
    X = d[xvars].astype(float)
    for fe in fe_cols:
        X = pd.concat([X, pd.get_dummies(d[fe].astype(str), prefix=fe, drop_first=True, dtype=float)], axis=1)
    X = sm.add_constant(X, has_constant="add")
    y = d[dep].astype(float)
    model = sm.OLS(y, X).fit()
    if cluster == "event":
        g = pd.factorize(d["event_key"].astype(str))[0]
        cov = cov_cluster(model, g, use_correction=True)
    elif cluster == "event_peer":
        g0 = pd.factorize(d["event_key"].astype(str))[0]
        g1 = pd.factorize(d["peer_code_norm"].astype(str))[0]
        cov, _, _ = cov_cluster_2groups(model, g0, g1, use_correction=True)
    else:
        raise ValueError(cluster)
    se = pd.Series(np.sqrt(np.maximum(np.diag(cov), 0)), index=model.params.index)
    out: dict[str, object] = {
        "nobs": int(len(d)),
        "events": int(d["event_key"].nunique()),
        "peer_firms": int(d["peer_code_norm"].nunique()),
        "overall_r2": float(model.rsquared),
        "cluster": cluster,
    }
    for x in xvars:
        b = float(model.params.get(x, np.nan))
        sx = float(se.get(x, np.nan))
        z = b / sx if sx and np.isfinite(sx) else np.nan
        out[f"{x}_coef"] = b
        out[f"{x}_se"] = sx
        out[f"{x}_z"] = z
        out[f"{x}_p"] = p_norm(z)
    return out


def focal_peer_closure(panel: pd.DataFrame) -> pd.DataFrame:
    controls = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm", "peer_rank", "ai"]
    xvars = ["focal_car_z", "peer_similarity_z", "focal_x_similarity", *controls]
    samples = {
        "all": pd.Series(True, index=panel.index),
        "drop_peer_genai_or_major": ~(
            panel["peer_own_strict_genai_m2_p2"].fillna(False)
            | panel["peer_major_announcement_m2_p2"].fillna(False)
        ),
    }
    fe_variants = {
        "peer_industry_week": ["peer_industry_week"],
        "focal_industry_week": ["focal_industry_week"],
    }
    rows = []
    for sample, mask in samples.items():
        d = panel[mask].copy()
        for fe_name, fe_cols in fe_variants.items():
            for cluster in ["event", "event_peer"]:
                res = fit_ols_cluster(d, "peer_car_0_p1_mm", xvars, fe_cols, cluster=cluster)
                rows.append(
                    {
                        "sample": sample,
                        "outcome": "PeerCAR[0,+1]",
                        "fe": fe_name,
                        "test": "FocalCAR x PeerSimilarity",
                        **res,
                    }
                )
    return pd.DataFrame(rows)


def two_way_cluster_mean(df: pd.DataFrame, y: str) -> dict[str, object]:
    d = df.dropna(subset=[y, "event_key", "peer_code_norm"]).copy()
    if d.empty:
        return {
            "nobs": 0,
            "events": 0,
            "peer_firms": 0,
            "mean": np.nan,
            "se": np.nan,
            "z": np.nan,
            "p": np.nan,
            "median": np.nan,
            "positive_rate": np.nan,
        }
    X = np.ones((len(d), 1))
    model = sm.OLS(d[y].astype(float), X).fit()
    g0 = pd.factorize(d["event_key"].astype(str))[0]
    g1 = pd.factorize(d["peer_code_norm"].astype(str))[0]
    cov, _, _ = cov_cluster_2groups(model, g0, g1, use_correction=True)
    se = float(np.sqrt(max(cov[0, 0], 0)))
    mean = float(model.params.iloc[0])
    z = mean / se if se else np.nan
    return {
        "nobs": int(len(d)),
        "events": int(d["event_key"].nunique()),
        "peer_firms": int(d["peer_code_norm"].nunique()),
        "mean": mean,
        "se": se,
        "z": z,
        "p": p_norm(z),
        "median": float(d[y].median()),
        "positive_rate": float((d[y] > 0).mean()),
    }


def analyst_coverage_main_effects() -> pd.DataFrame:
    rev = pd.read_csv(V34_REVISION)
    rev["event_dt"] = pd.to_datetime(rev["event_dt"], errors="coerce")
    for col in [
        "peer_ar0_mm",
        "peer_car_0_p1_mm",
        "peer_car_0_p20_mm",
        "peer_car_0_p60_mm",
        "revision_scaled",
    ]:
        rev[col] = pd.to_numeric(rev[col], errors="coerce")
    base = rev[
        rev["metric"].eq("feps")
        & rev["target_offset"].eq(1)
        & rev["post_horizon_days"].eq(60)
    ].drop_duplicates(["event_key", "peer_code_norm"]).copy()
    coverage_defs = {
        "fy1_feps_60d": rev[
            rev["metric"].eq("feps")
            & rev["target_offset"].eq(1)
            & rev["post_horizon_days"].eq(60)
            & rev["revision_scaled"].notna()
        ],
        "fy1_profit_parent_60d": rev[
            rev["metric"].eq("profit_parent")
            & rev["target_offset"].eq(1)
            & rev["post_horizon_days"].eq(60)
            & rev["revision_scaled"].notna()
        ],
        "fy1_feps_or_parent_60d": rev[
            rev["metric"].isin(["feps", "profit_parent"])
            & rev["target_offset"].eq(1)
            & rev["post_horizon_days"].eq(60)
            & rev["revision_scaled"].notna()
        ],
        "fy1_any_metric_60d": rev[
            rev["target_offset"].eq(1)
            & rev["post_horizon_days"].eq(60)
            & rev["revision_scaled"].notna()
        ],
    }
    outcomes = [
        ("PeerAR[0]", "peer_ar0_mm"),
        ("PeerCAR[0,+1]", "peer_car_0_p1_mm"),
        ("PeerCAR[0,+20]", "peer_car_0_p20_mm"),
        ("PeerCAR[0,+60]", "peer_car_0_p60_mm"),
    ]
    rows = []
    full_stats = {label: two_way_cluster_mean(base, col) for label, col in outcomes}
    for label, stats0 in full_stats.items():
        rows.append({"sample": "all_v34_base", "coverage_rows": len(base), "outcome": label, **stats0})
    for name, cov_rows in coverage_defs.items():
        keys = cov_rows[["event_key", "peer_code_norm"]].drop_duplicates()
        covered = base.merge(keys, on=["event_key", "peer_code_norm"], how="inner")
        uncovered = base.merge(keys.assign(_covered=1), on=["event_key", "peer_code_norm"], how="left")
        uncovered = uncovered[uncovered["_covered"].isna()].drop(columns=["_covered"])
        for label, col in outcomes:
            rows.append({"sample": name, "coverage_rows": len(covered), "outcome": label, **two_way_cluster_mean(covered, col)})
            rows.append({"sample": f"not_{name}", "coverage_rows": len(uncovered), "outcome": label, **two_way_cluster_mean(uncovered, col)})
    return pd.DataFrame(rows)


def coef_text(row: pd.Series, var: str) -> str:
    b = row.get(f"{var}_coef")
    p = row.get(f"{var}_p")
    return f"{fmt(b)}{stars(p)}"


def se_text(row: pd.Series, var: str) -> str:
    return f"({fmt(row.get(f'{var}_se'))})"


def write_doc(focal: pd.DataFrame, analyst: pd.DataFrame) -> None:
    exact = focal[
        focal["sample"].eq("all")
        & focal["fe"].eq("peer_industry_week")
        & focal["cluster"].eq("event")
    ].iloc[0]
    focal_tbl = focal[
        [
            "sample",
            "fe",
            "cluster",
            "nobs",
            "events",
            "peer_firms",
            "focal_car_z_coef",
            "focal_car_z_p",
            "focal_x_similarity_coef",
            "focal_x_similarity_se",
            "focal_x_similarity_p",
        ]
    ].copy()
    focal_tbl["FocalCAR"] = focal_tbl["focal_car_z_coef"].map(fmt)
    focal_tbl["FocalCAR p"] = focal_tbl["focal_car_z_p"].map(fmt)
    focal_tbl["FocalCAR x Similarity"] = [
        f"{fmt(r.focal_x_similarity_coef)}{stars(r.focal_x_similarity_p)}"
        for r in focal_tbl.itertuples(index=False)
    ]
    focal_tbl["se"] = focal_tbl["focal_x_similarity_se"].map(lambda x: f"({fmt(x)})")
    focal_tbl["interaction_p"] = focal_tbl["focal_x_similarity_p"].map(fmt)
    focal_tbl = focal_tbl[
        [
            "sample",
            "fe",
            "cluster",
            "FocalCAR",
            "FocalCAR p",
            "FocalCAR x Similarity",
            "se",
            "interaction_p",
            "nobs",
            "events",
            "peer_firms",
        ]
    ]
    analyst_key = analyst[
        analyst["sample"].isin(["fy1_feps_or_parent_60d", "not_fy1_feps_or_parent_60d", "fy1_feps_60d", "fy1_profit_parent_60d"])
        & analyst["outcome"].isin(["PeerAR[0]", "PeerCAR[0,+1]"])
    ].copy()
    analyst_key["mean_fmt"] = [f"{fmt(r.mean)}{stars(r.p)}" for r in analyst_key.itertuples(index=False)]
    analyst_key["se_fmt"] = analyst_key["se"].map(lambda x: f"({fmt(x)})")
    analyst_key["p_fmt"] = analyst_key["p"].map(fmt)
    analyst_key = analyst_key[
        [
            "sample",
            "outcome",
            "mean_fmt",
            "se_fmt",
            "p_fmt",
            "nobs",
            "events",
            "peer_firms",
            "positive_rate",
        ]
    ]
    verdict_focal = (
        "The exact no-event-FE focal-peer mirror closure does not support a negative competition-gradient: "
        f"`FocalCAR x PeerSimilarity` = {fmt(exact['focal_x_similarity_coef'])}, "
        f"p={fmt(exact['focal_x_similarity_p'])}."
    )
    covered = analyst[
        analyst["sample"].eq("fy1_feps_or_parent_60d")
        & analyst["outcome"].eq("PeerCAR[0,+1]")
    ].iloc[0]
    verdict_analyst = (
        f"In the FY+1 EPS-or-parent-profit analyst-covered subsample, PeerCAR[0,+1] = "
        f"{fmt(covered['mean'])}{stars(covered['p'])}, p={fmt(covered['p'])}, "
        f"N={int(covered['nobs'])}, events={int(covered['events'])}."
    )
    lines = [
        "# v37 mechanism closure checks",
        "",
        "## Scope",
        "",
        "- First check: exact focal-peer mirror closure, no event FE, industry-week FE, event-level cluster.",
        "- Second check: peer event-study main effect in analyst-covered subsamples from v34.",
        "- Main analyst coverage definition: FY+1 EPS or parent-profit revision observed within post 60 days.",
        "",
        "## Verdict",
        "",
        f"1. {verdict_focal}",
        f"2. {verdict_analyst}",
        "3. Implication: focal-peer mirror should be closed as exploratory/null. The analyst-covered sample keeps a negative CAR[0,+1] direction, but the small covered N means this is supporting evidence, not a new main test.",
        "",
        "## Focal-Peer Mirror Closure",
        "",
        focal_tbl.to_markdown(index=False),
        "",
        "## Analyst-Covered Main Effect",
        "",
        analyst_key.to_markdown(index=False),
        "",
        "## Output Files",
        "",
        "- `results/v37_mechanism_closure_20260605/focal_peer_exact_closure.csv`",
        "- `results/v37_mechanism_closure_20260605/analyst_covered_main_effects.csv`",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    panel = load_two_component_panel()
    focal = focal_peer_closure(panel)
    analyst = analyst_coverage_main_effects()
    focal.to_csv(OUT / "focal_peer_exact_closure.csv", index=False)
    analyst.to_csv(OUT / "analyst_covered_main_effects.csv", index=False)
    write_doc(focal, analyst)
    print(f"wrote {OUT}")
    print("\nFocal-peer exact closure:")
    print(
        focal[
            [
                "sample",
                "fe",
                "cluster",
                "nobs",
                "events",
                "peer_firms",
                "focal_car_z_coef",
                "focal_car_z_p",
                "focal_x_similarity_coef",
                "focal_x_similarity_se",
                "focal_x_similarity_p",
            ]
        ].to_string(index=False)
    )
    print("\nAnalyst-covered main effect:")
    print(
        analyst[
            analyst["sample"].isin(["fy1_feps_or_parent_60d", "fy1_feps_60d", "fy1_profit_parent_60d"])
            & analyst["outcome"].isin(["PeerAR[0]", "PeerCAR[0,+1]"])
        ][
            [
                "sample",
                "outcome",
                "nobs",
                "events",
                "peer_firms",
                "mean",
                "se",
                "p",
                "positive_rate",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
