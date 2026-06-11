# v23 CNINFO 1055 peer event-study smoke test

## Purpose

This run attaches market-model abnormal returns to the CNINFO 1055 GenAI disclosure peer-link panel. It is an average peer AR/CAR smoke test, not the original T05 specificity-by-AIActive regression.

## Design

- Peer-link input: `results/v23_cninfo_1055_peer_coverage_20260603/peer_link_panel.csv.gz`.
- Stock-return model cache: `results/v6_supplement_market_model_placebo_20260524/stock_returns_with_market_model_params.csv` (2021-05-24 to 2026-05-22).
- Event date is moved forward to the next available trading date.
- Analysis rows require complete clean peer trading for [-1,0,+1]: valid market-model abnormal returns, normal trading, and no limit-hit flag in the existing cache.
- Standard errors are two-way clustered by event and peer firm.

## Sample Flow, All 1055

| method_variant | linked_events | linked_peer_firms | complete_clean_rows | complete_clean_events | complete_clean_peer_firms |
|---|---|---|---|---|---|
| ren_wang_binary_global_top20 | 870.0 | 2816.0 | 15090.0 | 861.0 | 2483.0 |
| annual_report_global_ai_stripped_top10 | 870.0 | 2111.0 | 7494.0 | 860.0 | 1895.0 |
| annual_report_global_top10 | 870.0 | 2110.0 | 7516.0 | 860.0 | 1894.0 |
| liu_product_tfidf_global_top20 | 870.0 | 3013.0 | 15030.0 | 859.0 | 2648.0 |
| liu_product_tfidf_same_industry_d_top10 | 870.0 | 2197.0 | 7629.0 | 859.0 | 1989.0 |
| liu_product_tfidf_same_industry_d_top20 | 870.0 | 3016.0 | 14988.0 | 859.0 | 2700.0 |
| ren_wang_binary_global_top10 | 870.0 | 2033.0 | 7565.0 | 859.0 | 1824.0 |
| annual_report_global_ai_stripped_top5 | 870.0 | 1432.0 | 3751.0 | 858.0 | 1288.0 |
| annual_report_global_top5 | 870.0 | 1432.0 | 3755.0 | 858.0 | 1291.0 |
| annual_report_same_industry_d_top10 | 870.0 | 2202.0 | 7606.0 | 858.0 | 1991.0 |
| annual_report_same_industry_d_top5 | 870.0 | 1495.0 | 3813.0 | 858.0 | 1343.0 |
| liu_product_tfidf_global_top10 | 870.0 | 2173.0 | 7557.0 | 858.0 | 1934.0 |

## Strict Prior-Year Networks: CAR[0,+1]

| method_variant | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|
| ren_wang_binary_same_industry_d_top20 | -0.003061 | 0.000834 | 0.00024 | 14962.0 | 858.0 | 2714.0 | -0.003813 | 0.443123 |
| liu_product_tfidf_same_industry_d_top20 | -0.003046 | 0.000834 | 0.000261 | 14988.0 | 859.0 | 2700.0 | -0.003964 | 0.441086 |
| ren_wang_binary_global_top20 | -0.00266 | 0.000781 | 0.000661 | 15090.0 | 861.0 | 2483.0 | -0.003504 | 0.445659 |
| liu_product_tfidf_same_industry_d_top10 | -0.003133 | 0.000928 | 0.00074 | 7629.0 | 859.0 | 1989.0 | -0.003933 | 0.440949 |
| annual_report_global_top10 | -0.002832 | 0.000868 | 0.001106 | 7516.0 | 860.0 | 1894.0 | -0.003567 | 0.442789 |
| annual_report_same_industry_d_top10 | -0.002939 | 0.00091 | 0.001242 | 7606.0 | 858.0 | 1991.0 | -0.003853 | 0.441888 |
| ren_wang_binary_same_industry_d_top10 | -0.00292 | 0.000907 | 0.001288 | 7597.0 | 858.0 | 1982.0 | -0.003602 | 0.446887 |
| annual_report_global_ai_stripped_top10 | -0.002739 | 0.000865 | 0.001545 | 7494.0 | 860.0 | 1895.0 | -0.003393 | 0.445556 |
| liu_product_tfidf_global_top20 | -0.002478 | 0.000798 | 0.001894 | 15030.0 | 859.0 | 2648.0 | -0.003408 | 0.449235 |
| ren_wang_binary_global_top10 | -0.002472 | 0.000853 | 0.003756 | 7565.0 | 859.0 | 1824.0 | -0.003285 | 0.450231 |
| liu_product_tfidf_global_top10 | -0.002322 | 0.000881 | 0.00841 | 7557.0 | 858.0 | 1934.0 | -0.003534 | 0.448723 |
| annual_report_same_industry_d_top5 | -0.00258 | 0.001012 | 0.010772 | 3813.0 | 858.0 | 1343.0 | -0.003354 | 0.450564 |

