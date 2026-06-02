#!/usr/bin/env python3
"""Manual/LLM inspection gate for product-market peer definitions.

This script does not create the final peer variable. It prepares auditable
pair-level samples and a lightweight proxy score so we can decide whether each
peer-identification system is defensible before using it in the GenAI event
study.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

from run_v13_peer_validity_gate_20260531 import load_peer_systems


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "v13_peer_validity_gate_20260531"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "71_v13_peer_manual_llm_gate_20260531.md"
LLM_DIR = ROOT / "data" / "peer_validity_llm_20260531"

PRODUCT_TEXT = ROOT / "results" / "v4_peer_spillover_x_pilot" / "v4_company_product_text_latest.csv"
ANNUAL_TEXT = ROOT / "results" / "v12_annual_report_product_peers_20260530" / "annual_report_business_text_2021_2025.csv"

STOP_TERMS = {
    "公司",
    "业务",
    "产品",
    "服务",
    "主要",
    "经营",
    "销售",
    "生产",
    "研发",
    "制造",
    "提供",
    "客户",
    "市场",
    "行业",
    "相关",
    "技术",
    "管理",
    "发展",
    "平台",
    "系统",
    "解决",
    "方案",
    "综合",
    "国内",
    "国际",
    "企业",
    "投资",
    "控股",
    "贸易",
    "材料",
    "工程",
}


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = re.sub(r"\.0$", "", str(value).strip())
    digits = re.sub(r"\D", "", text)
    return digits.zfill(6) if digits else ""


def clean_text(value: object, max_len: int = 360) -> str:
    if pd.isna(value):
        return ""
    text = re.sub(r"\s+", "", str(value))
    text = re.sub(r"[，。；、,.；:：()\[\]【】（）]+", " ", text)
    return text[:max_len]


def char_ngrams(text: str, n_values: tuple[int, ...] = (2, 3)) -> set[str]:
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", text)
    grams: set[str] = set()
    for n in n_values:
        for i in range(max(len(text) - n + 1, 0)):
            gram = text[i : i + n]
            if len(gram) == n and gram not in STOP_TERMS:
                grams.add(gram)
    return grams


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return math.nan
    return len(a & b) / len(a | b)


def shared_terms(a: str, b: str, max_terms: int = 12) -> str:
    inter = sorted(char_ngrams(a) & char_ngrams(b), key=lambda x: (-len(x), x))
    # Remove grams that are pure generic fragments.
    inter = [x for x in inter if not any(stop in x for stop in STOP_TERMS)]
    return ";".join(inter[:max_terms])


def load_text_maps() -> pd.DataFrame:
    csmar = pd.read_csv(PRODUCT_TEXT, dtype={"stock_code": str})
    csmar["stock_code"] = csmar["stock_code"].map(code6)
    csmar = csmar.sort_values("info_year").drop_duplicates("stock_code", keep="last")
    csmar = csmar.rename(
        columns={
            "company_name": "company_name_csmar",
            "industry_d": "industry_d_csmar",
            "product_text": "scope_text",
        }
    )
    csmar = csmar[["stock_code", "company_name_csmar", "industry_d_csmar", "scope_text"]]

    annual = pd.read_csv(ANNUAL_TEXT, dtype={"stock_code": str})
    annual["stock_code"] = annual["stock_code"].map(code6)
    annual["report_year"] = pd.to_numeric(annual["report_year"], errors="coerce")
    annual = annual[annual["report_year"].eq(2024)].copy()
    annual = annual.drop_duplicates("stock_code")
    annual = annual.rename(
        columns={
            "company_name": "company_name_annual",
            "industry_d": "industry_d_annual",
            "business_text": "annual_business_text",
        }
    )
    annual = annual[
        ["stock_code", "company_name_annual", "industry_d_annual", "annual_business_text"]
    ]
    out = csmar.merge(annual, on="stock_code", how="outer")
    out["company_name"] = out["company_name_csmar"].fillna(out["company_name_annual"])
    out["industry_d"] = out["industry_d_csmar"].fillna(out["industry_d_annual"])
    out["scope_text"] = out["scope_text"].fillna("")
    out["annual_business_text"] = out["annual_business_text"].fillna("")
    return out.drop_duplicates("stock_code")


def attach_text(pairs: pd.DataFrame, texts: pd.DataFrame) -> pd.DataFrame:
    focal = texts.rename(
        columns={
            "stock_code": "focal_code",
            "company_name": "focal_name_text",
            "industry_d": "focal_industry_d_text",
            "scope_text": "focal_scope_text",
            "annual_business_text": "focal_annual_text",
        }
    )
    peer = texts.rename(
        columns={
            "stock_code": "peer_code",
            "company_name": "peer_name_text",
            "industry_d": "peer_industry_d_text",
            "scope_text": "peer_scope_text",
            "annual_business_text": "peer_annual_text",
        }
    )
    out = pairs.merge(
        focal[
            [
                "focal_code",
                "focal_name_text",
                "focal_industry_d_text",
                "focal_scope_text",
                "focal_annual_text",
            ]
        ],
        on="focal_code",
        how="left",
    )
    out = out.merge(
        peer[
            [
                "peer_code",
                "peer_name_text",
                "peer_industry_d_text",
                "peer_scope_text",
                "peer_annual_text",
            ]
        ],
        on="peer_code",
        how="left",
    )
    for side in ["focal", "peer"]:
        out[f"{side}_name_final"] = out[f"{side}_name"].fillna(out[f"{side}_name_text"])
        out[f"{side}_industry_final"] = out[f"{side}_industry_d"].fillna(
            out[f"{side}_industry_d_text"]
        )
    return out


def score_pairs(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in df.itertuples(index=False):
        focal_scope = clean_text(getattr(row, "focal_scope_text", ""))
        peer_scope = clean_text(getattr(row, "peer_scope_text", ""))
        focal_annual = clean_text(getattr(row, "focal_annual_text", ""))
        peer_annual = clean_text(getattr(row, "peer_annual_text", ""))
        scope_j = jaccard(char_ngrams(focal_scope), char_ngrams(peer_scope))
        annual_j = jaccard(char_ngrams(focal_annual), char_ngrams(peer_annual))
        same_industry = int(
            str(getattr(row, "focal_industry_final", "")) == str(getattr(row, "peer_industry_final", ""))
        )
        # Proxy only: designed to prioritize human/LLM review, not to replace it.
        proxy_score = 0
        proxy_score += 1 if same_industry else 0
        proxy_score += 1 if pd.notna(scope_j) and scope_j >= 0.055 else 0
        proxy_score += 1 if pd.notna(annual_j) and annual_j >= 0.035 else 0
        proxy_score += 1 if pd.to_numeric(getattr(row, "product_similarity", np.nan), errors="coerce") >= 0.18 else 0
        if proxy_score >= 3:
            label = "likely_direct_peer"
        elif proxy_score == 2:
            label = "possible_peer"
        else:
            label = "weak_or_needs_manual_review"
        r = row._asdict()
        r.update(
            {
                "same_industry_manual_proxy": same_industry,
                "scope_text_jaccard": scope_j,
                "annual_text_jaccard": annual_j,
                "shared_scope_terms": shared_terms(focal_scope, peer_scope),
                "shared_annual_terms": shared_terms(focal_annual, peer_annual),
                "manual_proxy_score_0_4": proxy_score,
                "manual_proxy_label": label,
                "focal_scope_excerpt": focal_scope,
                "peer_scope_excerpt": peer_scope,
                "focal_annual_excerpt": focal_annual,
                "peer_annual_excerpt": peer_annual,
            }
        )
        rows.append(r)
    return pd.DataFrame(rows)


def build_candidate_pairs() -> pd.DataFrame:
    systems = load_peer_systems()
    chosen = {
        "csmar_scope_top5": systems["csmar_scope_top5"],
        "annual_same_industry_2024_top5": systems["annual_same_industry_2024_top5"],
        "annual_global_ai_stripped_2024_top5": systems["annual_global_ai_stripped_2024_top5"],
        "random_same_industry_top5": systems["random_same_industry_top5"],
        "low_similarity_same_industry_top5": systems["low_similarity_same_industry_top5"],
    }
    frames = []
    for name, df in chosen.items():
        sub = df.copy()
        sub["peer_system"] = name
        frames.append(sub)
    pairs = pd.concat(frames, ignore_index=True)
    pairs["peer_rank"] = pd.to_numeric(pairs["peer_rank"], errors="coerce")
    pairs["product_similarity"] = pd.to_numeric(pairs["product_similarity"], errors="coerce")
    return pairs


def write_llm_validation_template(scored: pd.DataFrame) -> None:
    LLM_DIR.mkdir(parents=True, exist_ok=True)
    sample = (
        scored.sort_values(["focal_code", "peer_system", "peer_rank"])
        .groupby("peer_system", group_keys=False)
        .apply(lambda x: x.sample(min(30, len(x)), random_state=531))
        .reset_index(drop=True)
    )
    cols = [
        "focal_code",
        "focal_name_final",
        "focal_industry_final",
        "focal_scope_excerpt",
        "peer_system",
        "peer_rank",
        "peer_code",
        "peer_name_final",
        "peer_industry_final",
        "product_similarity",
        "peer_scope_excerpt",
        "scope_text_jaccard",
        "annual_text_jaccard",
        "shared_scope_terms",
        "human_competitor_score_0_to_3",
        "human_is_direct_product_market_peer_0_1",
        "human_reason",
    ]
    for col in cols:
        if col not in sample.columns:
            sample[col] = ""
    sample[cols].to_csv(
        LLM_DIR / "peer_system_validation_template_150_pairs_20260531.csv", index=False
    )
    task = """# Peer-System Validation Coding Task

