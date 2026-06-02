#!/usr/bin/env python3
"""Component screen for the new GenAI concreteness measurement.

The main residualized density measure did not reproduce the legacy effect. This
screen checks whether the signal lives in a specific Hope/Cheng component rather
than the full density index.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from run_v6_final_review_checks_20260525 import OUTCOME, ROOT, STRONG_FE
from run_v6_identification_strengthening_checks_20260524 import fit_absorbed


OUT_DIR = ROOT / "results" / "v9_genai_concreteness_component_screen_20260528"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "65_v9_genai_concreteness_component_screen_20260528.md"

PANEL_PATH = ROOT / "results" / "v9_genai_concreteness_main_checks_20260528" / "analysis_sample_top5_with_genai_concreteness.csv.gz"
X_PATH = ROOT / "results" / "genai_concreteness_measure_20260528" / "event_genai_concreteness.csv"

AI_DEFS = ["ext_any", "current_text_history"]
CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
CONTENT_FLAGS = [
    "competitive_risk_content",
    "category_validation_content",
    "speculative_or_generic_content",
    "substantive_or_existing_content",
    "positive_genai_claim_content",
    "denial_or_no_exposure_content",
]


def zscore(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").astype(float)
    std = x.std(ddof=0)
    if not np.isfinite(std) or std == 0:
        return pd.Series(np.zeros(len(x)), index=s.index)
    return (x - x.mean()) / std


def load_sample() -> pd.DataFrame:
    panel = pd.read_csv(PANEL_PATH, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    x_cols = [
        "event_id",
        "genai_concreteness_raw",
        "genai_concreteness_z",
        "genai_concreteness_resid_z",
        "genai_concreteness_char_density",
        "entity_concrete_count",
        "operational_concrete_count",
        "quant_concrete_count",
        "total_concrete_count",
        "genai_token_count",
        "genai_char_count",
        "ai_keyword_count",
        "positive_genai_sentence_count",
        *CONTENT_FLAGS,
    ]
    x = pd.read_csv(X_PATH, dtype={"event_id": str}, usecols=x_cols)
    # Preserve any columns already merged in the panel; add detailed count fields.
    add = x.drop(columns=[c for c in ["genai_concreteness_z", "genai_concreteness_resid_z"] if c in x.columns])
    d = panel.merge(add, on="event_id", how="left", suffixes=("", "_detail"), validate="many_to_one")
    event = d.drop_duplicates("event_id").copy()
    for col in [
        "genai_concreteness_raw",
        "genai_concreteness_char_density",
        "entity_concrete_count",
        "operational_concrete_count",
        "quant_concrete_count",
        "total_concrete_count",
        "genai_token_count",
        "genai_char_count",
        "ai_keyword_count",
        "positive_genai_sentence_count",
    ]:
        event[f"{col}_z_event"] = zscore(event[col])
        event[f"log1p_{col}_z_event"] = zscore(np.log1p(pd.to_numeric(event[col], errors="coerce").fillna(0)))
    keep = ["event_id"] + [c for c in event.columns if c.endswith("_z_event")]
    d = d.merge(event[keep], on="event_id", how="left", validate="many_to_one")
    return d


def run_one(data: pd.DataFrame, ai_def: str, x_col: str, model: str) -> dict[str, object]:
    d = data.copy()
    d["ai"] = pd.to_numeric(d[ai_def], errors="coerce").fillna(0).astype(float)
    d["x_main"] = pd.to_numeric(d[x_col], errors="coerce")
    d["x_ai"] = d["x_main"] * d["ai"]
    rows = fit_absorbed(d, OUTCOME, ["ai", "x_ai", *CONTROLS], STRONG_FE, model=model, term_focus="x_ai")
    if not rows:
        return {
            "ai_def": ai_def,
            "x_col": x_col,
            "model": model,
            "coef": np.nan,
            "se": np.nan,
            "z": np.nan,
            "p": np.nan,
            "nobs": 0,
            "events": 0,
            "peer_firms": 0,
        }
    row = rows[0]
    row.update({"ai_def": ai_def, "x_col": x_col})
    return row


def run_binary_content(data: pd.DataFrame, ai_def: str) -> pd.DataFrame:
    d = data.copy()
    d["ai"] = pd.to_numeric(d[ai_def], errors="coerce").fillna(0).astype(float)
    xvars = ["ai", *[f"{flag}_ai" for flag in CONTENT_FLAGS], *CONTROLS]
    for flag in CONTENT_FLAGS:
        d[f"{flag}_ai"] = pd.to_numeric(d[flag], errors="coerce").fillna(0).astype(float) * d["ai"]
    rows = fit_absorbed(d, OUTCOME, xvars, STRONG_FE, model="binary_content_flags_x_ai", term_focus=None)
    out = []
    focus = {f"{flag}_ai" for flag in CONTENT_FLAGS}
    for row in rows:
        if row["term"] in focus:
            row.update({"ai_def": ai_def, "x_col": row["term"]})
            out.append(row)
    return pd.DataFrame(out)


def pstars(p: float) -> str:
    if pd.isna(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def md_table(df: pd.DataFrame) -> str:
    d = df.copy()
    d["coef_se"] = d.apply(
        lambda r: f"{r['coef']:.6f}{pstars(r['p'])} ({r['se']:.6f})" if pd.notna(r.get("coef")) else "",
        axis=1,
    )
    cols = ["ai_def", "x_col", "coef_se", "p", "nobs", "events", "peer_firms"]
    out = d[cols].copy()
    out["p"] = out["p"].map(lambda x: "" if pd.isna(x) else f"{float(x):.4f}")
    return out.to_markdown(index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    sample = load_sample()

    continuous_x = [
        "genai_concreteness_raw_z_event",
        "genai_concreteness_char_density_z_event",
        "entity_concrete_count_z_event",
        "operational_concrete_count_z_event",
        "quant_concrete_count_z_event",
        "total_concrete_count_z_event",
        "log1p_entity_concrete_count_z_event",
        "log1p_operational_concrete_count_z_event",
        "log1p_quant_concrete_count_z_event",
        "log1p_total_concrete_count_z_event",
        "positive_genai_sentence_count_z_event",
        "log1p_positive_genai_sentence_count_z_event",
        "ai_keyword_count_z_event",
        "genai_token_count_z_event",
    ]
    rows = []
    for ai_def in AI_DEFS:
        for x_col in continuous_x:
            rows.append(run_one(sample, ai_def, x_col, "continuous_component_x_ai"))
    continuous = pd.DataFrame(rows)
    continuous.to_csv(OUT_DIR / "continuous_component_screen.csv", index=False)

    binary = pd.concat([run_binary_content(sample, ai_def) for ai_def in AI_DEFS], ignore_index=True)
    binary.to_csv(OUT_DIR / "binary_content_flag_screen.csv", index=False)

    top_cont = continuous.sort_values("p", na_position="last").head(30)
    top_bin = binary.sort_values("p", na_position="last")

    doc = f"""# V9 GenAI Concreteness Component Screen

Date: 2026-05-28

## Purpose

The full Hope/Cheng-style continuous density X did not reproduce the legacy `specificity_z x AIActivePeer` result. This screen checks whether a specific component of the new measurement has signal.

Specification for continuous components:

`PeerCAR[0,+1] ~ AIActive + Component_z x AIActive + PeerCAR[-10,-2] + PeerCAR[-20,-2] + event FE + peer industry-week FE`

SE: two-way clustered by `event_id + peer_code`.

## Top Continuous Component Results

{md_table(top_cont)}

## Binary Cheng-Style Content Flags

Each row is the coefficient on `content_flag x AIActive`, estimated jointly with the other content flags.

{md_table(top_bin)}

## Interpretation

This is a diagnostic screen, not a final table. Its purpose is to decide whether the new X should be refined around a specific component, kept only as validation, or abandoned as the headline X.

"""
    DOC_PATH.write_text(doc, encoding="utf-8")

    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()

