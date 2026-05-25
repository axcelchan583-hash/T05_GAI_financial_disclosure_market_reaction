#!/usr/bin/env python3
"""Identification-strengthening checks for the v6 peer-CAR design.

The checks implemented here are deliberately diagnostic:
1. Formal DDD: true Top5 product peers versus placebo peers.
2. Pre-window placebo CARs.
3. Focal-firm CAR sign decomposition.
4. Investor-question-triggered subsample.
5. Non-GenAI investor-interaction pseudo-event placebo.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups

from build_csmar_genai_event_library_20260523 import (
    GENAI_PAT,
    IIP_ZIP,
    clean_text,
    csv_members,
    has_genai,
    is_a_share,
    read_csv_chunks,
    z6,
)
from run_v6_announcement_clean_checks_20260524 import (
    ROOT,
    absorb_fixed_effects,
    attach_announcement_flags,
    base_clean_sample,
    build_announcement_stock_day_flags,
)


OUT_DIR = ROOT / "results" / "v6_identification_strengthening_20260524"
TRUE_EXT_PANEL = (
    ROOT
    / "results"
    / "v6_external_ai_active_checks_20260524"
    / "true_panel_with_external_ai_active.csv.gz"
)
PLACEBO_EXT_PANEL = (
    ROOT
    / "results"
    / "v6_external_ai_active_checks_20260524"
    / "placebo_panel_with_external_ai_active.csv.gz"
)
STOCK_MODEL_PATH = (
    ROOT
    / "results"
    / "v6_supplement_market_model_placebo_20260524"
    / "stock_returns_with_market_model_params.csv"
)
FOCAL_EVENTS_PATH = (
    ROOT
    / "results"
    / "csmar_v5_1_response_smoke_20260523"
    / "csmar_conservative_focal_events_2023_2026.csv"
)
COMBINED_EVENTS_PATH = (
    ROOT
    / "results"
    / "csmar_genai_event_library_20260523"
    / "combined_firm_day_genai_events.csv"
)
IIP_ANSWER_EVENTS_PATH = (
    ROOT
    / "results"
    / "csmar_genai_event_library_20260523"
    / "iip_answer_level_genai_events.csv"
)

OUTCOME = "peer_car_0_p1_mm"
AI_DEFS = ["current_text_history", "ext_any", "ext_plus_history"]
MAIN_AI_DEF = "current_text_history"


def code6(value: object) -> str:
    return z6(value)


def load_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    for col in ["event_date", "date_m1", "date_0", "date_p1"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    df["focal_code"] = df["focal_code"].map(code6)
    df["peer_code"] = df["peer_code"].map(code6)
    if "peer_industry_week" not in df.columns:
        df["peer_industry_d"] = df["peer_industry_d"].fillna("UNKNOWN").astype(str)
        df["event_week"] = df["date_0"].dt.strftime("%Y-%U")
        df["peer_industry_week"] = df["peer_industry_d"] + "|" + df["event_week"].fillna("")
    return df


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


def fit_absorbed(
    data: pd.DataFrame,
    outcome: str,
    xvars: list[str],
    fe_cols: list[str],
    model: str,
    term_focus: str | None = None,
) -> list[dict[str, object]]:
    need = [outcome, *xvars, "event_id", "peer_code", *fe_cols]
    d = data.dropna(subset=need).copy()
    if d.empty:
        return []
    dm = absorb_fixed_effects(d, [outcome, *xvars], fe_cols)
    y = dm[outcome].to_numpy()
    x = dm[xvars].to_numpy()
    ols = sm.OLS(y, x).fit()
    cov_two, _, _ = cov_cluster_2groups(
        ols, pd.Categorical(dm["event_id"]).codes, pd.Categorical(dm["peer_code"]).codes
    )
    se = np.sqrt(np.diag(np.asarray(cov_two)))
    rows = []
    for idx, term in enumerate(xvars):
        if term_focus is not None and term != term_focus:
            continue
        z = ols.params[idx] / se[idx] if se[idx] > 0 else math.nan
        p = 2 * (1 - stats.norm.cdf(abs(z))) if math.isfinite(z) else math.nan
        rows.append(
            {
                "model": model,
                "outcome": outcome,
                "term": term,
                "coef": float(ols.params[idx]),
                "se": float(se[idx]),
                "z": float(z),
                "p": float(p),
                "nobs": int(ols.nobs),
                "events": int(d["event_id"].nunique()),
                "peer_firms": int(d["peer_code"].nunique()),
                "mean_y": float(d[outcome].mean()),
            }
        )
    return rows


def add_main_terms(df: pd.DataFrame, ai_def: str) -> pd.DataFrame:
    out = df.copy()
    out["ai"] = out[ai_def].fillna(0).astype(float)
    out["spec_ai"] = out["specificity_z"] * out["ai"]
    return out


def add_ddd_terms(df: pd.DataFrame, ai_def: str) -> pd.DataFrame:
    out = add_main_terms(df, ai_def)
    out["true_peer"] = out["true_peer"].astype(float)
    out["ai_true"] = out["ai"] * out["true_peer"]
    out["spec_true"] = out["specificity_z"] * out["true_peer"]
    out["spec_ai_true"] = out["specificity_z"] * out["ai"] * out["true_peer"]
    return out


def clean_first_sample(df: pd.DataFrame) -> pd.DataFrame:
    sample = base_clean_sample(df)
    return sample[sample["either_cleaning_ann"].eq(0)].copy()


def run_formal_ddd(true: pd.DataFrame, placebo: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    control_specs = [
        ("low_top5", placebo[placebo["peer_group"].eq("low_similarity_same_industry") & placebo["peer_rank"].le(5)].copy()),
        ("random_top5", placebo[placebo["peer_group"].eq("random_same_industry") & placebo["peer_rank"].le(5)].copy()),
    ]
    true5 = true[true["peer_rank"].le(5)].copy()
    true5["true_peer"] = 1
    for control_name, control in control_specs:
        control["true_peer"] = 0
        combined = pd.concat([true5, control], ignore_index=True, sort=False)
        combined = clean_first_sample(combined)
        for ai_def in AI_DEFS:
            d = add_ddd_terms(combined, ai_def)
            xvars = ["ai", "true_peer", "ai_true", "spec_ai", "spec_true", "spec_ai_true"]
            for fe_name, fe_cols in [
                ("event_fe", ["event_id"]),
                ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
                ("event_peer_firm_fe", ["event_id", "peer_code"]),
            ]:
                for row in fit_absorbed(
                    d,
                    OUTCOME,
                    xvars,
                    fe_cols,
                    model="formal_ddd_true_top5_vs_placebo",
                    term_focus="spec_ai_true",
                ):
                    row.update({"control_group": control_name, "ai_def": ai_def, "fe_spec": fe_name})
                    rows.append(row)
    return pd.DataFrame(rows)


def add_prewindow_outcomes(df: pd.DataFrame, lookup: dict[str, dict[str, np.ndarray]]) -> pd.DataFrame:
    out = df.copy()
    vals_10, obs_10, ok_10 = [], [], []
    vals_20, obs_20, ok_20 = [], [], []
    for code, date0 in zip(out["peer_code"], out["date_0"]):
        v10, n10, k10 = window_sum(lookup, code, date0, -10, -2, 7)
        v20, n20, k20 = window_sum(lookup, code, date0, -20, -2, 15)
        vals_10.append(v10)
        obs_10.append(n10)
        ok_10.append(k10)
        vals_20.append(v20)
        obs_20.append(n20)
        ok_20.append(k20)
    out["peer_car_pre10_m2_mm"] = vals_10
    out["obs_pre10_m2"] = obs_10
    out["ok_pre10_m2"] = ok_10
    out["peer_car_pre20_m2_mm"] = vals_20
    out["obs_pre20_m2"] = obs_20
    out["ok_pre20_m2"] = ok_20
    return out


def run_prewindow(true: pd.DataFrame, placebo: pd.DataFrame, lookup: dict[str, dict[str, np.ndarray]]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    groups = [
        ("true_top5", true[true["peer_rank"].le(5)].copy()),
        ("low_top5", placebo[placebo["peer_group"].eq("low_similarity_same_industry") & placebo["peer_rank"].le(5)].copy()),
    ]
    for group_name, panel in groups:
        panel = add_prewindow_outcomes(panel, lookup)
        sample = clean_first_sample(panel)
        for ai_def in [MAIN_AI_DEF, "ext_any"]:
            d = add_main_terms(sample, ai_def)
            for outcome in ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]:
                for fe_name, fe_cols in [
                    ("event_fe", ["event_id"]),
                    ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
                ]:
                    for row in fit_absorbed(
                        d, outcome, ["ai", "spec_ai"], fe_cols, model="prewindow_placebo", term_focus="spec_ai"
                    ):
                        row.update({"peer_group": group_name, "ai_def": ai_def, "fe_spec": fe_name})
                        rows.append(row)
    return pd.DataFrame(rows)


def add_focal_car(df: pd.DataFrame, lookup: dict[str, dict[str, np.ndarray]]) -> pd.DataFrame:
    event_base = df[["event_id", "focal_code", "date_0"]].drop_duplicates("event_id").copy()
    cars, obs, ok = [], [], []
    for code, date0 in zip(event_base["focal_code"], event_base["date_0"]):
        v, n, k = window_sum(lookup, code, date0, 0, 1, 2)
        cars.append(v)
        obs.append(n)
        ok.append(k)
    event_base["focal_car_0_p1_mm"] = cars
    event_base["obs_focal_car_0_p1"] = obs
    event_base["ok_focal_car_0_p1"] = ok
    event_base["focal_car_positive"] = (event_base["focal_car_0_p1_mm"] > 0).astype(int)
    return df.merge(event_base[["event_id", "focal_car_0_p1_mm", "focal_car_positive"]], on="event_id", how="left")


def run_focal_car_sign(true: pd.DataFrame, lookup: dict[str, dict[str, np.ndarray]]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    panel = add_focal_car(true[true["peer_rank"].le(5)].copy(), lookup)
    sample = clean_first_sample(panel)
    for sign_name, sub in [
        ("focal_car_positive", sample[sample["focal_car_positive"].eq(1)].copy()),
        ("focal_car_nonpositive", sample[sample["focal_car_positive"].eq(0)].copy()),
    ]:
        d = add_main_terms(sub, MAIN_AI_DEF)
        for fe_name, fe_cols in [
            ("event_fe", ["event_id"]),
            ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
        ]:
            for row in fit_absorbed(
                d, OUTCOME, ["ai", "spec_ai"], fe_cols, model="focal_car_sign_subsample", term_focus="spec_ai"
            ):
                row.update({"subsample": sign_name, "ai_def": MAIN_AI_DEF, "fe_spec": fe_name})
                rows.append(row)

    d = add_main_terms(sample, MAIN_AI_DEF)
    d["ai_pos"] = d["ai"] * d["focal_car_positive"]
    d["spec_ai_pos"] = d["spec_ai"] * d["focal_car_positive"]
    for fe_name, fe_cols in [
        ("event_fe", ["event_id"]),
        ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
    ]:
        for row in fit_absorbed(
            d,
            OUTCOME,
            ["ai", "spec_ai", "ai_pos", "spec_ai_pos"],
            fe_cols,
            model="focal_car_sign_interaction",
            term_focus="spec_ai_pos",
        ):
            row.update({"subsample": "all", "ai_def": MAIN_AI_DEF, "fe_spec": fe_name})
            rows.append(row)
    return pd.DataFrame(rows)


def event_trigger_flags() -> pd.DataFrame:
    focal_events = pd.read_csv(FOCAL_EVENTS_PATH, dtype={"event_id": str, "focal_code": str, "stock_code": str})
    focal_events["focal_code"] = focal_events["focal_code"].map(code6)
    focal_events["event_date"] = pd.to_datetime(focal_events["event_date"], errors="coerce")
    focal_events["question_terms"] = focal_events["question_terms"].fillna("").astype(str)
    focal_events["sources"] = focal_events["sources"].fillna("").astype(str)
    focal_events["passive_question_genai"] = focal_events["question_terms"].str.len().gt(0).astype(int)
    focal_events["has_iip_source"] = focal_events["sources"].str.contains("csmar_investor_interaction", regex=False).astype(int)

    iip = pd.read_csv(
        IIP_ANSWER_EVENTS_PATH,
        dtype={"source_id": str, "stock_code": str},
        usecols=["stock_code", "event_date", "question_date", "question_terms"],
    )
    iip["stock_code"] = iip["stock_code"].map(code6)
    iip["event_date"] = pd.to_datetime(iip["event_date"], errors="coerce")
    iip["event_day"] = iip["event_date"].dt.normalize()
    iip["question_date"] = pd.to_datetime(iip["question_date"], errors="coerce")
    iip["question_terms"] = iip["question_terms"].fillna("").astype(str)
    iip["delay_days"] = (iip["event_date"] - iip["question_date"]).dt.total_seconds() / 86400
    quick = (
        iip[iip["question_terms"].str.len().gt(0)]
        .groupby(["stock_code", "event_day"], as_index=False)["delay_days"]
        .min()
    )
    quick["iip_question_trigger_quick"] = quick["delay_days"].le(7).astype(int)
    out = focal_events.merge(
        quick.rename(columns={"stock_code": "focal_code", "event_day": "event_date_day"}),
        left_on=["focal_code", focal_events["event_date"].dt.normalize()],
        right_on=["focal_code", "event_date_day"],
        how="left",
    )
    out["iip_question_trigger_quick"] = out["iip_question_trigger_quick"].fillna(0).astype(int)
    return out[["event_id", "passive_question_genai", "has_iip_source", "iip_question_trigger_quick", "delay_days"]]


def run_passive_question(true: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    flags = event_trigger_flags()
    panel = true[true["peer_rank"].le(5)].merge(flags, on="event_id", how="left")
    sample = clean_first_sample(panel)
    subsets = [
        ("question_genai", sample[sample["passive_question_genai"].eq(1)].copy()),
        ("iip_quick_question_genai", sample[sample["iip_question_trigger_quick"].eq(1)].copy()),
        ("not_question_genai", sample[sample["passive_question_genai"].eq(0)].copy()),
    ]
    for subset_name, sub in subsets:
        if sub.empty:
            continue
        d = add_main_terms(sub, MAIN_AI_DEF)
        for fe_name, fe_cols in [
            ("event_fe", ["event_id"]),
            ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
        ]:
            for row in fit_absorbed(
                d, OUTCOME, ["ai", "spec_ai"], fe_cols, model="passive_question_subsample", term_focus="spec_ai"
            ):
                row.update({"subsample": subset_name, "ai_def": MAIN_AI_DEF, "fe_spec": fe_name})
                rows.append(row)
    return pd.DataFrame(rows)


def general_specificity(text: object) -> dict[str, float | int]:
    s = clean_text(text)
    compact = re.sub(r"\s+", "", s)
    token_count = max(1, len(re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9]+", compact)))
    patterns = {
        "dates": r"(?:20[2-9]\d年\d{0,2}月?\d{0,2}日?|20[2-9]\d[-/]\d{1,2}[-/]\d{1,2}|[一二三四1234]季度|Q[1-4])",
        "money": r"\d+(?:\.\d+)?(?:亿元|万元|元|万美元|美元|人民币)",
        "percent": r"\d+(?:\.\d+)?%",
        "numbers": r"\d+(?:\.\d+)?(?:个|项|款|台|套|人|家|年|月|日|亿|万)?",
        "quoted_names": r"[“《][^”》]{2,40}[”》]",
        "orgs": r"[\u4e00-\u9fa5A-Za-z0-9]{2,35}(?:公司|集团|大学|研究院|实验室|中心|平台|科技|智能|网络|银行)",
        "stage": r"(?:已上线|已发布|已备案|已通过|已落地|已部署|已接入|签署|合作|共建|推出|发布|升级|备案通过|内测|公测)",
    }
    counts = {k: len(re.findall(pat, compact, flags=re.I)) for k, pat in patterns.items()}
    specific_items = int(sum(counts.values()))
    return {
        "specific_items": specific_items,
        "text_tokens": int(token_count),
        "specificity": 100 * specific_items / token_count,
    }


def build_non_genai_pseudo_events(target_focals: set[str], true_first_dates: pd.Series) -> pd.DataFrame:
    cache = OUT_DIR / "non_genai_iip_pseudo_events_first_by_focal.csv"
    if cache.exists():
        out = pd.read_csv(cache, dtype={"focal_code": str})
        out["event_date"] = pd.to_datetime(out["event_date"], errors="coerce")
        return out

    rows: list[pd.DataFrame] = []
    for chunk in read_csv_chunks(IIP_ZIP, csv_members(IIP_ZIP), chunksize=150_000):
        chunk["Symbol"] = chunk["Symbol"].map(code6)
        chunk = chunk[chunk["Symbol"].isin(target_focals) & chunk["Symbol"].map(is_a_share)].copy()
        if chunk.empty:
            continue
        chunk["ReplyContent"] = chunk.get("ReplyContent", "").map(clean_text)
        chunk["QuestionContent"] = chunk.get("QuestionContent", "").map(clean_text)
        chunk["event_date"] = pd.to_datetime(chunk.get("ReplyDate", ""), errors="coerce")
        chunk = chunk[
            chunk["event_date"].ge(pd.Timestamp("2023-01-01"))
            & chunk["event_date"].le(pd.Timestamp("2026-05-22"))
            & chunk["ReplyContent"].str.len().ge(20)
        ].copy()
        if chunk.empty:
            continue
        chunk["answer_has_genai"] = chunk["ReplyContent"].map(has_genai)
        chunk["question_has_genai"] = chunk["QuestionContent"].map(lambda x: bool(GENAI_PAT.search(clean_text(x))))
        chunk = chunk[(~chunk["answer_has_genai"]) & (~chunk["question_has_genai"])].copy()
        if chunk.empty:
            continue
        rows.append(
            chunk[
                [
                    "Symbol",
                    "ShortName",
                    "event_date",
                    "QuestionDate",
                    "QuestionContent",
                    "ReplyContent",
                    "ProblemSource",
                ]
            ].copy()
        )

    if not rows:
        return pd.DataFrame()
    raw = pd.concat(rows, ignore_index=True)
    raw["focal_code"] = raw["Symbol"].map(code6)
    raw["event_day"] = raw["event_date"].dt.normalize()
    first_map = true_first_dates.to_dict()
    raw["first_genai_date"] = raw["focal_code"].map(first_map)
    raw = raw[
        raw["first_genai_date"].isna()
        | ((raw["event_day"] - raw["first_genai_date"]).abs() > pd.Timedelta(days=30))
    ].copy()
    raw = raw.sort_values(["focal_code", "event_day", "event_date"])
    raw = raw.drop_duplicates(["focal_code", "event_day"])
    raw["event_rank"] = raw.groupby("focal_code").cumcount() + 1
    raw = raw[raw["event_rank"].le(1)].copy()
    metrics = pd.DataFrame([general_specificity(v) for v in raw["ReplyContent"]], index=raw.index)
    raw = pd.concat([raw, metrics], axis=1)
    raw["event_id"] = [
        f"NONAI{i+1:05d}_{code}_{day:%Y%m%d}"
        for i, (code, day) in enumerate(zip(raw["focal_code"], raw["event_day"]))
    ]
    out = raw.rename(
        columns={
            "ShortName": "focal_name",
            "QuestionContent": "sample_question",
            "ReplyContent": "sample_answer",
        }
    )[
        [
            "event_id",
            "focal_code",
            "focal_name",
            "event_day",
            "specificity",
            "specific_items",
            "text_tokens",
            "sample_question",
            "sample_answer",
        ]
    ].rename(columns={"event_day": "event_date"})
    lo, hi = out["specificity"].quantile([0.01, 0.99])
    spec_w = out["specificity"].clip(lo, hi)
    out["specificity_z"] = (spec_w - spec_w.mean()) / spec_w.std()
    out.to_csv(cache, index=False, encoding="utf-8-sig")
    return out


def history_ai_active_lookup() -> dict[str, np.ndarray]:
    hist = pd.read_csv(COMBINED_EVENTS_PATH, dtype={"stock_code": str})
    hist["stock_code"] = hist["stock_code"].map(code6)
    hist["event_date"] = pd.to_datetime(hist["event_date_str"], errors="coerce")
    hist = hist[hist["event_date"].ge(pd.Timestamp("2022-11-30"))].copy()
    return {
        code: np.array(sorted(sub["event_date"].dropna().dt.normalize().unique()), dtype="datetime64[ns]")
        for code, sub in hist.groupby("stock_code", sort=False)
    }


def attach_history_ai_active(panel: pd.DataFrame, hist_lookup: dict[str, np.ndarray]) -> pd.DataFrame:
    flags = []
    for peer, event_date in zip(panel["peer_code"], panel["event_date"]):
        dates = hist_lookup.get(code6(peer))
        if dates is None or len(dates) == 0 or pd.isna(event_date):
            flags.append(0)
            continue
        cutoff = np.datetime64((pd.Timestamp(event_date) - pd.Timedelta(days=5)).normalize())
        flags.append(int(np.searchsorted(dates, cutoff, side="right") > 0))
    out = panel.copy()
    out["current_text_history"] = flags
    return out


def add_event_trading_dates(events: pd.DataFrame, market_dates: np.ndarray) -> pd.DataFrame:
    event_dates = pd.to_datetime(events["event_date"], errors="coerce").dt.normalize().to_numpy(dtype="datetime64[ns]")
    pos0 = np.searchsorted(market_dates, event_dates, side="left")
    valid = pos0 < len(market_dates)
    out = events.loc[valid].copy()
    pos0 = pos0[valid]
    for offset, col in [(-1, "date_m1"), (0, "date_0"), (1, "date_p1")]:
        pos = pos0 + offset
        vals = np.full(len(out), np.datetime64("NaT"), dtype="datetime64[ns]")
        ok = (pos >= 0) & (pos < len(market_dates))
        vals[ok] = market_dates[pos[ok]]
        out[col] = pd.to_datetime(vals)
    out["event_week"] = out["date_0"].dt.strftime("%Y-%U")
    return out


def attach_main_window(panel: pd.DataFrame, lookup: dict[str, dict[str, np.ndarray]]) -> pd.DataFrame:
    vals, obs, ok = [], [], []
    vals_m1p1, obs_m1p1, ok_m1p1 = [], [], []
    for code, date0 in zip(panel["peer_code"], panel["date_0"]):
        v, n, k = window_sum(lookup, code, date0, 0, 1, 2)
        v3, n3, k3 = window_sum(lookup, code, date0, -1, 1, 3)
        vals.append(v)
        obs.append(n)
        ok.append(k)
        vals_m1p1.append(v3)
        obs_m1p1.append(n3)
        ok_m1p1.append(k3)
    out = panel.copy()
    out["peer_car_0_p1_mm"] = vals
    out["peer_car_m1_p1_mm"] = vals_m1p1
    out["obs_peer_car_m1_p1_mm"] = obs_m1p1
    out["normal_trading_m1_p1"] = (np.array(ok_m1p1) >= 3).astype(int)
    out["no_limit_m1_p1"] = (np.array(ok_m1p1) >= 3).astype(int)
    out["alpha_mm"] = 1.0
    out["beta_mm"] = 1.0
    return out


def run_non_genai_placebo(
    true: pd.DataFrame,
    placebo: pd.DataFrame,
    stock_model: pd.DataFrame,
    lookup: dict[str, dict[str, np.ndarray]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    true_first_dates = (
        true[true["is_first_focal_event"].eq(1)]
        .drop_duplicates("focal_code")
        .set_index("focal_code")["event_date"]
    )
    pseudo = build_non_genai_pseudo_events(set(true_first_dates.index), true_first_dates)
    if pseudo.empty:
        return pd.DataFrame(), pd.DataFrame()

    true_peers = (
        true[["focal_code", "focal_name", "focal_industry_d", "peer_rank", "peer_code", "peer_name", "peer_industry_d", "product_similarity", "same_industry_d"]]
        .drop_duplicates(["focal_code", "peer_code"])
    )
    true_peers = true_peers[true_peers["peer_rank"].le(5)].copy()
    true_peers["true_peer"] = 1
    low_peers = (
        placebo[placebo["peer_group"].eq("low_similarity_same_industry")]
        [["focal_code", "focal_name", "focal_industry_d", "peer_rank", "peer_code", "peer_name", "peer_industry_d", "product_similarity", "same_industry_d"]]
        .drop_duplicates(["focal_code", "peer_code"])
    )
    low_peers = low_peers[low_peers["peer_rank"].le(5)].copy()
    low_peers["true_peer"] = 0
    peers = pd.concat([true_peers, low_peers], ignore_index=True, sort=False)
    panel = pseudo.merge(peers, on="focal_code", how="inner", suffixes=("", "_peer"))
    market_dates = np.array(sorted(stock_model["date"].dropna().unique()), dtype="datetime64[ns]")
    panel = add_event_trading_dates(panel, market_dates)
    panel["peer_industry_d"] = panel["peer_industry_d"].fillna("UNKNOWN").astype(str)
    panel["peer_industry_week"] = panel["peer_industry_d"] + "|" + panel["event_week"].fillna("")
    panel = attach_history_ai_active(panel, history_ai_active_lookup())
    panel = attach_main_window(panel, lookup)
    panel["is_first_focal_event"] = 1
    flags = build_announcement_stock_day_flags()
    panel = attach_announcement_flags(panel, flags)
    panel.to_csv(OUT_DIR / "non_genai_placebo_panel.csv.gz", index=False, compression="gzip")

    sample = clean_first_sample(panel)
    d = add_ddd_terms(sample, MAIN_AI_DEF)
    rows = []
    for fe_name, fe_cols in [
        ("event_fe", ["event_id"]),
        ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
    ]:
        for row in fit_absorbed(
            d,
            OUTCOME,
            ["ai", "true_peer", "ai_true", "spec_ai", "spec_true", "spec_ai_true"],
            fe_cols,
            model="non_genai_iip_pseudo_event_ddd",
            term_focus="spec_ai_true",
        ):
            row.update({"ai_def": MAIN_AI_DEF, "fe_spec": fe_name})
            rows.append(row)
    return pd.DataFrame(rows), pseudo


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    true = load_panel(TRUE_EXT_PANEL)
    placebo = load_panel(PLACEBO_EXT_PANEL)
    stock_model = load_stock_model()
    lookup = build_return_lookup(stock_model)

    print("Running formal DDD...", flush=True)
    ddd = run_formal_ddd(true, placebo)
    ddd.to_csv(OUT_DIR / "formal_ddd_results.csv", index=False)

    print("Running pre-window placebo...", flush=True)
    pre = run_prewindow(true, placebo, lookup)
    pre.to_csv(OUT_DIR / "prewindow_placebo_results.csv", index=False)

    print("Running focal-CAR sign decomposition...", flush=True)
    focal_sign = run_focal_car_sign(true, lookup)
    focal_sign.to_csv(OUT_DIR / "focal_car_sign_results.csv", index=False)

    print("Running passive-question subsample...", flush=True)
    passive = run_passive_question(true)
    passive.to_csv(OUT_DIR / "passive_question_results.csv", index=False)

    print("Running non-GenAI pseudo-event placebo...", flush=True)
    non_genai, pseudo = run_non_genai_placebo(true, placebo, stock_model, lookup)
    non_genai.to_csv(OUT_DIR / "non_genai_placebo_results.csv", index=False)
    if not pseudo.empty:
        pseudo.to_csv(OUT_DIR / "non_genai_pseudo_events.csv", index=False, encoding="utf-8-sig")

    summary = []
    for name, df in [
        ("formal_ddd", ddd),
        ("prewindow", pre),
        ("focal_car_sign", focal_sign),
        ("passive_question", passive),
        ("non_genai_placebo", non_genai),
    ]:
        summary.append({"check": name, "rows": len(df), "min_p": df["p"].min() if "p" in df and len(df) else np.nan})
    pd.DataFrame(summary).to_csv(OUT_DIR / "identification_strengthening_summary.csv", index=False)

    print("\n=== formal DDD ===", flush=True)
    print(ddd.to_string(index=False), flush=True)
    print("\n=== pre-window ===", flush=True)
    print(pre.to_string(index=False), flush=True)
    print("\n=== focal CAR sign ===", flush=True)
    print(focal_sign.to_string(index=False), flush=True)
    print("\n=== passive question ===", flush=True)
    print(passive.to_string(index=False), flush=True)
    print("\n=== non-GenAI placebo ===", flush=True)
    print(non_genai.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
