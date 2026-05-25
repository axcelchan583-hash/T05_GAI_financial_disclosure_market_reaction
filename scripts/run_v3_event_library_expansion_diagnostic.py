#!/usr/bin/env python3
"""Expansion diagnostic for v3 event library.

This does not replace the main v3 design. It stress-tests whether the current
event bottleneck comes from using only first formal announcements.

Outputs three layers:
1. Formal CNINFO announcement events, all firm-events.
2. Formal CNINFO announcement events, first firm-event only.
3. Supplemental IR / interactive-QA events, clearly labeled as non-main sample.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_v3_genai_specificity_car_pilot import (  # noqa: E402
    A_SHARE_PAT,
    DOC_OUT as BASE_PILOT_DOC,
    OUT_DIR as BASE_OUT_DIR,
    compute_car,
    run_regression,
    specificity_metrics,
)

OUT_DIR = ROOT / "results" / "v3_event_library_expansion_diagnostic"
DOC_OUT = ROOT / "docs" / "选题" / "19_v3_event_library_expansion_diagnostic_20260522.md"

OFFICIAL_EVENTS = BASE_OUT_DIR / "cninfo_genai_event_candidates_with_specificity.csv"
OFFICIAL_FIRST = BASE_OUT_DIR / "cninfo_genai_first_events_with_specificity.csv"
IRQA_EVENTS = ROOT / "results" / "v8_3_external_evidence_link_pilot" / "public_irqa_events_for_linking.csv"


def table(df: pd.DataFrame, max_rows: int = 25) -> str:
    if df.empty:
        return "无"
    show = df.head(max_rows).copy()
    cols = list(show.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in show.iterrows():
        vals = [str(row.get(c, "")).replace("\n", " ").replace("|", "\\|")[:220] for c in cols]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def load_official(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, dtype={"sec_code": str})
    df["sec_code"] = df["sec_code"].str.zfill(6)
    df = df[df["sec_code"].map(lambda x: bool(A_SHARE_PAT.match(str(x))))].copy()
    df["sample_layer"] = "formal_cninfo_announcement"
    return df


def load_irqa_supplement() -> pd.DataFrame:
    if not IRQA_EVENTS.exists():
        return pd.DataFrame()
    src = pd.read_csv(IRQA_EVENTS, dtype={"Symbol": str})
    src["Symbol"] = src["Symbol"].str.zfill(6)
    src = src[src["Symbol"].map(lambda x: bool(A_SHARE_PAT.match(str(x))))].copy()
    src["event_text"] = src["event_text"].fillna("").astype(str)
    src = src[src["event_text"].str.len() >= 20].copy()

    rows = []
    for _, row in src.iterrows():
        metrics = specificity_metrics(row["event_text"])
        rows.append(
            {
                "query_terms": row.get("matched_terms", ""),
                "sec_code": row["Symbol"],
                "sec_name": row.get("company_or_short_name", ""),
                "announcement_id": row.get("source_url", ""),
                "announcement_title": row.get("event_source", "irqa_event"),
                "announcement_date": row.get("event_date", row.get("event_date_dt", "")),
                "pdf_url": row.get("source_url", ""),
                "download_status": "text_source",
                **metrics,
                "matched_genai_terms": row.get("matched_terms", ""),
                "genai_span_examples": row["event_text"][:1000],
                "event_source": row.get("event_source", ""),
                "source_url": row.get("source_url", ""),
                "sample_layer": "supplemental_irqa_not_main",
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["announcement_date_dt"] = pd.to_datetime(out["announcement_date"], errors="coerce")
    out = out[out["announcement_date_dt"].notna()].copy()
    out = out.sort_values(["sec_code", "announcement_date_dt", "announcement_id"])
    out["event_rank_within_firm"] = out.groupby("sec_code").cumcount() + 1
    return out


def add_simple_tstats(reg: pd.DataFrame) -> pd.DataFrame:
    out = reg.copy()
    if {"coef", "std_err"}.issubset(out.columns):
        out["t_stat"] = pd.to_numeric(out["coef"], errors="coerce") / pd.to_numeric(out["std_err"], errors="coerce")
    return out


def summarize_layer(name: str, events: pd.DataFrame, car: pd.DataFrame, reg: pd.DataFrame) -> dict:
    return {
        "sample_layer": name,
        "events_before_car": len(events),
        "unique_firms_before_car": events["sec_code"].nunique() if not events.empty else 0,
        "car_linked_events": len(car),
        "car_linked_firms": car["sec_code"].nunique() if not car.empty else 0,
        "mean_specificity": events["specificity"].mean() if "specificity" in events else np.nan,
        "mean_abs_car": car["abs_car_m1_p1"].mean() if "abs_car_m1_p1" in car else np.nan,
        "specificity_coef": reg.loc[reg["term"].eq("specificity"), "coef"].iloc[0]
        if "term" in reg and reg["term"].eq("specificity").any()
        else np.nan,
        "specificity_t": (
            reg.loc[reg["term"].eq("specificity"), "t_stat"].iloc[0]
            if "term" in reg and "t_stat" in reg and reg["term"].eq("specificity").any()
            else np.nan
        ),
    }


def write_layer_outputs(name: str, events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    events_path = OUT_DIR / f"{name}_events_before_car.csv"
    car_path = OUT_DIR / f"{name}_events_with_car.csv"
    reg_path = OUT_DIR / f"{name}_ols_abs_car_on_specificity.csv"
    if events_path.exists() and car_path.exists() and reg_path.exists():
        car = pd.read_csv(car_path, dtype={"sec_code": str})
        reg = pd.read_csv(reg_path)
        return car, reg
    if events.empty:
        car = pd.DataFrame()
        reg = run_regression(car)
    else:
        car = compute_car(events)
        reg = run_regression(car)
    events.to_csv(events_path, index=False, encoding="utf-8-sig")
    car.to_csv(car_path, index=False, encoding="utf-8-sig")
    reg = add_simple_tstats(reg)
    reg.to_csv(reg_path, index=False, encoding="utf-8-sig")
    return car, reg


def write_layer_from_existing_car(name: str, events: pd.DataFrame, car: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    events.to_csv(OUT_DIR / f"{name}_events_before_car.csv", index=False, encoding="utf-8-sig")
    car.to_csv(OUT_DIR / f"{name}_events_with_car.csv", index=False, encoding="utf-8-sig")
    reg = add_simple_tstats(run_regression(car))
    reg.to_csv(OUT_DIR / f"{name}_ols_abs_car_on_specificity.csv", index=False, encoding="utf-8-sig")
    return car, reg


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    official_all = load_official(OFFICIAL_EVENTS)
    official_first = load_official(OFFICIAL_FIRST)
    irqa = load_irqa_supplement()
    summaries = []
    cars = {}
    regs = {}

    print(f"Layer formal_all_events: events={len(official_all)}, firms={official_all['sec_code'].nunique() if not official_all.empty else 0}", flush=True)
    formal_all_car, formal_all_reg = write_layer_outputs("formal_all_events", official_all)
    cars["formal_all_events"] = formal_all_car
    regs["formal_all_events"] = formal_all_reg
    summaries.append(summarize_layer("formal_all_events", official_all, formal_all_car, formal_all_reg))

    formal_first_car = formal_all_car[formal_all_car.get("event_rank_within_firm", pd.Series(dtype=float)).eq(1)].copy()
    print(f"Layer formal_first_events: events={len(official_first)}, firms={official_first['sec_code'].nunique() if not official_first.empty else 0}", flush=True)
    formal_first_car, formal_first_reg = write_layer_from_existing_car("formal_first_events", official_first, formal_first_car)
    cars["formal_first_events"] = formal_first_car
    regs["formal_first_events"] = formal_first_reg
    summaries.append(summarize_layer("formal_first_events", official_first, formal_first_car, formal_first_reg))

    print(f"Layer irqa_all_events_supplement: events={len(irqa)}, firms={irqa['sec_code'].nunique() if not irqa.empty else 0}", flush=True)
    irqa_car, irqa_reg = write_layer_outputs("irqa_all_events_supplement", irqa)
    cars["irqa_all_events_supplement"] = irqa_car
    regs["irqa_all_events_supplement"] = irqa_reg
    summaries.append(summarize_layer("irqa_all_events_supplement", irqa, irqa_car, irqa_reg))

    irqa_first = irqa[irqa["event_rank_within_firm"].eq(1)].copy() if not irqa.empty else irqa
    irqa_first_car = irqa_car[irqa_car.get("event_rank_within_firm", pd.Series(dtype=float)).eq(1)].copy()
    print(f"Layer irqa_first_events_supplement: events={len(irqa_first)}, firms={irqa_first['sec_code'].nunique() if not irqa_first.empty else 0}", flush=True)
    irqa_first_car, irqa_first_reg = write_layer_from_existing_car("irqa_first_events_supplement", irqa_first, irqa_first_car)
    cars["irqa_first_events_supplement"] = irqa_first_car
    regs["irqa_first_events_supplement"] = irqa_first_reg
    summaries.append(summarize_layer("irqa_first_events_supplement", irqa_first, irqa_first_car, irqa_first_reg))

    summary = pd.DataFrame(summaries)
    summary.to_csv(OUT_DIR / "event_library_expansion_summary.csv", index=False, encoding="utf-8-sig")

    local_return_cutoff = pd.Timestamp("2026-02-13")
    irqa_year_counts = (
        irqa.groupby(irqa["announcement_date_dt"].dt.year)
        .size()
        .rename_axis("year")
        .reset_index(name="events")
        if not irqa.empty
        else pd.DataFrame(columns=["year", "events"])
    )
    irqa_before_return_cutoff = irqa[irqa["announcement_date_dt"].le(local_return_cutoff)].copy() if not irqa.empty else irqa

    formal_examples = cars["formal_all_events"].sort_values("abs_car_m1_p1", ascending=False) if not cars["formal_all_events"].empty else pd.DataFrame()
    irqa_examples = cars["irqa_all_events_supplement"].sort_values("abs_car_m1_p1", ascending=False) if not cars["irqa_all_events_supplement"].empty else pd.DataFrame()
    example_cols = [
        "sec_code",
        "sec_name",
        "announcement_date",
        "announcement_title",
        "event_source",
        "specificity",
        "genai_span_tokens",
        "matched_genai_terms",
        "abs_car_m1_p1",
        "car_m1_p1",
    ]

    report = f"""# v3 事件库扩容诊断

