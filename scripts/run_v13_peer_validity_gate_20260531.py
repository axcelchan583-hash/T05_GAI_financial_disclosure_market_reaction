#!/usr/bin/env python3
"""Peer-validity gate for T05 product-market peer definitions.

The goal is not to rerun the GenAI event-study. It is to ask which peer
identification system behaves like an economically meaningful peer system before
it is used as the outcome network.

Implemented gate:
1. Return comovement between focal firm returns and equal-weighted peer
   portfolio returns.
2. Market-model abnormal-return comovement as a market-adjusted robustness.
3. Pair-overlap diagnostics across peer systems.
4. A repo-relative LLM-peer request template for external coding.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "v13_peer_validity_gate_20260531"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "69_v13_peer_validity_gate_20260531.md"
LLM_DIR = ROOT / "data" / "peer_validity_llm_20260531"

STOCK_RETURNS = (
    ROOT
    / "results"
    / "v6_supplement_market_model_placebo_20260524"
    / "stock_returns_with_market_model_params.csv"
)
CSMAR_SCOPE = (
    ROOT / "results" / "csmar_v5_1_response_smoke_20260523" / "csmar_product_peer_network_top10.csv"
)
CSMAR_AI_STRIPPED = (
    ROOT / "results" / "v6_ai_stripped_similarity_checks_20260524" / "ai_stripped_product_peer_network_top10.csv"
)
INDUSTRY_PLACEBO = (
    ROOT
    / "results"
    / "v6_supplement_market_model_placebo_20260524"
    / "placebo_peer_networks_low_random.csv"
)
ANNUAL_SAME = (
    ROOT
    / "results"
    / "v12_annual_report_product_peers_20260530"
    / "annual_report_peer_network_same_industry_d_top10.csv"
)
ANNUAL_GLOBAL = (
    ROOT
    / "results"
    / "v12_annual_report_product_peers_20260530"
    / "annual_report_peer_network_global_top10.csv"
)
ANNUAL_STRIPPED = (
    ROOT
    / "results"
    / "v12_annual_report_product_peers_20260530"
    / "annual_report_peer_network_global_ai_stripped_top10.csv"
)
PRODUCT_TEXT = ROOT / "results" / "v4_peer_spillover_x_pilot" / "v4_company_product_text_latest.csv"

WINDOWS = {
    "return_2023_2026": ("2023-01-01", "2026-05-22"),
    "return_2025_2026": ("2025-01-01", "2026-05-22"),
}


def code6(value: object) -> str:
    if pd.isna(value):
        return ""
    text = re.sub(r"\.0$", "", str(value).strip())
    digits = re.sub(r"\D", "", text)
    return digits.zfill(6) if digits else ""


def fisher_z(r: float) -> float:
    if pd.isna(r):
        return math.nan
    r = max(min(float(r), 0.999999), -0.999999)
    return math.atanh(r)


def safe_corr(x: pd.Series, y: pd.Series, min_obs: int = 60) -> float:
    d = pd.concat([x, y], axis=1).dropna()
    if len(d) < min_obs:
        return math.nan
    if d.iloc[:, 0].std() == 0 or d.iloc[:, 1].std() == 0:
        return math.nan
    return float(d.iloc[:, 0].corr(d.iloc[:, 1]))


def safe_beta(x: pd.Series, y: pd.Series, min_obs: int = 60) -> float:
    """Return beta from focal return y on peer portfolio return x."""
    d = pd.concat([x, y], axis=1).dropna()
    if len(d) < min_obs:
        return math.nan
    var = float(d.iloc[:, 0].var())
    if var <= 0:
        return math.nan
    return float(d.iloc[:, 0].cov(d.iloc[:, 1]) / var)


def load_returns() -> pd.DataFrame:
    cols = ["peer_code", "date", "ret", "mkt_ret", "trdsta", "limit_status", "alpha_mm", "beta_mm"]
    ret = pd.read_csv(STOCK_RETURNS, usecols=cols, dtype={"peer_code": str})
    ret["stock_code"] = ret["peer_code"].map(code6)
    ret["date"] = pd.to_datetime(ret["date"], errors="coerce")
    for col in ["ret", "mkt_ret", "trdsta", "limit_status", "alpha_mm", "beta_mm"]:
        ret[col] = pd.to_numeric(ret[col], errors="coerce")
    ret = ret[ret["stock_code"].ne("") & ret["date"].notna()].copy()
    ret = ret[ret["trdsta"].eq(1) & ret["limit_status"].fillna(0).eq(0)].copy()
    ret["abret_mm"] = ret["ret"] - (ret["alpha_mm"] + ret["beta_mm"] * ret["mkt_ret"])
    return ret[["stock_code", "date", "ret", "abret_mm"]]


def normalize_pairs(df: pd.DataFrame, source: str, top_n: int, snapshot_year: int | None = None) -> pd.DataFrame:
    out = df.copy()
    out["focal_code"] = out["focal_code"].map(code6)
    out["peer_code"] = out["peer_code"].map(code6)
    out["peer_rank"] = pd.to_numeric(out["peer_rank"], errors="coerce")
    if snapshot_year is not None and "snapshot_report_year" in out.columns:
        out = out[pd.to_numeric(out["snapshot_report_year"], errors="coerce").eq(snapshot_year)].copy()
    out = out[out["peer_rank"].le(top_n) & out["focal_code"].ne("") & out["peer_code"].ne("")]
    out = out[out["focal_code"].ne(out["peer_code"])].copy()
    keep = [
        "focal_code",
        "peer_code",
        "peer_rank",
        "product_similarity",
        "focal_name",
        "peer_name",
        "focal_industry_d",
        "peer_industry_d",
    ]
    for col in keep:
        if col not in out.columns:
            out[col] = np.nan
    out["peer_source"] = source
    out["top_n"] = top_n
    return out[["peer_source", "top_n", *keep]].drop_duplicates(["focal_code", "peer_code"])


def load_peer_systems() -> dict[str, pd.DataFrame]:
    systems: dict[str, pd.DataFrame] = {}
    csmar = pd.read_csv(CSMAR_SCOPE, dtype={"focal_code": str, "peer_code": str})
    systems["csmar_scope_top5"] = normalize_pairs(csmar, "csmar_scope", 5)
    systems["csmar_scope_top10"] = normalize_pairs(csmar, "csmar_scope", 10)
    if CSMAR_AI_STRIPPED.exists():
        stripped = pd.read_csv(CSMAR_AI_STRIPPED, dtype={"focal_code": str, "peer_code": str})
        systems["csmar_scope_ai_stripped_top5"] = normalize_pairs(
            stripped, "csmar_scope_ai_stripped", 5
        )
        systems["csmar_scope_ai_stripped_top10"] = normalize_pairs(
            stripped, "csmar_scope_ai_stripped", 10
        )

    placebo = pd.read_csv(INDUSTRY_PLACEBO, dtype={"focal_code": str, "peer_code": str})
    for group in ["random_same_industry", "low_similarity_same_industry"]:
        sub = placebo[placebo["peer_group"].eq(group)].copy()
        systems[f"{group}_top5"] = normalize_pairs(sub, group, 5)
        systems[f"{group}_top10"] = normalize_pairs(sub, group, 10)

    for name, path, source in [
        ("annual_same_industry", ANNUAL_SAME, "annual_same_industry"),
        ("annual_global", ANNUAL_GLOBAL, "annual_global"),
        ("annual_global_ai_stripped", ANNUAL_STRIPPED, "annual_global_ai_stripped"),
    ]:
        df = pd.read_csv(path, dtype={"focal_code": str, "peer_code": str})
        # Use 2024 snapshot for static comparability with 2025-2026 returns.
        systems[f"{name}_2024_top5"] = normalize_pairs(df, source, 5, snapshot_year=2024)
        systems[f"{name}_2024_top10"] = normalize_pairs(df, source, 10, snapshot_year=2024)
    return systems


def evaluate_system(name: str, pairs: pd.DataFrame, returns: pd.DataFrame, window: str) -> tuple[pd.DataFrame, dict[str, object]]:
    start, end = WINDOWS[window]
    ret = returns[returns["date"].between(pd.Timestamp(start), pd.Timestamp(end))].copy()
    codes = set(pairs["focal_code"]) | set(pairs["peer_code"])
    ret = ret[ret["stock_code"].isin(codes)].copy()

    peer_ret = pairs[["focal_code", "peer_code"]].merge(
        ret.rename(columns={"stock_code": "peer_code"}),
        on="peer_code",
        how="inner",
    )
    peer_port = (
        peer_ret.groupby(["focal_code", "date"], as_index=False)
        .agg(peer_port_ret=("ret", "mean"), peer_port_abret=("abret_mm", "mean"), peer_ret_obs=("ret", "size"))
    )
    focal = ret.rename(
        columns={"stock_code": "focal_code", "ret": "focal_ret", "abret_mm": "focal_abret"}
    )[["focal_code", "date", "focal_ret", "focal_abret"]]
    panel = peer_port.merge(focal, on=["focal_code", "date"], how="inner")

    rows: list[dict[str, object]] = []
    for focal_code, sub in panel.groupby("focal_code", sort=False):
        obs_raw = int(sub[["focal_ret", "peer_port_ret"]].dropna().shape[0])
        obs_ab = int(sub[["focal_abret", "peer_port_abret"]].dropna().shape[0])
        rows.append(
            {
                "peer_system": name,
                "window": window,
                "focal_code": focal_code,
                "obs_raw": obs_raw,
                "obs_abret": obs_ab,
                "raw_corr": safe_corr(sub["peer_port_ret"], sub["focal_ret"]),
                "abret_corr": safe_corr(sub["peer_port_abret"], sub["focal_abret"]),
                "raw_beta": safe_beta(sub["peer_port_ret"], sub["focal_ret"]),
                "abret_beta": safe_beta(sub["peer_port_abret"], sub["focal_abret"]),
                "mean_peer_ret_obs": float(sub["peer_ret_obs"].mean()),
            }
        )
    focal_metrics = pd.DataFrame(rows)
    summary = summarize_focal_metrics(name, pairs, focal_metrics, window)
    return focal_metrics, summary


def mean_test(values: pd.Series) -> tuple[float, float, float]:
    v = values.dropna().astype(float)
    if len(v) < 3:
        return math.nan, math.nan, math.nan
    t, p = stats.ttest_1samp(v, 0.0)
    return float(v.mean()), float(t), float(p)


def summarize_focal_metrics(name: str, pairs: pd.DataFrame, fm: pd.DataFrame, window: str) -> dict[str, object]:
    out: dict[str, object] = {
        "peer_system": name,
        "window": window,
        "pair_count": int(len(pairs)),
        "focal_firms_in_network": int(pairs["focal_code"].nunique()),
        "peer_firms_in_network": int(pairs["peer_code"].nunique()),
        "focal_firms_with_returns": int(fm["focal_code"].nunique()) if not fm.empty else 0,
        "median_peer_similarity": float(pd.to_numeric(pairs["product_similarity"], errors="coerce").median()),
        "mean_peer_similarity": float(pd.to_numeric(pairs["product_similarity"], errors="coerce").mean()),
    }
    for metric in ["raw_corr", "abret_corr", "raw_beta", "abret_beta"]:
        vals = fm[metric].dropna() if metric in fm else pd.Series(dtype=float)
        mean, t, p = mean_test(vals)
        out[f"mean_{metric}"] = mean
        out[f"median_{metric}"] = float(vals.median()) if len(vals) else math.nan
        out[f"t_{metric}"] = t
        out[f"p_{metric}"] = p
        out[f"n_{metric}"] = int(len(vals))
    if "abret_corr" in fm:
        out["mean_fisher_abret_corr"] = float(fm["abret_corr"].map(fisher_z).dropna().mean())
    return out


def build_overlap(systems: dict[str, pd.DataFrame]) -> pd.DataFrame:
    pair_sets = {
        name: set(map(tuple, df[["focal_code", "peer_code"]].drop_duplicates().to_numpy()))
        for name, df in systems.items()
    }
    rows = []
    for a, set_a in pair_sets.items():
        for b, set_b in pair_sets.items():
            if a >= b:
                continue
            inter = len(set_a & set_b)
            union = len(set_a | set_b)
            rows.append(
                {
                    "system_a": a,
                    "system_b": b,
                    "pairs_a": len(set_a),
                    "pairs_b": len(set_b),
                    "overlap_pairs": inter,
                    "jaccard": inter / union if union else math.nan,
                    "overlap_share_a": inter / len(set_a) if set_a else math.nan,
                    "overlap_share_b": inter / len(set_b) if set_b else math.nan,
                }
            )
    return pd.DataFrame(rows)


def build_llm_template(systems: dict[str, pd.DataFrame]) -> None:
    LLM_DIR.mkdir(parents=True, exist_ok=True)
    product = pd.read_csv(PRODUCT_TEXT, dtype={"stock_code": str})
    product["stock_code"] = product["stock_code"].map(code6)
    for col in ["short_name", "industry_d", "product_text"]:
        if col not in product.columns:
            product[col] = ""
    product = product.drop_duplicates("stock_code")
    base = systems["csmar_scope_top5"][["focal_code"]].drop_duplicates().head(200)
    rows = base.merge(product, left_on="focal_code", right_on="stock_code", how="left")
    rows = rows[["focal_code", "short_name", "industry_d", "product_text"]].copy()
    rows["llm_peer_1_code"] = ""
    rows["llm_peer_1_name"] = ""
    rows["llm_peer_2_code"] = ""
    rows["llm_peer_2_name"] = ""
    rows["llm_peer_3_code"] = ""
    rows["llm_peer_3_name"] = ""
    rows["llm_peer_4_code"] = ""
    rows["llm_peer_4_name"] = ""
    rows["llm_peer_5_code"] = ""
    rows["llm_peer_5_name"] = ""
    rows["coder_notes"] = ""
    rows.to_csv(LLM_DIR / "llm_peer_request_template_200_20260531.csv", index=False)
    prompt = """# LLM Peer Coding Task

