# v56 expanded v55/v52 LLM empirical tables

## Scope

- Input coding: v52 POM-like 1,601-case v3.3 run plus v55 recoding of the 197 old-v36 first-firm events missing from v52.
- `A_old363_reaudited_first` answers how many of the old 363 first-firm events survive the stricter v3.3 rules.
- `A_first_firm` is the preferred expanded first-firm sample over the union of v52 and v55.
- Preferred peer method: `liu_product_tfidf_same_industry_d_top10`.

## T1 Coding Distribution

| source_batch | model_verdict | rows |
|---|---|---|
| v52_pom_like_1601 | A | 154.0 |
| v52_pom_like_1601 | B | 2.0 |
| v52_pom_like_1601 | C | 51.0 |
| v52_pom_like_1601 | D | 1294.0 |
| v52_pom_like_1601 | D-fw | 85.0 |
| v52_pom_like_1601 | U | 15.0 |
| v55_old_v36_missing197 | A | 49.0 |
| v55_old_v36_missing197 | B | 7.0 |
| v55_old_v36_missing197 | C | 30.0 |
| v55_old_v36_missing197 | D | 41.0 |
| v55_old_v36_missing197 | D-fw | 57.0 |
| v55_old_v36_missing197 | U | 13.0 |

Old 363 reaudited distribution:

| model_verdict | rows |
|---|---|
| A | 119.0 |
| B | 7.0 |
| C | 40.0 |
| D | 85.0 |
| D-fw | 97.0 |
| U | 15.0 |

A-field distribution:

| source_batch | out | mode | layer | realized | rows |
|---|---|---|---|---|---|
| v52_pom_like_1601 | 1 | own | compute | - | 47.0 |
| v52_pom_like_1601 | 1 | ext | compute | - | 18.0 |
| v52_pom_like_1601 | 1 | own | model | - | 15.0 |
| v52_pom_like_1601 | 1 | ext | model | - | 12.0 |
| v52_pom_like_1601 | 1 | own | app | - | 12.0 |
| v52_pom_like_1601 | 1 | ext | app | - | 9.0 |
| v52_pom_like_1601 | 1 | ext | compute | + | 7.0 |
| v52_pom_like_1601 | 1 | ext | app | + | 6.0 |
| v52_pom_like_1601 | 1 | own | model | + | 5.0 |
| v52_pom_like_1601 | 0 | ext | model | - | 4.0 |
| v52_pom_like_1601 | 1 | ext | model | + | 4.0 |
| v52_pom_like_1601 | 0 | own | model | - | 3.0 |
| v52_pom_like_1601 | 1 | own | app | + | 3.0 |
| v52_pom_like_1601 | 0 | ext | model | + | 2.0 |
| v52_pom_like_1601 | 0 | ext | app | - | 1.0 |
| v52_pom_like_1601 | 0 | ext | compute | - | 1.0 |
| v52_pom_like_1601 | 0 | own | app | + | 1.0 |
| v52_pom_like_1601 | 0 | own | compute | - | 1.0 |
| v52_pom_like_1601 | 0 | own | data | - | 1.0 |
| v52_pom_like_1601 | 1 | own | compute | + | 1.0 |

Event samples:

| sample_name | event_type | events | focal_firms | first_date | last_date |
|---|---|---|---|---|---|
| A_Dfw_stack | A | 203.0 | 160.0 | 2023-03-30 00:00:00 | 2026-05-25 00:00:00 |
| A_Dfw_stack | D-fw | 142.0 | 123.0 | 2023-02-16 00:00:00 | 2026-05-30 00:00:00 |
| A_all | A | 203.0 | 160.0 | 2023-03-30 00:00:00 | 2026-05-25 00:00:00 |
| A_first_firm | A | 160.0 | 160.0 | 2023-03-30 00:00:00 | 2026-05-25 00:00:00 |
| A_old363_reaudited_first | A | 119.0 | 119.0 | 2023-03-30 00:00:00 | 2026-04-28 00:00:00 |
| D_nonai_investment_placebo | D | 1145.0 | 692.0 | 2023-01-03 00:00:00 | 2026-06-03 00:00:00 |
| Dfw_all | D-fw | 142.0 | 123.0 | 2023-02-16 00:00:00 | 2026-05-30 00:00:00 |

