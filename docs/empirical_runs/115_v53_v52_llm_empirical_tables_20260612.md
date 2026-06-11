# v53 v52/v3.3 LLM empirical tables

## Scope

- Input coding: v52 DeepSeek V4-Pro v3.3 full 1,601-case run.
- Main A sample is model pre-coding only; human review is still required for paper-final claims.
- Preferred peer method: `liu_product_tfidf_same_industry_d_top10`.
- T1-T8 are produced here. T9 supplier benchmark is produced separately by `scripts/run_v54_v52_supplier_benchmark_20260612.py`.

## T1 Coding Distribution

| model_verdict | rows |
|---|---|
| A | 154.0 |
| B | 2.0 |
| C | 51.0 |
| D | 1294.0 |
| D-fw | 85.0 |
| U | 15.0 |

A-field distribution:

| out | mode | layer | realized | rows |
|---|---|---|---|---|
| 1 | own | compute | - | 47.0 |
| 1 | ext | compute | - | 18.0 |
| 1 | own | model | - | 15.0 |
| 1 | own | app | - | 12.0 |
| 1 | ext | model | - | 12.0 |
| 1 | ext | app | - | 9.0 |
| 1 | ext | compute | + | 7.0 |
| 1 | ext | app | + | 6.0 |
| 1 | own | model | + | 5.0 |
| 1 | ext | model | + | 4.0 |
| 0 | ext | model | - | 4.0 |
| 0 | own | model | - | 3.0 |

Event samples:

| sample_name | event_type | events | focal_firms | first_date | last_date |
|---|---|---|---|---|---|
| A_Dfw_stack | A | 154.0 | 119.0 | 2023-04-03 00:00:00 | 2026-05-25 00:00:00 |
| A_Dfw_stack | D-fw | 85.0 | 67.0 | 2023-02-16 00:00:00 | 2026-05-30 00:00:00 |
| A_all | A | 154.0 | 119.0 | 2023-04-03 00:00:00 | 2026-05-25 00:00:00 |
| A_first_firm | A | 119.0 | 119.0 | 2023-04-03 00:00:00 | 2026-05-25 00:00:00 |
| D_nonai_investment_placebo | D | 1145.0 | 692.0 | 2023-01-03 00:00:00 | 2026-06-03 00:00:00 |
| Dfw_all | D-fw | 85.0 | 67.0 | 2023-02-16 00:00:00 | 2026-05-30 00:00:00 |

## Peer Coverage

| sample_name | method_variant | input_events | events_with_peers | event_link_rate | peer_event_obs | unique_peer_firms |
|---|---|---|---|---|---|---|
| A_Dfw_stack | liu_product_tfidf_same_industry_d_top10 | 239.0 | 213.0 | 0.891213 | 2109.0 | 981.0 |
| A_all | liu_product_tfidf_same_industry_d_top10 | 154.0 | 136.0 | 0.883117 | 1348.0 | 753.0 |
| A_first_firm | liu_product_tfidf_same_industry_d_top10 | 119.0 | 102.0 | 0.857143 | 1008.0 | 727.0 |
| D_nonai_investment_placebo | liu_product_tfidf_same_industry_d_top10 | 1145.0 | 502.0 | 0.438428 | 4982.0 | 1913.0 |
| Dfw_all | liu_product_tfidf_same_industry_d_top10 | 85.0 | 77.0 | 0.905882 | 761.0 | 489.0 |

## T2 A-Sample Peer Main Effect

| sample_name | outcome_label | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|
| A_all | AR[0] | 0.000462 | 0.001756 | 0.792611 | 1171.0 | 133.0 | 664.0 | -0.000232 | 0.491887 |
| A_all | CAR[0,+1] | -0.004257 | 0.002321 | 0.066601 | 1171.0 | 133.0 | 664.0 | -0.004048 | 0.437233 |
| A_first_firm | AR[0] | 0.000293 | 0.001937 | 0.879849 | 876.0 | 100.0 | 635.0 | -0.00073 | 0.480594 |
| A_first_firm | CAR[0,+1] | -0.004152 | 0.00258 | 0.107545 | 876.0 | 100.0 | 635.0 | -0.004205 | 0.439498 |

## T3 Layer Heterogeneity

| group_value | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|
| app | -0.000774 | 0.005121 | 0.879904 | 242.0 | 28.0 | 196.0 | -0.001617 | 0.471074 |
| compute | -0.007393 | 0.003749 | 0.048592 | 542.0 | 62.0 | 336.0 | -0.005778 | 0.420664 |
| data | -0.009049 | 0.008971 | 0.313109 | 10.0 | 1.0 | 10.0 | -0.018615 | 0.2 |
| model | -0.001859 | 0.003245 | 0.566844 | 377.0 | 42.0 | 298.0 | -0.002068 | 0.445623 |

## T4 A vs D-fw Contrast

