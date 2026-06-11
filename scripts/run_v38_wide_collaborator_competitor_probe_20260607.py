#!/usr/bin/env python3
"""Probe relationship-dependent revaluation around v36 GenAI events.

This run compares product-market competitors with broad cooperative linked
firms using the v36 first-event GenAI sample. It is a measurement/probe run,
not a final paper table.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.sandwich_covariance import cov_cluster, cov_cluster_2groups


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_v23_cninfo_1055_peer_event_study_20260603 as pe  # noqa: E402


RUN_ID = "v38_wide_collaborator_competitor_probe_20260607"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "102_v38_wide_collaborator_competitor_probe_20260607.md"

QIAN_ROOT = ROOT.parent / "T05-qian-supplier-replication-cn"
V36_FIRST_PATH = (
    QIAN_ROOT
    / "results"
    / "v36_candidate_x_supplier_replication_20260604"
    / "v36_candidate_x_first_event_per_firm.csv"
)

PEER_PANEL_PATH = (
    ROOT
    / "results"
    / "v26_v36_x_peer_retest_20260604"
    / "v36_peer_event_study_panel_light.csv.gz"
)

NETWORK_EDGES_PATH = (
    ROOT
    / "results"
    / "v3_supplier_spillover_sample_diagnostic"
    / "listed_supplier_edges_network.csv"
)
TOPFIVE_EDGES_PATH = (
    ROOT
    / "results"
    / "v3_supplier_spillover_sample_diagnostic"
    / "listed_supplier_edges_topfive.csv"
)

MAIN_SAMPLE = "combined_first_event_per_firm"
MAIN_COMPETITOR_METHOD = "liu_product_tfidf_same_industry_d_top10"
PLACEBO_METHOD = "placebo_low_similarity_top5"
OUTCOMES = [
    ("peer_ar_m1_mm", "AR[-1]"),
    ("peer_ar0_mm", "AR[0]"),
    ("peer_ar_p1_mm", "AR[+1]"),
    ("peer_car_0_p1_mm", "CAR[0,+1]"),
    ("peer_car_m1_p1_mm", "CAR[-1,+1]"),
]


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    if "." in text:
        text = text.split(".", 1)[0]
    digits = "".join(ch for ch in text if ch.isdigit())
    return digits.zfill(6)[-6:] if digits else ""


def clean_id(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return text[:-2] if text.endswith(".0") else text


def p_from_z(z_value: float) -> float:
    return math.erfc(abs(z_value) / math.sqrt(2)) if math.isfinite(z_value) else math.nan


def fmt_coef(value: float, p_value: float) -> str:
    if pd.isna(value):
        return ""
    stars = "***" if p_value < 0.01 else "**" if p_value < 0.05 else "*" if p_value < 0.10 else ""
    return f"{value:.4f}{stars}"


def md_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "_No rows._"
    show = df.head(max_rows).copy()
    for col in show.select_dtypes(include=[np.number]).columns:
        show[col] = show[col].map(lambda x: round(float(x), 6) if pd.notna(x) else x)
    cols = list(show.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, row in show.iterrows():
        vals = ["" if pd.isna(row[c]) else str(row[c]).replace("|", "\\|") for c in cols]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def load_v36_first_events() -> pd.DataFrame:
    events = pd.read_csv(V36_FIRST_PATH, dtype=str, low_memory=False)
    events["sample_name"] = MAIN_SAMPLE
    events["event_id"] = events["event_id"].map(clean_id)
    events["event_key"] = events["sample_name"] + "::" + events["event_id"]
    events["focal_code"] = events["focal_code"].map(code6)
    events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce")
    events["event_year"] = events["event_date"].dt.year
    events = events[events["focal_code"].ne("") & events["event_date"].notna()].copy()
    return events


def load_edges(path: Path, edge_family: str) -> pd.DataFrame:
    edges = pd.read_csv(path, dtype=str, low_memory=False)
    edges["customer_code"] = edges["customer_code"].map(code6)
    edges["supplier_code"] = edges["supplier_code"].map(code6)
    edges["relation_year"] = pd.to_numeric(edges["year"], errors="coerce")
    edges["edge_family"] = edge_family
    edges["edge_source"] = edges.get("edge_source", edge_family)
    edges = edges[
        edges["customer_code"].ne("")
        & edges["supplier_code"].ne("")
        & edges["customer_code"].ne(edges["supplier_code"])
        & edges["relation_year"].notna()
    ].copy()
    return edges[["customer_code", "supplier_code", "relation_year", "edge_source", "edge_family"]].drop_duplicates()


def collapse_edges(edges: pd.DataFrame) -> pd.DataFrame:
    return (
        edges.groupby(["customer_code", "supplier_code", "relation_year"], as_index=False)
        .agg(
            edge_sources=("edge_source", lambda s: ";".join(sorted(set(s.astype(str))))),
            edge_families=("edge_family", lambda s: ";".join(sorted(set(s.astype(str))))),
        )
        .copy()
    )


def build_cooperative_links(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    edge_inputs = pd.concat(
        [
            load_edges(NETWORK_EDGES_PATH, "network"),
            load_edges(TOPFIVE_EDGES_PATH, "topfive"),
        ],
        ignore_index=True,
    )
    edges = collapse_edges(edge_inputs)

    supplier = events.merge(edges, left_on="focal_code", right_on="customer_code", how="left")
    supplier = supplier[supplier["supplier_code"].notna()].copy()
    supplier["relation_type"] = "supplier"
    supplier["related_code"] = supplier["supplier_code"].map(code6)

    customer = events.merge(edges, left_on="focal_code", right_on="supplier_code", how="left")
    customer = customer[customer["customer_code"].notna()].copy()
    customer["relation_type"] = "customer"
    customer["related_code"] = customer["customer_code"].map(code6)

    links = pd.concat([supplier, customer], ignore_index=True)
    links["edge_age"] = links["event_year"].astype(float) - links["relation_year"].astype(float)
    links = links[
        links["related_code"].ne("")
        & links["related_code"].ne(links["focal_code"])
        & links["edge_age"].between(1, 5)
    ].copy()
    links = links.sort_values(
        ["event_key", "related_code", "relation_type", "relation_year"],
        ascending=[True, True, True, False],
    )
    links = links.drop_duplicates(["event_key", "related_code", "relation_type"], keep="first").copy()
    keep = [
        "sample_name",
        "event_id",
        "event_key",
        "focal_code",
        "focal_name",
        "event_date",
        "event_year",
        "announcement_title",
        "auto_pdf_label",
        "candidate_row_type",
        "related_code",
        "relation_type",
        "relation_year",
        "edge_age",
        "edge_sources",
        "edge_families",
    ]
    for col in keep:
        if col not in links.columns:
            links[col] = ""
    direction = links[keep].copy()

    union = (
        direction.groupby(["sample_name", "event_id", "event_key", "focal_code", "related_code"], as_index=False)
        .agg(
            focal_name=("focal_name", "first"),
            event_date=("event_date", "first"),
            event_year=("event_year", "first"),
            announcement_title=("announcement_title", "first"),
            auto_pdf_label=("auto_pdf_label", "first"),
            candidate_row_type=("candidate_row_type", "first"),
            relation_type=("relation_type", lambda s: "cooperative_union"),
            relation_directions=("relation_type", lambda s: ";".join(sorted(set(s.astype(str))))),
            relation_year=("relation_year", "max"),
            edge_age=("edge_age", "min"),
            edge_sources=("edge_sources", lambda s: ";".join(sorted(set(";".join(s.astype(str)).split(";"))))),
            edge_families=("edge_families", lambda s: ";".join(sorted(set(";".join(s.astype(str)).split(";"))))),
        )
        .copy()
    )
    return direction.reset_index(drop=True), union.reset_index(drop=True)


def attach_returns(panel: pd.DataFrame, stock_model: pd.DataFrame) -> pd.DataFrame:
    if panel.empty:
        return panel.copy()
    out = panel.copy()
    out["peer_code"] = out["related_code"].map(code6)
    out = pe.attach_event_trading_dates(out, stock_model)
    out = pe.build_return_measures(out, stock_model)
    return out


def load_competitor_panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    cols = [
        "sample_name",
        "method_variant",
        "method",
        "method_top_n",
        "time_valid_prior_year",
        "event_id",
        "event_key",
        "focal_code",
        "sec_name",
        "event_date",
        "date_0",
        "auto_pdf_label",
        "candidate_row_type",
        "peer_code",
        "peer_name",
        "peer_rank",
        "peer_similarity",
        "complete_clean_m1_p1",
        "peer_ar_m1_mm",
        "peer_ar0_mm",
        "peer_ar_p1_mm",
        "peer_car_0_p1_mm",
        "peer_car_m1_p1_mm",
    ]
    panel = pd.read_csv(PEER_PANEL_PATH, usecols=cols, dtype=str, low_memory=False)
    for col in [
        "method_top_n",
        "time_valid_prior_year",
        "peer_rank",
        "peer_similarity",
        "complete_clean_m1_p1",
        "peer_ar_m1_mm",
        "peer_ar0_mm",
        "peer_ar_p1_mm",
        "peer_car_0_p1_mm",
        "peer_car_m1_p1_mm",
    ]:
        panel[col] = pd.to_numeric(panel[col], errors="coerce")
    panel["focal_code"] = panel["focal_code"].map(code6)
    panel["peer_code"] = panel["peer_code"].map(code6)
    panel["related_code"] = panel["peer_code"]
    panel["relation_type"] = "competitor"
    panel["relation_group"] = "competitor"
    main = panel[
        panel["sample_name"].eq(MAIN_SAMPLE)
        & panel["method_variant"].eq(MAIN_COMPETITOR_METHOD)
        & panel["time_valid_prior_year"].eq(1)
    ].copy()
    placebo = panel[
        panel["sample_name"].eq(MAIN_SAMPLE)
        & panel["method_variant"].eq(PLACEBO_METHOD)
    ].copy()
    placebo["relation_type"] = "placebo_low_similarity"
    placebo["relation_group"] = "placebo"
    return main, placebo


def standardize_relation_panel(df: pd.DataFrame, relation_group: str) -> pd.DataFrame:
    out = df.copy()
    out["relation_group"] = relation_group
    out["related_code"] = out["related_code"].map(code6)
    out["peer_code"] = out["related_code"]
    for col in ["sec_name", "focal_name"]:
        if col not in out.columns:
            out[col] = ""
    if "sec_name" not in out.columns or out["sec_name"].fillna("").eq("").all():
        out["sec_name"] = out.get("focal_name", "")
    keep = [
        "sample_name",
        "event_id",
        "event_key",
        "focal_code",
        "sec_name",
        "event_date",
        "date_0",
        "auto_pdf_label",
        "candidate_row_type",
        "related_code",
        "peer_code",
        "relation_type",
        "relation_group",
        "complete_clean_m1_p1",
        "peer_ar_m1_mm",
        "peer_ar0_mm",
        "peer_ar_p1_mm",
        "peer_car_0_p1_mm",
        "peer_car_m1_p1_mm",
    ]
    for col in keep:
        if col not in out.columns:
            out[col] = np.nan
    return out[keep].copy()


def clustered_mean(df: pd.DataFrame, outcome: str) -> dict[str, object]:
    d = df.dropna(subset=[outcome, "event_key", "related_code"]).copy()
    if d.empty:
        return {
            "mean": math.nan,
            "se": math.nan,
            "z": math.nan,
            "p": math.nan,
            "nobs": 0,
            "events": 0,
            "related_firms": 0,
            "median": math.nan,
            "positive_share": math.nan,
        }
    y = d[outcome].astype(float)
    estimate = float(y.mean())
    resid = y - estimate
    n = len(d)
    if d["event_key"].nunique() > 1 and d["related_code"].nunique() > 1:
        event_term = resid.groupby(d["event_key"]).sum().pow(2).sum()
        firm_term = resid.groupby(d["related_code"]).sum().pow(2).sum()
        pair_term = resid.groupby([d["event_key"], d["related_code"]]).sum().pow(2).sum()
        var = float((event_term + firm_term - pair_term) / (n * n))
        se = math.sqrt(var) if var >= 0 else math.nan
    else:
        se = float(y.std(ddof=1) / math.sqrt(n)) if n > 1 else math.nan
    z = float(estimate / se) if se and se > 0 else math.nan
    vals = y.to_numpy()
    return {
        "mean": estimate,
        "se": se,
        "z": z,
        "p": p_from_z(z),
        "nobs": int(n),
        "events": int(d["event_key"].nunique()),
        "related_firms": int(d["related_code"].nunique()),
        "median": float(np.nanmedian(vals)),
        "positive_share": float(np.mean(vals > 0)),
    }


def event_weighted_mean(df: pd.DataFrame, outcome: str) -> dict[str, object]:
    d = df.dropna(subset=[outcome, "event_key"]).copy()
    if d.empty:
        return {
            "event_weighted_mean": math.nan,
            "event_weighted_se": math.nan,
            "event_weighted_z": math.nan,
            "event_weighted_p": math.nan,
            "event_weighted_events": 0,
            "event_positive_share": math.nan,
        }
    event_means = d.groupby("event_key")[outcome].mean().astype(float)
    estimate = float(event_means.mean())
    se = float(event_means.std(ddof=1) / math.sqrt(len(event_means))) if len(event_means) > 1 else math.nan
    z = float(estimate / se) if se and se > 0 else math.nan
    return {
        "event_weighted_mean": estimate,
        "event_weighted_se": se,
        "event_weighted_z": z,
        "event_weighted_p": p_from_z(z),
        "event_weighted_events": int(len(event_means)),
        "event_positive_share": float((event_means > 0).mean()),
    }


def relation_event_study(panel: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    clean = panel[panel["complete_clean_m1_p1"].eq(1)].copy()
    for relation_type, d in clean.groupby("relation_type", dropna=False):
        for outcome, label in OUTCOMES:
            rows.append(
                {
                    "relation_type": relation_type,
                    "outcome": outcome,
                    "window": label,
                    **clustered_mean(d, outcome),
                    **event_weighted_mean(d, outcome),
                }
            )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["outcome", "relation_type"]).reset_index(drop=True)


def sample_flow(events: pd.DataFrame, direction: pd.DataFrame, union: pd.DataFrame, relation_panel: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "layer": "v36_first_events",
            "linked_rows": len(events),
            "events": events["event_key"].nunique(),
            "focal_firms": events["focal_code"].nunique(),
            "related_firms": np.nan,
            "clean_car0p1_rows": np.nan,
            "clean_car0p1_events": np.nan,
        }
    ]
    for name, df in [
        ("supplier_links_raw", direction[direction["relation_type"].eq("supplier")]),
        ("customer_links_raw", direction[direction["relation_type"].eq("customer")]),
        ("cooperative_union_raw", union),
    ]:
        rows.append(
            {
                "layer": name,
                "linked_rows": len(df),
                "events": df["event_key"].nunique(),
                "focal_firms": df["focal_code"].nunique(),
                "related_firms": df["related_code"].nunique(),
                "clean_car0p1_rows": np.nan,
                "clean_car0p1_events": np.nan,
            }
        )
    for relation_type, df in relation_panel.groupby("relation_type", dropna=False):
        clean = df[df["complete_clean_m1_p1"].eq(1) & df["peer_car_0_p1_mm"].notna()]
        rows.append(
            {
                "layer": f"{relation_type}_returns",
                "linked_rows": len(df),
                "events": df["event_key"].nunique(),
                "focal_firms": df["focal_code"].nunique(),
                "related_firms": df["related_code"].nunique(),
                "clean_car0p1_rows": len(clean),
                "clean_car0p1_events": clean["event_key"].nunique(),
            }
        )
    return pd.DataFrame(rows)


def prepare_stacked_panels(competitor: pd.DataFrame, union: pd.DataFrame, direction: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    comp = standardize_relation_panel(competitor, "competitor")
    coop_union = standardize_relation_panel(union, "cooperative")
    coop_direction = standardize_relation_panel(direction, "cooperative")

    coop_keys = set(zip(coop_union["event_key"], coop_union["related_code"]))
    comp_no_overlap = comp[
        ~pd.Series(list(zip(comp["event_key"], comp["related_code"])), index=comp.index).isin(coop_keys)
    ].copy()

    stack_union = pd.concat([comp_no_overlap, coop_union], ignore_index=True)
    stack_union["cooperative"] = stack_union["relation_group"].eq("cooperative").astype(int)

    direction_flags = (
        coop_direction.groupby(["event_key", "related_code"], as_index=False)
        .agg(
            is_supplier=("relation_type", lambda s: int("supplier" in set(s.astype(str)))),
            is_customer=("relation_type", lambda s: int("customer" in set(s.astype(str)))),
        )
    )
    coop_collapsed = (
        coop_direction.sort_values(["event_key", "related_code", "relation_type"])
        .drop_duplicates(["event_key", "related_code"], keep="first")
        .drop(columns=["relation_type"], errors="ignore")
        .merge(direction_flags, on=["event_key", "related_code"], how="left")
    )
    coop_collapsed["relation_type"] = "cooperative_direction"
    coop_collapsed["relation_group"] = "cooperative"
    comp2 = comp_no_overlap.copy()
    comp2["is_supplier"] = 0
    comp2["is_customer"] = 0
    stack_direction = pd.concat([comp2, coop_collapsed], ignore_index=True)
    stack_direction["cooperative"] = stack_direction["relation_group"].eq("cooperative").astype(int)

    overlap = pd.DataFrame(
        [
            {
                "metric": "competitor_rows_before_overlap_drop",
                "value": len(comp),
            },
            {
                "metric": "competitor_event_firm_overlaps_with_coop",
                "value": len(comp) - len(comp_no_overlap),
            },
            {
                "metric": "competitor_rows_after_overlap_drop",
                "value": len(comp_no_overlap),
            },
            {
                "metric": "cooperative_union_rows",
                "value": len(coop_union),
            },
        ]
    )
    return stack_union, stack_direction, overlap


def fit_event_fe(df: pd.DataFrame, outcome: str, regressors: list[str], sample_name: str) -> pd.DataFrame:
    cols = [outcome, "event_key", "related_code", *regressors]
    d = df[df["complete_clean_m1_p1"].eq(1)].dropna(subset=cols).copy()
    if d.empty:
        return pd.DataFrame()
    # Event FE only identifies regressors within events with variation.
    nunique_by_event = d.groupby("event_key")[regressors].nunique(dropna=True)
    keep_events = nunique_by_event[nunique_by_event.gt(1).any(axis=1)].index
    d = d[d["event_key"].isin(keep_events)].copy()
    if d.empty:
        return pd.DataFrame()

    rhs = " + ".join(regressors + ["C(event_key)"])
    model = smf.ols(f"{outcome} ~ {rhs}", data=d).fit()

    try:
        cov_event = cov_cluster(model, d["event_key"])
    except Exception:
        cov_event = model.cov_params().to_numpy()
    try:
        event_group = pd.factorize(d["event_key"])[0]
        related_group = pd.factorize(d["related_code"])[0]
        cov_both = cov_cluster_2groups(model, event_group, related_group)[0]
    except Exception:
        cov_both = cov_event

    rows = []
    params = model.params
    names = list(params.index)
    for reg in regressors:
        if reg not in params.index:
            continue
        idx = names.index(reg)
        coef = float(params[reg])
        se_event = math.sqrt(cov_event[idx, idx]) if cov_event[idx, idx] >= 0 else math.nan
        z_event = coef / se_event if se_event and se_event > 0 else math.nan
        se_tw = math.sqrt(cov_both[idx, idx]) if cov_both[idx, idx] >= 0 else math.nan
        z_tw = coef / se_tw if se_tw and se_tw > 0 else math.nan
        rows.append(
            {
                "sample": sample_name,
                "outcome": outcome,
                "regressor": reg,
                "coef": coef,
                "se_event_cluster": se_event,
                "p_event_cluster": p_from_z(z_event),
                "coef_event_fmt": fmt_coef(coef, p_from_z(z_event)),
                "se_two_way": se_tw,
                "p_two_way": p_from_z(z_tw),
                "coef_two_way_fmt": fmt_coef(coef, p_from_z(z_tw)),
                "nobs": int(len(d)),
                "events": int(d["event_key"].nunique()),
                "related_firms": int(d["related_code"].nunique()),
                "r2": float(model.rsquared),
            }
        )
    return pd.DataFrame(rows)


def write_report(flow: pd.DataFrame, event_study: pd.DataFrame, regressions: pd.DataFrame, overlap: pd.DataFrame) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    main_car = event_study[event_study["window"].eq("CAR[0,+1]")].copy()
    main_car = main_car[
        [
            "relation_type",
            "mean",
            "se",
            "p",
            "nobs",
            "events",
            "related_firms",
            "positive_share",
            "event_weighted_mean",
            "event_weighted_p",
            "event_weighted_events",
        ]
    ].sort_values("relation_type")
    reg_show = regressions[
        [
            "sample",
            "outcome",
            "regressor",
            "coef_event_fmt",
            "p_event_cluster",
            "coef_two_way_fmt",
            "p_two_way",
            "nobs",
            "events",
            "related_firms",
            "r2",
        ]
    ].copy()
    text = f"""# v38 Wide Collaborator-Competitor Probe

