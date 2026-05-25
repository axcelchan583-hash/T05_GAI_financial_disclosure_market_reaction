#!/usr/bin/env python3
"""Go/no-go diagnostics for the v4 AI-active peer spillover design.

This script formalizes the diagnostics prompted by the Claude review:

1. Re-estimate the triple interaction under one-way and two-way clustered SEs.
2. Rebuild AI-active peer flags using information observable before t-5.
3. Report the implied non-AI-active and AI-active within-group effects.
4. Run subsample regressions for AI-active and non-AI-active peers.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.sandwich_covariance import cov_cluster, cov_cluster_2groups


ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "results" / "v4_peer_spillover_controls_heterogeneity"
OUT_DIR = ROOT / "results" / "v4_go_no_go_diagnostics"

PANEL_TOP3 = INPUT_DIR / "v4_peer_event_controls_heterogeneity_top3.csv"
PANEL_TOP5 = INPUT_DIR / "v4_peer_event_controls_heterogeneity_top5.csv"
PANEL_TOP10 = INPUT_DIR / "v4_peer_event_controls_heterogeneity_top10.csv"

IRQA_FIRM_DAY = ROOT / "results" / "plan_a_irqa_multichannel_event_study" / "plan_a_irqa_strict_firm_day_events.csv"
PUBLIC_IRQA = ROOT / "results" / "v8_3_external_evidence_link_pilot" / "public_irqa_events_for_linking.csv"
FORMAL_EVENTS = ROOT / "results" / "v3_genai_specificity_car_pilot" / "cninfo_genai_event_candidates_with_specificity.csv"
ANNUAL_EVIDENCE = ROOT / "results" / "v8_3_external_evidence_link_pilot" / "firm_external_evidence_panel_2024.csv"

OUTCOMES = {
    "peer_ar0": {
        "obs_col": "obs_ar0",
        "required_obs": 1,
        "normal_col": "normal_trading_ar0",
        "limit_col": "no_limit_ar0",
    },
    "peer_car_0_p1": {
        "obs_col": "obs_car_0_p1",
        "required_obs": 2,
        "normal_col": "normal_trading_0_p1",
        "limit_col": "no_limit_0_p1",
    },
    "peer_car_m1_p1": {
        "obs_col": "obs_car_m1_p1",
        "required_obs": 3,
        "normal_col": "normal_trading_m1_p1",
        "limit_col": "no_limit_m1_p1",
    },
}

CONTROLS = [
    "z_peer_beta",
    "z_pre_mom_60",
    "z_pre_vol_120",
    "z_pre_absret_60",
    "is_chinext_or_star",
    "z_peer_rank",
]


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = re.sub(r"\.0$", "", text)
    text = re.sub(r"\D", "", text)
    return text.zfill(6) if text else ""


def read_panel(path: Path, topn: int) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"peer_code": str, "focal_code": str})
    df["peer_code"] = df["peer_code"].map(code6)
    df["focal_code"] = df["focal_code"].map(code6)
    df["raw_event_date"] = pd.to_datetime(df["raw_event_date"], errors="coerce")
    df["event_date_for_car"] = pd.to_datetime(df["event_date_for_car"], errors="coerce")
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df["topn"] = topn
    for col in [
        "specificity",
        "product_similarity",
        "x_specificity_similarity",
        "peer_rank",
        *CONTROLS,
        *OUTCOMES.keys(),
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_public_evidence_events() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    if IRQA_FIRM_DAY.exists():
        irqa = pd.read_csv(IRQA_FIRM_DAY)
        irqa = irqa.rename(columns={"stock_code": "code", "event_date_str": "event_date"})
        frames.append(
            pd.DataFrame(
                {
                    "code": irqa["code"].map(code6),
                    "evidence_date": pd.to_datetime(irqa["event_date"], errors="coerce"),
                    "evidence_type": "strict_irqa",
                }
            )
        )

    if PUBLIC_IRQA.exists():
        public = pd.read_csv(PUBLIC_IRQA)
        frames.append(
            pd.DataFrame(
                {
                    "code": public["Symbol"].map(code6),
                    "evidence_date": pd.to_datetime(public["event_date"], errors="coerce"),
                    "evidence_type": "public_irqa_linking",
                }
            )
        )

    if FORMAL_EVENTS.exists():
        formal = pd.read_csv(FORMAL_EVENTS)
        frames.append(
            pd.DataFrame(
                {
                    "code": formal["sec_code"].map(code6),
                    "evidence_date": pd.to_datetime(formal["announcement_date_dt"], errors="coerce"),
                    "evidence_type": "formal_announcement",
                }
            )
        )

    if not frames:
        return pd.DataFrame(columns=["code", "evidence_date", "evidence_type"])

    events = pd.concat(frames, ignore_index=True)
    events = events[events["code"].ne("") & events["evidence_date"].notna()].copy()
    return events.drop_duplicates()


def load_annual_evidence() -> pd.DataFrame:
    if not ANNUAL_EVIDENCE.exists():
        return pd.DataFrame(columns=["code", "report_disclosure_date", "n_claim_sentences"])
    annual = pd.read_csv(ANNUAL_EVIDENCE)
    annual["code"] = annual["Symbol"].map(code6)
    annual["report_disclosure_date"] = pd.to_datetime(
        annual["report_disclosure_date"], errors="coerce"
    )
    annual["n_claim_sentences"] = pd.to_numeric(
        annual["n_claim_sentences"], errors="coerce"
    ).fillna(0)
    return annual[["code", "report_disclosure_date", "n_claim_sentences"]].drop_duplicates()


def add_preobservable_ai_flags(panel: pd.DataFrame) -> pd.DataFrame:
    public_events = load_public_evidence_events()
    annual = load_annual_evidence()

    public_by_code = {
        code: sorted(sub["evidence_date"].tolist())
        for code, sub in public_events.groupby("code", sort=False)
    }
    annual_by_code = {
        code: sorted(sub["report_disclosure_date"].dropna().tolist())
        for code, sub in annual.loc[annual["n_claim_sentences"] > 0].groupby("code", sort=False)
    }

    public_tminus5 = []
    annual_tminus5 = []
    for _, row in panel.iterrows():
        peer = row["peer_code"]
        event_date = row["raw_event_date"]
        if pd.isna(event_date):
            public_tminus5.append(0)
            annual_tminus5.append(0)
            continue
        cutoff = event_date - pd.Timedelta(days=5)
        public_tminus5.append(int(any(d <= cutoff for d in public_by_code.get(peer, []))))
        annual_tminus5.append(int(any(d <= cutoff for d in annual_by_code.get(peer, []))))

    out = panel.copy()
    out["ai_public_tminus5"] = public_tminus5
    out["ai_annual_tminus5"] = annual_tminus5
    out["ai_preobs_tminus5"] = (
        (out["ai_public_tminus5"] == 1) | (out["ai_annual_tminus5"] == 1)
    ).astype(int)

    # Existing broad variable from the prior heterogeneity script, retained for comparison.
    out["ai_existing_broad"] = out["peer_has_pre_public_or_annual_ai"].fillna(0).astype(int)

    for active in [
        "ai_existing_broad",
        "ai_public_tminus5",
        "ai_annual_tminus5",
        "ai_preobs_tminus5",
    ]:
        out[f"sim_{active}"] = out["product_similarity"] * out[active]
        out[f"xspecsim_{active}"] = out["x_specificity_similarity"] * out[active]
    return out


def clean_outcome_sample(df: pd.DataFrame, outcome: str) -> pd.DataFrame:
    cfg = OUTCOMES[outcome]
    return df[
        (df[cfg["obs_col"]] == cfg["required_obs"])
        & (df[cfg["normal_col"]] == 1)
        & (df[cfg["limit_col"]] == 1)
    ].copy()


def covariance_matrix(model, data: pd.DataFrame, cov_type: str):
    if cov_type == "ols":
        return model.cov_params()
    if cov_type == "event_cluster":
        return cov_cluster(model, pd.Categorical(data["event_id"]).codes)
    if cov_type == "peer_cluster":
        return cov_cluster(model, pd.Categorical(data["peer_code"]).codes)
    if cov_type == "date_cluster":
        return cov_cluster(model, pd.Categorical(data["event_date"].astype(str)).codes)
    if cov_type == "twoway_event_peer":
        cov_both, _, _ = cov_cluster_2groups(
            model,
            pd.Categorical(data["event_id"]).codes,
            pd.Categorical(data["peer_code"]).codes,
        )
        return cov_both
    if cov_type == "twoway_date_peer":
        cov_both, _, _ = cov_cluster_2groups(
            model,
            pd.Categorical(data["event_date"].astype(str)).codes,
            pd.Categorical(data["peer_code"]).codes,
        )
        return cov_both
    raise ValueError(f"Unknown covariance type: {cov_type}")


def linear_test(model, cov, weights: dict[str, float]) -> tuple[float, float, float, float]:
    params = model.params
    names = list(params.index)
    w = np.zeros(len(names))
    for term, value in weights.items():
        if term in params.index:
            w[names.index(term)] = value
    coef = float(np.dot(w, params.values))
    cov_arr = np.asarray(cov)
    var = float(w @ cov_arr @ w)
    se = float(np.sqrt(var)) if var >= 0 else np.nan
    z = coef / se if np.isfinite(se) and se > 0 else np.nan
    p = float(2 * (1 - stats.norm.cdf(abs(z)))) if np.isfinite(z) else np.nan
    return coef, se, z, p


def run_interaction_model(
    data: pd.DataFrame,
    topn: int,
    outcome: str,
    active: str,
    controls: bool,
) -> list[dict[str, object]]:
    x_active = f"xspecsim_{active}"
    sim_active = f"sim_{active}"
    rhs = [
        "product_similarity",
        "x_specificity_similarity",
        active,
        sim_active,
        x_active,
        "C(event_id)",
    ]
    if controls:
        rhs.extend(CONTROLS)

    needed = [
        outcome,
        "product_similarity",
        "x_specificity_similarity",
        active,
        sim_active,
        x_active,
        "event_id",
        "peer_code",
        "event_date",
    ] + (CONTROLS if controls else [])
    used = data.dropna(subset=needed).copy()
    try:
        model = smf.ols(f"{outcome} ~ {' + '.join(rhs)}", data=used).fit()
    except Exception:
        return []

    cov_types = [
        "ols",
        "event_cluster",
        "peer_cluster",
        "date_cluster",
        "twoway_event_peer",
        "twoway_date_peer",
    ]
    rows: list[dict[str, object]] = []
    for cov_type in cov_types:
        cov = covariance_matrix(model, used, cov_type)
        for effect, weights in {
            "baseline_non_ai_effect": {"x_specificity_similarity": 1.0},
            "incremental_ai_active_effect": {x_active: 1.0},
            "total_ai_active_effect": {
                "x_specificity_similarity": 1.0,
                x_active: 1.0,
            },
        }.items():
            coef, se, z, p = linear_test(model, cov, weights)
            rows.append(
                {
                    "topn": topn,
                    "outcome": outcome,
                    "active_definition": active,
                    "controls": controls,
                    "cov_type": cov_type,
                    "effect": effect,
                    "coef": coef,
                    "se": se,
                    "z": z,
                    "p": p,
                    "nobs": int(model.nobs),
                    "events": int(used["event_id"].nunique()),
                    "event_dates": int(used["event_date"].nunique()),
                    "peer_firms": int(used["peer_code"].nunique()),
                    "active_obs": int(used[active].sum()),
                    "active_events": int(used.loc[used[active] == 1, "event_id"].nunique()),
                    "active_peer_firms": int(used.loc[used[active] == 1, "peer_code"].nunique()),
                    "r2": float(model.rsquared),
                }
            )
    return rows


def run_subsample_model(
    data: pd.DataFrame,
    topn: int,
    outcome: str,
    active: str,
    active_value: int,
    controls: bool,
) -> list[dict[str, object]]:
    sample = data[data[active] == active_value].copy()
    rhs = ["product_similarity", "x_specificity_similarity", "C(event_id)"]
    if controls:
        rhs.extend(CONTROLS)
    needed = [
        outcome,
        "product_similarity",
        "x_specificity_similarity",
        "event_id",
        "peer_code",
        "event_date",
    ] + (CONTROLS if controls else [])
    used = sample.dropna(subset=needed).copy()
    if len(used) < 50 or used["event_id"].nunique() < 20 or used["peer_code"].nunique() < 20:
        return []
    try:
        model = smf.ols(f"{outcome} ~ {' + '.join(rhs)}", data=used).fit()
    except Exception:
        return []
    rows = []
    for cov_type in ["event_cluster", "peer_cluster", "twoway_event_peer", "twoway_date_peer"]:
        cov = covariance_matrix(model, used, cov_type)
        coef, se, z, p = linear_test(
            model, cov, {"x_specificity_similarity": 1.0}
        )
        rows.append(
            {
                "topn": topn,
                "outcome": outcome,
                "active_definition": active,
                "active_value": active_value,
                "controls": controls,
                "cov_type": cov_type,
                "coef": coef,
                "se": se,
                "z": z,
                "p": p,
                "nobs": int(model.nobs),
                "events": int(used["event_id"].nunique()),
                "event_dates": int(used["event_date"].nunique()),
                "peer_firms": int(used["peer_code"].nunique()),
                "r2": float(model.rsquared),
            }
        )
    return rows


def sample_diagnostics(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for topn, top in panel.groupby("topn", sort=True):
        for outcome in OUTCOMES:
            clean = clean_outcome_sample(top, outcome)
            row = {
                "topn": topn,
                "outcome": outcome,
                "raw_rows": len(top),
                "raw_events": top["event_id"].nunique(),
                "raw_peer_firms": top["peer_code"].nunique(),
                "clean_rows": len(clean),
                "clean_events": clean["event_id"].nunique(),
                "clean_event_dates": clean["event_date"].nunique(),
                "clean_peer_firms": clean["peer_code"].nunique(),
            }
            for active in [
                "ai_existing_broad",
                "ai_public_tminus5",
                "ai_annual_tminus5",
                "ai_preobs_tminus5",
            ]:
                row[f"{active}_rows"] = int(clean[active].sum())
                row[f"{active}_share"] = float(clean[active].mean())
                row[f"{active}_events"] = int(clean.loc[clean[active] == 1, "event_id"].nunique())
                row[f"{active}_peer_firms"] = int(clean.loc[clean[active] == 1, "peer_code"].nunique())
            rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    panel_specs = [(3, PANEL_TOP3), (5, PANEL_TOP5)]
    if PANEL_TOP10.exists():
        panel_specs.append((10, PANEL_TOP10))
    panels = [
        add_preobservable_ai_flags(read_panel(path, topn=topn))
        for topn, path in panel_specs
    ]
    panel = pd.concat(panels, ignore_index=True)

    panel.to_csv(OUT_DIR / "v4_go_no_go_analysis_panel.csv", index=False)
    diag = sample_diagnostics(panel)
    diag.to_csv(OUT_DIR / "v4_go_no_go_sample_diagnostics.csv", index=False)

    interaction_rows: list[dict[str, object]] = []
    subsample_rows: list[dict[str, object]] = []
    for topn, top in panel.groupby("topn", sort=True):
        for outcome in OUTCOMES:
            clean = clean_outcome_sample(top, outcome)
            for active in [
                "ai_existing_broad",
                "ai_public_tminus5",
                "ai_annual_tminus5",
                "ai_preobs_tminus5",
            ]:
                for controls in [False, True]:
                    interaction_rows.extend(
                        run_interaction_model(clean, int(topn), outcome, active, controls)
                    )
                    for active_value in [0, 1]:
                        subsample_rows.extend(
                            run_subsample_model(
                                clean,
                                int(topn),
                                outcome,
                                active,
                                active_value,
                                controls,
                            )
                        )

    interactions = pd.DataFrame(interaction_rows)
    subsamples = pd.DataFrame(subsample_rows)
    interactions.to_csv(OUT_DIR / "v4_go_no_go_interaction_effects.csv", index=False)
    subsamples.to_csv(OUT_DIR / "v4_go_no_go_subsample_effects.csv", index=False)

    focus = interactions[
        (interactions["topn"] == 5)
        & (interactions["outcome"] == "peer_car_m1_p1")
        & (interactions["effect"].isin(["incremental_ai_active_effect", "total_ai_active_effect"]))
        & (interactions["cov_type"].isin(["twoway_event_peer", "twoway_date_peer"]))
    ].copy()
    focus.to_csv(OUT_DIR / "v4_go_no_go_focus_main_effects.csv", index=False)

    print("Sample diagnostics:")
    print(
        diag[
            [
                "topn",
                "outcome",
                "clean_rows",
                "clean_events",
                "clean_peer_firms",
                "ai_preobs_tminus5_rows",
                "ai_preobs_tminus5_share",
            ]
        ].to_string(index=False)
    )
    print("\nFocus main effects:")
    print(
        focus[
            [
                "active_definition",
                "controls",
                "cov_type",
                "effect",
                "coef",
                "se",
                "p",
                "nobs",
                "events",
                "peer_firms",
                "active_obs",
            ]
        ]
        .sort_values(["active_definition", "controls", "cov_type", "effect"])
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
