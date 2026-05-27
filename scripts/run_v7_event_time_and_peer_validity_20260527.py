#!/usr/bin/env python3
"""Event-time and product-market peer-validity checks for T05.

This script turns two existing robustness ideas into paper-ready artifacts:
1. a daily event-time plot for Specificity_z x AIActivePeer around focal GenAI
   disclosures; and
2. a product-market proximity gradient table/plot plus descriptive validation
   of true Top peers versus low-similarity/random placebo peers.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from run_v6_announcement_clean_checks_20260524 import base_clean_sample
from run_v6_final_review_checks_20260525 import ROOT
from run_v6_identification_strengthening_checks_20260524 import fit_absorbed


OUT_DIR = ROOT / "results" / "v7_event_time_peer_validity_20260527"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "60_v7_event_time_peer_validity_20260527.md"

TOP5_PATH = (
    ROOT
    / "results"
    / "v7_ai_supply_chain_disclosure_diagnostic_20260527"
    / "analysis_sample_top5_with_supply_chain_codes.csv.gz"
)
RETURNS_PATH = (
    ROOT
    / "results"
    / "v7_ai_supply_chain_stacked_did_20260527"
    / "needed_peer_daily_abret_mm.csv.gz"
)
TRUE_PANEL_PATH = (
    ROOT
    / "results"
    / "v6_external_ai_active_checks_20260524"
    / "true_panel_with_external_ai_active.csv.gz"
)
PLACEBO_PANEL_PATH = (
    ROOT
    / "results"
    / "v6_external_ai_active_checks_20260524"
    / "placebo_panel_with_external_ai_active.csv.gz"
)
PROXIMITY_RESULTS_PATH = ROOT / "results" / "v6_final_review_checks_20260525" / "proximity_gradient.csv"
LEAD_LAG_WINDOW_PATH = ROOT / "results" / "v6_final_review_checks_20260525" / "lead_lag.csv"

AI_DEFS = ["ext_any", "current_text_history"]
AI_LABELS = {"ext_any": "External AIActive", "current_text_history": "Text-history AIActive"}


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    digits = "".join(ch for ch in text if ch.isdigit())
    return digits.zfill(6) if digits else ""


def load_top5() -> pd.DataFrame:
    df = pd.read_csv(TOP5_PATH, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    df = df[df["peer_rank"].le(5)].copy()
    if "either_cleaning_ann" in df.columns:
        df = df[df["either_cleaning_ann"].eq(0)].copy()
    if "is_first_focal_event" in df.columns:
        df = df[df["is_first_focal_event"].eq(1)].copy()
    df["event_id"] = df["event_id"].astype(str)
    df["peer_code"] = df["peer_code"].map(code6)
    df["date_0"] = pd.to_datetime(df["date_0"], errors="coerce")
    for col in ["specificity_z", *AI_DEFS, "product_similarity"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["event_id", "peer_code", "date_0", "specificity_z"])


def load_returns() -> pd.DataFrame:
    ret = pd.read_csv(RETURNS_PATH, dtype={"peer_code": str})
    ret["peer_code"] = ret["peer_code"].map(code6)
    ret["date"] = pd.to_datetime(ret["date"], errors="coerce")
    ret["abret_mm"] = pd.to_numeric(ret["abret_mm"], errors="coerce")
    return ret.dropna(subset=["peer_code", "date", "abret_mm"]).sort_values(["peer_code", "date"])


def make_daily_panel(base: pd.DataFrame, returns: pd.DataFrame, tau_min: int = -10, tau_max: int = 10) -> pd.DataFrame:
    lookup: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for code, sub in returns.groupby("peer_code", sort=False):
        sub = sub.sort_values("date")
        lookup[code] = (
            sub["date"].to_numpy(dtype="datetime64[ns]"),
            sub["abret_mm"].to_numpy(dtype=float),
        )

    keep_cols = [
        "event_id",
        "focal_code",
        "focal_name",
        "peer_code",
        "peer_name",
        "peer_rank",
        "peer_industry_d",
        "product_similarity",
        "date_0",
        "specificity_z",
        *AI_DEFS,
    ]
    rows: list[dict[str, object]] = []
    for rec in base[keep_cols].itertuples(index=False):
        recd = rec._asdict()
        code = code6(recd["peer_code"])
        item = lookup.get(code)
        if item is None:
            continue
        dates, abrets = item
        date0 = np.datetime64(pd.Timestamp(recd["date_0"]).normalize())
        pos0 = int(np.searchsorted(dates, date0, side="left"))
        if pos0 >= len(dates) or dates[pos0] != date0:
            continue
        pair_id = f"{recd['event_id']}|{code}"
        for tau in range(tau_min, tau_max + 1):
            pos = pos0 + tau
            if pos < 0 or pos >= len(dates):
                continue
            val = abrets[pos]
            if not np.isfinite(val):
                continue
            row = {
                **recd,
                "peer_code": code,
                "pair_id": pair_id,
                "tau": tau,
                "tau_fe": str(tau),
                "date": pd.Timestamp(dates[pos]),
                "date_str": str(pd.Timestamp(dates[pos]).date()),
                "abret_mm": float(val),
            }
            for ai_def in AI_DEFS:
                row[f"ai_{ai_def}"] = float(recd[ai_def]) if pd.notna(recd[ai_def]) else 0.0
                row[f"spec_ai_{ai_def}"] = row[f"ai_{ai_def}"] * float(recd["specificity_z"])
            rows.append(row)
    return pd.DataFrame(rows)


def run_daily_event_time(daily: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    base_tau = -2
    for ai_def in AI_DEFS:
        d = daily.copy()
        xvars: list[str] = []
        focus_terms: list[str] = []
        for tau in range(-10, 11):
            if tau == base_tau:
                continue
            suffix = f"{tau:+d}".replace("+", "p").replace("-", "m")
            ai_col = f"ai_{ai_def}_tau_{suffix}"
            spec_col = f"spec_ai_{ai_def}_tau_{suffix}"
            d[ai_col] = d[f"ai_{ai_def}"] * d["tau"].eq(tau).astype(float)
            d[spec_col] = d[f"spec_ai_{ai_def}"] * d["tau"].eq(tau).astype(float)
            xvars.extend([ai_col, spec_col])
            focus_terms.append(spec_col)
        model_rows = fit_absorbed(
            d,
            "abret_mm",
            xvars,
            ["pair_id", "tau_fe"],
            model=f"daily_event_time_{ai_def}",
            term_focus=None,
        )
        for row in model_rows:
            if row["term"] not in focus_terms:
                continue
            tau_token = row["term"].split("_tau_")[-1]
            tau = int(tau_token.replace("p", "").replace("m", "-"))
            row.update({"ai_def": ai_def, "tau": tau, "base_tau": base_tau, "fe": "pair_id+tau_fe"})
            rows.append(row)
    out = pd.DataFrame(rows).sort_values(["ai_def", "tau"])
    if out.empty:
        return out
    out["ci_low"] = out["coef"] - 1.96 * out["se"]
    out["ci_high"] = out["coef"] + 1.96 * out["se"]
    return out


def load_clean_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    df["event_id"] = df["event_id"].astype(str)
    df["peer_code"] = df["peer_code"].map(code6)
    for col in ["product_similarity", "same_industry_d", *AI_DEFS, "peer_rank"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return base_clean_sample(df[df["either_cleaning_ann"].eq(0)].copy())


def peer_validity_summary() -> pd.DataFrame:
    true = load_clean_panel(TRUE_PANEL_PATH)
    placebo = load_clean_panel(PLACEBO_PANEL_PATH)
    groups = [
        ("true_top1_3", true[true["peer_rank"].between(1, 3)]),
        ("true_top4_5", true[true["peer_rank"].between(4, 5)]),
        ("true_top6_10", true[true["peer_rank"].between(6, 10)]),
        (
            "low_similarity_top5",
            placebo[placebo["peer_group"].eq("low_similarity_same_industry") & placebo["peer_rank"].between(1, 5)],
        ),
        (
            "random_same_industry_top5",
            placebo[placebo["peer_group"].eq("random_same_industry") & placebo["peer_rank"].between(1, 5)],
        ),
    ]
    rows = []
    for name, d in groups:
        rows.append(
            {
                "peer_group": name,
                "obs": int(len(d)),
                "events": int(d["event_id"].nunique()),
                "peer_firms": int(d["peer_code"].nunique()),
                "mean_similarity": float(d["product_similarity"].mean()),
                "median_similarity": float(d["product_similarity"].median()),
                "p25_similarity": float(d["product_similarity"].quantile(0.25)),
                "p75_similarity": float(d["product_similarity"].quantile(0.75)),
                "same_industry_rate": float(d["same_industry_d"].mean()),
                "ext_any_share": float(d["ext_any"].mean()),
                "text_history_share": float(d["current_text_history"].mean()),
            }
        )
    return pd.DataFrame(rows)


def prepare_proximity_results() -> pd.DataFrame:
    prox = pd.read_csv(PROXIMITY_RESULTS_PATH)
    prox["ci_low"] = prox["coef"] - 1.96 * prox["se"]
    prox["ci_high"] = prox["coef"] + 1.96 * prox["se"]
    prox["ai_label"] = prox["ai_def"].map(AI_LABELS)
    order = {
        "true_top1_3": 1,
        "true_top4_5": 2,
        "true_top6_10": 3,
        "low_similarity_top5": 4,
        "random_same_industry_top5": 5,
    }
    prox["plot_order"] = prox["peer_group"].map(order)
    return prox.sort_values(["ai_def", "plot_order"])


def prepare_window_lead_lag() -> pd.DataFrame:
    lead = pd.read_csv(LEAD_LAG_WINDOW_PATH)
    labels = {
        "peer_car_pre20_m11_mm": "[-20,-11]",
        "peer_car_pre10_m2_mm": "[-10,-2]",
        "peer_car_pre5_m2_mm": "[-5,-2]",
        "peer_car_0_p1_mm": "[0,+1]",
        "peer_car_post2_p5_mm": "[+2,+5]",
        "peer_car_post2_p10_mm": "[+2,+10]",
    }
    order = {
        "peer_car_pre20_m11_mm": 1,
        "peer_car_pre10_m2_mm": 2,
        "peer_car_pre5_m2_mm": 3,
        "peer_car_0_p1_mm": 4,
        "peer_car_post2_p5_mm": 5,
        "peer_car_post2_p10_mm": 6,
    }
    lead["window_label"] = lead["window"].map(labels)
    lead["plot_order"] = lead["window"].map(order)
    lead["ci_low"] = lead["coef"] - 1.96 * lead["se"]
    lead["ci_high"] = lead["coef"] + 1.96 * lead["se"]
    lead["ai_label"] = lead["ai_def"].map(AI_LABELS)
    return lead.sort_values(["ai_def", "plot_order"])


def plot_event_time(event_time: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    for ax, ai_def in zip(axes, AI_DEFS):
        d = event_time[event_time["ai_def"].eq(ai_def)].sort_values("tau")
        ax.axhline(0, color="#444444", linewidth=0.8)
        ax.axvline(-0.5, color="#999999", linestyle="--", linewidth=0.8)
        x = d["tau"].to_numpy(dtype=float)
        y = d["coef"].to_numpy(dtype=float)
        low = d["ci_low"].to_numpy(dtype=float)
        high = d["ci_high"].to_numpy(dtype=float)
        ax.plot(x, y, marker="o", color="#2B5C8A", linewidth=1.4)
        ax.fill_between(x, low, high, color="#2B5C8A", alpha=0.18)
        ax.set_title(AI_LABELS[ai_def])
        ax.set_xlabel("Trading day relative to focal disclosure")
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Coefficient on Specificity_z x AIActive")
    fig.suptitle("Daily Event-Time Coefficients for Peer Abnormal Returns", y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_proximity(prox: pd.DataFrame, path: Path) -> None:
    labels = {
        "true_top1_3": "Top1-3",
        "true_top4_5": "Top4-5",
        "true_top6_10": "Top6-10",
        "low_similarity_top5": "Low-sim",
        "random_same_industry_top5": "Random",
    }
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    for ax, ai_def in zip(axes, AI_DEFS):
        d = prox[prox["ai_def"].eq(ai_def)].sort_values("plot_order")
        x = np.arange(len(d))
        y = d["coef"].to_numpy(dtype=float)
        yerr = np.vstack([(y - d["ci_low"].to_numpy(dtype=float)), (d["ci_high"].to_numpy(dtype=float) - y)])
        ax.axhline(0, color="#444444", linewidth=0.8)
        ax.errorbar(x, y, yerr=yerr, marker="o", color="#7A3E3E", linewidth=1.4, capsize=3)
        ax.set_xticks(x)
        ax.set_xticklabels([labels[g] for g in d["peer_group"]], rotation=25, ha="right")
        ax.set_title(AI_LABELS[ai_def])
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Coefficient on Specificity_z x AIActive")
    fig.suptitle("Product-Market Proximity Gradient", y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_window_lead_lag(lead: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    for ax, ai_def in zip(axes, AI_DEFS):
        d = lead[lead["ai_def"].eq(ai_def)].sort_values("plot_order")
        x = np.arange(len(d))
        y = d["coef"].to_numpy(dtype=float)
        yerr = np.vstack([(y - d["ci_low"].to_numpy(dtype=float)), (d["ci_high"].to_numpy(dtype=float) - y)])
        colors = ["#7A3E3E" if w == "[0,+1]" else "#2B5C8A" for w in d["window_label"]]
        ax.axhline(0, color="#444444", linewidth=0.8)
        for xi, yi, lo, hi, color in zip(x, y, yerr[0], yerr[1], colors):
            ax.errorbar([xi], [yi], yerr=np.array([[lo], [hi]]), marker="o", color=color, capsize=3)
        ax.set_xticks(x)
        ax.set_xticklabels(d["window_label"], rotation=25, ha="right")
        ax.set_title(AI_LABELS[ai_def])
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Coefficient on Specificity_z x AIActive")
    fig.suptitle("Lead/Lag Window Coefficients for Peer CAR", y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def fmt_table(df: pd.DataFrame, cols: list[str] | None = None, digits: int = 4) -> str:
    if df.empty:
        return "_No rows._"
    out = df.copy()
    if cols is not None:
        out = out[cols]
    for col in out.select_dtypes(include=[np.number]).columns:
        out[col] = out[col].map(lambda x: round(float(x), digits) if pd.notna(x) else x)
    return out.to_markdown(index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Loading Top5 and daily returns...", flush=True)
    top5 = load_top5()
    returns = load_returns()
    daily = make_daily_panel(top5, returns)
    daily.to_csv(OUT_DIR / "daily_event_time_panel_top5.csv.gz", index=False, compression="gzip")

    print("Running daily event-time regressions...", flush=True)
    event_time = run_daily_event_time(daily)
    event_time.to_csv(OUT_DIR / "daily_event_time_coefficients.csv", index=False)

    print("Preparing peer-validity summaries...", flush=True)
    validity = peer_validity_summary()
    prox = prepare_proximity_results()
    lead_window = prepare_window_lead_lag()
    validity.to_csv(OUT_DIR / "product_market_peer_validity_summary.csv", index=False)
    prox.to_csv(OUT_DIR / "product_market_proximity_gradient_coefficients.csv", index=False)
    lead_window.to_csv(OUT_DIR / "window_lead_lag_coefficients.csv", index=False)

    event_plot = OUT_DIR / "event_time_spec_ai_daily.png"
    prox_plot = OUT_DIR / "proximity_gradient_coefficients.png"
    lead_window_plot = OUT_DIR / "window_lead_lag_coefficients.png"
    plot_event_time(event_time, event_plot)
    plot_proximity(prox, prox_plot)
    plot_window_lead_lag(lead_window, lead_window_plot)

    doc = f"""# V7 Event-Time and Product-Market Peer-Validity Checks

