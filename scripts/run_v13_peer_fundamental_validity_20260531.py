#!/usr/bin/env python3
"""Fundamental comovement gate for peer systems.

Uses CSMAR income-statement data to test whether candidate peer portfolios
comove with focal firms in sales growth and gross margin. This mirrors the
peer-validity logic in peer-identification papers: valid product-market peers
should share operating fundamentals, not just stock returns.
"""

from __future__ import annotations

import math
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from run_v13_peer_validity_gate_20260531 import (
    ANNUAL_GLOBAL,
    ANNUAL_SAME,
    ANNUAL_STRIPPED,
    CSMAR_SCOPE,
    INDUSTRY_PLACEBO,
    OUT_DIR,
    code6,
    normalize_pairs,
)


ROOT = Path(__file__).resolve().parents[1]
FIN_ZIP = Path(
    "/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/"
    "上市公司财务信息/利润表105632229(仅供四川大学使用).zip"
)
FUND_DOC = ROOT / "docs" / "empirical_runs" / "70_v13_peer_fundamental_validity_20260531.md"
FUND_CACHE = OUT_DIR / "financials_fs_comins_annual_metrics.csv.gz"


def load_financials() -> pd.DataFrame:
    if FUND_CACHE.exists():
        return pd.read_csv(FUND_CACHE, dtype={"stock_code": str})
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(FIN_ZIP) as zf:
        xlsx = [n for n in zf.namelist() if n.endswith(".xlsx")][0]
        extract_dir = OUT_DIR / "_tmp_extract"
        extract_dir.mkdir(parents=True, exist_ok=True)
        path = extract_dir / Path(xlsx).name
        if not path.exists():
            zf.extract(xlsx, extract_dir)
    usecols = ["Stkcd", "ShortName", "Accper", "Typrep", "B001100000", "B001101000", "B001201000"]
    raw = pd.read_excel(path, usecols=usecols, header=0, skiprows=[1, 2])
    raw = raw.rename(
        columns={
            "Stkcd": "stock_code",
            "ShortName": "short_name",
            "Accper": "accper",
            "Typrep": "typrep",
            "B001100000": "total_revenue",
            "B001101000": "operating_revenue",
            "B001201000": "operating_cost",
        }
    )
    raw["stock_code"] = raw["stock_code"].map(code6)
    raw["accper"] = pd.to_datetime(raw["accper"], errors="coerce")
    raw = raw[raw["stock_code"].ne("") & raw["accper"].notna()].copy()
    raw = raw[raw["typrep"].astype(str).str.upper().eq("A")].copy()
    raw = raw[raw["accper"].dt.month.eq(12) & raw["accper"].dt.day.eq(31)].copy()
    raw["fiscal_year"] = raw["accper"].dt.year.astype(int)
    for col in ["total_revenue", "operating_revenue", "operating_cost"]:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")
    raw["revenue"] = raw["operating_revenue"].where(raw["operating_revenue"].gt(0), raw["total_revenue"])
    raw["gross_margin"] = np.where(
        raw["revenue"].gt(0) & raw["operating_cost"].notna(),
        (raw["revenue"] - raw["operating_cost"]) / raw["revenue"],
        np.nan,
    )
    raw = raw.sort_values(["stock_code", "fiscal_year"])
    raw["log_revenue"] = np.where(raw["revenue"].gt(0), np.log(raw["revenue"]), np.nan)
    raw["sales_growth"] = raw.groupby("stock_code")["log_revenue"].diff()
    out = raw[
        ["stock_code", "short_name", "fiscal_year", "revenue", "sales_growth", "gross_margin"]
    ].copy()
    out = out[out["fiscal_year"].between(2021, 2025)].copy()
    out.to_csv(FUND_CACHE, index=False, compression="gzip")
    return out