## Peer Coverage

| sample_name | method_variant | input_events | events_with_peers | event_link_rate | peer_event_obs | unique_peer_firms |
|---|---|---|---|---|---|---|
| A_Dfw_stack | liu_product_tfidf_same_industry_d_top10 | 345.0 | 312.0 | 0.904348 | 3085.0 | 1312.0 |
| A_all | liu_product_tfidf_same_industry_d_top10 | 203.0 | 181.0 | 0.891626 | 1788.0 | 906.0 |
| A_first_firm | liu_product_tfidf_same_industry_d_top10 | 160.0 | 140.0 | 0.875 | 1378.0 | 879.0 |
| A_old363_reaudited_first | liu_product_tfidf_same_industry_d_top10 | 119.0 | 106.0 | 0.890756 | 1038.0 | 669.0 |
| D_nonai_investment_placebo | liu_product_tfidf_same_industry_d_top10 | 1145.0 | 502.0 | 0.438428 | 4982.0 | 1913.0 |
| Dfw_all | liu_product_tfidf_same_industry_d_top10 | 142.0 | 131.0 | 0.922535 | 1297.0 | 795.0 |

## T2 A-Sample Peer Main Effect

| sample_name | outcome_label | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|
| A_all | AR[0] | -0.000633 | 0.001562 | 0.685095 | 1578.0 | 178.0 | 811.0 | -0.000852 | 0.478454 |
| A_all | CAR[0,+1] | -0.005859 | 0.002224 | 0.008432 | 1578.0 | 178.0 | 811.0 | -0.004351 | 0.429024 |
| A_first_firm | AR[0] | -0.001442 | 0.001735 | 0.406143 | 1216.0 | 138.0 | 780.0 | -0.001671 | 0.463816 |
| A_first_firm | CAR[0,+1] | -0.006558 | 0.002561 | 0.010464 | 1216.0 | 138.0 | 780.0 | -0.004324 | 0.428454 |
| A_old363_reaudited_first | AR[0] | -0.002825 | 0.002171 | 0.193139 | 941.0 | 106.0 | 607.0 | -0.002366 | 0.451647 |
| A_old363_reaudited_first | CAR[0,+1] | -0.009614 | 0.00317 | 0.002424 | 941.0 | 106.0 | 607.0 | -0.007201 | 0.402763 |

## T3 Layer Heterogeneity

| group_value | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|
| app | -0.005784 | 0.004812 | 0.229435 | 385.0 | 44.0 | 292.0 | -0.00423 | 0.428571 |
| compute | -0.007225 | 0.003558 | 0.042289 | 601.0 | 68.0 | 360.0 | -0.005781 | 0.414309 |
| data | -0.054263 | 0.035523 | 0.126629 | 18.0 | 2.0 | 18.0 | -0.033685 | 0.111111 |
| model | -0.002962 | 0.003161 | 0.348722 | 574.0 | 64.0 | 408.0 | -0.002058 | 0.454704 |

## T4 A vs D-fw Contrast

