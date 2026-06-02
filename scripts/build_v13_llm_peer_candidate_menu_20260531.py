#!/usr/bin/env python3
"""Build a candidate menu for LLM-generated/re-ranked peer validation.

True LLM peers require a model/human to choose competitors from business
descriptions. This script prepares the auditable menu: for each focal firm, it
lists candidates drawn from existing literature-backed peer systems so an
external LLM can select the Top5 product-market peers without hallucinating stock
codes.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from run_v13_peer_validity_gate_20260531 import load_peer_systems
from run_v13_peer_manual_llm_gate_20260531 import load_text_maps, clean_text


ROOT = Path(__file__).resolve().parents[1]
LLM_DIR = ROOT / "data" / "peer_validity_llm_20260531"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "74_v13_llm_peer_candidate_menu_20260531.md"


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    digits = re.sub(r"\D", "", str(value))
    return digits.zfill(6) if digits else ""


def main() -> None:
    LLM_DIR.mkdir(parents=True, exist_ok=True)
    systems = load_peer_systems()
    texts = load_text_maps()
    focal_base = pd.read_csv(
        LLM_DIR / "llm_peer_request_template_200_20260531.csv", dtype={"focal_code": str}
    )[["focal_code", "short_name", "industry_d", "product_text"]]
    focal_base["focal_code"] = focal_base["focal_code"].map(code6)
    focal_set = set(focal_base["focal_code"])
    text_lookup = texts[["stock_code", "company_name", "industry_d", "scope_text"]].rename(
        columns={
            "stock_code": "focal_code",
            "company_name": "focal_name_from_text",
            "industry_d": "focal_industry_from_text",
            "scope_text": "focal_scope_from_text",
        }
    )
    focal_base = focal_base.merge(text_lookup, on="focal_code", how="left")
    for col in ["short_name", "industry_d", "product_text"]:
        focal_base[col] = focal_base[col].replace(r"^\s*$", pd.NA, regex=True)
    focal_base["short_name"] = focal_base["short_name"].fillna(focal_base["focal_name_from_text"])
    focal_base["industry_d"] = focal_base["industry_d"].fillna(focal_base["focal_industry_from_text"])
    focal_base["product_text"] = focal_base["product_text"].fillna(focal_base["focal_scope_from_text"])

    selected_systems = {
        "csmar_scope": systems["csmar_scope_top10"],
        "annual_same_industry": systems["annual_same_industry_2024_top10"],
        "annual_global_ai_stripped": systems["annual_global_ai_stripped_2024_top10"],
        "random_same_industry": systems["random_same_industry_top10"],
    }
    frames = []
    for source, df in selected_systems.items():
        sub = df[df["focal_code"].isin(focal_set)].copy()
        sub["candidate_source_system"] = source
        frames.append(sub)
    cand = pd.concat(frames, ignore_index=True)
    cand["peer_code"] = cand["peer_code"].map(code6)
    cand["focal_code"] = cand["focal_code"].map(code6)
    cand["source_rank"] = pd.to_numeric(cand["peer_rank"], errors="coerce")
    cand["product_similarity"] = pd.to_numeric(cand["product_similarity"], errors="coerce")
    source_order = {
        "annual_same_industry": 1,
        "csmar_scope": 2,
        "annual_global_ai_stripped": 3,
        "random_same_industry": 4,
    }
    cand["source_priority"] = cand["candidate_source_system"].map(source_order)
    cand = cand.sort_values(
        ["focal_code", "source_priority", "source_rank", "product_similarity"],
        ascending=[True, True, True, False],
    )
    cand = cand.drop_duplicates(["focal_code", "peer_code"], keep="first")

    peer_text = texts.rename(
        columns={
            "stock_code": "peer_code",
            "company_name": "peer_name_text",
            "industry_d": "peer_industry_d_text",
            "scope_text": "peer_scope_text",
            "annual_business_text": "peer_annual_text",
        }
    )
    cand = cand.merge(
        peer_text[
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
    cand["peer_name_final"] = cand["peer_name"].fillna(cand["peer_name_text"])
    cand["peer_industry_final"] = cand["peer_industry_d"].fillna(cand["peer_industry_d_text"])
    cand["peer_business_excerpt"] = cand["peer_scope_text"].fillna("").map(lambda x: clean_text(x, 220))
    cand = cand.drop(
        columns=[
            "focal_name",
            "focal_industry_d",
            "focal_industry_c",
            "focal_name_text",
            "focal_industry_d_text",
        ],
        errors="ignore",
    )

    menu = focal_base.rename(
        columns={
            "short_name": "focal_name",
            "industry_d": "focal_industry",
            "product_text": "focal_business_excerpt",
        }
    ).merge(cand, on="focal_code", how="left")
    menu["focal_business_excerpt"] = menu["focal_business_excerpt"].fillna("").map(
        lambda x: clean_text(x, 260)
    )
    menu = menu.sort_values(["focal_code", "source_priority", "source_rank"])
    menu["candidate_id_within_focal"] = menu.groupby("focal_code").cumcount() + 1
    out_cols = [
        "focal_code",
        "focal_name",
        "focal_industry",
        "focal_business_excerpt",
        "candidate_id_within_focal",
        "peer_code",
        "peer_name_final",
        "peer_industry_final",
        "candidate_source_system",
        "source_rank",
        "product_similarity",
        "peer_business_excerpt",
        "llm_selected_rank_1_to_5",
        "llm_is_direct_product_market_peer_0_1",
        "llm_reason",
    ]
    for col in out_cols:
        if col not in menu.columns:
            menu[col] = ""
    menu[out_cols].to_csv(LLM_DIR / "llm_peer_candidate_menu_200_20260531.csv", index=False)

    task = """# LLM Peer Re-Ranking Task

