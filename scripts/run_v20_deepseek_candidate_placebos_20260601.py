#!/usr/bin/env python3
"""DeepSeek-candidate-menu placebo peer tests.

This script rebuilds the random / low-similarity placebo peer sets using the
same candidate menus that fed the v17 DeepSeek Flash-selected Top5 network.
For each focal firm, it excludes the DeepSeek-selected Top5 peers and then
constructs:

1. random peers sampled from the remaining candidate menu;
2. low-similarity peers selected from the bottom of the remaining candidate menu.

This is cleaner than the older v6 placebo because the candidate universe is
held fixed to the exact auditable menu used by the headline DeepSeek peer
selection.
"""

from __future__ import annotations

import re
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
from run_v16_full_semantic_reranked_peer_network_20260531 import build_event_peer_panel
from run_v17_deepseek_flash_peer_coding_20260531 import load_candidate_rows
from run_v6_announcement_clean_checks_20260524 import (
    ROOT,
    attach_announcement_flags,
    build_announcement_stock_day_flags,
)
from run_v6_identification_strengthening_checks_20260524 import (
    build_return_lookup,
    load_stock_model,
)


OUT_DIR = ROOT / "results" / "v20_deepseek_candidate_placebos_20260601"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "84_v20_deepseek_candidate_placebos_20260601.md"
V17_NETWORK = (
    ROOT
    / "results"
    / "v17_deepseek_flash_peer_coding_20260531"
    / "deepseek_flash_peer_network_top5_full_compact15.csv"
)


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    digits = re.sub(r"\D", "", str(value))
    return digits.zfill(6) if digits else ""


def normalize_candidate_meta(candidates: pd.DataFrame) -> pd.DataFrame:
    d = candidates.copy()
    d["focal_code"] = d["focal_code"].map(code6)
    d["peer_code"] = d["peer_code"].map(code6)
    for col in ["product_similarity", "source_rank", "source_priority"]:
        if col in d.columns:
            d[col] = pd.to_numeric(d[col], errors="coerce")
    return d


def make_network(rows: list[dict[str, object]], source_name: str) -> pd.DataFrame:
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["peer_source"] = source_name
    out["top_n"] = 5
    return out[
        [
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
        ]
    ].copy()


def row_dict(row: pd.Series, rank: int) -> dict[str, object]:
    return {
        "focal_code": row["focal_code"],
        "peer_code": row["peer_code"],
        "peer_rank": rank,
        "peer_similarity": float(row.get("product_similarity", np.nan)),
        "focal_name": row.get("focal_name_final", ""),
        "peer_name": row.get("peer_name_final", ""),
        "focal_industry_d": row.get("focal_industry_final", ""),
        "peer_industry_d": row.get("peer_industry_final", ""),
        "candidate_source_system": row.get("candidate_source_system", ""),
        "source_rank": row.get("source_rank", np.nan),
    }


def build_placebo_networks(top_n: int = 5) -> dict[str, pd.DataFrame]:
    candidates = normalize_candidate_meta(load_candidate_rows(max_candidates=15))
    selected = pd.read_csv(V17_NETWORK, dtype={"focal_code": str, "peer_code": str})
    selected["focal_code"] = selected["focal_code"].map(code6)
    selected["peer_code"] = selected["peer_code"].map(code6)
    selected_sets = {
        focal: set(g["peer_code"])
        for focal, g in selected[["focal_code", "peer_code"]].drop_duplicates().groupby("focal_code")
    }

    low_rows: list[dict[str, object]] = []
    rand_rows: list[dict[str, object]] = []
    coverage_rows: list[dict[str, object]] = []

    for focal, g in candidates.groupby("focal_code", sort=True):
        g = g.drop_duplicates("peer_code").copy()
        g = g[~g["peer_code"].isin(selected_sets.get(focal, set()))].copy()
        g = g[g["peer_code"].ne(focal)]
        if len(g) < top_n:
            coverage_rows.append(
                {
                    "focal_code": focal,
                    "remaining_candidates": len(g),
                    "used_in_placebo": 0,
                }
            )
            continue
        low = g.sort_values(
            ["product_similarity", "source_priority", "source_rank"],
            ascending=[True, True, True],
        ).head(top_n)
        seed = int(focal[-5:]) + 20260601 if focal[-5:].isdigit() else 20260601
        rand = g.sample(n=top_n, random_state=seed)
        for rank, (_, row) in enumerate(low.iterrows(), start=1):
            low_rows.append(row_dict(row, rank))
        for rank, (_, row) in enumerate(rand.iterrows(), start=1):
            rand_rows.append(row_dict(row, rank))
        coverage_rows.append(
            {
                "focal_code": focal,
                "remaining_candidates": len(g),
                "used_in_placebo": 1,
            }
        )

    coverage = pd.DataFrame(coverage_rows)
    coverage.to_csv(OUT_DIR / "candidate_placebo_coverage_by_focal.csv", index=False)
    return {
        "deepseek_candidate_low_similarity_top5": make_network(
            low_rows, "deepseek_candidate_low_similarity"
        ),
        "deepseek_candidate_random_top5": make_network(rand_rows, "deepseek_candidate_random"),
    }


