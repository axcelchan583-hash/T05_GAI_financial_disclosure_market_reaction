#!/usr/bin/env python3
"""Run the peer-CAR main effect with annual-report product-market peers.

This script is a smoke-test bridge from the v12 annual-report peer network to
the v6 market-reaction pipeline. It keeps the event-level X, trading calendar,
market-model CAR construction, announcement-cleaning rules, external AIActive
definitions, and absorbed-FE regression machinery aligned with the existing
v6/v8 analyses, while swapping only the product-market peer network.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

from run_v6_announcement_clean_checks_20260524 import (
    ROOT,
    attach_announcement_flags,
    build_announcement_stock_day_flags,
)
from run_v6_external_ai_active_checks_20260524 import (
    attach_external_flags,
    load_first_dates,
    load_hiring_lookup,
)
from run_v6_identification_strengthening_checks_20260524 import (
    build_return_lookup,
    fit_absorbed,
    load_stock_model,
    window_sum,
)


PEER_DIR = ROOT / "results" / "v12_annual_report_product_peers_20260530"
OUT_DIR = ROOT / "results" / "v12_annual_report_peer_main_effect_20260530"
EVENT_INFO_PATH = (
    ROOT
    / "results"
    / "v6_external_ai_active_checks_20260524"
    / "true_panel_with_external_ai_active.csv.gz"
)

PEER_FILES = {
    "annual_same_industry_d": PEER_DIR / "annual_report_peer_event_same_industry_d_top10.csv",
    "annual_global": PEER_DIR / "annual_report_peer_event_global_top10.csv",
    "annual_global_ai_stripped": PEER_DIR
    / "annual_report_peer_event_global_ai_stripped_top10.csv",
}

OUTCOME = "peer_car_0_p1_mm"
PREWINDOW_CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
AI_DEFS = ["ext_any", "current_text_history", "ext_no_hiring", "ext_plus_history"]


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = re.sub(r"\.0$", "", str(value).strip())
    digits = re.sub(r"\D", "", text)
    return digits.zfill(6) if digits else ""


def load_event_info() -> pd.DataFrame:
    """Load frozen event-level trading dates and event X from the v6 panel."""
    cols = [
        "event_id",
        "focal_code",
        "event_date",
        "specificity",
        "specificity_z",
        "is_first_focal_event",
        "date_m1",
        "date_0",
        "date_p1",
    ]
    event = pd.read_csv(
        EVENT_INFO_PATH,
        usecols=lambda c: c in cols,
        dtype={"event_id": str, "focal_code": str},
    )
    event = event.drop_duplicates("event_id").copy()
    for col in ["event_date", "date_m1", "date_0", "date_p1"]:
        event[col] = pd.to_datetime(event[col], errors="coerce")
    event["focal_code"] = event["focal_code"].map(code6)
    return event


def add_return_columns(panel: pd.DataFrame, stock_model: pd.DataFrame) -> pd.DataFrame:
    """Attach event-window returns and market-model abnormal returns."""
    out = panel.copy()
    stock = stock_model.copy()
    stock["peer_code"] = stock["peer_code"].map(code6)
    stock["date"] = pd.to_datetime(stock["date"], errors="coerce")

    keep = ["peer_code", "date", "ret", "mkt_ret", "trdsta", "limit_status"]
    for suffix, date_col in [("m1", "date_m1"), ("0", "date_0"), ("p1", "date_p1")]:
        tmp = stock[keep].rename(
            columns={
                "date": date_col,
                "ret": f"ret_{suffix}",
                "mkt_ret": f"mkt_ret_{suffix}",
                "trdsta": f"trdsta_{suffix}",
                "limit_status": f"limit_status_{suffix}",
            }
        )
        out = out.merge(tmp, on=["peer_code", date_col], how="left")

    params = stock[["peer_code", "date", "alpha_mm", "beta_mm", "est_obs"]].rename(
        columns={"date": "date_0"}
    )
    out = out.merge(params, on=["peer_code", "date_0"], how="left")
    for suffix in ["m1", "0", "p1"]:
        out[f"abret_{suffix}_mm"] = out[f"ret_{suffix}"] - (
            out["alpha_mm"] + out["beta_mm"] * out[f"mkt_ret_{suffix}"]
        )
    out["peer_ar0_mm"] = out["abret_0_mm"]
    out["peer_car_0_p1_mm"] = out[["abret_0_mm", "abret_p1_mm"]].sum(axis=1, min_count=2)
    out["peer_car_m1_p1_mm"] = out[["abret_m1_mm", "abret_0_mm", "abret_p1_mm"]].sum(
        axis=1, min_count=3
    )
    out["obs_peer_car_m1_p1_mm"] = out[
        ["abret_m1_mm", "abret_0_mm", "abret_p1_mm"]
    ].notna().sum(axis=1)
    out["normal_trading_m1_p1"] = (
        out[["trdsta_m1", "trdsta_0", "trdsta_p1"]].fillna(-999).astype(int).eq(1).all(axis=1)
    ).astype(int)
    out["no_limit_m1_p1"] = (
        out[["limit_status_m1", "limit_status_0", "limit_status_p1"]]
        .fillna(999)
        .astype(int)
        .eq(0)
        .all(axis=1)
    ).astype(int)
    return out


def add_prewindow_controls(panel: pd.DataFrame, lookup: dict[str, dict[str, np.ndarray]]) -> pd.DataFrame:
    out = panel.copy()
    pre10: list[float] = []
    pre20: list[float] = []
    pre10_obs: list[int] = []
    pre20_obs: list[int] = []
    for code, date0 in zip(out["peer_code"], out["date_0"]):
        val10, obs10, _ = window_sum(lookup, code, date0, -10, -2, 7)
        val20, obs20, _ = window_sum(lookup, code, date0, -20, -2, 12)
        pre10.append(val10)
        pre20.append(val20)
        pre10_obs.append(obs10)
        pre20_obs.append(obs20)
    out["peer_car_pre10_m2_mm"] = pre10
    out["peer_car_pre20_m2_mm"] = pre20
    out["obs_peer_car_pre10_m2_mm"] = pre10_obs
    out["obs_peer_car_pre20_m2_mm"] = pre20_obs
    return out


def add_text_history_seed(panel: pd.DataFrame, first_dates: pd.DataFrame) -> pd.DataFrame:
    """Create ai_active_peer_tminus5 so v6 attach_external_flags can be reused."""
    out = panel.copy()
    peer = out["peer_code"].astype(str).str.zfill(6)
    event_date = pd.to_datetime(out["event_date"], errors="coerce")
    cutoff = event_date - pd.Timedelta(days=5)
    joined = first_dates.reindex(peer.to_numpy())
    history_date = pd.to_datetime(
        joined["history_genai_disclosure_first_date"], errors="coerce"
    ).reset_index(drop=True)
    out["ai_active_peer_tminus5"] = (
        history_date.notna() & history_date.le(cutoff.reset_index(drop=True))
    ).astype(int).to_numpy()
    return out


def build_panel(peer_name: str, peer_path: Path, stock_model: pd.DataFrame) -> pd.DataFrame:
    print(f"Loading annual-report peer panel: {peer_name}", flush=True)
    keep_cols = [
        "event_id",
        "focal_code",
        "event_date",
        "specificity",
        "focal_name",
        "focal_industry_d",
        "peer_rank",
        "peer_code",
        "peer_name",
        "peer_industry_d",
        "product_similarity",
        "same_industry_d",
    ]
    panel = pd.read_csv(peer_path, usecols=lambda c: c in keep_cols, dtype={"event_id": str})
    panel["focal_code"] = panel["focal_code"].map(code6)
    panel["peer_code"] = panel["peer_code"].map(code6)
    panel["event_date"] = pd.to_datetime(panel["event_date"], errors="coerce")
    panel["peer_rank"] = pd.to_numeric(panel["peer_rank"], errors="coerce")

    event_info = load_event_info()
    event_cols = [
        "event_id",
        "date_m1",
        "date_0",
        "date_p1",
        "specificity_z",
        "is_first_focal_event",
    ]
    panel = panel.merge(event_info[event_cols], on="event_id", how="left")
    panel["peer_source"] = peer_name
    panel["event_week"] = panel["date_0"].dt.strftime("%Y-%U")
    panel["peer_industry_d"] = panel["peer_industry_d"].fillna("UNKNOWN").astype(str)
    panel["peer_industry_week"] = panel["peer_industry_d"] + "|" + panel["event_week"].fillna("")

    panel = add_return_columns(panel, stock_model)
    return panel


def base_sample(panel: pd.DataFrame, top_n: int) -> pd.DataFrame:
    sample = panel[
        panel["peer_rank"].le(top_n)
        & panel["is_first_focal_event"].eq(1)
        & panel["obs_peer_car_m1_p1_mm"].eq(3)
        & panel["normal_trading_m1_p1"].eq(1)
        & panel["no_limit_m1_p1"].eq(1)
        & panel["alpha_mm"].notna()
        & panel["beta_mm"].notna()
        & panel["either_cleaning_ann"].eq(0)
    ].copy()
    return sample


def add_ai_terms(df: pd.DataFrame, ai_def: str) -> pd.DataFrame:
    out = df.copy()
    out["ai"] = out[ai_def].fillna(0).astype(float)
    out["spec_ai"] = out["specificity_z"].astype(float) * out["ai"]
    return out


def run_regressions(panel: pd.DataFrame, peer_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    specs = [
        ("event_fe", ["event_id"]),
        ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
    ]
    for top_n in [5, 10]:
        sample = base_sample(panel, top_n)
        summary = {
            "peer_source": peer_name,
            "top_n": top_n,
            "obs": len(sample),
            "events": sample["event_id"].nunique(),
            "peer_firms": sample["peer_code"].nunique(),
            "mean_peer_car_0_p1_mm": sample[OUTCOME].mean(),
        }
        for ai_def in AI_DEFS:
            summary[f"mean_{ai_def}"] = sample[ai_def].mean()
        summary_rows.append(summary)
        sample.to_csv(
            OUT_DIR / f"analysis_sample_{peer_name}_top{top_n}.csv.gz",
            index=False,
            compression="gzip",
        )
        for ai_def in AI_DEFS:
            d = add_ai_terms(sample, ai_def)
            for fe_name, fe_cols in specs:
                xvars = ["ai", "spec_ai", *PREWINDOW_CONTROLS]
                for reg in fit_absorbed(
                    d,
                    OUTCOME,
                    xvars,
                    fe_cols,
                    model=f"{peer_name}_top{top_n}_{ai_def}_{fe_name}_prewindow",
                    term_focus="spec_ai",
                ):
                    reg.update(
                        {
                            "peer_source": peer_name,
                            "top_n": top_n,
                            "ai_active_def": ai_def,
                            "fe_spec": fe_name,
                            "sample": "first_focal_event_drop_either_cleaning_ann_with_prewindow",
                            "controls": "+".join(PREWINDOW_CONTROLS),
                        }
                    )
                    rows.append(reg)
    return pd.DataFrame(summary_rows), pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading stock-return model cache...", flush=True)
    stock_model = load_stock_model()
    ret_lookup = build_return_lookup(stock_model)
    first_dates = load_first_dates()
    hiring = load_hiring_lookup()
    ann_flags = build_announcement_stock_day_flags(refresh=False)

    all_summaries: list[pd.DataFrame] = []
    all_regs: list[pd.DataFrame] = []
    for peer_name, peer_path in PEER_FILES.items():
        panel = build_panel(peer_name, peer_path, stock_model)
        print(f"Attaching announcement flags: {peer_name}", flush=True)
        panel = attach_announcement_flags(panel, ann_flags)
        print(f"Attaching external AIActive flags: {peer_name}", flush=True)
        panel = add_text_history_seed(panel, first_dates)
        panel = attach_external_flags(panel, first_dates, hiring)
        print(f"Adding pre-window CAR controls: {peer_name}", flush=True)
        panel = add_prewindow_controls(panel, ret_lookup)
        panel.to_csv(OUT_DIR / f"full_panel_{peer_name}.csv.gz", index=False, compression="gzip")
        summary, regs = run_regressions(panel, peer_name)
        all_summaries.append(summary)
        all_regs.append(regs)

    summary_out = pd.concat(all_summaries, ignore_index=True)
    regs_out = pd.concat(all_regs, ignore_index=True)
    summary_out.to_csv(OUT_DIR / "annual_report_peer_main_effect_sample_summary.csv", index=False)
    regs_out.to_csv(OUT_DIR / "annual_report_peer_main_effect_regressions.csv", index=False)

    key = regs_out[
        regs_out["ai_active_def"].isin(["ext_any", "current_text_history"])
        & regs_out["top_n"].eq(5)
        & regs_out["fe_spec"].eq("event_fe_peer_industry_week_fe")
    ].copy()
    print("\nSample summary:", flush=True)
    print(summary_out.to_string(index=False), flush=True)
    print("\nKey Top5 strong-FE coefficients:", flush=True)
    print(
        key[
            [
                "peer_source",
                "ai_active_def",
                "coef",
                "se",
                "z",
                "p",
                "nobs",
                "events",
                "peer_firms",
            ]
        ].to_string(index=False),
        flush=True,
    )


if __name__ == "__main__":
    main()
