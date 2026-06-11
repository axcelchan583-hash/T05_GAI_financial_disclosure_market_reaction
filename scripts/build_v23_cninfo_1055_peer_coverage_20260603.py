#!/usr/bin/env python3
"""Audit whether CNINFO GenAI events can be linked to product-market peers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


RUN_ID = "v23_cninfo_1055_peer_coverage_20260603"
ROOT = Path(__file__).resolve().parents[1]
QIAN_ROOT = ROOT.parent / "T05-qian-supplier-replication-cn"
EVENT_DIR = QIAN_ROOT / "results" / "v27_cninfo_priority_pdf_audit_2023_2026_20260603"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "86_v23_cninfo_1055_peer_coverage_20260603.md"


@dataclass(frozen=True)
class NetworkSpec:
    method: str
    rel_path: str
    time_valid: bool
    top_ns: tuple[int, ...]
    notes: str


EVENT_FILES = [
    ("all_1055", EVENT_DIR / "manual_review_priority_pdf_all.csv"),
    ("likely_106", EVENT_DIR / "manual_review_likely_qian_initiatives.csv"),
    ("possible_or_backfill_921", EVENT_DIR / "manual_review_possible_or_backfill.csv"),
]


NETWORK_SPECS = [
    NetworkSpec(
        "csmar_scope_product_text",
        "results/csmar_v5_1_response_smoke_20260523/csmar_product_peer_network_top10.csv",
        False,
        (5, 10),
        "CSMAR business-scope product text, static top-10 network.",
    ),
    NetworkSpec(
        "annual_report_global",
        "results/v12_annual_report_product_peers_20260530/annual_report_peer_network_global_top10.csv",
        True,
        (5, 10),
        "Annual-report product text, latest snapshot <= event year - 1.",
    ),
    NetworkSpec(
        "annual_report_same_industry_d",
        "results/v12_annual_report_product_peers_20260530/annual_report_peer_network_same_industry_d_top10.csv",
        True,
        (5, 10),
        "Annual-report product text restricted to CSRC industry D, latest snapshot <= event year - 1.",
    ),
    NetworkSpec(
        "annual_report_global_ai_stripped",
        "results/v12_annual_report_product_peers_20260530/annual_report_peer_network_global_ai_stripped_top10.csv",
        True,
        (5, 10),
        "Annual-report product text after removing AI terms, latest snapshot <= event year - 1.",
    ),
    NetworkSpec(
        "full_semantic_reranked",
        "results/v16_full_semantic_reranked_peers_20260531/full_semantic_reranked_peer_network_top10.csv",
        False,
        (5, 10),
        "Semantic reranked union of candidate peer sources, static as-of network.",
    ),
    NetworkSpec(
        "csmar_scope_semantic_only",
        "results/v16_full_semantic_reranked_peers_20260531/csmar_scope_only_semantic_peer_network_top10.csv",
        False,
        (5, 10),
        "Semantic rerank using CSMAR-scope candidates only, static as-of network.",
    ),
    NetworkSpec(
        "annual_only_semantic",
        "results/v16_full_semantic_reranked_peers_20260531/annual_only_semantic_peer_network_top10.csv",
        False,
        (5, 10),
        "Semantic rerank using annual-report candidates only, static as-of network.",
    ),
    NetworkSpec(
        "annual_same_only_semantic",
        "results/v16_full_semantic_reranked_peers_20260531/annual_same_only_semantic_peer_network_top10.csv",
        False,
        (5, 10),
        "Semantic rerank using same-industry annual-report candidates only, static as-of network.",
    ),
    NetworkSpec(
        "deepseek_flash",
        "results/v17_deepseek_flash_peer_coding_20260531/deepseek_flash_peer_network_top5_full_compact15.csv",
        False,
        (5,),
        "DeepSeek flash reranked top-5 peers, static as-of network.",
    ),
    NetworkSpec(
        "deepseek_open_ended",
        "results/v18_cao_style_open_ended_deepseek_peers_20260531/deepseek_open_ended_peer_network_top5_full_asof2025.csv",
        False,
        (5,),
        "Cao-style open-ended DeepSeek top-5 peers, static as-of 2025.",
    ),
    NetworkSpec(
        "deepseek_open_ended_same_industry",
        "results/v18_cao_style_open_ended_deepseek_peers_20260531/deepseek_open_ended_peer_network_top5_same_industry_full_asof2025.csv",
        False,
        (5,),
        "Cao-style open-ended DeepSeek top-5 peers with same-industry restriction, static as-of 2025.",
    ),
    NetworkSpec(
        "ren_wang_binary_global",
        "results/v22_chinese_literature_product_peers_20260601/ren_wang_binary_global_peer_network_top20.csv",
        True,
        (5, 10, 20),
        "Ren-Wang binary product keywords, global peers, latest snapshot <= event year - 1.",
    ),
    NetworkSpec(
        "ren_wang_binary_same_industry_d",
        "results/v22_chinese_literature_product_peers_20260601/ren_wang_binary_same_industry_d_peer_network_top20.csv",
        True,
        (5, 10, 20),
        "Ren-Wang binary product keywords, same-industry-D peers, latest snapshot <= event year - 1.",
    ),
    NetworkSpec(
        "liu_product_tfidf_global",
        "results/v22_chinese_literature_product_peers_20260601/liu_product_tfidf_global_peer_network_top20.csv",
        True,
        (5, 10, 20),
        "Liu-style product TF-IDF, global peers, latest snapshot <= event year - 1.",
    ),
    NetworkSpec(
        "liu_product_tfidf_same_industry_d",
        "results/v22_chinese_literature_product_peers_20260601/liu_product_tfidf_same_industry_d_peer_network_top20.csv",
        True,
        (5, 10, 20),
        "Liu-style product TF-IDF, same-industry-D peers, latest snapshot <= event year - 1.",
    ),
    NetworkSpec(
        "placebo_low_similarity",
        "results/v20_deepseek_candidate_placebos_20260601/deepseek_candidate_low_similarity_top5.csv",
        False,
        (5,),
        "Low-similarity placebo peers from the DeepSeek candidate menu.",
    ),
    NetworkSpec(
        "placebo_random",
        "results/v20_deepseek_candidate_placebos_20260601/deepseek_candidate_random_top5.csv",
        False,
        (5,),
        "Random placebo peers from the DeepSeek candidate menu.",
    ),
]


def code6(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    if "." in text:
        text = text.split(".", 1)[0]
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None
    return digits.zfill(6)[-6:]


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, low_memory=False)


def load_events() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for sample_name, path in EVENT_FILES:
        if not path.exists():
            raise FileNotFoundError(path)
        df = read_csv(path)
        df["sample_name"] = sample_name
        df["event_id"] = df.get("announcement_id", pd.Series(index=df.index, dtype=str)).fillna("")
        fallback_id = (
            df.get("sec_code", pd.Series(index=df.index, dtype=str)).fillna("")
            + "_"
            + df.get("announcement_date", pd.Series(index=df.index, dtype=str)).fillna("")
            + "_"
            + df.get("announcement_title", pd.Series(index=df.index, dtype=str)).fillna("")
        )
        df.loc[df["event_id"].str.strip().eq(""), "event_id"] = fallback_id
        df["event_key"] = df["sample_name"] + "::" + df["event_id"].astype(str)
        df["focal_code"] = df["sec_code"].map(code6)
        df["event_date_raw"] = df.get("manual_event_date_corrected", "").where(
            df.get("manual_event_date_corrected", "").notna()
            & df.get("manual_event_date_corrected", "").astype(str).str.strip().ne(""),
            df.get("announcement_date", ""),
        )
        df["event_date"] = pd.to_datetime(df["event_date_raw"], errors="coerce")
        df["event_year"] = df["event_date"].dt.year
        if "auto_pdf_label" not in df.columns:
            df["auto_pdf_label"] = "unknown"
        df["auto_pdf_label"] = df["auto_pdf_label"].fillna("unknown")
        keep_cols = [
            "sample_name",
            "event_key",
            "event_id",
            "focal_code",
            "sec_name",
            "event_date",
            "event_year",
            "announcement_date",
            "announcement_title",
            "auto_pdf_label",
            "auto_keep_likely_qian",
            "candidate_tier",
        ]
        for col in keep_cols:
            if col not in df.columns:
                df[col] = pd.NA
        frames.append(df[keep_cols].copy())
    events = pd.concat(frames, ignore_index=True)
    events = events[events["focal_code"].notna() & events["event_date"].notna()].copy()
    return events


def standardize_network(spec: NetworkSpec) -> pd.DataFrame:
    path = ROOT / spec.rel_path
    if not path.exists():
        raise FileNotFoundError(path)
    df = read_csv(path)
    if "peer_similarity" not in df.columns and "product_similarity" in df.columns:
        df["peer_similarity"] = df["product_similarity"]
    if "peer_source" not in df.columns:
        df["peer_source"] = spec.method
    for col in ["focal_name", "peer_name", "focal_industry_d", "peer_industry_d"]:
        if col not in df.columns:
            df[col] = pd.NA
    if "snapshot_report_year" not in df.columns:
        df["snapshot_report_year"] = pd.NA
    cols = [
        "peer_source",
        "snapshot_report_year",
        "focal_code",
        "focal_name",
        "peer_code",
        "peer_name",
        "peer_rank",
        "peer_similarity",
        "focal_industry_d",
        "peer_industry_d",
    ]
    out = df[cols].copy()
    out["focal_code"] = out["focal_code"].map(code6)
    out["peer_code"] = out["peer_code"].map(code6)
    out["peer_rank"] = numeric(out["peer_rank"])
    out["peer_similarity"] = numeric(out["peer_similarity"])
    out["snapshot_report_year"] = numeric(out["snapshot_report_year"])
    out = out[
        out["focal_code"].notna()
        & out["peer_code"].notna()
        & out["peer_rank"].notna()
        & out["peer_code"].ne(out["focal_code"])
    ].copy()
    return out


def link_network(events: pd.DataFrame, spec: NetworkSpec) -> pd.DataFrame:
    network = standardize_network(spec)
    linked_frames: list[pd.DataFrame] = []
    for top_n in spec.top_ns:
        subset = network[network["peer_rank"].le(top_n)].copy()
        if subset.empty:
            continue
        merged = events.merge(subset, on="focal_code", how="inner")
        if spec.time_valid:
            merged = merged[
                merged["snapshot_report_year"].notna()
                & merged["event_year"].notna()
                & merged["snapshot_report_year"].le(merged["event_year"] - 1)
            ].copy()
            merged["latest_snapshot_year"] = merged.groupby("event_key")["snapshot_report_year"].transform("max")
            merged = merged[merged["snapshot_report_year"].eq(merged["latest_snapshot_year"])].copy()
            merged = merged.sort_values(
                ["event_key", "peer_code", "snapshot_report_year", "peer_rank"],
                ascending=[True, True, False, True],
            )
            merged = merged.drop_duplicates(["event_key", "peer_code"], keep="first")
        else:
            merged = merged.sort_values(["event_key", "peer_code", "peer_rank"])
            merged = merged.drop_duplicates(["event_key", "peer_code"], keep="first")
        if merged.empty:
            continue
        merged["method"] = spec.method
        merged["method_top_n"] = top_n
        merged["method_variant"] = spec.method + "_top" + str(top_n)
        merged["time_valid_prior_year"] = int(spec.time_valid)
        merged["network_notes"] = spec.notes
        linked_frames.append(merged)
    if not linked_frames:
        return pd.DataFrame()
    return pd.concat(linked_frames, ignore_index=True)


def summarize_panel(events: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    base = (
        events.groupby("sample_name", dropna=False)
        .agg(input_events=("event_key", "nunique"), input_focal_firms=("focal_code", "nunique"))
        .reset_index()
    )
    rows = []
    variants = sorted(panel["method_variant"].dropna().unique()) if not panel.empty else []
    for variant in variants:
        method_panel = panel[panel["method_variant"].eq(variant)].copy()
        for sample_name, sample_base in base.groupby("sample_name"):
            sample_panel = method_panel[method_panel["sample_name"].eq(sample_name)]
            input_events = int(sample_base["input_events"].iloc[0])
            input_firms = int(sample_base["input_focal_firms"].iloc[0])
            peer_counts = sample_panel.groupby("event_key")["peer_code"].nunique()
            rows.append(
                {
                    "method_variant": variant,
                    "method": sample_panel["method"].iloc[0] if not sample_panel.empty else variant.rsplit("_top", 1)[0],
                    "top_n": int(sample_panel["method_top_n"].iloc[0]) if not sample_panel.empty else pd.NA,
                    "time_valid_prior_year": int(sample_panel["time_valid_prior_year"].iloc[0]) if not sample_panel.empty else pd.NA,
                    "sample_name": sample_name,
                    "input_events": input_events,
                    "input_focal_firms": input_firms,
                    "events_with_peers": int(sample_panel["event_key"].nunique()),
                    "focal_firms_with_peers": int(sample_panel["focal_code"].nunique()),
                    "peer_event_obs": int(len(sample_panel)),
                    "unique_peer_firms": int(sample_panel["peer_code"].nunique()),
                    "event_link_rate": sample_panel["event_key"].nunique() / input_events if input_events else pd.NA,
                    "firm_link_rate": sample_panel["focal_code"].nunique() / input_firms if input_firms else pd.NA,
                    "mean_peers_per_linked_event": float(peer_counts.mean()) if len(peer_counts) else 0.0,
                    "median_peers_per_linked_event": float(peer_counts.median()) if len(peer_counts) else 0.0,
                }
            )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["sample_name", "event_link_rate", "peer_event_obs"], ascending=[True, False, False])


def summarize_by_label(events: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    base = (
        events.groupby(["sample_name", "auto_pdf_label"], dropna=False)
        .agg(input_events=("event_key", "nunique"), input_focal_firms=("focal_code", "nunique"))
        .reset_index()
    )
    linked = (
        panel.groupby(["method_variant", "sample_name", "auto_pdf_label"], dropna=False)
        .agg(
            events_with_peers=("event_key", "nunique"),
            focal_firms_with_peers=("focal_code", "nunique"),
            peer_event_obs=("peer_code", "size"),
            unique_peer_firms=("peer_code", "nunique"),
        )
        .reset_index()
    )
    variants = pd.DataFrame({"method_variant": sorted(panel["method_variant"].dropna().unique())})
    if variants.empty:
        return pd.DataFrame()
    out = variants.merge(base, how="cross").merge(
        linked, on=["method_variant", "sample_name", "auto_pdf_label"], how="left"
    )
    for col in ["events_with_peers", "focal_firms_with_peers", "peer_event_obs", "unique_peer_firms"]:
        out[col] = out[col].fillna(0).astype(int)
    out["event_link_rate"] = out["events_with_peers"] / out["input_events"]
    return out.sort_values(["sample_name", "auto_pdf_label", "event_link_rate"], ascending=[True, True, False])


def summarize_by_year(events: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    base = (
        events.groupby(["sample_name", "event_year"], dropna=False)
        .agg(input_events=("event_key", "nunique"), input_focal_firms=("focal_code", "nunique"))
        .reset_index()
    )
    linked = (
        panel.groupby(["method_variant", "sample_name", "event_year"], dropna=False)
        .agg(
            events_with_peers=("event_key", "nunique"),
            focal_firms_with_peers=("focal_code", "nunique"),
            peer_event_obs=("peer_code", "size"),
            unique_peer_firms=("peer_code", "nunique"),
        )
        .reset_index()
    )
    variants = pd.DataFrame({"method_variant": sorted(panel["method_variant"].dropna().unique())})
    if variants.empty:
        return pd.DataFrame()
    out = variants.merge(base, how="cross").merge(
        linked, on=["method_variant", "sample_name", "event_year"], how="left"
    )
    for col in ["events_with_peers", "focal_firms_with_peers", "peer_event_obs", "unique_peer_firms"]:
        out[col] = out[col].fillna(0).astype(int)
    out["event_link_rate"] = out["events_with_peers"] / out["input_events"]
    return out.sort_values(["sample_name", "event_year", "event_link_rate"], ascending=[True, True, False])


def summarize_event_counts(events: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    linked = (
        panel.groupby(["method_variant", "sample_name", "event_key"], dropna=False)
        .agg(peer_count=("peer_code", "nunique"))
        .reset_index()
    )
    variants = pd.DataFrame({"method_variant": sorted(panel["method_variant"].dropna().unique())})
    if variants.empty:
        return pd.DataFrame()
    event_cols = [
        "sample_name",
        "event_key",
        "event_id",
        "focal_code",
        "sec_name",
        "event_date",
        "event_year",
        "announcement_title",
        "auto_pdf_label",
    ]
    out = variants.merge(events[event_cols], how="cross").merge(
        linked, on=["method_variant", "sample_name", "event_key"], how="left"
    )
    out["peer_count"] = out["peer_count"].fillna(0).astype(int)
    return out


def write_report(events: pd.DataFrame, summary: pd.DataFrame, label_summary: pd.DataFrame, panel: pd.DataFrame) -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    all_summary = summary[summary["sample_name"].eq("all_1055")].copy()
    strict_summary = all_summary[all_summary["time_valid_prior_year"].eq(1)].copy()
    static_summary = all_summary[all_summary["time_valid_prior_year"].eq(0)].copy()
    likely_summary = summary[summary["sample_name"].eq("likely_106")].copy()

    def top_lines(df: pd.DataFrame, limit: int = 8) -> list[str]:
        rows = []
        for _, row in df.head(limit).iterrows():
            rows.append(
                f"| {row['method_variant']} | {int(row['events_with_peers'])} | "
                f"{row['event_link_rate']:.3f} | {int(row['focal_firms_with_peers'])} | "
                f"{int(row['peer_event_obs'])} | {int(row['unique_peer_firms'])} |"
            )
        return rows

    all_events = events[events["sample_name"].eq("all_1055")]
    base_counts = (
        events.groupby("sample_name")
        .agg(events=("event_key", "nunique"), focal_firms=("focal_code", "nunique"))
        .reset_index()
    )
    label_counts = (
        all_events.groupby("auto_pdf_label")
        .agg(events=("event_key", "nunique"), focal_firms=("focal_code", "nunique"))
        .reset_index()
        .sort_values("events", ascending=False)
    )

    lines: list[str] = []
    lines.append("# v23 CNINFO 1055 peer coverage audit")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This run checks whether the 1055 CNINFO GenAI disclosure candidates can be connected to prior T05 product-market peer definitions. "
        "It is a coverage audit only; it does not estimate peer abnormal returns."
    )
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- Event source: `{EVENT_DIR.relative_to(ROOT.parent)}/manual_review_priority_pdf_all.csv`.")
    lines.append("- Event date: `manual_event_date_corrected` if available, otherwise `announcement_date`.")
    lines.append("- Time-valid annual networks keep the latest `snapshot_report_year <= event_year - 1`.")
    lines.append("- Static LLM/semantic networks are reported as coverage diagnostics only because they are not event-year rolling networks.")
    lines.append("")
    lines.append("## Sample counts")
    lines.append("")
    lines.append("| sample | events | focal firms |")
    lines.append("|---|---:|---:|")
    for _, row in base_counts.iterrows():
        lines.append(f"| {row['sample_name']} | {int(row['events'])} | {int(row['focal_firms'])} |")
    lines.append("")
    lines.append("All-1055 automatic PDF labels:")
    lines.append("")
    lines.append("| auto label | events | focal firms |")
    lines.append("|---|---:|---:|")
    for _, row in label_counts.iterrows():
        lines.append(f"| {row['auto_pdf_label']} | {int(row['events'])} | {int(row['focal_firms'])} |")
    lines.append("")
    lines.append("## Main coverage result")
    lines.append("")
    lines.append("Strict prior-year peer networks on all 1055 events:")
    lines.append("")
    lines.append("| method | linked events | event link rate | linked focal firms | peer-event obs | unique peers |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    lines.extend(top_lines(strict_summary))
    lines.append("")
    lines.append("Static/LLM coverage diagnostics on all 1055 events:")
    lines.append("")
    lines.append("| method | linked events | event link rate | linked focal firms | peer-event obs | unique peers |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    lines.extend(top_lines(static_summary))
    lines.append("")
    lines.append("Likely-Qian subset coverage:")
    lines.append("")
    lines.append("| method | linked events | event link rate | linked focal firms | peer-event obs | unique peers |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    lines.extend(top_lines(likely_summary))
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    if not strict_summary.empty:
        best = strict_summary.sort_values(["event_link_rate", "peer_event_obs"], ascending=[False, False]).iloc[0]
        lines.append(
            f"- The best strict prior-year peer network links {int(best['events_with_peers'])} of 1055 events "
            f"({best['event_link_rate']:.1%}) and {int(best['focal_firms_with_peers'])} focal firms."
        )
    if not static_summary.empty:
        best_static = static_summary.sort_values(["event_link_rate", "peer_event_obs"], ascending=[False, False]).iloc[0]
        lines.append(
            f"- The best static diagnostic network links {int(best_static['events_with_peers'])} of 1055 events "
            f"({best_static['event_link_rate']:.1%}); this is useful for design triage but should not be used as a clean event-time design without rebuilding as rolling/as-of peers."
        )
    lines.append("- Compared with listed-supplier links, product-market peers are expected to be much less sparse because every A-share focal firm can in principle have listed product peers.")
    lines.append("")
    lines.append("## Output files")
    lines.append("")
    lines.append(f"- `{OUT_DIR.relative_to(ROOT)}/peer_coverage_summary.csv`")
    lines.append(f"- `{OUT_DIR.relative_to(ROOT)}/auto_label_peer_coverage_summary.csv`")
    lines.append(f"- `{OUT_DIR.relative_to(ROOT)}/year_peer_coverage_summary.csv`")
    lines.append(f"- `{OUT_DIR.relative_to(ROOT)}/event_peer_counts_by_method.csv`")
    lines.append(f"- `{OUT_DIR.relative_to(ROOT)}/peer_link_panel.csv.gz`")
    lines.append(f"- `{OUT_DIR.relative_to(ROOT)}/network_inventory.csv`")
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def inventory(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for spec in NETWORK_SPECS:
        path = ROOT / spec.rel_path
        exists = path.exists()
        row = {
            "method": spec.method,
            "path": spec.rel_path,
            "exists": int(exists),
            "time_valid_prior_year": int(spec.time_valid),
            "top_ns": ",".join(str(x) for x in spec.top_ns),
            "notes": spec.notes,
        }
        if exists:
            df = standardize_network(spec)
            row.update(
                {
                    "network_rows": int(len(df)),
                    "network_focal_firms": int(df["focal_code"].nunique()),
                    "network_peer_firms": int(df["peer_code"].nunique()),
                    "min_snapshot_year": int(df["snapshot_report_year"].min()) if df["snapshot_report_year"].notna().any() else pd.NA,
                    "max_snapshot_year": int(df["snapshot_report_year"].max()) if df["snapshot_report_year"].notna().any() else pd.NA,
                }
            )
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    events = load_events()
    panels: list[pd.DataFrame] = []
    for spec in NETWORK_SPECS:
        linked = link_network(events, spec)
        if not linked.empty:
            panels.append(linked)
            print(
                f"{spec.method}: variants={','.join(str(x) for x in spec.top_ns)} "
                f"rows={len(linked):,} events={linked['event_key'].nunique():,}"
            )
        else:
            print(f"{spec.method}: no linked rows")
    if not panels:
        raise RuntimeError("No peer links were created.")
    panel = pd.concat(panels, ignore_index=True)

    summary = summarize_panel(events, panel)
    label_summary = summarize_by_label(events, panel)
    year_summary = summarize_by_year(events, panel)
    event_counts = summarize_event_counts(events, panel)
    network_inventory = inventory(panel)

    panel_out_cols = [
        "method_variant",
        "method",
        "method_top_n",
        "time_valid_prior_year",
        "sample_name",
        "event_id",
        "event_key",
        "focal_code",
        "sec_name",
        "event_date",
        "event_year",
        "announcement_title",
        "auto_pdf_label",
        "peer_code",
        "peer_name",
        "peer_rank",
        "peer_similarity",
        "snapshot_report_year",
        "focal_industry_d",
        "peer_industry_d",
        "network_notes",
    ]
    panel[panel_out_cols].to_csv(OUT_DIR / "peer_link_panel.csv.gz", index=False)
    summary.to_csv(OUT_DIR / "peer_coverage_summary.csv", index=False)
    label_summary.to_csv(OUT_DIR / "auto_label_peer_coverage_summary.csv", index=False)
    year_summary.to_csv(OUT_DIR / "year_peer_coverage_summary.csv", index=False)
    event_counts.to_csv(OUT_DIR / "event_peer_counts_by_method.csv", index=False)
    network_inventory.to_csv(OUT_DIR / "network_inventory.csv", index=False)
    write_report(events, summary, label_summary, panel)

    print(f"wrote {OUT_DIR}")
    print(f"wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
