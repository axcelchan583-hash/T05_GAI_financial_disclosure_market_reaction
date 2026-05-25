#!/usr/bin/env python3
"""Coarse feasibility pilot for v8.3.

This is not the claim-level pilot. It only checks whether existing annual
AI-disclosure and AI-investment data can form a rough disclosure/support grid.
"""

from __future__ import annotations

import math
from pathlib import Path
from zipfile import ZipFile

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path("/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/上市公司数据相关信息")
OUT_DIR = ROOT / "results" / "v8_3_coarse_pilot"
DOC_OUT = ROOT / "docs" / "选题" / "13_v8_3_coarse_pilot_20260517.md"

WORD_ZIP = DATA_ROOT / "人工智能词频统计表100453121(仅供沪江大学使用).zip"
INVEST_ZIP = DATA_ROOT / "人工智能投资水平131920031(仅供沪江大学使用).zip"


def read_first_xlsx_from_zip(path: Path) -> pd.DataFrame:
    with ZipFile(path) as zf:
        xlsx_names = [name for name in zf.namelist() if name.lower().endswith(".xlsx")]
        if not xlsx_names:
            raise FileNotFoundError(f"No .xlsx found in {path}")
        with zf.open(xlsx_names[0]) as f:
            df = pd.read_excel(f)
    return df