Date: 2026-06-07

## Scope

This is the first data probe for the redesigned T05 question:

```text
Do concrete GenAI initiative disclosures trigger relationship-dependent market revaluation,
with product-market competitors reacting negatively and pre-existing cooperative linked firms
reacting more favorably?
```

This run uses only the v36 `first event per focal firm` sample and compares:

- main competitors: `{MAIN_COMPETITOR_METHOD}`;
- upstream listed suppliers from pre-event supply-chain edges;
- downstream listed customers from the same edge file, reversing the direction;
- supplier/customer union;
- low-similarity placebo peers, for a rough sanity check.

All cooperative links require relation year in event year minus 5 through event year minus 1.

## Sample Flow

{md_table(flow, max_rows=80)}

## CAR[0,+1] by Relation Type

{md_table(main_car, max_rows=80)}

## Stacked Event-FE Regressions

Baseline group is product-market competitors. Competitor event-firm rows that also appear in the cooperative union are removed from the competitor baseline.

{md_table(reg_show, max_rows=80)}

## Competitor-Cooperative Overlap

{md_table(overlap, max_rows=20)}

## Reading

- The key weak-form test is whether `cooperative > competitor` in the stacked event-FE regression.
- Absolute positive cooperative CAR is a stronger condition and should not be assumed ex ante.
- If supplier/customer union is not positive but the stacked coefficient is positive, the result can still support relation-dependent revaluation.
- If neither absolute cooperative CAR nor relative stacked difference survives, keep the paper on the conservative competitor-negative path.

