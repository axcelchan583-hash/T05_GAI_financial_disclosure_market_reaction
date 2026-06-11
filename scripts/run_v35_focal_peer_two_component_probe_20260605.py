#!/usr/bin/env python3
"""Focal-peer two-component decomposition probe.

Motivation:
The raw focal-peer CAR relation can contain both:
1. a common / contagion component: focal and peers move together;
2. a competitive component: the comovement is weaker or negative for more
   exposed product-market peers.

This script estimates:

PeerCAR_{e,j} = b1 FocalCAR_e + b2 FocalCAR_e x Prox_{e,j}
                + b3 Prox_{e,j} + controls + FE + eps.

It also estimates event-FE versions for peer-level Prox, where FocalCAR itself
is absorbed but FocalCAR x Prox remains identified within event.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups


ROOT = Path("/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction")
OUT = ROOT / "results/v35_focal_peer_two_component_probe_20260605"
DOC = ROOT / "docs/empirical_runs/99_v35_focal_peer_two_component_probe_20260605.md"

PANEL_PATH = ROOT / "results/v33_supplement_data_probe_20260605/panel_with_supplement_flags.csv.gz"
V31_PATH = ROOT / "results/v31_pom_analog_cross_section_20260605/analysis_panel_pom_analog.csv.gz"


def zscore(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    sd = x.std(ddof=0)
    if not sd or pd.isna(sd):
        return x * np.nan
    return (x - x.mean()) / sd


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH)
    v31_cols = [
        "event_key",
        "peer_code",
        "peer_industry_hhi_z",
        "peer_sales_growth_z",
        "peer_log_revenue_z",
        "peer_gross_margin_z",
        "product_distance_z",
    ]
    v31 = pd.read_csv(V31_PATH, usecols=lambda c: c in v31_cols)
    v31 = v31.drop_duplicates(["event_key", "peer_code"])
    df = df.merge(v31, on=["event_key", "peer_code"], how="left")
    df["peer_similarity_z"] = zscore(df["peer_similarity"])
    df["top3_peer"] = (pd.to_numeric(df["peer_rank"], errors="coerce") <= 3).astype(float)
    df["focal_car_z"] = zscore(df["focal_car_0_p1_mm"])
    df["focal_ar0_z"] = zscore(df["focal_ar0_mm"])
    df["ai"] = pd.to_numeric(df["ai"], errors="coerce")
    df["spec_z"] = pd.to_numeric(df["spec_z"], errors="coerce")
    df["event_year"] = pd.to_datetime(df["event_dt"], errors="coerce").dt.year.astype("Int64").astype(str)
    return df


def fit_ols(
    df: pd.DataFrame,
    dep: str,
    xvars: list[str],
    fe_cols: list[str],
    cluster_cols: tuple[str, str] = ("event_key", "peer_code_norm"),
) -> dict:
    needed = [dep, *xvars, *fe_cols, *cluster_cols]
    d = df.dropna(subset=needed).copy()
    if d.empty:
        return {"nobs": 0, "events": 0, "peer_firms": 0, "overall_r2": np.nan, "within_r2": np.nan}
    X = d[xvars].astype(float)
    for fe in fe_cols:
        dum = pd.get_dummies(d[fe].astype(str), prefix=fe, drop_first=True, dtype=float)
        X = pd.concat([X, dum], axis=1)
    X = sm.add_constant(X, has_constant="add")
    y = d[dep].astype(float)
    model = sm.OLS(y, X).fit()
    g0 = pd.factorize(d[cluster_cols[0]].astype(str))[0]
    g1 = pd.factorize(d[cluster_cols[1]].astype(str))[0]
    cov, _, _ = cov_cluster_2groups(model, g0, g1, use_correction=True)
    se = pd.Series(np.sqrt(np.maximum(np.diag(cov), 0)), index=model.params.index)
    rows = {}
    for x in xvars:
        b = float(model.params.get(x, np.nan))
        sx = float(se.get(x, np.nan))
        z = b / sx if sx and np.isfinite(sx) else np.nan
        p = 2 * (1 - stats.norm.cdf(abs(z))) if np.isfinite(z) else np.nan
        rows[f"{x}_coef"] = b
        rows[f"{x}_se"] = sx
        rows[f"{x}_z"] = z
        rows[f"{x}_p"] = p
    # Within R2 approximation: residualize y and modeled fitted component on FE.
    within_r2 = np.nan
    if fe_cols:
        try:
            y_res = residualize_on_fe(d, dep, fe_cols)
            X_small = d[xvars].astype(float)
            for col in X_small:
                X_small[col] = residualize_series_on_fe(d, col, fe_cols)
            m2 = sm.OLS(y_res, X_small).fit()
            within_r2 = float(m2.rsquared)
        except Exception:
            within_r2 = np.nan
    return {
        "nobs": int(len(d)),
        "events": int(d["event_key"].nunique()),
        "peer_firms": int(d["peer_code_norm"].nunique()),
        "overall_r2": float(model.rsquared),
        "within_r2": within_r2,
        **rows,
    }


def residualize_series_on_fe(df: pd.DataFrame, col: str, fe_cols: list[str]) -> pd.Series:
    X = pd.DataFrame(index=df.index)
    for fe in fe_cols:
        X = pd.concat([X, pd.get_dummies(df[fe].astype(str), prefix=fe, drop_first=True, dtype=float)], axis=1)
    X = sm.add_constant(X, has_constant="add")
    return sm.OLS(df[col].astype(float), X).fit().resid


def residualize_on_fe(df: pd.DataFrame, col: str, fe_cols: list[str]) -> pd.Series:
    return residualize_series_on_fe(df, col, fe_cols)


def run_models(panel: pd.DataFrame) -> pd.DataFrame:
    samples = {
        "all": pd.Series(True, index=panel.index),
        "drop_genai_or_major": ~(
            panel["peer_own_strict_genai_m2_p2"].fillna(False)
            | panel["peer_major_announcement_m2_p2"].fillna(False)
        ),
    }
    outcomes = {
        "PeerCAR[0,+1]": ("peer_car_0_p1_mm", "focal_car_z"),
        "PeerAR[0]": ("peer_ar0_mm", "focal_ar0_z"),
    }
    prox_specs = [
        ("peer_similarity_z", "competition", "continuous product similarity"),
        ("top3_peer", "competition", "top-3 product peer"),
        ("ai", "competition", "AI-active peer"),
        ("peer_industry_hhi_z", "competition", "peer industry HHI"),
        ("spec_z", "event_signal", "event disclosure specificity"),
    ]
    base_controls = [
        "peer_car_pre10_m2_mm",
        "peer_car_pre20_m2_mm",
        "peer_rank",
        "peer_similarity_z",
        "ai",
    ]
    rows = []
    for sample_name, mask in samples.items():
        d0 = panel[mask].copy()
        for outcome_label, (dep, focal_var) in outcomes.items():
            for prox, prox_type, prox_label in prox_specs:
                interaction = f"{focal_var}_x_{prox}"
                d = d0.copy()
                d[interaction] = d[focal_var] * pd.to_numeric(d[prox], errors="coerce")
                if prox == "spec_z":
                    # Spec is event-level. Its interaction with focal CAR is also
                    # event-level, so event FE would absorb it.
                    fe_variants = [
                        ("no_event_fe_peer_industry_week", ["peer_industry_week"]),
                        ("no_event_fe_focal_industry_week", ["focal_industry_week"]),
                    ]
                else:
                    fe_variants = [
                        ("no_event_fe_peer_industry_week", ["peer_industry_week"]),
                        ("event_fe", ["event_key"]),
                    ]
                for fe_name, fe_cols in fe_variants:
                    controls = [c for c in base_controls if c != prox and c in d.columns]
                    if fe_name == "event_fe":
                        # FocalCAR is event-level and is absorbed by event FE.
                        # Keep only the peer-level exposure and its interaction.
                        xvars = [prox, interaction] + controls
                    else:
                        xvars = [focal_var, prox, interaction] + controls
                    res = fit_ols(d, dep, xvars, fe_cols)
                    rows.append(
                        {
                            "sample": sample_name,
                            "outcome": outcome_label,
                            "dep": dep,
                            "focal_var": focal_var,
                            "prox": prox,
                            "prox_type": prox_type,
                            "prox_label": prox_label,
                            "interaction": interaction,
                            "fe": fe_name,
                            **res,
                        }
                    )
    return pd.DataFrame(rows)


def format_coef(b: float, p: float) -> str:
    if pd.isna(b):
        return ""
    stars = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""
    return f"{b:.4f}{stars}"


def write_doc(results: pd.DataFrame) -> None:
    compact_rows = []
    for r in results.itertuples(index=False):
        focal = getattr(r, f"{r.focal_var}_coef", np.nan)
        focal_p = getattr(r, f"{r.focal_var}_p", np.nan)
        inter = getattr(r, f"{r.interaction}_coef", np.nan)
        inter_p = getattr(r, f"{r.interaction}_p", np.nan)
        compact_rows.append(
            {
                "sample": r.sample,
                "outcome": r.outcome,
                "prox": r.prox,
                "fe": r.fe,
                "FocalMove": format_coef(focal, focal_p),
                "FocalMove x Prox": format_coef(inter, inter_p),
                "interaction_p": round(inter_p, 4) if pd.notna(inter_p) else np.nan,
                "nobs": r.nobs,
                "events": r.events,
                "peer_firms": r.peer_firms,
            }
        )
    compact = pd.DataFrame(compact_rows)
    key = compact[
        compact["outcome"].eq("PeerCAR[0,+1]")
        & compact["sample"].eq("all")
        & compact["fe"].isin(["no_event_fe_peer_industry_week", "event_fe"])
    ].copy()
    clean = compact[
        compact["outcome"].eq("PeerCAR[0,+1]")
        & compact["sample"].eq("drop_genai_or_major")
        & compact["fe"].isin(["no_event_fe_peer_industry_week", "event_fe"])
    ].copy()
    ar_key = compact[
        compact["outcome"].eq("PeerAR[0]")
        & compact["sample"].eq("all")
        & compact["fe"].isin(["no_event_fe_peer_industry_week", "event_fe"])
    ].copy()
    ar_clean = compact[
        compact["outcome"].eq("PeerAR[0]")
        & compact["sample"].eq("drop_genai_or_major")
        & compact["fe"].isin(["no_event_fe_peer_industry_week", "event_fe"])
    ].copy()

    lines = [
        "# v35 focal-peer two-component probe",
        "",
        "## Scope",
        "",
        "- Input: v33 supplement panel.",
        "- Goal: evaluate Claude's two-component interpretation: common/contagion level effect plus competitive exposure gradient.",
        "- `FocalCAR` is standardized focal firm CAR[0,+1] for PeerCAR models and standardized focal AR[0] for PeerAR models.",
        "- `FocalCAR x Prox < 0` is the key competitive-gradient prediction.",
        "- Peer-level Prox variables are also run with event FE; `Spec` is event-level, so its focal-CAR interaction is not identified under event FE.",
        "- In event-FE rows, the focal-firm return level is omitted because it is event-level and absorbed by event FE.",
        "",
        "## Headline Read",
        "",
        "1. Claude's two-component interpretation is conceptually right: a GenAI disclosure can contain both a common/contagion signal and a peer-level competitive signal. The raw v33 focal-peer mirror and the v35 PeerAR[0] no-event-FE models support the existence of a positive common component.",
        "2. The controlled PeerCAR[0,+1] level relation is only positive in direction, not statistically sharp after peer-industry-week FE and controls. Do not overstate the common-component test as a main result.",
        "3. The desired competitive-gradient sign is not supported in this pass. `FocalMove x PeerSimilarity`, `FocalMove x Top3Peer`, and `FocalMove x AIActivePeer` are near zero or positive and insignificant.",
        "4. `FocalMove x peer_industry_hhi_z` is the only negative lead in some PeerCAR specifications, but it is weak and not stable under event FE / pollution cleaning. Treat it as exploratory.",
        "5. `FocalMove x Spec` is positive but insignificant. Since Spec is event-level, it is better interpreted as a possible common-signal moderator, not peer-level competition exposure.",
        "6. Bottom line: keep Claude's decomposition as the framing for why raw focal-peer positive correlation does not kill the competition story, but do not use `FocalMove x Prox` as a finished mechanism table yet. The stronger current evidence remains: pollution cleaning, CAR[0,+1] persistence, long-window non-reversal, analyst forecast revision, and the existing event-FE `Spec x AIActivePeer` result.",
        "",
        "## Main PeerCAR Results: All Sample",
        "",
        key.to_markdown(index=False),
        "",
        "## Main PeerCAR Results: Drop Peer GenAI Or Major Announcement",
        "",
        clean.to_markdown(index=False),
        "",
        "## Main PeerAR Results: All Sample",
        "",
        ar_key.to_markdown(index=False),
        "",
        "## Main PeerAR Results: Drop Peer GenAI Or Major Announcement",
        "",
        ar_clean.to_markdown(index=False),
        "",
        "## Output Files",
        "",
        "- `results/v35_focal_peer_two_component_probe_20260605/focal_peer_two_component_regressions.csv`",
        "- `results/v35_focal_peer_two_component_probe_20260605/focal_peer_two_component_compact.csv`",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    compact.to_csv(OUT / "focal_peer_two_component_compact.csv", index=False)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    panel = load_panel()
    results = run_models(panel)
    results.to_csv(OUT / "focal_peer_two_component_regressions.csv", index=False)
    write_doc(results)
    print(f"wrote {OUT}")
    show_cols = [
        "sample",
        "outcome",
        "prox",
        "fe",
        "nobs",
        "events",
        "peer_firms",
        "focal_car_z_coef",
        "focal_car_z_p",
        "focal_car_z_x_peer_similarity_z_coef",
        "focal_car_z_x_peer_similarity_z_p",
        "focal_car_z_x_top3_peer_coef",
        "focal_car_z_x_top3_peer_p",
        "focal_car_z_x_ai_coef",
        "focal_car_z_x_ai_p",
        "focal_car_z_x_peer_industry_hhi_z_coef",
        "focal_car_z_x_peer_industry_hhi_z_p",
        "focal_car_z_x_spec_z_coef",
        "focal_car_z_x_spec_z_p",
    ]
    existing = [c for c in show_cols if c in results.columns]
    print(results[results["outcome"].eq("PeerCAR[0,+1]")][existing].to_string(index=False))


if __name__ == "__main__":
    main()
