#!/usr/bin/env python3
"""Build the v4 peer-spillover X pilot sample.

This pilot builds only the explanatory-side sample:

    focal GenAI communication event i,t x product-market peer j

It joins event-level GenAI specificity from the strict IR/interactive QA sample
with text-based product-market similarity from CSMAR company business text.
It does not compute peer CAR yet.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


ROOT = Path(__file__).resolve().parents[1]

EVENT_PATH = (
    ROOT
    / "results"
    / "plan_a_irqa_multichannel_event_study"
    / "plan_a_irqa_strict_firm_day_events.csv"
)

COMPANY_INFO_PATH = Path(
    "/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/"
    "上市公司财务信息/STK_LISTEDCOINFOANL.xlsx"
)

OUT_DIR = ROOT / "results" / "v4_peer_spillover_x_pilot"
DOC_PATH = ROOT / "docs" / "选题" / "23_v4_x_peer_similarity_pilot_20260522.md"


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = re.sub(r"\.0$", "", text)
    text = re.sub(r"\D", "", text)
    return text.zfill(6) if text else ""


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    text = text.replace("\r", "\n")
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9%％（）()、，。；;：:＋+./-]", "", text)
    return text


def read_events() -> pd.DataFrame:
    events = pd.read_csv(EVENT_PATH)
    events["focal_code"] = events["stock_code"].map(code6)
    events["event_date"] = pd.to_datetime(events["event_date_str"], errors="coerce")
    events["event_year"] = events["event_date"].dt.year
    events["specificity"] = pd.to_numeric(events["hope_style_specificity_proxy"], errors="coerce")
    events = events[events["focal_code"].ne("") & events["event_date"].notna()].copy()
    events = events.sort_values(["event_date", "focal_code"]).reset_index(drop=True)
    events["event_id"] = [
        f"E{idx + 1:04d}_{row.focal_code}_{row.event_date:%Y%m%d}"
        for idx, row in events.iterrows()
    ]
    return events


def read_company_text() -> pd.DataFrame:
    raw = pd.read_excel(COMPANY_INFO_PATH, dtype=str)
    raw = raw[~raw["Symbol"].isin(["股票代码", "没有单位"])].copy()
    raw["stock_code"] = raw["Symbol"].map(code6)
    raw["info_date"] = pd.to_datetime(raw["EndDate"], errors="coerce")
    raw["info_year"] = raw["info_date"].dt.year
    raw = raw[raw["stock_code"].ne("") & raw["info_year"].notna()].copy()
    raw["business_scope_clean"] = raw["BusinessScope"].map(clean_text)
    raw["main_business_clean"] = raw["MAINBUSSINESS"].map(clean_text)
    raw["industry_c"] = raw["IndustryNameC"].fillna("")
    raw["industry_d"] = raw["IndustryNameD"].fillna("")
    raw["company_name"] = raw["ShortName"].fillna("")
    raw["product_text"] = (
        raw["main_business_clean"].fillna("")
        + "。"
        + raw["business_scope_clean"].fillna("")
    )
    raw["text_len"] = raw["product_text"].str.len()
    raw = raw[raw["text_len"] >= 20].copy()

    latest = (
        raw.sort_values(["stock_code", "info_year"])
        .groupby("stock_code", as_index=False)
        .tail(1)
        .copy()
    )
    return latest[
        [
            "stock_code",
            "company_name",
            "info_year",
            "industry_c",
            "industry_d",
            "product_text",
            "text_len",
        ]
    ].reset_index(drop=True)


def build_similarity(
    events: pd.DataFrame,
    companies: pd.DataFrame,
    top_n: int = 10,
    restrict_same_industry_d: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    focal_codes = sorted(set(events["focal_code"]))
    focal_companies = companies[companies["stock_code"].isin(focal_codes)].copy()

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 4),
        min_df=2,
        max_df=0.85,
        max_features=50000,
        sublinear_tf=True,
        norm="l2",
    )
    matrix = vectorizer.fit_transform(companies["product_text"])
    matrix = normalize(matrix, norm="l2", copy=False)

    code_to_idx = {code: idx for idx, code in enumerate(companies["stock_code"])}
    rows: list[dict[str, object]] = []

    for focal_code in focal_codes:
        if focal_code not in code_to_idx:
            continue
        focal_idx = code_to_idx[focal_code]
        sims = (matrix[focal_idx] @ matrix.T).toarray().ravel()
        sims[focal_idx] = -np.inf

        if not np.isfinite(sims).any():
            continue

        focal_row = companies.iloc[focal_idx]
        candidate_pool = np.ones(len(sims), dtype=bool)
        candidate_pool[focal_idx] = False
        if restrict_same_industry_d and str(focal_row["industry_d"]).strip():
            candidate_pool &= companies["industry_d"].eq(focal_row["industry_d"]).to_numpy()

        candidate_indices = np.where(candidate_pool)[0]
        if len(candidate_indices) == 0:
            continue

        pool_sims = sims[candidate_indices]
        keep = min(top_n, len(candidate_indices))
        local_top = np.argpartition(-pool_sims, range(keep))[:keep]
        candidate_idx = candidate_indices[local_top]
        candidate_idx = candidate_idx[np.argsort(-sims[candidate_idx])]

        for rank, peer_idx in enumerate(candidate_idx, start=1):
            peer_row = companies.iloc[int(peer_idx)]
            sim = float(sims[int(peer_idx)])
            if not math.isfinite(sim):
                continue
            rows.append(
                {
                    "focal_code": focal_code,
                    "focal_name": focal_row["company_name"],
                    "focal_info_year": int(focal_row["info_year"]),
                    "focal_industry_c": focal_row["industry_c"],
                    "focal_industry_d": focal_row["industry_d"],
                    "peer_rank": rank,
                    "peer_code": peer_row["stock_code"],
                    "peer_name": peer_row["company_name"],
                    "peer_info_year": int(peer_row["info_year"]),
                    "peer_industry_c": peer_row["industry_c"],
                    "peer_industry_d": peer_row["industry_d"],
                    "product_similarity": sim,
                    "same_industry_c": int(focal_row["industry_c"] == peer_row["industry_c"]),
                    "same_industry_d": int(focal_row["industry_d"] == peer_row["industry_d"]),
                }
            )

    peer_network = pd.DataFrame(rows)
    peer_events = events.merge(peer_network, on="focal_code", how="inner")
    peer_events["x_specificity_similarity"] = (
        peer_events["specificity"] * peer_events["product_similarity"]
    )
    return peer_network, peer_events


def write_report(events: pd.DataFrame, companies: pd.DataFrame, peer_network: pd.DataFrame, peer_events: pd.DataFrame) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    matched_focal_events = peer_events["event_id"].nunique()
    matched_focal_firms = peer_events["focal_code"].nunique()
    event_count = len(events)
    focal_firms = events["focal_code"].nunique()

    sim_stats = peer_network["product_similarity"].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])
    x_stats = peer_events["x_specificity_similarity"].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])
    same_d = peer_network["same_industry_d"].mean()

    top_focals = (
        peer_events.groupby(["focal_code", "focal_name"], as_index=False)
        .agg(
            event_days=("event_id", "nunique"),
            peer_event_obs=("peer_code", "count"),
            mean_specificity=("specificity", "mean"),
            mean_similarity=("product_similarity", "mean"),
        )
        .sort_values(["event_days", "peer_event_obs"], ascending=False)
        .head(20)
    )

    examples = peer_network[peer_network["focal_code"].isin(top_focals["focal_code"].head(8))].copy()
    examples = examples[examples["peer_rank"] <= 5].copy()

    report = f"""# v4 X 试跑：GenAI 具体性 × 产品市场相似度

