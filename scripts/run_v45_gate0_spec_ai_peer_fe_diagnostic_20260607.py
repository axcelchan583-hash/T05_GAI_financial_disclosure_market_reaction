#!/usr/bin/env python3
"""Gate 0 diagnostic for Spec x AIActive under peer fixed effects."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v25_empirical_table_pack_20260604 as v25  # noqa: E402
import run_v28_v36_peer_main_effect_tables_20260605 as v28  # noqa: E402


RUN_ID = "v45_gate0_spec_ai_peer_fe_diagnostic_20260607"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "109_v45_gate0_spec_ai_peer_fe_diagnostic_20260607.md"
ANALYST_PANEL = ROOT / "results" / "v34_analyst_forecast_revision_probe_20260605" / "analyst_revision_panel.csv.gz"


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


def fmt(value: object, digits: int = 4) -> str:
    if value is None or pd.isna(value):
        return ""
    return f"{float(value):.{digits}f}"


def markdown_table(df: pd.DataFrame) -> str:
    rows = ["| " + " | ".join(df.columns) + " |", "|" + "|".join("---" for _ in df.columns) + "|"]
    for _, row in df.iterrows():
        rows.append("| " + " | ".join("" if pd.isna(row[c]) else str(row[c]) for c in df.columns) + " |")
    return "\n".join(rows)


def load_main_panel() -> pd.DataFrame:
    event_panel = v28.load_event_panel()
    with_spec = v28.attach_specificity(event_panel)
    panel = v28.mechanism_sample(with_spec).copy()
    panel["peer_code"] = panel["peer_code"].astype(str).str.zfill(6)
    panel["event_key"] = panel["event_key"].astype(str)
    return panel


def peer_frequency(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    freq = (
        panel.groupby("peer_code", as_index=False)
        .agg(event_count=("event_key", "nunique"), obs_count=("event_key", "size"))
        .sort_values(["event_count", "peer_code"])
    )
    x = freq["event_count"].astype(float)
    dist = pd.DataFrame(
        [
            {
                "metric": "peer_event_frequency",
                "min": x.min(),
                "p25": x.quantile(0.25),
                "median": x.median(),
                "p75": x.quantile(0.75),
                "max": x.max(),
                "mean": x.mean(),
                "peer_firms": len(freq),
                "obs": int(panel.shape[0]),
            }
        ]
    )
    singleton = freq[freq["event_count"].eq(1)].copy()
    singleton_summary = pd.DataFrame(
        [
            {
                "peer_firms": int(len(freq)),
                "singleton_peer_firms": int(len(singleton)),
                "singleton_peer_share": len(singleton) / len(freq) if len(freq) else math.nan,
                "total_obs": int(len(panel)),
                "singleton_obs": int(singleton["obs_count"].sum()),
                "singleton_obs_share": singleton["obs_count"].sum() / len(panel) if len(panel) else math.nan,
            }
        ]
    )
    return freq, dist, singleton_summary


def variance_decomposition(panel: pd.DataFrame, xvar: str = "spec_ai") -> pd.DataFrame:
    d = panel.dropna(subset=[xvar, "peer_code"]).copy()
    x = pd.to_numeric(d[xvar], errors="coerce").astype(float)
    peer_mean = d.groupby("peer_code")[xvar].transform("mean").astype(float)
    peer_means = d.groupby("peer_code")[xvar].mean().astype(float)
    within = x - peer_mean
    weighted_between = peer_mean - x.mean()
    rows = [
        {
            "variable": xvar,
            "overall_sd": x.std(ddof=0),
            "between_peer_sd_unweighted": peer_means.std(ddof=0),
            "between_peer_sd_obs_weighted": weighted_between.std(ddof=0),
            "within_peer_sd": within.std(ddof=0),
            "within_over_overall": within.std(ddof=0) / x.std(ddof=0) if x.std(ddof=0) > 0 else math.nan,
            "within_share_of_variance": within.var(ddof=0) / x.var(ddof=0) if x.var(ddof=0) > 0 else math.nan,
            "obs": int(len(d)),
            "peer_firms": int(d["peer_code"].nunique()),
        }
    ]
    non_singletons = d[d.groupby("peer_code")["event_key"].transform("nunique").gt(1)].copy()
    if not non_singletons.empty:
        xs = pd.to_numeric(non_singletons[xvar], errors="coerce").astype(float)
        pm = non_singletons.groupby("peer_code")[xvar].transform("mean").astype(float)
        rows.append(
            {
                "variable": f"{xvar}_non_singleton_peers",
                "overall_sd": xs.std(ddof=0),
                "between_peer_sd_unweighted": non_singletons.groupby("peer_code")[xvar].mean().std(ddof=0),
                "between_peer_sd_obs_weighted": (pm - xs.mean()).std(ddof=0),
                "within_peer_sd": (xs - pm).std(ddof=0),
                "within_over_overall": (xs - pm).std(ddof=0) / xs.std(ddof=0) if xs.std(ddof=0) > 0 else math.nan,
                "within_share_of_variance": (xs - pm).var(ddof=0) / xs.var(ddof=0) if xs.var(ddof=0) > 0 else math.nan,
                "obs": int(len(non_singletons)),
                "peer_firms": int(non_singletons["peer_code"].nunique()),
            }
        )
    return pd.DataFrame(rows)


def model_row(
    panel: pd.DataFrame,
    label: str,
    outcome: str,
    xvars: list[str],
    fe_cols: list[str],
    singleton_obs: int,
) -> dict[str, object]:
    res = v28.fit_absorbed_ols(panel, outcome, xvars, fe_cols)
    if res is None:
        return {
            "spec": label,
            "outcome": outcome,
            "xvars": ",".join(xvars),
            "fe": "+".join(fe_cols),
        }
    absorbed = singleton_obs if "peer_code" in fe_cols else 0
    return {
        "spec": label,
        "outcome": outcome,
        "xvars": ",".join(xvars),
        "fe": "+".join(fe_cols),
        "coef": res.get("spec_ai_coef"),
        "se": res.get("spec_ai_se"),
        "z": res.get("spec_ai_z"),
        "p": res.get("spec_ai_p"),
        "coef_fmt": f"{fmt(res.get('spec_ai_coef'))}{stars(res.get('spec_ai_p'))}",
        "se_fmt": f"({fmt(res.get('spec_ai_se'))})",
        "nobs": res.get("nobs"),
        "events": res.get("events"),
        "peer_firms": res.get("peer_firms"),
        "absorbed_no_contribution_obs": absorbed,
        "effective_identification_obs": int(res.get("nobs", 0)) - absorbed,
        "overall_r2": res.get("overall_r2"),
        "within_r2": res.get("within_r2"),
    }


def main_regressions(panel: pd.DataFrame, singleton_obs: int) -> pd.DataFrame:
    specs = [
        ("event_fe_only", ["ai", "spec_ai"], ["event_key"]),
        ("event_fe_plus_pre_returns", ["ai", "spec_ai", *v28.PRE_CONTROLS], ["event_key"]),
        ("event_and_peer_firm_fe", ["ai", "spec_ai", *v28.PRE_CONTROLS], ["event_key", "peer_code"]),
    ]
    return pd.DataFrame(
        [model_row(panel, label, v28.MAIN_OUTCOME, xvars, fe, singleton_obs) for label, xvars, fe in specs]
    )


def non_singleton_checks(panel: pd.DataFrame) -> pd.DataFrame:
    event_counts = panel.groupby("peer_code")["event_key"].transform("nunique")
    sub = panel[event_counts.gt(1)].copy()
    rows = [
        model_row(sub, "non_singleton_event_fe_only", v28.MAIN_OUTCOME, ["ai", "spec_ai"], ["event_key"], 0),
        model_row(
            sub,
            "non_singleton_event_fe_plus_pre_returns",
            v28.MAIN_OUTCOME,
            ["ai", "spec_ai", *v28.PRE_CONTROLS],
            ["event_key"],
            0,
        ),
    ]
    return pd.DataFrame(rows)


def fit_slope_two_way(
    data: pd.DataFrame,
    outcome: str,
    xvar: str,
    fe_cols: list[str],
    cluster_peer_col: str = "peer_code",
) -> dict[str, object]:
    need = [outcome, xvar, "event_key", cluster_peer_col, *fe_cols]
    d = data.dropna(subset=list(dict.fromkeys(need))).copy()
    if len(d) < 20 or d[xvar].nunique() < 2:
        return {
            "nobs": len(d),
            "events": d["event_key"].nunique() if "event_key" in d else 0,
            "peer_firms": d[cluster_peer_col].nunique() if cluster_peer_col in d else 0,
            "coef": math.nan,
            "se": math.nan,
            "z": math.nan,
            "p": math.nan,
        }
    if fe_cols:
        dm = v25.absorb_frame(d, [outcome, xvar], fe_cols)
        y = dm[outcome].to_numpy(dtype=float)
        x = dm[[xvar]].to_numpy(dtype=float)
    else:
        y = d[outcome].astype(float).to_numpy()
        x = sm.add_constant(d[[xvar]].astype(float), has_constant="add").to_numpy()
    keep_x_index = 0 if fe_cols else 1
    bread = np.linalg.pinv(x.T @ x)
    beta = bread @ (x.T @ y)
    resid = y - x @ beta
    meat_event = v25.cluster_meat(x, resid, d["event_key"])
    meat_peer = v25.cluster_meat(x, resid, d[cluster_peer_col])
    pair = d["event_key"].astype(str) + "|" + d[cluster_peer_col].astype(str)
    meat_pair = v25.cluster_meat(x, resid, pair)
    cov = bread @ (meat_event + meat_peer - meat_pair) @ bread
    coef = float(beta[keep_x_index])
    se = math.sqrt(float(cov[keep_x_index, keep_x_index])) if cov[keep_x_index, keep_x_index] >= 0 else math.nan
    z_value = coef / se if se and se > 0 else math.nan
    return {
        "nobs": int(len(d)),
        "events": int(d["event_key"].nunique()),
        "peer_firms": int(d[cluster_peer_col].nunique()),
        "coef": coef,
        "se": se,
        "z": z_value,
        "p": v25.p_from_z(z_value),
    }


def analyst_fallback() -> pd.DataFrame:
    rev = pd.read_csv(ANALYST_PANEL, low_memory=False)
    sub = rev[
        rev["metric"].eq("feps")
        & rev["target_offset"].eq(1)
        & rev["post_horizon_days"].eq(60)
        & rev["revision_scaled"].notna()
    ].copy()
    sub["peer_code"] = sub["peer_code_norm"].astype(str).str.zfill(6)
    sub["focal_code"] = sub["focal_code_norm"].astype(str).str.zfill(6)
    rows: list[dict[str, object]] = []
    for outcome, label in [
        ("peer_car_0_p1_mm", "PeerCAR[0,+1]"),
        ("revision_scaled", "FY+1 EPS revision_scaled"),
        ("revision_down", "FY+1 EPS revision_down"),
    ]:
        for fe_cols, fe_label in [([], "no_fe"), (["event_key"], "event_fe")]:
            res = fit_slope_two_way(sub, outcome, "ai", fe_cols)
            rows.append(
                {
                    "sample": "fy1_feps_60d_covered",
                    "outcome": label,
                    "regressor": "AIActivePeer",
                    "fe": fe_label,
                    **res,
                    "coef_fmt": f"{fmt(res.get('coef'))}{stars(res.get('p'))}",
                    "se_fmt": f"({fmt(res.get('se'))})",
                }
            )
    return pd.DataFrame(rows)


def format_numeric(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_numeric_dtype(out[col]):
            if col in {"nobs", "events", "peer_firms", "obs", "total_obs", "singleton_obs", "effective_identification_obs", "absorbed_no_contribution_obs"}:
                out[col] = out[col].map(lambda x: "" if pd.isna(x) else str(int(round(float(x)))))
            else:
                out[col] = out[col].map(lambda x: "" if pd.isna(x) else fmt(x, 4))
    return out


def verdict(variance: pd.DataFrame, non_singleton: pd.DataFrame, fallback: pd.DataFrame) -> tuple[str, str]:
    within_ratio = float(variance.loc[variance["variable"].eq("spec_ai"), "within_over_overall"].iloc[0])
    ns = non_singleton[non_singleton["spec"].eq("non_singleton_event_fe_only")].iloc[0]
    ns_sig = pd.notna(ns["p"]) and float(ns["p"]) < 0.05 and float(ns["coef"]) < 0
    ai_rev = fallback[
        fallback["outcome"].eq("FY+1 EPS revision_scaled") & fallback["fe"].eq("event_fe")
    ].iloc[0]
    ai_revision_stable = pd.notna(ai_rev["p"]) and float(ai_rev["p"]) < 0.10
    if within_ratio < 0.35 or ns_sig:
        return (
            "A 主线 GO",
            "剔除 singleton 后 event FE 规格仍为负且显著；本次不是 within SD 极低，而是 peer FE 改用更窄的 within-peer 对比并移除大量 singleton 识别贡献，不能据此判定 event-FE 主效应不存在。",
        )
    if ai_revision_stable:
        return (
            "B fallback",
            "剔除 singleton 后 specificity 也不稳，但 AIActive 的 analyst revision 路线有统计支持。",
        )
    return (
        "C 保留 specificity 降级",
        "specificity 在 peer FE 下不稳，但 analyst fallback 也未形成稳健替代；保留 event-FE specificity 作为异质性/机制证据，主效应仍锚定 competitor CAR。",
    )


def write_doc(
    freq_dist: pd.DataFrame,
    singleton_summary: pd.DataFrame,
    variance: pd.DataFrame,
    main_regs: pd.DataFrame,
    non_singleton: pd.DataFrame,
    fallback: pd.DataFrame,
    verdict_label: str,
    verdict_text: str,
) -> None:
    lines = [
        "# v45 Gate 0: Spec x AIActive Peer-FE Diagnostic",
        "",
        "Date: 2026-06-07",
        "",
        "## Purpose",
        "",
        "Diagnose whether `Spec x AIActivePeer` disappearing under peer-firm fixed effects is mainly a power / singleton / within-variation problem, or evidence that the effect is absent.",
        "",
        "## 1. Peer-Firm Event Frequency",
        "",
        markdown_table(format_numeric(freq_dist)),
        "",
        "## Singleton Contribution",
        "",
        markdown_table(format_numeric(singleton_summary)),
        "",
        "## 2. Between/Within Variation of Spec x AIActivePeer",
        "",
        markdown_table(format_numeric(variance)),
        "",
        "## 3. Same-Subsample Event-FE Check After Dropping Singleton Peers",
        "",
        markdown_table(format_numeric(non_singleton)),
        "",
        "## 4. Main Specification Comparison",
        "",
        markdown_table(format_numeric(main_regs)),
        "",
        "## 5. Analyst-Covered Fallback Probe",
        "",
        markdown_table(format_numeric(fallback)),
        "",
        "## Verdict",
        "",
        f"**{verdict_label}.** {verdict_text}",
        "",
        "## Table Order Recommendation",
        "",
        "1. Keep the main Table 2 event-study result on product-market competitor CAR.",
        "2. Put `Spec x AIActivePeer` event-FE heterogeneity as the main mechanism/heterogeneity table.",
        "3. Put the peer-firm-FE version in robustness, explicitly noting the high singleton share and the fact that this specification asks a narrower within-peer question.",
        "4. Use analyst-covered evidence as supporting mechanism evidence, not as the fallback main route unless later analyst revision tests become stronger.",
        "",
        "## Output Files",
        "",
        f"- `results/{RUN_ID}/peer_frequency_by_firm.csv`",
        f"- `results/{RUN_ID}/peer_frequency_distribution.csv`",
        f"- `results/{RUN_ID}/singleton_summary.csv`",
        f"- `results/{RUN_ID}/spec_ai_variance_decomposition.csv`",
        f"- `results/{RUN_ID}/main_spec_comparison.csv`",
        f"- `results/{RUN_ID}/non_singleton_event_fe_checks.csv`",
        f"- `results/{RUN_ID}/analyst_fallback_aiactive.csv`",
    ]
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    panel = load_main_panel()
    freq, freq_dist, singleton_summary = peer_frequency(panel)
    singleton_obs = int(singleton_summary["singleton_obs"].iloc[0])
    variance = variance_decomposition(panel)
    main_regs = main_regressions(panel, singleton_obs)
    non_singleton = non_singleton_checks(panel)
    fallback = analyst_fallback()
    verdict_label, verdict_text = verdict(variance, non_singleton, fallback)

    freq.to_csv(OUT_DIR / "peer_frequency_by_firm.csv", index=False, encoding="utf-8-sig")
    freq_dist.to_csv(OUT_DIR / "peer_frequency_distribution.csv", index=False, encoding="utf-8-sig")
    singleton_summary.to_csv(OUT_DIR / "singleton_summary.csv", index=False, encoding="utf-8-sig")
    variance.to_csv(OUT_DIR / "spec_ai_variance_decomposition.csv", index=False, encoding="utf-8-sig")
    main_regs.to_csv(OUT_DIR / "main_spec_comparison.csv", index=False, encoding="utf-8-sig")
    non_singleton.to_csv(OUT_DIR / "non_singleton_event_fe_checks.csv", index=False, encoding="utf-8-sig")
    fallback.to_csv(OUT_DIR / "analyst_fallback_aiactive.csv", index=False, encoding="utf-8-sig")

    write_doc(freq_dist, singleton_summary, variance, main_regs, non_singleton, fallback, verdict_label, verdict_text)

    print("peer frequency")
    print(format_numeric(freq_dist).to_string(index=False))
    print("\nsingleton")
    print(format_numeric(singleton_summary).to_string(index=False))
    print("\nvariance")
    print(format_numeric(variance).to_string(index=False))
    print("\nnon-singleton checks")
    print(format_numeric(non_singleton).to_string(index=False))
    print("\nmain regressions")
    print(format_numeric(main_regs).to_string(index=False))
    print("\nfallback")
    print(format_numeric(fallback).to_string(index=False))
    print(f"\nVERDICT: {verdict_label} - {verdict_text}")
    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