def load_static_peer_systems() -> dict[str, pd.DataFrame]:
    systems: dict[str, pd.DataFrame] = {}
    csmar = pd.read_csv(CSMAR_SCOPE, dtype={"focal_code": str, "peer_code": str})
    systems["csmar_scope_top5"] = normalize_pairs(csmar, "csmar_scope", 5)
    systems["csmar_scope_top10"] = normalize_pairs(csmar, "csmar_scope", 10)
    placebo = pd.read_csv(INDUSTRY_PLACEBO, dtype={"focal_code": str, "peer_code": str})
    for group in ["random_same_industry", "low_similarity_same_industry"]:
        sub = placebo[placebo["peer_group"].eq(group)].copy()
        systems[f"{group}_top5"] = normalize_pairs(sub, group, 5)
        systems[f"{group}_top10"] = normalize_pairs(sub, group, 10)
    return systems


def load_annual_peer_systems() -> dict[str, pd.DataFrame]:
    systems = {}
    for key, path, source in [
        ("annual_same_industry", ANNUAL_SAME, "annual_same_industry"),
        ("annual_global", ANNUAL_GLOBAL, "annual_global"),
        ("annual_global_ai_stripped", ANNUAL_STRIPPED, "annual_global_ai_stripped"),
    ]:
        df = pd.read_csv(path, dtype={"focal_code": str, "peer_code": str})
        for top_n in [5, 10]:
            pairs = normalize_pairs(df, source, top_n)
            # Restore snapshot year after normalizing.
            year_map = df[["focal_code", "peer_code", "snapshot_report_year"]].copy()
            year_map["focal_code"] = year_map["focal_code"].map(code6)
            year_map["peer_code"] = year_map["peer_code"].map(code6)
            year_map["snapshot_report_year"] = pd.to_numeric(
                year_map["snapshot_report_year"], errors="coerce"
            )
            pairs = pairs.merge(year_map, on=["focal_code", "peer_code"], how="left")
            pairs["fiscal_year"] = pairs["snapshot_report_year"] + 1
            systems[f"{key}_next_year_top{top_n}"] = pairs.dropna(subset=["fiscal_year"]).copy()
    return systems


def residualize_year(df: pd.DataFrame, col: str) -> pd.Series:
    return df[col] - df.groupby("fiscal_year")[col].transform("mean")


def corr_stat(x: pd.Series, y: pd.Series) -> tuple[float, float, int]:
    d = pd.concat([x, y], axis=1).dropna()
    if len(d) < 20 or d.iloc[:, 0].std() == 0 or d.iloc[:, 1].std() == 0:
        return math.nan, math.nan, int(len(d))
    r, p = stats.pearsonr(d.iloc[:, 0], d.iloc[:, 1])
    return float(r), float(p), int(len(d))