| sample_name | method_variant | group_col | group_value | outcome | outcome_label | estimate | se | z | p | nobs | events | focal_firms | peer_firms | median | positive_share | model | term | coef | overall_r2 | within_r2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A_Dfw_stack | liu_product_tfidf_same_industry_d_top10 | event_type | A | peer_car_0_p1_mm | CAR[0,+1] | -0.004257 | 0.002321 | -1.834356 | 0.066601 | 1171.0 | 133.0 | 102.0 | 664.0 | -0.004048 | 0.437233 | mean_by_event_type |  |  |  |  |
| A_Dfw_stack | liu_product_tfidf_same_industry_d_top10 | event_type | D-fw | peer_car_0_p1_mm | CAR[0,+1] | -0.001529 | 0.003165 | -0.48301 | 0.629089 | 659.0 | 75.0 | 59.0 | 431.0 | -0.002784 | 0.461305 | mean_by_event_type |  |  |  |  |
| A_Dfw_stack | liu_product_tfidf_same_industry_d_top10 |  |  |  |  |  | 0.005365 | -1.00577 | 0.314526 | 1830.0 | 208.0 | 144.0 | 879.0 |  |  | A_vs_Dfw_peer_car | credible_A | -0.005396 | 0.46036 | 0.013828 |
| A_Dfw_stack | liu_product_tfidf_same_industry_d_top10 |  |  |  |  |  | 0.002667 | -0.47101 | 0.637634 | 1830.0 | 208.0 | 144.0 | 879.0 |  |  | A_vs_Dfw_x_AIActive | credible_x_ai | -0.001256 | 0.460411 | 0.013921 |

## T5 Specificity x AIActive

| sample_name | method_variant | ai_def | term | coef | se | z | p | nobs | events | focal_firms | peer_firms | overall_r2 | within_r2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A_all | annual_report_same_industry_d_top10 | current_text_history | spec_ai | 0.007595 | 0.003014 | 2.520325 | 0.011725 | 1144.0 | 134.0 | 102.0 | 653.0 | 0.464928 | 0.026785 |
| A_all | liu_product_tfidf_global_top10 | current_text_history | spec_ai | 0.004883 | 0.002516 | 1.940763 | 0.052287 | 1138.0 | 133.0 | 102.0 | 647.0 | 0.642332 | 0.022316 |
| A_all | liu_product_tfidf_global_top10 | ext_any | spec_ai | 0.004457 | 0.002311 | 1.928778 | 0.053758 | 1138.0 | 133.0 | 102.0 | 647.0 | 0.641768 | 0.020776 |
| A_all | annual_only_semantic_top10 | current_text_history | spec_ai | 0.005015 | 0.003234 | 1.550826 | 0.120943 | 988.0 | 115.0 | 83.0 | 490.0 | 0.465351 | 0.015283 |
| A_all | csmar_scope_product_text_top5 | current_text_history | spec_ai | 0.006153 | 0.004185 | 1.470137 | 0.141525 | 599.0 | 139.0 | 105.0 | 388.0 | 0.689033 | 0.044797 |
| A_all | ren_wang_binary_global_top20 | ext_any | spec_ai | 0.002665 | 0.001829 | 1.456852 | 0.145157 | 2299.0 | 134.0 | 102.0 | 1009.0 | 0.539036 | 0.024093 |
| A_all | csmar_scope_product_text_top5 | ext_any | spec_ai | 0.00669 | 0.004619 | 1.448363 | 0.147516 | 599.0 | 139.0 | 105.0 | 388.0 | 0.692291 | 0.054804 |
| A_all | annual_same_only_semantic_top10 | current_text_history | spec_ai | 0.004359 | 0.003071 | 1.419336 | 0.155801 | 978.0 | 115.0 | 83.0 | 492.0 | 0.453382 | 0.014404 |
| A_all | liu_product_tfidf_global_top20 | ext_any | spec_ai | 0.001946 | 0.001378 | 1.412264 | 0.157872 | 2284.0 | 134.0 | 102.0 | 1057.0 | 0.533926 | 0.0228 |
| A_all | deepseek_flash_top5 | ext_any | spec_ai | 0.004702 | 0.003362 | 1.39856 | 0.161945 | 595.0 | 137.0 | 103.0 | 357.0 | 0.565569 | 0.031793 |
| A_all | liu_product_tfidf_global_top20 | current_text_history | spec_ai | 0.002654 | 0.001914 | 1.386269 | 0.165665 | 2284.0 | 134.0 | 102.0 | 1057.0 | 0.534045 | 0.023051 |
| A_all | annual_report_global_ai_stripped_top10 | ext_any | spec_ai | 0.004006 | 0.003168 | 1.26455 | 0.206033 | 1137.0 | 134.0 | 102.0 | 620.0 | 0.648716 | 0.019295 |
| A_all | deepseek_open_ended_same_industry_top5 | ext_any | spec_ai | 0.002902 | 0.002453 | 1.183026 | 0.236799 | 347.0 | 110.0 | 83.0 | 208.0 | 0.70407 | 0.005979 |
| A_all | liu_product_tfidf_same_industry_d_top20 | current_text_history | spec_ai | 0.002272 | 0.001965 | 1.156224 | 0.24759 | 2296.0 | 134.0 | 102.0 | 1106.0 | 0.38195 | 0.013239 |
| A_all | placebo_low_similarity_top5 | current_text_history | spec_ai | -0.006906 | 0.005992 | -1.152621 | 0.249066 | 576.0 | 139.0 | 105.0 | 379.0 | 0.742217 | 0.008383 |
| A_all | full_semantic_reranked_top10 | current_text_history | spec_ai | 0.00335 | 0.002924 | 1.145807 | 0.251875 | 1179.0 | 139.0 | 105.0 | 657.0 | 0.432215 | 0.00498 |
| A_all | ren_wang_binary_global_top10 | current_text_history | spec_ai | -0.004277 | 0.003918 | -1.091761 | 0.274938 | 1152.0 | 134.0 | 102.0 | 620.0 | 0.625505 | 0.025817 |
| A_all | liu_product_tfidf_same_industry_d_top10 | current_text_history | spec_ai | 0.003228 | 0.002967 | 1.087877 | 0.276649 | 1171.0 | 133.0 | 102.0 | 664.0 | 0.459729 | 0.010995 |
| A_all | liu_product_tfidf_same_industry_d_top20 | ext_any | spec_ai | 0.00155 | 0.001472 | 1.052618 | 0.292516 | 2296.0 | 134.0 | 102.0 | 1106.0 | 0.381723 | 0.012875 |
| A_all | deepseek_open_ended_top5 | current_text_history | spec_ai | -0.003085 | 0.002995 | -1.030021 | 0.303 | 497.0 | 127.0 | 99.0 | 298.0 | 0.749516 | 0.003592 |

