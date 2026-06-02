#!/usr/bin/env python3
"""Baseline table for the average peer reaction to GenAI disclosure events.

This run answers a narrow design question:

    Does the GenAI disclosure event itself have a stable average effect on
    product-market peers?

It is intentionally descriptive. The current paper's headline result remains
the within-event heterogeneity coefficient:

    Specificity_z x AIActivePeer -> PeerCAR[0,+1].

The tables here show why the average event-level peer effect is not a clean
main story: it mixes category validation and competitive-risk channels.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_v6_announcement_clean_checks_20260524 import base_clean_sample  # noqa: E402
from run_v6_identification_strengthening_checks_20260524 import fit_absorbed  # noqa: E402


DATE_TAG = "20260529"
OUT_DIR = ROOT / "results" / f"v11_genai_announcement_baseline_table_{DATE_TAG}"
DOC_PATH = ROOT / "docs" / "empirical_runs" / f"66_v11_genai_announcement_baseline_table_{DATE_TAG}.md"

OUTCOME = "peer_car_0_p1_mm"
PREWINDOW_CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
STRONG_FE = ["event_id", "peer_industry_week"]

FROZEN_TOP5 = (
    ROOT / "results" / "v6_focal_good_news_pretrend_checks_20260525" / "analysis_sample_top5.csv.gz"
)
TRUE_ANN_PANEL = (
    ROOT
    / "results"
    / "v6_announcement_clean_checks_20260524"
    / "true_peer_market_model_car_panel_with_ann_flags.csv.gz"
)
PLACEBO_ANN_PANEL = (
    ROOT
    / "results"
    / "v6_announcement_clean_checks_20260524"
    / "placebo_peer_market_model_car_panel_with_ann_flags.csv.gz"
)
NON_GENAI_PANEL = (
    ROOT
    / "results"
    / "v6_identification_strengthening_20260524"
    / "non_genai_placebo_panel.csv.gz"
)
TYPE_PANEL = (
    ROOT
    / "results"
    / "v7_disclosure_type_horserace_20260527"
    / "analysis_sample_top5_with_disclosure_types.csv.gz"
)

TYPE_FLAGS = {
    "own_genai_implementation_regex": "own_impl",
    "ai_supply_chain_exposure": "supply_chain",
    "generic_ai_attention_regex": "generic_attention",
    "denial_no_current_regex": "denial_no_current",
}


def ensure_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def p_from_z(z: float) -> float:
    return 2 * (1 - stats.norm.cdf(abs(z))) if math.isfinite(z) else math.nan


def clustered_mean_test(
    data: pd.DataFrame,
    outcome: str,
    label: str,
    sample: str,
    cluster: str = "event_id + peer_code",
) -> dict[str, object]:
    d = data.dropna(subset=[outcome, "event_id", "peer_code"]).copy()
    y = d[outcome].astype(float).to_numpy()
    x = np.ones((len(d), 1))
    model = sm.OLS(y, x).fit()
    cov_two, _, _ = cov_cluster_2groups(
        model, pd.Categorical(d["event_id"]).codes, pd.Categorical(d["peer_code"]).codes
    )
    var = float(np.asarray(cov_two)[0, 0])
    se = math.sqrt(var) if var >= 0 else math.nan
    z = float(model.params[0] / se) if se and se > 0 else math.nan
    return {
        "test": label,
        "sample": sample,
        "outcome": outcome,
        "estimate": float(model.params[0]),
        "se": se,
        "z": z,
        "p": p_from_z(z),
        "nobs": int(model.nobs),
        "events": int(d["event_id"].nunique()),
        "peer_firms": int(d["peer_code"].nunique()),
        "cluster": cluster,
        "interpretation": "mean PeerCAR against zero",
    }


def add_display_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "estimate" in out.columns:
        out["coef_se"] = out.apply(
            lambda r: f"{r['estimate']:.6f}{stars(r['p'])} ({r['se']:.6f})"
            if pd.notna(r.get("estimate")) and pd.notna(r.get("se"))
            else "",
            axis=1,
        )
    elif "coef" in out.columns:
        out["coef_se"] = out.apply(
            lambda r: f"{r['coef']:.6f}{stars(r['p'])} ({r['se']:.6f})"
            if pd.notna(r.get("coef")) and pd.notna(r.get("se"))
            else "",
            axis=1,
        )
    return out


def stars(p: float) -> str:
    if pd.isna(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def markdown_table(df: pd.DataFrame, cols: list[str] | None = None, digits: int = 4) -> str:
    if df.empty:
        return "_No rows._"
    out = df.copy()
    if cols is not None:
        out = out[cols]
    for col in out.select_dtypes(include=[np.number]).columns:
        out[col] = out[col].map(lambda x: round(float(x), digits) if pd.notna(x) else x)
    return out.to_markdown(index=False)


def load_frozen_top5() -> pd.DataFrame:
    df = pd.read_csv(FROZEN_TOP5, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    df = ensure_numeric(
        df,
        [
            OUTCOME,
            "peer_car_m1_p1_mm",
            "specificity_z",
            "current_text_history",
            "ext_any",
            *PREWINDOW_CONTROLS,
        ],
    )
    return df[df["peer_rank"].le(5)].copy()


def clean_announcement_panel(path: Path, peer_group: str | None = None) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    df = ensure_numeric(
        df,
        [
            OUTCOME,
            "peer_car_m1_p1_mm",
            "peer_rank",
            "is_first_focal_event",
            "obs_peer_car_m1_p1_mm",
            "normal_trading_m1_p1",
            "no_limit_m1_p1",
            "alpha_mm",
            "beta_mm",
            "either_cleaning_ann",
            "specificity_z",
        ],
    )
    if peer_group is not None and "peer_group" in df.columns:
        df = df[df["peer_group"].eq(peer_group)].copy()
    df = df[df["peer_rank"].le(5)].copy()
    df = base_clean_sample(df)
    if "either_cleaning_ann" in df.columns:
        df = df[df["either_cleaning_ann"].eq(0)].copy()
    if "event_week" not in df.columns:
        df["date_0"] = pd.to_datetime(df["date_0"], errors="coerce")
        df["event_week"] = df["date_0"].dt.strftime("%Y-%U")
    if "peer_industry_week" not in df.columns:
        df["peer_industry_week"] = df["peer_industry_d"].fillna("UNKNOWN").astype(str) + "|" + df[
            "event_week"
        ].fillna("")
    return df


def run_top5_vs_placebo() -> pd.DataFrame:
    true = clean_announcement_panel(TRUE_ANN_PANEL)
    true = true[true["peer_rank"].le(5)].copy()
    true["true_top5"] = 1.0

    placebo = pd.read_csv(PLACEBO_ANN_PANEL, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    rows: list[dict[str, object]] = []
    for group in ["low_similarity_same_industry", "random_same_industry"]:
        control = placebo[placebo["peer_group"].eq(group)].copy()
        tmp_path_df = ensure_numeric(
            control,
            [
                OUTCOME,
                "peer_rank",
                "is_first_focal_event",
                "obs_peer_car_m1_p1_mm",
                "normal_trading_m1_p1",
                "no_limit_m1_p1",
                "alpha_mm",
                "beta_mm",
                "either_cleaning_ann",
            ],
        )
        control = tmp_path_df[tmp_path_df["peer_rank"].le(5)].copy()
        control = base_clean_sample(control)
        control = control[control["either_cleaning_ann"].eq(0)].copy()
        if "event_week" not in control.columns:
            control["date_0"] = pd.to_datetime(control["date_0"], errors="coerce")
            control["event_week"] = control["date_0"].dt.strftime("%Y-%U")
        if "peer_industry_week" not in control.columns:
            control["peer_industry_week"] = control["peer_industry_d"].fillna("UNKNOWN").astype(str) + "|" + control[
                "event_week"
            ].fillna("")
        control["true_top5"] = 0.0

        combined = pd.concat([true, control], ignore_index=True, sort=False)
        for fe_name, fe_cols in [
            ("event_fe", ["event_id"]),
            ("event_fe_peer_industry_week_fe", STRONG_FE),
        ]:
            result_rows = fit_absorbed(
                combined,
                OUTCOME,
                ["true_top5"],
                fe_cols,
                model="top5_vs_placebo",
                term_focus="true_top5",
            )
            for row in result_rows:
                row.update(
                    {
                        "comparison": f"true_top5_vs_{group}",
                        "fe": fe_name,
                        "cluster": "event_id + peer_code",
                        "interpretation": "same GenAI event: Top5 peers minus placebo peers",
                    }
                )
                rows.append(row)
    return pd.DataFrame(rows)


def run_ai_active_average(frozen: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for ai_def in ["ext_any", "current_text_history"]:
        d = frozen.copy()
        d["ai"] = d[ai_def].fillna(0).astype(float)
        xvars = ["ai", *PREWINDOW_CONTROLS]
        for fe_name, fe_cols in [
            ("event_fe", ["event_id"]),
            ("event_fe_peer_industry_week_fe", STRONG_FE),
        ]:
            for row in fit_absorbed(
                d,
                OUTCOME,
                xvars,
                fe_cols,
                model="ai_active_average_without_specificity",
                term_focus="ai",
            ):
                row.update(
                    {
                        "ai_def": ai_def,
                        "fe": fe_name,
                        "controls": "PeerCAR[-10,-2] + PeerCAR[-20,-2]",
                        "cluster": "event_id + peer_code",
                        "interpretation": "same GenAI event: AI-active peers minus non-AI-active peers",
                    }
                )
                rows.append(row)
    return pd.DataFrame(rows)


def run_type_average() -> pd.DataFrame:
    df = pd.read_csv(TYPE_PANEL, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    df = ensure_numeric(df, [OUTCOME, *TYPE_FLAGS.keys(), "specificity_z", *PREWINDOW_CONTROLS])
    for col in TYPE_FLAGS:
        df[col] = df[col].fillna(0).astype(float)
    if "focal_industry_week" not in df.columns:
        df["event_week"] = pd.to_datetime(df["date_0"], errors="coerce").dt.strftime("%Y-%U")
        df["focal_industry_week"] = df["focal_industry_d"].fillna("UNKNOWN").astype(str) + "|" + df[
            "event_week"
        ].fillna("")
    rows: list[dict[str, object]] = []
    flag_cols = list(TYPE_FLAGS.keys())
    renamed = {v: k for k, v in TYPE_FLAGS.items()}

    # Separate event-level type regressions.
    for flag, label in TYPE_FLAGS.items():
        for fe_name, fe_cols in [
            ("event_week_peer_industry_week", ["event_week", "peer_industry_week"]),
            ("focal_industry_week_peer_industry_week", ["focal_industry_week", "peer_industry_week"]),
        ]:
            for row in fit_absorbed(
                df,
                OUTCOME,
                [flag, *PREWINDOW_CONTROLS],
                fe_cols,
                model="separate_disclosure_type_average",
                term_focus=flag,
            ):
                row.update(
                    {
                        "type": label,
                        "fe": fe_name,
                        "controls": "PeerCAR[-10,-2] + PeerCAR[-20,-2]",
                        "cluster": "event_id + peer_code",
                        "interpretation": "event-level disclosure type average peer effect",
                    }
                )
                rows.append(row)

    # Joint horse-race with specificity as another event-level characteristic.
    xvars = [*flag_cols, "specificity_z", *PREWINDOW_CONTROLS]
    for fe_name, fe_cols in [
        ("event_week_peer_industry_week", ["event_week", "peer_industry_week"]),
        ("focal_industry_week_peer_industry_week", ["focal_industry_week", "peer_industry_week"]),
    ]:
        for row in fit_absorbed(df, OUTCOME, xvars, fe_cols, model="joint_type_and_specificity_average"):
            term = row["term"]
            if term not in flag_cols and term != "specificity_z":
                continue
            row.update(
                {
                    "type": TYPE_FLAGS.get(term, term),
                    "fe": fe_name,
                    "controls": "all type flags + Specificity_z + PeerCAR[-10,-2] + PeerCAR[-20,-2]",
                    "cluster": "event_id + peer_code",
                    "interpretation": "joint event-level average peer effect",
                }
            )
            rows.append(row)
    return pd.DataFrame(rows)


def run_non_genai_pseudo() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(NON_GENAI_PANEL, dtype={"event_id": str, "focal_code": str, "peer_code": str})
    df = ensure_numeric(df, [OUTCOME, "specificity_z", "current_text_history"])
    df = df[df["peer_rank"].le(5)].copy()
    if "either_cleaning_ann" in df.columns:
        df = df[df["either_cleaning_ann"].eq(0)].copy()
    mean = pd.DataFrame(
        [
            clustered_mean_test(
                df,
                OUTCOME,
                label="non_genai_pseudo_top5_mean_peer_car",
                sample="same focal firms, non-GenAI IIP pseudo-events, Top5 peers",
            )
        ]
    )
    df["ai"] = df["current_text_history"].fillna(0).astype(float)
    df["spec_ai"] = df["specificity_z"] * df["ai"]
    rows = []
    for fe_name, fe_cols in [
        ("event_fe", ["event_id"]),
        ("event_fe_peer_industry_week_fe", STRONG_FE),
    ]:
        for row in fit_absorbed(
            df,
            OUTCOME,
            ["ai", "spec_ai"],
            fe_cols,
            model="non_genai_pseudo_specificity_x_text_history",
            term_focus="spec_ai",
        ):
            row.update(
                {
                    "fe": fe_name,
                    "ai_def": "current_text_history",
                    "cluster": "event_id + peer_code",
                    "interpretation": "pseudo-event specificity x prior GenAI disclosure history",
                }
            )
            rows.append(row)
    return mean, pd.DataFrame(rows)


def write_doc(
    mean_tests: pd.DataFrame,
    diff_tests: pd.DataFrame,
    ai_tests: pd.DataFrame,
    type_tests: pd.DataFrame,
    pseudo_mean: pd.DataFrame,
    pseudo_spec: pd.DataFrame,
) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    mean_disp = add_display_cols(mean_tests)
    diff_disp = add_display_cols(diff_tests)
    ai_disp = add_display_cols(ai_tests)
    type_disp = add_display_cols(type_tests)
    pseudo_mean_disp = add_display_cols(pseudo_mean)
    pseudo_spec_disp = add_display_cols(pseudo_spec)

    doc = f"""# V11 GenAI Announcement Baseline Table

