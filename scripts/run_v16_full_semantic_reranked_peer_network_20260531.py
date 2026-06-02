#!/usr/bin/env python3
"""Build and test a full-sample semantic re-ranked peer network.

This expands the v13 200-focal "LLM/semantic" peer gate to all focal firms that
appear in the current event library. The construction is code-safe: candidates
come from auditable peer systems, then a deterministic semantic product/category
scorer re-ranks them into Top5/Top10 peers.

The goal is diagnostic. If this cleaner semantic peer network cannot reproduce
the current PeerCAR result under external AIActive, the paper should not pretend
that the result is robust to a literature-clean peer definition.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from run_v13_peer_codex_manual_coding_20260531 import score_pair
from run_v13_peer_manual_llm_gate_20260531 import clean_text, load_text_maps
from run_v13_peer_validity_gate_20260531 import load_peer_systems
from run_v15_alternative_peer_definitions_20260531 import (
    attach_ai_flags,
    attach_returns,
    format_table,
    load_event_base,
    run_model,
    source_summary,
)
from run_v6_announcement_clean_checks_20260524 import (
    ROOT,
    attach_announcement_flags,
    build_announcement_stock_day_flags,
)
from run_v6_identification_strengthening_checks_20260524 import (
    build_return_lookup,
    load_stock_model,
)


OUT_DIR = ROOT / "results" / "v16_full_semantic_reranked_peers_20260531"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "79_v16_full_semantic_reranked_peers_20260531.md"

SOURCE_PRIORITY = {
    "annual_same_industry": 1,
    "csmar_scope": 2,
    "annual_global_ai_stripped": 3,
    "random_same_industry": 4,
}


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    digits = re.sub(r"\D", "", str(value))
    return digits.zfill(6) if digits else ""


def build_candidate_menu() -> pd.DataFrame:
    """Create all candidate focal-peer rows before semantic re-ranking."""
    systems = load_peer_systems()
    event_focals = load_event_base()[["focal_code"]].drop_duplicates()
    focal_set = set(event_focals["focal_code"].map(code6))
    selected_systems = {
        "annual_same_industry": systems["annual_same_industry_2024_top10"],
        "csmar_scope": systems["csmar_scope_top10"],
        "annual_global_ai_stripped": systems["annual_global_ai_stripped_2024_top10"],
        "random_same_industry": systems["random_same_industry_top10"],
    }

    frames = []
    for source, df in selected_systems.items():
        sub = df[df["focal_code"].isin(focal_set)].copy()
        sub["candidate_source_system"] = source
        sub["source_rank"] = pd.to_numeric(sub["peer_rank"], errors="coerce")
        sub["source_priority"] = SOURCE_PRIORITY[source]
        frames.append(sub)
    cand = pd.concat(frames, ignore_index=True)
    cand["focal_code"] = cand["focal_code"].map(code6)
    cand["peer_code"] = cand["peer_code"].map(code6)
    cand["product_similarity"] = pd.to_numeric(cand["product_similarity"], errors="coerce")
    cand = cand[cand["focal_code"].ne("") & cand["peer_code"].ne("")]
    cand = cand[cand["focal_code"].ne(cand["peer_code"])].copy()
    cand = cand.sort_values(
        ["focal_code", "source_priority", "source_rank", "product_similarity"],
        ascending=[True, True, True, False],
    )
    cand = cand.drop_duplicates(["focal_code", "peer_code"], keep="first")

    texts = load_text_maps()
    focal_text = texts.rename(
        columns={
            "stock_code": "focal_code",
            "company_name": "focal_name_text",
            "industry_d": "focal_industry_text",
            "scope_text": "focal_scope_text",
        }
    )[["focal_code", "focal_name_text", "focal_industry_text", "focal_scope_text"]]
    peer_text = texts.rename(
        columns={
            "stock_code": "peer_code",
            "company_name": "peer_name_text",
            "industry_d": "peer_industry_text",
            "scope_text": "peer_scope_text",
        }
    )[["peer_code", "peer_name_text", "peer_industry_text", "peer_scope_text"]]
    cand = cand.merge(focal_text, on="focal_code", how="left")
    cand = cand.merge(peer_text, on="peer_code", how="left")

    cand["focal_name_final"] = cand["focal_name"].fillna(cand["focal_name_text"])
    cand["peer_name_final"] = cand["peer_name"].fillna(cand["peer_name_text"])
    cand["focal_industry_final"] = cand["focal_industry_d"].fillna(cand["focal_industry_text"])
    cand["peer_industry_final"] = cand["peer_industry_d"].fillna(cand["peer_industry_text"])
    cand["focal_scope_excerpt"] = cand["focal_scope_text"].fillna("").map(lambda x: clean_text(x, 260))
    cand["peer_scope_excerpt"] = cand["peer_scope_text"].fillna("").map(lambda x: clean_text(x, 220))
    # Match the v13 200-focal semantic re-ranker: scoring is based on semantic
    # product categories and source similarity, not extra Jaccard features.
    cand["scope_text_jaccard"] = np.nan
    cand["annual_text_jaccard"] = np.nan
    return cand


def build_semantic_network() -> tuple[pd.DataFrame, pd.DataFrame]:
    cache_network = OUT_DIR / "full_semantic_reranked_peer_network_top10.csv"
    cache_scored = OUT_DIR / "full_semantic_candidate_scores.csv.gz"
    if cache_network.exists() and cache_scored.exists():
        network = pd.read_csv(cache_network, dtype={"focal_code": str, "peer_code": str})
        scored = pd.read_csv(cache_scored, dtype={"focal_code": str, "peer_code": str})
        return network, scored

    cand = build_candidate_menu()
    scores = cand.apply(score_pair, axis=1, result_type="expand")
    scores.columns = [
        "semantic_score_0_3",
        "semantic_direct_peer",
        "semantic_reason",
        "semantic_focal_categories",
        "semantic_peer_categories",
    ]
    scored = cand.join(scores)
    scored["semantic_score_0_3"] = pd.to_numeric(scored["semantic_score_0_3"], errors="coerce").fillna(0)
    scored["semantic_direct_peer"] = pd.to_numeric(scored["semantic_direct_peer"], errors="coerce").fillna(0)
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
    selected = scored.groupby("focal_code", as_index=False, group_keys=False).head(10).copy()
    selected["peer_rank"] = selected.groupby("focal_code").cumcount() + 1
    selected["peer_source"] = "full_semantic_reranked"
    selected["top_n"] = 10
    # Candidate systems already carry focal/peer names and industries. Drop
    # those raw columns before renaming the semantically cleaned fields, or
    # pandas will retain duplicate labels in memory.
    selected = selected.drop(
        columns=["focal_name", "peer_name", "focal_industry_d", "peer_industry_d"],
        errors="ignore",
    )
    selected = selected.rename(
        columns={
            "focal_name_final": "focal_name",
            "peer_name_final": "peer_name",
            "focal_industry_final": "focal_industry_d",
            "peer_industry_final": "peer_industry_d",
            "product_similarity": "peer_similarity",
        }
    )
    keep = [
        "peer_source",
        "top_n",
        "focal_code",
        "peer_code",
        "peer_rank",
        "peer_similarity",
        "focal_name",
        "peer_name",
        "focal_industry_d",
        "peer_industry_d",
        "candidate_source_system",
        "source_rank",
        "source_priority",
        "semantic_score_0_3",
        "semantic_direct_peer",
        "semantic_reason",
        "semantic_focal_categories",
        "semantic_peer_categories",
    ]
    network = selected[keep].copy()
    scored.to_csv(cache_scored, index=False, compression="gzip")
    network.to_csv(cache_network, index=False)
    return network, scored


def build_event_peer_panel(network: pd.DataFrame) -> pd.DataFrame:
    ev = load_event_base()
    d = ev.merge(network, on="focal_code", how="inner")
    d = d[d["peer_code"].ne(d["focal_code"])].copy()
    d["peer_industry_d"] = d["peer_industry_d"].fillna("UNKNOWN").astype(str)
    d["event_week"] = pd.to_datetime(d["date_0"], errors="coerce").dt.strftime("%Y-%U")
    d["peer_industry_week"] = d["peer_industry_d"] + "|" + d["event_week"].fillna("")
    return d


def source_mix(network: pd.DataFrame) -> pd.DataFrame:
    return (
        network.groupby("candidate_source_system", as_index=False)
        .agg(
            selected_pairs=("peer_code", "size"),
            mean_rank=("peer_rank", "mean"),
            direct_share=("semantic_direct_peer", "mean"),
            mean_score=("semantic_score_0_3", "mean"),
            mean_similarity=("peer_similarity", "mean"),
        )
        .sort_values("selected_pairs", ascending=False)
    )


def candidate_summary(scored: pd.DataFrame) -> pd.DataFrame:
    return (
        scored.groupby("candidate_source_system", as_index=False)
        .agg(
            candidate_rows=("peer_code", "size"),
            focal_firms=("focal_code", "nunique"),
            mean_score=("semantic_score_0_3", "mean"),
            direct_share=("semantic_direct_peer", "mean"),
            mean_similarity=("product_similarity", "mean"),
        )
        .sort_values("candidate_rows", ascending=False)
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Building full semantic peer network...", flush=True)
    network, scored = build_semantic_network()
    network.to_csv(OUT_DIR / "full_semantic_reranked_peer_network_top10.csv", index=False)

    print("Building event-peer panel and returns...", flush=True)
    lookup = build_return_lookup(load_stock_model())
    ann_flags = build_announcement_stock_day_flags()
    panel = build_event_peer_panel(network)
    panel = attach_returns(panel, lookup)
    panel = attach_announcement_flags(panel, ann_flags)
    panel = attach_ai_flags(panel)
    panel.to_csv(OUT_DIR / "full_semantic_reranked_event_peer_panel.csv.gz", index=False, compression="gzip")

    summaries = pd.DataFrame([source_summary(panel, "full_semantic_reranked")])
    cand_summary = candidate_summary(scored)
    mix = source_mix(network)
    regs = []
    for top_n in [3, 5, 10]:
        for ai_def in ["ext_any", "current_text_history", "ext_no_hiring", "ext_plus_history"]:
            regs.append(run_model(panel, ai_def, "full_semantic_reranked", top_n))
    res = pd.DataFrame(regs)

    summaries.to_csv(OUT_DIR / "full_semantic_coverage_summary.csv", index=False)
    cand_summary.to_csv(OUT_DIR / "full_semantic_candidate_source_summary.csv", index=False)
    mix.to_csv(OUT_DIR / "full_semantic_selected_source_mix.csv", index=False)
    res.to_csv(OUT_DIR / "full_semantic_main_effects.csv", index=False)

    doc = f"""# v16 Full-Sample Semantic Re-ranked Peer Network

