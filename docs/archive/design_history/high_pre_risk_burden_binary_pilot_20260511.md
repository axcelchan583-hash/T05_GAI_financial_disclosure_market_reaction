# High Pre-risk-writing Burden Binary Pilot

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

Middle tercile firms are excluded from the binary DID sample. Industries with fewer than `20` firms with pre-period risk-text data are excluded from the binary split.

## Outputs

- Panel with exposure and outcomes: `/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/data/interim/high_pre_risk_burden_binary_v0.parquet`
- DID pilot table: `/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/high_pre_risk_burden_did_pilot_v0.csv`
- Event-study pilot table: `/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/high_pre_risk_burden_event_pilot_v0.csv`
- Balance table: `/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/high_pre_risk_burden_balance_v0.csv`

## Exposure Counts

| group                         |   n_firms |
|:------------------------------|----------:|
| high_top_tercile              |      1291 |
| low_bottom_tercile            |      1251 |
| middle_tercile                |      1243 |
| industry_too_small_or_missing |       329 |

Number of CSRC detailed industries used in the high/low split: `41`.

Binary high/low firm count: `2542`.

## Pre-period Balance / Split Validation

| variable                     |   high_n |   low_n |   high_mean |   low_mean |   diff_high_minus_low |   welch_p |
|:-----------------------------|---------:|--------:|------------:|-----------:|----------------------:|----------:|
| pre_risk_chars_ln_mean       |     1291 |    1251 |      6.3495 |     3.5961 |                2.7535 |    0      |
| pre_risk_chars_mean          |     1291 |    1251 |    759.116  |   211.118  |              547.999  |    0      |
| pre_risk_category_count_mean |     1291 |    1251 |      3.4525 |     1.608  |                1.8445 |    0      |
| pre_risk_modification_mean   |     1100 |     765 |      0.3944 |     0.3568 |                0.0376 |    0.0037 |
| pre_Size                     |     1291 |    1251 |     22.3066 |    22.1833 |                0.1233 |    0.0177 |
| pre_Lev                      |     1291 |    1251 |      0.4074 |     0.4297 |               -0.0224 |    0.0046 |
| pre_ROA                      |     1291 |    1251 |      0.0314 |     0.0222 |                0.0092 |    0.0032 |
| pre_BE_ratio                 |     1291 |    1251 |      0.5926 |     0.5703 |                0.0224 |    0.0045 |

Interpretation: the split mechanically separates high and low pre-risk-writing burden by construction. The relevant concern is balance on generic firm characteristics such as Size, Lev, ROA, and BE_ratio.

## DID Pilot Results

Window: 2018-2021 and 2023-2024. The 2022 transition year is excluded. 2025 is excluded in this pilot because the reusable controls panel is incomplete for 2025.

Treatment:

```text
PostChatGPT_t * HighPreRiskBurden_i
```

Controls: Size, Lev, ROA.

| outcome                      | spec               |    coef |     se |        t |      p |   nobs |   n_firms |
|:-----------------------------|:-------------------|--------:|-------:|---------:|-------:|-------:|----------:|
| risk_verifiability_index     | firm_year          | -0.0854 | 0.0201 |  -4.2467 | 0      |  13461 |      2542 |
| risk_verifiability_index     | firm_industry_year | -0.0849 | 0.0202 |  -4.1986 | 0      |  13461 |      2542 |
| risk_specificity_index       | firm_year          | -0.2526 | 0.0233 | -10.8411 | 0      |  13461 |      2542 |
| risk_specificity_index       | firm_industry_year | -0.2504 | 0.0233 | -10.7492 | 0      |  13461 |      2542 |
| risk_quality_index_old_style | firm_year          | -0.3733 | 0.0278 | -13.4516 | 0      |  13461 |      2542 |
| risk_quality_index_old_style | firm_industry_year | -0.3706 | 0.0277 | -13.3612 | 0      |  13461 |      2542 |
| risk_boilerplate_ratio       | firm_year          | -0.0046 | 0.0015 |  -3.0034 | 0.0027 |  13461 |      2542 |
| risk_boilerplate_ratio       | firm_industry_year | -0.0046 | 0.0015 |  -2.9953 | 0.0027 |  13461 |      2542 |
| risk_similarity_lag          | firm_year          |  0.0374 | 0.0163 |   2.2945 | 0.0218 |   9896 |      2323 |
| risk_similarity_lag          | firm_industry_year |  0.0368 | 0.0165 |   2.2255 | 0.0261 |   9896 |      2323 |

## Event-study Pilot for Main Y

Outcome: `risk_verifiability_index`. Reference year: 2021. Fixed effects: firm FE + year FE. Controls: Size, Lev, ROA.

|   year |   rel_year |    coef |     se |       t |      p |   nobs |
|-------:|-----------:|--------:|-------:|--------:|-------:|-------:|
|   2018 |         -3 |  0.0551 | 0.0279 |  1.9731 | 0.0485 |  13461 |
|   2019 |         -2 |  0.0457 | 0.0262 |  1.7403 | 0.0818 |  13461 |
|   2020 |         -1 |  0.0208 | 0.022  |  0.944  | 0.3452 |  13461 |
|   2023 |          2 | -0.0656 | 0.0219 | -2.9994 | 0.0027 |  13461 |
|   2024 |          3 | -0.0503 | 0.0236 | -2.1285 | 0.0333 |  13461 |

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