日期：2026-05-22

## 1. 这次跑了什么

本次只跑 v4 的解释变量侧，不跑 CAR：

```text
X_ijt = Specificity_it × ProductSimilarity_ij
```

其中：

- `Specificity_it` 来自 Plan A 严格互动平台 firm-day 样本；
- `ProductSimilarity_ij` 用国泰安 `STK_LISTEDCOINFOANL.xlsx` 中 2024 年或最新年份的 `MAINBUSSINESS + BusinessScope` 文本构造；
- 文本相似度用中文字符 2-4 gram TF-IDF cosine；
- 主口径在同 `IndustryNameD` 内取 Top 10 产品市场相似 peer。

注意：这还是 pilot。正式版最好改成年报业务章节文本，而不是公司基本资料里的经营范围 / 主营业务。

## 2. 样本覆盖

| item | value |
|---|---:|
| strict GenAI firm-day events | {event_count} |
| focal firms in event sample | {focal_firms} |
| companies with usable product text | {len(companies)} |
| events matched to peer network | {matched_focal_events} |
| focal firms matched to peer network | {matched_focal_firms} |
| peer-event X observations | {len(peer_events)} |
| unique focal-peer links | {len(peer_network)} |

## 3. 相似度分布

| stat | product_similarity |
|---|---:|
| mean | {sim_stats['mean']:.4f} |
| std | {sim_stats['std']:.4f} |
| p10 | {sim_stats['10%']:.4f} |
| p25 | {sim_stats['25%']:.4f} |
| p50 | {sim_stats['50%']:.4f} |
| p75 | {sim_stats['75%']:.4f} |
| p90 | {sim_stats['90%']:.4f} |
| min | {sim_stats['min']:.4f} |
| max | {sim_stats['max']:.4f} |

