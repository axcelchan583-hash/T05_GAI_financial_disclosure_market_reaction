#!/usr/bin/env python3
"""Disclosure-type horse-race for the T05 peer-CAR design.

This diagnostic splits focal GenAI disclosures into rough regex-based types:
own GenAI implementation, AI supply-chain exposure, generic AI attention, and
denial/no-current-involvement. It asks whether the current peer-revaluation
result is driven by a particular disclosure type, and whether type indicators
absorb the existing Specificity_z x AIActivePeer effect.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from run_v6_final_review_checks_20260525 import OUTCOME, ROOT, STRONG_FE
from run_v6_identification_strengthening_checks_20260524 import fit_absorbed


OUT_DIR = ROOT / "results" / "v7_disclosure_type_horserace_20260527"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "59_v7_disclosure_type_horserace_20260527.md"

TOP5_SUPPLY_PATH = (
    ROOT
    / "results"
    / "v7_ai_supply_chain_disclosure_diagnostic_20260527"
    / "analysis_sample_top5_with_supply_chain_codes.csv.gz"
)

TYPE_FLAGS = [
    "own_genai_implementation_regex",
    "ai_supply_chain_exposure",
    "generic_ai_attention_regex",
    "denial_no_current_regex",
]
TYPE_LABELS = {
    "own_genai_implementation_regex": "own_impl",
    "ai_supply_chain_exposure": "supply_chain",
    "generic_ai_attention_regex": "generic_attention",
    "denial_no_current_regex": "denial_no_current",
}
AI_DEFS = ["ext_any", "current_text_history"]
CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]


def load_sample() -> pd.DataFrame:
    df = pd.read_csv(TOP5_SUPPLY_PATH, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    df = df[df["peer_rank"].le(5)].copy()
    # This file is already the first-event, announcement-cleaned Top5 sample from
    # the v6/v7 branch, but keep the filters explicit for reproducibility.
    if "either_cleaning_ann" in df.columns:
        df = df[df["either_cleaning_ann"].eq(0)].copy()
    if "is_first_focal_event" in df.columns:
        df = df[df["is_first_focal_event"].eq(1)].copy()
    for col in TYPE_FLAGS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    for col in ["specificity_z", OUTCOME, *CONTROLS, *AI_DEFS]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if "focal_industry_week" not in df.columns:
        df["event_week"] = pd.to_datetime(df["date_0"], errors="coerce").dt.strftime("%Y-%U")
        df["focal_industry_week"] = df["focal_industry_d"].fillna("UNKNOWN").astype(str) + "|" + df[
            "event_week"
        ].fillna("")
    return df


def add_terms(df: pd.DataFrame, ai_def: str) -> pd.DataFrame:
    out = df.copy()
    out["ai"] = out[ai_def].fillna(0).astype(float)
    out["spec_ai"] = out["specificity_z"] * out["ai"]
    for flag in TYPE_FLAGS:
        label = TYPE_LABELS[flag]
        out[f"{label}_ai"] = out[flag].astype(float) * out["ai"]
        out[f"{label}_spec_ai"] = out[flag].astype(float) * out["specificity_z"] * out["ai"]
    return out


def collect_rows(
    data: pd.DataFrame,
    outcome: str,
    xvars: list[str],
    fe_cols: list[str],
    model: str,
    ai_def: str,
    controls_note: str,
    focus_terms: list[str] | None = None,
) -> list[dict[str, object]]:
    rows = fit_absorbed(data, outcome, xvars, fe_cols, model=model, term_focus=None)
    out: list[dict[str, object]] = []
    for row in rows:
        if focus_terms is not None and row["term"] not in focus_terms:
            continue
        row.update(
            {
                "ai_def": ai_def,
                "fe": "+".join(fe_cols),
                "controls": controls_note,
                "cluster": "event_id + peer_code",
            }
        )
        out.append(row)
    return out


def summarize_types(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    event = df.drop_duplicates("event_id").copy()
    rows = []
    for flag in TYPE_FLAGS:
        rows.append(
            {
                "type": TYPE_LABELS[flag],
                "events": int(event[flag].sum()),
                "event_share": float(event[flag].mean()),
                "obs": int(df[flag].sum()),
                "obs_share": float(df[flag].mean()),
                "mean_specificity_z_events": float(event.loc[event[flag].eq(1), "specificity_z"].mean()),
            }
        )
    # Mutually informative overlap table.
    overlap = []
    for left in TYPE_FLAGS:
        for right in TYPE_FLAGS:
            overlap.append(
                {
                    "left": TYPE_LABELS[left],
                    "right": TYPE_LABELS[right],
                    "event_overlap": int((event[left].eq(1) & event[right].eq(1)).sum()),
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(overlap)


def p_stars(p: float) -> str:
    if pd.isna(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def pretty(df: pd.DataFrame, cols: list[str] | None = None, digits: int = 4) -> str:
    if df.empty:
        return "_No rows._"
    out = df.copy()
    if cols is not None:
        out = out[cols]
    for col in out.select_dtypes(include=[np.number]).columns:
        out[col] = out[col].map(lambda x: round(float(x), digits) if pd.notna(x) else x)
    return out.to_markdown(index=False)


def add_display_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["coef_se"] = out.apply(
        lambda r: f"{r['coef']:.6f}{p_stars(r['p'])} ({r['se']:.6f})"
        if pd.notna(r.get("coef"))
        else "",
        axis=1,
    )
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    sample = load_sample()
    type_summary, overlap = summarize_types(sample)

    rows: list[dict[str, object]] = []
    focus_type_ai = [f"{TYPE_LABELS[f]}_ai" for f in TYPE_FLAGS]
    focus_spec_type_ai = ["spec_ai", *focus_type_ai]

    for ai_def in AI_DEFS:
        d = add_terms(sample, ai_def)

        # 1. Type-only slopes: which disclosure type has a different AIActive-peer slope?
        rows.extend(
            collect_rows(
                d,
                OUTCOME,
                [*focus_type_ai, *CONTROLS],
                STRONG_FE,
                model="type_x_ai_only",
                ai_def=ai_def,
                controls_note="PeerCAR[-10,-2] + PeerCAR[-20,-2]",
                focus_terms=focus_type_ai,
            )
        )

        # 2. Horse-race: does type coding absorb the existing Specificity_z x AIActive effect?
        rows.extend(
            collect_rows(
                d,
                OUTCOME,
                ["ai", "spec_ai", *focus_type_ai, *CONTROLS],
                STRONG_FE,
                model="specificity_plus_type_x_ai",
                ai_def=ai_def,
                controls_note="AIActive + PeerCAR[-10,-2] + PeerCAR[-20,-2]",
                focus_terms=focus_spec_type_ai,
            )
        )

        # 3. Type-specific specificity slopes: among each type, does specificity still matter?
        spec_by_type = [f"{TYPE_LABELS[f]}_spec_ai" for f in TYPE_FLAGS]
        rows.extend(
            collect_rows(
                d,
                OUTCOME,
                ["ai", *spec_by_type, *CONTROLS],
                STRONG_FE,
                model="type_specific_specificity_x_ai",
                ai_def=ai_def,
                controls_note="AIActive + PeerCAR[-10,-2] + PeerCAR[-20,-2]",
                focus_terms=spec_by_type,
            )
        )

    # 4. Event-level average peer effect without event FE. This is not the main
    # identification, but helps distinguish category validation from competitive
    # threat by showing whether supply-chain events move close peers on average.
    average_rows = collect_rows(
        sample,
        OUTCOME,
        [*TYPE_FLAGS, *CONTROLS],
        ["focal_industry_week", "peer_industry_week"],
        model="average_peer_effect_no_event_fe",
        ai_def="none",
        controls_note="PeerCAR[-10,-2] + PeerCAR[-20,-2]",
        focus_terms=TYPE_FLAGS,
    )

    results = pd.DataFrame(rows)
    avg = pd.DataFrame(average_rows)

    type_summary.to_csv(OUT_DIR / "disclosure_type_summary.csv", index=False)
    overlap.to_csv(OUT_DIR / "disclosure_type_overlap.csv", index=False)
    results.to_csv(OUT_DIR / "disclosure_type_aiactive_horserace.csv", index=False)
    avg.to_csv(OUT_DIR / "disclosure_type_average_peer_effect.csv", index=False)
    sample.to_csv(OUT_DIR / "analysis_sample_top5_with_disclosure_types.csv.gz", index=False, compression="gzip")

    res_disp = add_display_cols(results)
    avg_disp = add_display_cols(avg)

    doc = f"""# V7 Disclosure-Type Horse-Race

