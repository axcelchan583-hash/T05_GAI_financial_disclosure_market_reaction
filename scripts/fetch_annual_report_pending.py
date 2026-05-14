#!/usr/bin/env python3
"""Fetch 2025 annual-report disclosure schedule and pending list.

Source interface: AkShare `stock_report_disclosure`, which wraps CNINFO's
appointment-disclosure data page.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import akshare as ak
import pandas as pd


PROJECT = Path("/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction")
RESULTS = PROJECT / "results"
DOCS = PROJECT / "docs"
AS_OF = date(2026, 4, 28)
PERIOD = "2025年报"
SOURCE_URL = "https://www.cninfo.com.cn/new/commonUrl?url=data/yypl"


def _latest_appointment(row: pd.Series) -> pd.Timestamp | pd.NaT:
    candidates = [
        row.get("三次变更"),
        row.get("二次变更"),
        row.get("初次变更"),
        row.get("首次预约"),
    ]
    for value in candidates:
        if pd.notna(value):
            return value
    return pd.NaT


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    df = ak.stock_report_disclosure(market="沪深京", period=PERIOD)
    df = df.copy()
    for col in ["首次预约", "初次变更", "二次变更", "三次变更", "实际披露"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    df["股票代码"] = df["股票代码"].astype(str).str.zfill(6)
    df["最新预约"] = df.apply(_latest_appointment, axis=1)
    df["是否已披露"] = df["实际披露"].notna()
    df["source"] = SOURCE_URL
    df["source_period"] = PERIOD
    df["retrieved_as_of"] = AS_OF.isoformat()
    df["source_status"] = df["是否已披露"].map(
        {True: "disclosed_by_source", False: "not_disclosed_by_source_actual_empty"}
    )

    # Keep B-share codes out of the default pending list for the A-share topic.
    a_share_mask = ~df["股票代码"].str.startswith(("200", "900"))
    df_a = df.loc[a_share_mask].copy()
    pending = df_a.loc[~df_a["是否已披露"]].sort_values(["最新预约", "股票代码"]).copy()

    full_path = RESULTS / "annual_report_2025_schedule_20260428.csv"
    pending_path = RESULTS / "annual_report_2025_pending_20260428.csv"
    md_path = DOCS / "annual_report_2025_pending_20260428.md"

    df_a.to_csv(full_path, index=False, encoding="utf-8-sig")
    pending.to_csv(pending_path, index=False, encoding="utf-8-sig")

    by_date = (
        pending.assign(最新预约=pending["最新预约"].dt.strftime("%Y-%m-%d").fillna("missing"))
        .groupby("最新预约", dropna=False)
        .size()
        .reset_index(name="count")
    )
    by_prefix = (
        pending.assign(code_prefix=pending["股票代码"].str[:3])
        .groupby("code_prefix")
        .size()
        .reset_index(name="count")
        .sort_values("code_prefix")
    )

    preview_cols = ["股票代码", "股票简称", "首次预约", "初次变更", "二次变更", "三次变更", "最新预约"]
    preview = pending[preview_cols].head(120).copy()
    for col in ["首次预约", "初次变更", "二次变更", "三次变更", "最新预约"]:
        preview[col] = preview[col].dt.strftime("%Y-%m-%d").fillna("")

    lines = [
        "# 2025 Annual Report Pending List",
        "",
        f"- Retrieval date: {AS_OF.isoformat()}",
        f"- Source: CNINFO appointment-disclosure data via AkShare, `{SOURCE_URL}`",
        f"- Period: {PERIOD}",
        f"- A-share-like sample after excluding 200/900 B-share codes: {len(df_a)}",
        f"- Not yet disclosed by source actual-disclosure field: {len(pending)}",
        f"- Full schedule CSV: `results/{full_path.name}`",
        f"- Pending CSV: `results/{pending_path.name}`",
        "",
        "## Pending Count by Latest Appointment Date",
        "",
        by_date.to_markdown(index=False),
        "",
        "## Pending Count by Code Prefix",
        "",
        by_prefix.to_markdown(index=False),
        "",
        "## First 120 Pending Firms",
        "",
        preview.to_markdown(index=False),
        "",
        "## Notes",
        "",
        "- `not yet disclosed` means the source has no `实际披露` date at retrieval time.",
        "- Firms scheduled on 2026-04-28 may still disclose later the same day; rerun after market close or on 2026-04-29 for a cleaner snapshot.",
        "- For final empirical work, verify annual-report PDFs from CNINFO announcements before text extraction.",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {full_path}")
    print(f"wrote {pending_path}")
    print(f"wrote {md_path}")
    print(f"pending={len(pending)} total_a={len(df_a)}")


if __name__ == "__main__":
    main()