| sample_name | method_variant | group_col | group_value | outcome | outcome_label | estimate | se | z | p | nobs | events | focal_firms | peer_firms | median | positive_share | model | term | coef | overall_r2 | within_r2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A_Dfw_stack | liu_product_tfidf_same_industry_d_top10 | event_type | A | peer_car_0_p1_mm | CAR[0,+1] | -0.005859 | 0.002224 | -2.634247 | 0.008432 | 1578.0 | 178.0 | 140.0 | 811.0 | -0.004351 | 0.429024 | mean_by_event_type |  |  |  |  |
| A_Dfw_stack | liu_product_tfidf_same_industry_d_top10 | event_type | D-fw | peer_car_0_p1_mm | CAR[0,+1] | -0.000192 | 0.002278 | -0.084214 | 0.932886 | 1137.0 | 129.0 | 112.0 | 704.0 | -0.001799 | 0.471416 | mean_by_event_type |  |  |  |  |
| A_Dfw_stack | liu_product_tfidf_same_industry_d_top10 |  |  |  |  |  | 0.005202 | -2.316047 | 0.020556 | 2715.0 | 307.0 | 231.0 | 1189.0 |  |  | A_vs_Dfw_peer_car | credible_A | -0.012047 | 0.419102 | 0.019286 |
| A_Dfw_stack | liu_product_tfidf_same_industry_d_top10 |  |  |  |  |  | 0.002597 | -1.154188 | 0.248423 | 2715.0 | 307.0 | 231.0 | 1189.0 |  |  | A_vs_Dfw_x_AIActive | credible_x_ai | -0.002998 | 0.419324 | 0.019661 |

## T5 Specificity x AIActive

