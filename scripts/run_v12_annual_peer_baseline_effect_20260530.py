#!/usr/bin/env python3
"""Average GenAI-announcement peer reaction under annual-report peer networks."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups


ROOT = Path(__file__).resolve().parents[1]
IN_DIR = ROOT / "results" / "v12_annual_report_peer_main_effect_20260530"
OUT_DIR = ROOT / "results" / "v12_annual_peer_baseline_effect_20260530"
DOC_PATH = ROOT / "docs" / "empirical_runs" / "68_v12_annual_peer_baseline_effect_20260530.md"

OUTCOMES = ["peer_car_0_p1_mm", "peer_car_m1_p1_mm"]
SOURCES = ["annual_same_industry_d", "annual_global", "annual_global_ai_stripped"]


def p_from_z(z: float) -> float:
    return 2 * (1 - stats.norm.cdf(abs(z))) if math.isfinite(z) else math.nan


def clustered_mean(df: pd.DataFrame, outcome: str, source: str, top_n: int) -> dict[str, object]:
    d = df.dropna(subset=[outcome, "event_id", "peer_code"]).copy()
    model = sm.OLS(d[outcome].astype(float).to_numpy(), np.ones((len(d), 1))).fit()
    cov_two, _, _ = cov_cluster_2groups(
        model, pd.Categorical(d["event_id"]).codes, pd.Categorical(d["peer_code"]).codes
    )
    var = float(np.asarray(cov_two)[0, 0])
    se = math.sqrt(var) if var >= 0 else math.nan
    z = float(model.params[0] / se) if se and se > 0 else math.nan
    return {
        "peer_source": source,
        "top_n": top_n,
        "outcome": outcome,
        "estimate": float(model.params[0]),
        "se": se,
        "z": z,
        "p": p_from_z(z),
        "nobs": int(model.nobs),
        "events": int(d["event_id"].nunique()),
        "peer_firms": int(d["peer_code"].nunique()),
        "cluster": "event_id + peer_code",
    }


def diff_top5_vs_6_10(df: pd.DataFrame, outcome: str, source: str) -> dict[str, object]:
    d = df[df["peer_rank"].le(10)].dropna(subset=[outcome, "event_id", "peer_code"]).copy()
    d["top5"] = d["peer_rank"].le(5).astype(float)
    x = sm.add_constant(d[["top5"]].astype(float), has_constant="add")
    model = sm.OLS(d[outcome].astype(float).to_numpy(), x.to_numpy()).fit()
    cov_two, _, _ = cov_cluster_2groups(
        model, pd.Categorical(d["event_id"]).codes, pd.Categorical(d["peer_code"]).codes
    )
    se = np.sqrt(np.diag(np.asarray(cov_two)))
    idx = list(x.columns).index("top5")
    z = float(model.params[idx] / se[idx]) if se[idx] > 0 else math.nan
    return {
        "peer_source": source,
        "comparison": "Top5 minus ranks 6-10",
        "outcome": outcome,
        "coef": float(model.params[idx]),
        "se": float(se[idx]),
        "z": z,
        "p": p_from_z(z),
        "nobs": int(model.nobs),
        "events": int(d["event_id"].nunique()),
        "peer_firms": int(d["peer_code"].nunique()),
        "cluster": "event_id + peer_code",
    }


def markdown_table(df: pd.DataFrame, cols: list[str]) -> str:
    out = df[cols].copy()
    for col in out.select_dtypes(include=[np.number]).columns:
        out[col] = out[col].map(lambda x: round(float(x), 6) if pd.notna(x) else x)
    return out.to_markdown(index=False)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mean_rows: list[dict[str, object]] = []
    diff_rows: list[dict[str, object]] = []
    for source in SOURCES:
        top10 = pd.read_csv(IN_DIR / f"analysis_sample_{source}_top10.csv.gz", dtype={"event_id": str, "peer_code": str})
        top10["peer_rank"] = pd.to_numeric(top10["peer_rank"], errors="coerce")
        for top_n in [5, 10]:
            sample = top10[top10["peer_rank"].le(top_n)].copy()
            for outcome in OUTCOMES:
                mean_rows.append(clustered_mean(sample, outcome, source, top_n))
        for outcome in OUTCOMES:
            diff_rows.append(diff_top5_vs_6_10(top10, outcome, source))

    means = pd.DataFrame(mean_rows)
    diffs = pd.DataFrame(diff_rows)
    means.to_csv(OUT_DIR / "annual_peer_mean_car_against_zero.csv", index=False)
    diffs.to_csv(OUT_DIR / "annual_peer_top5_minus_6_10.csv", index=False)

    doc = f"""# v12 Annual-Report Peer Baseline Announcement Effect

日期：2026-05-30

## Purpose

This table asks the simpler question before using specificity or AIActivePeer:

```text
Does a focal GenAI disclosure event have an average market reaction among annual-report product-market peers?
```

The test is an intercept-only event-study mean with two-way clustered standard errors by focal event and peer firm.

## Mean Peer CAR Against Zero

{markdown_table(means, ['peer_source', 'top_n', 'outcome', 'estimate', 'se', 'p', 'nobs', 'events', 'peer_firms'])}

## Top5 Minus Ranks 6-10

{markdown_table(diffs, ['peer_source', 'comparison', 'outcome', 'coef', 'se', 'p', 'nobs', 'events', 'peer_firms'])}

## Interpretation

年报 peer 网络下，GenAI 披露事件本身对 peer 的平均 CAR 没有稳定负向反应。
同细分行业 Top5 的 `CAR[0,+1]` 均值为正且不显著；global / AI-word-stripped global
也不显著。Top5 与 ranks 6-10 的差异同样不显著。

这与旧 CSMAR peer 口径的 v11 baseline 一致：平均公告效应不是当前论文能讲的主故事。
如果继续 peer-CAR 设计，必须依赖有文献和理论支撑的条件效应，而不是简单公告平均效应。
"""
    DOC_PATH.write_text(doc, encoding="utf-8")
    print(means.to_string(index=False), flush=True)
    print(diffs.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
