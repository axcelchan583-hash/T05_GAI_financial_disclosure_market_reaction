#!/usr/bin/env python3
"""Build and validate a code-safe LLM/semantic re-ranked peer network.

The candidate menu prevents hallucinated stock codes. The semantic re-ranker
selects Top5 peers from candidates using product/customer/use-case overlap,
then evaluates the resulting network with the same return and fundamentals gates
used for CSMAR, annual-report, and industry peer systems.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from run_v13_peer_codex_manual_coding_20260531 import score_pair
from run_v13_peer_validity_gate_20260531 import (
    OUT_DIR,
    WINDOWS,
    evaluate_system,
    load_peer_systems,
    load_returns,
)
from run_v13_peer_fundamental_validity_20260531 import load_financials


ROOT = Path(__file__).resolve().parents[1]
MENU = ROOT / "data" / "peer_validity_llm_20260531" / "llm_peer_candidate_menu_200_20260531.csv"
NETWORK = OUT_DIR / "llm_semantic_reranked_peer_network_top5_200.csv"
RET_SUMMARY = OUT_DIR / "llm_semantic_reranked_return_gate_200.csv"
FUND_SUMMARY = OUT_DIR / "llm_semantic_reranked_fundamental_gate_200.csv"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "76_v13_llm_reranked_peer_gate_20260531.md"


SOURCE_PRIORITY = {
    "annual_same_industry": 1,
    "csmar_scope": 2,
    "annual_global_ai_stripped": 3,
    "random_same_industry": 4,
}


def prepare_for_score(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["focal_name_final"] = out["focal_name"]
    out["focal_industry_final"] = out["focal_industry"]
    out["focal_scope_excerpt"] = out["focal_business_excerpt"]
    out["peer_scope_excerpt"] = out["peer_business_excerpt"]
    out["scope_text_jaccard"] = np.nan
    out["annual_text_jaccard"] = np.nan
    return out


def build_network() -> pd.DataFrame:
    menu = pd.read_csv(MENU, dtype={"focal_code": str, "peer_code": str})
    menu = prepare_for_score(menu)
    scores = menu.apply(score_pair, axis=1, result_type="expand")
    scores.columns = [
        "semantic_score_0_3",
        "semantic_direct_peer",
        "semantic_reason",
        "semantic_focal_categories",
        "semantic_peer_categories",
    ]
    scored = menu.join(scores)
    scored["source_priority"] = scored["candidate_source_system"].map(SOURCE_PRIORITY).fillna(9)
    scored["product_similarity"] = pd.to_numeric(scored["product_similarity"], errors="coerce").fillna(-1)
    scored["source_rank"] = pd.to_numeric(scored["source_rank"], errors="coerce").fillna(999)
    scored = scored.sort_values(
        [
            "focal_code",
            "semantic_score_0_3",
            "semantic_direct_peer",
            "source_priority",
            "product_similarity",
            "source_rank",
        ],
        ascending=[True, False, False, True, False, True],
    )
    selected = scored.groupby("focal_code", as_index=False, group_keys=False).head(5).copy()
    selected["peer_rank"] = selected.groupby("focal_code").cumcount() + 1
    selected["peer_source"] = "llm_semantic_reranked"
    selected["top_n"] = 5
    selected = selected.rename(
        columns={
            "focal_name": "focal_name",
            "focal_industry": "focal_industry_d",
            "peer_name_final": "peer_name",
            "peer_industry_final": "peer_industry_d",
        }
    )
    keep = [
        "peer_source",
        "top_n",
        "focal_code",
        "peer_code",
        "peer_rank",
        "product_similarity",
        "focal_name",
        "peer_name",
        "focal_industry_d",
        "peer_industry_d",
        "candidate_source_system",
        "semantic_score_0_3",
        "semantic_direct_peer",
        "semantic_reason",
        "semantic_focal_categories",
        "semantic_peer_categories",
    ]
    selected[keep].to_csv(NETWORK, index=False)
    return selected[keep]


def restrict_systems_to_focal(focal_codes: set[str]) -> dict[str, pd.DataFrame]:
    systems = load_peer_systems()
    wanted = [
        "csmar_scope_top5",
        "annual_same_industry_2024_top5",
        "annual_global_ai_stripped_2024_top5",
        "random_same_industry_top5",
        "low_similarity_same_industry_top5",
    ]
    out = {name: systems[name][systems[name]["focal_code"].isin(focal_codes)].copy() for name in wanted}
    return out


def return_gate(network: pd.DataFrame) -> pd.DataFrame:
    returns = load_returns()
    focal_codes = set(network["focal_code"])
    systems = restrict_systems_to_focal(focal_codes)
    systems["llm_semantic_reranked_top5"] = network.copy()
    rows = []
    for name, pairs in systems.items():
        # Use the same short window as the prior validation table; older window is
        # less relevant for a 2024 text/LLM peer system.
        fm, summary = evaluate_system(name, pairs, returns, "return_2025_2026")
        rows.append(summary)
    res = pd.DataFrame(rows).sort_values("mean_abret_corr", ascending=False)
    res.to_csv(RET_SUMMARY, index=False)
    return res


def corr_stat(x: pd.Series, y: pd.Series) -> tuple[float, float, int]:
    d = pd.concat([x, y], axis=1).dropna()
    if len(d) < 20 or d.iloc[:, 0].std() == 0 or d.iloc[:, 1].std() == 0:
        return math.nan, math.nan, int(len(d))
    r, p = stats.pearsonr(d.iloc[:, 0], d.iloc[:, 1])
    return float(r), float(p), int(len(d))


def evaluate_2025_fundamentals(name: str, pairs: pd.DataFrame, fin: pd.DataFrame) -> list[dict[str, object]]:
    f2025 = fin[fin["fiscal_year"].eq(2025)].copy()
    pair_year = pairs[["focal_code", "peer_code"]].drop_duplicates()
    peer = pair_year.merge(
        f2025.rename(columns={"stock_code": "peer_code"}),
        on="peer_code",
        how="left",
    )
    peer_port = (
        peer.groupby("focal_code", as_index=False)
        .agg(
            peer_sales_growth=("sales_growth", "mean"),
            peer_gross_margin=("gross_margin", "mean"),
            peer_obs=("sales_growth", "count"),
        )
    )
    focal = f2025.rename(
        columns={
            "stock_code": "focal_code",
            "sales_growth": "focal_sales_growth",
            "gross_margin": "focal_gross_margin",
        }
    )[["focal_code", "focal_sales_growth", "focal_gross_margin"]]
    panel = peer_port.merge(focal, on="focal_code", how="inner")
    panel = panel[panel["peer_obs"].ge(2)].copy()
    rows = []
    for metric, focal_col, peer_col in [
        ("sales_growth_2025", "focal_sales_growth", "peer_sales_growth"),
        ("gross_margin_2025", "focal_gross_margin", "peer_gross_margin"),
    ]:
        r, p, n = corr_stat(panel[focal_col], panel[peer_col])
        rows.append(
            {
                "peer_system": name,
                "metric": metric,
                "corr": r,
                "p": p,
                "n_focal": n,
                "focal_firms": panel["focal_code"].nunique(),
                "year": 2025,
            }
        )
    return rows


def fundamental_gate(network: pd.DataFrame) -> pd.DataFrame:
    focal_codes = set(network["focal_code"])
    systems = restrict_systems_to_focal(focal_codes)
    systems["llm_semantic_reranked_top5"] = network.copy()
    fin = load_financials()
    rows: list[dict[str, object]] = []
    for name, pairs in systems.items():
        rows.extend(evaluate_2025_fundamentals(name, pairs, fin))
    res = pd.DataFrame(rows)
    res.to_csv(FUND_SUMMARY, index=False)
    return res


def markdown_table(df: pd.DataFrame, cols: list[str], digits: int = 4) -> str:
    out = df[cols].copy()
    for col in out.select_dtypes(include=[np.number]).columns:
        out[col] = out[col].map(lambda x: round(float(x), digits) if pd.notna(x) else x)
    return out.to_markdown(index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    network = build_network()
    ret = return_gate(network)
    fund = fundamental_gate(network)
    network_summary = (
        network.groupby("candidate_source_system", as_index=False)
        .agg(
            selected_pairs=("peer_code", "size"),
            mean_rank=("peer_rank", "mean"),
            direct_share=("semantic_direct_peer", "mean"),
            mean_score=("semantic_score_0_3", "mean"),
        )
        .sort_values("selected_pairs", ascending=False)
    )
    doc = f"""# v13 LLM/Semantic Re-ranked Peer Gate

