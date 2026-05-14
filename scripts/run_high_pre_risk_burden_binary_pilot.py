from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
from scipy import stats

from build_industry_binary_exposure import clean_stkcd, load_industry_anchor


T05 = Path("/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction")
DATA22 = Path("/Users/mac/computerscience/0暂时不做了/22数据要素与AI溢出/data/interim")
RISK_MAIN = Path(
    "/Users/mac/computerscience/0做完了/15会计研究/v4/risk_disclosure_trial/data/risk_features/"
    "existing_literature_y_specificity_similarity_2015_2025.parquet"
)
RISK_VERIF = Path(
    "/Users/mac/computerscience/0做完了/15会计研究/v4/risk_disclosure_trial/data/risk_features/"
    "risk_disclosure_verifiable_features_2015_2025.parquet"
)

OUT_EXPOSURE = T05 / "data/interim/high_pre_risk_burden_binary_v0.parquet"
OUT_REG = T05 / "results/high_pre_risk_burden_did_pilot_v0.csv"
OUT_EVENT = T05 / "results/high_pre_risk_burden_event_pilot_v0.csv"
OUT_BALANCE = T05 / "results/high_pre_risk_burden_balance_v0.csv"
OUT_MEMO = T05 / "docs/high_pre_risk_burden_binary_pilot_20260511.md"

PRE_YEARS = list(range(2018, 2022))
REG_YEARS = [2018, 2019, 2020, 2021, 2023, 2024]
MIN_INDUSTRY_FIRMS = 20


