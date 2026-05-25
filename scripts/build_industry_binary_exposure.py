from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


T05 = Path("/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction")
DATA22 = Path("/Users/mac/computerscience/0暂时不做了/22数据要素与AI溢出/data/interim")
RISK_FEATURES = Path(
    "/Users/mac/computerscience/0做完了/15会计研究/v4/risk_disclosure_trial/data/risk_features/"
    "existing_literature_y_specificity_similarity_2015_2025.parquet"
)

OUT_PARQUET = T05 / "data/interim/industry_binary_exposure_v0.parquet"
OUT_MEMO = T05 / "docs/archive/design_history/industry_binary_exposure_v0_20260510.md"


CSRC_L1_NAMES = {
    "A": "农、林、牧、渔业",
    "B": "采矿业",
    "C": "制造业",
    "D": "电力、热力、燃气及水生产和供应业",
    "E": "建筑业",
    "F": "批发和零售业",
    "G": "交通运输、仓储和邮政业",
    "H": "住宿和餐饮业",
    "I": "信息传输、软件和信息技术服务业",
    "J": "金融业",
    "K": "房地产业",
    "L": "租赁和商务服务业",
    "M": "科学研究和技术服务业",
    "N": "水利、环境和公共设施管理业",
    "O": "居民服务、修理和其他服务业",
    "P": "教育",
    "Q": "卫生和社会工作",
    "R": "文化、体育和娱乐业",
    "S": "综合",
}

HIGH_L1 = {"B", "D", "I", "J", "K"}
LOW_L1 = {"A", "F", "H", "O", "R"}
HIGH_MANUFACTURING_CODES = {"C25", "C26", "C27"}
HIGH_TRANSPORT_CODES = {"G55", "G56"}


def clean_stkcd(value: object) -> str | None:
    s = str(value).strip()
    if not s.isdigit():
        return None
    return s.zfill(6)


