#!/usr/bin/env python3
"""Grouped FactSet relationship results based on v42 extracted links."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_v38_wide_collaborator_competitor_probe_20260607 as v38  # noqa: E402


RUN_ID = "v43_factset_grouped_relationship_results_20260607"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "107_v43_factset_grouped_relationship_results_20260607.md"

V42_DIR = ROOT / "results" / "v42_factset_relationship_probe_20260607"
V42_LINKS = V42_DIR / "factset_event_relationship_links.csv"

MAIN_TYPES = [
    "factset_competitor",
    "factset_upstream_supplier",
    "factset_downstream_customer",
    "factset_partner_high_confidence",
    "factset_partner_investment",
    "factset_partner_all",
    "factset_relationship_union",
]


def md_table(df: pd.DataFrame, max_rows: int = 100) -> str:
    return v38.md_table(df, max_rows=max_rows)


def p_from_z(z_value: float) -> float:
    return math.erfc(abs(z_value) / math.sqrt(2)) if math.isfinite(z_value) else math.nan


def collapse_subset(links: pd.DataFrame, mask: pd.Series, relation_type: str, relation_group: str) -> pd.DataFrame:
    d = links[mask].copy()
    if d.empty:
        return d
    d["relation_start"] = pd.to_datetime(d["relation_start"], errors="coerce")
    d["relation_end"] = pd.to_datetime(d["relation_end"], errors="coerce")
    d = d.sort_values(
        ["event_key", "related_code", "relation_start", "relation_end"],
        ascending=[True, True, False, False],
    )
    d = d.drop_duplicates(["event_key", "related_code"], keep="first").copy()
    d["relation_type"] = relation_type
    d["relation_group"] = relation_group
    return d.reset_index(drop=True)


def build_grouped_links(links: pd.DataFrame) -> pd.DataFrame:
    parts = [
        collapse_subset(links, links["relation_type"].eq("factset_competitor"), "factset_competitor", "competitor"),
        collapse_subset(links, links["relation_type"].eq("factset_upstream_supplier"), "factset_upstream_supplier", "supplier"),
        collapse_subset(links, links["relation_type"].eq("factset_downstream_customer"), "factset_downstream_customer", "customer"),
        collapse_subset(links, links["relation_group"].eq("partner_high_confidence"), "factset_partner_high_confidence", "partner_high_confidence"),
        collapse_subset(links, links["rel_type"].isin(["PARTNER-INVESTO", "PARTNER-EINVEST"]), "factset_partner_investment", "partner_investment"),
        collapse_subset(links, links["relation_family"].eq("partner"), "factset_partner_all", "partner_all"),
    ]
    union = collapse_subset(links, pd.Series(True, index=links.index), "factset_relationship_union", "factset_union")
    parts.append(union)
    return pd.concat([p for p in parts if p is not None and not p.empty], ignore_index=True)


def sample_flow(grouped: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for relation_type, d in grouped.groupby("relation_type", dropna=False):
        r = returns[returns["relation_type"].eq(relation_type)].copy()
        clean = r[r["complete_clean_m1_p1"].eq(1) & r["peer_car_0_p1_mm"].notna()]
        rows.append(
            {
                "relation_type": relation_type,
                "linked_rows": len(d),
                "events": d["event_key"].nunique(),
                "focal_firms": d["focal_code"].nunique(),
                "related_firms": d["related_code"].nunique(),
                "clean_car0p1_rows": len(clean),
                "clean_car0p1_events": clean["event_key"].nunique(),
                "clean_related_firms": clean["related_code"].nunique(),
            }
        )
    return pd.DataFrame(rows).sort_values("relation_type").reset_index(drop=True)


def coverage_table(grouped: pd.DataFrame) -> pd.DataFrame:
    return (
        grouped.groupby(["relation_group", "relation_type"], as_index=False)
        .agg(
            rows=("related_code", "size"),
            events=("event_key", "nunique"),
            focal_firms=("focal_code", "nunique"),
            related_firms=("related_code", "nunique"),
            rel_types=("rel_type", lambda s: ";".join(sorted(set(s.astype(str))))),
        )
        .sort_values(["relation_group", "rows"], ascending=[True, False])
        .reset_index(drop=True)
    )


def standardize_plus(df: pd.DataFrame, relation_group: str) -> pd.DataFrame:
    out = v38.standardize_relation_panel(df, relation_group)
    for col in [
        "related_factset_id",
        "related_factset_name",
        "rel_type",
        "relation_family",
        "focal_side",
        "relation_start",
        "relation_end",
        "relation_year",
        "relation_age_days",
        "revenue_percent",
        "percent_estimated",
        "match_evidence",
    ]:
        if col in df.columns and len(df) == len(out):
            out[col] = df[col].values
        elif col not in out.columns:
            out[col] = np.nan
    return out


def prepare_stack(product_competitor: pd.DataFrame, factset_returns: pd.DataFrame, relation_types: list[str]) -> pd.DataFrame:
    comp = standardize_plus(product_competitor, "product_competitor")
    comp["stack_relation"] = "product_competitor"
    parts = [comp]
    for relation_type in relation_types:
        d = factset_returns[factset_returns["relation_type"].eq(relation_type)].copy()
        if d.empty:
            continue
        s = standardize_plus(d, "factset")
        s["stack_relation"] = relation_type
        parts.append(s)
    stack = pd.concat(parts, ignore_index=True)
    factset_keys = set(
        zip(
            stack.loc[stack["stack_relation"].ne("product_competitor"), "event_key"],
            stack.loc[stack["stack_relation"].ne("product_competitor"), "related_code"],
        )
    )
    overlap = pd.Series(list(zip(stack["event_key"], stack["related_code"])), index=stack.index).isin(factset_keys)
    stack = stack[~(stack["stack_relation"].eq("product_competitor") & overlap)].copy()
    for relation_type in relation_types:
        stack[f"is_{relation_type}"] = stack["stack_relation"].eq(relation_type).astype(int)
    return stack.reset_index(drop=True)


def fit_stack(stack: pd.DataFrame, relation_types: list[str], sample: str) -> pd.DataFrame:
    regressors = [f"is_{t}" for t in relation_types if f"is_{t}" in stack.columns]
    rows = []
    for outcome, _ in v38.OUTCOMES:
        rows.append(v38.fit_event_fe(stack, outcome, regressors, sample))
    return pd.concat([r for r in rows if not r.empty], ignore_index=True) if rows else pd.DataFrame()


def write_report(flow: pd.DataFrame, coverage: pd.DataFrame, event_study: pd.DataFrame, regressions: pd.DataFrame) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    car = event_study[event_study["window"].eq("CAR[0,+1]")].copy()
    text = f"""# v43 FactSet Grouped Relationship Results

