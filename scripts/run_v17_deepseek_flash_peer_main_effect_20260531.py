#!/usr/bin/env python3
"""Run main PeerCAR tests on the DeepSeek Flash-selected peer network."""

from __future__ import annotations

import pandas as pd

from run_v15_alternative_peer_definitions_20260531 import (
    attach_ai_flags,
    attach_returns,
    format_table,
    run_model,
    source_summary,
)
from run_v16_full_semantic_reranked_peer_network_20260531 import build_event_peer_panel
from run_v6_announcement_clean_checks_20260524 import (
    ROOT,
    attach_announcement_flags,
    build_announcement_stock_day_flags,
)
from run_v6_identification_strengthening_checks_20260524 import (
    build_return_lookup,
    load_stock_model,
)


OUT_DIR = ROOT / "results" / "v17_deepseek_flash_peer_coding_20260531"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "81_v17_deepseek_flash_peer_network_20260531.md"
NETWORK = OUT_DIR / "deepseek_flash_peer_network_top5_full_compact15.csv"
SUMMARY_JSON = OUT_DIR / "deepseek_flash_summary_full_compact15.json"


def source_mix(network: pd.DataFrame) -> pd.DataFrame:
    return (
        network.groupby("candidate_source_system", as_index=False)
        .agg(
            selected_pairs=("peer_code", "size"),
            mean_rank=("peer_rank", "mean"),
            mean_similarity=("peer_similarity", "mean"),
        )
        .sort_values("selected_pairs", ascending=False)
    )


def main() -> None:
    network = pd.read_csv(NETWORK, dtype={"focal_code": str, "peer_code": str})
    # build_event_peer_panel expects a peer_source column but we want a compact
    # source name in tables.
    network["peer_source"] = "deepseek_flash_top5"
    lookup = build_return_lookup(load_stock_model())
    ann_flags = build_announcement_stock_day_flags()
    panel = build_event_peer_panel(network)
    panel = attach_returns(panel, lookup)
    panel = attach_announcement_flags(panel, ann_flags)
    panel = attach_ai_flags(panel)
    panel.to_csv(OUT_DIR / "deepseek_flash_event_peer_panel_full_compact15.csv.gz", index=False, compression="gzip")

    summaries = pd.DataFrame([source_summary(panel, "deepseek_flash_top5")])
    mix = source_mix(network)
    regs = []
    for top_n in [3, 5]:
        for ai_def in ["ext_any", "current_text_history", "ext_no_hiring", "ext_plus_history"]:
            regs.append(run_model(panel, ai_def, "deepseek_flash_top5", top_n))
    res = pd.DataFrame(regs)
    summaries.to_csv(OUT_DIR / "deepseek_flash_coverage_summary_full_compact15.csv", index=False)
    mix.to_csv(OUT_DIR / "deepseek_flash_source_mix_full_compact15.csv", index=False)
    res.to_csv(OUT_DIR / "deepseek_flash_main_effects_full_compact15.csv", index=False)

    doc = f"""# v17 DeepSeek Flash Peer Network

Date: 2026-05-31

Purpose: use DeepSeek V4 Flash to select direct product-market peers from a
compact no-random candidate menu and test whether the GenAI peer-CAR result
survives under an actual generative-AI peer-selection pass.

## API Coding Setup

- Model: `deepseek-v4-flash`
- Candidate menu: no-random v16 pool, max 15 candidates per focal firm.
- Output: compact JSON code list only, no explanations.
- API key was read from environment variable and was not stored in scripts or
  outputs.

Summary file:

```text
{SUMMARY_JSON.relative_to(ROOT)}
```

Network file:

```text
{NETWORK.relative_to(ROOT)}
```

## Coverage

{format_table(summaries, ['peer_source','raw_rows','raw_events','raw_focal_firms','raw_peer_firms','raw_top5_rows','mean_peer_similarity_top5','median_peer_similarity_top5'])}

## Selected Candidate Source Mix

{format_table(mix, ['candidate_source_system','selected_pairs','mean_rank','mean_similarity'])}

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

This is the closest current implementation to the Cao et al.-style GenAI peer
idea. It still uses a candidate menu to avoid hallucinated stock codes, but the
final Top5 selection is made by a generative model rather than the deterministic
semantic scorer.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")
    print(summaries.to_string(index=False), flush=True)
    print(mix.to_string(index=False), flush=True)
    print(res.to_string(index=False), flush=True)
    print(f"Wrote {DOC_PATH}", flush=True)


if __name__ == "__main__":
    main()