日期：2026-05-22

## 1. 目的

上一轮 v3 最小试跑已经证明：

```text
GenAI disclosure specificity -> |CAR[-1,+1]|
```

这条数据链路可以跑通，但“首个非定期正式公告”只有 15 个可连接 CAR 的事件。本轮只做扩容诊断，不改变主设计。

基础试跑报告：`{BASE_PILOT_DOC.relative_to(ROOT)}`

## 2. 样本层

| layer | 解释 |
|---|---|
| formal_all_events | 巨潮正式公告中所有非定期 GenAI 事件；不再只取每家公司首个事件 |
| formal_first_events | 巨潮正式公告中每家公司首个 GenAI 事件；对应主样本保守版 |
| irqa_all_events_supplement | IR 活动记录 / 互动问答 GenAI 事件；只作为补充样本，不建议直接放主回归 |
| irqa_first_events_supplement | IR/互动问答每家公司首个事件；用于判断补充样本的横截面覆盖 |

## 3. 扩容结果

{table(summary)}

## 3.1 IR/互动问答的时间覆盖问题

本地日收益当前只能稳定算到 `{local_return_cutoff.date()}`。IR/互动问答补充样本的年份分布如下：

{table(irqa_year_counts)}

在 `{local_return_cutoff.date()}` 及以前的 IR/互动问答事件只有 `{len(irqa_before_return_cutoff)}` 条、`{irqa_before_return_cutoff["sec_code"].nunique() if not irqa_before_return_cutoff.empty else 0}` 家公司。因此，本轮 IR/互动问答不是“文本样本不够”，而是“行情窗口尚未补到 2026 年后半段”。等日收益更新到 2026 年 5 月以后，IR/互动问答层的 CAR 样本会大幅增加。