同业一致性：

| item | value |
|---|---:|
| Top10 peer same IndustryNameD share | {same_d:.3f} |

## 4. X 分布

| stat | Specificity × ProductSimilarity |
|---|---:|
| mean | {x_stats['mean']:.4f} |
| std | {x_stats['std']:.4f} |
| p10 | {x_stats['10%']:.4f} |
| p25 | {x_stats['25%']:.4f} |
| p50 | {x_stats['50%']:.4f} |
| p75 | {x_stats['75%']:.4f} |
| p90 | {x_stats['90%']:.4f} |
| min | {x_stats['min']:.4f} |
| max | {x_stats['max']:.4f} |

## 5. 事件最多的披露公司

{top_focals.to_markdown(index=False)}

## 6. Top 5 peer 抽查

{examples[['focal_code','focal_name','focal_industry_c','peer_rank','peer_code','peer_name','peer_industry_c','product_similarity','same_industry_c']].to_markdown(index=False)}

## 7. 判断

这次 X 跑通了：严格互动平台事件可以和产品市场 peer 网络连接，形成几千个 `event × peer` 层面的解释变量观测。

但目前的 peer 网络只是可行性版本，有两个风险：

1. `BusinessScope` 容易包含过宽的经营范围，可能把相似度做得偏泛；
2. 字符 n-gram TF-IDF 能抓住产品词接近，但没有语义理解。

下一步不应立刻解释经济结果，而应先做人工抽查和更严格 peer network：

```text
第一优先：抽查 Top 10 peer 是否真像竞品。
第二优先：用年报业务章节替换 BusinessScope / MAINBUSSINESS。
第三优先：补收益后再跑 PeerCAR。
```

## 8. 输出文件

- `results/v4_peer_spillover_x_pilot/v4_focal_peer_network_same_industry_d_top10.csv`
- `results/v4_peer_spillover_x_pilot/v4_peer_event_x_same_industry_d_top10.csv`
- `results/v4_peer_spillover_x_pilot/v4_focal_peer_top5_same_industry_d_audit.csv`
- `results/v4_peer_spillover_x_pilot/v4_focal_peer_network_global_top10.csv`
"""
    DOC_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    events = read_events()
    companies = read_company_text()
    peer_network, peer_events = build_similarity(
        events, companies, top_n=10, restrict_same_industry_d=True
    )
    global_peer_network, global_peer_events = build_similarity(
        events, companies, top_n=10, restrict_same_industry_d=False
    )

    peer_network.to_csv(
        OUT_DIR / "v4_focal_peer_network_same_industry_d_top10.csv",
        index=False,
        encoding="utf-8-sig",
    )
    peer_events.to_csv(
        OUT_DIR / "v4_peer_event_x_same_industry_d_top10.csv",
        index=False,
        encoding="utf-8-sig",
    )
    (
        peer_network[peer_network["peer_rank"] <= 5]
        .sort_values(["focal_code", "peer_rank"])
        .to_csv(
            OUT_DIR / "v4_focal_peer_top5_same_industry_d_audit.csv",
            index=False,
            encoding="utf-8-sig",
        )
    )
    global_peer_network.to_csv(
        OUT_DIR / "v4_focal_peer_network_global_top10.csv",
        index=False,
        encoding="utf-8-sig",
    )
    global_peer_events.to_csv(
        OUT_DIR / "v4_peer_event_x_global_top10.csv",
        index=False,
        encoding="utf-8-sig",
    )
    companies.to_csv(OUT_DIR / "v4_company_product_text_latest.csv", index=False, encoding="utf-8-sig")
    write_report(events, companies, peer_network, peer_events)

    print(f"events: {len(events)}")
    print(f"focal firms: {events['focal_code'].nunique()}")
    print(f"companies with product text: {len(companies)}")
    print(f"peer links: {len(peer_network)}")
    print(f"peer-event X observations: {len(peer_events)}")
    print(f"global peer links: {len(global_peer_network)}")
    print(f"global peer-event X observations: {len(global_peer_events)}")
    print(f"matched events: {peer_events['event_id'].nunique()}")
    print(f"matched focal firms: {peer_events['focal_code'].nunique()}")
    print(f"wrote: {OUT_DIR}")
    print(f"wrote: {DOC_PATH}")


if __name__ == "__main__":
    main()