def evaluate_pairs(name: str, pairs: pd.DataFrame, financials: pd.DataFrame, annual_mode: bool) -> pd.DataFrame:
    if annual_mode:
        pair_year = pairs[["focal_code", "peer_code", "fiscal_year"]].drop_duplicates().copy()
        pair_year["fiscal_year"] = pair_year["fiscal_year"].astype(int)
    else:
        years = financials["fiscal_year"].drop_duplicates().to_frame()
        pair_year = pairs[["focal_code", "peer_code"]].drop_duplicates().merge(years, how="cross")
    peer = pair_year.merge(
        financials.rename(columns={"stock_code": "peer_code"}),
        on=["peer_code", "fiscal_year"],
        how="left",
    )
    peer_port = (
        peer.groupby(["focal_code", "fiscal_year"], as_index=False)
        .agg(
            peer_sales_growth=("sales_growth", "mean"),
            peer_gross_margin=("gross_margin", "mean"),
            peer_metric_obs=("sales_growth", "count"),
        )
    )
    focal = financials.rename(
        columns={
            "stock_code": "focal_code",
            "sales_growth": "focal_sales_growth",
            "gross_margin": "focal_gross_margin",
        }
    )[["focal_code", "fiscal_year", "focal_sales_growth", "focal_gross_margin"]]
    panel = peer_port.merge(focal, on=["focal_code", "fiscal_year"], how="inner")
    panel = panel[panel["peer_metric_obs"].ge(2)].copy()
    panel["focal_sales_growth_yresid"] = residualize_year(panel, "focal_sales_growth")
    panel["peer_sales_growth_yresid"] = residualize_year(panel, "peer_sales_growth")
    panel["focal_gross_margin_yresid"] = residualize_year(panel, "focal_gross_margin")
    panel["peer_gross_margin_yresid"] = residualize_year(panel, "peer_gross_margin")
    rows = []
    specs = [
        ("sales_growth", "focal_sales_growth", "peer_sales_growth"),
        ("gross_margin", "focal_gross_margin", "peer_gross_margin"),
        ("sales_growth_year_resid", "focal_sales_growth_yresid", "peer_sales_growth_yresid"),
        ("gross_margin_year_resid", "focal_gross_margin_yresid", "peer_gross_margin_yresid"),
    ]
    for metric, focal_col, peer_col in specs:
        r, p, n = corr_stat(panel[focal_col], panel[peer_col])
        rows.append(
            {
                "peer_system": name,
                "metric": metric,
                "corr": r,
                "p": p,
                "n_focal_year": n,
                "focal_firms": panel["focal_code"].nunique(),
                "years": ",".join(map(str, sorted(panel["fiscal_year"].dropna().astype(int).unique()))),
                "annual_mode": annual_mode,
            }
        )
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame, cols: list[str], digits: int = 4) -> str:
    out = df[cols].copy()
    for col in out.select_dtypes(include=[np.number]).columns:
        out[col] = out[col].map(lambda x: round(float(x), digits) if pd.notna(x) else x)
    return out.to_markdown(index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading income statement metrics...", flush=True)
    financials = load_financials()
    rows = []
    print("Evaluating static peer systems...", flush=True)
    for name, pairs in load_static_peer_systems().items():
        rows.append(evaluate_pairs(name, pairs, financials, annual_mode=False))
    print("Evaluating annual-report peer systems...", flush=True)
    for name, pairs in load_annual_peer_systems().items():
        rows.append(evaluate_pairs(name, pairs, financials, annual_mode=True))
    res = pd.concat(rows, ignore_index=True)
    res.to_csv(OUT_DIR / "peer_validity_fundamental_comovement_summary.csv", index=False)
    main = res[
        res["peer_system"].str.contains("top5")
        & res["metric"].isin(["sales_growth_year_resid", "gross_margin_year_resid"])
    ].copy()
    doc = f"""# v13 Peer Fundamental Validity Gate

日期：2026-05-31

## Purpose

This table adds an operating-fundamentals validation layer to the peer systems.
Following peer-identification validation logic, valid product-market peers should
share not only stock-return comovement but also sales-growth and gross-margin
comovement.

Financial data source:

```text
CSMAR FS_Comins income statement
Typrep = A consolidated statements
annual reports only: Accper = YYYY-12-31
```

Measures:

- `sales_growth = Δ log(operating revenue)`
- `gross_margin = (operating revenue - operating cost) / operating revenue`
- year-residualized versions subtract each fiscal year's cross-sectional mean.

## Main Fundamental Gate, Top5

{markdown_table(main, ['peer_system', 'metric', 'corr', 'p', 'n_focal_year', 'focal_firms', 'years'])}

## Output

```text
results/v13_peer_validity_gate_20260531/peer_validity_fundamental_comovement_summary.csv
```

## Reading

This is a first-pass gate. Revenue/gross-margin validation is noisier than daily
return comovement because annual accounting data provide only a few observations
per firm. It should be used as supportive evidence, not as the sole peer-selection
criterion.
"""
    FUND_DOC.write_text(doc, encoding="utf-8")
    print(main.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
