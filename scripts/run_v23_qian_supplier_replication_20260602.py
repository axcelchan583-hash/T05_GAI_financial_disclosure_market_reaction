#!/usr/bin/env python3
"""Qian-style supplier stock-reaction replication audit for China A shares.

This is a narrow audit: customer GenAI event -> upstream listed supplier AR.
It uses existing local T05 panels and market-model return estimates.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "v23_qian_supplier_replication_20260602"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "86_v23_qian_supplier_replication_20260602.md"

EVENT_META_PATH = (
    ROOT
    / "results"
    / "v7_ai_supply_chain_disclosure_diagnostic_20260527"
    / "all_focal_events_supply_chain_codes.csv"
)
FIRST_CHAIN_PATH = (
    ROOT
    / "results"
    / "v21_supplier_specificity_smoke_20260601"
    / "chain_event_panel_before_car.csv"
)
ALL_CHAIN_PATH = (
    ROOT
    / "results"
    / "v21_supplier_specificity_smoke_20260601"
    / "chain_event_panel_all_events_with_car.csv.gz"
)
FORMAL_CHAIN_PATH = (
    ROOT
    / "results"
    / "v3_supplier_spillover_sample_diagnostic"
    / "formal_union_supplier_event_panel_before_car.csv"
)
RETURNS_PATH = (
    ROOT
    / "results"
    / "v6_supplement_market_model_placebo_20260524"
    / "stock_returns_with_market_model_params.csv"
)

STRICT_GENAI_RE = re.compile(
    r"(?:AIGC|ChatGPT|DeepSeek|AI大模型|大模型|生成式AI|生成式人工智能|生成式人工智慧|"
    r"generative\s*AI|GenAI|GPT|LLM|large\s+language\s+model|语言模型)",
    re.IGNORECASE,
)


@dataclass
class FlowStage:
    sample: str
    stage: str
    rows: int
    events: int
    affected_firms: int
    upstream_rows: int
    downstream_rows: int


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    digits = "".join(ch for ch in text if ch.isdigit())
    return digits.zfill(6) if digits else ""


def strict_genai_text(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    text = df[[c for c in cols if c in df.columns]].fillna("").astype(str).agg(" ".join, axis=1)
    return text.str.contains(STRICT_GENAI_RE)


def add_flow(rows: list[FlowStage], sample: str, stage: str, df: pd.DataFrame) -> None:
    relation = df["relation"] if "relation" in df.columns else pd.Series(["upstream_supplier"] * len(df))
    rows.append(
        FlowStage(
            sample=sample,
            stage=stage,
            rows=len(df),
            events=df["event_id"].nunique() if "event_id" in df.columns else 0,
            affected_firms=df["affected_code"].nunique() if "affected_code" in df.columns else 0,
            upstream_rows=int(relation.eq("upstream_supplier").sum()),
            downstream_rows=int(relation.eq("downstream_customer").sum()),
        )
    )


def load_event_meta() -> pd.DataFrame:
    meta = pd.read_csv(EVENT_META_PATH, dtype={"event_id": str, "focal_code": str, "stock_code": str})
    meta["event_id"] = meta["event_id"].astype(str)
    meta["focal_code"] = meta["focal_code"].map(code6)
    meta["event_date"] = pd.to_datetime(meta["event_date"], errors="coerce")
    meta["event_year"] = meta["event_date"].dt.year
    meta["strict_genai_event"] = strict_genai_text(
        meta,
        ["answer_terms", "question_terms", "sample_answer", "sample_question"],
    )
    keep = [
        "event_id",
        "focal_code",
        "event_date",
        "event_year",
        "answer_terms",
        "question_terms",
        "sources",
        "company_name",
        "sample_answer",
        "sample_question",
        "strict_genai_event",
    ]
    return meta[[c for c in keep if c in meta.columns]].drop_duplicates("event_id")


def supplier_prior_genai_dates(meta: pd.DataFrame) -> pd.Series:
    strict = meta[meta["strict_genai_event"].eq(True) & meta["event_date"].notna()].copy()
    return strict.groupby("focal_code")["event_date"].min()


def normalize_chain_panel(df: pd.DataFrame, sample: str, meta: pd.DataFrame, flow: list[FlowStage]) -> pd.DataFrame:
    out = df.copy()
    out["event_id"] = out["event_id"].astype(str)
    out["focal_code"] = out["focal_code"].map(code6)
    out["customer_code"] = out["customer_code"].map(code6)
    out["affected_code"] = out["affected_code"].map(code6)
    out["event_date"] = pd.to_datetime(out["event_date"], errors="coerce")
    out["event_year"] = pd.to_numeric(out["event_year"], errors="coerce")
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out["relation"] = out["relation"].fillna("").astype(str)
    out["sample"] = sample
    add_flow(flow, sample, "input_existing_chain_panel", out)

    out = out.merge(
        meta.drop(columns=["focal_code", "event_date", "event_year"], errors="ignore"),
        on="event_id",
        how="left",
    )
    out["strict_genai_event"] = out["strict_genai_event"].fillna(False).astype(bool)
    out = out[out["event_year"].ge(2023) & out["strict_genai_event"]].copy()
    add_flow(flow, sample, "strict_genai_2023plus", out)

    out = out[out["year"].between(out["event_year"] - 5, out["event_year"] - 1)].copy()
    add_flow(flow, sample, "relation_year_window_tminus5_to_tminus1", out)

    out = out[out["customer_code"].ne(out["affected_code"])].copy()
    add_flow(flow, sample, "drop_customer_equals_affected", out)
    return out


def load_formal_panel(flow: list[FlowStage]) -> pd.DataFrame:
    raw = pd.read_csv(FORMAL_CHAIN_PATH, dtype={"customer_event_id": str, "customer_code": str, "supplier_code": str})
    out = raw.copy()
    out["event_id"] = out["customer_event_id"].astype(str)
    out["focal_code"] = out["customer_code"].map(code6)
    out["customer_code"] = out["customer_code"].map(code6)
    out["affected_code"] = out["supplier_code"].map(code6)
    out["event_date"] = pd.to_datetime(out["event_date"], errors="coerce")
    out["event_year"] = out["event_date"].dt.year
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out["relation"] = "upstream_supplier"
    out["sample"] = "formal_announcement_only"
    out["strict_genai_event"] = strict_genai_text(
        out,
        ["matched_genai_terms", "announcement_title", "genai_span_examples"],
    )
    add_flow(flow, "formal_announcement_only", "input_existing_formal_supplier_panel", out)

    out = out[out["event_year"].ge(2023) & out["strict_genai_event"]].copy()
    add_flow(flow, "formal_announcement_only", "strict_genai_2023plus", out)
    out = out[out["year"].between(out["event_year"] - 5, out["event_year"] - 1)].copy()
    add_flow(flow, "formal_announcement_only", "relation_year_window_tminus5_to_tminus1", out)
    out = out[out["customer_code"].ne(out["affected_code"])].copy()
    add_flow(flow, "formal_announcement_only", "drop_customer_equals_affected", out)
    return out


def drop_affected_prior_genai(
    df: pd.DataFrame,
    sample: str,
    prior_dates: pd.Series,
    flow: list[FlowStage],
) -> pd.DataFrame:
    out = df.copy()
    out["affected_prior_genai_date"] = out["affected_code"].map(prior_dates)
    out["affected_prior_genai"] = (
        out["affected_prior_genai_date"].notna()
        & out["event_date"].notna()
        & (out["affected_prior_genai_date"] <= out["event_date"])
    )
    out = out[~out["affected_prior_genai"]].copy()
    add_flow(flow, sample, "drop_affected_prior_or_same_day_genai_event", out)
    return out


def load_returns(codes: set[str], min_event_date: pd.Timestamp, max_event_date: pd.Timestamp) -> pd.DataFrame:
    min_date = min_event_date - pd.tseries.offsets.BDay(15)
    max_date = max_event_date + pd.tseries.offsets.BDay(15)
    chunks: list[pd.DataFrame] = []
    usecols = ["peer_code", "date", "ret", "mkt_ret", "trdsta", "limit_status", "alpha_mm", "beta_mm", "est_obs"]
    for chunk in pd.read_csv(RETURNS_PATH, usecols=usecols, chunksize=1_000_000):
        chunk["peer_code"] = chunk["peer_code"].map(code6)
        chunk = chunk[chunk["peer_code"].isin(codes)]
        if chunk.empty:
            continue
        chunk["date"] = pd.to_datetime(chunk["date"], errors="coerce")
        chunk = chunk[chunk["date"].between(min_date, max_date)]
        if chunk.empty:
            continue
        for col in ["ret", "mkt_ret", "trdsta", "limit_status", "alpha_mm", "beta_mm", "est_obs"]:
            chunk[col] = pd.to_numeric(chunk[col], errors="coerce")
        valid = (
            chunk["trdsta"].eq(1)
            & chunk["limit_status"].fillna(0).eq(0)
            & chunk["alpha_mm"].notna()
            & chunk["beta_mm"].notna()
            & chunk["ret"].notna()
            & chunk["mkt_ret"].notna()
        )
        chunk["valid_market_model_day"] = valid
        chunk["abret_mm"] = np.where(valid, chunk["ret"] - (chunk["alpha_mm"] + chunk["beta_mm"] * chunk["mkt_ret"]), np.nan)
        chunks.append(chunk)
    if not chunks:
        return pd.DataFrame(columns=usecols + ["valid_market_model_day", "abret_mm"])
    return pd.concat(chunks, ignore_index=True).drop_duplicates(["peer_code", "date"]).sort_values(["peer_code", "date"])


def attach_event_returns(panel: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    lookup: dict[str, pd.DataFrame] = {}
    for code, sub in returns.groupby("peer_code", sort=False):
        lookup[code] = sub.sort_values("date").reset_index(drop=True)

    records: list[dict[str, object]] = []
    for rec in panel.to_dict("records"):
        code = code6(rec.get("affected_code"))
        event_date = pd.Timestamp(rec.get("event_date"))
        sub = lookup.get(code)
        if sub is None or pd.isna(event_date):
            records.append({**rec, "date_0": pd.NaT})
            continue
        dates = sub["date"].to_numpy(dtype="datetime64[ns]")
        pos0 = int(np.searchsorted(dates, np.datetime64(event_date.normalize()), side="left"))
        if pos0 >= len(sub):
            records.append({**rec, "date_0": pd.NaT})
            continue
        item = dict(rec)
        for label, offset in [("m1", -1), ("0", 0), ("p1", 1)]:
            pos = pos0 + offset
            if pos < 0 or pos >= len(sub):
                item[f"date_{label}"] = pd.NaT
                item[f"ar_{label}_mm"] = np.nan
                item[f"ok_{label}"] = False
                continue
            row = sub.iloc[pos]
            item[f"date_{label}"] = row["date"]
            item[f"ar_{label}_mm"] = row["abret_mm"]
            item[f"ok_{label}"] = bool(row["valid_market_model_day"])
        ar0 = item.get("ar_0_mm", np.nan)
        arp1 = item.get("ar_p1_mm", np.nan)
        arm1 = item.get("ar_m1_mm", np.nan)
        item["car_0_p1_mm"] = ar0 + arp1 if pd.notna(ar0) and pd.notna(arp1) else np.nan
        item["car_m1_p1_mm"] = arm1 + ar0 + arp1 if pd.notna(arm1) and pd.notna(ar0) and pd.notna(arp1) else np.nan
        records.append(item)
    return pd.DataFrame(records)


def one_sample_stats(values: pd.Series) -> dict[str, float | int]:
    vals = pd.to_numeric(values, errors="coerce").dropna().to_numpy(dtype=float)
    n = len(vals)
    if n == 0:
        return {
            "n": 0,
            "mean": np.nan,
            "se": np.nan,
            "t": np.nan,
            "p_ttest": np.nan,
            "median": np.nan,
            "positive_rate": np.nan,
            "p_sign": np.nan,
            "p_wilcoxon": np.nan,
        }
    mean = float(np.mean(vals))
    se = float(np.std(vals, ddof=1) / math.sqrt(n)) if n > 1 else np.nan
    if n > 1 and np.nanstd(vals, ddof=1) > 0:
        t_stat, p_ttest = stats.ttest_1samp(vals, 0.0)
    else:
        t_stat, p_ttest = np.nan, np.nan
    try:
        p_wilcoxon = stats.wilcoxon(vals, zero_method="wilcox").pvalue if n > 0 and np.any(vals != 0) else np.nan
    except ValueError:
        p_wilcoxon = np.nan
    pos = int(np.sum(vals > 0))
    p_sign = stats.binomtest(pos, n, 0.5).pvalue if n > 0 else np.nan
    return {
        "n": n,
        "mean": mean,
        "se": se,
        "t": float(t_stat) if pd.notna(t_stat) else np.nan,
        "p_ttest": float(p_ttest) if pd.notna(p_ttest) else np.nan,
        "median": float(np.median(vals)),
        "positive_rate": float(pos / n),
        "p_sign": float(p_sign),
        "p_wilcoxon": float(p_wilcoxon) if pd.notna(p_wilcoxon) else np.nan,
    }


def event_study_tests(samples: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for sample, df in samples.items():
        for relation, sub in df.groupby("relation", dropna=False):
            for label, col in [("day_m1", "ar_m1_mm"), ("day_0", "ar_0_mm"), ("day_p1", "ar_p1_mm")]:
                rows.append({"sample": sample, "relation": relation, "day": label, **one_sample_stats(sub[col])})
    return pd.DataFrame(rows)


def car_tests(samples: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for sample, df in samples.items():
        for relation, sub in df.groupby("relation", dropna=False):
            for outcome in ["car_0_p1_mm", "car_m1_p1_mm"]:
                rows.append({"sample": sample, "relation": relation, "outcome": outcome, **one_sample_stats(sub[outcome])})
    return pd.DataFrame(rows)


def validation_checks(samples: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for sample, df in samples.items():
        if df.empty:
            continue
        year_ok = df["year"].between(df["event_year"] - 5, df["event_year"] - 1)
        no_self = df["customer_code"].ne(df["affected_code"])
        ok0 = df["ok_0"].where(df["ok_0"].notna(), False).astype(bool)
        okp1 = df["ok_p1"].where(df["ok_p1"].notna(), False).astype(bool)
        rows.extend(
            [
                {"sample": sample, "check": "relation_year_window_ok", "passed": bool(year_ok.all()), "violations": int((~year_ok).sum())},
                {"sample": sample, "check": "customer_not_equal_affected", "passed": bool(no_self.all()), "violations": int((~no_self).sum())},
                {"sample": sample, "check": "ar0_has_valid_market_model_days_only", "passed": bool(ok0[df["ar_0_mm"].notna()].all()), "violations": int((df["ar_0_mm"].notna() & ~ok0).sum())},
                {"sample": sample, "check": "car0p1_requires_valid_day0_and_day1", "passed": bool((df["car_0_p1_mm"].isna() | (ok0 & okp1)).all()), "violations": int((df["car_0_p1_mm"].notna() & ~(ok0 & okp1)).sum())},
            ]
        )
    return pd.DataFrame(rows)


def replication_decision(day_tests: pd.DataFrame, car_df: pd.DataFrame) -> pd.DataFrame:
    main_day = day_tests[
        day_tests["sample"].eq("first_valid_events")
        & day_tests["relation"].eq("upstream_supplier")
        & day_tests["day"].eq("day_0")
    ]
    pre_day = day_tests[
        day_tests["sample"].eq("first_valid_events")
        & day_tests["relation"].eq("upstream_supplier")
        & day_tests["day"].eq("day_m1")
    ]
    main_car = car_df[
        car_df["sample"].eq("first_valid_events")
        & car_df["relation"].eq("upstream_supplier")
        & car_df["outcome"].eq("car_0_p1_mm")
    ]
    pre_ok = bool(pre_day["p_ttest"].iloc[0] >= 0.10) if not pre_day.empty and pd.notna(pre_day["p_ttest"].iloc[0]) else False

    ar0_signal = False
    car_signal = False
    if not main_day.empty:
        r = main_day.iloc[0]
        ar0_signal = bool(r["mean"] > 0 and r["p_ttest"] < 0.10 and r["positive_rate"] > 0.5 and pre_ok)
    if not main_car.empty:
        r = main_car.iloc[0]
        car_signal = bool(r["mean"] > 0 and r["p_ttest"] < 0.10 and r["positive_rate"] > 0.5 and pre_ok)

    verdict = "has_china_replication_signal" if (ar0_signal or car_signal) else "main_effect_not_replicated"
    reason = (
        "upstream supplier AR0 or CAR[0,+1] is positive at p<0.10, day -1 is not significant, and positive rate exceeds 0.5"
        if verdict == "has_china_replication_signal"
        else "first-event upstream supplier AR0/CAR[0,+1] does not satisfy the pre-specified positive-significance-positive-rate gate"
    )
    return pd.DataFrame(
        [
            {
                "main_sample": "first_valid_events",
                "main_relation": "upstream_supplier",
                "verdict": verdict,
                "ar0_signal": ar0_signal,
                "car0p1_signal": car_signal,
                "day_m1_not_significant": pre_ok,
                "reason": reason,
            }
        ]
    )


def fmt(x: object) -> str:
    if pd.isna(x):
        return ""
    if isinstance(x, (float, np.floating)):
        return f"{x:.6g}"
    return str(x)


def md_table(df: pd.DataFrame, cols: list[str] | None = None, max_rows: int | None = None) -> str:
    if cols is not None:
        df = df[cols]
    if max_rows is not None:
        df = df.head(max_rows)
    if df.empty:
        return "无"
    lines = ["| " + " | ".join(df.columns) + " |", "| " + " | ".join(["---"] * len(df.columns)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(fmt(row[col]).replace("\n", " ") for col in df.columns) + " |")
    return "\n".join(lines)


def write_report(
    sample_flow: pd.DataFrame,
    day_tests: pd.DataFrame,
    car_df: pd.DataFrame,
    decision: pd.DataFrame,
    checks: pd.DataFrame,
) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    flow_last = sample_flow[sample_flow["stage"].isin(["after_ar0_available", "after_car0p1_available"])].copy()
    main_day = day_tests[
        day_tests["sample"].eq("first_valid_events")
        & day_tests["relation"].eq("upstream_supplier")
    ].copy()
    main_car = car_df[
        car_df["sample"].eq("first_valid_events")
        & car_df["relation"].eq("upstream_supplier")
    ].copy()
    placebo = pd.concat(
        [
            day_tests[day_tests["relation"].eq("downstream_customer")].assign(test_type="AR day"),
            car_df[car_df["relation"].eq("downstream_customer")].assign(test_type="CAR"),
        ],
        ignore_index=True,
        sort=False,
    )
    text = f"""# v23 Qian 供应商主效应中国复刻审计

