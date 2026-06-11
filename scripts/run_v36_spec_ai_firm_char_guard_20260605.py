#!/usr/bin/env python3
"""Guard test for Specificity x AIActivePeer.

This pass asks whether the current Spec x AIActivePeer result survives after
adding interactions between disclosure specificity and observable peer firm
style characteristics:

    Spec x Size, Spec x Beta, Spec x Volatility, Spec x MB.

If Spec x AIActivePeer collapses here, AIActivePeer is likely proxying for a
firm-type/style response rather than competitive AI exposure.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v25_empirical_table_pack_20260604 as v25  # noqa: E402


RUN_ID = "v36_spec_ai_firm_char_guard_20260605"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "100_v36_spec_ai_firm_char_guard_20260605.md"

PANEL_PATH = ROOT / "results/v31_pom_analog_cross_section_20260605/analysis_panel_pom_analog.csv.gz"
RETURNS_PATH = ROOT / "results/v6_supplement_market_model_placebo_20260524/stock_returns_with_market_model_params.csv"
V33_PANEL_PATH = ROOT / "results/v33_supplement_data_probe_20260605/panel_with_supplement_flags.csv.gz"
FI_T10_PATH = Path(
    "/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/上市公司财务信息/FI_T10.xlsx"
)

PRE_CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
POM_CONTROLS = [
    "peer_prior_ai_patent",
    "peer_sales_growth_z",
    "product_distance_z",
    "peer_industry_hhi_z",
    "peer_log_revenue_z",
    *PRE_CONTROLS,
]
CORE = ["ai", "spec_ai"]
STYLE_VARS = ["peer_size_z", "peer_beta_z", "peer_volatility_z", "peer_mb_z"]
STYLE_INTERACTIONS = [f"spec_x_{v.removeprefix('peer_').removesuffix('_z')}" for v in STYLE_VARS]


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = re.sub(r"\.0$", "", str(value).strip())
    digits = re.sub(r"\D", "", text)
    return digits.zfill(6)[-6:] if digits else ""


def winsor_z(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    return v25.zscore(v25.winsorize(x))


def p_from_z(z_value: float) -> float:
    return v25.p_from_z(z_value)


def stars(p_value: object) -> str:
    if p_value is None or pd.isna(p_value):
        return ""
    p = float(p_value)
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


def fmt_coef(res: dict[str, object], var: str) -> str:
    coef = res.get(f"{var}_coef")
    if coef is None or pd.isna(coef):
        return ""
    return f"{fmt(coef)}{stars(res.get(f'{var}_p'))}"


def fmt_se(res: dict[str, object], var: str) -> str:
    se = res.get(f"{var}_se")
    if se is None or pd.isna(se):
        return ""
    return f"({fmt(se)})"


def load_panel() -> pd.DataFrame:
    d = pd.read_csv(PANEL_PATH, dtype={"event_key": str, "peer_code": str, "focal_code": str}, low_memory=False)
    d["peer_code"] = d["peer_code"].map(code6)
    d["focal_code"] = d["focal_code"].map(code6)
    d["date_0"] = pd.to_datetime(d["date_0"], errors="coerce")
    d["fiscal_year_pre"] = pd.to_numeric(d["fiscal_year_pre"], errors="coerce").astype("Int64")
    for col in [
        "peer_ar0_mm",
        "peer_car_0_p1_mm",
        "ai",
        "spec_z",
        "spec_ai",
        *POM_CONTROLS,
    ]:
        if col in d.columns:
            d[col] = pd.to_numeric(d[col], errors="coerce")
    return d


def attach_pollution_flags(d: pd.DataFrame) -> pd.DataFrame:
    if not V33_PANEL_PATH.exists():
        d["drop_genai_or_major"] = True
        return d
    v33_cols = [
        "event_key",
        "peer_code",
        "peer_own_strict_genai_m2_p2",
        "peer_major_announcement_m2_p2",
    ]
    v33 = pd.read_csv(V33_PANEL_PATH, usecols=lambda c: c in v33_cols, dtype={"event_key": str, "peer_code": str})
    v33["peer_code"] = v33["peer_code"].map(code6)
    v33 = v33.drop_duplicates(["event_key", "peer_code"])
    out = d.merge(v33, on=["event_key", "peer_code"], how="left")
    own = out["peer_own_strict_genai_m2_p2"].fillna(False).astype(bool)
    major = out["peer_major_announcement_m2_p2"].fillna(False).astype(bool)
    out["drop_genai_or_major"] = ~(own | major)
    return out


def load_fi_t10_style() -> pd.DataFrame:
    usecols = ["Stkcd", "Accper", "F100401A", "F100801A", "F100802A", "F101001A", "F101002A"]
    fi = pd.read_excel(FI_T10_PATH, usecols=lambda c: c in usecols, skiprows=[1, 2])
    fi = fi.rename(
        columns={
            "Stkcd": "peer_code",
            "Accper": "accper",
            "F100401A": "pb",
            "F100801A": "market_value_a",
            "F100802A": "market_value_b",
            "F101001A": "bm_a",
            "F101002A": "bm_b",
        }
    )
    fi["peer_code"] = fi["peer_code"].map(code6)
    fi["accper"] = pd.to_datetime(fi["accper"], errors="coerce")
    fi["fiscal_year_pre"] = fi["accper"].dt.year.astype("Int64")
    fi = fi[fi["accper"].dt.month.eq(12) & fi["accper"].dt.day.eq(31)].copy()
    for col in ["pb", "market_value_a", "market_value_b", "bm_a", "bm_b"]:
        fi[col] = pd.to_numeric(fi[col], errors="coerce")
    fi["market_value"] = fi["market_value_a"].combine_first(fi["market_value_b"])
    fi["mb"] = fi["pb"]
    bm = fi["bm_a"].combine_first(fi["bm_b"])
    fi.loc[fi["mb"].isna() & bm.gt(0), "mb"] = 1.0 / bm
    fi["peer_size_raw"] = np.log(fi["market_value"].where(fi["market_value"].gt(0)))
    fi["peer_mb_raw"] = fi["mb"].where(fi["mb"].gt(0))
    fi = fi.sort_values(["peer_code", "fiscal_year_pre", "accper"])
    fi = fi.drop_duplicates(["peer_code", "fiscal_year_pre"], keep="last")
    return fi[["peer_code", "fiscal_year_pre", "peer_size_raw", "peer_mb_raw"]]


def attach_annual_style(d: pd.DataFrame) -> pd.DataFrame:
    fi = load_fi_t10_style()
    out = d.merge(fi, on=["peer_code", "fiscal_year_pre"], how="left")
    out["peer_size_z"] = winsor_z(out["peer_size_raw"])
    out["peer_mb_z"] = winsor_z(out["peer_mb_raw"])
    return out


def load_return_style(d: pd.DataFrame) -> pd.DataFrame:
    peer_codes = set(d["peer_code"].dropna().map(code6))
    usecols = ["peer_code", "date", "ret", "beta_mm", "est_obs", "trdsta", "limit_status"]
    chunks = []
    for chunk in pd.read_csv(RETURNS_PATH, usecols=usecols, dtype={"peer_code": str}, chunksize=1_500_000):
        chunk["peer_code"] = chunk["peer_code"].map(code6)
        sub = chunk[chunk["peer_code"].isin(peer_codes)].copy()
        if not sub.empty:
            chunks.append(sub)
    if not chunks:
        return pd.DataFrame(columns=["peer_code", "date_0", "peer_beta_raw", "peer_volatility_raw", "peer_est_obs"])
    r = pd.concat(chunks, ignore_index=True)
    r["date_0"] = pd.to_datetime(r["date"], errors="coerce")
    for col in ["ret", "beta_mm", "est_obs", "trdsta", "limit_status"]:
        r[col] = pd.to_numeric(r[col], errors="coerce")
    r = r.sort_values(["peer_code", "date_0"])
    # Match the existing market-model logic: 200 trading days, at least 120 obs,
    # shifted by 11 trading days to avoid event-window leakage.
    r["peer_volatility_raw"] = (
        r.groupby("peer_code", sort=False)["ret"]
        .transform(lambda s: s.rolling(200, min_periods=120).std().shift(11))
    )
    r["peer_beta_raw"] = r["beta_mm"]
    return r[["peer_code", "date_0", "peer_beta_raw", "peer_volatility_raw", "est_obs"]].rename(
        columns={"est_obs": "peer_est_obs"}
    )


def attach_return_style(d: pd.DataFrame) -> pd.DataFrame:
    r = load_return_style(d)
    out = d.merge(r, on=["peer_code", "date_0"], how="left")
    out["peer_beta_z"] = winsor_z(out["peer_beta_raw"])
    out["peer_volatility_z"] = winsor_z(out["peer_volatility_raw"])
    return out


def add_interactions(d: pd.DataFrame) -> pd.DataFrame:
    out = d.copy()
    for var in STYLE_VARS:
        short = var.removeprefix("peer_").removesuffix("_z")
        out[f"spec_x_{short}"] = out["spec_z"] * out[var]
    return out


def cluster_cov(x: np.ndarray, resid: np.ndarray, d: pd.DataFrame, cluster_mode: str) -> np.ndarray:
    if cluster_mode == "event":
        return v25.cluster_meat(x, resid, d["event_key"])
    if cluster_mode == "event_peer":
        meat_event = v25.cluster_meat(x, resid, d["event_key"])
        meat_peer = v25.cluster_meat(x, resid, d["peer_code"])
        pair_group = d["event_key"].astype(str) + "|" + d["peer_code"].astype(str)
        meat_pair = v25.cluster_meat(x, resid, pair_group)
        return meat_event + meat_peer - meat_pair
    raise ValueError(f"unknown cluster_mode={cluster_mode}")


def fit_absorbed(
    data: pd.DataFrame,
    outcome: str,
    xvars: list[str],
    fe_cols: list[str],
    cluster_mode: str = "event_peer",
) -> dict[str, object] | None:
    need = list(dict.fromkeys([outcome, *xvars, *fe_cols, "event_key", "peer_code", "focal_code"]))
    d = data.dropna(subset=need).copy()
    if len(d) < 80 or d["event_key"].nunique() < 8 or d["peer_code"].nunique() < 20:
        return None
    dm = v25.absorb_frame(d, [outcome, *xvars], fe_cols)
    y = dm[outcome].to_numpy(dtype=float)
    x = dm[xvars].to_numpy(dtype=float)
    keep = np.nanstd(x, axis=0) > 1e-12
    dropped = [var for var, ok in zip(xvars, keep) if not ok]
    if not keep.all():
        xvars = [var for var, ok in zip(xvars, keep) if ok]
        x = x[:, keep]
    if x.shape[1] == 0:
        return None
    bread = np.linalg.pinv(x.T @ x)
    beta = bread @ (x.T @ y)
    resid = y - x @ beta
    meat = cluster_cov(x, resid, d, cluster_mode)
    cov = bread @ meat @ bread
    within_tss = float(np.sum((y - y.mean()) ** 2))
    rss = float(np.sum(resid**2))
    raw_y = d[outcome].to_numpy(dtype=float)
    overall_tss = float(np.sum((raw_y - raw_y.mean()) ** 2))
    out: dict[str, object] = {
        "nobs": int(len(d)),
        "events": int(d["event_key"].nunique()),
        "focal_firms": int(d["focal_code"].nunique()),
        "peer_firms": int(d["peer_code"].nunique()),
        "within_r2": 1.0 - rss / within_tss if within_tss > 0 else math.nan,
        "overall_r2": 1.0 - rss / overall_tss if overall_tss > 0 else math.nan,
        "fe_cols": ",".join(fe_cols),
        "cluster_mode": cluster_mode,
        "dropped_xvars": "|".join(dropped),
    }
    for i, var in enumerate(xvars):
        var_se = math.sqrt(float(cov[i, i])) if float(cov[i, i]) >= 0 else math.nan
        coef = float(beta[i])
        z_value = coef / var_se if var_se and var_se > 0 else math.nan
        out[f"{var}_coef"] = coef
        out[f"{var}_se"] = var_se
        out[f"{var}_z"] = z_value
        out[f"{var}_p"] = p_from_z(z_value)
    return out


def run_models(d: pd.DataFrame) -> pd.DataFrame:
    specs = [
        ("M1_base", "Base v31 controls", CORE + POM_CONTROLS),
        ("M2_add_style_main", "Add firm-style main effects", CORE + POM_CONTROLS + STYLE_VARS),
        (
            "M3_add_each_interaction",
            "Add Spec x firm-style interactions",
            CORE + POM_CONTROLS + STYLE_VARS + STYLE_INTERACTIONS,
        ),
    ]
    # Single-interaction diagnostics make it easy to see which firm-type proxy,
    # if any, is absorbing the original Spec x AIActivePeer coefficient.
    for v, inter in zip(STYLE_VARS, STYLE_INTERACTIONS, strict=False):
        specs.append((f"S_{inter}", f"Only {inter}", CORE + POM_CONTROLS + [v, inter]))

    samples = {
        "all": pd.Series(True, index=d.index),
        "drop_peer_genai_or_major": d["drop_genai_or_major"].fillna(True).astype(bool),
    }
    outcomes = [("PeerCAR[0,+1]", "peer_car_0_p1_mm"), ("PeerAR[0]", "peer_ar0_mm")]
    rows = []
    for sample_name, mask in samples.items():
        ds = d[mask].copy()
        for outcome_label, outcome in outcomes:
            for spec_id, spec_label, xvars in specs:
                for cluster_mode in ["event_peer", "event"]:
                    res = fit_absorbed(ds, outcome, xvars, ["event_key"], cluster_mode=cluster_mode)
                    row = {
                        "sample": sample_name,
                        "outcome_label": outcome_label,
                        "outcome": outcome,
                        "spec_id": spec_id,
                        "spec_label": spec_label,
                        "xvars": "|".join(xvars),
                        "fe": "event_key",
                        "cluster": cluster_mode,
                    }
                    if res:
                        row.update(res)
                    rows.append(row)
    return pd.DataFrame(rows)


def coverage(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in [
        "peer_size_raw",
        "peer_mb_raw",
        "peer_beta_raw",
        "peer_volatility_raw",
        "peer_est_obs",
        *STYLE_VARS,
        *STYLE_INTERACTIONS,
        "spec_ai",
    ]:
        x = d[col] if col in d.columns else pd.Series(index=d.index, dtype=float)
        rows.append(
            {
                "variable": col,
                "nonmissing_rows": int(x.notna().sum()),
                "nonmissing_events": int(d.loc[x.notna(), "event_key"].nunique()) if col in d.columns else 0,
                "mean": float(pd.to_numeric(x, errors="coerce").mean()) if pd.to_numeric(x, errors="coerce").notna().any() else math.nan,
                "std": float(pd.to_numeric(x, errors="coerce").std(ddof=0)) if pd.to_numeric(x, errors="coerce").notna().any() else math.nan,
            }
        )
    return pd.DataFrame(rows)


def compact_table(results: pd.DataFrame) -> pd.DataFrame:
    keep = results[
        results["cluster"].eq("event_peer")
        & results["outcome_label"].eq("PeerCAR[0,+1]")
        & results["sample"].isin(["all", "drop_peer_genai_or_major"])
        & results["spec_id"].isin(["M1_base", "M2_add_style_main", "M3_add_each_interaction"])
    ].copy()
    rows = []
    for r in keep.itertuples(index=False):
        rec = {
            "sample": r.sample,
            "model": r.spec_id,
            "label": r.spec_label,
            "Spec x AIActive": fmt_coef(r._asdict(), "spec_ai"),
            "se": fmt_se(r._asdict(), "spec_ai"),
            "p": fmt(r._asdict().get("spec_ai_p")),
            "N": getattr(r, "nobs", ""),
            "events": getattr(r, "events", ""),
            "peer_firms": getattr(r, "peer_firms", ""),
            "within_r2": fmt(getattr(r, "within_r2", math.nan), 3),
        }
        for var in STYLE_INTERACTIONS:
            rec[var] = fmt_coef(r._asdict(), var)
        rows.append(rec)
    return pd.DataFrame(rows)


def write_doc(results: pd.DataFrame, cov: pd.DataFrame, compact: pd.DataFrame) -> None:
    main = results[
        results["sample"].eq("all")
        & results["outcome_label"].eq("PeerCAR[0,+1]")
        & results["spec_id"].isin(["M1_base", "M2_add_style_main", "M3_add_each_interaction"])
    ].copy()
    main_rows = []
    for r in main.itertuples(index=False):
        rd = r._asdict()
        main_rows.append(
            {
                "cluster": r.cluster,
                "model": r.spec_id,
                "Spec x AIActive": fmt_coef(rd, "spec_ai"),
                "se": fmt_se(rd, "spec_ai"),
                "p": fmt(rd.get("spec_ai_p")),
                "N": getattr(r, "nobs", ""),
                "events": getattr(r, "events", ""),
                "peer_firms": getattr(r, "peer_firms", ""),
            }
        )
    main_tbl = pd.DataFrame(main_rows)
    full = results[
        results["sample"].eq("all")
        & results["outcome_label"].eq("PeerCAR[0,+1]")
        & results["spec_id"].eq("M3_add_each_interaction")
        & results["cluster"].eq("event_peer")
    ].copy()
    if not full.empty:
        r = full.iloc[0].to_dict()
        coef = r.get("spec_ai_coef")
        p = r.get("spec_ai_p")
        verdict = (
            "SURVIVES"
            if pd.notna(coef) and coef < 0 and pd.notna(p) and p < 0.10
            else "DOES NOT SURVIVE"
        )
        verdict_line = f"`Spec x AIActivePeer` in the full guard model: {fmt(coef)}{stars(p)}, p={fmt(p)} -> **{verdict}** at the 10% threshold."
    else:
        verdict_line = "Full guard model did not estimate."

    lines = [
        "# v36 Spec x AIActivePeer firm-characteristic guard",
        "",
        "## Scope",
        "",
        "- Input panel: v31 POM-analog analysis panel.",
        "- Purpose: test Claude's key objection that `AIActivePeer` may proxy for peer firm type/style rather than AI competition exposure.",
        "- Dependent variable: peer `CAR[0,+1]` is the decision variable; `AR[0]` is retained as auxiliary output.",
        "- Fixed effects: event fixed effects.",
        "- Main standard errors: two-way clustered by event and peer firm. Event-only clustered estimates are also saved because Claude requested event-level clustering.",
        "- Firm-style controls: annual market size and MB/PB from CSMAR `FI_T10`; rolling beta and return volatility from the existing 200-day/skip-11 market-model return cache.",
        "",
        "## Verdict",
        "",
        verdict_line,
        "",
        "Decision rule: if the full model keeps a negative `Spec x AIActivePeer` with p < 0.10, the AIActive mechanism survives this guard. If not, the current mechanism has to be treated as unresolved.",
        "",
        "## Main CAR[0,+1] Guard Table",
        "",
        main_tbl.to_markdown(index=False),
        "",
        "## Compact Two-Way Clustered Table",
        "",
        compact.to_markdown(index=False),
        "",
        "## Variable Coverage",
        "",
        cov.to_markdown(index=False),
        "",
        "## Output Files",
        "",
        f"- `results/{RUN_ID}/analysis_panel_with_firm_chars.csv.gz`",
        f"- `results/{RUN_ID}/spec_ai_firm_char_guard_regressions.csv`",
        f"- `results/{RUN_ID}/spec_ai_firm_char_guard_compact.csv`",
        f"- `results/{RUN_ID}/firm_char_coverage.csv`",
    ]
    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = load_panel()
    d = attach_pollution_flags(d)
    d = attach_annual_style(d)
    d = attach_return_style(d)
    d = add_interactions(d)
    cov = coverage(d)
    results = run_models(d)
    compact = compact_table(results)
    d.to_csv(OUT_DIR / "analysis_panel_with_firm_chars.csv.gz", index=False, compression="gzip")
    cov.to_csv(OUT_DIR / "firm_char_coverage.csv", index=False)
    results.to_csv(OUT_DIR / "spec_ai_firm_char_guard_regressions.csv", index=False)
    compact.to_csv(OUT_DIR / "spec_ai_firm_char_guard_compact.csv", index=False)
    write_doc(results, cov, compact)
    print(f"wrote {OUT_DIR}")
    focus = results[
        results["outcome_label"].eq("PeerCAR[0,+1]")
        & results["sample"].eq("all")
        & results["spec_id"].isin(["M1_base", "M2_add_style_main", "M3_add_each_interaction"])
    ][
        [
            "cluster",
            "spec_id",
            "nobs",
            "events",
            "peer_firms",
            "spec_ai_coef",
            "spec_ai_se",
            "spec_ai_p",
            "spec_x_size_coef",
            "spec_x_size_p",
            "spec_x_beta_coef",
            "spec_x_beta_p",
            "spec_x_volatility_coef",
            "spec_x_volatility_p",
            "spec_x_mb_coef",
            "spec_x_mb_p",
        ]
    ]
    print(focus.to_string(index=False))


if __name__ == "__main__":
    main()
