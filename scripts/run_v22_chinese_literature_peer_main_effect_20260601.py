#!/usr/bin/env python3
"""Run peer-CAR regressions using v22 Chinese-literature peer networks."""

from __future__ import annotations

from pathlib import Path

import run_v12_annual_report_peer_main_effect_20260530 as v12


ROOT = v12.ROOT
PEER_DIR = ROOT / "results" / "v22_chinese_literature_product_peers_20260601"
OUT_DIR = ROOT / "results" / "v22_chinese_literature_peer_main_effect_20260601"


v12.OUT_DIR = OUT_DIR
v12.PEER_FILES = {
    "ren_wang_binary_global": PEER_DIR / "ren_wang_binary_global_peer_event_top20.csv",
    "ren_wang_binary_same_industry_d": PEER_DIR
    / "ren_wang_binary_same_industry_d_peer_event_top20.csv",
    "liu_product_tfidf_global": PEER_DIR / "liu_product_tfidf_global_peer_event_top20.csv",
    "liu_product_tfidf_same_industry_d": PEER_DIR
    / "liu_product_tfidf_same_industry_d_peer_event_top20.csv",
}


def main() -> None:
    missing = [str(p) for p in v12.PEER_FILES.values() if not Path(p).exists()]
    if missing:
        raise FileNotFoundError("Missing v22 peer-event files:\n" + "\n".join(missing))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    v12.main()


if __name__ == "__main__":
    main()