def clean_text(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    s = str(value).strip()
    if not s or s in {"None", "nan", "没有单位"}:
        return None
    return s


def choose_industry(row: pd.Series) -> tuple[str | None, str | None]:
    for code_col, name_col in [
        ("IndustryCodeD", "IndustryNameD"),
        ("IndustryCodeC", "IndustryNameC"),
        ("IndustryCode", "IndustryName"),
    ]:
        code = clean_text(row.get(code_col))
        name = clean_text(row.get(name_col))
        if code:
            return code, name
    return None, None


def classify_industry(code: str | None, name: str | None) -> tuple[float, str]:
    if not code:
        return np.nan, "missing_industry"
    code = str(code).strip().upper()
    name = name or ""
    l1 = code[0]
    sub3 = code[:3]

    if l1 in HIGH_L1:
        return 1.0, "high_l1"
    if sub3 in HIGH_MANUFACTURING_CODES:
        return 1.0, "high_manufacturing_subclass"
    if sub3 in HIGH_TRANSPORT_CODES or "航空运输" in name or "水上运输" in name:
        return 1.0, "high_transport_subclass"
    if l1 in LOW_L1:
        return 0.0, "low_l1"
    return np.nan, "excluded_middle"


def load_industry_anchor() -> pd.DataFrame:
    stk = pd.read_parquet(DATA22 / "stk_listcoinfo.parquet")
    stk["stkcd"] = stk["Symbol"].map(clean_stkcd)
    stk = stk[stk["stkcd"].notna()].copy()
    stk["enddate_dt"] = pd.to_datetime(stk["EndDate"], errors="coerce")
    stk["info_year"] = stk["enddate_dt"].dt.year

    chosen = stk.apply(choose_industry, axis=1, result_type="expand")
    stk["csrc_code"] = chosen[0]
    stk["csrc_name"] = chosen[1]
    stk["csrc_l1_code"] = stk["csrc_code"].str[0]
    stk["csrc_l1_name"] = stk["csrc_l1_code"].map(CSRC_L1_NAMES)
    classified = stk.apply(lambda r: classify_industry(r["csrc_code"], r["csrc_name"]), axis=1, result_type="expand")
    stk["HighRiskDiscIndustry"] = classified[0]
    stk["industry_binary_rule"] = classified[1]

    # Anchor exposure in pre-GenAI industry information whenever available.
    pre = stk[stk["enddate_dt"] <= pd.Timestamp("2021-12-31")].copy()
    pre_anchor = pre.sort_values(["stkcd", "enddate_dt"]).groupby("stkcd").tail(1)
    all_anchor = stk.sort_values(["stkcd", "enddate_dt"]).groupby("stkcd").tail(1)
    missing = all_anchor[~all_anchor["stkcd"].isin(pre_anchor["stkcd"])].copy()
    anchor = pd.concat([pre_anchor, missing], ignore_index=True)
    anchor["industry_anchor_source"] = np.where(anchor["enddate_dt"] <= pd.Timestamp("2021-12-31"), "latest_pre2022", "fallback_post2021")

    keep = [
        "stkcd",
        "ShortName",
        "EndDate",
        "LISTINGSTATE",
        "csrc_code",
        "csrc_name",
        "csrc_l1_code",
        "csrc_l1_name",
        "HighRiskDiscIndustry",
        "industry_binary_rule",
        "industry_anchor_source",
    ]
    return anchor[keep].copy()


def load_st_year_status() -> pd.DataFrame:
    stk = pd.read_parquet(DATA22 / "stk_listcoinfo.parquet")
    stk["stkcd"] = stk["Symbol"].map(clean_stkcd)
    stk = stk[stk["stkcd"].notna()].copy()
    stk["year"] = pd.to_datetime(stk["EndDate"], errors="coerce").dt.year
    out = stk[["stkcd", "year", "ShortName", "LISTINGSTATE"]].dropna(subset=["year"]).copy()
    out["year"] = out["year"].astype(int)
    return out.rename(columns={"ShortName": "short_name_year", "LISTINGSTATE": "listing_state_year"})


def load_annual_report_panel() -> pd.DataFrame:
    iar = pd.read_parquet(DATA22 / "iar_rept.parquet")
    iar["stkcd"] = iar["Stkcd"].map(clean_stkcd)
    iar = iar[iar["stkcd"].notna()].copy()
    iar["year"] = pd.to_datetime(iar["Accper"], errors="coerce").dt.year
    rpt = iar["Reptyp"].astype(str).str.strip()
    annual = iar[(rpt == "4") & iar["year"].between(2018, 2025)].copy()
    return annual[["stkcd", "year"]].drop_duplicates().sort_values(["stkcd", "year"])


def load_pre_risk_burden() -> pd.DataFrame:
    risk = pd.read_parquet(RISK_FEATURES)
    risk["stkcd"] = risk["Stkcd"].map(clean_stkcd)
    risk = risk[risk["year"].between(2018, 2021)].copy()
    cols = ["risk_chars", "risk_chars_ln", "risk_category_count", "risk_modification_index"]
    for col in cols:
        risk[col] = pd.to_numeric(risk[col], errors="coerce")
    agg = (
        risk.groupby("stkcd")
        .agg(
            pre_risk_years=("year", "nunique"),
            mean_risk_length_pre=("risk_chars", "mean"),
            median_risk_length_pre=("risk_chars", "median"),
            mean_risk_chars_ln_pre=("risk_chars_ln", "mean"),
            mean_risk_category_count_pre=("risk_category_count", "mean"),
            mean_risk_modification_pre=("risk_modification_index", "mean"),
        )
        .reset_index()
    )
    return agg


def st_pt_flag(name: object, state: object) -> bool:
    text = f"{name or ''} {state or ''}"
    return any(token in text.upper() for token in ["*ST", " ST", "ST ", "PT", "暂停上市", "退市"])


def welch_test(x: pd.Series, y: pd.Series) -> tuple[float, float]:
    x = pd.to_numeric(x, errors="coerce").dropna()
    y = pd.to_numeric(y, errors="coerce").dropna()
    if len(x) < 2 or len(y) < 2:
        return np.nan, np.nan
    try:
        from scipy import stats

        res = stats.ttest_ind(x, y, equal_var=False, nan_policy="omit")
        return float(res.statistic), float(res.pvalue)
    except Exception:
        diff = x.mean() - y.mean()
        se = np.sqrt(x.var(ddof=1) / len(x) + y.var(ddof=1) / len(y))
        return float(diff / se), np.nan


def fmt_num(value: object, digits: int = 3) -> str:
    if value is None or pd.isna(value):
        return "NA"
    return f"{float(value):,.{digits}f}"


def make_markdown_table(df: pd.DataFrame, cols: list[str], max_rows: int | None = None) -> str:
    view = df[cols].copy()
    if max_rows is not None:
        view = view.head(max_rows)
    return view.to_markdown(index=False)


def build_outputs() -> None:
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    anchor = load_industry_anchor()
    status = load_st_year_status()
    panel = load_annual_report_panel()
    pre = load_pre_risk_burden()

    out = panel.merge(anchor, on="stkcd", how="left")
    out = out.merge(status, on=["stkcd", "year"], how="left")
    out = out.merge(pre, on="stkcd", how="left")
    out["is_st_pt"] = out.apply(
        lambda r: st_pt_flag(r.get("short_name_year") or r.get("ShortName"), r.get("listing_state_year") or r.get("LISTINGSTATE")),
        axis=1,
    )
    out["LowRiskDiscIndustry"] = np.where(out["HighRiskDiscIndustry"].isin([0.0, 1.0]), 1 - out["HighRiskDiscIndustry"], np.nan)
    out["has_pre_risk_burden"] = out["mean_risk_length_pre"].notna()
    out["in_sample"] = (
        out["HighRiskDiscIndustry"].isin([0.0, 1.0]) & (~out["is_st_pt"]) & out["has_pre_risk_burden"]
    ).astype(int)

    out = out[
        [
            "stkcd",
            "year",
            "csrc_l1_code",
            "csrc_l1_name",
            "csrc_code",
            "csrc_name",
            "HighRiskDiscIndustry",
            "LowRiskDiscIndustry",
            "industry_binary_rule",
            "industry_anchor_source",
            "in_sample",
            "is_st_pt",
            "has_pre_risk_burden",
            "pre_risk_years",
            "mean_risk_length_pre",
            "median_risk_length_pre",
            "mean_risk_chars_ln_pre",
            "mean_risk_category_count_pre",
            "mean_risk_modification_pre",
        ]
    ].sort_values(["stkcd", "year"])
    out.to_parquet(OUT_PARQUET, index=False)

    firm = (
        out.sort_values(["stkcd", "year"])
        .drop_duplicates("stkcd")
        .copy()
    )
    firm_valid = firm[firm["has_pre_risk_burden"] & (~firm["is_st_pt"])].copy()
    firm_hilo = firm_valid[firm_valid["HighRiskDiscIndustry"].isin([0.0, 1.0])].copy()
    high = firm_hilo[firm_hilo["HighRiskDiscIndustry"] == 1.0]["mean_risk_length_pre"]
    low = firm_hilo[firm_hilo["HighRiskDiscIndustry"] == 0.0]["mean_risk_length_pre"]
    t_stat, p_value = welch_test(high, low)
    corr = firm_hilo[["HighRiskDiscIndustry", "mean_risk_length_pre"]].corr().iloc[0, 1]

    detailed_summary = (
        firm_valid.groupby(["csrc_l1_code", "csrc_l1_name", "csrc_code", "csrc_name", "industry_binary_rule", "HighRiskDiscIndustry"], dropna=False)
        .agg(
            n_firms=("stkcd", "nunique"),
            mean_risk_length_pre=("mean_risk_length_pre", "mean"),
            median_risk_length_pre=("mean_risk_length_pre", "median"),
        )
        .reset_index()
        .sort_values(["HighRiskDiscIndustry", "csrc_l1_code", "csrc_code"], na_position="last")
    )

    l1_summary = (
        firm_valid.groupby(["csrc_l1_code", "csrc_l1_name", "industry_binary_rule", "HighRiskDiscIndustry"], dropna=False)
        .agg(
            n_firms=("stkcd", "nunique"),
            mean_risk_length_pre=("mean_risk_length_pre", "mean"),
            median_risk_length_pre=("mean_risk_length_pre", "median"),
        )
        .reset_index()
        .sort_values(["HighRiskDiscIndustry", "csrc_l1_code"], na_position="last")
    )

    year_counts_source = out.copy()
    year_counts_source["binary_group"] = np.select(
        [
            year_counts_source["HighRiskDiscIndustry"] == 1.0,
            year_counts_source["HighRiskDiscIndustry"] == 0.0,
        ],
        ["high_1", "low_0"],
        default="excluded_nan",
    )
    year_counts = (
        year_counts_source.groupby(["year", "binary_group"], dropna=False)["stkcd"]
        .nunique()
        .reset_index(name="n_firm_year_firms")
        .pivot(index="year", columns="binary_group", values="n_firm_year_firms")
        .fillna(0)
        .astype(int)
        .reset_index()
    )
    for col in ["low_0", "high_1", "excluded_nan"]:
        if col not in year_counts.columns:
            year_counts[col] = 0

    distribution = (
        firm_hilo.groupby("HighRiskDiscIndustry")["mean_risk_length_pre"]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .reset_index()
    )

    pass_count = len(high) >= 300 and len(low) >= 100
    pass_mean = (high.mean() > low.mean()) if len(high) and len(low) else False
    pass_sig = bool(pd.notna(p_value) and p_value < 0.05 and pass_mean)
    corr_flag = "pass" if pd.notna(corr) and 0.3 <= abs(corr) <= 0.6 else "flag"

    validation_pass = pass_count and pass_sig and (corr_flag == "pass")
    memo = f"""# Industry Binary Exposure v0

Date: 2026-05-10 handoff; generated 2026-05-11

## Bottom Line

This script constructed `HighRiskDiscIndustry_i` as an industry-level 0/1 exposure for T05 and wrote the firm-year panel to:

```text
{OUT_PARQUET}
```

Validation status: {"PASS" if validation_pass else "FAIL"}.

This variable should not replace the continuous `PreRiskWritingBurden_i` main design. In this v0 validation, the high-risk industry group is only slightly longer than the low-risk group in pre-period risk disclosure, the difference is not statistically significant, and the correlation with continuous pre-period risk length is near zero. If used at all, treat it as an exploratory contrast and not as evidence that the industry binary captures risk-disclosure writing burden.

## Classification Rule

`HighRiskDiscIndustry = 1`:

- CSRC level-1 `J` finance, `K` real estate, `B` mining, `D` utilities, and `I` information transmission/software/IT services;
- CSRC manufacturing subclasses `C25`, `C26`, and `C27`;
- CSRC transportation subclasses `G55` water transport and `G56` air transport, also captured by names containing water or air transport.

`HighRiskDiscIndustry = 0`:

- CSRC level-1 `A`, `F`, `H`, `O`, and `R`.

Excluded:

- remaining manufacturing, construction, business services, scientific services, environmental/public facilities, education, health/social work, comprehensive, and missing-industry firms.

Industry exposure is anchored on the latest available pre-2022 listing-company industry record. Firms without a pre-2022 record use their earliest post-2021 fallback industry and are flagged in `industry_anchor_source`.

## Data Sources

- Firm-year sample frame: annual reports in `iar_rept.parquet`, `Reptyp == 4`, years 2018-2025.
- Industry classification: `stk_listcoinfo.parquet`, using `IndustryCodeD` first, then `IndustryCodeC`, then `IndustryCode`.
- Pre-period risk burden validation: `existing_literature_y_specificity_similarity_2015_2025.parquet`, using firm-level 2018-2021 mean `risk_chars`.

## Validation: High vs Low Risk-disclosure Industries

Firm-level pre-period risk length, non-ST/PT firms with available 2018-2021 risk text:

| Metric | Value |
|---|---:|
| High group firms | {len(high):,} |
| Low group firms | {len(low):,} |
| High mean pre risk length | {fmt_num(high.mean(), 1)} |
| Low mean pre risk length | {fmt_num(low.mean(), 1)} |
| High median pre risk length | {fmt_num(high.median(), 1)} |
| Low median pre risk length | {fmt_num(low.median(), 1)} |
| Welch t-stat | {fmt_num(t_stat, 3)} |
| Welch p-value | {fmt_num(p_value, 4)} |
| Correlation: industry 0/1 vs mean risk length | {fmt_num(corr, 3)} |

Completion checks:

- Sample-size check: {"PASS" if pass_count else "FAIL"}.
- High-group mean greater than low-group mean: {"PASS" if pass_mean else "FAIL"}.
- Difference statistically significant at 5%: {"PASS" if pass_sig else "FAIL"}.
- Correlation in target 0.3-0.6 range: {corr_flag.upper()}.

Interpretation: the high-risk industry binary has usable treatment/control sample sizes, but it does not pass the core data-driven validation. It is too weakly related to continuous pre-period risk-disclosure length to be sold as a persuasive 0/1 version of `PreRiskWritingBurden_i`.

## Risk-length Distribution by Binary Group

{make_markdown_table(distribution, ["HighRiskDiscIndustry", "count", "mean", "median", "std", "min", "max"])}

## Industry-level Summary

Detailed rows are grouped by CSRC detailed code because manufacturing and transportation have subclass exceptions.

{make_markdown_table(detailed_summary, ["csrc_l1_code", "csrc_l1_name", "csrc_code", "csrc_name", "n_firms", "mean_risk_length_pre", "HighRiskDiscIndustry"], max_rows=80)}

## Firm-year Sample Counts

{make_markdown_table(year_counts, ["year", "high_1", "low_0", "excluded_nan"])}

## Main Continuous vs Binary Exposure Compatibility

The current binary exposure is compared against firm-level mean pre-period risk-disclosure length, a direct continuous proxy for `PreRiskWritingBurden_i`.

- Correlation with continuous pre-period risk length: `{fmt_num(corr, 3)}`.
- High group internal mean: `{fmt_num(high.mean(), 1)}`.
- Low group internal mean: `{fmt_num(low.mean(), 1)}`.

This is not a DID result. It only checks whether the industry binary carries a plausible pre-period risk-writing-burden signal.

## Caveats

1. Manufacturing exclusions are substantial by design. The rule keeps only `C25`, `C26`, and `C27` as high-risk manufacturing and leaves the rest as middle/excluded.
2. Finance is included in the high-risk group because it is naturally risk-disclosure intensive, but journal reviewers may object that finance follows sector-specific accounting and regulatory regimes. A non-financial-only robustness version may be needed.
3. 2022 reports should remain transition-period sensitive, consistent with the main T05 design. This file only constructs exposure and does not decide the regression window.
4. Firms without a pre-period risk-text record are kept in the panel but `in_sample = 0`.
5. The variable is intended as a robustness contrast for continuous exposure DID, not as proof that identification is valid.

## Open Questions

1. Should the final robustness table exclude finance entirely after using finance in the validation step?
2. Should the industry binary be crossed with `PostGenAI` directly, or used only as a split-sample check around the continuous `PreRiskWritingBurden_i`?
3. Should the post-2021 fallback industry firms be excluded from the regression sample to keep exposure strictly pre-determined?
"""
    OUT_MEMO.write_text(memo, encoding="utf-8")

    print(f"wrote {OUT_PARQUET}")
    print(f"wrote {OUT_MEMO}")
    print(f"firm-year rows={len(out):,}, firms={out['stkcd'].nunique():,}")
    print(f"high firms={len(high):,}, low firms={len(low):,}, corr={corr:.3f}, p={p_value:.4g}")


if __name__ == "__main__":
    build_outputs()