def source_mix(network: pd.DataFrame, source_name: str) -> pd.DataFrame:
    if network.empty:
        return pd.DataFrame()
    out = (
        network.groupby("candidate_source_system", as_index=False)
        .agg(
            peer_source=("peer_source", "first"),
            selected_pairs=("peer_code", "size"),
            mean_rank=("peer_rank", "mean"),
            mean_similarity=("peer_similarity", "mean"),
        )
        .sort_values(["peer_source", "selected_pairs"], ascending=[True, False])
    )
    out["network_name"] = source_name
    return out


def run_panel_tests(networks: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    lookup = build_return_lookup(load_stock_model())
    ann_flags = build_announcement_stock_day_flags()
    summaries = []
    regs = []
    mixes = []
    for name, net in networks.items():
        net.to_csv(OUT_DIR / f"{name}.csv", index=False)
        panel = build_event_peer_panel(net)
        panel = attach_returns(panel, lookup)
        panel = attach_announcement_flags(panel, ann_flags)
        panel = attach_ai_flags(panel)
        panel.to_csv(OUT_DIR / f"{name}_event_peer_panel.csv.gz", index=False, compression="gzip")
        summaries.append(source_summary(panel, name))
        mixes.append(source_mix(net, name))
        for ai_def in ["ext_any", "current_text_history", "ext_no_hiring", "ext_plus_history"]:
            regs.append(run_model(panel, ai_def, name, 5))
    return pd.DataFrame(summaries), pd.DataFrame(regs), pd.concat(mixes, ignore_index=True)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    networks = build_placebo_networks(top_n=5)
    summary, regs, mix = run_panel_tests(networks)

    coverage = pd.read_csv(OUT_DIR / "candidate_placebo_coverage_by_focal.csv", dtype={"focal_code": str})
    coverage_summary = pd.DataFrame(
        [
            {
                "focal_firms_with_candidate_menu": int(len(coverage)),
                "focal_firms_with_placebo_top5": int(coverage["used_in_placebo"].sum()),
                "mean_remaining_candidates": float(coverage["remaining_candidates"].mean()),
                "median_remaining_candidates": float(coverage["remaining_candidates"].median()),
            }
        ]
    )

    summary.to_csv(OUT_DIR / "deepseek_candidate_placebo_coverage_summary.csv", index=False)
    regs.to_csv(OUT_DIR / "deepseek_candidate_placebo_main_effects.csv", index=False)
    mix.to_csv(OUT_DIR / "deepseek_candidate_placebo_source_mix.csv", index=False)
    coverage_summary.to_csv(OUT_DIR / "deepseek_candidate_placebo_focal_coverage_summary.csv", index=False)

    doc = f"""# v20 DeepSeek Candidate-Menu Placebo Peers

Date: 2026-06-01

Purpose: rebuild random and low-similarity placebo peer sets from the same
candidate menu used by the v17 DeepSeek Flash-selected Top5 network. This
holds the auditable candidate universe fixed and excludes the actual
DeepSeek-selected Top5 peers before constructing placebo peers.

## Construction

For each focal firm:

1. reconstruct the v17 no-random candidate menu, max 15 candidates;
2. remove the v17 DeepSeek-selected Top5 peers;
3. create `deepseek_candidate_low_similarity_top5` by choosing the remaining
   candidates with the lowest product similarity;
4. create `deepseek_candidate_random_top5` by drawing five remaining candidates
   using a deterministic focal-code seed.

These are falsification peers, not alternative headline peer definitions.

## Candidate Coverage

{format_table(coverage_summary, ['focal_firms_with_candidate_menu','focal_firms_with_placebo_top5','mean_remaining_candidates','median_remaining_candidates'])}

## Event-Peer Coverage

{format_table(summary, ['peer_source','raw_rows','raw_events','raw_focal_firms','raw_peer_firms','raw_top5_rows','mean_peer_similarity_top5','median_peer_similarity_top5'])}

## Candidate Source Mix

{format_table(mix, ['network_name','candidate_source_system','selected_pairs','mean_rank','mean_similarity'])}

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

## Reading

This is a stricter placebo than the older v6 random / low-similarity peer sets
because it uses the exact candidate universe that fed the headline DeepSeek
selection. If the headline result also appears in these placebo sets, then the
DeepSeek-selected-peer story is weak. If the placebo coefficients attenuate
toward zero, this supports the claim that the result is tied to the selected
product-market peers rather than any firm in the candidate menu.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")
    print(summary.to_string(index=False), flush=True)
    print(regs.to_string(index=False), flush=True)
    print(f"Wrote {OUT_DIR}", flush=True)
    print(f"Wrote {DOC_PATH}", flush=True)


if __name__ == "__main__":
    main()
