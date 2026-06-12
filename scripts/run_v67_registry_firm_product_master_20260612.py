#!/usr/bin/env python3
"""Build the v67 registry firm-product master for CAC verification design v2."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_v65_registry_based_event_study_20260612 as v65  # noqa: E402


RUN_ID = "v67_registry_firm_product_master_20260612"
OUT_DIR = ROOT / "results" / RUN_ID
DOC_PATH = ROOT / "docs" / "empirical_runs" / "127_v67_registry_firm_product_master_20260612.md"

REGISTRY_PATH = ROOT / "results/v64_official_registry_master_20260612/official_registry_master_genai_relevant_subset.csv"
V66_CANDIDATES = ROOT / "results/v66_registry_full_recall_matching_20260612/registry_all_candidate_matches.csv"


GENAI_BATCH_PUBLIC = {
    "2024-04": ("2024-04-02 17:00:00", "official_page_date", "https://www.cac.gov.cn/2024-04/02/c_1713729983803145.htm"),
    "2024-08": ("2024-08-08 16:00:19", "pdf_metadata_proxy", "https://www.cac.gov.cn/2024-04/02/c_1713729983803145.htm"),
    "2024-11": ("2024-11-20 16:33:49", "pdf_metadata_proxy", "https://www.cac.gov.cn/2024-04/02/c_1713729983803145.htm"),
    "2025-01": ("2025-01-08 19:47:00", "official_page_date", "https://www.cac.gov.cn/2025-01/08/c_1738034725920930.htm"),
    "2025-03": ("2025-04-08 17:00:00", "official_page_date", "https://www.cac.gov.cn/2025-04/08/c_1745817775881843.htm"),
    "2025-06": ("2025-07-11 20:20:00", "official_page_date", "https://www.cac.gov.cn/2025-07/11/c_1753948489002783.htm"),
    "2025-08": ("2025-09-10 20:05:00", "official_page_date", "https://www.cac.gov.cn/2025-09/10/c_1759222982377536.htm"),
    "2025-10": ("2025-11-11 18:30:00", "official_page_date", "https://www.cac.gov.cn/2025-11/11/c_1764585284364412.htm"),
    "2025-12": ("2026-01-09 18:30:00", "official_page_date", "https://www.cac.gov.cn/2026-01/09/c_1769688009588554.htm"),
    "2026-02": ("2026-03-17 19:36:00", "official_page_date", "https://www.cac.gov.cn/2026-03/17/c_1775482074695536.htm"),
    "2026-04": ("2026-05-13 17:31:06", "official_page_date", "https://www.cac.gov.cn/2026-05/13/c_1780406330282017.htm"),
}


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, low_memory=False).fillna("")


def product_id(source: str, filing_no: str) -> str:
    key = f"{source}::{filing_no}".strip()
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def load_public_date_maps() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for batch, (dt, precision, url) in GENAI_BATCH_PUBLIC.items():
        rows.append(
            {
                "registry_source": "cac_genai_service",
                "source_batch": batch,
                "batch_public_datetime": dt,
                "batch_public_date_precision": precision,
                "batch_public_source_url": url,
            }
        )

    deep_manifest = ROOT / "data/raw/cac_deep_synthesis_filing/attachments_manifest.csv"
    if deep_manifest.exists():
        deep = read_csv(deep_manifest)
        for _, row in deep.iterrows():
            rows.append(
                {
                    "registry_source": "cac_deep_synthesis_filing",
                    "source_batch": row["batch"],
                    "batch_public_datetime": row["notice_create_time"],
                    "batch_public_date_precision": "official_notice_create_time",
                    "batch_public_source_url": row["source_page_url"],
                }
            )

    algo_manifest = ROOT / "data/raw/cac_algorithm_filing/attachments_manifest.csv"
    if algo_manifest.exists():
        algo = read_csv(algo_manifest)
        for _, row in algo.iterrows():
            # The ordinary algorithm index page does not preserve a per-attachment first-public date.
            # Use month-end as a conservative proxy and keep the precision flag visible.
            batch_date = pd.to_datetime(row["batch"] + "-01", errors="coerce") + pd.offsets.MonthEnd(0)
            rows.append(
                {
                    "registry_source": "cac_algorithm_filing",
                    "source_batch": row["batch"],
                    "batch_public_datetime": f"{batch_date:%Y-%m-%d} 23:59:59" if pd.notna(batch_date) else "",
                    "batch_public_date_precision": "source_batch_month_end_proxy",
                    "batch_public_source_url": row["url"],
                }
            )
    out = pd.DataFrame(rows)
    out["batch_public_datetime"] = pd.to_datetime(out["batch_public_datetime"], errors="coerce")
    out["batch_public_date"] = out["batch_public_datetime"].dt.date.astype(str).replace("NaT", "")
    return out


def verification_type(row: pd.Series) -> str:
    source = row["registry_source"]
    status = row["registry_status"]
    if source == "cac_genai_service" and status == "已备案":
        return "self_filing"
    if source == "cac_genai_service" and status == "已登记":
        return "app_registration"
    if source == "cac_deep_synthesis_filing":
        return "deep_synthesis"
    if source == "cac_algorithm_filing":
        return "ordinary_algorithm_genai_keyword"
    return "other"


def confidence_bucket(row: pd.Series) -> str:
    method = row.get("match_method", "")
    rank = int(float(row.get("match_rank", 0) or 0))
    scope = row.get("match_scope", "")
    if method == "full_name_exact":
        return "high"
    if method == "full_name_contained":
        return "medium"
    if scope == "entity_name" and rank >= 70:
        return "medium"
    if scope == "item_product_text":
        return "text_only_low"
    return "low"


def relation_guess(row: pd.Series) -> str:
    method = row.get("match_method", "")
    if method == "full_name_exact":
        return "direct"
    if method == "full_name_contained":
        return "branch_or_subunit_candidate"
    if row.get("match_scope", "") == "item_product_text":
        return "product_text_only"
    return "name_similarity_candidate"


def build_registry_products(reg: pd.DataFrame, public_dates: pd.DataFrame) -> pd.DataFrame:
    products = reg.copy()
    products["registry_row_id"] = [f"REGROW{i + 1:05d}" for i in range(len(products))]
    products["registry_product_id"] = [product_id(s, f) for s, f in zip(products["registry_source"], products["filing_no"])]
    products["verification_type"] = products.apply(verification_type, axis=1)
    products = products.merge(public_dates, on=["registry_source", "source_batch"], how="left")
    products["batch_public_datetime"] = pd.to_datetime(products["batch_public_datetime"], errors="coerce")
    products["batch_public_date"] = products["batch_public_datetime"].dt.date.astype(str).replace("NaT", "")
    products["filing_date_dt"] = pd.to_datetime(products["filing_date"], errors="coerce")
    products["pre_registry_era"] = (
        products["registry_source"].eq("cac_deep_synthesis_filing")
        & products["batch_public_datetime"].lt(pd.Timestamp("2023-08-15"))
    ).astype(int)
    return products


def build_status_history(products: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "registry_product_id",
        "registry_source",
        "filing_no",
        "registry_status",
        "verification_type",
        "source_batch",
        "batch_public_date",
        "batch_public_datetime",
        "batch_public_date_precision",
        "batch_public_source_url",
        "source_label",
        "source_url",
        "source_file",
    ]
    hist = products[cols].drop_duplicates().sort_values(["registry_product_id", "batch_public_datetime", "source_batch"])
    return hist


def build_candidates(products: pd.DataFrame) -> pd.DataFrame:
    if not V66_CANDIDATES.exists():
        raise FileNotFoundError(f"Run v66 first: {V66_CANDIDATES}")
    cand = read_csv(V66_CANDIDATES)
    cand = cand.drop(columns=[c for c in ["batch_public_date", "batch_public_datetime"] if c in cand.columns], errors="ignore")
    keep_cols = [
        "registry_row_id",
        "registry_product_id",
        "verification_type",
        "batch_public_date",
        "batch_public_datetime",
        "batch_public_date_precision",
        "batch_public_source_url",
        "pre_registry_era",
    ]
    keys = products[keep_cols].copy()
    out = cand.merge(keys, on="registry_row_id", how="left")
    out["match_confidence"] = out.apply(confidence_bucket, axis=1)
    out["relation_to_listed"] = out.apply(relation_guess, axis=1)
    out["listed_code"] = out["stock_code"].map(v65.z6)
    out["listed_name"] = out["stock_name"]
    return out


def build_master(candidates: pd.DataFrame) -> pd.DataFrame:
    master = candidates[candidates["match_confidence"].isin(["high", "medium"])].copy()
    master = master.sort_values(
        ["registry_product_id", "listed_code", "match_rank", "match_len"],
        ascending=[True, True, False, False],
    ).drop_duplicates(["registry_product_id", "listed_code"], keep="first")
    cols = [
        "registry_product_id",
        "registry_source",
        "registry_status",
        "verification_type",
        "pre_registry_era",
        "entity_name",
        "item_name",
        "application_product",
        "main_purpose",
        "filing_no",
        "filing_date",
        "source_batch",
        "batch_public_date",
        "batch_public_datetime",
        "batch_public_date_precision",
        "batch_public_source_url",
        "listed_code",
        "listed_name",
        "full_name",
        "relation_to_listed",
        "match_method",
        "match_scope",
        "match_text",
        "match_rank",
        "match_len",
        "match_confidence",
        "source_label",
        "source_url",
        "source_file",
        "source_locator",
    ]
    return master[cols]


def build_review_queue(candidates: pd.DataFrame) -> pd.DataFrame:
    q = candidates.copy()
    q["review_priority"] = q["match_confidence"].map(
        {
            "high": "P3-高置信抽查",
            "medium": "P1-中置信主体关系复核",
            "text_only_low": "P0-仅产品文本命中",
            "low": "P0-低置信名称召回",
        }
    ).fillna("P0-待判")
    q["review_status"] = ""
    q["manual_relation"] = ""
    q["keep_flag"] = ""
    q["correct_stock_code"] = ""
    q["correct_stock_name"] = ""
    q["manual_reason"] = ""
    q["reviewer"] = ""
    q["review_date"] = ""
    front = [
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
    rest = [c for c in q.columns if c not in front]
    return q[front + rest].sort_values(
        ["review_priority", "registry_source", "registry_product_id", "match_rank", "match_len", "stock_code"],
        ascending=[True, True, True, False, False, True],
    )


def md_table(df: pd.DataFrame, limit: int = 40) -> str:
    if df.empty:
        return "_No rows._"
    show = df.head(limit).copy()
    lines = ["| " + " | ".join(show.columns) + " |", "|" + "|".join("---" for _ in show.columns) + "|"]
    for _, row in show.iterrows():
        lines.append("| " + " | ".join("" if pd.isna(row[c]) else str(row[c]).replace("|", "\\|") for c in show.columns) + " |")
    return "\n".join(lines)


def write_doc(products: pd.DataFrame, master: pd.DataFrame, candidates: pd.DataFrame, status_history: pd.DataFrame) -> None:
    source_counts = (
        products.groupby(["registry_source", "registry_status", "verification_type"], as_index=False)
        .agg(products=("registry_product_id", "nunique"), entities=("entity_name", "nunique"))
        .sort_values(["registry_source", "registry_status"])
    )
    listed_counts = (
        master.groupby(["registry_source", "registry_status", "verification_type"], as_index=False)
        .agg(firm_product_rows=("registry_product_id", "size"), products=("registry_product_id", "nunique"), firms=("listed_code", "nunique"))
        .sort_values(["registry_source", "registry_status"])
    )
    date_precision = (
        products.groupby(["registry_source", "batch_public_date_precision"], as_index=False)
        .agg(products=("registry_product_id", "nunique"))
        .sort_values(["registry_source", "batch_public_date_precision"])
    )
    match_counts = (
        candidates.groupby(["match_confidence", "match_scope", "match_method"], as_index=False)
        .agg(candidate_pairs=("stock_code", "size"), products=("registry_product_id", "nunique"), firms=("stock_code", "nunique"))
        .sort_values(["match_confidence", "candidate_pairs"], ascending=[True, False])
    )
    lines = [
        "# v67 Registry Firm-Product Master",
        "",
        "## Scope",
        "",
        "- Implements the first execution step for `15_registry_verified_adoption_experiment_design_v2_20260612.md`.",
        "- Builds stable `registry_product_id = sha1(registry_source + filing_no)`.",
        "- Adds `batch_public_date` and its precision/source flag.",
        "- Keeps GenAI `已登记` as adoption verification, not self-developed model verification.",
        "",
        "## Outputs",
        "",
        f"- `results/{RUN_ID}/registry_products_all.csv`",
        f"- `results/{RUN_ID}/registry_status_history.csv`",
        f"- `results/{RUN_ID}/registry_firm_product_candidates_all.csv`",
        f"- `results/{RUN_ID}/registry_firm_product_master.csv`",
        f"- `results/{RUN_ID}/registry_product_match_review_queue.csv`",
        "",
        "## Counts",
        "",
        f"- Registry source rows: {len(products)}",
        f"- Unique registry products: {products['registry_product_id'].nunique()}",
        f"- Candidate firm-product pairs, all recall: {len(candidates)}",
        f"- Preliminary high/medium firm-product master rows: {len(master)}",
        f"- Preliminary listed firms: {master['listed_code'].nunique()}",
        "",
        "## Product Counts By Source",
        "",
        md_table(source_counts, limit=80),
        "",
        "## Preliminary Listed Firm-Product Counts",
        "",
        md_table(listed_counts, limit=80),
        "",
        "## Batch Public Date Precision",
        "",
        md_table(date_precision, limit=80),
        "",
        "## Candidate Match Counts",
        "",
        md_table(match_counts, limit=80),
        "",
        "## Caveat",
        "",
        "For GenAI service attachments 2024-08 and 2024-11, no separate CAC article page was found in the local archive; the first-public date uses PDF metadata proxy and is flagged accordingly. Ordinary algorithm filing dates use source-batch month-end proxy.",
        "",
    ]
    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reg = read_csv(REGISTRY_PATH)
    public_dates = load_public_date_maps()
    products = build_registry_products(reg, public_dates)
    status_history = build_status_history(products)
    candidates = build_candidates(products)
    master = build_master(candidates)
    review_queue = build_review_queue(candidates)

    products.to_csv(OUT_DIR / "registry_products_all.csv", index=False, encoding="utf-8-sig")
    status_history.to_csv(OUT_DIR / "registry_status_history.csv", index=False, encoding="utf-8-sig")
    candidates.to_csv(OUT_DIR / "registry_firm_product_candidates_all.csv", index=False, encoding="utf-8-sig")
    master.to_csv(OUT_DIR / "registry_firm_product_master.csv", index=False, encoding="utf-8-sig")
    review_queue.to_csv(OUT_DIR / "registry_product_match_review_queue.csv", index=False, encoding="utf-8-sig")
    public_dates.to_csv(OUT_DIR / "registry_batch_public_dates.csv", index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(OUT_DIR / f"{RUN_ID}.xlsx") as writer:
        products.head(200000).to_excel(writer, sheet_name="Registry_products", index=False)
        master.head(200000).to_excel(writer, sheet_name="Firm_product_master", index=False)
        review_queue.head(200000).to_excel(writer, sheet_name="Review_queue", index=False)
        status_history.head(200000).to_excel(writer, sheet_name="Status_history", index=False)
        public_dates.to_excel(writer, sheet_name="Batch_public_dates", index=False)

    write_doc(products, master, candidates, status_history)

    print("run_id", RUN_ID)
    print("registry_source_rows", len(products))
    print("unique_registry_products", products["registry_product_id"].nunique())
    print("all_candidate_pairs", len(candidates))
    print("preliminary_master_rows", len(master))
    print("preliminary_master_firms", master["listed_code"].nunique())
    print("doc", DOC_PATH)


if __name__ == "__main__":
    main()
