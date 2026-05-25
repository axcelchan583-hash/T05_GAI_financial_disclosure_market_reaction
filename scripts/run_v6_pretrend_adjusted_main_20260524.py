#!/usr/bin/env python3
"""Pretrend-adjusted main effects for v6."""

from __future__ import annotations

import pandas as pd

from run_v6_announcement_clean_checks_20260524 import base_clean_sample
from run_v6_identification_strengthening_checks_20260524 import (
    MAIN_AI_DEF,
    OUTCOME,
    TRUE_EXT_PANEL,
    add_main_terms,
    add_prewindow_outcomes,
    build_return_lookup,
    fit_absorbed,
    load_panel,
    load_stock_model,
    OUT_DIR,
)


def main() -> None:
    true = load_panel(TRUE_EXT_PANEL)
    stock_model = load_stock_model()
    lookup = build_return_lookup(stock_model)
    panel = add_prewindow_outcomes(true[true["peer_rank"].le(5)].copy(), lookup)
    sample = base_clean_sample(panel)
    sample = sample[sample["either_cleaning_ann"].eq(0)].copy()

    rows = []
    for ai_def in [MAIN_AI_DEF, "ext_any", "ext_plus_history"]:
        d = add_main_terms(sample, ai_def)
        specs = [
            ("no_pretrend_control", ["ai", "spec_ai"]),
            ("control_pre10", ["ai", "spec_ai", "peer_car_pre10_m2_mm"]),
            ("control_pre20", ["ai", "spec_ai", "peer_car_pre20_m2_mm"]),
            ("control_pre10_pre20", ["ai", "spec_ai", "peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]),
        ]
        for control_spec, xvars in specs:
            for fe_name, fe_cols in [
                ("event_fe", ["event_id"]),
                ("event_fe_peer_industry_week_fe", ["event_id", "peer_industry_week"]),
                ("event_peer_firm_fe", ["event_id", "peer_code"]),
            ]:
                for row in fit_absorbed(
                    d,
                    OUTCOME,
                    xvars,
                    fe_cols,
                    model="pretrend_adjusted_main",
                    term_focus="spec_ai",
                ):
                    row.update({"ai_def": ai_def, "control_spec": control_spec, "fe_spec": fe_name})
                    rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(OUT_DIR / "pretrend_adjusted_main_results.csv", index=False)
    print(out.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