def clean_common(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df[pd.to_datetime(df["EndDate"], errors="coerce").notna()].copy()
    df["EndDate"] = pd.to_datetime(df["EndDate"])
    df["year"] = df["EndDate"].dt.year
    df["Symbol"] = df["Symbol"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(6)
    return df


def numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def pct(x: float) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return ""
    return f"{100 * x:.2f}%"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)

    words = clean_common(read_first_xlsx_from_zip(WORD_ZIP))
    words = numeric(
        words,
        [
            "AnnualReportAIWordFre",
            "AnnualReportAISentenceFre",
            "AnnualReportSentence",
            "MDAAIWordFre",
            "MDAAIAISentenceFre",
            "MDASentence",
        ],
    )

    invest = clean_common(read_first_xlsx_from_zip(INVEST_ZIP))
    invest = numeric(
        invest,
        [
            "Category",
            "AISoftInvest",
            "AISoftInvestValueAdd",
            "AIHardInvest",
            "AIHardInvestValueAdd",
            "AIInvestTotal",
            "AIInvestTotalValueAdd",
            "AIInvestLevel",
        ],
    )

    invest_year = (
        invest.groupby(["Symbol", "year", "ShortName"], as_index=False)
        .agg(
            AIInvestTotal=("AIInvestTotal", "max"),
            AIInvestTotalValueAdd=("AIInvestTotalValueAdd", "max"),
            AIInvestLevel=("AIInvestLevel", "max"),
        )
    )

    word_year = words[
        [
            "Symbol",
            "year",
            "ShortName",
            "AnnualReportAIWordFre",
            "AnnualReportAISentenceFre",
            "AnnualReportSentence",
            "MDAAIWordFre",
            "MDAAIAISentenceFre",
            "MDASentence",
        ]
    ].copy()

    panel = word_year.merge(
        invest_year.drop(columns=["ShortName"]),
        on=["Symbol", "year"],
        how="left",
    )

    panel["MDA_AI_sentence_share"] = panel["MDAAIAISentenceFre"] / panel["MDASentence"].replace({0: pd.NA})
    panel["AR_AI_sentence_share"] = panel["AnnualReportAISentenceFre"] / panel["AnnualReportSentence"].replace({0: pd.NA})
    panel["HasAIDisclosure"] = (panel["MDAAIAISentenceFre"].fillna(0) > 0) | (
        panel["AnnualReportAISentenceFre"].fillna(0) > 0
    )
    panel["HasCurrentAISupport"] = (panel["AIInvestTotal"].fillna(0) > 0) | (
        panel["AIInvestTotalValueAdd"].fillna(0) > 0
    )
    panel["NoCurrentAISupport"] = ~panel["HasCurrentAISupport"]

    panel = panel.sort_values(["Symbol", "year"])
    panel["FutureAISupport_t1"] = panel.groupby("Symbol")["HasCurrentAISupport"].shift(-1)
    panel["FutureAIInvestmentAdd_t1"] = panel.groupby("Symbol")["AIInvestTotalValueAdd"].shift(-1)
    panel["FutureAIRealization_t1"] = (panel["FutureAISupport_t1"] == True) | (
        panel["FutureAIInvestmentAdd_t1"].fillna(0) > 0
    )

    sample = panel[(panel["year"] >= 2023) & (panel["year"] <= 2025)].copy()
    sample = sample[sample["FutureAISupport_t1"].notna()].copy()

    # A coarse version of a "specificity/disclosure x support" grid.
    # It is not the v8.3 claim-level HighSpecificity variable.
    positive_disclosure = sample[sample["HasAIDisclosure"]].copy()
    if not positive_disclosure.empty:
        threshold = positive_disclosure["MDA_AI_sentence_share"].fillna(0).median()
    else:
        threshold = 0
    sample["HighAIDisclosureIntensity"] = sample["MDA_AI_sentence_share"].fillna(0) >= threshold
    sample.loc[~sample["HasAIDisclosure"], "HighAIDisclosureIntensity"] = False

    grid = (
        sample.groupby(["HighAIDisclosureIntensity", "NoCurrentAISupport"], dropna=False)
        .agg(
            n=("Symbol", "size"),
            firms=("Symbol", "nunique"),
            future_realization_rate=("FutureAIRealization_t1", "mean"),
            mean_mda_ai_sentence_share=("MDA_AI_sentence_share", "mean"),
            mean_current_ai_invest_level=("AIInvestLevel", "mean"),
        )
        .reset_index()
        .sort_values(["HighAIDisclosureIntensity", "NoCurrentAISupport"])
    )

    by_year = (
        sample.groupby("year")
        .agg(
            obs=("Symbol", "size"),
            firms=("Symbol", "nunique"),
            has_ai_disclosure=("HasAIDisclosure", "mean"),
            no_current_support=("NoCurrentAISupport", "mean"),
            future_realization_rate=("FutureAIRealization_t1", "mean"),
        )
        .reset_index()
    )

    core_cell = sample[(sample["HighAIDisclosureIntensity"]) & (sample["NoCurrentAISupport"])]
    top_examples = (
        core_cell.sort_values(["MDA_AI_sentence_share", "AnnualReportAISentenceFre"], ascending=False)
        .head(30)
        [
            [
                "Symbol",
                "ShortName",
                "year",
                "MDAAIAISentenceFre",
                "MDASentence",
                "MDA_AI_sentence_share",
                "AIInvestTotal",
                "AIInvestTotalValueAdd",
                "AIInvestLevel",
                "FutureAIRealization_t1",
            ]
        ]
    )

    sample.to_csv(OUT_DIR / "coarse_panel_2023_2025.csv", index=False)
    grid.to_csv(OUT_DIR / "coarse_2x2_grid.csv", index=False)
    by_year.to_csv(OUT_DIR / "coarse_by_year.csv", index=False)
    top_examples.to_csv(OUT_DIR / "coarse_core_cell_examples.csv", index=False)

    grid_md = grid.copy()
    for col in ["future_realization_rate", "mean_mda_ai_sentence_share", "mean_current_ai_invest_level"]:
        grid_md[col] = grid_md[col].map(lambda v: "" if pd.isna(v) else f"{v:.6f}")
    by_year_md = by_year.copy()
    for col in ["has_ai_disclosure", "no_current_support", "future_realization_rate"]:
        by_year_md[col] = by_year_md[col].map(pct)

    report = f"""# v8.3 粗 pilot：AI 披露强度 × 当前 AI 投资支撑

**日期**：2026-05-17

## 1. 这次跑了什么

这不是 v8.3 的 claim-level pilot。它只是用现成的年度数据先检查一个更粗的问题：

```text
AI 披露强度 × 当前 AI 投资支撑
    -> 下一年是否有 AI 投资支撑
```

目的不是验证主假说，而是判断数据中是否存在“披露多但当前支撑弱”的样本格。

## 2. 数据

- 披露侧：人工智能词频统计表 `AI_WordFreSta.xlsx`
- 支撑侧：人工智能投资水平 `AI_InvestmentLevel.xlsx`
- 样本期：2023-2025 中有下一年数据的 firm-year
- 口径：firm-year

## 3. 粗变量

```text
HighAIDisclosureIntensity = MD&A AI sentence share 在有 AI 披露样本中的中位数以上
NoCurrentAISupport = 当年 AIInvestTotal 与 AIInvestTotalValueAdd 均不大于 0
FutureAIRealization_t1 = 下一年存在 AI 投资支撑或新增 AI 投资
```

注意：`HighAIDisclosureIntensity` 不是 `HighSpecificity`，`FutureAIRealization_t1` 也不是 claim-matched realization。

## 4. 年度概况

{by_year_md.to_markdown(index=False)}

## 5. 粗 2x2 结果

{grid_md.to_markdown(index=False)}

## 6. 核心格样本

核心格：

```text
HighAIDisclosureIntensity = 1
NoCurrentAISupport = 1
```

样本量：

```text
{len(core_cell)}
```

前 30 个例子见：

```text
{OUT_DIR / "coarse_core_cell_examples.csv"}
```

## 7. 硬判断

这次粗 pilot 只能回答：

```text
firm-year 层面是否有“AI 披露强、当前 AI 投资支撑弱”的样本格
```

不能回答：

```text
具体 GenAI claim 是否有 current support
具体 GenAI claim 是否被未来硬证据兑现
specificity 是否在无支撑时失效
```

要真正跑 v8.3，还需要至少一个 claim-level 文本源：

1. 公告 / 年报 / IR / 互动易原文；
2. claim date；
3. GenAI-specific forward-looking claim 抽取；
4. current support 与 future realization 的 claim-type matching。

如果只有当前这两个年度表，最多只能做 firm-year AI disclosure-action gap，不能做 v8.3 主实验。
"""

    DOC_OUT.write_text(report, encoding="utf-8")

    print(f"sample_obs={len(sample)}")
    print(f"sample_firms={sample['Symbol'].nunique()}")
    print(f"core_cell_obs={len(core_cell)}")
    print(f"mda_share_threshold={threshold}")
    print(f"wrote={OUT_DIR}")
    print(f"report={DOC_OUT}")


if __name__ == "__main__":
    main()