日期：2026-05-31

## Purpose

This file converts the LLM peer candidate menu into an actual code-safe
LLM/semantic re-ranked Top5 peer network and evaluates it using the same
return-comovement and fundamentals-comovement gates.

The network is "code-safe" because the LLM/semantic selection is restricted to a
candidate menu built from observable A-share peer systems. This follows the
spirit of LLM peer identification while avoiding hallucinated stock codes.

## Outputs

```text
{NETWORK.relative_to(ROOT)}
{RET_SUMMARY.relative_to(ROOT)}
{FUND_SUMMARY.relative_to(ROOT)}
```

## Selected Candidate Source Mix

{markdown_table(network_summary, ['candidate_source_system', 'selected_pairs', 'mean_rank', 'direct_share', 'mean_score'])}

## Return-Comovement Gate, Matched 200-Focal Sample, 2025-2026

{markdown_table(ret, ['peer_system', 'pair_count', 'focal_firms_with_returns', 'mean_abret_corr', 'median_abret_corr', 'mean_raw_corr', 'median_raw_corr'])}

## Fundamentals Gate, Matched 200-Focal Sample, 2025

{markdown_table(fund, ['peer_system', 'metric', 'corr', 'p', 'n_focal', 'focal_firms'])}

## Reading

This completes a first LLM/semantic peer-system pass. The resulting network is
not an unconstrained LLM peer list; it is an auditable LLM-style re-ranking from
literature-backed candidate systems.

The key comparison should be made on the matched 200-focal sample:

```text
If the LLM/semantic re-ranked network beats random and low-similarity systems on
return and fundamentals comovement, it passes the validity gate.

If it does not beat annual same-industry text peers, then annual-report text
peers remain the measurement-clean benchmark.
```
"""
    DOC_PATH.write_text(doc, encoding="utf-8")
    print("Return gate:")
    print(ret.to_string(index=False))
    print("\nFundamental gate:")
    print(fund.to_string(index=False))


if __name__ == "__main__":
    main()
