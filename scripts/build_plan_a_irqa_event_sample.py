#!/usr/bin/env python3
"""Build Plan A strict IR/interactive-QA GenAI communication event sample.

Plan A treats exchange interactive Q&A as firm communication events. The strict
sample keeps only records where the company's answer itself contains GenAI
terms. Investor questions are retained as controls/context, not as disclosure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_v3_genai_specificity_car_pilot import A_SHARE_PAT, specificity_metrics  # noqa: E402

IR_ROOT = Path(
    "/Users/mac/computerscience/第三方资料/04_项目专用资料/T05_GAI_financial_disclosure_market_reaction/ir_interaction_data_20260519"
)
QA_CSV = IR_ROOT / "interactive_platforms" / "interim" / "genai_interactive_qa_answered_combined_2023_2026.csv"

OUT_DIR = ROOT / "results" / "plan_a_irqa_multichannel_event_study"
DOC_OUT = ROOT / "docs" / "选题" / "21_plan_A_irqa_multichannel_event_study_20260522.md"

GENAI_TERMS = [
    "生成式人工智能",
    "生成式AI",
    "生成式 AI",
    "AIGC",
    "大模型",
    "AI大模型",
    "大语言模型",
    "语言大模型",
    "基础模型",
    "预训练模型",
    "多模态大模型",
    "ChatGPT",
    "GPT",
    "DeepSeek",
    "文心一言",
    "通义千问",
    "智谱",
    "智能体",
    "模型备案",
    "RAG",
    "Agent",
]
GENAI_PAT = re.compile("|".join(re.escape(t) for t in GENAI_TERMS), re.I)


def z6(x: object) -> str:
    return re.sub(r"\.0$", "", str(x)).strip().zfill(6)


def term_hits(text: object) -> str:
    s = str(text or "")
    hits = [t for t in GENAI_TERMS if re.search(re.escape(t), s, re.I)]
    return ";".join(sorted(set(hits)))


def has_genai(text: object) -> bool:
    return bool(GENAI_PAT.search(str(text or "")))


def split_terms(series: pd.Series) -> str:
    out: set[str] = set()
    for v in series.dropna().astype(str):
        for item in re.split(r"[;,；]", v):
            item = item.strip()
            if item:
                out.add(item)
    return ";".join(sorted(out))


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


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    qa = pd.read_csv(QA_CSV, dtype={"stock_code": str})
    qa["stock_code"] = qa["stock_code"].map(z6)
    qa = qa[qa["stock_code"].map(lambda x: bool(A_SHARE_PAT.match(str(x))))].copy()
    qa["answer_text"] = qa["answer_text"].fillna("").astype(str)
    qa["question_text"] = qa["question_text"].fillna("").astype(str)
    qa["answer_dt"] = pd.to_datetime(qa["answer_date"], errors="coerce")
    qa["question_dt"] = pd.to_datetime(qa["question_date"], errors="coerce")
    qa["event_date"] = pd.to_datetime(qa["event_date"], errors="coerce")
    qa["answer_has_genai"] = qa["answer_text"].map(has_genai)
    qa["question_has_genai"] = qa["question_text"].map(has_genai)
    qa["answer_matched_terms"] = qa["answer_text"].map(term_hits)
    qa["question_matched_terms"] = qa["question_text"].map(term_hits)
    qa["answer_after_close"] = qa["answer_dt"].dt.hour.ge(15).fillna(False)
    qa["answer_on_weekend"] = qa["answer_dt"].dt.dayofweek.ge(5).fillna(False)

    strict = qa[qa["answer_has_genai"]].copy()
    metric_rows = []
    for _, row in strict.iterrows():
        metric_rows.append(specificity_metrics(row["answer_text"]))
    metrics = pd.DataFrame(metric_rows, index=strict.index)
    strict = pd.concat([strict, metrics], axis=1)

    strict["event_date_str"] = strict["event_date"].dt.strftime("%Y-%m-%d")
    row_cols = [
        "platform",
        "source_id",
        "stock_code",
        "company_name",
        "event_date_str",
        "answer_date",
        "question_date",
        "answer_after_close",
        "answer_on_weekend",
        "answer_matched_terms",
        "question_matched_terms",
        "specificity",
        "specific_items",
        "genai_span_tokens",
        "genai_mentions",
        "question_text",
        "answer_text",
        "source_url",
    ]
    strict[row_cols].to_csv(OUT_DIR / "plan_a_irqa_strict_answer_level_events.csv", index=False, encoding="utf-8-sig")

    firm_day = (
        strict.groupby(["stock_code", "company_name", "event_date_str"], as_index=False)
        .agg(
            qa_count=("source_id", "nunique"),
            platform_count=("platform", "nunique"),
            platforms=("platform", lambda x: ";".join(sorted(set(map(str, x))))),
            answer_terms=("answer_matched_terms", split_terms),
            question_terms=("question_matched_terms", split_terms),
            max_specificity=("specificity", "max"),
            mean_specificity=("specificity", "mean"),
            total_specific_items=("specific_items", "sum"),
            total_answer_tokens=("genai_span_tokens", "sum"),
            total_genai_mentions=("genai_mentions", "sum"),
            any_after_close=("answer_after_close", "max"),
            any_weekend_answer=("answer_on_weekend", "max"),
            first_answer_time=("answer_dt", "min"),
            sample_answer=("answer_text", lambda x: " || ".join(str(v)[:260] for v in x.head(3))),
            sample_question=("question_text", lambda x: " || ".join(str(v)[:180] for v in x.head(3))),
        )
        .sort_values(["event_date_str", "stock_code"])
    )
    firm_day["hope_style_specificity_proxy"] = 100 * firm_day["total_specific_items"] / firm_day["total_answer_tokens"].clip(lower=1)
    firm_day.to_csv(OUT_DIR / "plan_a_irqa_strict_firm_day_events.csv", index=False, encoding="utf-8-sig")

    source_stats = (
        strict.groupby("platform", as_index=False)
        .agg(
            answer_level_events=("source_id", "nunique"),
            firm_day_events=("event_date_str", lambda x: strict.loc[x.index, ["stock_code", "event_date_str"]].drop_duplicates().shape[0]),
            firms=("stock_code", "nunique"),
            mean_specificity=("specificity", "mean"),
        )
    )
    date_stats = (
        firm_day.assign(month=lambda d: d["event_date_str"].str.slice(0, 7))
        .groupby("month", as_index=False)
        .agg(firm_day_events=("stock_code", "size"), firms=("stock_code", "nunique"))
    )
    top_firms = (
        firm_day.groupby(["stock_code", "company_name"], as_index=False)
        .size()
        .rename(columns={"size": "firm_day_events"})
        .sort_values("firm_day_events", ascending=False)
        .head(25)
    )
    source_stats.to_csv(OUT_DIR / "plan_a_irqa_source_stats.csv", index=False, encoding="utf-8-sig")
    date_stats.to_csv(OUT_DIR / "plan_a_irqa_monthly_stats.csv", index=False, encoding="utf-8-sig")
    top_firms.to_csv(OUT_DIR / "plan_a_irqa_top_firms.csv", index=False, encoding="utf-8-sig")

    qa["event_date_str"] = qa["event_date"].dt.strftime("%Y-%m-%d")
    all_answered_firm_days = qa.drop_duplicates(["stock_code", "event_date_str"]).shape[0]
    report = f"""# Plan A：IR/互动问答 GenAI 沟通事件研究

