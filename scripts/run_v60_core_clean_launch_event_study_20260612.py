#!/usr/bin/env python3
"""Run core-clean GenAI launch/deploy event-study checks from the v56 sample."""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v23_cninfo_1055_peer_event_study_20260603 as pe  # noqa: E402
import run_v38_wide_collaborator_competitor_probe_20260607 as v38  # noqa: E402


RUN_ID = "v60_core_clean_launch_event_study_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "120_v60_core_clean_launch_event_study_20260612.md"

V56_EVENTS = ROOT / "results/v56_v55_expanded_llm_empirical_tables_20260612/expanded_event_samples.csv"
V56_PEER_PANEL = ROOT / "results/v56_v55_expanded_llm_empirical_tables_20260612/analysis_panel_with_returns_ai.csv.gz"
V57_CSMAR_SUPPLIER_PANEL = ROOT / "results/v57_v56_expanded_supplier_benchmark_20260612/supplier_event_panel_with_returns.csv.gz"
V58_FACTSET_PANEL = ROOT / "results/v58_v56_factset_supplier_benchmark_20260612/factset_relation_panel.csv.gz"

PREFERRED_METHOD = "liu_product_tfidf_same_industry_d_top10"
OUTCOMES = pe.OUTCOMES
MAIN_OUTCOME = "peer_car_0_p1_mm"

LAUNCH_PATTERN = re.compile(r"发布|上线|推出|正式发布|正式上线|备案通过|大模型算法备案|成果发布会|发布会|新产品")
EXCLUDE_TITLE_PATTERN = re.compile(
    r"董事会|监事会|股东大会|决议|年度报告|半年度报告|季度报告|业绩快报|工作报告|会议纪要|"
    r"投资者交流|调研|行动方案|提质增效|致投资者|H股公告|可行性研究|可研|募集|"
    r"向特定对象发行|发行股票|股票预案|预案|定增|对外投资|收购|增资|购买.*股权|"
    r"股权|并购|重大资产重组|现金收购|关联交易|框架|战略合作|合作协议|签署.*协议|"
    r"设立|合资|股价异动|异常波动|问询|关注函|回复|补充协议|进展|风险提示|澄清|"
    r"更正|中标|重大合同|合同|项目建设|基地|数据中心|智算中心|算力中心|服务器|"
    r"采购|专利|著作权|商标|证书|超募资金|在建项目|永久补充"
)