| sample_name | method_variant | ai_def | term | coef | se | z | p | nobs | events | focal_firms | peer_firms | overall_r2 | within_r2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A_all | annual_report_same_industry_d_top10 | current_text_history | spec_ai | 0.005237 | 0.001821 | 2.874935 | 0.004041 | 1548.0 | 179.0 | 140.0 | 801.0 | 0.515732 | 0.026337 |
| A_all | annual_only_semantic_top10 | ext_any | spec_ai | 0.004154 | 0.001675 | 2.480446 | 0.013122 | 1329.0 | 153.0 | 114.0 | 614.0 | 0.495892 | 0.011533 |
| A_all | full_semantic_reranked_top10 | ext_any | spec_ai | 0.003706 | 0.001535 | 2.414913 | 0.015739 | 1574.0 | 184.0 | 143.0 | 825.0 | 0.470878 | 0.013241 |
| A_all | ren_wang_binary_global_top20 | ext_any | spec_ai | 0.002679 | 0.001238 | 2.163374 | 0.030512 | 3099.0 | 179.0 | 140.0 | 1193.0 | 0.553961 | 0.018045 |
| A_all | annual_same_only_semantic_top10 | ext_any | spec_ai | 0.003537 | 0.00171 | 2.068759 | 0.038569 | 1313.0 | 153.0 | 114.0 | 607.0 | 0.490011 | 0.010587 |
| A_all | liu_product_tfidf_global_top10 | current_text_history | spec_ai | 0.003948 | 0.002005 | 1.968924 | 0.048962 | 1537.0 | 178.0 | 140.0 | 804.0 | 0.635592 | 0.019101 |
| A_all | annual_only_semantic_top5 | ext_any | spec_ai | 0.004151 | 0.002245 | 1.848888 | 0.064474 | 668.0 | 152.0 | 114.0 | 360.0 | 0.577474 | 0.011687 |
| A_all | csmar_scope_product_text_top10 | current_text_history | spec_ai | -0.00363 | 0.002063 | -1.759957 | 0.078415 | 1578.0 | 184.0 | 143.0 | 902.0 | 0.641197 | 0.011331 |
| A_all | csmar_scope_semantic_only_top10 | current_text_history | spec_ai | -0.004233 | 0.002413 | -1.754205 | 0.079395 | 1496.0 | 184.0 | 143.0 | 856.0 | 0.645293 | 0.01416 |
| A_all | annual_same_only_semantic_top5 | ext_any | spec_ai | 0.004163 | 0.00245 | 1.699582 | 0.08921 | 663.0 | 152.0 | 114.0 | 352.0 | 0.568367 | 0.010843 |
| A_all | annual_report_global_ai_stripped_top10 | ext_any | spec_ai | 0.003349 | 0.002031 | 1.648746 | 0.0992 | 1526.0 | 179.0 | 140.0 | 765.0 | 0.658313 | 0.021533 |
| A_all | annual_report_global_top10 | ext_any | spec_ai | 0.00282 | 0.001858 | 1.518386 | 0.128917 | 1528.0 | 179.0 | 140.0 | 758.0 | 0.655934 | 0.018173 |
| A_all | liu_product_tfidf_global_top10 | ext_any | spec_ai | 0.002174 | 0.001492 | 1.457409 | 0.145003 | 1537.0 | 178.0 | 140.0 | 804.0 | 0.635077 | 0.017717 |
| A_all | deepseek_flash_top5 | ext_any | spec_ai | 0.004038 | 0.002841 | 1.421465 | 0.155182 | 792.0 | 182.0 | 141.0 | 466.0 | 0.604891 | 0.036186 |
| A_all | deepseek_open_ended_same_industry_top5 | ext_any | spec_ai | 0.005528 | 0.003959 | 1.396414 | 0.16259 | 494.0 | 151.0 | 118.0 | 269.0 | 0.73367 | 0.015304 |
| A_all | placebo_low_similarity_top5 | current_text_history | spec_ai | -0.0072 | 0.005236 | -1.375229 | 0.16906 | 765.0 | 184.0 | 143.0 | 502.0 | 0.747562 | 0.008241 |
| A_all | liu_product_tfidf_same_industry_d_top5 | ext_any | spec_ai | -0.002183 | 0.001598 | -1.365883 | 0.171976 | 790.0 | 178.0 | 140.0 | 493.0 | 0.549248 | 0.021597 |
| A_all | liu_product_tfidf_same_industry_d_top20 | current_text_history | spec_ai | 0.001712 | 0.001329 | 1.288349 | 0.197625 | 3081.0 | 179.0 | 140.0 | 1299.0 | 0.431424 | 0.01451 |
| A_all | full_semantic_reranked_top10 | current_text_history | spec_ai | 0.003041 | 0.002368 | 1.283833 | 0.1992 | 1574.0 | 184.0 | 143.0 | 825.0 | 0.469412 | 0.010508 |
| A_all | ren_wang_binary_global_top5 | ext_any | spec_ai | -0.004418 | 0.003499 | -1.262649 | 0.206716 | 780.0 | 178.0 | 140.0 | 434.0 | 0.727497 | 0.014836 |
| A_all | annual_only_semantic_top10 | current_text_history | spec_ai | 0.0027 | 0.002249 | 1.200426 | 0.229974 | 1329.0 | 153.0 | 114.0 | 614.0 | 0.49448 | 0.008764 |
| A_all | csmar_scope_semantic_only_top5 | current_text_history | spec_ai | -0.003521 | 0.002993 | -1.176263 | 0.23949 | 779.0 | 184.0 | 143.0 | 503.0 | 0.658743 | 0.006466 |
| A_all | full_semantic_reranked_top5 | current_text_history | spec_ai | -0.002482 | 0.002244 | -1.106108 | 0.26868 | 796.0 | 183.0 | 143.0 | 470.0 | 0.579626 | 0.00852 |
| A_all | placebo_random_top5 | current_text_history | spec_ai | 0.004808 | 0.004565 | 1.053219 | 0.292241 | 775.0 | 184.0 | 143.0 | 491.0 | 0.776776 | 0.018158 |
| A_all | annual_report_same_industry_d_top5 | current_text_history | spec_ai | 0.001956 | 0.001923 | 1.016923 | 0.30919 | 774.0 | 178.0 | 140.0 | 480.0 | 0.586064 | 0.022412 |
| A_all | annual_same_only_semantic_top10 | current_text_history | spec_ai | 0.002016 | 0.002153 | 0.936448 | 0.349043 | 1313.0 | 153.0 | 114.0 | 607.0 | 0.488856 | 0.008345 |
| A_all | annual_report_same_industry_d_top10 | ext_any | spec_ai | 0.001593 | 0.001724 | 0.924038 | 0.355466 | 1548.0 | 179.0 | 140.0 | 801.0 | 0.51338 | 0.021609 |
| A_all | liu_product_tfidf_global_top5 | ext_any | spec_ai | -0.003397 | 0.003754 | -0.90473 | 0.365608 | 766.0 | 177.0 | 139.0 | 472.0 | 0.736729 | 0.053524 |
| A_all | full_semantic_reranked_top5 | ext_any | spec_ai | 0.001972 | 0.002181 | 0.903869 | 0.366065 | 796.0 | 183.0 | 143.0 | 470.0 | 0.580014 | 0.009435 |
| A_all | liu_product_tfidf_same_industry_d_top5 | current_text_history | spec_ai | 0.00263 | 0.003007 | 0.874777 | 0.381696 | 790.0 | 178.0 | 140.0 | 493.0 | 0.549471 | 0.022081 |