## Output Files

- `results/{RUN_ID}/sample_flow.csv`
- `results/{RUN_ID}/relation_event_study.csv`
- `results/{RUN_ID}/stacked_regressions.csv`
- `results/{RUN_ID}/relation_panel.csv.gz`
- `results/{RUN_ID}/stack_union_panel.csv.gz`
- `results/{RUN_ID}/stack_direction_panel.csv.gz`
"""
    DOC_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    events = load_v36_first_events()
    print(f"events: {len(events):,}, focal firms: {events['focal_code'].nunique():,}")

    direction_links, union_links = build_cooperative_links(events)
    print(
        "cooperative links:",
        f"direction={len(direction_links):,}",
        f"union={len(union_links):,}",
        f"events={union_links['event_key'].nunique():,}",
    )

    stock_model = pe.load_stock_model()
    direction_returns = attach_returns(direction_links, stock_model)
    union_returns = attach_returns(union_links, stock_model)
    print(
        "cooperative nonmissing CAR[0,+1] before clean filters:",
        int(direction_returns["peer_car_0_p1_mm"].notna().sum()) if not direction_returns.empty else 0,
        int(union_returns["peer_car_0_p1_mm"].notna().sum()) if not union_returns.empty else 0,
    )
    print(
        "cooperative clean CAR[0,+1]:",
        int(
            (
                direction_returns["complete_clean_m1_p1"].eq(1)
                & direction_returns["peer_car_0_p1_mm"].notna()
            ).sum()
        )
        if not direction_returns.empty
        else 0,
        int(
            (
                union_returns["complete_clean_m1_p1"].eq(1)
                & union_returns["peer_car_0_p1_mm"].notna()
            ).sum()
        )
        if not union_returns.empty
        else 0,
    )

    competitor, placebo = load_competitor_panel()
    relation_parts = [
        standardize_relation_panel(competitor, "competitor"),
        standardize_relation_panel(placebo, "placebo"),
        standardize_relation_panel(direction_returns, "cooperative"),
        standardize_relation_panel(union_returns, "cooperative"),
    ]
    relation_panel = pd.concat(relation_parts, ignore_index=True)

    stack_union, stack_direction, overlap = prepare_stacked_panels(competitor, union_returns, direction_returns)

    flow = sample_flow(events, direction_links, union_links, relation_panel)
    event_study = relation_event_study(relation_panel)

    regs = []
    for outcome in ["peer_ar0_mm", "peer_car_0_p1_mm", "peer_car_m1_p1_mm"]:
        regs.append(fit_event_fe(stack_union, outcome, ["cooperative"], "union_vs_competitor"))
        regs.append(fit_event_fe(stack_direction, outcome, ["is_supplier", "is_customer"], "supplier_customer_vs_competitor"))
    regressions = pd.concat([r for r in regs if not r.empty], ignore_index=True) if regs else pd.DataFrame()

    flow.to_csv(OUT_DIR / "sample_flow.csv", index=False, encoding="utf-8-sig")
    event_study.to_csv(OUT_DIR / "relation_event_study.csv", index=False, encoding="utf-8-sig")
    regressions.to_csv(OUT_DIR / "stacked_regressions.csv", index=False, encoding="utf-8-sig")
    overlap.to_csv(OUT_DIR / "competitor_cooperative_overlap.csv", index=False, encoding="utf-8-sig")
    relation_panel.to_csv(OUT_DIR / "relation_panel.csv.gz", index=False)
    stack_union.to_csv(OUT_DIR / "stack_union_panel.csv.gz", index=False)
    stack_direction.to_csv(OUT_DIR / "stack_direction_panel.csv.gz", index=False)

    write_report(flow, event_study, regressions, overlap)
    car = event_study[event_study["window"].eq("CAR[0,+1]")]
    print(car[["relation_type", "mean", "p", "nobs", "events", "related_firms", "event_weighted_mean", "event_weighted_p"]].to_string(index=False))
    print(regressions[["sample", "outcome", "regressor", "coef", "p_event_cluster", "p_two_way", "nobs", "events"]].to_string(index=False))
    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
