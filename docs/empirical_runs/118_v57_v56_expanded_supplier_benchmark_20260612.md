# v57 v56 expanded supplier benchmark

## Scope

- Input events: v56 expanded v52+v55 LLM-coded samples.
- Supplier links: CSMAR supply-chain network plus top-five supplier/customer tables, event-year minus 1 to minus 5.
- Return measure: same market-model abnormal returns as the competitor event study.
- This remains a benchmark because listed-supplier coverage is sparse.

## Supplier Coverage

| sample_name | event_type | edge_family | input_events | events_with_suppliers | event_link_rate | supplier_event_obs | supplier_firms | customer_firms_with_suppliers |
|---|---|---|---|---|---|---|---|---|
| A_Dfw_stack | A | network | 201.0 | 14.0 | 0.069652 | 26.0 | 25.0 | 13.0 |
| A_Dfw_stack | A | topfive | 201.0 | 14.0 | 0.069652 | 23.0 | 22.0 | 13.0 |
| A_Dfw_stack | A | union | 201.0 | 14.0 | 0.069652 | 26.0 | 25.0 | 13.0 |
| A_Dfw_stack | D-fw | network | 142.0 | 20.0 | 0.140845 | 51.0 | 35.0 | 16.0 |
| A_Dfw_stack | D-fw | topfive | 142.0 | 18.0 | 0.126761 | 36.0 | 24.0 | 14.0 |
| A_Dfw_stack | D-fw | union | 142.0 | 20.0 | 0.140845 | 51.0 | 35.0 | 16.0 |
| A_all | A | network | 201.0 | 14.0 | 0.069652 | 26.0 | 25.0 | 13.0 |
| A_all | A | topfive | 201.0 | 14.0 | 0.069652 | 23.0 | 22.0 | 13.0 |
| A_all | A | union | 201.0 | 14.0 | 0.069652 | 26.0 | 25.0 | 13.0 |
| A_first_firm | A | network | 159.0 | 13.0 | 0.081761 | 25.0 | 25.0 | 13.0 |
| A_first_firm | A | topfive | 159.0 | 13.0 | 0.081761 | 22.0 | 22.0 | 13.0 |
| A_first_firm | A | union | 159.0 | 13.0 | 0.081761 | 25.0 | 25.0 | 13.0 |
| A_old363_reaudited_first | A | network | 118.0 | 11.0 | 0.09322 | 21.0 | 21.0 | 11.0 |
| A_old363_reaudited_first | A | topfive | 118.0 | 11.0 | 0.09322 | 19.0 | 19.0 | 11.0 |
| A_old363_reaudited_first | A | union | 118.0 | 11.0 | 0.09322 | 21.0 | 21.0 | 11.0 |
| Dfw_all | D-fw | network | 142.0 | 20.0 | 0.140845 | 51.0 | 35.0 | 16.0 |
| Dfw_all | D-fw | topfive | 142.0 | 18.0 | 0.126761 | 36.0 | 24.0 | 14.0 |
| Dfw_all | D-fw | union | 142.0 | 20.0 | 0.140845 | 51.0 | 35.0 | 16.0 |

## T9 Supplier Event Study

| sample_name | event_type | edge_family | outcome_label | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A_Dfw_stack | A | union | AR[0] | 0.001403 | 0.002347 | 0.549973 | 21.0 | 12.0 | 20.0 | -0.000309 | 0.47619 |
| A_Dfw_stack | A | union | CAR[0,+1] | 0.012467 | 0.00835 | 0.135437 | 21.0 | 12.0 | 20.0 | -0.003398 | 0.428571 |
| A_Dfw_stack | D-fw | union | AR[0] | -0.002054 | 0.00337 | 0.542313 | 39.0 | 17.0 | 30.0 | -0.005612 | 0.307692 |
| A_Dfw_stack | D-fw | union | CAR[0,+1] | -0.005077 | 0.009885 | 0.607551 | 39.0 | 17.0 | 30.0 | -0.017407 | 0.25641 |
| A_all | A | union | AR[0] | 0.001403 | 0.002347 | 0.549973 | 21.0 | 12.0 | 20.0 | -0.000309 | 0.47619 |
| A_all | A | union | CAR[0,+1] | 0.012467 | 0.00835 | 0.135437 | 21.0 | 12.0 | 20.0 | -0.003398 | 0.428571 |
| A_first_firm | A | union | AR[0] | 0.000934 | 0.002484 | 0.706987 | 20.0 | 11.0 | 20.0 | -0.00048 | 0.45 |
| A_first_firm | A | union | CAR[0,+1] | 0.013933 | 0.009 | 0.121576 | 20.0 | 11.0 | 20.0 | -0.001713 | 0.45 |
| A_old363_reaudited_first | A | union | AR[0] | 0.002418 | 0.002314 | 0.296009 | 17.0 | 9.0 | 17.0 | 0.001317 | 0.529412 |
| A_old363_reaudited_first | A | union | CAR[0,+1] | 0.018971 | 0.009956 | 0.056703 | 17.0 | 9.0 | 17.0 | 0.003747 | 0.529412 |
| Dfw_all | D-fw | union | AR[0] | -0.002054 | 0.00337 | 0.542313 | 39.0 | 17.0 | 30.0 | -0.005612 | 0.307692 |
| Dfw_all | D-fw | union | CAR[0,+1] | -0.005077 | 0.009885 | 0.607551 | 39.0 | 17.0 | 30.0 | -0.017407 | 0.25641 |

## Competitor vs Supplier Sign Check

| side | sample_name | edge_family | outcome_label | estimate | se | p | events | firms |
|---|---|---|---|---|---|---|---|---|
| product_market_competitors | A_all | liu_product_tfidf_same_industry_d_top10 | CAR[0,+1] | -0.005859 | 0.002224 | 0.008432 | 178.0 | 811.0 |
| listed_suppliers | A_all | union | CAR[0,+1] | 0.012467 | 0.00835 | 0.135437 | 12.0 | 20.0 |

## Output Files

- `results/v57_v56_expanded_supplier_benchmark_20260612/supplier_coverage_summary.csv`
- `results/v57_v56_expanded_supplier_benchmark_20260612/supplier_event_panel.csv.gz`
- `results/v57_v56_expanded_supplier_benchmark_20260612/supplier_event_panel_with_returns.csv.gz`
- `results/v57_v56_expanded_supplier_benchmark_20260612/t9_supplier_event_study.csv`
- `results/v57_v56_expanded_supplier_benchmark_20260612/competitor_vs_supplier_sign_check.csv`
- `results/v57_v56_expanded_supplier_benchmark_20260612/v57_v56_expanded_supplier_benchmark_20260612.xlsx`