Date: 2026-05-29

## Purpose

This run answers a narrow question:

```text
Does the GenAI disclosure event itself have a stable average effect on similar firms?
```

The answer is **no clean negative standalone story**. The average Top5 peer reaction is not reliably different from zero. When true Top5 peers are compared with low-similarity peers within the same event, the difference is positive rather than negative; the comparison with random same-industry peers is null. Event-level supply-chain exposure also has a positive average peer effect. This supports the current paper framing: the headline result should remain the conditional peer-revaluation coefficient `Specificity_z × AIActivePeer`, not an average GenAI-announcement effect.

## Input Samples

- Frozen headline Top5 sample: `{FROZEN_TOP5.relative_to(ROOT)}`
- True / placebo market-model CAR panels with announcement cleaning flags: `{TRUE_ANN_PANEL.relative_to(ROOT)}`, `{PLACEBO_ANN_PANEL.relative_to(ROOT)}`
- Disclosure-type coded Top5 sample: `{TYPE_PANEL.relative_to(ROOT)}`
- Non-GenAI pseudo-event panel: `{NON_GENAI_PANEL.relative_to(ROOT)}`

Outcome throughout: `PeerCAR[0,+1]` (`peer_car_0_p1_mm`).

## Panel A. Mean Peer CAR Against Zero