日期：2026-06-02

## 结论

本轮只做 `Qian et al. supplier stock reaction` 的最小复刻审计，不把结果包装成新论文。

预设判据：

```text
first valid focal event per firm
upstream listed supplier
AR0 或 CAR[0,+1] > 0 且 p < 0.10
Day -1 不显著
对应正收益比例 > 0.5
```

审计结论：

{md_table(decision)}

## 样本流失

{md_table(flow_last)}

## 主样本 Qian-style AR[-1,0,+1]

{md_table(main_day, ["day", "n", "mean", "se", "t", "p_ttest", "median", "positive_rate", "p_sign", "p_wilcoxon"])}

## 主样本 CAR

{md_table(main_car, ["outcome", "n", "mean", "se", "t", "p_ttest", "median", "positive_rate", "p_sign", "p_wilcoxon"])}

## 方向 placebo

`downstream_customer` 只用于判断是否存在泛 AI 热点反应，不作为 Qian-style 主结果。

{md_table(placebo, max_rows=40)}

## 校验

{md_table(checks)}

## 口径说明

- 事件：2023 年后严格 GenAI 事件，要求文本或触发词含 `AIGC / ChatGPT / GPT / 大模型 / 生成式AI / DeepSeek / LLM` 等；不靠泛 AI、RAG、Agent、NLP 单独入样。
- 供应链：CSMAR 供应链网络关系表和前五大供应商/客户表；关系年份必须在事件年前 5 年到前 1 年。
- 主关系：`upstream_supplier`，即 focal customer 的既有上市供应商。
- 最小混杂处理：剔除供应商自身在客户事件日之前或当天已有严格 GenAI 事件的观测。
- AR：使用现有 market-model 参数，剔除停牌、涨跌停、缺失 alpha/beta 或缺失收益的交易日。
- 未完成限制：本轮未系统剔除供应商同日业绩、并购、重大合同、监管处罚等非 GenAI 重大公告污染；也未做 PSM、IV、Heckman 或异质性。
"""
    DOC_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    flow: list[FlowStage] = []

    meta = load_event_meta()
    prior_dates = supplier_prior_genai_dates(meta)

    first = normalize_chain_panel(pd.read_csv(FIRST_CHAIN_PATH), "first_valid_events", meta, flow)
    all_events = normalize_chain_panel(pd.read_csv(ALL_CHAIN_PATH), "all_valid_events", meta, flow)
    formal = load_formal_panel(flow)

    first = drop_affected_prior_genai(first, "first_valid_events", prior_dates, flow)
    all_events = drop_affected_prior_genai(all_events, "all_valid_events", prior_dates, flow)
    formal = drop_affected_prior_genai(formal, "formal_announcement_only", prior_dates, flow)

    panels = {"first_valid_events": first, "all_valid_events": all_events, "formal_announcement_only": formal}
    all_for_returns = pd.concat([p for p in panels.values() if not p.empty], ignore_index=True, sort=False)
    codes = set(all_for_returns["affected_code"].dropna().map(code6))
    min_date = all_for_returns["event_date"].min()
    max_date = all_for_returns["event_date"].max()
    returns = load_returns(codes, min_date, max_date)

    attached: dict[str, pd.DataFrame] = {}
    for sample, panel in panels.items():
        tmp = attach_event_returns(panel, returns)
        add_flow(flow, sample, "after_returns_attached", tmp)
        add_flow(flow, sample, "after_ar0_available", tmp[tmp["ar_0_mm"].notna()])
        add_flow(flow, sample, "after_car0p1_available", tmp[tmp["car_0_p1_mm"].notna()])
        attached[sample] = tmp
        tmp.to_csv(OUT_DIR / f"analysis_sample_{sample}.csv.gz", index=False, encoding="utf-8-sig")
        if sample == "first_valid_events":
            stata_cols = [
                "sample",
                "event_id",
                "relation",
                "focal_code",
                "affected_code",
                "event_date",
                "event_year",
                "year",
                "ar_m1_mm",
                "ar_0_mm",
                "ar_p1_mm",
                "car_0_p1_mm",
                "car_m1_p1_mm",
                "ok_m1",
                "ok_0",
                "ok_p1",
            ]
            tmp[[c for c in stata_cols if c in tmp.columns]].to_csv(
                OUT_DIR / "analysis_sample_first_valid_events_for_stata.csv",
                index=False,
                encoding="utf-8-sig",
            )

    sample_flow = pd.DataFrame([stage.__dict__ for stage in flow])
    day_tests = event_study_tests(attached)
    car_df = car_tests(attached)
    checks = validation_checks(attached)
    decision = replication_decision(day_tests, car_df)

    sample_flow.to_csv(OUT_DIR / "sample_flow.csv", index=False, encoding="utf-8-sig")
    day_tests.to_csv(OUT_DIR / "event_study_day_tests.csv", index=False, encoding="utf-8-sig")
    car_df.to_csv(OUT_DIR / "car_tests.csv", index=False, encoding="utf-8-sig")
    checks.to_csv(OUT_DIR / "validation_checks.csv", index=False, encoding="utf-8-sig")
    decision.to_csv(OUT_DIR / "replication_decision.csv", index=False, encoding="utf-8-sig")

    direction_placebo = pd.concat(
        [
            day_tests[day_tests["relation"].eq("downstream_customer")].assign(test_family="event_day_ar"),
            car_df[car_df["relation"].eq("downstream_customer")].assign(test_family="car"),
        ],
        ignore_index=True,
        sort=False,
    )
    direction_placebo.to_csv(OUT_DIR / "direction_placebo_summary.csv", index=False, encoding="utf-8-sig")

    write_report(sample_flow, day_tests, car_df, decision, checks)

    print(decision.to_string(index=False))
    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