日期：2026-05-22

## 1. 能不能做

可以做，但主样本口径必须严格定义为：

```text
公司在交易所互动平台的回复文本本身包含 GenAI 相关内容。
投资者问题只作为语境或关注度控制，不直接视为公司披露。
```

现有互动问答数据中，A 股已回复记录共有 `{len(qa)}` 条，约 `{all_answered_firm_days}` 个公司-日期。若只保留公司回复文本本身含 GenAI 关键词的严格样本，剩余：

| 层级 | 数量 |
|---|---:|
| answer-level events | {len(strict)} |
| firm-day events | {len(firm_day)} |
| firms | {firm_day["stock_code"].nunique()} |

这已经达到“几百个样本”的最低要求。

## 2. 数据源分布

{table(source_stats)}

## 3. 月度分布

{table(date_stats, max_rows=40)}

## 4. 事件最多的公司

{table(top_firms)}

## 5. 具体怎么做

### 5.1 样本单位

主样本建议使用 `firm-day`，不是单条问答。

原因：同一公司同一天可能连续回复多条 GenAI 问题，市场反应无法分辨每条问答的独立效应。

```text
unit = firm i × reply date t
```

### 5.2 主 X

主 X 使用公司回复文本的 Hope-style specificity：

```text
Specificity_it = concrete details in company answer / answer text length
```