## Strict Prior-Year Networks: AR[0]

| method_variant | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|
| annual_report_same_industry_d_top10 | -0.001798 | 0.000622 | 0.003859 | 7606.0 | 858.0 | 1991.0 | -0.002467 | 0.450697 |
| ren_wang_binary_global_top20 | -0.001549 | 0.000547 | 0.004606 | 15090.0 | 861.0 | 2483.0 | -0.002331 | 0.450696 |
| annual_report_global_top10 | -0.00163 | 0.000606 | 0.007155 | 7516.0 | 860.0 | 1894.0 | -0.001997 | 0.459021 |
| ren_wang_binary_same_industry_d_top20 | -0.001522 | 0.000583 | 0.008997 | 14962.0 | 858.0 | 2714.0 | -0.002402 | 0.451009 |
| annual_report_global_ai_stripped_top10 | -0.001539 | 0.000601 | 0.010469 | 7494.0 | 860.0 | 1895.0 | -0.001864 | 0.459034 |
| ren_wang_binary_same_industry_d_top10 | -0.001523 | 0.000625 | 0.014782 | 7597.0 | 858.0 | 1982.0 | -0.002553 | 0.447282 |
| liu_product_tfidf_same_industry_d_top20 | -0.001275 | 0.000572 | 0.025817 | 14988.0 | 859.0 | 2700.0 | -0.002172 | 0.457433 |
| liu_product_tfidf_same_industry_d_top10 | -0.001336 | 0.000628 | 0.033483 | 7629.0 | 859.0 | 1989.0 | -0.002253 | 0.457989 |
| ren_wang_binary_same_industry_d_top5 | -0.001515 | 0.000713 | 0.033673 | 3808.0 | 858.0 | 1333.0 | -0.002499 | 0.449317 |
| annual_report_global_ai_stripped_top5 | -0.001311 | 0.000654 | 0.045046 | 3751.0 | 858.0 | 1288.0 | -0.001784 | 0.460144 |
| ren_wang_binary_global_top10 | -0.001168 | 0.000595 | 0.049781 | 7565.0 | 859.0 | 1824.0 | -0.002028 | 0.458956 |
| liu_product_tfidf_global_top20 | -0.001046 | 0.000552 | 0.057766 | 15030.0 | 859.0 | 2648.0 | -0.001831 | 0.462009 |

## Static/LLM Diagnostic Networks: CAR[0,+1]

