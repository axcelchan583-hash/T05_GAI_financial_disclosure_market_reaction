#!/usr/bin/env python3
"""Mean peer abnormal-return event study for the CNINFO 1055 GenAI events."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from build_v23_cninfo_1055_peer_coverage_20260603 import OUT_DIR as COVERAGE_DIR


RUN_ID = "v23_cninfo_1055_peer_event_study_20260603"
ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "87_v23_cninfo_1055_peer_event_study_20260603.md"
PANEL_PATH = COVERAGE_DIR / "peer_link_panel.csv.gz"
STOCK_MODEL_PATH = (
    ROOT
    / "results"
    / "v6_supplement_market_model_placebo_20260524"
    / "stock_returns_with_market_model_params.csv"
)

OUTCOMES = [
    ("peer_ar_m1_mm", "AR[-1]"),
    ("peer_ar0_mm", "AR[0]"),
    ("peer_ar_p1_mm", "AR[+1]"),
    ("peer_car_0_p1_mm", "CAR[0,+1]"),
    ("peer_car_m1_p1_mm", "CAR[-1,+1]"),
]


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if "." in text:
        text = text.split(".", 1)[0]
    digits = "".join(ch for ch in text if ch.isdigit())
    return digits.zfill(6)[-6:] if digits else ""


def p_from_z(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2)) if math.isfinite(z) else math.nan


def load_stock_model() -> pd.DataFrame:
    ret = pd.read_csv(STOCK_MODEL_PATH, dtype={"peer_code": str})
    ret["peer_code"] = ret["peer_code"].map(code6)
    ret["date"] = pd.to_datetime(ret["date"], errors="coerce")
    for col in ["ret", "mkt_ret", "trdsta", "limit_status", "alpha_mm", "beta_mm", "est_obs"]:
        ret[col] = pd.to_numeric(ret[col], errors="coerce")
    ret["abret_mm"] = ret["ret"] - (ret["alpha_mm"] + ret["beta_mm"] * ret["mkt_ret"])
    return ret.dropna(subset=["peer_code", "date"]).sort_values(["peer_code", "date"])


def build_return_lookup(ret: pd.DataFrame) -> dict[str, dict[str, np.ndarray]]:
    lookup: dict[str, dict[str, np.ndarray]] = {}
    for code, sub in ret.groupby("peer_code", sort=False):
        sub = sub.sort_values("date")
        dates = sub["date"].to_numpy(dtype="datetime64[ns]")
        abret = sub["abret_mm"].to_numpy(dtype=float)
        valid = np.isfinite(abret)
        normal = sub["trdsta"].fillna(-999).astype(int).eq(1).to_numpy()
        no_limit = sub["limit_status"].fillna(0).astype(int).eq(0).to_numpy()
        ok = valid & normal & no_limit
        lookup[code] = {
            "dates": dates,
            "abret0": np.where(valid, abret, 0.0),
            "valid_cum": np.cumsum(valid.astype(int)),
            "ok_cum": np.cumsum(ok.astype(int)),
            "abret_cum": np.cumsum(np.where(valid, abret, 0.0)),
        }
    return lookup


def window_sum(
    lookup: dict[str, dict[str, np.ndarray]],
    code: str,
    date0: pd.Timestamp,
    start_offset: int,
    end_offset: int,
    min_valid: int,
) -> tuple[float, int, int]:
    rec = lookup.get(code6(code))
    if rec is None or pd.isna(date0):
        return math.nan, 0, 0
    dates = rec["dates"]
    d0 = np.datetime64(pd.Timestamp(date0).normalize())
    pos0 = int(np.searchsorted(dates, d0, side="left"))
    if pos0 >= len(dates) or dates[pos0] != d0:
        return math.nan, 0, 0
    left = pos0 + start_offset
    right = pos0 + end_offset
    if left < 0 or right >= len(dates) or right < left:
        return math.nan, 0, 0

    def span(cum: np.ndarray) -> float:
        return float(cum[right] - (cum[left - 1] if left > 0 else 0.0))

    valid_n = int(span(rec["valid_cum"]))
    ok_n = int(span(rec["ok_cum"]))
    if valid_n < min_valid:
        return math.nan, valid_n, ok_n
    return span(rec["abret_cum"]), valid_n, ok_n


def next_trading_day(date: pd.Timestamp, trading_dates: np.ndarray) -> pd.Timestamp | pd.NaT:
    if pd.isna(date):
        return pd.NaT
    target = np.datetime64(pd.Timestamp(date).normalize())
    pos = int(np.searchsorted(trading_dates, target, side="left"))
    if pos >= len(trading_dates):
        return pd.NaT
    return pd.Timestamp(trading_dates[pos])


def clustered_mean(df: pd.DataFrame, outcome: str) -> dict[str, object]:
    d = df.dropna(subset=[outcome, "event_key", "peer_code"]).copy()
    if d.empty:
        return {
            "estimate": math.nan,
            "se": math.nan,
            "z": math.nan,
            "p": math.nan,
            "nobs": 0,
            "events": 0,
            "focal_firms": 0,
            "peer_firms": 0,
            "median": math.nan,
            "positive_share": math.nan,
        }
    y = d[outcome].astype(float)
    estimate = float(y.mean())
    resid = y - estimate
    n = len(d)
    if d["event_key"].nunique() > 1 and d["peer_code"].nunique() > 1:
        event_term = resid.groupby(d["event_key"]).sum().pow(2).sum()
        peer_term = resid.groupby(d["peer_code"]).sum().pow(2).sum()
        pair_term = resid.groupby([d["event_key"], d["peer_code"]]).sum().pow(2).sum()
        var = float((event_term + peer_term - pair_term) / (n * n))
        se = math.sqrt(var) if var >= 0 else math.nan
    else:
        se = float(y.std(ddof=1) / math.sqrt(n)) if n > 1 else math.nan
    z = float(estimate / se) if se and se > 0 else math.nan
    return {
        "estimate": estimate,
        "se": se,
        "z": z,
        "p": p_from_z(z),
        "nobs": int(n),
        "events": int(d["event_key"].nunique()),
        "focal_firms": int(d["focal_code"].nunique()),
        "peer_firms": int(d["peer_code"].nunique()),
        "median": float(np.nanmedian(y.to_numpy())),
        "positive_share": float(np.mean(y.to_numpy() > 0)),
    }


def attach_event_trading_dates(panel: pd.DataFrame, stock_model: pd.DataFrame) -> pd.DataFrame:
    trading_dates = np.array(sorted(stock_model["date"].dropna().unique()), dtype="datetime64[ns]")
    out = panel.copy()
    out["event_date"] = pd.to_datetime(out["event_date"], errors="coerce")
    event_dates = out[["event_key", "event_date"]].drop_duplicates("event_key").copy()
    event_dates["date_0"] = event_dates["event_date"].map(lambda x: next_trading_day(x, trading_dates))
    out = out.merge(event_dates[["event_key", "date_0"]], on="event_key", how="left")
    return out


def build_return_measures(panel: pd.DataFrame, stock_model: pd.DataFrame) -> pd.DataFrame:
    lookup = build_return_lookup(stock_model)
    pairs = panel[["peer_code", "date_0"]].drop_duplicates().copy()
    rows: list[dict[str, object]] = []
    for code, date0 in zip(pairs["peer_code"], pairs["date_0"]):
        ar_m1, obs_m1, ok_m1 = window_sum(lookup, code, pd.Timestamp(date0), -1, -1, 1)
        ar0, obs_0, ok_0 = window_sum(lookup, code, pd.Timestamp(date0), 0, 0, 1)
        ar_p1, obs_p1, ok_p1 = window_sum(lookup, code, pd.Timestamp(date0), 1, 1, 1)
        car_0_p1, obs_0_p1, ok_0_p1 = window_sum(lookup, code, pd.Timestamp(date0), 0, 1, 2)
        car_m1_p1, obs_m1_p1, ok_m1_p1 = window_sum(lookup, code, pd.Timestamp(date0), -1, 1, 3)
        rows.append(
            {
                "peer_code": code,
                "date_0": date0,
                "peer_ar_m1_mm": ar_m1,
                "peer_ar0_mm": ar0,
                "peer_ar_p1_mm": ar_p1,
                "peer_car_0_p1_mm": car_0_p1,
                "peer_car_m1_p1_mm": car_m1_p1,
                "obs_peer_ar_m1_mm": obs_m1,
                "obs_peer_ar0_mm": obs_0,
                "obs_peer_ar_p1_mm": obs_p1,
                "obs_peer_car_0_p1_mm": obs_0_p1,
                "obs_peer_car_m1_p1_mm": obs_m1_p1,
                "ok_peer_ar_m1_mm": ok_m1,
                "ok_peer_ar0_mm": ok_0,
                "ok_peer_ar_p1_mm": ok_p1,
                "ok_peer_car_0_p1_mm": ok_0_p1,
                "ok_peer_car_m1_p1_mm": ok_m1_p1,
            }
        )
    returns = pd.DataFrame(rows)
    out = panel.merge(returns, on=["peer_code", "date_0"], how="left")
    out["complete_clean_m1_p1"] = out["ok_peer_car_m1_p1_mm"].ge(3).astype(int)
    return out


def sample_flow(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_cols = ["sample_name", "method_variant", "method", "method_top_n", "time_valid_prior_year"]
    for key, d in panel.groupby(group_cols, dropna=False):
        base = dict(zip(group_cols, key))
        rows.append(
            {
                **base,
                "linked_rows": int(len(d)),
                "linked_events": int(d["event_key"].nunique()),
                "linked_focal_firms": int(d["focal_code"].nunique()),
                "linked_peer_firms": int(d["peer_code"].nunique()),
                "rows_with_trading_date": int(d["date_0"].notna().sum()),
                "events_with_trading_date": int(d.loc[d["date_0"].notna(), "event_key"].nunique()),
                "complete_clean_rows": int(d["complete_clean_m1_p1"].eq(1).sum()),
                "complete_clean_events": int(d.loc[d["complete_clean_m1_p1"].eq(1), "event_key"].nunique()),
                "complete_clean_peer_firms": int(d.loc[d["complete_clean_m1_p1"].eq(1), "peer_code"].nunique()),
            }
        )
    return pd.DataFrame(rows).sort_values(["sample_name", "complete_clean_events"], ascending=[True, False])


def summarize(panel: pd.DataFrame, by_label: bool = False) -> pd.DataFrame:
    group_cols = ["sample_name", "method_variant", "method", "method_top_n", "time_valid_prior_year"]
    if by_label:
        group_cols.append("auto_pdf_label")
    rows = []
    clean = panel[panel["complete_clean_m1_p1"].eq(1)].copy()
    for key, d in clean.groupby(group_cols, dropna=False):
        base = dict(zip(group_cols, key))
        for outcome, label in OUTCOMES:
            rows.append({**base, "outcome": outcome, "outcome_label": label, **clustered_mean(d, outcome)})
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["sample_name", "outcome", "time_valid_prior_year", "p", "method_variant"])


def markdown_table(df: pd.DataFrame, cols: list[str], limit: int = 12) -> str:
    if df.empty:
        return "_No rows._"
    out = df[cols].head(limit).copy()
    for col in out.select_dtypes(include=[np.number]).columns:
        out[col] = out[col].map(lambda x: round(float(x), 6) if pd.notna(x) else x)
    rows = []
    rows.append("| " + " | ".join(cols) + " |")
    rows.append("|" + "|".join("---" for _ in cols) + "|")
    for _, row in out.iterrows():
        vals = []
        for col in cols:
            val = row[col]
            if pd.isna(val):
                vals.append("")
            else:
                vals.append(str(val))
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join(rows)


def write_report(summary: pd.DataFrame, flow: pd.DataFrame, stock_model: pd.DataFrame) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    stock_min = stock_model["date"].min()
    stock_max = stock_model["date"].max()

    def slice_rows(sample: str, outcome: str, time_valid: int) -> pd.DataFrame:
        return summary[
            summary["sample_name"].eq(sample)
            & summary["outcome"].eq(outcome)
            & summary["time_valid_prior_year"].eq(time_valid)
        ].sort_values(["p", "method_variant"])

    all_strict_car = slice_rows("all_1055", "peer_car_0_p1_mm", 1)
    all_static_car = slice_rows("all_1055", "peer_car_0_p1_mm", 0)
    likely_strict_car = slice_rows("likely_106", "peer_car_0_p1_mm", 1)
    all_strict_ar0 = slice_rows("all_1055", "peer_ar0_mm", 1)

    all_flow = flow[flow["sample_name"].eq("all_1055")].sort_values(
        ["time_valid_prior_year", "complete_clean_events"], ascending=[False, False]
    )

    lines = [
        "# v23 CNINFO 1055 peer event-study smoke test",
        "",
        "## Purpose",
        "",
        "This run attaches market-model abnormal returns to the CNINFO 1055 GenAI disclosure peer-link panel. "
        "It is an average peer AR/CAR smoke test, not the original T05 specificity-by-AIActive regression.",
        "",
        "## Design",
        "",
        f"- Peer-link input: `{PANEL_PATH.relative_to(ROOT)}`.",
        f"- Stock-return model cache: `results/v6_supplement_market_model_placebo_20260524/stock_returns_with_market_model_params.csv` ({stock_min.date()} to {stock_max.date()}).",
        "- Event date is moved forward to the next available trading date.",
        "- Analysis rows require complete clean peer trading for [-1,0,+1]: valid market-model abnormal returns, normal trading, and no limit-hit flag in the existing cache.",
        "- Standard errors are two-way clustered by event and peer firm.",
        "",
        "## Sample Flow, All 1055",
        "",
        markdown_table(
            all_flow,
            [
                "method_variant",
                "linked_events",
                "linked_peer_firms",
                "complete_clean_rows",
                "complete_clean_events",
                "complete_clean_peer_firms",
            ],
            12,
        ),
        "",
        "## Strict Prior-Year Networks: CAR[0,+1]",
        "",
        markdown_table(
            all_strict_car,
            ["method_variant", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"],
            12,
        ),
        "",
        "## Strict Prior-Year Networks: AR[0]",
        "",
        markdown_table(
            all_strict_ar0,
            ["method_variant", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"],
            12,
        ),
        "",
        "## Static/LLM Diagnostic Networks: CAR[0,+1]",
        "",
        markdown_table(
            all_static_car,
            ["method_variant", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"],
            12,
        ),
        "",
        "## Likely-Qian Subset: Strict Prior-Year CAR[0,+1]",
        "",
        markdown_table(
            likely_strict_car,
            ["method_variant", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"],
            12,
        ),
        "",
        "## Reading",
        "",
        "- This is useful for deciding whether the peer lane has enough observations after replacing the old event library with CNINFO full-text events.",
        "- The headline T05 question still needs event-level disclosure specificity coding; these mean CAR tables only answer whether peers move on average around the event.",
        "- Static LLM/semantic networks should be rebuilt as rolling/as-of peers before being used as a final causal design.",
        "",
        "## Output Files",
        "",
        f"- `{OUT_DIR.relative_to(ROOT)}/peer_event_study_summary.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/peer_event_study_summary_by_label.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/peer_event_study_sample_flow.csv`",
        f"- `{OUT_DIR.relative_to(ROOT)}/peer_event_study_panel_light.csv.gz`",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not PANEL_PATH.exists():
        raise FileNotFoundError(PANEL_PATH)
    panel = pd.read_csv(PANEL_PATH, dtype={"focal_code": str, "peer_code": str, "event_id": str}, low_memory=False)
    panel["method_top_n"] = pd.to_numeric(panel["method_top_n"], errors="coerce")
    panel["time_valid_prior_year"] = pd.to_numeric(panel["time_valid_prior_year"], errors="coerce").fillna(0).astype(int)
    panel["peer_rank"] = pd.to_numeric(panel["peer_rank"], errors="coerce")
    panel["event_date"] = pd.to_datetime(panel["event_date"], errors="coerce")
    print(f"Loaded peer-link panel: {len(panel):,} rows, {panel['event_key'].nunique():,} stacked events")

    stock_model = load_stock_model()
    print(
        f"Loaded stock model: {len(stock_model):,} rows, {stock_model['peer_code'].nunique():,} firms, "
        f"{stock_model['date'].min().date()} to {stock_model['date'].max().date()}"
    )
    panel = attach_event_trading_dates(panel, stock_model)
    print(f"Rows with event trading date: {panel['date_0'].notna().sum():,}")
    panel = build_return_measures(panel, stock_model)
    print(f"Complete clean [-1,+1] rows: {panel['complete_clean_m1_p1'].eq(1).sum():,}")

    flow = sample_flow(panel)
    summary = summarize(panel, by_label=False)
    summary_by_label = summarize(panel, by_label=True)

    light_cols = [
        "sample_name",
        "method_variant",
        "method",
        "method_top_n",
        "time_valid_prior_year",
        "event_id",
        "event_key",
        "focal_code",
        "sec_name",
        "event_date",
        "date_0",
        "auto_pdf_label",
        "peer_code",
        "peer_name",
        "peer_rank",
        "peer_similarity",
        "snapshot_report_year",
        "complete_clean_m1_p1",
        "peer_ar_m1_mm",
        "peer_ar0_mm",
        "peer_ar_p1_mm",
        "peer_car_0_p1_mm",
        "peer_car_m1_p1_mm",
    ]
    panel[light_cols].to_csv(OUT_DIR / "peer_event_study_panel_light.csv.gz", index=False)
    flow.to_csv(OUT_DIR / "peer_event_study_sample_flow.csv", index=False)
    summary.to_csv(OUT_DIR / "peer_event_study_summary.csv", index=False)
    summary_by_label.to_csv(OUT_DIR / "peer_event_study_summary_by_label.csv", index=False)
    write_report(summary, flow, stock_model)

    key = summary[
        summary["sample_name"].eq("all_1055")
        & summary["outcome"].eq("peer_car_0_p1_mm")
        & summary["time_valid_prior_year"].eq(1)
    ].sort_values(["p", "method_variant"])
    print(key[["method_variant", "estimate", "se", "p", "nobs", "events", "peer_firms"]].head(12).to_string(index=False))
    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