Date: 2026-06-07

## Scope

This run reuses v42 FactSet A-share relationship links and collapses granular partner subtypes into interpretable groups. It does not rescan the FactSet 20GB relationship file.

Grouped relation types:

- `factset_competitor`
- `factset_upstream_supplier`
- `factset_downstream_customer`
- `factset_partner_high_confidence`: non-investment operational partner types such as research collaboration, joint venture, technology, licensing, distribution, manufacturing, and marketing.
- `factset_partner_investment`: `PARTNER-INVESTO` and `PARTNER-EINVEST`.
- `factset_partner_all`
- `factset_relationship_union`

## Sample Flow

{md_table(flow, max_rows=100)}

## Coverage

{md_table(coverage, max_rows=100)}

## CAR[0,+1] by Grouped Relation Type

{md_table(
        car[
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
        ]
        if not car.empty
        else car,
        max_rows=100,
    )}

## Stacked Event-FE Regressions

Baseline is the existing product-market competitor panel, with overlapping product-competitor event-firm rows removed.

{md_table(
        regressions[
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
        ]
        if not regressions.empty
        else regressions,
        max_rows=120,
    )}

## Reading

- FactSet competitor is strongly negative in the raw event-study mean.
- FactSet supplier/customer are much larger than CSMAR supply-chain links but do not show a positive absolute CAR in this first pass.
- Investment-type partners show the clearest positive relative coefficient versus product-market competitors, but this is not the same as operational GenAI collaboration.
- High-confidence operational partners are not yet positive; they need manual validation or a narrower theory before becoming a main collaborator Y.

## Output Files

- `results/{RUN_ID}/factset_grouped_links.csv`
- `results/{RUN_ID}/factset_grouped_relation_panel.csv.gz`
- `results/{RUN_ID}/factset_grouped_event_study.csv`
- `results/{RUN_ID}/factset_grouped_stacked_regressions.csv`
"""
    DOC_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    links = pd.read_csv(V42_LINKS, dtype=str, low_memory=False)
    links["event_date"] = pd.to_datetime(links["event_date"], errors="coerce")
    for col in ["relation_start", "relation_end"]:
        links[col] = pd.to_datetime(links[col], errors="coerce")
    grouped = build_grouped_links(links)

    stock_model = v38.pe.load_stock_model()
    returns = v38.attach_returns(grouped, stock_model)
    relation_panel = standardize_plus(returns, "factset_grouped")
    flow = sample_flow(grouped, returns)
    coverage = coverage_table(grouped)
    event_study = v38.relation_event_study(relation_panel)

    product_competitor, _ = v38.load_competitor_panel()
    core_types = [
        "factset_competitor",
        "factset_upstream_supplier",
        "factset_downstream_customer",
        "factset_partner_high_confidence",
        "factset_partner_investment",
    ]
    stack_core = prepare_stack(product_competitor, returns, core_types)
    reg_core = fit_stack(stack_core, core_types, "core_grouped_relations_vs_product_competitor")

    separate = []
    for relation_type in ["factset_partner_all", "factset_relationship_union"]:
        st = prepare_stack(product_competitor, returns, [relation_type])
        separate.append(fit_stack(st, [relation_type], f"{relation_type}_vs_product_competitor"))
    regressions = pd.concat([reg_core, *[r for r in separate if not r.empty]], ignore_index=True)

    grouped.to_csv(OUT_DIR / "factset_grouped_links.csv", index=False, encoding="utf-8-sig")
    flow.to_csv(OUT_DIR / "sample_flow.csv", index=False, encoding="utf-8-sig")
    coverage.to_csv(OUT_DIR / "coverage.csv", index=False, encoding="utf-8-sig")
    event_study.to_csv(OUT_DIR / "factset_grouped_event_study.csv", index=False, encoding="utf-8-sig")
    regressions.to_csv(OUT_DIR / "factset_grouped_stacked_regressions.csv", index=False, encoding="utf-8-sig")
    relation_panel.to_csv(OUT_DIR / "factset_grouped_relation_panel.csv.gz", index=False)
    stack_core.to_csv(OUT_DIR / "factset_core_stack_panel.csv.gz", index=False)

    write_report(flow, coverage, event_study, regressions)
    car = event_study[event_study["window"].eq("CAR[0,+1]")]
    print(car[["relation_type", "mean", "p", "nobs", "events", "related_firms", "event_weighted_mean", "event_weighted_p"]].to_string(index=False))
    print(regressions[regressions["outcome"].eq("peer_car_0_p1_mm")][["sample", "regressor", "coef", "p_event_cluster", "p_two_way", "nobs", "events"]].to_string(index=False))
    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
