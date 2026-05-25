#!/usr/bin/env python3
"""Rerun v6 main effects with external pre-event AIActivePeer definitions."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from run_v6_announcement_clean_checks_20260524 import (
    OUTCOMES,
    ROOT,
    base_clean_sample,
    fit_absorbed_model,
)


ANN_DIR = ROOT / "results" / "v6_announcement_clean_checks_20260524"
EXT_DIR = ROOT / "results" / "v6_external_ai_active_20260524"
OUT_DIR = ROOT / "results" / "v6_external_ai_active_checks_20260524"

TRUE_PANEL = ANN_DIR / "true_peer_market_model_car_panel_with_ann_flags.csv.gz"
PLACEBO_PANEL = ANN_DIR / "placebo_peer_market_model_car_panel_with_ann_flags.csv.gz"
FIRST_DATES = EXT_DIR / "external_ai_evidence_first_dates_by_firm.csv"
HIRING_DAY = EXT_DIR / "external_ai_hiring_firm_day_counts.csv.gz"

FLAG_SPECS = [
    ("current_text_history", "Current text-history AIActivePeer from the earlier event library"),
    ("prior_cac", "Prior CAC GenAI filing or registration"),
    ("prior_ai_patent_grant", "Prior broad-AI patent grant"),
    ("prior_broad_ai_hiring_365_ge1", "At least one broad-AI job posting in prior 365 days"),
    ("prior_broad_ai_hiring_365_ge3", "At least three broad-AI job postings in prior 365 days"),
    ("ext_no_hiring", "Prior CAC or broad-AI patent grant"),
    ("ext_any", "Prior CAC, broad-AI patent grant, or >=1 broad-AI hiring in prior 365 days"),
    ("ext_strict", "Prior CAC, broad-AI patent grant, or >=3 broad-AI hiring in prior 365 days"),
    ("ext_genai_strict", "Prior CAC, GenAI patent grant, or >=1 GenAI hiring in prior 365 days"),
    ("ext_plus_history", "ext_strict plus prior post-ChatGPT GenAI disclosure"),
]


def load_panels() -> tuple[pd.DataFrame, pd.DataFrame]:
    true = pd.read_csv(TRUE_PANEL, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    placebo = pd.read_csv(PLACEBO_PANEL, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    for df in [true, placebo]:
        for col in ["event_date", "date_0", "date_m1", "date_p1"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        df["peer_industry_d"] = df["peer_industry_d"].fillna("UNKNOWN").astype(str)
        df["event_week"] = df["date_0"].dt.strftime("%Y-%U")
        df["peer_industry_week"] = df["peer_industry_d"] + "|" + df["event_week"].fillna("")
    return true, placebo


def load_first_dates() -> pd.DataFrame:
    df = pd.read_csv(FIRST_DATES, dtype={"stock_code": str})
    date_cols = [c for c in df.columns if c.endswith("_date")]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df.set_index("stock_code")


def load_hiring_lookup() -> dict[str, dict[str, np.ndarray]]:
    df = pd.read_csv(HIRING_DAY, dtype={"stock_code": str}, parse_dates=["post_date"])
    out: dict[str, dict[str, np.ndarray]] = {}
    for code, sub in df.sort_values(["stock_code", "post_date"]).groupby("stock_code", sort=False):
        dates = sub["post_date"].to_numpy(dtype="datetime64[ns]")
        broad = sub["broad_ai_hiring_count"].fillna(0).to_numpy(dtype=float)
        genai = sub["genai_hiring_count"].fillna(0).to_numpy(dtype=float)
        out[code] = {
            "dates": dates,
            "broad_cum": np.cumsum(broad),
            "genai_cum": np.cumsum(genai),
        }
    return out


def count_between(rec: dict[str, np.ndarray] | None, start: np.datetime64, end: np.datetime64, key: str) -> float:
    if rec is None:
        return 0.0
    dates = rec["dates"]
    if len(dates) == 0:
        return 0.0
    cum = rec[key]
    right = np.searchsorted(dates, end, side="right")
    left = np.searchsorted(dates, start, side="left")
    if right <= left:
        return 0.0
    total_right = cum[right - 1]
    total_left = cum[left - 1] if left > 0 else 0.0
    return float(total_right - total_left)


def attach_external_flags(panel: pd.DataFrame, first_dates: pd.DataFrame, hiring: dict[str, dict[str, np.ndarray]]) -> pd.DataFrame:
    out = panel.copy()
    peer = out["peer_code"].astype(str).str.zfill(6)
    event_date = pd.to_datetime(out["event_date"], errors="coerce")
    cutoff = event_date - pd.Timedelta(days=5)

    date_map = {
        "prior_cac": "cac_first_date",
        "prior_ai_patent_grant": "ai_patent_grant_first_date",
        "prior_genai_patent_grant": "genai_patent_grant_first_date",
        "prior_history_genai_disclosure": "history_genai_disclosure_first_date",
    }
    joined = first_dates.reindex(peer.to_numpy())
    for flag, date_col in date_map.items():
        dates = pd.to_datetime(joined[date_col], errors="coerce").reset_index(drop=True)
        out[flag] = (dates.notna() & dates.le(cutoff.reset_index(drop=True))).astype(int).to_numpy()

    broad365: list[float] = []
    broad180: list[float] = []
    genai365: list[float] = []
    for code, cut in zip(peer, cutoff):
        if pd.isna(cut):
            broad365.append(0.0)
            broad180.append(0.0)
            genai365.append(0.0)
            continue
        end = np.datetime64(pd.Timestamp(cut).normalize())
        start365 = np.datetime64((pd.Timestamp(cut) - pd.Timedelta(days=365)).normalize())
        start180 = np.datetime64((pd.Timestamp(cut) - pd.Timedelta(days=180)).normalize())
        rec = hiring.get(code)
        broad365.append(count_between(rec, start365, end, "broad_cum"))
        broad180.append(count_between(rec, start180, end, "broad_cum"))
        genai365.append(count_between(rec, start365, end, "genai_cum"))

    out["prior_broad_ai_hiring_365_count"] = broad365
    out["prior_broad_ai_hiring_180_count"] = broad180
    out["prior_genai_hiring_365_count"] = genai365
    out["prior_broad_ai_hiring_365_ge1"] = (out["prior_broad_ai_hiring_365_count"] >= 1).astype(int)
    out["prior_broad_ai_hiring_365_ge3"] = (out["prior_broad_ai_hiring_365_count"] >= 3).astype(int)
    out["prior_genai_hiring_365_ge1"] = (out["prior_genai_hiring_365_count"] >= 1).astype(int)

    out["current_text_history"] = out["ai_active_peer_tminus5"].fillna(0).astype(int)
    out["ext_no_hiring"] = (out["prior_cac"].eq(1) | out["prior_ai_patent_grant"].eq(1)).astype(int)
    out["ext_any"] = (
        out["prior_cac"].eq(1)
        | out["prior_ai_patent_grant"].eq(1)
        | out["prior_broad_ai_hiring_365_ge1"].eq(1)
    ).astype(int)
    out["ext_strict"] = (
        out["prior_cac"].eq(1)
        | out["prior_ai_patent_grant"].eq(1)
        | out["prior_broad_ai_hiring_365_ge3"].eq(1)
    ).astype(int)
    out["ext_genai_strict"] = (
        out["prior_cac"].eq(1)
        | out["prior_genai_patent_grant"].eq(1)
        | out["prior_genai_hiring_365_ge1"].eq(1)
    ).astype(int)
    out["ext_plus_history"] = (out["ext_strict"].eq(1) | out["prior_history_genai_disclosure"].eq(1)).astype(int)

    for flag, _ in FLAG_SPECS:
        out[f"specz_x_{flag}"] = out["specificity_z"] * out[flag]
    return out


def run_models(panel: pd.DataFrame, peer_group: str, top_n: int) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    sample0 = base_clean_sample(panel)
    samples = [
        ("base_no_announcement_filter", sample0),
        ("drop_either_cleaning_ann", sample0[sample0["either_cleaning_ann"].eq(0)].copy()),
    ]
    fe_specs = [
        ("event_fe", ["event_id"]),
        ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
    ]
    summaries: list[dict[str, object]] = []
    regs: list[dict[str, object]] = []
    for sample_name, sample in samples:
        row = {
            "peer_group": peer_group,
            "top_n": top_n,
            "sample": sample_name,
            "obs": len(sample),
            "events": sample["event_id"].nunique(),
            "peer_firms": sample["peer_code"].nunique(),
        }
        for flag, _ in FLAG_SPECS:
            row[f"mean_{flag}"] = sample[flag].mean()
        summaries.append(row)
        for flag, desc in FLAG_SPECS:
            interaction = f"specz_x_{flag}"
            for fe_name, fe_cols in fe_specs:
                for outcome in OUTCOMES:
                    for reg in fit_absorbed_model(sample, outcome, [flag, interaction], fe_cols):
                        reg.update(
                            {
                                "peer_group": peer_group,
                                "top_n": top_n,
                                "sample": sample_name,
                                "fe_spec": fe_name,
                                "ai_active_def": flag,
                                "ai_active_def_desc": desc,
                                "interaction_term": interaction,
                                "model": "M1_specz_x_ai_active_external",
                            }
                        )
                        regs.append(reg)
    return summaries, regs


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    first_dates = load_first_dates()
    hiring = load_hiring_lookup()
    true, placebo = load_panels()
    true = attach_external_flags(true, first_dates, hiring)
    placebo = attach_external_flags(placebo, first_dates, hiring)

    true.to_csv(OUT_DIR / "true_panel_with_external_ai_active.csv.gz", index=False, compression="gzip")
    placebo.to_csv(OUT_DIR / "placebo_panel_with_external_ai_active.csv.gz", index=False, compression="gzip")

    groups = [
        ("true_top5", true[true["peer_rank"].le(5)].copy(), 5),
        ("true_top10", true[true["peer_rank"].le(10)].copy(), 10),
        (
            "low_similarity_same_industry",
            placebo[placebo["peer_group"].eq("low_similarity_same_industry")].copy(),
            10,
        ),
    ]
    all_summaries: list[dict[str, object]] = []
    all_regs: list[dict[str, object]] = []
    for peer_group, panel, top_n in groups:
        summaries, regs = run_models(panel, peer_group, top_n)
        all_summaries.extend(summaries)
        all_regs.extend(regs)

    summary = pd.DataFrame(all_summaries)
    regs = pd.DataFrame(all_regs)
    summary.to_csv(OUT_DIR / "v6_external_ai_active_sample_summary.csv", index=False)
    regs.to_csv(OUT_DIR / "v6_external_ai_active_regressions.csv", index=False)

    key = regs[
        regs["term"].eq(regs["interaction_term"])
        & regs["sample"].eq("drop_either_cleaning_ann")
        & regs["outcome"].eq("peer_car_0_p1_mm")
    ].copy()
    print(summary.to_string(index=False), flush=True)
    print(key.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