def clean(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def p_from_z(z_value: float) -> float:
    return math.erfc(abs(z_value) / math.sqrt(2)) if math.isfinite(z_value) else math.nan


def md_table(df: pd.DataFrame, cols: list[str] | None = None, limit: int = 40) -> str:
    if df.empty:
        return "_No rows._"
    out = df.copy()
    if cols is not None:
        out = out[cols]
    out = out.head(limit).copy()
    for col in out.select_dtypes(include=[np.number]).columns:
        out[col] = out[col].map(lambda x: round(float(x), 6) if pd.notna(x) else x)
    lines = ["| " + " | ".join(out.columns) + " |", "|" + "|".join("---" for _ in out.columns) + "|"]
    for _, row in out.iterrows():
        lines.append("| " + " | ".join("" if pd.isna(row[c]) else str(row[c]).replace("|", "\\|") for c in out.columns) + " |")
    return "\n".join(lines)


def strict_next_trading_day(date: pd.Timestamp, trading_dates: np.ndarray) -> pd.Timestamp | pd.NaT:
    if pd.isna(date):
        return pd.NaT
    target = np.datetime64(pd.Timestamp(date).normalize())
    pos = int(np.searchsorted(trading_dates, target, side="right"))
    if pos >= len(trading_dates):
        return pd.NaT
    return pd.Timestamp(trading_dates[pos])


def load_a_events() -> pd.DataFrame:
    events = pd.read_csv(V56_EVENTS, dtype=str, low_memory=False).fillna("")
    a = events[events["sample_name"].eq("A_all")].drop_duplicates("event_id").copy()
    a["focal_code"] = a["focal_code"].map(pe.code6)
    a["event_date"] = pd.to_datetime(a["event_date"], errors="coerce")
    for col in ["announcement_title", "evidence", "reason", "priority_evidence", "metadata_snippet", "primary_pom_like_category"]:
        if col not in a.columns:
            a[col] = ""
    text = a[
        ["announcement_title", "evidence", "reason", "priority_evidence", "metadata_snippet", "primary_pom_like_category"]
    ].agg(" ".join, axis=1)
    title = a["announcement_title"].fillna("")
    a["core_launch_text_hit"] = text.str.contains(LAUNCH_PATTERN, na=False)
    a["core_excluded_title_form"] = title.str.contains(EXCLUDE_TITLE_PATTERN, na=False)
    a["core_clean_launch"] = (
        a["model_verdict"].eq("A")
        & a["mode"].eq("own")
        & a["layer"].isin(["model", "app"])
        & a["out"].eq("1")
        & a["core_launch_text_hit"]
        & ~a["core_excluded_title_form"]
    )
    a["core_realized_plus"] = a["core_clean_launch"] & a["realized"].eq("+")
    return a[a["focal_code"].ne("") & a["event_date"].notna()].copy()


def build_core_samples(a: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sample_defs: list[tuple[str, pd.DataFrame]] = []
    core = a[a["core_clean_launch"]].copy()
    core_first = core.sort_values(["focal_code", "event_date", "event_id"]).drop_duplicates("focal_code")
    realized = a[a["core_realized_plus"]].copy()
    realized_first = realized.sort_values(["focal_code", "event_date", "event_id"]).drop_duplicates("focal_code")
    sample_defs.extend(
        [
            ("Core_clean_launch_all", core),
            ("Core_clean_launch_first_firm", core_first),
            ("Core_realized_plus_all", realized),
            ("Core_realized_plus_first_firm", realized_first),
        ]
    )
    frames: list[pd.DataFrame] = []
    for sample_name, sub in sample_defs:
        if sub.empty:
            continue
        event = sub.copy()
        event["sample_name"] = sample_name
        event["event_key"] = event["sample_name"] + "::" + event["event_id"].astype(str)
        frames.append(event)
    samples = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return samples, core


def sample_summary(samples: pd.DataFrame) -> pd.DataFrame:
    if samples.empty:
        return pd.DataFrame()
    return (
        samples.groupby("sample_name", as_index=False)
        .agg(
            events=("event_id", "nunique"),
            focal_firms=("focal_code", "nunique"),
            first_date=("event_date", "min"),
            last_date=("event_date", "max"),
            model_layer=("layer", lambda s: ";".join(sorted(set(s.astype(str))))),
        )
        .sort_values("sample_name")
    )


def summarize_pe_style(panel: pd.DataFrame, group_cols: list[str], outcome_prefix: str = "peer") -> pd.DataFrame:
    if panel.empty:
        return pd.DataFrame()
    clean_panel = panel[panel["complete_clean_m1_p1"].eq(1)].copy()
    rows: list[dict[str, object]] = []
    for key, d in clean_panel.groupby(group_cols, dropna=False):
        base = dict(zip(group_cols, key))
        for outcome, label in OUTCOMES:
            rows.append({**base, "outcome": outcome, "outcome_label": label, **pe.clustered_mean(d, outcome)})
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(group_cols + ["outcome"]).reset_index(drop=True)


def focal_panel(samples: pd.DataFrame, use_strict_next_day: bool) -> pd.DataFrame:
    if samples.empty:
        return samples.copy()
    stock = pe.load_stock_model()
    out = samples.copy()
    out["peer_code"] = out["focal_code"].map(pe.code6)
    if use_strict_next_day:
        trading_dates = np.array(sorted(stock["date"].dropna().unique()), dtype="datetime64[ns]")
        out["date_0"] = out["event_date"].map(lambda x: strict_next_trading_day(x, trading_dates))
    else:
        out = pe.attach_event_trading_dates(out, stock)
    out = pe.build_return_measures(out, stock)
    return out


def build_peer_panel(samples: pd.DataFrame) -> pd.DataFrame:
    if samples.empty or not V56_PEER_PANEL.exists():
        return pd.DataFrame()
    base = pd.read_csv(V56_PEER_PANEL, dtype=str, low_memory=False)
    for col in [
        "method_top_n",
        "time_valid_prior_year",
        "complete_clean_m1_p1",
        "peer_ar_m1_mm",
        "peer_ar0_mm",
        "peer_ar_p1_mm",
        "peer_car_0_p1_mm",
        "peer_car_m1_p1_mm",
    ]:
        if col in base.columns:
            base[col] = pd.to_numeric(base[col], errors="coerce")
    base = base[base["sample_name"].eq("A_all")].copy()
    parts: list[pd.DataFrame] = []
    for sample_name, ids in samples.groupby("sample_name")["event_id"]:
        sub = base[base["event_id"].astype(str).isin(set(ids.astype(str)))].copy()
        if sub.empty:
            continue
        sub["sample_name"] = sample_name
        sub["event_key"] = sample_name + "::" + sub["event_id"].astype(str)
        parts.append(sub)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def build_csmar_supplier_panel(samples: pd.DataFrame) -> pd.DataFrame:
    if samples.empty or not V57_CSMAR_SUPPLIER_PANEL.exists():
        return pd.DataFrame()
    base = pd.read_csv(V57_CSMAR_SUPPLIER_PANEL, dtype=str, low_memory=False)
    for col in [
        "complete_clean_m1_p1",
        "peer_ar_m1_mm",
        "peer_ar0_mm",
        "peer_ar_p1_mm",
        "peer_car_0_p1_mm",
        "peer_car_m1_p1_mm",
    ]:
        if col in base.columns:
            base[col] = pd.to_numeric(base[col], errors="coerce")
    base = base[base["sample_name"].eq("A_all")].copy()
    parts: list[pd.DataFrame] = []
    for sample_name, ids in samples.groupby("sample_name")["event_id"]:
        sub = base[base["event_id"].astype(str).isin(set(ids.astype(str)))].copy()
        if sub.empty:
            continue
        sub["sample_name"] = sample_name
        sub["event_key"] = sample_name + "::" + sub["event_id"].astype(str)
        parts.append(sub)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def summarize_factset(panel: pd.DataFrame) -> pd.DataFrame:
    if panel.empty:
        return pd.DataFrame()
    clean_panel = panel[
        panel["complete_clean_m1_p1"].eq(1)
        & panel["relation_type"].isin(["factset_upstream_supplier", "factset_downstream_customer", "factset_relationship_union"])
    ].copy()
    rows: list[dict[str, object]] = []
    for (sample_name, relation_type), d in clean_panel.groupby(["sample_name", "relation_type"], dropna=False):
        for outcome, label in v38.OUTCOMES:
            rows.append(
                {
                    "sample_name": sample_name,
                    "relation_type": relation_type,
                    "outcome": outcome,
                    "outcome_label": label,
                    **v38.clustered_mean(d, outcome),
                    **v38.event_weighted_mean(d, outcome),
                }
            )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["sample_name", "relation_type", "outcome"]).reset_index(drop=True)


def build_factset_panel(samples: pd.DataFrame) -> pd.DataFrame:
    if samples.empty or not V58_FACTSET_PANEL.exists():
        return pd.DataFrame()
    base = pd.read_csv(V58_FACTSET_PANEL, dtype=str, low_memory=False)
    for col in [
        "complete_clean_m1_p1",
        "peer_ar_m1_mm",
        "peer_ar0_mm",
        "peer_ar_p1_mm",
        "peer_car_0_p1_mm",
        "peer_car_m1_p1_mm",
    ]:
        if col in base.columns:
            base[col] = pd.to_numeric(base[col], errors="coerce")
    base = base[base["sample_name"].eq("A_all")].copy()
    parts: list[pd.DataFrame] = []
    for sample_name, ids in samples.groupby("sample_name")["event_id"]:
        sub = base[base["event_id"].astype(str).isin(set(ids.astype(str)))].copy()
        if sub.empty:
            continue
        sub["sample_name"] = sample_name
        sub["event_key"] = sample_name + "::" + sub["event_id"].astype(str)
        parts.append(sub)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def peer_minus_focal(peer_panel: pd.DataFrame, focal_inclusive: pd.DataFrame) -> pd.DataFrame:
    if peer_panel.empty or focal_inclusive.empty:
        return pd.DataFrame()
    peer = peer_panel[
        peer_panel["method_variant"].eq(PREFERRED_METHOD)
        & peer_panel["complete_clean_m1_p1"].eq(1)
    ].copy()
    if peer.empty:
        return pd.DataFrame()
    event_peer = (
        peer.groupby(["sample_name", "event_id"], as_index=False)
        .agg(
            peer_mean_car=("peer_car_0_p1_mm", "mean"),
            peer_obs=("peer_code", "size"),
            peer_firms=("peer_code", "nunique"),
        )
        .copy()
    )
    foc = focal_inclusive[focal_inclusive["complete_clean_m1_p1"].eq(1)][
        ["sample_name", "event_id", "peer_car_0_p1_mm"]
    ].rename(columns={"peer_car_0_p1_mm": "focal_car"})
    merged = event_peer.merge(foc, on=["sample_name", "event_id"], how="inner")
    merged["peer_minus_focal"] = merged["peer_mean_car"] - merged["focal_car"]
    rows = []
    for sample_name, d in merged.groupby("sample_name"):
        vals = d["peer_minus_focal"].astype(float)
        mean = float(vals.mean())
        se = float(vals.std(ddof=1) / math.sqrt(len(vals))) if len(vals) > 1 else math.nan
        z = mean / se if se and se > 0 else math.nan
        rows.append(
            {
                "sample_name": sample_name,
                "events": int(len(vals)),
                "peer_minus_focal_mean": mean,
                "se": se,
                "p": p_from_z(z),
                "median": float(vals.median()),
                "positive_share": float((vals > 0).mean()),
                "mean_peer_car": float(d["peer_mean_car"].mean()),
                "mean_focal_car": float(d["focal_car"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("sample_name")


def write_doc(
    core_events: pd.DataFrame,
    sample_counts: pd.DataFrame,
    focal_next: pd.DataFrame,
    focal_inclusive: pd.DataFrame,
    peer_summary: pd.DataFrame,
    csmar_summary: pd.DataFrame,
    factset_summary: pd.DataFrame,
    rel_summary: pd.DataFrame,
) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    main_samples = ["Core_clean_launch_all", "Core_clean_launch_first_firm", "Core_realized_plus_all", "Core_realized_plus_first_firm"]
    focal_next_main = focal_next[
        focal_next["sample_name"].isin(main_samples)
        & focal_next["outcome"].isin(["peer_ar0_mm", "peer_ar_p1_mm", "peer_car_0_p1_mm", "peer_car_m1_p1_mm"])
    ]
    peer_main = peer_summary[
        peer_summary["method_variant"].eq(PREFERRED_METHOD)
        & peer_summary["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
    ]
    csmar_main = csmar_summary[
        csmar_summary.get("edge_family", pd.Series(dtype=str)).eq("union")
        & csmar_summary["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
    ] if not csmar_summary.empty else csmar_summary
    factset_main = factset_summary[
        factset_summary["relation_type"].isin(["factset_upstream_supplier", "factset_downstream_customer"])
        & factset_summary["outcome"].isin(["peer_ar0_mm", "peer_car_0_p1_mm"])
    ] if not factset_summary.empty else factset_summary
    lines = [
        "# v60 Core Clean GenAI Launch Event Study",
        "",
        "## Scope",
        "",
        "- Input: v56 expanded A sample.",
        "- Main strict sample `Core_clean_launch`: own GenAI model/app announcement, external-facing (`out=1`), launch/release/filing text hit, and no title-form noise such as board resolutions, investment, M&A, financing, framework agreements, annual reports, investor minutes, patents, or compute/capex projects.",
        "- Ultra-strict sample `Core_realized_plus`: the same rule plus LLM field `realized=+`.",
        "- Focal firm main timing uses strict next trading day because CNINFO disclosures are often released after market close. Peer and relation panels reuse v56/v57/v58 return panels, so they use the existing event-date-to-next-available-trading-day convention.",
        "",
        "## Core Events",
        "",
        md_table(
            core_events[
                [
                    "event_date",
                    "focal_code",
                    "sec_name",
                    "announcement_title",
                    "out",
                    "mode",
                    "layer",
                    "realized",
                ]
            ],
            limit=30,
        ),
        "",
        "## Sample Counts",
        "",
        md_table(sample_counts, limit=20),
        "",
        "## Focal Firm Returns, Strict Next Trading Day",
        "",
        md_table(
            focal_next_main,
            ["sample_name", "outcome_label", "estimate", "se", "p", "nobs", "events", "focal_firms", "median", "positive_share"],
            30,
        ),
        "",
        "## Product-Market Peer Returns",
        "",
        md_table(
            peer_main,
            ["sample_name", "outcome_label", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"],
            30,
        ),
        "",
        "## Peer Minus Focal, Same Existing Event Clock",
        "",
        md_table(rel_summary, limit=20),
        "",
        "## CSMAR Listed Supplier Benchmark",
        "",
        md_table(
            csmar_main,
            ["sample_name", "edge_family", "outcome_label", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"],
            30,
        ),
        "",
        "## FactSet Supplier/Customer Benchmark",
        "",
        md_table(
            factset_main,
            [
                "sample_name",
                "relation_type",
                "outcome_label",
                "mean",
                "se",
                "p",
                "nobs",
                "events",
                "related_firms",
                "median",
                "positive_share",
                "event_weighted_mean",
                "event_weighted_p",
            ],
            40,
        ),
        "",
        "## Output Files",
        "",
        f"- `results/{RUN_ID}/core_event_samples.csv`",
        f"- `results/{RUN_ID}/core_classification_all_A.csv`",
        f"- `results/{RUN_ID}/focal_returns_strict_next_day_summary.csv`",
        f"- `results/{RUN_ID}/peer_returns_summary.csv`",
        f"- `results/{RUN_ID}/csmar_supplier_summary.csv`",
        f"- `results/{RUN_ID}/factset_relation_summary.csv`",
        f"- `results/{RUN_ID}/peer_minus_focal_summary.csv`",
        f"- `results/{RUN_ID}/{RUN_ID}.xlsx`",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    a = load_a_events()
    samples, core_events = build_core_samples(a)
    if samples.empty:
        raise RuntimeError("No core samples were created.")
    counts = sample_summary(samples)

    focal_next_panel = focal_panel(samples, use_strict_next_day=True)
    focal_inclusive_panel = focal_panel(samples, use_strict_next_day=False)
    focal_next_summary = summarize_pe_style(focal_next_panel, ["sample_name"])
    focal_inclusive_summary = summarize_pe_style(focal_inclusive_panel, ["sample_name"])

    peer_panel = build_peer_panel(samples)
    peer_summary = summarize_pe_style(peer_panel, ["sample_name", "method_variant", "method", "method_top_n", "time_valid_prior_year"])

    csmar_panel = build_csmar_supplier_panel(samples)
    csmar_summary = summarize_pe_style(csmar_panel, ["sample_name", "event_type", "edge_family"])

    factset_panel = build_factset_panel(samples)
    factset_summary = summarize_factset(factset_panel)

    rel_summary = peer_minus_focal(peer_panel, focal_inclusive_panel)

    a.to_csv(OUT_DIR / "core_classification_all_A.csv", index=False, encoding="utf-8-sig")
    samples.to_csv(OUT_DIR / "core_event_samples.csv", index=False, encoding="utf-8-sig")
    counts.to_csv(OUT_DIR / "core_sample_counts.csv", index=False, encoding="utf-8-sig")
    focal_next_panel.to_csv(OUT_DIR / "focal_returns_strict_next_day_panel.csv.gz", index=False)
    focal_next_summary.to_csv(OUT_DIR / "focal_returns_strict_next_day_summary.csv", index=False, encoding="utf-8-sig")
    focal_inclusive_summary.to_csv(OUT_DIR / "focal_returns_existing_event_clock_summary.csv", index=False, encoding="utf-8-sig")
    peer_summary.to_csv(OUT_DIR / "peer_returns_summary.csv", index=False, encoding="utf-8-sig")
    csmar_summary.to_csv(OUT_DIR / "csmar_supplier_summary.csv", index=False, encoding="utf-8-sig")
    factset_summary.to_csv(OUT_DIR / "factset_relation_summary.csv", index=False, encoding="utf-8-sig")
    rel_summary.to_csv(OUT_DIR / "peer_minus_focal_summary.csv", index=False, encoding="utf-8-sig")

    xlsx = OUT_DIR / f"{RUN_ID}.xlsx"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        counts.to_excel(writer, sheet_name="Sample_counts", index=False)
        core_events.to_excel(writer, sheet_name="Core_events", index=False)
        focal_next_summary.to_excel(writer, sheet_name="Focal_next", index=False)
        peer_summary.to_excel(writer, sheet_name="Peer", index=False)
        csmar_summary.to_excel(writer, sheet_name="CSMAR_supplier", index=False)
        factset_summary.to_excel(writer, sheet_name="FactSet", index=False)
        rel_summary.to_excel(writer, sheet_name="Peer_minus_focal", index=False)

    write_doc(core_events, counts, focal_next_summary, focal_inclusive_summary, peer_summary, csmar_summary, factset_summary, rel_summary)

    print(f"wrote {OUT_DIR}", flush=True)
    print(f"wrote {DOC_PATH}", flush=True)
    print("\nCore sample counts:")
    print(counts.to_string(index=False), flush=True)
    print("\nCore focal strict-next CAR[0,+1]:")
    focal_car = focal_next_summary[focal_next_summary["outcome"].eq(MAIN_OUTCOME)]
    print(focal_car[["sample_name", "estimate", "se", "p", "nobs", "events", "focal_firms", "median", "positive_share"]].to_string(index=False), flush=True)
    print("\nPreferred product-peer CAR[0,+1]:")
    peer_car = peer_summary[
        peer_summary["method_variant"].eq(PREFERRED_METHOD) & peer_summary["outcome"].eq(MAIN_OUTCOME)
    ]
    print(peer_car[["sample_name", "estimate", "se", "p", "nobs", "events", "peer_firms", "median", "positive_share"]].to_string(index=False), flush=True)
    print("\nPeer minus focal:")
    print(rel_summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