{markdown_table(mean_disp, ["test", "sample", "coef_se", "p", "nobs", "events", "peer_firms", "cluster"])}

## Panel B. Same-Event Top5 Peers Versus Placebo Peers

These regressions estimate `Top5 true product-market peer - placebo peer` within the same focal GenAI event.

{markdown_table(diff_disp, ["comparison", "fe", "coef_se", "p", "nobs", "events", "peer_firms", "cluster"])}

## Panel C. AI-Active Versus Non-AI-Active Peers Without Specificity

These regressions ask whether AI-active peers are, on average, more negative around GenAI disclosures before using `Specificity_z`.

{markdown_table(ai_disp, ["ai_def", "fe", "coef_se", "p", "nobs", "events", "peer_firms", "controls"])}

## Panel D. Event-Level Disclosure Type Average Effects

These rows do **not** use focal-event FE because the disclosure-type variables are event-level. They use calendar-week or focal-industry-week controls plus peer-industry-week FE and pre-window peer CAR controls.

{markdown_table(type_disp, ["model", "type", "fe", "coef_se", "p", "nobs", "events", "peer_firms", "controls"])}

## Panel E. Non-GenAI Pseudo-Events

Mean peer CAR around ordinary non-GenAI investor-interaction events:

{markdown_table(pseudo_mean_disp, ["test", "coef_se", "p", "nobs", "events", "peer_firms", "cluster"])}

