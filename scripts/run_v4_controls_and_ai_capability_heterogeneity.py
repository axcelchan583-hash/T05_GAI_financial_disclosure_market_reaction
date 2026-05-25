#!/usr/bin/env python3
"""Run peer controls and AI-capability heterogeneity for v4 peer spillovers."""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "results" / "v4_peer_spillover_csmar_event_study"
OUT_DIR = ROOT / "results" / "v4_peer_spillover_controls_heterogeneity"

PANEL_TOP3 = INPUT_DIR / "v4_peer_event_with_car_csmar_top3.csv"
PANEL_TOP5 = INPUT_DIR / "v4_peer_event_with_car_csmar_top5.csv"
PANEL_TOP10 = INPUT_DIR / "v4_peer_event_with_car_csmar_top10.csv"
STOCK_CACHE = INPUT_DIR / "v4_csmar_peer_daily_returns_subset.csv"
IRQA_FIRM_DAY = ROOT / "results" / "plan_a_irqa_multichannel_event_study" / "plan_a_irqa_strict_firm_day_events.csv"
PUBLIC_IRQA = ROOT / "results" / "v8_3_external_evidence_link_pilot" / "public_irqa_events_for_linking.csv"
FORMAL_EVENTS = ROOT / "results" / "v3_genai_specificity_car_pilot" / "cninfo_genai_event_candidates_with_specificity.csv"
ANNUAL_EVIDENCE = ROOT / "results" / "v8_3_external_evidence_link_pilot" / "firm_external_evidence_panel_2024.csv"


OUTCOMES = ["peer_ar0", "peer_car_0_p1", "peer_car_m1_p1"]


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = re.sub(r"\.0$", "", text)
    text = re.sub(r"\D", "", text)
    return text.zfill(6) if text else ""


def zscore(series: pd.Series) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce")
    sd = x.std(ddof=0)
    if not np.isfinite(sd) or sd == 0:
        return x * np.nan
    return (x - x.mean()) / sd