def zscore(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    sd = x.std()
    if not np.isfinite(sd) or sd == 0:
        return x * np.nan
    return (x - x.mean()) / sd


def load_risk_main() -> pd.DataFrame:
    df = pd.read_parquet(RISK_MAIN)
    df["stkcd"] = df["Stkcd"].map(clean_stkcd)
    return df[df["stkcd"].notna()].copy()


def load_verifiable() -> pd.DataFrame:
    df = pd.read_parquet(RISK_VERIF)
    df["stkcd"] = df["Stkcd"].map(clean_stkcd)
    keep = ["stkcd", "year", "risk_verifiability_index", "np_liability_verifiability_index"]
    return df[df["stkcd"].notna()][keep].copy()


def load_controls() -> pd.DataFrame:
    df = pd.read_parquet(DATA22 / "controls_firm_year.parquet")
    df["stkcd"] = df["stkcd"].map(clean_stkcd)
    df = df[df["stkcd"].notna()].copy()
    return df.rename(columns={"report_year": "year"})


def make_exposure(risk: pd.DataFrame, anchor: pd.DataFrame) -> pd.DataFrame:
    pre = risk[risk["year"].isin(PRE_YEARS)].copy()
    agg = (
        pre.groupby("stkcd")
        .agg(
            pre_years=("year", "nunique"),
            pre_risk_chars_mean=("risk_chars", "mean"),
            pre_risk_chars_median=("risk_chars", "median"),
            pre_risk_chars_ln_mean=("risk_chars_ln", "mean"),
            pre_risk_category_count_mean=("risk_category_count", "mean"),
            pre_risk_modification_mean=("risk_modification_index", "mean"),
            pre_risk_specificity_mean=("risk_specificity_index", "mean"),
            pre_risk_boilerplate_mean=("risk_boilerplate_ratio", "mean"),
        )
        .reset_index()
    )
    out = agg.merge(
        anchor[
            [
                "stkcd",
                "ShortName",
                "csrc_code",
                "csrc_name",
                "csrc_l1_code",
                "csrc_l1_name",
                "industry_anchor_source",
            ]
        ],
        on="stkcd",
        how="left",
    )
    # The primary split uses pre-period log risk-section length. A secondary index
    # is retained for later robustness, but not used to define the v0 treatment.
    out["pre_burden_index"] = (
        zscore(out["pre_risk_chars_ln_mean"].fillna(0))
        + zscore(out["pre_risk_category_count_mean"].fillna(0))
        + zscore(out["pre_risk_modification_mean"].fillna(0))
    ) / 3.0

    out["industry_n_with_pre_burden"] = out.groupby("csrc_code")["stkcd"].transform("nunique")
    eligible = out["csrc_code"].notna() & (out["industry_n_with_pre_burden"] >= MIN_INDUSTRY_FIRMS)
    out["industry_rank_pct"] = np.nan
    out.loc[eligible, "industry_rank_pct"] = out.loc[eligible].groupby("csrc_code")[
        "pre_risk_chars_ln_mean"
    ].rank(pct=True, method="average")
    out["HighPreRiskBurden"] = np.where(out["industry_rank_pct"] >= 2 / 3, 1.0, np.nan)
    out["HighPreRiskBurden"] = np.where(out["industry_rank_pct"] <= 1 / 3, 0.0, out["HighPreRiskBurden"])
    out["burden_binary_group"] = np.select(
        [
            out["HighPreRiskBurden"] == 1.0,
            out["HighPreRiskBurden"] == 0.0,
            eligible,
        ],
        ["high_top_tercile", "low_bottom_tercile", "middle_tercile"],
        default="industry_too_small_or_missing",
    )
    out["LowPreRiskBurden"] = np.where(out["HighPreRiskBurden"].isin([0.0, 1.0]), 1 - out["HighPreRiskBurden"], np.nan)
    return out


def make_panel(risk: pd.DataFrame, verif: pd.DataFrame, controls: pd.DataFrame, exposure: pd.DataFrame) -> pd.DataFrame:
    keep_main = [
        "stkcd",
        "year",
        "risk_chars",
        "risk_chars_ln",
        "risk_boilerplate_ratio",
        "risk_specificity_index",
        "risk_quality_index_old_style",
        "risk_similarity_lag",
        "risk_modification_index",
    ]
    panel = risk[keep_main].merge(verif, on=["stkcd", "year"], how="left")
    panel = panel.merge(
        exposure[
            [
                "stkcd",
                "csrc_code",
                "csrc_name",
                "csrc_l1_code",
                "csrc_l1_name",
                "industry_anchor_source",
                "pre_years",
                "pre_risk_chars_mean",
                "pre_risk_chars_ln_mean",
                "pre_risk_category_count_mean",
                "pre_risk_modification_mean",
                "pre_burden_index",
                "industry_n_with_pre_burden",
                "industry_rank_pct",
                "HighPreRiskBurden",
                "LowPreRiskBurden",
                "burden_binary_group",
            ]
        ],
        on="stkcd",
        how="left",
    )
    panel = panel.merge(controls[["stkcd", "year", "Size", "Lev", "ROA", "BE_ratio"]], on=["stkcd", "year"], how="left")
    panel["PostChatGPT"] = (panel["year"] >= 2023).astype(int)
    panel["DID_Post_HighPreRiskBurden"] = panel["PostChatGPT"] * panel["HighPreRiskBurden"]
    panel["in_binary_sample"] = panel["HighPreRiskBurden"].isin([0.0, 1.0])
    return panel


def welch_row(df: pd.DataFrame, var: str) -> dict[str, object]:
    high = pd.to_numeric(df.loc[df["HighPreRiskBurden"] == 1.0, var], errors="coerce").dropna()
    low = pd.to_numeric(df.loc[df["HighPreRiskBurden"] == 0.0, var], errors="coerce").dropna()
    if len(high) >= 2 and len(low) >= 2:
        test = stats.ttest_ind(high, low, equal_var=False, nan_policy="omit")
        t_stat, p_val = float(test.statistic), float(test.pvalue)
    else:
        t_stat, p_val = np.nan, np.nan
    return {
        "variable": var,
        "high_n": len(high),
        "low_n": len(low),
        "high_mean": high.mean() if len(high) else np.nan,
        "low_mean": low.mean() if len(low) else np.nan,
        "diff_high_minus_low": high.mean() - low.mean() if len(high) and len(low) else np.nan,
        "welch_t": t_stat,
        "welch_p": p_val,
    }


def balance_table(exposure: pd.DataFrame, controls: pd.DataFrame) -> pd.DataFrame:
    pre_controls = controls[controls["year"].isin(PRE_YEARS)].copy()
    agg = (
        pre_controls.groupby("stkcd")
        .agg(
            pre_Size=("Size", "mean"),
            pre_Lev=("Lev", "mean"),
            pre_ROA=("ROA", "mean"),
            pre_BE_ratio=("BE_ratio", "mean"),
        )
        .reset_index()
    )
    df = exposure.merge(agg, on="stkcd", how="left")
    rows = [
        welch_row(df, "pre_risk_chars_ln_mean"),
        welch_row(df, "pre_risk_chars_mean"),
        welch_row(df, "pre_risk_category_count_mean"),
        welch_row(df, "pre_risk_modification_mean"),
        welch_row(df, "pre_Size"),
        welch_row(df, "pre_Lev"),
        welch_row(df, "pre_ROA"),
        welch_row(df, "pre_BE_ratio"),
    ]
    return pd.DataFrame(rows)


def run_panel_regression(df: pd.DataFrame, outcome: str, spec: str, controls: bool = True) -> dict[str, object]:
    data = df[df["year"].isin(REG_YEARS) & df["in_binary_sample"]].copy()
    xcols = ["DID_Post_HighPreRiskBurden"]
    if controls:
        xcols += ["Size", "Lev", "ROA"]
    cols = ["stkcd", "year", "csrc_code", outcome] + xcols
    data = data[cols].replace([np.inf, -np.inf], np.nan).dropna().copy()
    data = data.set_index(["stkcd", "year"])
    y = data[outcome].astype(float)
    x = data[xcols].astype(float)
    if spec == "firm_year":
        mod = PanelOLS(y, x, entity_effects=True, time_effects=True, drop_absorbed=True)
    elif spec == "firm_industry_year":
        tmp = data.reset_index()
        tmp["industry_year"] = pd.Categorical(tmp["csrc_code"].astype(str) + "_" + tmp["year"].astype(str)).codes
        tmp = tmp.set_index(["stkcd", "year"])
        other = tmp[["industry_year"]]
        mod = PanelOLS(y, x, entity_effects=True, other_effects=other, drop_absorbed=True)
    else:
        raise ValueError(spec)
    res = mod.fit(cov_type="clustered", cluster_entity=True)
    term = "DID_Post_HighPreRiskBurden"
    return {
        "outcome": outcome,
        "spec": spec,
        "controls": controls,
        "coef": res.params.get(term, np.nan),
        "se": res.std_errors.get(term, np.nan),
        "t": res.tstats.get(term, np.nan),
        "p": res.pvalues.get(term, np.nan),
        "nobs": int(res.nobs),
        "n_firms": int(data.index.get_level_values("stkcd").nunique()),
        "years": ",".join(map(str, sorted(data.index.get_level_values("year").unique()))),
    }


def run_event_study(df: pd.DataFrame, outcome: str = "risk_verifiability_index") -> pd.DataFrame:
    years = [2018, 2019, 2020, 2023, 2024]
    data = df[df["year"].isin(REG_YEARS) & df["in_binary_sample"]].copy()
    for yr in years:
        data[f"event_{yr}"] = ((data["year"] == yr) & (data["HighPreRiskBurden"] == 1.0)).astype(int)
    xcols = [f"event_{yr}" for yr in years] + ["Size", "Lev", "ROA"]
    cols = ["stkcd", "year", outcome] + xcols
    data = data[cols].replace([np.inf, -np.inf], np.nan).dropna().set_index(["stkcd", "year"])
    mod = PanelOLS(data[outcome].astype(float), data[xcols].astype(float), entity_effects=True, time_effects=True, drop_absorbed=True)
    res = mod.fit(cov_type="clustered", cluster_entity=True)
    rows = []
    for yr in years:
        term = f"event_{yr}"
        rows.append(
            {
                "outcome": outcome,
                "rel_year": yr - 2021,
                "year": yr,
                "coef": res.params.get(term, np.nan),
                "se": res.std_errors.get(term, np.nan),
                "t": res.tstats.get(term, np.nan),
                "p": res.pvalues.get(term, np.nan),
                "nobs": int(res.nobs),
            }
        )
    return pd.DataFrame(rows)


def md_table(df: pd.DataFrame, cols: list[str], max_rows: int | None = None, digits: int = 4) -> str:
    view = df[cols].copy()
    if max_rows:
        view = view.head(max_rows)
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.{digits}f}")
    return view.to_markdown(index=False)


