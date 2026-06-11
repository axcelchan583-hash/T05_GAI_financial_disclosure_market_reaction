#!/usr/bin/env python3
"""Audit FactSet investment-linked partner effects around v36 GenAI events."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v38_wide_collaborator_competitor_probe_20260607 as v38  # noqa: E402


RUN_ID = "v47_factset_investment_partner_audit_20260608"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "111_v47_factset_investment_partner_audit_20260608.md"
V43_DIR = ROOT / "results" / "v43_factset_grouped_relationship_results_20260607"


def stars(p: object) -> str:
    if p is None or pd.isna(p):
        return ""
    p = float(p)
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def fmt(value: object, digits: int = 4) -> str:
    if value is None or pd.isna(value):
        return ""
    return f"{float(value):.{digits}f}"


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
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


def investment_role(rel_type: str, focal_side: str) -> str:
    rel_type = str(rel_type)
    focal_side = str(focal_side)
    # FactSet methodology:
    # EINVEST: source company owns equity in target.
    # INVESTO: target entity owns equity in source company.
    if rel_type == "PARTNER-EINVEST" and focal_side == "source":
        return "investee_of_focal"
    if rel_type == "PARTNER-EINVEST" and focal_side == "target":
        return "investor_in_focal"
    if rel_type == "PARTNER-INVESTO" and focal_side == "source":
        return "investor_in_focal"
    if rel_type == "PARTNER-INVESTO" and focal_side == "target":
        return "investee_of_focal"
    return "other_investment_link"


def investment_direction_cn(role: str) -> str:
    if role == "investor_in_focal":
        return "关联方持有/投资焦点公司"
    if role == "investee_of_focal":
        return "焦点公司持有/投资关联方"
    return "投资关系方向未分类"


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    links = pd.read_csv(V43_DIR / "factset_grouped_links.csv", low_memory=False)
    panel = pd.read_csv(V43_DIR / "factset_grouped_relation_panel.csv.gz", low_memory=False)
    link_meta_cols = [
        "event_key",
        "related_code",
        "rel_type",
        "focal_side",
        "announcement_title",
        "focal_name",
        "candidate_row_type",
        "auto_pdf_label",
    ]
    link_meta = links[[c for c in link_meta_cols if c in links.columns]].copy()
    link_meta["related_code"] = link_meta["related_code"].map(v38.code6)
    panel["related_code"] = panel["related_code"].map(v38.code6)
    panel = panel.merge(
        link_meta.drop_duplicates(["event_key", "related_code", "rel_type", "focal_side"]),
        on=["event_key", "related_code", "rel_type", "focal_side"],
        how="left",
        suffixes=("", "_from_link"),
    )
    for col in ["announcement_title", "focal_name", "candidate_row_type", "auto_pdf_label"]:
        alt = f"{col}_from_link"
        if alt in panel.columns:
            if col in panel.columns:
                panel[col] = panel[col].where(panel[col].notna() & panel[col].astype(str).ne(""), panel[alt])
            else:
                panel[col] = panel[alt]
            panel = panel.drop(columns=[alt])
    for df in [links, panel]:
        df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
        df["related_code"] = df["related_code"].map(v38.code6)
        df["focal_code"] = df["focal_code"].map(v38.code6)
        if "focal_name" not in df.columns:
            df["focal_name"] = df.get("sec_name", "")
        if "announcement_title" not in df.columns:
            df["announcement_title"] = ""
        df["investment_role"] = [investment_role(rt, side) for rt, side in zip(df["rel_type"], df["focal_side"])]
        df["investment_direction_cn"] = df["investment_role"].map(investment_direction_cn)
    links = links[links["relation_type"].eq("factset_partner_investment")].copy()
    panel = panel[panel["relation_type"].eq("factset_partner_investment")].copy()
    return links, panel


def sample_flow(links: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, df in [
        ("investment_linked_partner", links),
        ("investor_in_focal", links[links["investment_role"].eq("investor_in_focal")]),
        ("investee_of_focal", links[links["investment_role"].eq("investee_of_focal")]),
    ]:
        p = panel if label == "investment_linked_partner" else panel[panel["investment_role"].eq(label)]
        clean = p[p["complete_clean_m1_p1"].eq(1) & p["peer_car_0_p1_mm"].notna()].copy()
        rows.append(
            {
                "sample": label,
                "raw_relationship_rows": len(df),
                "raw_events": df["event_key"].nunique(),
                "raw_focal_firms": df["focal_code"].nunique(),
                "raw_related_firms": df["related_code"].nunique(),
                "clean_car0p1_rows": len(clean),
                "clean_car0p1_events": clean["event_key"].nunique(),
                "clean_related_firms": clean["related_code"].nunique(),
            }
        )
    return pd.DataFrame(rows)


def grouped_event_study(panel: pd.DataFrame) -> pd.DataFrame:
    parts = []
    base = panel.copy()
    base["relation_type"] = "investment_linked_partner"
    parts.append(base)
    for role in ["investor_in_focal", "investee_of_focal"]:
        d = panel[panel["investment_role"].eq(role)].copy()
        d["relation_type"] = role
        parts.append(d)
    for rel_type in sorted(panel["rel_type"].dropna().unique()):
        d = panel[panel["rel_type"].eq(rel_type)].copy()
        d["relation_type"] = rel_type
        parts.append(d)
    for combo, d in panel.groupby(["rel_type", "focal_side"], dropna=False):
        rel_type, focal_side = combo
        x = d.copy()
        x["relation_type"] = f"{rel_type}_{focal_side}"
        parts.append(x)
    stack = pd.concat(parts, ignore_index=True)
    return v38.relation_event_study(stack)


def event_level_contribution(panel: pd.DataFrame) -> pd.DataFrame:
    clean = panel[panel["complete_clean_m1_p1"].eq(1) & panel["peer_car_0_p1_mm"].notna()].copy()
    event = (
        clean.groupby(["event_key", "event_date", "focal_code", "focal_name", "announcement_title"], as_index=False)
        .agg(
            relationship_rows=("related_code", "size"),
            related_firms=("related_code", "nunique"),
            mean_car0p1=("peer_car_0_p1_mm", "mean"),
            max_car0p1=("peer_car_0_p1_mm", "max"),
            min_car0p1=("peer_car_0_p1_mm", "min"),
            positive_share=("peer_car_0_p1_mm", lambda x: float((x > 0).mean())),
            roles=("investment_role", lambda s: ";".join(sorted(set(s.astype(str))))),
            rel_types=("rel_type", lambda s: ";".join(sorted(set(s.astype(str))))),
            related_names=("related_factset_name", lambda s: "; ".join(list(dict.fromkeys(s.dropna().astype(str)))[:6])),
        )
        .sort_values("mean_car0p1", ascending=False)
    )
    event["rank_abs_contribution"] = event["mean_car0p1"].abs().rank(method="first", ascending=False).astype(int)
    return event


def leave_one_event_out(panel: pd.DataFrame) -> pd.DataFrame:
    clean = panel[panel["complete_clean_m1_p1"].eq(1) & panel["peer_car_0_p1_mm"].notna()].copy()
    rows = []
    for label, d in [
        ("investment_linked_partner", clean),
        ("investor_in_focal", clean[clean["investment_role"].eq("investor_in_focal")]),
        ("investee_of_focal", clean[clean["investment_role"].eq("investee_of_focal")]),
    ]:
        event_means = d.groupby("event_key")["peer_car_0_p1_mm"].mean().astype(float)
        base_mean = float(event_means.mean()) if len(event_means) else math.nan
        if len(event_means) <= 2:
            rows.append(
                {
                    "sample": label,
                    "events": len(event_means),
                    "base_event_weighted_mean": base_mean,
                    "loo_min_mean": math.nan,
                    "loo_max_mean": math.nan,
                    "loo_share_positive": math.nan,
                    "largest_positive_event": "",
                    "largest_negative_event": "",
                }
            )
            continue
        loo = []
        for key in event_means.index:
            loo.append((key, float(event_means.drop(index=key).mean())))
        loo_df = pd.DataFrame(loo, columns=["dropped_event_key", "loo_mean"])
        largest_pos = event_means.idxmax()
        largest_neg = event_means.idxmin()
        rows.append(
            {
                "sample": label,
                "events": len(event_means),
                "base_event_weighted_mean": base_mean,
                "loo_min_mean": float(loo_df["loo_mean"].min()),
                "loo_max_mean": float(loo_df["loo_mean"].max()),
                "loo_share_positive": float((loo_df["loo_mean"] > 0).mean()),
                "largest_positive_event": largest_pos,
                "largest_positive_event_mean": float(event_means.loc[largest_pos]),
                "largest_negative_event": largest_neg,
                "largest_negative_event_mean": float(event_means.loc[largest_neg]),
            }
        )
    return pd.DataFrame(rows)


def relationship_examples(panel: pd.DataFrame, n: int = 40) -> pd.DataFrame:
    clean = panel[panel["complete_clean_m1_p1"].eq(1) & panel["peer_car_0_p1_mm"].notna()].copy()
    cols = [
        "event_date",
        "focal_code",
        "focal_name",
        "related_code",
        "related_factset_name",
        "investment_role",
        "investment_direction_cn",
        "rel_type",
        "focal_side",
        "relation_start",
        "relation_age_days",
        "peer_car_0_p1_mm",
        "peer_ar0_mm",
        "peer_ar_p1_mm",
        "announcement_title",
        "match_evidence",
    ]
    show = clean.sort_values("peer_car_0_p1_mm", ascending=False).head(n // 2)
    show2 = clean.sort_values("peer_car_0_p1_mm", ascending=True).head(n // 2)
    out = pd.concat([show, show2], ignore_index=True)
    for col in cols:
        if col not in out.columns:
            out[col] = np.nan
    return out[cols].copy()


def write_doc(
    flow: pd.DataFrame,
    event_study: pd.DataFrame,
    loo: pd.DataFrame,
    top_events: pd.DataFrame,
    examples: pd.DataFrame,
) -> None:
    car = event_study[event_study["window"].eq("CAR[0,+1]")].copy()
    ar0 = event_study[event_study["window"].eq("AR[0]")].copy()
    key = car[car["relation_type"].isin(["investment_linked_partner", "investor_in_focal", "investee_of_focal"])]
    key_ar0 = ar0[ar0["relation_type"].isin(["investment_linked_partner", "investor_in_focal", "investee_of_focal"])]

    lines = [
        "# v47 FactSet Investment-Linked Partner Audit",
        "",
        "Date: 2026-06-08",
        "",
        "## Scope",
        "",
        "This run audits the FactSet `PARTNER-INVESTO` and `PARTNER-EINVEST` rows that produced a positive event-weighted CAR in v43.",
        "",
        "FactSet methodology guide definitions:",
        "",
        "- `PARTNER-EINVEST` / Equity Investment: the source company owns an equity stake in the target entity.",
        "- `PARTNER-INVESTO` / Investor: the target entity owns equity in the source company.",
        "",
        "Accordingly, relative to the focal GenAI discloser:",
        "",
        "- `investor_in_focal`: the listed related firm holds/invests in the focal firm.",
        "- `investee_of_focal`: the focal firm holds/invests in the listed related firm.",
        "",
        "## Sample Flow",
        "",
        md_table(flow),
        "",
        "## CAR[0,+1] by Direction",
        "",
        md_table(key),
        "",
        "## AR[0] by Direction",
        "",
        md_table(key_ar0),
        "",
        "## Leave-One-Event-Out Check",
        "",
        md_table(loo),
        "",
        "## Top Event-Level Means",
        "",
        md_table(top_events.sort_values("mean_car0p1", ascending=False).head(15)),
        "",
        "## Bottom Event-Level Means",
        "",
        md_table(top_events.sort_values("mean_car0p1", ascending=True).head(15)),
        "",
        "## High/Low Relationship Examples for Manual Validation",
        "",
        md_table(examples, max_rows=40),
        "",
        "## Reading",
        "",
        "- The positive investment-linked result is not obviously a pure direction story: both `investor_in_focal` and `investee_of_focal` have positive relationship-level mean CARs.",
        "- The event-weighted positive result should be treated as a promising second finding, not yet as final main evidence, because it needs manual validation of FactSet investment links and direction semantics in Chinese cases.",
        "- If retained, the safest label is `investment-linked partners`, not generic collaborators or operating partners.",
        "",
        "## Output Files",
        "",
        f"- `results/{RUN_ID}/investment_sample_flow.csv`",
        f"- `results/{RUN_ID}/investment_event_study_by_direction.csv`",
        f"- `results/{RUN_ID}/investment_event_level_contribution.csv`",
        f"- `results/{RUN_ID}/investment_leave_one_event_out.csv`",
        f"- `results/{RUN_ID}/investment_relationship_examples.csv`",
    ]
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    links, panel = load_inputs()
    flow = sample_flow(links, panel)
    event_study = grouped_event_study(panel)
    event_contrib = event_level_contribution(panel)
    loo = leave_one_event_out(panel)
    examples = relationship_examples(panel)

    flow.to_csv(OUT_DIR / "investment_sample_flow.csv", index=False, encoding="utf-8-sig")
    event_study.to_csv(OUT_DIR / "investment_event_study_by_direction.csv", index=False, encoding="utf-8-sig")
    event_contrib.to_csv(OUT_DIR / "investment_event_level_contribution.csv", index=False, encoding="utf-8-sig")
    loo.to_csv(OUT_DIR / "investment_leave_one_event_out.csv", index=False, encoding="utf-8-sig")
    examples.to_csv(OUT_DIR / "investment_relationship_examples.csv", index=False, encoding="utf-8-sig")
    write_doc(flow, event_study, loo, event_contrib, examples)

    car = event_study[event_study["window"].eq("CAR[0,+1]")]
    print("sample flow")
    print(flow.to_string(index=False))
    print("\nCAR[0,+1]")
    print(
        car[
            car["relation_type"].isin(["investment_linked_partner", "investor_in_focal", "investee_of_focal"])
        ].to_string(index=False)
    )
    print("\nleave-one-event-out")
    print(loo.to_string(index=False))
    print(f"\nwrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