Input: `data/peer_validity_llm_20260531/llm_peer_request_template_200_20260531.csv`

For each focal Chinese A-share firm, identify up to five product-market competitors
from Chinese listed firms using only information that would be observable from
public business descriptions. Rank peers from closest to less close.

Coding rule:
- Product-market competitor means a firm selling similar products/services to similar customer groups.
- Do not choose supply-chain complements unless they directly compete in end products.
- Prefer A-share listed firms and fill stock code when known.
- If uncertain, leave the code blank but write the name and note uncertainty.

Output:
`data/peer_validity_llm_20260531/llm_peer_coded_200_YYYYMMDD.csv`
with the same columns filled.

This is for validating text-based peer systems, following the spirit of
Cao, Chen, Tucker, and Wan (2025, Review of Accounting Studies), not for
constructing the main variable by hand.
"""
    (LLM_DIR / "LLM_PEER_CODING_TASK.md").write_text(prompt, encoding="utf-8")


def markdown_table(df: pd.DataFrame, cols: list[str], digits: int = 4) -> str:
    out = df[cols].copy()
    for col in out.select_dtypes(include=[np.number]).columns:
        out[col] = out[col].map(lambda x: round(float(x), digits) if pd.notna(x) else x)
    return out.to_markdown(index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading peer systems...", flush=True)
    systems = load_peer_systems()
    print("Loading returns...", flush=True)
    returns = load_returns()
    all_focal_rows: list[pd.DataFrame] = []
    summary_rows: list[dict[str, object]] = []
    for name, pairs in systems.items():
        for window in WINDOWS:
            print(f"Evaluating {name} / {window} ({len(pairs)} pairs)", flush=True)
            fm, summary = evaluate_system(name, pairs, returns, window)
            all_focal_rows.append(fm)
            summary_rows.append(summary)
    focal_metrics = pd.concat(all_focal_rows, ignore_index=True)
    summary = pd.DataFrame(summary_rows)
    overlap = build_overlap(systems)
    build_llm_template(systems)

    focal_metrics.to_csv(OUT_DIR / "peer_validity_focal_return_comovement.csv", index=False)
    summary.to_csv(OUT_DIR / "peer_validity_return_comovement_summary.csv", index=False)
    overlap.to_csv(OUT_DIR / "peer_system_pair_overlap.csv", index=False)

    # Keep the main table compact: top5 systems and market-model adjusted comovement.
    main = summary[
        summary["peer_system"].str.contains("top5")
        & summary["window"].eq("return_2025_2026")
    ].copy()
    main = main.sort_values("mean_abret_corr", ascending=False)

    doc = f"""# v13 Peer-Validity Gate