Date: 2026-05-27

## Purpose

This run packages tasks 4 and 5 into paper-ready artifacts:

1. daily event-time coefficients for `Specificity_z × AIActivePeer`;
2. product-market proximity gradient and peer-set validity diagnostics.

## Event-Time Check

Specification: daily market-model peer abnormal return on `Specificity_z × AIActivePeer × event-time day`, with event-peer pair FE and event-time FE. Tau = -2 is omitted. Standard errors are two-way clustered by focal event and peer firm.

Figure:

`results/v7_event_time_peer_validity_20260527/event_time_spec_ai_daily.png`

Window-level figure:

`results/v7_event_time_peer_validity_20260527/window_lead_lag_coefficients.png`

Key table:

{fmt_table(event_time[event_time["tau"].between(-5, 5)], ["ai_def", "tau", "coef", "se", "z", "p", "ci_low", "ci_high", "nobs", "events", "peer_firms"])}

Window-level lead/lag table:

{fmt_table(lead_window, ["ai_def", "window_label", "coef", "se", "z", "p", "nobs", "events", "peer_firms", "ci_low", "ci_high"])}

## Product-Market Peer-Set Validity

Descriptive validation of peer sets after first-event and announcement-cleaning filters.

{fmt_table(validity)}

## Proximity Gradient

Specification: current headline peer-CAR model with controls `PeerCAR[-10,-2] + PeerCAR[-20,-2]`, FE `event_id + peer_industry_week`, and two-way clustered standard errors.

Figure:

`results/v7_event_time_peer_validity_20260527/proximity_gradient_coefficients.png`

{fmt_table(prox, ["ai_def", "peer_group", "coef", "se", "z", "p", "nobs", "events", "peer_firms", "ci_low", "ci_high"])}

## Reading

- The daily event-time plot is mainly a transparency check. It should be shown as evidence on timing rather than as the headline estimator.
- Product-market validity is stronger: the coefficient is largest for Top1-3 peers, attenuates for Top6-10, and is null for low-similarity/random peers.
- The validity table shows that constructed Top peers have much higher product-text similarity than low-similarity and random peers, supporting the use of Top5 as the main peer set.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")

    print(f"Wrote {DOC_PATH}")
    print(f"Wrote outputs under {OUT_DIR}")


if __name__ == "__main__":
    main()
