#!/usr/bin/env python3
"""Validation battery for DeepSeek product-market peer definitions.

This script implements the fast, non-human parts of the Cao et al.-style peer
validity package:

1. overlap with alternative peer systems;
2. stock-return comovement;
3. accounting-fundamental comovement;
4. absolute-deviation homogeneity tests.

It deliberately excludes manual blind review.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_v13_peer_fundamental_validity_20260531 import load_financials  # noqa: E402
from run_v13_peer_validity_gate_20260531 import (  # noqa: E402
    evaluate_system,
    load_peer_systems,
    load_returns,
)


OUT_DIR = ROOT / "results" / "v19_deepseek_peer_validity_checks_20260531"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "83_v19_deepseek_peer_validity_checks_20260531.md"

V17 = ROOT / "results" / "v17_deepseek_flash_peer_coding_20260531" / "deepseek_flash_peer_network_top5_full_compact15.csv"
V18 = ROOT / "results" / "v18_cao_style_open_ended_deepseek_peers_20260531" / "deepseek_open_ended_peer_network_top5_full_asof2025.csv"
V18_SAME = (
    ROOT
    / "results"
    / "v18_cao_style_open_ended_deepseek_peers_20260531"
    / "deepseek_open_ended_peer_network_top5_same_industry_full_asof2025.csv"
)


def normalize_deepseek(path: Path, source: str) -> pd.DataFrame:
    d = pd.read_csv(path, dtype={"focal_code": str, "peer_code": str})
    d = d.copy()
    d["peer_source"] = source
    d["top_n"] = 5
    if "product_similarity" not in d.columns:
        d["product_similarity"] = pd.to_numeric(d.get("peer_similarity"), errors="coerce")
    for col in ["focal_name", "peer_name", "focal_industry_d", "peer_industry_d"]:
        if col not in d.columns:
            d[col] = np.nan
    keep = [
        "peer_source",
        "top_n",
        "focal_code",
        "peer_code",
        "peer_rank",
        "product_similarity",
        "focal_name",
        "peer_name",
        "focal_industry_d",
        "peer_industry_d",
    ]
    return d[keep].drop_duplicates(["focal_code", "peer_code"])


def selected_peer_systems() -> dict[str, pd.DataFrame]:
    systems = load_peer_systems()
    out = {
        "deepseek_candidate_menu_top5": normalize_deepseek(V17, "deepseek_candidate_menu"),
        "deepseek_open_ended_top5": normalize_deepseek(V18, "deepseek_open_ended"),
        "deepseek_open_ended_same_industry_top5": normalize_deepseek(
            V18_SAME, "deepseek_open_ended_same_industry"
        ),
        "csmar_scope_top5": systems["csmar_scope_top5"],
        "annual_same_industry_2024_top5": systems["annual_same_industry_2024_top5"],
        "annual_global_ai_stripped_2024_top5": systems[
            "annual_global_ai_stripped_2024_top5"
        ],
        "random_same_industry_top5": systems["random_same_industry_top5"],
        "low_similarity_same_industry_top5": systems["low_similarity_same_industry_top5"],
    }
    return out


def pair_set(df: pd.DataFrame) -> set[tuple[str, str]]:
    return set(map(tuple, df[["focal_code", "peer_code"]].drop_duplicates().to_numpy()))


def overlap_table(systems: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    pair_sets = {k: pair_set(v) for k, v in systems.items()}
    for a, set_a in pair_sets.items():
        for b, set_b in pair_sets.items():
            inter = len(set_a & set_b)
            union = len(set_a | set_b)
            rows.append(
                {
                    "system_a": a,
                    "system_b": b,
                    "pairs_a": len(set_a),
                    "pairs_b": len(set_b),
                    "overlap_pairs": inter,
                    "share_of_a": inter / len(set_a) if set_a else math.nan,
                    "share_of_b": inter / len(set_b) if set_b else math.nan,
                    "jaccard": inter / union if union else math.nan,
                }
            )
    return pd.DataFrame(rows)


def return_comovement(systems: dict[str, pd.DataFrame]) -> pd.DataFrame:
    returns = load_returns()
    rows = []
    focal_rows = []
    for name, pairs in systems.items():
        for window in ["return_2025_2026", "return_2023_2026"]:
            fm, summary = evaluate_system(name, pairs, returns, window)
            rows.append(summary)
            fm.to_csv(OUT_DIR / f"focal_return_comovement_{name}_{window}.csv", index=False)
            focal_rows.append(fm)
    pd.concat(focal_rows, ignore_index=True).to_csv(
        OUT_DIR / "deepseek_peer_validity_focal_return_comovement.csv", index=False
    )
    return pd.DataFrame(rows)


def corr_p(x: pd.Series, y: pd.Series) -> tuple[float, float, int]:
    d = pd.concat([x, y], axis=1).dropna()
    if len(d) < 30 or d.iloc[:, 0].std() == 0 or d.iloc[:, 1].std() == 0:
        return math.nan, math.nan, int(len(d))
    r, p = stats.pearsonr(d.iloc[:, 0], d.iloc[:, 1])
    return float(r), float(p), int(len(d))


def metric_panel(pairs: pd.DataFrame, financials: pd.DataFrame) -> pd.DataFrame:
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
    for col in ["focal_sales_growth", "peer_sales_growth", "focal_gross_margin", "peer_gross_margin"]:
        panel[col + "_yresid"] = panel[col] - panel.groupby("fiscal_year")[col].transform("mean")
    return panel


def fundamental_comovement_and_deviation(systems: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    financials = load_financials()
    corr_rows = []
    dev_rows = []
    for name, pairs in systems.items():
        panel = metric_panel(pairs, financials)
        panel.to_csv(OUT_DIR / f"fundamental_panel_{name}.csv", index=False)
        specs = [
            ("sales_growth_year_resid", "focal_sales_growth_yresid", "peer_sales_growth_yresid"),
            ("gross_margin_year_resid", "focal_gross_margin_yresid", "peer_gross_margin_yresid"),
            ("sales_growth_raw", "focal_sales_growth", "peer_sales_growth"),
            ("gross_margin_raw", "focal_gross_margin", "peer_gross_margin"),
        ]
        for metric, focal_col, peer_col in specs:
            r, p, n = corr_p(panel[focal_col], panel[peer_col])
            corr_rows.append(
                {
                    "peer_system": name,
                    "metric": metric,
                    "corr": r,
                    "p": p,
                    "n_focal_year": n,
                    "focal_firms": panel["focal_code"].nunique(),
                    "years": ",".join(map(str, sorted(panel["fiscal_year"].dropna().astype(int).unique()))),
                }
            )
            diff = (panel[focal_col] - panel[peer_col]).abs().replace([np.inf, -np.inf], np.nan)
            dev_rows.append(
                {
                    "peer_system": name,
                    "metric": metric,
                    "mean_abs_deviation": float(diff.mean()),
                    "median_abs_deviation": float(diff.median()),
                    "n_focal_year": int(diff.notna().sum()),
                    "focal_firms": panel["focal_code"].nunique(),
                }
            )
    return pd.DataFrame(corr_rows), pd.DataFrame(dev_rows)


def return_deviation(systems: dict[str, pd.DataFrame]) -> pd.DataFrame:
    returns = load_returns()
    rows = []
    for name, pairs in systems.items():
        start, end = pd.Timestamp("2025-01-01"), pd.Timestamp("2026-05-22")
        ret = returns[returns["date"].between(start, end)].copy()
        peer = pairs[["focal_code", "peer_code"]].merge(
            ret.rename(columns={"stock_code": "peer_code"}),
            on="peer_code",
            how="inner",
        )
        focal = ret.rename(columns={"stock_code": "focal_code", "ret": "focal_ret", "abret_mm": "focal_abret"})[
            ["focal_code", "date", "focal_ret", "focal_abret"]
        ]
        d = peer.merge(focal, on=["focal_code", "date"], how="inner")
        d["abs_ret_dev"] = (d["ret"] - d["focal_ret"]).abs()
        d["abs_abret_dev"] = (d["abret_mm"] - d["focal_abret"]).abs()
        rows.append(
            {
                "peer_system": name,
                "mean_abs_ret_dev": float(d["abs_ret_dev"].mean()),
                "median_abs_ret_dev": float(d["abs_ret_dev"].median()),
                "mean_abs_abret_dev": float(d["abs_abret_dev"].mean()),
                "median_abs_abret_dev": float(d["abs_abret_dev"].median()),
                "pair_day_obs": int(len(d)),
                "focal_firms": d["focal_code"].nunique(),
                "peer_firms": d["peer_code"].nunique(),
            }
        )
    return pd.DataFrame(rows)


def md_table(df: pd.DataFrame, cols: list[str], n: int | None = None) -> str:
    out = df[cols].copy()
    if n is not None:
        out = out.head(n)
    for col in out.select_dtypes(include=[np.number]).columns:
        out[col] = out[col].map(lambda x: round(float(x), 4) if pd.notna(x) else x)
    return out.to_markdown(index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    systems = selected_peer_systems()

    network_summary = []
    for name, pairs in systems.items():
        network_summary.append(
            {
                "peer_system": name,
                "pair_count": len(pairs),
                "focal_firms": pairs["focal_code"].nunique(),
                "peer_firms": pairs["peer_code"].nunique(),
                "same_industry_share": float(
                    pairs["focal_industry_d"].fillna("").eq(pairs["peer_industry_d"].fillna("")).mean()
                ),
                "mean_similarity": float(pd.to_numeric(pairs["product_similarity"], errors="coerce").mean()),
                "median_similarity": float(pd.to_numeric(pairs["product_similarity"], errors="coerce").median()),
            }
        )
    network_summary = pd.DataFrame(network_summary)
    network_summary.to_csv(OUT_DIR / "network_summary.csv", index=False)

    overlaps = overlap_table(systems)
    overlaps.to_csv(OUT_DIR / "overlap_matrix.csv", index=False)

    ret = return_comovement(systems)
    ret.to_csv(OUT_DIR / "return_comovement_summary.csv", index=False)

    fund_corr, fund_dev = fundamental_comovement_and_deviation(systems)
    fund_corr.to_csv(OUT_DIR / "fundamental_comovement_summary.csv", index=False)
    fund_dev.to_csv(OUT_DIR / "fundamental_abs_deviation_summary.csv", index=False)

    ret_dev = return_deviation(systems)
    ret_dev.to_csv(OUT_DIR / "return_abs_deviation_summary.csv", index=False)

    key_ret = ret[ret["window"].eq("return_2025_2026")].copy()
    key_ret = key_ret.sort_values("mean_abret_beta", ascending=False)
    key_fund = fund_corr[fund_corr["metric"].isin(["sales_growth_year_resid", "gross_margin_year_resid"])].copy()
    key_fund = key_fund.sort_values(["metric", "corr"], ascending=[True, False])
    key_ret_dev = ret_dev.sort_values("mean_abs_abret_dev")
    key_overlap = overlaps[
        overlaps["system_a"].eq("deepseek_candidate_menu_top5")
        & overlaps["system_b"].ne("deepseek_candidate_menu_top5")
    ].sort_values("share_of_a", ascending=False)

    doc = f"""# v19 DeepSeek Peer Validity Checks

