#!/usr/bin/env python3
"""Variant tests for the full semantic re-ranked peer network.

This script reuses the full candidate scores from v16 and asks which candidate
pool is carrying the semantic peer-CAR result:

- all candidates;
- no random same-industry candidates;
- annual-report-only candidates;
- CSMAR-scope-only candidates;
- annual same-industry only.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from run_v15_alternative_peer_definitions_20260531 import (
    attach_ai_flags,
    attach_returns,
    format_table,
    run_model,
    source_summary,
)
from run_v16_full_semantic_reranked_peer_network_20260531 import (
    DOC_PATH as V16_DOC_PATH,
    OUT_DIR,
    build_event_peer_panel,
    build_semantic_network,
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


DOC_PATH = ROOT / "docs" / "empirical_runs" / "80_v16_full_semantic_peer_variants_20260531.md"

VARIANTS: dict[str, list[str]] = {
    "all_candidates": [
        "annual_same_industry",
        "csmar_scope",
        "annual_global_ai_stripped",
        "random_same_industry",
    ],
    "no_random": [
        "annual_same_industry",
        "csmar_scope",
        "annual_global_ai_stripped",
    ],
    "annual_only": [
        "annual_same_industry",
        "annual_global_ai_stripped",
    ],
    "annual_same_only": [
        "annual_same_industry",
    ],
    "csmar_scope_only": [
        "csmar_scope",
    ],
}


def select_network(scored: pd.DataFrame, variant: str, sources: list[str], top_k: int = 10) -> pd.DataFrame:
    d = scored[scored["candidate_source_system"].isin(sources)].copy()
    d["semantic_score_0_3"] = pd.to_numeric(d["semantic_score_0_3"], errors="coerce").fillna(0)
    d["semantic_direct_peer"] = pd.to_numeric(d["semantic_direct_peer"], errors="coerce").fillna(0)
    d["source_priority"] = pd.to_numeric(d["source_priority"], errors="coerce").fillna(9)
    d["product_similarity"] = pd.to_numeric(d["product_similarity"], errors="coerce").fillna(-1)
    d["source_rank"] = pd.to_numeric(d["source_rank"], errors="coerce").fillna(999)
    d = d.sort_values(
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
    selected = d.groupby("focal_code", as_index=False, group_keys=False).head(top_k).copy()
    selected["peer_rank"] = selected.groupby("focal_code").cumcount() + 1
    selected["peer_source"] = variant
    selected["top_n"] = top_k
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
    for col in keep:
        if col not in selected.columns:
            selected[col] = np.nan
    return selected[keep].copy()


def source_mix(network: pd.DataFrame, variant: str) -> pd.DataFrame:
    out = (
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
    out.insert(0, "variant", variant)
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Ensure v16 scored candidates exist.
    _, scored = build_semantic_network()
    lookup = build_return_lookup(load_stock_model())
    ann_flags = build_announcement_stock_day_flags()

    all_regs = []
    all_summaries = []
    all_mix = []
    for variant, sources in VARIANTS.items():
        print(f"Running variant {variant}...", flush=True)
        network = select_network(scored, variant, sources)
        network.to_csv(OUT_DIR / f"{variant}_semantic_peer_network_top10.csv", index=False)
        panel = build_event_peer_panel(network)
        panel = attach_returns(panel, lookup)
        panel = attach_announcement_flags(panel, ann_flags)
        panel = attach_ai_flags(panel)
        panel.to_csv(OUT_DIR / f"{variant}_semantic_event_peer_panel.csv.gz", index=False, compression="gzip")
        summ = source_summary(panel, variant)
        summ["candidate_sources"] = ",".join(sources)
        all_summaries.append(summ)
        all_mix.append(source_mix(network, variant))
        for top_n in [5, 10]:
            for ai_def in ["ext_any", "current_text_history", "ext_no_hiring", "ext_plus_history"]:
                all_regs.append(run_model(panel, ai_def, variant, top_n))

    summaries = pd.DataFrame(all_summaries)
    mix = pd.concat(all_mix, ignore_index=True)
    regs = pd.DataFrame(all_regs)
    summaries.to_csv(OUT_DIR / "full_semantic_variant_coverage_summary.csv", index=False)
    mix.to_csv(OUT_DIR / "full_semantic_variant_source_mix.csv", index=False)
    regs.to_csv(OUT_DIR / "full_semantic_variant_main_effects.csv", index=False)

    doc = f"""# v16 Full Semantic Peer Variants

Date: 2026-05-31

Purpose: decompose the full semantic re-ranked peer result by candidate pool.
This addresses whether the replacement peer network is truly independent of the
old CSMAR scope network and whether random same-industry candidates are carrying
the result.

The base v16 full semantic result is documented in:

```text
{V16_DOC_PATH.relative_to(ROOT)}
```

## Coverage

{format_table(summaries, ['peer_source','raw_rows','raw_events','raw_focal_firms','raw_peer_firms','raw_top5_rows','mean_peer_similarity_top5','median_peer_similarity_top5'])}

## Source Mix

{format_table(mix, ['variant','candidate_source_system','selected_pairs','mean_rank','direct_share','mean_score','mean_similarity'])}

## Main Effects

Specification:

```text
PeerCAR[0,+1] = beta * Specificity_z x AIActivePeer
              + AIActivePeer
              + PeerCAR[-10,-2] + PeerCAR[-20,-2]
              + event FE + peer industry-week FE
```

Sample: first focal GenAI events, announcement-cleaned observations.

{format_table(regs, ['peer_source','top_n','ai_def','coef','se','p','nobs','events','focal_firms','peer_firms','mean_y','mean_ai'])}

## Reading Rule

- `no_random` is the cleaner candidate-pool version for a paper table.
- `annual_only` is the most literature-clean annual-report text version.
- `csmar_scope_only` tests whether the old result is simply reappearing through
  the old CSMAR business-scope candidates.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")
    print(regs.to_string(index=False), flush=True)
    print(f"Wrote {OUT_DIR}", flush=True)
    print(f"Wrote {DOC_PATH}", flush=True)


if __name__ == "__main__":
    main()