## T6 OUT/M/R/Layer x AIActive Cuts

| cut | term | coef | se | z | p | nobs | events | focal_firms | peer_firms | overall_r2 | within_r2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| OUT_1 | cut_x_ai | -0.013526 | 0.004436 | -3.048762 | 0.002298 | 1578.0 | 178.0 | 140.0 | 811.0 | 0.49453 | 0.012932 |
| M_ext | cut_x_ai | -0.002915 | 0.003699 | -0.787995 | 0.4307 | 1578.0 | 178.0 | 140.0 | 811.0 | 0.492607 | 0.009176 |
| L_compute | cut_x_ai | -0.003046 | 0.004109 | -0.741471 | 0.458408 | 1578.0 | 178.0 | 140.0 | 811.0 | 0.492639 | 0.00924 |
| L_model_app | cut_x_ai | 0.002042 | 0.004128 | 0.494709 | 0.620806 | 1578.0 | 178.0 | 140.0 | 811.0 | 0.49253 | 0.009026 |
| R_plus | cut_x_ai | 0.00071 | 0.0051 | 0.139284 | 0.889226 | 1578.0 | 178.0 | 140.0 | 811.0 | 0.492447 | 0.008863 |

## T7 Ex-Post Validation Readout

| event_type | events | cac_by_event_p365 | cac_post365_new | ai_patent_by_event_p365 | ai_patent_post365_new | genai_patent_by_event_p365 | genai_patent_post365_new | history_by_event_p365 | history_post365_new | post365_broad_ai_hiring | post365_genai_hiring |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 203.0 | 0.083744 | 0.049261 | 0.08867 | 0.004926 | 0.014778 | 0.004926 | 0.896552 | 0.08867 | 3.935961 | 1.857143 |
| D-fw | 142.0 | 0.06338 | 0.028169 | 0.035211 | 0.014085 | 0.0 | 0.0 | 0.950704 | 0.147887 | 2.84507 | 1.323944 |

## T8 Non-GenAI Investment Placebo

| sample_name | outcome_label | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|
| D_nonai_investment_placebo | AR[0] | -0.000216 | 0.000672 | 0.747526 | 4305.0 | 498.0 | 1693.0 | -0.000354 | 0.49036 |
| D_nonai_investment_placebo | CAR[0,+1] | -0.001989 | 0.000937 | 0.033684 | 4305.0 | 498.0 | 1693.0 | -0.002241 | 0.455981 |

## Output Files

- `results/v56_v55_expanded_llm_empirical_tables_20260612/expanded_coded_rows_enriched.csv`
- `results/v56_v55_expanded_llm_empirical_tables_20260612/expanded_event_samples.csv`
- `results/v56_v55_expanded_llm_empirical_tables_20260612/peer_link_panel.csv.gz`
- `results/v56_v55_expanded_llm_empirical_tables_20260612/analysis_panel_with_returns_ai.csv.gz`
- `results/v56_v55_expanded_llm_empirical_tables_20260612/t2_peer_main_effect.csv`