def main() -> None:
    OUT_EXPOSURE.parent.mkdir(parents=True, exist_ok=True)
    OUT_REG.parent.mkdir(parents=True, exist_ok=True)
    OUT_MEMO.parent.mkdir(parents=True, exist_ok=True)

    risk = load_risk_main()
    verif = load_verifiable()
    controls = load_controls()
    anchor = load_industry_anchor()
    exposure = make_exposure(risk, anchor)
    panel = make_panel(risk, verif, controls, exposure)
    panel.to_parquet(OUT_EXPOSURE, index=False)

    balance = balance_table(exposure, controls)
    balance.to_csv(OUT_BALANCE, index=False)

    outcomes = [
        "risk_verifiability_index",
        "risk_specificity_index",
        "risk_quality_index_old_style",
        "risk_boilerplate_ratio",
        "risk_similarity_lag",
    ]
    reg_rows = []
    for outcome in outcomes:
        for spec in ["firm_year", "firm_industry_year"]:
            try:
                reg_rows.append(run_panel_regression(panel, outcome, spec, controls=True))
            except Exception as exc:
                reg_rows.append({"outcome": outcome, "spec": spec, "error": repr(exc)})
    reg = pd.DataFrame(reg_rows)
    reg.to_csv(OUT_REG, index=False)

    event = run_event_study(panel, "risk_verifiability_index")
    event.to_csv(OUT_EVENT, index=False)

    exp_counts = exposure["burden_binary_group"].value_counts(dropna=False).rename_axis("group").reset_index(name="n_firms")
    industry_count = exposure[exposure["burden_binary_group"].isin(["high_top_tercile", "low_bottom_tercile"])][
        "csrc_code"
    ].nunique()
    binary_firms = exposure[exposure["HighPreRiskBurden"].isin([0.0, 1.0])]["stkcd"].nunique()

    main_reg = reg[
        (reg["outcome"] == "risk_verifiability_index") & (reg["spec"].isin(["firm_year", "firm_industry_year"]))
    ].copy()

    memo = f"""# High Pre-risk-writing Burden Binary Pilot

Date: 2026-05-11

## Purpose

This pilot replaces the continuous second difference in the T05 DID with a data-driven binary exposure:

```text
D1 = PostChatGPT_t
D2 = HighPreRiskBurden_i
```

`HighPreRiskBurden_i` is defined using pre-period annual-report risk disclosure, not post-treatment text.

## Definition

Primary v0 definition:

```text
HighPreRiskBurden_i = 1[firm is in the top tercile of 2018-2021 mean log risk-section length within the same CSRC detailed industry]
LowPreRiskBurden_i  = 1[firm is in the bottom tercile within the same CSRC detailed industry]
```

Middle tercile firms are excluded from the binary DID sample. Industries with fewer than `{MIN_INDUSTRY_FIRMS}` firms with pre-period risk-text data are excluded from the binary split.

## Outputs

- Panel with exposure and outcomes: `{OUT_EXPOSURE}`
- DID pilot table: `{OUT_REG}`
- Event-study pilot table: `{OUT_EVENT}`
- Balance table: `{OUT_BALANCE}`

## Exposure Counts

{md_table(exp_counts, ["group", "n_firms"])}

Number of CSRC detailed industries used in the high/low split: `{industry_count}`.

Binary high/low firm count: `{binary_firms}`.

## Pre-period Balance / Split Validation

{md_table(balance, ["variable", "high_n", "low_n", "high_mean", "low_mean", "diff_high_minus_low", "welch_p"], digits=4)}

Interpretation: the split mechanically separates high and low pre-risk-writing burden by construction. The relevant concern is balance on generic firm characteristics such as Size, Lev, ROA, and BE_ratio.

## DID Pilot Results

Window: 2018-2021 and 2023-2024. The 2022 transition year is excluded. 2025 is excluded in this pilot because the reusable controls panel is incomplete for 2025.

Treatment:

```text
PostChatGPT_t * HighPreRiskBurden_i
```

Controls: Size, Lev, ROA.

{md_table(reg, ["outcome", "spec", "coef", "se", "t", "p", "nobs", "n_firms"], digits=4)}

## Event-study Pilot for Main Y

Outcome: `risk_verifiability_index`. Reference year: 2021. Fixed effects: firm FE + year FE. Controls: Size, Lev, ROA.

{md_table(event, ["year", "rel_year", "coef", "se", "t", "p", "nobs"], digits=4)}

## Current Judgment

This binary exposure is more defensible than the hand-coded industry 0/1 exposure because it is validated directly from pre-period risk-disclosure text and is defined within industry.

It is still not a complete GenAI design by itself. The decisive next gate remains:

```text
PostChatGPT_t * HighPreRiskBurden_i -> RiskSectionGAIWritingScore_it
```

Without that first stage, the current DID can only be described as a post-ChatGPT change among firms with high pre-period risk-writing burden, not as confirmed GAI-assisted writing.

## Caveats

1. The high/low split is based on text length in v0; later versions should test an index using length, risk-category breadth, and annual modification burden.
2. High/low firms are split within CSRC detailed industry, but firm size and financial characteristics may still differ.
3. This pilot does not prove parallel trends; the event-study table is only a first screen.
4. This pilot does not include `RiskSectionGAIWritingScore`, because that measure has not been built yet.
"""
    OUT_MEMO.write_text(memo, encoding="utf-8")

    print(f"wrote {OUT_EXPOSURE}")
    print(f"wrote {OUT_REG}")
    print(f"wrote {OUT_EVENT}")
    print(f"wrote {OUT_BALANCE}")
    print(f"wrote {OUT_MEMO}")
    print("exposure counts:")
    print(exp_counts.to_string(index=False))
    print("main Y pilot:")
    print(main_reg[["outcome", "spec", "coef", "se", "t", "p", "nobs", "n_firms"]].to_string(index=False))


if __name__ == "__main__":
    main()