Pseudo-event `Specificity_z × current_text_history` check:

{markdown_table(pseudo_spec_disp, ["fe", "coef_se", "p", "nobs", "events", "peer_firms", "cluster"])}

## Interpretation

1. The average Top5 peer CAR around focal GenAI disclosures is close to zero and statistically insignificant.
2. Same-event Top5-minus-low-similarity peer differences are positive, and Top5-minus-random same-industry differences are null. Neither pattern supports a negative average announcement-level peer effect.
3. AI-active peers are not uniformly more negative around GenAI disclosure events before using `Specificity_z`.
4. Disclosure type matters: AI supply-chain exposure shows a positive average peer effect, consistent with category validation rather than competitive-risk reassessment.
5. Non-GenAI pseudo-events do not reproduce the current `Specificity_z × AIActivePeer` negative pattern.

The current main paper should therefore say:

```text
The average peer reaction to GenAI disclosures is mixed and weak.
The robust pattern emerges in the conditional channel:
more specific focal GenAI disclosures are associated with more negative
short-window revaluation of AI-active close product-market peers.
```

"""
    DOC_PATH.write_text(doc, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    frozen = load_frozen_top5()
    true_clean = clean_announcement_panel(TRUE_ANN_PANEL)
    true_clean = true_clean[true_clean["peer_rank"].le(5)].copy()

    mean_tests = pd.DataFrame(
        [
            clustered_mean_test(
                frozen,
                OUTCOME,
                label="genai_true_top5_mean_peer_car_frozen",
                sample="first focal GenAI event, announcement-cleaned, Top5 product-market peers",
            ),
            clustered_mean_test(
                true_clean,
                OUTCOME,
                label="genai_true_top5_mean_peer_car_announcement_clean_panel",
                sample="first focal GenAI event, announcement-cleaned true Top5 panel",
            ),
        ]
    )

    diff_tests = run_top5_vs_placebo()
    ai_tests = run_ai_active_average(frozen)
    type_tests = run_type_average()
    pseudo_mean, pseudo_spec = run_non_genai_pseudo()

    mean_tests.to_csv(OUT_DIR / "panel_a_mean_peer_car.csv", index=False)
    diff_tests.to_csv(OUT_DIR / "panel_b_top5_vs_placebo.csv", index=False)
    ai_tests.to_csv(OUT_DIR / "panel_c_ai_active_without_specificity.csv", index=False)
    type_tests.to_csv(OUT_DIR / "panel_d_disclosure_type_average_effects.csv", index=False)
    pseudo_mean.to_csv(OUT_DIR / "panel_e_non_genai_pseudo_mean.csv", index=False)
    pseudo_spec.to_csv(OUT_DIR / "panel_e_non_genai_pseudo_specificity_x_history.csv", index=False)

    summary = pd.DataFrame(
        [
            {
                "output_dir": str(OUT_DIR.relative_to(ROOT)),
                "doc": str(DOC_PATH.relative_to(ROOT)),
                "frozen_rows": len(frozen),
                "frozen_events": frozen["event_id"].nunique(),
                "frozen_peer_firms": frozen["peer_code"].nunique(),
                "true_clean_rows": len(true_clean),
                "true_clean_events": true_clean["event_id"].nunique(),
            }
        ]
    )
    summary.to_csv(OUT_DIR / "run_summary.csv", index=False)

    write_doc(mean_tests, diff_tests, ai_tests, type_tests, pseudo_mean, pseudo_spec)
    print(f"Wrote {OUT_DIR}")
    print(f"Wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
