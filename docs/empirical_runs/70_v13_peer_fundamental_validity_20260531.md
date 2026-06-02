# v13 Peer Fundamental Validity Gate

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

| peer_system                              | metric                  |    corr |      p |   n_focal_year |   focal_firms | years                    |
|:-----------------------------------------|:------------------------|--------:|-------:|---------------:|--------------:|:-------------------------|
| csmar_scope_top5                         | sales_growth_year_resid |  0.1327 | 0      |          12137 |          2652 | 2021,2022,2023,2024,2025 |
| csmar_scope_top5                         | gross_margin_year_resid |  0.4413 | 0      |          12268 |          2652 | 2021,2022,2023,2024,2025 |
| random_same_industry_top5                | sales_growth_year_resid |  0.0598 | 0      |          11921 |          2598 | 2021,2022,2023,2024,2025 |
| random_same_industry_top5                | gross_margin_year_resid |  0.3106 | 0      |          12034 |          2598 | 2021,2022,2023,2024,2025 |
| low_similarity_same_industry_top5        | sales_growth_year_resid | -0.0195 | 0.0356 |          11600 |          2599 | 2021,2022,2023,2024,2025 |
| low_similarity_same_industry_top5        | gross_margin_year_resid |  0.3489 | 0      |          11724 |          2599 | 2021,2022,2023,2024,2025 |
| annual_same_industry_next_year_top5      | sales_growth_year_resid |  0.2028 | 0      |           4767 |          2587 | 2022,2023,2024,2025      |
| annual_same_industry_next_year_top5      | gross_margin_year_resid |  0.6139 | 0      |           4632 |          2587 | 2022,2023,2024,2025      |
| annual_global_next_year_top5             | sales_growth_year_resid |  0.1898 | 0      |           4774 |          2592 | 2022,2023,2024,2025      |
| annual_global_next_year_top5             | gross_margin_year_resid |  0.5497 | 0      |           4643 |          2592 | 2022,2023,2024,2025      |
| annual_global_ai_stripped_next_year_top5 | sales_growth_year_resid |  0.188  | 0      |           4774 |          2592 | 2022,2023,2024,2025      |
| annual_global_ai_stripped_next_year_top5 | gross_margin_year_resid |  0.5527 | 0      |           4643 |          2592 | 2022,2023,2024,2025      |

## Output

```text
results/v13_peer_validity_gate_20260531/peer_validity_fundamental_comovement_summary.csv
```

## Reading

This is a first-pass gate. Revenue/gross-margin validation is noisier than daily
return comovement because annual accounting data provide only a few observations
per firm. It should be used as supportive evidence, not as the sole peer-selection
criterion.

## Interpretation

The fundamental-comovement gate points in the same direction as the return-comovement
gate:

1. The old `csmar_scope_top5` peer network is not invalid. It has higher
   sales-growth comovement than random same-industry peers:

   ```text
   csmar_scope_top5 sales-growth corr = 0.1327
   random same-industry sales-growth corr = 0.0598
   low-similarity same-industry sales-growth corr = -0.0195
   ```

   It also has higher gross-margin comovement than random same-industry peers:

   ```text
   csmar_scope_top5 gross-margin corr = 0.4413
   random same-industry gross-margin corr = 0.3106
   low-similarity same-industry gross-margin corr = 0.3489
   ```

2. The annual-report text peers are stronger on fundamentals:

   ```text
   annual same-industry text sales-growth corr = 0.2028
   annual same-industry text gross-margin corr = 0.6139
   annual global text sales-growth corr = 0.1898
   annual global text gross-margin corr = 0.5497
   annual global AI-word-stripped text sales-growth corr = 0.1880
   annual global AI-word-stripped text gross-margin corr = 0.5527
   ```

3. This creates a clean measurement conclusion:

   ```text
   If the paper needs the most literature-clean peer-definition system,
   annual-report text peers are better.

   If the paper keeps the current significant PeerCAR result,
   old CSMAR scope peers must be defended as a valid but not dominant
   Hoberg-Phillips-style business-description peer system.
   ```

4. Therefore, the current paper should not present peer construction as settled.
   The honest framing is:

   ```text
   We identify product-market peers using a text-based business-description approach.
   The headline CSMAR business-scope network passes return and fundamentals
   validity gates relative to random and low-similarity industry peers, but a
   stricter annual-report text network has even stronger peer-validity metrics and
   does not reproduce the same GenAI-event coefficient. Peer definition is therefore
   a first-order limitation and robustness issue.
   ```