Date: 2026-05-31

Purpose: fast non-human validation package for the DeepSeek product-market peer
definitions. This deliberately skips manual blind review and mirrors the other
Cao et al. validation layers: overlap with alternative systems, return
comovement, accounting-fundamental comovement, and homogeneity / deviation.

## Network Summary

{md_table(network_summary, ['peer_system','pair_count','focal_firms','peer_firms','same_industry_share','mean_similarity','median_similarity'])}

## Overlap with v17 Candidate-Menu DeepSeek Peers

{md_table(key_overlap, ['system_b','overlap_pairs','share_of_a','share_of_b','jaccard'])}

## Return Comovement, 2025-2026

Higher `mean_abret_beta` and `mean_abret_corr` indicate stronger market
comovement between focal firms and their peer portfolios.

{md_table(key_ret, ['peer_system','focal_firms_with_returns','mean_abret_beta','mean_abret_corr','mean_raw_beta','mean_raw_corr'])}

## Return Homogeneity, 2025-2026

Lower absolute deviation means peers move more similarly to focal firms.

{md_table(key_ret_dev, ['peer_system','mean_abs_abret_dev','median_abs_abret_dev','mean_abs_ret_dev','median_abs_ret_dev','pair_day_obs'])}

## Fundamental Comovement

{md_table(key_fund, ['peer_system','metric','corr','p','n_focal_year','focal_firms'])}

## Fundamental Homogeneity

{md_table(fund_dev[fund_dev['metric'].isin(['sales_growth_year_resid','gross_margin_year_resid'])].sort_values(['metric','mean_abs_deviation']), ['peer_system','metric','mean_abs_deviation','median_abs_deviation','n_focal_year','focal_firms'])}

## Reading

- The candidate-menu DeepSeek network should be judged against random and
  low-similarity placebos, not against an impossible perfect peer list.
- If candidate-menu DeepSeek peers beat random/low-similarity peers in return
  comovement and homogeneity, the peer measure has market-validity support.
- The open-ended Cao-style peer network is a useful boundary check but selects a
  substantially different and noisier set of firms in China.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")
    print(f"Wrote {DOC_PATH}")
    print(key_ret[["peer_system", "mean_abret_beta", "mean_abret_corr", "focal_firms_with_returns"]].to_string(index=False))
    print(key_fund[["peer_system", "metric", "corr", "p"]].to_string(index=False))


if __name__ == "__main__":
    main()