| method_variant | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|
| csmar_scope_semantic_only_top5 | -0.003365 | 0.000914 | 0.000231 | 3789.0 | 872.0 | 1393.0 | -0.003989 | 0.441805 |
| csmar_scope_product_text_top10 | -0.002917 | 0.000808 | 0.000304 | 7606.0 | 872.0 | 2213.0 | -0.00403 | 0.440442 |
| placebo_low_similarity_top5 | -0.003404 | 0.000944 | 0.000311 | 3720.0 | 872.0 | 1423.0 | -0.004579 | 0.430914 |
| csmar_scope_semantic_only_top10 | -0.002978 | 0.000828 | 0.000322 | 7146.0 | 872.0 | 2131.0 | -0.004119 | 0.439547 |
| full_semantic_reranked_top10 | -0.002958 | 0.000844 | 0.000457 | 7589.0 | 871.0 | 2096.0 | -0.003624 | 0.44525 |
| placebo_random_top5 | -0.003103 | 0.000904 | 0.000598 | 3696.0 | 872.0 | 1413.0 | -0.003888 | 0.435606 |
| deepseek_open_ended_top5 | -0.003421 | 0.001042 | 0.001028 | 3518.0 | 849.0 | 835.0 | -0.004181 | 0.432064 |
| csmar_scope_product_text_top5 | -0.002886 | 0.000923 | 0.00176 | 3821.0 | 872.0 | 1425.0 | -0.004109 | 0.442293 |
| full_semantic_reranked_top5 | -0.002723 | 0.00095 | 0.004149 | 3828.0 | 871.0 | 1333.0 | -0.003231 | 0.449321 |
| annual_only_semantic_top10 | -0.002838 | 0.001019 | 0.005364 | 5880.0 | 666.0 | 1394.0 | -0.003537 | 0.446939 |
| deepseek_open_ended_same_industry_top5 | -0.003161 | 0.001221 | 0.009614 | 2477.0 | 739.0 | 635.0 | -0.004259 | 0.433589 |
| annual_same_only_semantic_top10 | -0.002689 | 0.001043 | 0.009927 | 5830.0 | 666.0 | 1376.0 | -0.003549 | 0.448199 |

## Likely-Qian Subset: Strict Prior-Year CAR[0,+1]

| method_variant | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|
| liu_product_tfidf_same_industry_d_top20 | -0.005374 | 0.002249 | 0.016871 | 1498.0 | 88.0 | 935.0 | -0.006063 | 0.399199 |
| ren_wang_binary_global_top5 | -0.005611 | 0.002546 | 0.027497 | 369.0 | 88.0 | 260.0 | -0.0062 | 0.392954 |
| ren_wang_binary_global_top10 | -0.004924 | 0.002349 | 0.036075 | 753.0 | 88.0 | 482.0 | -0.005527 | 0.413015 |
| ren_wang_binary_global_top20 | -0.004623 | 0.002234 | 0.038501 | 1499.0 | 88.0 | 835.0 | -0.005699 | 0.408939 |
| liu_product_tfidf_same_industry_d_top10 | -0.004978 | 0.002462 | 0.04322 | 763.0 | 88.0 | 536.0 | -0.006683 | 0.401048 |
| liu_product_tfidf_global_top20 | -0.003884 | 0.002126 | 0.067661 | 1501.0 | 88.0 | 895.0 | -0.005455 | 0.418388 |
| ren_wang_binary_same_industry_d_top20 | -0.004018 | 0.002441 | 0.099722 | 1476.0 | 87.0 | 908.0 | -0.005532 | 0.413957 |
| annual_report_same_industry_d_top10 | -0.004082 | 0.002713 | 0.13244 | 740.0 | 87.0 | 523.0 | -0.005757 | 0.416216 |
| ren_wang_binary_same_industry_d_top10 | -0.003744 | 0.002525 | 0.13805 | 740.0 | 87.0 | 522.0 | -0.005647 | 0.410811 |
| annual_report_global_top10 | -0.003489 | 0.00239 | 0.144334 | 732.0 | 88.0 | 485.0 | -0.003696 | 0.428962 |
| annual_report_global_top5 | -0.003762 | 0.002644 | 0.154727 | 366.0 | 87.0 | 261.0 | -0.003257 | 0.42623 |
| annual_report_global_ai_stripped_top10 | -0.003532 | 0.002488 | 0.155805 | 732.0 | 88.0 | 482.0 | -0.004437 | 0.427596 |

## Reading

- This is useful for deciding whether the peer lane has enough observations after replacing the old event library with CNINFO full-text events.
- The headline T05 question still needs event-level disclosure specificity coding; these mean CAR tables only answer whether peers move on average around the event.
- Static LLM/semantic networks should be rebuilt as rolling/as-of peers before being used as a final causal design.

## Output Files

- `results/v23_cninfo_1055_peer_event_study_20260603/peer_event_study_summary.csv`
- `results/v23_cninfo_1055_peer_event_study_20260603/peer_event_study_summary_by_label.csv`
- `results/v23_cninfo_1055_peer_event_study_20260603/peer_event_study_sample_flow.csv`
- `results/v23_cninfo_1055_peer_event_study_20260603/peer_event_study_panel_light.csv.gz`