日期：2026-05-31

## Purpose

This gate evaluates whether candidate peer systems behave like economically
meaningful peer systems before they are used in the GenAI event-study.

Primary validation follows the logic used in peer-identification papers:

```text
If j is a valid peer of i, returns of i and the equal-weighted peer portfolio of j
should comove more strongly than weak/random peers.
```

We report both raw-return comovement and market-model abnormal-return comovement.

## Literature-backed Peer Systems

- Industry peers: SIC/CSRC same-industry baseline.
- Text-based product-market peers: Hoberg and Phillips (2016, JPE) / TNIC-style.
- Search-based peers: Lee, Ma, and Wang (2015, JFE), not locally observable here.
- Common analyst peers: Kaustia and Rantala (2021, JFQA), requires analyst coverage data.
- Technological peers: Cao, Ma, Tucker, and Wan (2018, TAR), separate technology-space construct.
- LLM-generated peers: Cao, Chen, Tucker, and Wan (2025, RAST), prepared here as a validation template.

## Main Return-Comovement Gate, 2025-2026, Top5

Sorted by mean market-model abnormal-return correlation:

{markdown_table(main, ['peer_system', 'pair_count', 'focal_firms_with_returns', 'mean_abret_corr', 'median_abret_corr', 'p_abret_corr', 'mean_raw_corr', 'median_raw_corr', 'p_raw_corr', 'mean_peer_similarity'])}

## Outputs

```text
results/v13_peer_validity_gate_20260531/peer_validity_return_comovement_summary.csv
results/v13_peer_validity_gate_20260531/peer_validity_focal_return_comovement.csv
results/v13_peer_validity_gate_20260531/peer_system_pair_overlap.csv
data/peer_validity_llm_20260531/llm_peer_request_template_200_20260531.csv
data/peer_validity_llm_20260531/LLM_PEER_CODING_TASK.md
```

## Current Reading

This is a measurement gate, not the final paper table. A peer system should be
preferred only if it has both:

1. a published peer-identification literature anchor; and
2. stronger return comovement than random/low-similarity same-industry peers.

Revenue and gross-margin comovement will be added after confirming the local
financial-statement fields.
"""
    DOC_PATH.write_text(doc, encoding="utf-8")
    print(main.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