当前脚本中的 `hope_style_specificity_proxy` 是规则化试跑版。正式版应替换为中文 NER：

- 组织名；
- 产品 / 模型 / 平台名；
- 时间；
- 金额；
- 百分比；
- 数量；
- 合作方；
- 备案号 / 合同 / 项目名称。

### 5.3 主 Y

主 Y：

```text
|CAR[-1,+1]| 或 ABVOL[-1,+1]
```

事件日应按公司回复发布时间处理：

- 15:00 前回复：当天为事件日；
- 15:00 后回复：下一交易日为事件日；
- 周末 / 节假日回复：下一交易日为事件日。

### 5.4 基准模型

```text
|CAR|_it = β Specificity_it
            + Controls
            + Firm FE / Industry FE
            + Date FE or Month FE
            + ε_it
```

更建议的主表：

```text
|CAR|_it = β1 Specificity_it
            + β2 PriorAICapability_i
            + β3 Specificity_it × PriorAICapability_i
            + Controls
            + FE
            + ε
```

### 5.5 必要控制

- question specificity 或 question length；
- 是否投资者问题中已含 GenAI 词；
- 回复长度；
- 同日问答数量；
- 是否盘后回复；
- 公司规模、BM、ROA、换手率、历史波动；
- 行业 × 日期 / 日期固定效应；
- 同日重大公告过滤。

## 6. 当前最大数据缺口

当前 CSMAR 日收益只到 `2026-02-13`，而互动问答严格样本集中在 2026-02-19 到 2026-05-19。

公开行情接口已验证可以抓取深市个股 2026 年 2 月后的日行情，但正式版本仍建议：

1. 优先补 CSMAR / Wind / RESSET 的统一日收益；
2. 若只做 pilot，可用东方财富公开日 K 线补 2026-02-14 之后的个股收益；
3. 市场收益也要同步补齐，不能只补个股。

## 7. 风险判断

Plan A 可以做，但论文题目要改得更准确：

```text
中国上市公司 GenAI 互动沟通的信息含量
```

不要再写成“正式公告的信息含量”。互动问答的制度含义是：

- 公司公开回复；
- 交易所平台留痕；
- 投资者可观察；
- 但由投资者问题触发，不是完全自愿公告。

因此它的理论应落在“投资者问询触发的信息披露 / 互动平台沟通 / 信息不对称缓解”，而不是传统公告事件。
"""
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOC_OUT.write_text(report, encoding="utf-8")
    print(f"strict_answer_events={len(strict)} firm_day_events={len(firm_day)} firms={firm_day['stock_code'].nunique()}")
    print(f"sample={OUT_DIR / 'plan_a_irqa_strict_firm_day_events.csv'}")
    print(f"report={DOC_OUT}")


if __name__ == "__main__":
    main()