Input: `data/peer_validity_llm_20260531/llm_peer_candidate_menu_200_20260531.csv`

For each `focal_code`, review the candidate peer list. Select up to five direct
product-market peers from the candidates and fill:

- `llm_selected_rank_1_to_5`: 1 to 5 for selected peers, blank otherwise.
- `llm_is_direct_product_market_peer_0_1`: 1 if the candidate is a product-market
  competitor, 0 otherwise.
- `llm_reason`: one short reason.

Rules:
- Product-market peer means similar products/services sold to similar customers
  or use cases.
- Do not select supply-chain complements unless they directly compete in the end
  product market.
- Do not reward generic terms such as technology, platform, service, AI, digital,
  intelligent, or solution unless the product/customer overlap is concrete.
- Prefer candidates with observable product/customer overlap over candidates
  that merely share the same CSRC industry.

Output:
`data/peer_validity_llm_20260531/llm_peer_candidate_menu_coded_200_YYYYMMDD.csv`

After coding, the selected rows can be converted into an LLM-re-ranked peer
network and evaluated with the same return/fundamental gates.
"""
    (LLM_DIR / "LLM_PEER_RERANKING_TASK.md").write_text(task, encoding="utf-8")

    doc = f"""# v13 LLM Peer Candidate Menu

日期：2026-05-31

## Purpose

The current peer-validity gate has evaluated CSMAR scope peers, annual-report
text peers, and industry placebo peers. A strict LLM-generated peer system is not
yet available. This file makes that step executable without allowing the LLM to
hallucinate stock codes.

## Outputs

```text
data/peer_validity_llm_20260531/llm_peer_candidate_menu_200_20260531.csv
data/peer_validity_llm_20260531/LLM_PEER_RERANKING_TASK.md
```

## Candidate Sources

For each of 200 focal firms, candidates are drawn from:

```text
annual same-industry text Top10;
CSMAR business-scope text Top10;
annual global AI-word-stripped text Top10;
random same-industry Top10.
```

The intended LLM task is to re-rank/select Top5 direct product-market peers from
this candidate menu. The resulting selected rows can then be evaluated using the
same return-comovement and fundamentals-comovement scripts.

## Status

This prepares the LLM-peer construction gate. It is not yet a completed
LLM-generated peer network until the candidate menu is coded.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")
    print(
        {
            "focal_firms": int(menu["focal_code"].nunique()),
            "candidate_rows": int(len(menu)),
            "output": str(LLM_DIR / "llm_peer_candidate_menu_200_20260531.csv"),
        }
    )


if __name__ == "__main__":
    main()
