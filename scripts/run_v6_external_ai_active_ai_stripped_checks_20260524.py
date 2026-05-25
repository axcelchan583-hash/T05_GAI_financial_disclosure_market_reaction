#!/usr/bin/env python3
"""External AIActivePeer checks on the AI-word-stripped peer network."""

from __future__ import annotations

import pandas as pd

from run_v6_external_ai_active_checks_20260524 import (
    OUT_DIR as BASE_OUT_DIR,
    ROOT,
    attach_external_flags,
    load_first_dates,
    load_hiring_lookup,
    run_models,
)


AI_STRIPPED_PANEL = (
    ROOT
    / "results"
    / "v6_ai_stripped_similarity_checks_20260524"
    / "ai_stripped_peer_market_model_car_panel_with_ann_flags.csv.gz"
)
OUT_DIR = ROOT / "results" / "v6_external_ai_active_ai_stripped_checks_20260524"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    first_dates = load_first_dates()
    hiring = load_hiring_lookup()
    panel = pd.read_csv(AI_STRIPPED_PANEL, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    for col in ["event_date", "date_0", "date_m1", "date_p1"]:
        panel[col] = pd.to_datetime(panel[col], errors="coerce")
    panel["peer_industry_d"] = panel["peer_industry_d"].fillna("UNKNOWN").astype(str)
    panel["event_week"] = panel["date_0"].dt.strftime("%Y-%U")
    panel["peer_industry_week"] = panel["peer_industry_d"] + "|" + panel["event_week"].fillna("")
    panel = attach_external_flags(panel, first_dates, hiring)
    panel.to_csv(OUT_DIR / "ai_stripped_panel_with_external_ai_active.csv.gz", index=False, compression="gzip")

    all_summaries = []
    all_regs = []
    for peer_group, sub, top_n in [
        ("ai_stripped_top5", panel[panel["peer_rank"].le(5)].copy(), 5),
        ("ai_stripped_top10", panel[panel["peer_rank"].le(10)].copy(), 10),
    ]:
        summaries, regs = run_models(sub, peer_group, top_n)
        all_summaries.extend(summaries)
        all_regs.extend(regs)
    summary = pd.DataFrame(all_summaries)
    regs = pd.DataFrame(all_regs)
    summary.to_csv(OUT_DIR / "v6_external_ai_active_ai_stripped_sample_summary.csv", index=False)
    regs.to_csv(OUT_DIR / "v6_external_ai_active_ai_stripped_regressions.csv", index=False)
    key = regs[
        regs["term"].eq(regs["interaction_term"])
        & regs["sample"].eq("drop_either_cleaning_ann")
        & regs["outcome"].eq("peer_car_0_p1_mm")
    ].copy()
    print(summary.to_string(index=False), flush=True)
    print(key.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