def read_panel(path: Path, topn: int) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"peer_code": str, "focal_code": str})
    df["peer_code"] = df["peer_code"].map(code6)
    df["focal_code"] = df["focal_code"].map(code6)
    df["raw_event_date"] = pd.to_datetime(df["raw_event_date"], errors="coerce")
    df["event_date_for_car"] = pd.to_datetime(df["event_date_for_car"], errors="coerce")
    df["topn"] = topn
    for col in [
        "specificity",
        "product_similarity",
        "x_specificity_similarity",
        "peer_rank",
        "peer_beta",
        *OUTCOMES,
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def read_stock_cache() -> pd.DataFrame:
    stock = pd.read_csv(STOCK_CACHE, dtype={"peer_code": str})
    stock["peer_code"] = stock["peer_code"].map(code6)
    stock["date"] = pd.to_datetime(stock["date"], errors="coerce")
    for col in ["ret_wd", "market_type", "trdsta", "limit_status"]:
        stock[col] = pd.to_numeric(stock[col], errors="coerce")
    return stock.dropna(subset=["peer_code", "date"]).sort_values(["peer_code", "date"])


def add_pre_event_stock_controls(panel: pd.DataFrame, stock: pd.DataFrame) -> pd.DataFrame:
    stock_by_peer = {code: sub.sort_values("date") for code, sub in stock.groupby("peer_code", sort=False)}
    rows: list[dict[str, object]] = []
    for _, row in panel.iterrows():
        peer = row["peer_code"]
        event_date = row["event_date_for_car"]
        firm = stock_by_peer.get(peer)
        if firm is None or pd.isna(event_date):
            rows.append(
                {
                    "pre_mom_60": math.nan,
                    "pre_vol_120": math.nan,
                    "pre_absret_60": math.nan,
                    "market_type_pre": math.nan,
                }
            )
            continue
        hist = firm[firm["date"] < event_date].tail(130).copy()
        mom = hist.tail(60)["ret_wd"].dropna()
        vol = hist.tail(120)["ret_wd"].dropna()
        last = hist.tail(1)
        rows.append(
            {
                "pre_mom_60": float(np.prod(1.0 + mom) - 1.0) if len(mom) >= 40 else math.nan,
                "pre_vol_120": float(vol.std(ddof=1)) if len(vol) >= 80 else math.nan,
                "pre_absret_60": float(mom.abs().mean()) if len(mom) >= 40 else math.nan,
                "market_type_pre": int(last["market_type"].iloc[0]) if not last.empty and pd.notna(last["market_type"].iloc[0]) else math.nan,
            }
        )
    out = panel.join(pd.DataFrame(rows, index=panel.index))
    for col in ["peer_beta", "pre_mom_60", "pre_vol_120", "pre_absret_60", "peer_rank"]:
        out[f"z_{col}"] = zscore(out[col])
    out["is_chinext_or_star"] = out["market_type_pre"].isin([16, 32]).astype(int)
    return out


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
    return events[events["code"].ne("") & events["evidence_date"].notna()].drop_duplicates()


def load_annual_ai_codes() -> set[str]:
    if not ANNUAL_EVIDENCE.exists():
        return set()
    annual = pd.read_csv(ANNUAL_EVIDENCE)
    annual["code"] = annual["Symbol"].map(code6)
    annual["n_claim_sentences"] = pd.to_numeric(annual["n_claim_sentences"], errors="coerce")
    return set(annual.loc[(annual["code"].ne("")) & (annual["n_claim_sentences"] > 0), "code"])


def add_ai_capability(panel: pd.DataFrame) -> pd.DataFrame:
    evidence = load_public_evidence_events()
    annual_codes = load_annual_ai_codes()

    evidence_by_code = {
        code: sorted(sub["evidence_date"].tolist())
        for code, sub in evidence.groupby("code", sort=False)
    }

    prior_public = []
    prior_annual = []
    for _, row in panel.iterrows():
        peer = row["peer_code"]
        event_date = row["raw_event_date"]
        dates = evidence_by_code.get(peer, [])
        prior_public.append(int(any(d < event_date for d in dates)) if pd.notna(event_date) else 0)
        prior_annual.append(int(peer in annual_codes))

    out = panel.copy()
    out["peer_has_prior_public_genai_event"] = prior_public
    out["peer_has_annual_report_genai_2024"] = prior_annual
    out["peer_has_pre_public_or_annual_ai"] = (
        (out["peer_has_prior_public_genai_event"] == 1)
        | (out["peer_has_annual_report_genai_2024"] == 1)
    ).astype(int)

    out["low_peer_ai_capability_strict"] = 1 - out["peer_has_prior_public_genai_event"]
    out["low_peer_ai_capability_broad"] = 1 - out["peer_has_pre_public_or_annual_ai"]

    for low_col in ["low_peer_ai_capability_strict", "low_peer_ai_capability_broad"]:
        suffix = low_col.replace("low_peer_ai_capability_", "")
        out[f"x_specsim_low_{suffix}"] = out["x_specificity_similarity"] * out[low_col]
        out[f"sim_low_{suffix}"] = out["product_similarity"] * out[low_col]
    return out


def regression(label: str, outcome: str, formula: str, data: pd.DataFrame) -> dict[str, object]:
    used = data.dropna(subset=[outcome, "event_id", "peer_code"]).copy()
    terms = [
        "x_specificity_similarity",
        "x_specsim_low_strict",
        "x_specsim_low_broad",
    ]
    row: dict[str, object] = {
        "model": label,
        "outcome": outcome,
        "formula": formula,
        "nobs": int(len(used)),
        "events": int(used["event_id"].nunique()),
        "peer_firms": int(used["peer_code"].nunique()),
    }
    try:
        model = smf.ols(formula, data=used).fit(
            cov_type="cluster",
            cov_kwds={"groups": used["event_id"]},
        )
    except Exception as exc:  # noqa: BLE001
        row["error"] = str(exc)
        return row

    row["nobs"] = int(model.nobs)
    row["r2"] = float(model.rsquared)
    for term in terms:
        if term in model.params.index:
            row[f"coef_{term}"] = model.params[term]
            row[f"se_{term}"] = model.bse[term]
            row[f"t_{term}"] = model.tvalues[term]
            row[f"p_{term}"] = model.pvalues[term]

    for variant in ["strict", "broad"]:
        low_term = f"x_specsim_low_{variant}"
        if "x_specificity_similarity" in model.params.index and low_term in model.params.index:
            test = model.t_test(f"x_specificity_similarity + {low_term} = 0")
            row[f"coef_low_effect_{variant}"] = (
                model.params["x_specificity_similarity"] + model.params[low_term]
            )
            row[f"se_low_effect_{variant}"] = float(np.asarray(test.sd).ravel()[0])
            row[f"t_low_effect_{variant}"] = float(np.asarray(test.tvalue).ravel()[0])
            row[f"p_low_effect_{variant}"] = float(np.asarray(test.pvalue).ravel()[0])
    return row


def run_tables(panel: pd.DataFrame, topn: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    clean = panel[
        (panel["normal_trading_m1_p1"] == 1)
        & (panel["no_limit_m1_p1"] == 1)
        & (panel["obs_car_m1_p1"] == 3)
    ].copy()

    controls = "z_peer_beta + z_pre_mom_60 + z_pre_vol_120 + z_pre_absret_60 + is_chinext_or_star + z_peer_rank"
    baseline = "product_similarity + x_specificity_similarity + C(event_id)"
    control_formula = f"{baseline} + {controls}"
    peer_fe_formula = f"{baseline} + {controls} + C(peer_code)"

    rows: list[dict[str, object]] = []
    for sample_name, sample in [("raw", panel), ("clean", clean)]:
        for outcome in OUTCOMES:
            rows.append(regression(f"top{topn}_{sample_name}_baseline", outcome, f"{outcome} ~ {baseline}", sample))
            rows.append(regression(f"top{topn}_{sample_name}_controls", outcome, f"{outcome} ~ {control_formula}", sample))
            rows.append(regression(f"top{topn}_{sample_name}_controls_peerfe", outcome, f"{outcome} ~ {peer_fe_formula}", sample))

    controls_table = pd.DataFrame(rows)

    hetero_rows: list[dict[str, object]] = []
    for low_variant in ["strict", "broad"]:
        low_col = f"low_peer_ai_capability_{low_variant}"
        x_low = f"x_specsim_low_{low_variant}"
        sim_low = f"sim_low_{low_variant}"
        hetero_base = (
            "product_similarity + x_specificity_similarity + "
            f"{low_col} + {sim_low} + {x_low} + C(event_id)"
        )
        hetero_controls = f"{hetero_base} + {controls}"
        for sample_name, sample in [("raw", panel), ("clean", clean)]:
            for outcome in OUTCOMES:
                hetero_rows.append(
                    regression(
                        f"top{topn}_{sample_name}_hetero_{low_variant}",
                        outcome,
                        f"{outcome} ~ {hetero_base}",
                        sample,
                    )
                )
                hetero_rows.append(
                    regression(
                        f"top{topn}_{sample_name}_hetero_{low_variant}_controls",
                        outcome,
                        f"{outcome} ~ {hetero_controls}",
                        sample,
                    )
                )

    hetero_table = pd.DataFrame(hetero_rows)
    return controls_table, hetero_table


def write_diagnostics(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for topn, sub in panel.groupby("topn"):
        rows.append(
            {
                "topn": int(topn),
                "rows": len(sub),
                "events": sub["event_id"].nunique(),
                "peer_firms": sub["peer_code"].nunique(),
                "prior_public_share": sub["peer_has_prior_public_genai_event"].mean(),
                "annual_genai_share": sub["peer_has_annual_report_genai_2024"].mean(),
                "low_strict_share": sub["low_peer_ai_capability_strict"].mean(),
                "low_broad_share": sub["low_peer_ai_capability_broad"].mean(),
                "pre_controls_complete_share": sub[
                    ["z_peer_beta", "z_pre_mom_60", "z_pre_vol_120", "z_pre_absret_60"]
                ].notna().all(axis=1).mean(),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stock = read_stock_cache()

    panels = []
    panel_specs = [(3, PANEL_TOP3), (5, PANEL_TOP5)]
    if PANEL_TOP10.exists():
        panel_specs.append((10, PANEL_TOP10))

    for topn, path in panel_specs:
        panel = read_panel(path, topn=topn)
        panel = add_pre_event_stock_controls(panel, stock)
        panel = add_ai_capability(panel)
        panel.to_csv(OUT_DIR / f"v4_peer_event_controls_heterogeneity_top{topn}.csv", index=False)
        controls, hetero = run_tables(panel, topn=topn)
        controls.to_csv(OUT_DIR / f"v4_controls_regression_top{topn}.csv", index=False)
        hetero.to_csv(OUT_DIR / f"v4_ai_capability_heterogeneity_top{topn}.csv", index=False)
        panels.append(panel)

    combined = pd.concat(panels, ignore_index=True)
    diagnostics = write_diagnostics(combined)
    diagnostics.to_csv(OUT_DIR / "v4_controls_heterogeneity_diagnostics.csv", index=False)

    controls_all = pd.concat(
        [pd.read_csv(OUT_DIR / f"v4_controls_regression_top{topn}.csv") for topn, _ in panel_specs],
        ignore_index=True,
    )
    hetero_all = pd.concat(
        [pd.read_csv(OUT_DIR / f"v4_ai_capability_heterogeneity_top{topn}.csv") for topn, _ in panel_specs],
        ignore_index=True,
    )
    controls_all.to_csv(OUT_DIR / "v4_controls_regression_all.csv", index=False)
    hetero_all.to_csv(OUT_DIR / "v4_ai_capability_heterogeneity_all.csv", index=False)

    print("Diagnostics:")
    print(diagnostics.to_string(index=False))
    print("\nClosest control-spec rows:")
    print(
        controls_all.sort_values("p_x_specificity_similarity")
        .head(8)[
            [
                "model",
                "outcome",
                "coef_x_specificity_similarity",
                "se_x_specificity_similarity",
                "p_x_specificity_similarity",
                "nobs",
                "events",
                "peer_firms",
            ]
        ]
        .to_string(index=False)
    )
    print("\nClosest heterogeneity rows:")
    print(
        hetero_all.sort_values(
            [
                "p_x_specsim_low_strict",
                "p_x_specsim_low_broad",
            ],
            na_position="last",
        )
        .head(12)[
            [
                "model",
                "outcome",
                "coef_x_specificity_similarity",
                "p_x_specificity_similarity",
                "coef_x_specsim_low_strict",
                "p_x_specsim_low_strict",
                "coef_x_specsim_low_broad",
                "p_x_specsim_low_broad",
                "nobs",
                "events",
            ]
        ]
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
