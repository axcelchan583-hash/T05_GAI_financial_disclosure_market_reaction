#!/usr/bin/env python3
"""Full-recall CAC registry to A-share candidate matching.

This run deliberately keeps low-confidence textual candidates. It is for manual
review and sample rescue only; do not treat the full candidate set as an event
study sample without review.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v65_registry_based_event_study_20260612 as v65  # noqa: E402


RUN_ID = "v66_registry_full_recall_matching_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "126_v66_registry_full_recall_matching_20260612.md"
OBSIDIAN_DIR = Path("/Users/mac/Documents/Obsidian Vault/23-5")
OBSIDIAN_MD = OBSIDIAN_DIR / "T05_备案主体A股全召回复核工作台_v66_20260612.md"
OBSIDIAN_CSV = OBSIDIAN_DIR / "T05_备案主体A股全召回复核队列_v66_20260612.csv"


def clip(value: object, limit: int = 180) -> str:
    text = "" if pd.isna(value) else str(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text[: limit - 1] + "…" if len(text) > limit else text


def make_lookup(companies: pd.DataFrame) -> tuple[dict[str, list[dict[str, object]]], dict[str, list[dict[str, object]]]]:
    full_lookup: dict[str, list[dict[str, object]]] = defaultdict(list)
    short_lookup: dict[str, list[dict[str, object]]] = defaultdict(list)
    for c in companies.to_dict("records"):
        full_key = str(c.get("full_key") or "")
        short_key = str(c.get("short_key") or "")
        if full_key:
            full_lookup[full_key].append(c)
        if short_key:
            short_lookup[short_key].append(c)
    return full_lookup, short_lookup


def add_candidate(
    rows: list[dict[str, object]],
    registry_row_id: str,
    candidate: dict[str, object],
    method: str,
    scope: str,
    field: str,
    match_text: str,
    rank: int,
    match_len: int,
) -> None:
    rows.append(
        {
            "registry_row_id": registry_row_id,
            "stock_code": candidate["stock_code"],
            "stock_name": candidate["stock_name"],
            "full_name": candidate["full_name"],
            "industry_c": candidate["industry_c"],
            "industry_d": candidate["industry_d"],
            "listing_state": candidate["listing_state"],
            "match_scope": scope,
            "match_field": field,
            "match_method": method,
            "match_text": match_text,
            "match_rank": rank,
            "match_len": match_len,
        }
    )


def substrings(text: str, min_len: int, max_len: int) -> set[str]:
    out: set[str] = set()
    upper = min(max_len, len(text))
    for length in range(min_len, upper + 1):
        for start in range(0, len(text) - length + 1):
            out.add(text[start : start + length])
    return out


def build_all_candidates(reg: pd.DataFrame, companies: pd.DataFrame) -> pd.DataFrame:
    full_lookup, short_lookup = make_lookup(companies)
    max_full_len = max((len(k) for k in full_lookup), default=0)
    max_short_len = max((len(k) for k in short_lookup), default=0)
    rows: list[dict[str, object]] = []

    text_fields = ["item_name", "application_product", "main_purpose", "comments"]
    for rec in reg.to_dict("records"):
        row_id = str(rec["registry_row_id"])
        entity = str(rec.get("entity_key") or "")
        if entity:
            for c in full_lookup.get(entity, []):
                add_candidate(rows, row_id, c, "full_name_exact", "entity_name", "entity_name", entity, 100, len(entity))

            for part in substrings(entity, 6, max_full_len):
                if part == entity:
                    continue
                for c in full_lookup.get(part, []):
                    add_candidate(rows, row_id, c, "full_name_contained", "entity_name", "entity_name", part, 90, len(part))

            for length in range(2, min(max_short_len, len(entity)) + 1):
                prefix = entity[:length]
                for c in short_lookup.get(prefix, []):
                    next_char = entity[length : length + 1]
                    if next_char in v65.BAD_PREFIX_NEXT_CHARS:
                        method = "short_name_prefix_risky_next_char"
                        rank = 50 if length == 2 else 68
                    elif length == len(str(c.get("short_key") or "")) and length == len(entity):
                        method = "short_name_exact_entity"
                        rank = 88
                    elif length >= 4:
                        method = "short_name_prefix_len4plus"
                        rank = 82
                    elif length == 3:
                        method = "short_name_prefix_len3"
                        rank = 76
                    else:
                        method = "short_name_prefix_len2"
                        rank = 50
                    add_candidate(rows, row_id, c, method, "entity_name", "entity_name", prefix, rank, length)

            for part in substrings(entity, 2, max_short_len):
                if entity.startswith(part):
                    continue
                for c in short_lookup.get(part, []):
                    if len(part) >= 4:
                        method = "short_name_contained_len4plus"
                        rank = 70
                    elif len(part) == 3:
                        method = "short_name_contained_len3"
                        rank = 54
                    else:
                        method = "short_name_contained_len2"
                        rank = 38
                    add_candidate(rows, row_id, c, method, "entity_name", "entity_name", part, rank, len(part))

        for field in text_fields:
            text = v65.clean_name(rec.get(field, ""))
            if not text:
                continue
            for part in substrings(text, 3, max_short_len):
                for c in short_lookup.get(part, []):
                    if len(part) >= 4:
                        rank = 34
                        method = "stock_short_in_item_text_len4plus"
                    else:
                        rank = 24
                        method = "stock_short_in_item_text_len3"
                    add_candidate(rows, row_id, c, method, "item_product_text", field, part, rank, len(part))

    if not rows:
        return pd.DataFrame()
    cand = pd.DataFrame(rows)
    cand = (
        cand.sort_values(
            ["registry_row_id", "stock_code", "match_rank", "match_len"],
            ascending=[True, True, False, False],
        )
        .drop_duplicates(["registry_row_id", "stock_code", "match_scope", "match_method", "match_text"], keep="first")
        .copy()
    )
    return cand


def merge_registry(candidates: pd.DataFrame, reg: pd.DataFrame) -> pd.DataFrame:
    keep = [
        "registry_row_id",
        "registry_source",
        "registry_source_label",
        "source_batch",
        "registry_status",
        "registry_role",
        "entity_name",
        "item_name",
        "item_type",
        "application_product",
        "main_purpose",
        "filing_no",
        "filing_date",
        "event_date",
        "event_clock",
        "jurisdiction",
        "comments",
        "model_keyword_hit",
        "source_label",
        "source_url",
        "source_file",
        "source_locator",
    ]
    out = candidates.merge(reg[keep], on="registry_row_id", how="left")
    out["focal_code"] = out["stock_code"].map(v65.z6)
    out["event_date"] = pd.to_datetime(out["event_date"], errors="coerce")
    out["source_item_key"] = out[["registry_source", "filing_no", "item_name", "event_date"]].astype(str).agg("::".join, axis=1)
    return out.sort_values(["registry_row_id", "match_rank", "match_len", "stock_code"], ascending=[True, False, False, True]).reset_index(drop=True)


def row_summary(reg: pd.DataFrame, matched: pd.DataFrame) -> pd.DataFrame:
    if matched.empty:
        base = reg.copy()
        base["candidate_pairs"] = 0
        return base

    agg = (
        matched.groupby("registry_row_id", as_index=False)
        .agg(
            candidate_pairs=("stock_code", "size"),
            candidate_firms=("stock_code", "nunique"),
            entity_candidate_pairs=("match_scope", lambda s: int((s == "entity_name").sum())),
            text_candidate_pairs=("match_scope", lambda s: int((s == "item_product_text").sum())),
            best_rank=("match_rank", "max"),
            best_match_len=("match_len", "max"),
            top_candidates=(
                "stock_code",
                lambda s: "；".join(
                    matched.loc[s.index]
                    .sort_values(["match_rank", "match_len", "stock_code"], ascending=[False, False, True])
                    .assign(label=lambda d: d["stock_code"] + " " + d["stock_name"] + "(" + d["match_method"] + ")")
                    ["label"]
                    .head(8)
                    .tolist()
                ),
            ),
        )
        .copy()
    )
    out = reg.merge(agg, on="registry_row_id", how="left")
    for col in ["candidate_pairs", "candidate_firms", "entity_candidate_pairs", "text_candidate_pairs"]:
        out[col] = out[col].fillna(0).astype(int)
    out["best_rank"] = out["best_rank"].fillna(0).astype(int)
    out["best_match_len"] = out["best_match_len"].fillna(0).astype(int)
    out["top_candidates"] = out["top_candidates"].fillna("")
    return out


def best_tier(matched: pd.DataFrame) -> pd.DataFrame:
    if matched.empty:
        return matched
    keys = ["registry_row_id"]
    best = matched.groupby(keys, as_index=False).agg(best_rank=("match_rank", "max"))
    tmp = matched.merge(best, on=keys, how="inner")
    tmp = tmp[tmp["match_rank"].eq(tmp["best_rank"])].copy()
    best_len = tmp.groupby(keys, as_index=False).agg(best_match_len=("match_len", "max"))
    tmp = tmp.merge(best_len, on=keys, how="inner")
    tmp = tmp[tmp["match_len"].eq(tmp["best_match_len"])].copy()
    return tmp.drop(columns=["best_rank", "best_match_len"]).copy()


def coverage_tables(reg: pd.DataFrame, matched: pd.DataFrame, summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    matched_by_source = (
        matched.groupby("registry_source", as_index=False)
        .agg(
            rows_with_candidates=("registry_row_id", "nunique"),
            candidate_pairs=("stock_code", "size"),
            candidate_firms=("stock_code", "nunique"),
        )
    )
    by_source = (
        reg.groupby("registry_source", as_index=False)
        .agg(registry_rows=("registry_row_id", "size"), registry_entities=("entity_name", "nunique"))
        .merge(matched_by_source, on="registry_source", how="left")
        .fillna(0)
    )
    by_status = (
        summary.groupby(["registry_source", "registry_status"], as_index=False)
        .agg(
            registry_rows=("registry_row_id", "size"),
            rows_with_candidates=("candidate_pairs", lambda s: int((s > 0).sum())),
            candidate_pairs=("candidate_pairs", "sum"),
        )
        .sort_values(["registry_source", "registry_status"])
    )
    by_method = (
        matched.groupby(["match_scope", "match_method"], as_index=False)
        .agg(candidate_pairs=("stock_code", "size"), registry_rows=("registry_row_id", "nunique"), firms=("stock_code", "nunique"))
        .sort_values(["match_scope", "candidate_pairs"], ascending=[True, False])
    )
    return by_source, by_status, by_method


def review_priority(row: pd.Series) -> str:
    method = str(row["match_method"])
    scope = str(row["match_scope"])
    rank = int(row["match_rank"])
    firms_for_row = int(row.get("firms_for_registry_row", 0))
    if method == "full_name_exact":
        return "P3-全称精确保留抽查"
    if scope == "item_product_text":
        return "P1-仅项目/产品文本命中"
    if rank < 55:
        return "P0-极低置信名称召回"
    if "contained_len2" in method or "prefix_len2" in method:
        return "P0-二字简称极易误配"
    if "risky_next_char" in method:
        return "P0-行政区/通用前缀风险"
    if firms_for_row > 1:
        return "P0-同一备案多候选"
    if "contained" in method:
        return "P0-简称/全称包含需核"
    if "prefix" in method:
        return "P1-简称前缀需核"
    return "P2-其他候选抽查"


def build_review_queue(matched: pd.DataFrame) -> pd.DataFrame:
    if matched.empty:
        return matched
    counts = matched.groupby("registry_row_id")["stock_code"].nunique().rename("firms_for_registry_row").reset_index()
    q = matched.merge(counts, on="registry_row_id", how="left")
    q["review_priority"] = q.apply(review_priority, axis=1)
    q["review_status"] = ""
    q["manual_relation"] = ""
    q["keep_flag"] = ""
    q["correct_stock_code"] = ""
    q["correct_stock_name"] = ""
    q["manual_reason"] = ""
    q["reviewer"] = ""
    q["review_date"] = ""
    first_cols = [
        "review_priority",
        "review_status",
        "manual_relation",
        "keep_flag",
        "correct_stock_code",
        "correct_stock_name",
        "manual_reason",
        "reviewer",
        "review_date",
    ]
    rest = [c for c in q.columns if c not in first_cols]
    return q[first_cols + rest].sort_values(
        ["review_priority", "registry_source", "registry_row_id", "match_rank", "match_len", "stock_code"],
        ascending=[True, True, True, False, False, True],
    )


def md_table(df: pd.DataFrame, cols: list[str] | None = None, limit: int = 50) -> str:
    return v65.md_table(df, cols=cols, limit=limit)


def write_docs(
    reg: pd.DataFrame,
    matched: pd.DataFrame,
    summary: pd.DataFrame,
    best: pd.DataFrame,
    by_source: pd.DataFrame,
    by_status: pd.DataFrame,
    by_method: pd.DataFrame,
    review_queue: pd.DataFrame,
) -> None:
    genai = summary[summary["registry_source"].eq("cac_genai_service")].copy()
    genai_status = by_status[by_status["registry_source"].eq("cac_genai_service")].copy()
    sample_cols = [
        "review_priority",
        "registry_source",
        "registry_status",
        "entity_name",
        "item_name",
        "focal_code",
        "stock_name",
        "match_scope",
        "match_method",
        "match_text",
        "match_rank",
        "firms_for_registry_row",
    ]
    examples = review_queue[review_queue["review_priority"].str.startswith("P0")].head(80)
    lines = [
        "# v66 Registry Full-Recall Matching",
        "",
        "## Scope",
        "",
        "- Input: v64 official CAC GenAI-relevant registry master.",
        "- Purpose: recall every textual A-share candidate, including low-confidence name and model/app-text hits.",
        "- Guardrail: this is a manual-review universe, not a clean event-study sample.",
        "",
        "## Files",
        "",
        f"- `results/{RUN_ID}/registry_all_candidate_matches.csv`",
        f"- `results/{RUN_ID}/registry_row_candidate_summary.csv`",
        f"- `results/{RUN_ID}/registry_best_tier_candidates_keep_ties.csv`",
        f"- `results/{RUN_ID}/registry_full_recall_review_queue.csv`",
        f"- `{OBSIDIAN_MD}`",
        f"- `{OBSIDIAN_CSV}`",
        "",
        "## Counts By Source",
        "",
        md_table(by_source),
        "",
        "## Counts By Status",
        "",
        md_table(by_status),
        "",
        "## Candidate Methods",
        "",
        md_table(by_method, limit=80),
        "",
        "## GenAI Service Rows",
        "",
        md_table(
            genai_status,
            cols=["registry_source", "registry_status", "registry_rows", "rows_with_candidates", "candidate_pairs"],
        ),
        "",
        "## P0 Examples",
        "",
        md_table(examples, cols=sample_cols, limit=80),
        "",
    ]
    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")

    priority = (
        review_queue.groupby("review_priority", as_index=False)
        .agg(candidate_pairs=("stock_code", "size"), registry_rows=("registry_row_id", "nunique"), firms=("stock_code", "nunique"))
        .sort_values("review_priority")
    )
    obs_lines = [
        "---",
        "project: T05",
        "purpose: CAC registry full-recall A-share candidate review",
        "created: 2026-06-12",
        f"run_id: {RUN_ID}",
        f"registry_rows: {len(reg)}",
        f"candidate_pairs: {len(matched)}",
        f"rows_with_candidates: {int((summary['candidate_pairs'] > 0).sum())}",
        f"full_queue_csv: {OBSIDIAN_CSV.name}",
        "---",
        "",
        "# T05 备案主体-A股全召回复核工作台（v66）",
        "",
        "这份笔记是召回池，不是最终样本。当前目标是先把所有可能相关的 A 股候选摊开，后面人工标记 `keep/drop/revise`。",
        "",
        "每条候选先填：",
        "",
        "```text",
        "复核: 通过 | 不通过 | 存疑",
        "关系: 直接上市主体 | 控股子公司/分公司 | 同集团非上市主体 | 项目/产品文本相关 | 无关误配",
        "处理: keep_direct | keep_subsidiary | keep_text_link | drop_uncertain | drop_false | revise_code",
        "修正代码: ",
        "人工理由: ",
        "```",
        "",
        "## 路径",
        "",
        f"- v66 结果文档：`{DOC_PATH}`",
        f"- 完整复核 CSV：`{OBSIDIAN_CSV}`",
        f"- 全候选 CSV：`{OUT_DIR / 'registry_all_candidate_matches.csv'}`",
        f"- 每条备案汇总：`{OUT_DIR / 'registry_row_candidate_summary.csv'}`",
        "",
        "## 总览",
        "",
        f"- 官方备案记录：{len(reg)}",
        f"- 有至少一个 A 股候选的备案记录：{int((summary['candidate_pairs'] > 0).sum())}",
        f"- A 股候选对：{len(matched)}",
        f"- best-tier 候选对（保留并列）：{len(best)}",
        f"- 生成式 AI 服务备案/登记原始记录：{len(genai)}",
        f"- 生成式 AI 服务有候选记录：{int((genai['candidate_pairs'] > 0).sum())}",
        "",
        "## 来源覆盖",
        "",
        md_table(by_source),
        "",
        "## 生成式 AI 服务按状态",
        "",
        md_table(genai_status, cols=["registry_status", "registry_rows", "rows_with_candidates", "candidate_pairs"]),
        "",
        "## 匹配方式",
        "",
        md_table(by_method, limit=80),
        "",
        "## 复核优先级",
        "",
        md_table(priority),
        "",
        "## P0 样例",
        "",
        "完整队列见同目录 CSV。这里先列 P0 前 80 条，方便快速感受噪音来源。",
        "",
        md_table(examples, cols=sample_cols, limit=80),
        "",
    ]
    OBSIDIAN_DIR.mkdir(parents=True, exist_ok=True)
    OBSIDIAN_MD.write_text("\n".join(obs_lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reg = v65.load_registry()
    companies = v65.load_company_info()
    candidates = build_all_candidates(reg, companies)
    matched = merge_registry(candidates, reg)
    summary = row_summary(reg, matched)
    best = best_tier(matched)
    by_source, by_status, by_method = coverage_tables(reg, matched, summary)
    review_queue = build_review_queue(matched)

    matched.to_csv(OUT_DIR / "registry_all_candidate_matches.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT_DIR / "registry_row_candidate_summary.csv", index=False, encoding="utf-8-sig")
    best.to_csv(OUT_DIR / "registry_best_tier_candidates_keep_ties.csv", index=False, encoding="utf-8-sig")
    by_source.to_csv(OUT_DIR / "registry_full_recall_coverage_by_source.csv", index=False, encoding="utf-8-sig")
    by_status.to_csv(OUT_DIR / "registry_full_recall_coverage_by_status.csv", index=False, encoding="utf-8-sig")
    by_method.to_csv(OUT_DIR / "registry_full_recall_candidate_methods.csv", index=False, encoding="utf-8-sig")
    review_queue.to_csv(OUT_DIR / "registry_full_recall_review_queue.csv", index=False, encoding="utf-8-sig")
    review_queue.to_csv(OBSIDIAN_CSV, index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(OUT_DIR / f"{RUN_ID}.xlsx") as writer:
        by_source.to_excel(writer, sheet_name="Coverage_by_source", index=False)
        by_status.to_excel(writer, sheet_name="Coverage_by_status", index=False)
        by_method.to_excel(writer, sheet_name="Methods", index=False)
        summary.to_excel(writer, sheet_name="Registry_row_summary", index=False)
        best.head(200000).to_excel(writer, sheet_name="Best_tier_keep_ties", index=False)
        review_queue.head(200000).to_excel(writer, sheet_name="Review_queue", index=False)

    write_docs(reg, matched, summary, best, by_source, by_status, by_method, review_queue)

    print("run_id", RUN_ID)
    print("registry_rows", len(reg))
    print("candidate_pairs", len(matched))
    print("rows_with_candidates", int((summary["candidate_pairs"] > 0).sum()))
    print("best_tier_pairs", len(best))
    print("doc", DOC_PATH)
    print("obsidian_md", OBSIDIAN_MD)
    print("obsidian_csv", OBSIDIAN_CSV)


if __name__ == "__main__":
    main()