Input: `data/peer_validity_llm_20260531/peer_system_validation_template_150_pairs_20260531.csv`

For each focal-peer pair, judge whether the peer is a direct product-market
competitor of the focal firm.

Score:
- 3 = close direct competitor: similar product/service and similar customer/use case.
- 2 = related product-market peer: same broad market, but products or customers differ.
- 1 = weakly related: same industry label or supply-chain relation, but not a direct competitor.
- 0 = not a product-market competitor.

Do not reward generic words such as "technology", "platform", "service", "digital",
"AI", or "intelligent" unless the actual products or customers overlap.

Fill:
- `human_competitor_score_0_to_3`
- `human_is_direct_product_market_peer_0_1` (1 if score is 2 or 3)
- `human_reason`

Output with the same rows:
`data/peer_validity_llm_20260531/peer_system_validation_coded_150_pairs_YYYYMMDD.csv`
"""
    (LLM_DIR / "LLM_PEER_SYSTEM_VALIDATION_TASK.md").write_text(task, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pairs = build_candidate_pairs()
    texts = load_text_maps()
    scored = score_pairs(attach_text(pairs, texts))

    scored_path = OUT_DIR / "peer_manual_proxy_pair_scores.csv"
    compact_cols = [
        "peer_system",
        "focal_code",
        "focal_name_final",
        "focal_industry_final",
        "peer_rank",
        "peer_code",
        "peer_name_final",
        "peer_industry_final",
        "product_similarity",
        "same_industry_manual_proxy",
        "scope_text_jaccard",
        "annual_text_jaccard",
        "manual_proxy_score_0_4",
        "manual_proxy_label",
        "shared_scope_terms",
        "shared_annual_terms",
    ]
    scored[compact_cols].to_csv(scored_path, index=False)

    summary = (
        scored.groupby("peer_system", as_index=False)
        .agg(
            pair_count=("peer_code", "size"),
            focal_firms=("focal_code", "nunique"),
            same_industry_share=("same_industry_manual_proxy", "mean"),
            mean_scope_jaccard=("scope_text_jaccard", "mean"),
            median_scope_jaccard=("scope_text_jaccard", "median"),
            mean_annual_jaccard=("annual_text_jaccard", "mean"),
            median_annual_jaccard=("annual_text_jaccard", "median"),
            likely_direct_share=(
                "manual_proxy_label",
                lambda s: float((s == "likely_direct_peer").mean()),
            ),
            weak_review_share=(
                "manual_proxy_label",
                lambda s: float((s == "weak_or_needs_manual_review").mean()),
            ),
        )
        .sort_values(["likely_direct_share", "mean_scope_jaccard"], ascending=False)
    )
    summary_path = OUT_DIR / "peer_manual_proxy_summary.csv"
    summary.to_csv(summary_path, index=False)
    write_llm_validation_template(scored)

    doc = f"""# v13 Peer Manual / LLM Gate

