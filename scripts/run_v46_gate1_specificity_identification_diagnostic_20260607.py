#!/usr/bin/env python3
"""Gate 1 diagnostic for whether specificity can carry identification."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v25_empirical_table_pack_20260604 as v25  # noqa: E402
import run_v28_v36_peer_main_effect_tables_20260605 as v28  # noqa: E402


RUN_ID = "v46_gate1_specificity_identification_diagnostic_20260607"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "110_v46_gate1_specificity_identification_diagnostic_20260607.md"


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


def load_panel() -> pd.DataFrame:
    event_panel = v28.load_event_panel()
    with_spec = v28.attach_specificity(event_panel)
    panel = v28.mechanism_sample(with_spec).copy()
    panel["peer_code"] = panel["peer_code"].astype(str).str.zfill(6)
    panel["event_key"] = panel["event_key"].astype(str)
    panel["ai"] = pd.to_numeric(panel["ai"], errors="coerce").fillna(0.0)
    return panel


def cluster_cov(x: np.ndarray, resid: np.ndarray, clusters: list[pd.Series]) -> np.ndarray:
    bread = np.linalg.pinv(x.T @ x)
    if len(clusters) == 1:
        meat = v25.cluster_meat(x, resid, clusters[0])
    elif len(clusters) == 2:
        c0, c1 = clusters
        meat0 = v25.cluster_meat(x, resid, c0)
        meat1 = v25.cluster_meat(x, resid, c1)
        pair = c0.astype(str) + "|" + c1.astype(str)
        meat_pair = v25.cluster_meat(x, resid, pair)
        meat = meat0 + meat1 - meat_pair
    else:
        raise ValueError("Only one-way or two-way clusters are supported.")
    return bread @ meat @ bread


def fit_absorbed(
    data: pd.DataFrame,
    outcome: str,
    xvars: list[str],
    fe_cols: list[str],
    key_var: str,
    cluster_peer_col: str = "peer_code",
) -> dict[str, object]:
    need = [outcome, *xvars, *fe_cols, "event_key", cluster_peer_col]
    d = data.dropna(subset=list(dict.fromkeys(need))).copy()
    out: dict[str, object] = {
        "outcome": outcome,
        "xvars": ",".join(xvars),
        "fe": "+".join(fe_cols) if fe_cols else "none",
        "key_var": key_var,
        "nobs": int(len(d)),
        "events": int(d["event_key"].nunique()) if len(d) else 0,
        "peer_firms": int(d[cluster_peer_col].nunique()) if len(d) else 0,
    }
    if len(d) < 30:
        out["status"] = "too_few_obs"
        return out
    if fe_cols:
        dm = v25.absorb_frame(d, [outcome, *xvars], fe_cols)
    else:
        dm = d[[outcome, *xvars]].astype(float).copy()

    residual_sd = {var: float(pd.to_numeric(dm[var], errors="coerce").std(ddof=0)) for var in xvars}
    keep_vars = [var for var in xvars if residual_sd[var] > 1e-12]
    out["key_resid_sd_after_fe"] = residual_sd.get(key_var, math.nan)
    out["absorbed_vars"] = ",".join(var for var in xvars if var not in keep_vars)
    if key_var not in keep_vars:
        out["status"] = "key_var_absorbed_by_fe"
        return out
    if not keep_vars:
        out["status"] = "all_x_absorbed"
        return out

    y = dm[outcome].to_numpy(dtype=float)
    x = dm[keep_vars].to_numpy(dtype=float)
    beta = np.linalg.pinv(x.T @ x) @ (x.T @ y)
    resid = y - x @ beta
    idx = keep_vars.index(key_var)

    cov_event = cluster_cov(x, resid, [d["event_key"]])
    cov_peer = cluster_cov(x, resid, [d[cluster_peer_col]])
    cov_two_way = cluster_cov(x, resid, [d["event_key"], d[cluster_peer_col]])

    coef = float(beta[idx])
    for label, cov in [("event", cov_event), ("peer", cov_peer), ("two_way", cov_two_way)]:
        se = math.sqrt(float(cov[idx, idx])) if float(cov[idx, idx]) >= 0 else math.nan
        z_value = coef / se if se and se > 0 else math.nan
        out[f"se_{label}"] = se
        out[f"z_{label}"] = z_value
        out[f"p_{label}"] = v25.p_from_z(z_value)
    out["coef"] = coef
    out["coef_fmt_event_cluster"] = f"{fmt(coef)}{stars(out.get('p_event'))}"
    out["se_fmt_event_cluster"] = f"({fmt(out.get('se_event'))})"
    out["coef_fmt_peer_cluster"] = f"{fmt(coef)}{stars(out.get('p_peer'))}"
    out["se_fmt_peer_cluster"] = f"({fmt(out.get('se_peer'))})"
    out["status"] = "estimated"
    return out


def add_effective_obs(panel: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    peer_counts = panel.groupby("peer_code")["event_key"].nunique()
    singleton_codes = set(peer_counts[peer_counts.eq(1)].index)
    for idx, row in out.iterrows():
        fe = str(row.get("fe", ""))
        if "peer_code" in fe:
            d = panel.copy()
            if str(row.get("sample", "")).startswith("AIActive=1"):
                d = d[d["ai"].eq(1)]
            elif str(row.get("sample", "")).startswith("AIActive=0"):
                d = d[d["ai"].eq(0)]
            singleton_obs = int(d["peer_code"].isin(singleton_codes).sum())
            out.loc[idx, "absorbed_no_contribution_obs"] = singleton_obs
            out.loc[idx, "effective_identification_obs"] = int(row.get("nobs", 0)) - singleton_obs
        else:
            out.loc[idx, "absorbed_no_contribution_obs"] = 0
            out.loc[idx, "effective_identification_obs"] = row.get("nobs", 0)
    return out


def run_original_prompt_specs(panel: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for sample_label, d in [("AIActive=1", panel[panel["ai"].eq(1)]), ("AIActive=0", panel[panel["ai"].eq(0)])]:
        for spec_label, fe_cols in [
            ("event_fe", ["event_key"]),
            ("event_plus_peer_fe", ["event_key", "peer_code"]),
        ]:
            res = fit_absorbed(
                d,
                "peer_car_0_p1_mm",
                ["spec_z", *v28.PRE_CONTROLS],
                fe_cols,
                "spec_z",
            )
            res.update({"test": "T1/T2_original_prompt", "sample": sample_label, "spec": spec_label})
            rows.append(res)
    return add_effective_obs(panel, pd.DataFrame(rows))


def run_feasible_specs(panel: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for sample_label, d in [("AIActive=1", panel[panel["ai"].eq(1)]), ("AIActive=0", panel[panel["ai"].eq(0)])]:
        for spec_label, fe_cols in [
            ("peer_industry_week_fe", ["peer_industry_week"]),
            ("peer_industry_week_plus_peer_fe", ["peer_industry_week", "peer_code"]),
        ]:
            res = fit_absorbed(
                d,
                "peer_car_0_p1_mm",
                ["spec_z", *v28.PRE_CONTROLS],
                fe_cols,
                "spec_z",
            )
            res.update({"test": "T1/T2_feasible_no_event_fe", "sample": sample_label, "spec": spec_label})
            rows.append(res)
    return add_effective_obs(panel, pd.DataFrame(rows))


def run_t3(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for spec_label, fe_cols in [
        ("event_fe", ["event_key"]),
        ("peer_industry_week_fe", ["peer_industry_week"]),
    ]:
        for key_var in ["spec_z", "ai", "spec_ai"]:
            res = fit_absorbed(
                panel,
                "peer_car_0_p1_mm",
                ["spec_z", "ai", "spec_ai", *v28.PRE_CONTROLS],
                fe_cols,
                key_var,
            )
            res.update({"test": "T3_full_sample_decomposition", "sample": "full", "spec": spec_label})
            rows.append(res)
    return pd.DataFrame(rows)


def run_t4(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    d = panel[panel["ai"].eq(1)].copy()
    for outcome, outcome_label in [
        ("peer_car_m1_p1_mm", "PeerCAR[-1,+1]"),
        ("peer_ar0_mm", "PeerAR[0]"),
    ]:
        res = fit_absorbed(
            d,
            outcome,
            ["spec_z", *v28.PRE_CONTROLS],
            ["peer_industry_week"],
            "spec_z",
        )
        res.update({"test": "T4_feasible_T1a_robustness", "sample": "AIActive=1", "spec": f"{outcome_label}_peer_industry_week_fe"})
        rows.append(res)
    res = fit_absorbed(
        d,
        "peer_car_0_p1_mm",
        ["legacy_detail_density_raw", *v28.PRE_CONTROLS],
        ["peer_industry_week"],
        "legacy_detail_density_raw",
    )
    res.update({"test": "T4_feasible_T1a_robustness", "sample": "AIActive=1", "spec": "raw_detail_density_peer_industry_week_fe"})
    rows.append(res)
    return pd.DataFrame(rows)


def format_numeric(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_numeric_dtype(out[col]):
            if col in {"nobs", "events", "peer_firms", "absorbed_no_contribution_obs", "effective_identification_obs"}:
                out[col] = out[col].map(lambda x: "" if pd.isna(x) else str(int(round(float(x)))))
            else:
                out[col] = out[col].map(lambda x: "" if pd.isna(x) else fmt(x, 4))
    return out


def compact(df: pd.DataFrame) -> pd.DataFrame:
    keep = [
        "test",
        "sample",
        "spec",
        "outcome",
        "key_var",
        "status",
        "coef",
        "se_event",
        "p_event",
        "se_peer",
        "p_peer",
        "nobs",
        "events",
        "peer_firms",
        "absorbed_no_contribution_obs",
        "effective_identification_obs",
        "key_resid_sd_after_fe",
        "absorbed_vars",
    ]
    return df[[c for c in keep if c in df.columns]].copy()


def verdict(original: pd.DataFrame, feasible: pd.DataFrame) -> tuple[str, str]:
    t1_peer = feasible[
        feasible["sample"].eq("AIActive=1")
        & feasible["spec"].eq("peer_industry_week_plus_peer_fe")
        & feasible["key_var"].eq("spec_z")
    ].iloc[0]
    t2_peer = feasible[
        feasible["sample"].eq("AIActive=0")
        & feasible["spec"].eq("peer_industry_week_plus_peer_fe")
        & feasible["key_var"].eq("spec_z")
    ].iloc[0]
    t1_sig = t1_peer.get("status") == "estimated" and pd.notna(t1_peer.get("p_event")) and float(t1_peer["p_event"]) < 0.05 and float(t1_peer["coef"]) < 0
    t2_sig = t2_peer.get("status") == "estimated" and pd.notna(t2_peer.get("p_event")) and float(t2_peer["p_event"]) < 0.10 and float(t2_peer["coef"]) < 0
    if t1_sig and not t2_sig:
        return (
            "GO under feasible no-event-FE peer-FE test",
            "原 prompt 的 event-FE 子样本规格不可识别；在可识别的 peer-industry-week + peer-FE 规格下，AIActive=1 子样本 Spec 显著为负，AIActive=0 子样本不显著。",
        )
    if not t1_sig:
        return (
            "DOWNGRADE",
            "原 prompt 的 event-FE 子样本规格不可识别；可识别的 AIActive=1 peer-FE 规格下 Spec 也不显著，specificity 不能作为 within-peer 主线，只能保留为 event-FE 交互异质性。",
        )
    return (
        "MIXED",
        "原 prompt 的 event-FE 子样本规格不可识别；可识别规格下 AIActive=1 和 AIActive=0 都呈显著负向，Spec 更像普遍负向信号而非 AI-active 竞争专属。",
    )


def write_doc(
    original: pd.DataFrame,
    feasible: pd.DataFrame,
    t3: pd.DataFrame,
    t4: pd.DataFrame,
    verdict_label: str,
    verdict_text: str,
) -> None:
    lines = [
        "# v46 Gate 1: Specificity Identification Diagnostic",
        "",
        "Date: 2026-06-07",
        "",
        "## Key Identification Note",
        "",
        "`Spec` is an event-level variable. Therefore, in AIActive-only or non-AIActive-only subsamples, `Spec` is constant within each event and is mechanically absorbed by event fixed effects. The original T1/T2 event-FE specifications cannot estimate a coefficient on `Spec`.",
        "",
        "For completeness, this run first reports the original prompt specifications as absorbed, then runs a feasible no-event-FE version with peer-industry-week fixed effects and an optional peer-firm fixed effect.",
        "",
        "## T1/T2 Original Prompt Specifications",
        "",
        markdown_table(format_numeric(compact(original))),
        "",
        "## T1/T2 Feasible Specifications",
        "",
        markdown_table(format_numeric(compact(feasible))),
        "",
        "## T3 Full-Sample Decomposition",
        "",
        markdown_table(format_numeric(compact(t3))),
        "",
        "## T4 Robustness for Feasible T1(a)",
        "",
        markdown_table(format_numeric(compact(t4))),
        "",
        "## Verdict",
        "",
        f"**{verdict_label}.** {verdict_text}",
        "",
        "## Writing Implication",
        "",
        "Do not write that `Spec` is identified in AIActive-only event-FE regressions. With event FE, the estimable object is the interaction `Spec x AIActivePeer`, because AIActive varies across peers within the same event. If the paper needs a within-peer specificity claim, it must use a no-event-FE design with time/industry controls and explain the different identifying variation.",
        "",
        "## Output Files",
        "",
        f"- `results/{RUN_ID}/t1_t2_original_prompt.csv`",
        f"- `results/{RUN_ID}/t1_t2_feasible_specs.csv`",
        f"- `results/{RUN_ID}/t3_full_sample_decomposition.csv`",
        f"- `results/{RUN_ID}/t4_feasible_robustness.csv`",
    ]
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    panel = load_panel()
    original = run_original_prompt_specs(panel)
    feasible = run_feasible_specs(panel)
    t3 = run_t3(panel)
    t4 = run_t4(panel)
    verdict_label, verdict_text = verdict(original, feasible)

    original.to_csv(OUT_DIR / "t1_t2_original_prompt.csv", index=False, encoding="utf-8-sig")
    feasible.to_csv(OUT_DIR / "t1_t2_feasible_specs.csv", index=False, encoding="utf-8-sig")
    t3.to_csv(OUT_DIR / "t3_full_sample_decomposition.csv", index=False, encoding="utf-8-sig")
    t4.to_csv(OUT_DIR / "t4_feasible_robustness.csv", index=False, encoding="utf-8-sig")
    write_doc(original, feasible, t3, t4, verdict_label, verdict_text)

    print("T1/T2 original")
    print(format_numeric(compact(original)).to_string(index=False))
    print("\nT1/T2 feasible")
    print(format_numeric(compact(feasible)).to_string(index=False))
    print("\nT3")
    print(format_numeric(compact(t3)).to_string(index=False))
    print("\nT4")
    print(format_numeric(compact(t4)).to_string(index=False))
    print(f"\nVERDICT: {verdict_label} - {verdict_text}")
    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