Date: 2026-05-31

Purpose: expand the v13 200-focal semantic peer re-ranking to the full focal-event
universe and test whether the current GenAI peer-CAR result survives under a
cleaner semantic product-market peer definition.

## Construction

Candidate peers are drawn from four auditable systems:

1. annual-report same-industry text Top10;
2. CSMAR business-scope text Top10;
3. annual-report global AI-word-stripped Top10;
4. random same-industry Top10, included only as a candidate pool stress test.

Candidates are re-ranked by the deterministic semantic product/category scorer
used in v13. This is an auditable LLM-style semantic reranking, not an external
API call and not a hand-picked peer list.

## Coverage

{format_table(summaries, ['peer_source','raw_rows','raw_events','raw_focal_firms','raw_peer_firms','raw_top5_rows','mean_peer_similarity_top5','median_peer_similarity_top5'])}

## Candidate Source Summary

{format_table(cand_summary, ['candidate_source_system','candidate_rows','focal_firms','mean_score','direct_share','mean_similarity'])}

## Selected Source Mix

{format_table(mix, ['candidate_source_system','selected_pairs','mean_rank','direct_share','mean_score','mean_similarity'])}

## Main Effects

Specification:

```text
PeerCAR[0,+1] = beta * Specificity_z x AIActivePeer
              + AIActivePeer
              + PeerCAR[-10,-2] + PeerCAR[-20,-2]
              + event FE + peer industry-week FE
```

Sample: first focal GenAI events, announcement-cleaned observations.

{format_table(res, ['peer_source','top_n','ai_def','coef','se','p','nobs','events','focal_firms','peer_firms','mean_y','mean_ai'])}

## Reading

This is the key go/no-go test for replacing the old CSMAR scope Top5 with a
cleaner semantic peer definition. A viable replacement should preserve a
negative and preferably significant coefficient for `ext_any` at Top5.

If `ext_any` is not negative/significant here, then the current peer-CAR result
cannot be described as robust to the full semantic product-market peer network.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")
    print(summaries.to_string(index=False), flush=True)
    print(mix.to_string(index=False), flush=True)
    print(res.to_string(index=False), flush=True)
    print(f"Wrote {OUT_DIR}", flush=True)
    print(f"Wrote {DOC_PATH}", flush=True)


if __name__ == "__main__":
    main()
