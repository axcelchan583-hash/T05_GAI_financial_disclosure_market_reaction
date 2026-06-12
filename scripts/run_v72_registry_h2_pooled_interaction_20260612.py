#!/usr/bin/env python3
"""Run H2 registry-verification pooled interaction tests.

This run uses firm-level administrative timing from v68/v70 as the main label.
Product-level strict labels are retained only as audit columns.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v23_cninfo_1055_peer_event_study_20260603 as pe  # noqa: E402
import run_v25_empirical_table_pack_20260604 as v25  # noqa: E402
import run_v53_v52_llm_empirical_tables_20260612 as v53  # noqa: E402


RUN_ID = "v72_registry_h2_pooled_interaction_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "132_v72_registry_h2_pooled_interaction_20260612.md"

PANEL_PATH = ROOT / "results/v56_v55_expanded_llm_empirical_tables_20260612/analysis_panel_with_returns_ai.csv.gz"
LABEL_PATH = ROOT / "results/v70_product_level_registry_labels_20260612/event_product_level_registry_labels.csv"

PREFERRED_METHOD = "liu_product_tfidf_same_industry_d_top10"
OUTCOMES = [
    ("peer_ar0_mm", "AR[0]"),
    ("peer_car_0_p1_mm", "CAR[0,+1]"),
    ("peer_car_m1_p1_mm", "CAR[-1,+1]"),
]
PRE_CONTROLS = ["peer_car_pre10_m2_mm", "peer_car_pre20_m2_mm"]
SUBGROUP_ORDER = ["all", "model_app", "own", "own_model_app", "out1_model_app"]


def clean(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def normal_p(z_value: float) -> float:
    return math.erfc(abs(z_value) / math.sqrt(2.0)) if math.isfinite(z_value) else math.nan


def md_table(df: pd.DataFrame, cols: list[str] | None = None, limit: int = 60) -> str:
    if df.empty:
        return "_No rows._"
    show = df.copy()
    if cols is not None:
        show = show[cols]
    show = show.head(limit).copy()
    for col in show.select_dtypes(include=[np.number]).columns:
        show[col] = show[col].map(lambda x: round(float(x), 6) if pd.notna(x) else x)
    rows = ["| " + " | ".join(show.columns) + " |", "|" + "|".join("---" for _ in show.columns) + "|"]
    for _, row in show.iterrows():
        rows.append("| " + " | ".join(clean(row[c]).replace("|", "\\|") for c in show.columns) + " |")
    return "\n".join(rows)


def load_panel() -> pd.DataFrame:
    usecols = [
        "sample_name",
        "event_type",
        "event_id",
        "event_key",
        "focal_code",
        "sec_name",
        "event_date",
        "announcement_title",
        "out",
        "mode",
        "layer",
        "realized",
        "method_variant",
        "method",
        "method_top_n",
        "time_valid_prior_year",
        "complete_clean_m1_p1",
        "peer_code",
        "peer_name",
        "peer_rank",
        "peer_similarity",
        "peer_industry_week",
        "focal_industry_week",
        "peer_ar0_mm",
        "peer_car_0_p1_mm",
        "peer_car_m1_p1_mm",
        "peer_car_pre10_m2_mm",
        "peer_car_pre20_m2_mm",
    ]
    panel = pd.read_csv(PANEL_PATH, usecols=usecols, dtype=str, low_memory=False)
    panel = panel[panel["method_variant"].eq(PREFERRED_METHOD)].copy()
    panel = panel[panel["time_valid_prior_year"].astype(str).eq("1")].copy()
    panel = panel[panel["complete_clean_m1_p1"].astype(str).eq("1")].copy()
    for col in [
        "peer_rank",
        "peer_similarity",
        "peer_ar0_mm",
        "peer_car_0_p1_mm",
        "peer_car_m1_p1_mm",
        "peer_car_pre10_m2_mm",
        "peer_car_pre20_m2_mm",
    ]:
        panel[col] = pd.to_numeric(panel[col], errors="coerce")
    return panel


def subgroup_mask(data: pd.DataFrame, subgroup: str) -> pd.Series:
    if subgroup == "all":
        return pd.Series(True, index=data.index)
    if subgroup == "model_app":
        return data["layer"].isin(["model", "app"])
    if subgroup == "own":
        return data["mode"].eq("own")
    if subgroup == "own_model_app":
        return data["mode"].eq("own") & data["layer"].isin(["model", "app"])
    if subgroup == "out1_model_app":
        return data["out"].astype(str).eq("1") & data["layer"].isin(["model", "app"])
    raise ValueError(subgroup)


def load_labels() -> pd.DataFrame:
    cols = [
        "sample_name",
        "event_id",
        "event_key",
        "focal_code",
        "event_date",
        "firm_level_verification_timing_v68",
        "firm_level_verification_type_v68",
        "registry_firm_product_count",
        "registry_products_at_event_count",
        "registry_products_later_count",
        "product_level_match",
        "product_level_verification_timing",
        "product_level_verification_type",
        "event_after_recent_censor_start",
    ]
    labels = pd.read_csv(LABEL_PATH, usecols=cols, dtype=str, low_memory=False).fillna("")
    labels = labels.drop_duplicates(["event_key"]).copy()
    for col in [
        "registry_firm_product_count",
        "registry_products_at_event_count",
        "registry_products_later_count",
        "product_level_match",
        "event_after_recent_censor_start",
    ]:
        labels[col] = pd.to_numeric(labels[col], errors="coerce").fillna(0).astype(int)
    return labels


def merge_inputs() -> pd.DataFrame:
    panel = load_panel()
    labels = load_labels()
    data = panel.merge(
        labels.drop(columns=["sample_name", "event_id", "focal_code", "event_date"], errors="ignore"),
        on="event_key",
        how="inner",
        validate="many_to_one",
    )
    data = data.rename(columns={"firm_level_verification_timing_v68": "verification_timing"})
    data["later_verified"] = data["verification_timing"].eq("later_verified").astype(int)
    data["never_verified"] = data["verification_timing"].eq("never_verified").astype(int)
    data["verified_at_event"] = data["verification_timing"].eq("verified_at_event").astype(int)
    data["peer_similarity_w"] = v25.winsorize(data["peer_similarity"], 0.01, 0.99)
    return data


def cell_counts(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    event_data = data.drop_duplicates(["sample_name", "event_key"]).copy()
    for subgroup in SUBGROUP_ORDER:
        sub = event_data[subgroup_mask(event_data, subgroup)].copy()
        if sub.empty:
            continue
        out = (
            sub
        .groupby(["sample_name", "event_type", "verification_timing"], dropna=False)
        .agg(
            events=("event_key", "nunique"),
            focal_firms=("focal_code", "nunique"),
            product_level_matched_events=("product_level_match", "sum"),
            recent_censored_events=("event_after_recent_censor_start", "sum"),
        )
        .reset_index()
        .sort_values(["sample_name", "event_type", "verification_timing"])
        )
        out.insert(0, "subgroup", subgroup)
        rows.append(out)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def grouped_means(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for sample in ["A_first_firm", "A_all"]:
        for subgroup in SUBGROUP_ORDER:
            base = data[data["sample_name"].eq(sample) & subgroup_mask(data, subgroup)].copy()
            base = base[base["verification_timing"].isin(["later_verified", "never_verified", "verified_at_event"])].copy()
            for timing, d in base.groupby("verification_timing", dropna=False):
                event_product_matches = int(d.drop_duplicates("event_key")["product_level_match"].sum())
                for outcome, label in OUTCOMES:
                    rows.append(
                        {
                            "sample_name": sample,
                            "subgroup": subgroup,
                            "verification_timing": timing,
                            "outcome": outcome,
                            "outcome_label": label,
                            "product_level_matched_events": event_product_matches,
                            **pe.clustered_mean(d, outcome),
                        }
                    )
    return pd.DataFrame(rows).sort_values(["sample_name", "outcome", "verification_timing"])


def fit_interaction(
    data: pd.DataFrame,
    sample_name: str,
    subgroup: str,
    outcome: str,
    with_pre: bool,
) -> tuple[dict[str, object] | None, np.ndarray | None, list[str]]:
    d = data[data["sample_name"].eq(sample_name) & subgroup_mask(data, subgroup)].copy()
    d = d[d["verification_timing"].isin(["later_verified", "never_verified"])].copy()
    d["sim_later"] = d["peer_similarity_w"] * d["later_verified"]
    d["sim_never"] = d["peer_similarity_w"] * d["never_verified"]
    xvars = ["sim_later", "sim_never"] + (PRE_CONTROLS if with_pre else [])
    need = [outcome, *xvars, "event_key", "peer_code", "focal_code", "peer_industry_week"]
    d = d.dropna(subset=need).copy()
    if len(d) < 80 or d["event_key"].nunique() < 8:
        return None, None, xvars
    dm = v25.absorb_frame(d, [outcome, *xvars], ["event_key", "peer_industry_week"])
    y = dm[outcome].to_numpy(dtype=float)
    x = dm[xvars].to_numpy(dtype=float)
    keep = np.nanstd(x, axis=0) > 1e-12
    if not keep.all():
        xvars = [var for var, ok in zip(xvars, keep) if ok]
        x = x[:, keep]
    if x.shape[1] == 0:
        return None, None, xvars
    bread = np.linalg.pinv(x.T @ x)
    beta = bread @ (x.T @ y)
    resid = y - x @ beta
    meat_event = v25.cluster_meat(x, resid, d["event_key"])
    meat_peer = v25.cluster_meat(x, resid, d["peer_code"])
    pair_group = d["event_key"].astype(str) + "|" + d["peer_code"].astype(str)
    meat_pair = v25.cluster_meat(x, resid, pair_group)
    cov = bread @ (meat_event + meat_peer - meat_pair) @ bread
    raw_y = d[outcome].to_numpy(dtype=float)
    within_tss = float(np.sum((y - y.mean()) ** 2))
    overall_tss = float(np.sum((raw_y - raw_y.mean()) ** 2))
    rss = float(np.sum(resid**2))
    result: dict[str, object] = {
        "sample_name": sample_name,
        "subgroup": subgroup,
        "outcome": outcome,
        "with_pre_controls": int(with_pre),
        "nobs": int(len(d)),
        "events": int(d["event_key"].nunique()),
        "focal_firms": int(d["focal_code"].nunique()),
        "peer_firms": int(d["peer_code"].nunique()),
        "within_r2": 1.0 - rss / within_tss if within_tss > 0 else math.nan,
        "overall_r2": 1.0 - rss / overall_tss if overall_tss > 0 else math.nan,
    }
    for i, var in enumerate(xvars):
        var_se = math.sqrt(float(cov[i, i])) if float(cov[i, i]) >= 0 else math.nan
        coef = float(beta[i])
        z_value = coef / var_se if var_se and var_se > 0 else math.nan
        result[f"{var}_coef"] = coef
        result[f"{var}_se"] = var_se
        result[f"{var}_z"] = z_value
        result[f"{var}_p"] = normal_p(z_value)
    if "sim_later" in xvars and "sim_never" in xvars:
        i = xvars.index("sim_later")
        j = xvars.index("sim_never")
        diff = float(beta[i] - beta[j])
        var = float(cov[i, i] + cov[j, j] - 2 * cov[i, j])
        se = math.sqrt(var) if var >= 0 else math.nan
        z_value = diff / se if se and se > 0 else math.nan
        result["later_minus_never_coef"] = diff
        result["later_minus_never_se"] = se
        result["later_minus_never_z"] = z_value
        result["later_minus_never_p"] = normal_p(z_value)
    return result, cov, xvars


def regressions(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for sample in ["A_first_firm", "A_all"]:
        for subgroup in SUBGROUP_ORDER:
            for outcome, label in OUTCOMES:
                for with_pre in [0, 1]:
                    res, _, _ = fit_interaction(data, sample, subgroup, outcome, bool(with_pre))
                    if res is not None:
                        res["outcome_label"] = label
                        rows.append(res)
    return pd.DataFrame(rows)


def product_audit(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for sample in ["A_first_firm", "A_all"]:
        for subgroup in SUBGROUP_ORDER:
            d0 = data[data["sample_name"].eq(sample) & subgroup_mask(data, subgroup)].copy()
            d0 = d0[d0["verification_timing"].isin(["later_verified", "verified_at_event", "never_verified"])].copy()
            d0["product_match_group"] = np.where(d0["product_level_match"].eq(1), "product_matched", "not_product_matched")
            for group, d in d0.groupby("product_match_group"):
                for outcome, label in OUTCOMES:
                    rows.append(
                        {
                            "sample_name": sample,
                            "subgroup": subgroup,
                            "product_match_group": group,
                            "outcome": outcome,
                            "outcome_label": label,
                            **pe.clustered_mean(d, outcome),
                        }
                    )
    return pd.DataFrame(rows).sort_values(["sample_name", "outcome", "product_match_group"])


def write_doc(counts: pd.DataFrame, means: pd.DataFrame, regs: pd.DataFrame, audit: pd.DataFrame) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    main_regs = regs[regs["outcome"].eq("peer_car_0_p1_mm")].copy()
    main_means = means[means["outcome"].eq("peer_car_0_p1_mm")].copy()
    audit_main = audit[audit["outcome"].eq("peer_car_0_p1_mm")].copy()
    lines = [
        "# v72 Registry H2 Pooled Interaction",
        "",
        "## Purpose",
        "",
        "- Tests the v3 design's H2 main claim: later-verified GenAI disclosures vs never-verified disclosures.",
        "- Uses firm-level administrative timing as the main label and product-level strict matches only as audit columns.",
        f"- Preferred peer method: `{PREFERRED_METHOD}`.",
        "- FE: event + peer industry-week. SE: two-way clustered by event and peer firm.",
        "- Subgroups: all, model/app only, own only, own model/app, and out=1 model/app.",
        "",
        "## Outputs",
        "",
        f"- `results/{RUN_ID}/analysis_panel_with_registry_labels.csv.gz`",
        f"- `results/{RUN_ID}/registry_h2_cell_counts.csv`",
        f"- `results/{RUN_ID}/registry_h2_grouped_means.csv`",
        f"- `results/{RUN_ID}/registry_h2_pooled_interactions.csv`",
        f"- `results/{RUN_ID}/registry_h2_product_audit_means.csv`",
        f"- `results/{RUN_ID}/{RUN_ID}.xlsx`",
        "",
        "## Cell Counts",
        "",
        md_table(counts[counts["sample_name"].isin(["A_first_firm", "A_all", "A_Dfw_stack"])], limit=80),
        "",
        "## CAR[0,+1] Group Means",
        "",
        md_table(
            main_means,
            [
                "sample_name",
                "subgroup",
                "verification_timing",
                "estimate",
                "se",
                "p",
                "nobs",
                "events",
                "peer_firms",
                "median",
                "positive_share",
                "product_level_matched_events",
            ],
            30,
        ),
        "",
        "## CAR[0,+1] Pooled Interaction",
        "",
        md_table(
            main_regs,
            [
                "sample_name",
                "subgroup",
                "with_pre_controls",
                "sim_later_coef",
                "sim_later_se",
                "sim_later_p",
                "sim_never_coef",
                "sim_never_se",
                "sim_never_p",
                "later_minus_never_coef",
                "later_minus_never_se",
                "later_minus_never_p",
                "nobs",
                "events",
                "peer_firms",
                "within_r2",
            ],
            20,
        ),
        "",
        "## Product-Level Audit Means",
        "",
        md_table(
            audit_main,
            ["sample_name", "subgroup", "product_match_group", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"],
            20,
        ),
        "",
        "## Interpretation",
        "",
        "H2 is not supported in this executable test. In the all-sample diagnostic means, `never_verified` is more negative than `later_verified`; restricting to model/app, own, own-model/app, or out=1 model/app weakens the never group but does not produce a significant later-vs-never gradient. The pooled interaction table also shows positive or near-zero `sim_later` coefficients and insignificant later-minus-never Wald tests. Product-level matched events are too few and are not more negative than unmatched events.",
        "",
        "Design implication: registry verification should not be the main identifying axis unless the label definition is changed. The current evidence says that `never_verified` is not a clean cheap-talk control because many credible GenAI announcements do not need CAC product filing or do not disclose product names in a matchable way.",
        "",
    ]
    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = merge_inputs()
    counts = cell_counts(data)
    means = grouped_means(data)
    regs = regressions(data)
    audit = product_audit(data)

    data.to_csv(OUT_DIR / "analysis_panel_with_registry_labels.csv.gz", index=False, compression="gzip")
    counts.to_csv(OUT_DIR / "registry_h2_cell_counts.csv", index=False, encoding="utf-8-sig")
    means.to_csv(OUT_DIR / "registry_h2_grouped_means.csv", index=False, encoding="utf-8-sig")
    regs.to_csv(OUT_DIR / "registry_h2_pooled_interactions.csv", index=False, encoding="utf-8-sig")
    audit.to_csv(OUT_DIR / "registry_h2_product_audit_means.csv", index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(OUT_DIR / f"{RUN_ID}.xlsx") as writer:
        counts.to_excel(writer, sheet_name="Cell_counts", index=False)
        means.to_excel(writer, sheet_name="Grouped_means", index=False)
        regs.to_excel(writer, sheet_name="Pooled_interactions", index=False)
        audit.to_excel(writer, sheet_name="Product_audit", index=False)

    write_doc(counts, means, regs, audit)
    print("run_id", RUN_ID)
    print("rows", len(data), "events", data["event_key"].nunique())
    if not regs.empty:
        show = regs[regs["outcome"].eq("peer_car_0_p1_mm")][
            [
                "sample_name",
                "subgroup",
                "with_pre_controls",
                "sim_later_coef",
                "sim_later_p",
                "sim_never_coef",
                "sim_never_p",
                "later_minus_never_coef",
                "later_minus_never_p",
                "events",
            ]
        ]
        print(show.to_string(index=False))
    print("doc", DOC_PATH)


if __name__ == "__main__":
    main()