## T6 OUT/M/R/Layer x AIActive Cuts

| cut | term | coef | se | z | p | nobs | events | focal_firms | peer_firms | overall_r2 | within_r2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| OUT_1 | cut_x_ai | -0.00839 | 0.00425 | -1.974303 | 0.048347 | 1171.0 | 133.0 | 102.0 | 664.0 | 0.4596 | 0.01076 |
| M_ext | cut_x_ai | -0.004791 | 0.00413 | -1.160148 | 0.245988 | 1171.0 | 133.0 | 102.0 | 664.0 | 0.45953 | 0.010632 |
| L_compute | cut_x_ai | -0.002094 | 0.004353 | -0.481109 | 0.630439 | 1171.0 | 133.0 | 102.0 | 664.0 | 0.459067 | 0.009784 |
| R_plus | cut_x_ai | -0.001266 | 0.00541 | -0.234008 | 0.814979 | 1171.0 | 133.0 | 102.0 | 664.0 | 0.458978 | 0.009622 |
| L_model_app | cut_x_ai | 0.000816 | 0.004343 | 0.187856 | 0.850989 | 1171.0 | 133.0 | 102.0 | 664.0 | 0.458972 | 0.00961 |

## T7 Ex-Post Validation Readout

| event_type | events | cac_by_event_p365 | cac_post365_new | ai_patent_by_event_p365 | ai_patent_post365_new | genai_patent_by_event_p365 | genai_patent_post365_new | history_by_event_p365 | history_post365_new | post365_broad_ai_hiring | post365_genai_hiring |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 154.0 | 0.084416 | 0.045455 | 0.097403 | 0.006494 | 0.012987 | 0.0 | 0.88961 | 0.103896 | 3.75974 | 1.88961 |
| D-fw | 85.0 | 0.058824 | 0.011765 | 0.035294 | 0.011765 | 0.0 | 0.0 | 0.952941 | 0.2 | 1.576471 | 0.670588 |

## T8 Non-GenAI Investment Placebo

| sample_name | outcome_label | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|
| D_nonai_investment_placebo | AR[0] | -0.000216 | 0.000672 | 0.747526 | 4305.0 | 498.0 | 1693.0 | -0.000354 | 0.49036 |
| D_nonai_investment_placebo | CAR[0,+1] | -0.001989 | 0.000937 | 0.033684 | 4305.0 | 498.0 | 1693.0 | -0.002241 | 0.455981 |

## Output Files

- `results/v53_v52_llm_empirical_tables_20260612/v52_coded_rows_enriched.csv`
- `results/v53_v52_llm_empirical_tables_20260612/v52_event_samples.csv`
- `results/v53_v52_llm_empirical_tables_20260612/peer_link_panel.csv.gz`
- `results/v53_v52_llm_empirical_tables_20260612/analysis_panel_with_returns_ai.csv.gz`
- `results/v53_v52_llm_empirical_tables_20260612/t1_coding_verdict_distribution.csv`
- `results/v53_v52_llm_empirical_tables_20260612/t2_peer_main_effect.csv`
- `results/v53_v52_llm_empirical_tables_20260612/t3_layer_heterogeneity.csv`
- `results/v53_v52_llm_empirical_tables_20260612/t4_a_vs_dfw_contrast.csv`
- `results/v53_v52_llm_empirical_tables_20260612/t5_specificity_x_ai.csv`
- `results/v53_v52_llm_empirical_tables_20260612/t6_out_m_r_layer_cuts.csv`
- `results/v53_v52_llm_empirical_tables_20260612/t7_validation_summary.csv`
- `results/v53_v52_llm_empirical_tables_20260612/t8_nonai_investment_placebo.csv`
