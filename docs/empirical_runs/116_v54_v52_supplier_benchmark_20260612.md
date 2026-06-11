# v54 v52 supplier benchmark

## Scope

- Input events: v52/v3.3 LLM-coded sample produced in v53, after valid A-share code and event-date filters.
- Supplier links: CSMAR supply-chain network plus top-five supplier/customer tables, event-year minus 1 to minus 5.
- Return measure: same market-model abnormal returns as the competitor event study.
- This is a benchmark, not the headline identification table; listed supplier coverage is sparse in A-share data.

## Supplier Coverage

| sample_name | event_type | edge_family | input_events | events_with_suppliers | event_link_rate | supplier_event_obs | supplier_firms | customer_firms_with_suppliers |
|---|---|---|---|---|---|---|---|---|
| A_Dfw_stack | A | network | 153.0 | 9.0 | 0.058824 | 20.0 | 20.0 | 9.0 |
| A_Dfw_stack | A | topfive | 153.0 | 9.0 | 0.058824 | 17.0 | 17.0 | 9.0 |
| A_Dfw_stack | A | union | 153.0 | 9.0 | 0.058824 | 20.0 | 20.0 | 9.0 |
| A_Dfw_stack | D-fw | network | 85.0 | 13.0 | 0.152941 | 37.0 | 23.0 | 9.0 |
| A_Dfw_stack | D-fw | topfive | 85.0 | 11.0 | 0.129412 | 22.0 | 12.0 | 7.0 |
| A_Dfw_stack | D-fw | union | 85.0 | 13.0 | 0.152941 | 37.0 | 23.0 | 9.0 |
| A_all | A | network | 153.0 | 9.0 | 0.058824 | 20.0 | 20.0 | 9.0 |
| A_all | A | topfive | 153.0 | 9.0 | 0.058824 | 17.0 | 17.0 | 9.0 |
| A_all | A | union | 153.0 | 9.0 | 0.058824 | 20.0 | 20.0 | 9.0 |
| A_first_firm | A | network | 118.0 | 9.0 | 0.076271 | 20.0 | 20.0 | 9.0 |
| A_first_firm | A | topfive | 118.0 | 9.0 | 0.076271 | 17.0 | 17.0 | 9.0 |
| A_first_firm | A | union | 118.0 | 9.0 | 0.076271 | 20.0 | 20.0 | 9.0 |
| Dfw_all | D-fw | network | 85.0 | 13.0 | 0.152941 | 37.0 | 23.0 | 9.0 |
| Dfw_all | D-fw | topfive | 85.0 | 11.0 | 0.129412 | 22.0 | 12.0 | 7.0 |
| Dfw_all | D-fw | union | 85.0 | 13.0 | 0.152941 | 37.0 | 23.0 | 9.0 |

## T9 Supplier Event Study

| sample_name | event_type | edge_family | outcome_label | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A_Dfw_stack | A | union | AR[0] | 0.00287 | 0.002462 | 0.243704 | 15.0 | 7.0 | 15.0 | 0.001317 | 0.533333 |
| A_Dfw_stack | A | union | CAR[0,+1] | 0.006154 | 0.005394 | 0.253899 | 15.0 | 7.0 | 15.0 | -2.8e-05 | 0.466667 |
| A_Dfw_stack | D-fw | union | AR[0] | -0.001335 | 0.004 | 0.738608 | 27.0 | 11.0 | 19.0 | -0.003413 | 0.333333 |
| A_Dfw_stack | D-fw | union | CAR[0,+1] | -0.002576 | 0.011716 | 0.825959 | 27.0 | 11.0 | 19.0 | -0.013704 | 0.259259 |
| A_all | A | union | AR[0] | 0.00287 | 0.002462 | 0.243704 | 15.0 | 7.0 | 15.0 | 0.001317 | 0.533333 |
| A_all | A | union | CAR[0,+1] | 0.006154 | 0.005394 | 0.253899 | 15.0 | 7.0 | 15.0 | -2.8e-05 | 0.466667 |
| A_first_firm | A | union | AR[0] | 0.00287 | 0.002462 | 0.243704 | 15.0 | 7.0 | 15.0 | 0.001317 | 0.533333 |
| A_first_firm | A | union | CAR[0,+1] | 0.006154 | 0.005394 | 0.253899 | 15.0 | 7.0 | 15.0 | -2.8e-05 | 0.466667 |
| Dfw_all | D-fw | union | AR[0] | -0.001335 | 0.004 | 0.738608 | 27.0 | 11.0 | 19.0 | -0.003413 | 0.333333 |
| Dfw_all | D-fw | union | CAR[0,+1] | -0.002576 | 0.011716 | 0.825959 | 27.0 | 11.0 | 19.0 | -0.013704 | 0.259259 |

## Competitor vs Supplier Sign Check

| side | sample_name | edge_family | outcome_label | estimate | se | p | events | firms |
|---|---|---|---|---|---|---|---|---|
| product_market_competitors | A_all | liu_product_tfidf_same_industry_d_top10 | CAR[0,+1] | -0.004257 | 0.002321 | 0.066601 | 133.0 | 664.0 |
| listed_suppliers | A_all | union | CAR[0,+1] | 0.006154 | 0.005394 | 0.253899 | 7.0 | 15.0 |

## Output Files

- `results/v54_v52_supplier_benchmark_20260612/supplier_coverage_summary.csv`
- `results/v54_v52_supplier_benchmark_20260612/supplier_event_panel.csv.gz`
- `results/v54_v52_supplier_benchmark_20260612/supplier_event_panel_with_returns.csv.gz`
- `results/v54_v52_supplier_benchmark_20260612/t9_supplier_event_study.csv`
- `results/v54_v52_supplier_benchmark_20260612/competitor_vs_supplier_sign_check.csv`
- `results/v54_v52_supplier_benchmark_20260612/v54_v52_supplier_benchmark_20260612.xlsx`