Date: 2026-05-27

## Purpose

This run splits focal GenAI disclosures into rough disclosure types and reruns the current Top5 peer-CAR framework.

Types:

- `own_impl`: focal firm describes its own GenAI implementation, deployment, product, model, or application.
- `supply_chain`: focal firm frames itself as exposed to AI/large-model demand through compute, data centers, semiconductors, optical modules, cooling, terminals, or data resources.
- `generic_attention`: focal firm gives generic AI/GenAI attention language without own implementation or supply-chain exposure.
- `denial_no_current`: focal firm denies current involvement or says it has no current GenAI business/cooperation.

Main interpretation target is not the average event effect, but `type × AIActivePeer` inside the existing peer-revaluation design.

## Sample and Type Counts

Top5 first focal GenAI event, announcement-cleaned, market-model `PeerCAR[0,+1]`.

{pretty(type_summary)}

## Type x AIActive Only

Outcome: `PeerCAR[0,+1]`. FE: `event_id + peer_industry_week`. SE: two-way clustered by `event_id + peer_code`. Controls: `PeerCAR[-10,-2] + PeerCAR[-20,-2]`.

{pretty(res_disp[res_disp["model"].eq("type_x_ai_only")], ["ai_def", "model", "term", "coef_se", "p", "nobs", "events", "peer_firms"])}

## Specificity plus Type x AIActive Horse-Race

This table asks whether disclosure-type interactions absorb the original `Specificity_z × AIActivePeer` effect.

{pretty(res_disp[res_disp["model"].eq("specificity_plus_type_x_ai")], ["ai_def", "model", "term", "coef_se", "p", "nobs", "events", "peer_firms"])}

## Type-Specific Specificity x AIActive

This table asks whether specificity matters more inside a particular disclosure type.

{pretty(res_disp[res_disp["model"].eq("type_specific_specificity_x_ai")], ["ai_def", "model", "term", "coef_se", "p", "nobs", "events", "peer_firms"])}

## Average Peer Effect without Event FE

This is descriptive only. It uses `focal_industry_week + peer_industry_week` FE, not event FE, because event FE would absorb focal-event type flags.

{pretty(avg_disp, ["term", "coef_se", "p", "nobs", "events", "peer_firms"])}

## Reading Rule

- If `own_impl_ai` is negative and stronger than `supply_chain_ai`, the evidence supports the competitive-risk interpretation.
- If `supply_chain` is positive in the no-event-FE table but not negative in `type × AIActive`, it supports category validation rather than competitive threat.
- If `spec_ai` remains negative after adding type interactions, the original specificity signal is not merely a disguised disclosure-type dummy.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")

    print(f"Wrote {DOC_PATH}")
    print(f"Wrote outputs under {OUT_DIR}")


if __name__ == "__main__":
    main()