## 4. 回归输出：正式公告全部事件

{table(regs["formal_all_events"])}

## 5. 回归输出：IR/互动问答补充样本

{table(regs["irqa_all_events_supplement"])}

## 6. 正式公告 CAR 最大的例子

{table(formal_examples[[c for c in example_cols if c in formal_examples.columns]], max_rows=20)}

## 7. IR/互动问答 CAR 最大的例子

{table(irqa_examples[[c for c in example_cols if c in irqa_examples.columns]], max_rows=20)}

## 8. 判断

正式公告层如果仍然只有几十条以内，说明主样本不是“没跑出来”，而是题材本身在交易所正式公告中很稀疏。

IR/互动问答能放大样本，但它们的信息披露制度含义弱于交易所正式公告，且事件日信息泄露、投资者问题诱导、管理层选择性回复都更难处理。因此它们更适合：

1. 做 external validation；
2. 做补充信息环境样本；
3. 支持 case evidence；
4. 帮助训练 GenAI 句段识别规则。

若要把 IR/互动问答升级为主样本，需要把论文问题从“正式公告的信息含量”改成“多渠道 GenAI 沟通的信息含量”，这会是另一个版本。
"""
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text(report, encoding="utf-8")
    print(f"summary={OUT_DIR / 'event_library_expansion_summary.csv'}", flush=True)
    print(f"report={DOC_OUT}", flush=True)


if __name__ == "__main__":
    main()