日期：2026-05-31

## Purpose

This is the third layer of the peer-validity gate:

```text
return comovement
+ operating-fundamental comovement
+ manual / LLM inspectability
```

It does not replace human coding. It prepares a pair-level validation file and a
transparent proxy score so that weak peer systems can be identified before the
paper relies on them.

## Outputs

```text
{scored_path.relative_to(ROOT)}
{summary_path.relative_to(ROOT)}
data/peer_validity_llm_20260531/peer_system_validation_template_150_pairs_20260531.csv
data/peer_validity_llm_20260531/LLM_PEER_SYSTEM_VALIDATION_TASK.md
```

## Proxy Scoring Rule

For each focal-peer pair, the proxy score adds one point for each item:

```text
same CSRC detailed industry;
CSMAR business-scope char n-gram Jaccard >= 0.055;
annual-report business-text char n-gram Jaccard >= 0.035;
source product-similarity score >= 0.18.
```

Labels:

```text
3-4 points: likely_direct_peer
2 points:   possible_peer
0-1 points: weak_or_needs_manual_review
```

This is a screening score only. The manuscript should cite the human/LLM-coded
validation file, not this proxy score, if formal manual validation is used.

## Summary

{summary.to_markdown(index=False, floatfmt=".4f")}

## Current Reading

- The CSMAR scope network remains inspectable: it has high same-industry coverage
  and a non-trivial share of likely direct peers under the proxy rule.
- Annual same-industry peers look strongest under the same-source inspection rule,
  consistent with the return/fundamental gates.
- Annual global AI-word-stripped peers are literature-cleaner than arbitrary
  global text matches, but they still contain cross-industry false positives that
  need manual review.
- Random and low-similarity same-industry peers remain useful placebo systems.

## Completion Status

Manual/LLM validation is not complete until
`peer_system_validation_template_150_pairs_20260531.csv` is independently coded.
The current file makes that coding feasible and auditable.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
