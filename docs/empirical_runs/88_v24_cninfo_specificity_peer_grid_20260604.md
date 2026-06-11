# v24 CNINFO specificity x peer grid

## Purpose

This run tests combinations of GenAI-event definitions, product-market peer definitions, and event-level specificity measures on the CNINFO 1055 PDF event library.
The headline grid is `Specificity_z x AIActivePeer -> PeerCAR[0,+1]` with event fixed effects and peer-industry-week fixed effects.

## Event Definitions

| event_def | events | focal_firms | likely_events | possible_events | denial_events |
|---|---|---|---|---|---|
| E0_all_1055 | 1055.0 | 640.0 | 106.0 | 285.0 | 285.0 |
| E1_reviewable_no_denial | 742.0 | 517.0 | 106.0 | 285.0 | 0.0 |
| E2_likely_or_possible | 391.0 | 300.0 | 106.0 | 285.0 | 0.0 |
| E3_likely_only | 106.0 | 91.0 | 106.0 | 0.0 | 0.0 |
| E4_first_likely_or_possible | 300.0 | 300.0 | 87.0 | 213.0 | 0.0 |
| E5_first_reviewable_no_denial | 517.0 | 517.0 | 86.0 | 189.0 | 0.0 |

## Specificity Measures

| specificity | mean | sd | p05 | p50 | p95 | nonmissing |
|---|---|---|---|---|---|---|
| legacy_detail_density | 5.670549 | 5.271451 | 1.052632 | 4.394726 | 15.0 | 1055.0 |
| genai_concreteness_raw | 0.02762 | 0.028207 | 0.0 | 0.02439 | 0.083333 | 1055.0 |
| genai_concreteness_resid | 0.0 | 1.0 | -1.26863 | -0.146474 | 1.929795 | 1055.0 |
| machine_component_sum | 3.540284 | 2.360825 | 0.0 | 4.0 | 7.0 | 1055.0 |
| machine_specificity_score | 2.381991 | 1.427243 | 0.0 | 3.0 | 4.0 | 1055.0 |
| auto_action_score | 3.481232 | 0.924336 | 1.7 | 3.7 | 5.7 | 1055.0 |

## Best Strict Prior-Year Heterogeneity Results

| event_def | method_variant | specificity | ai_def | coef | se | p | q_bh_all | nobs | events | peer_firms |
|---|---|---|---|---|---|---|---|---|---|---|
| E3_likely_only | annual_report_global_top5 | auto_action_score | current_text_history | 0.020529 | 0.002981 | 0.0 | 0.0 | 366.0 | 87.0 | 261.0 |
| E3_likely_only | annual_report_global_ai_stripped_top5 | auto_action_score | current_text_history | 0.020142 | 0.003045 | 0.0 | 0.0 | 365.0 | 87.0 | 259.0 |
| E3_likely_only | liu_product_tfidf_same_industry_d_top5 | genai_concreteness_raw | current_text_history | -0.019451 | 0.004016 | 1e-06 | 0.000758 | 383.0 | 88.0 | 299.0 |
| E3_likely_only | liu_product_tfidf_same_industry_d_top10 | machine_component_sum | current_text_history | -0.009818 | 0.002567 | 0.000131 | 0.04219 | 763.0 | 88.0 | 536.0 |
| E4_first_likely_or_possible | liu_product_tfidf_global_top20 | auto_action_score | current_text_history | 0.00487 | 0.001307 | 0.000194 | 0.051283 | 4471.0 | 258.0 | 1924.0 |
| E3_likely_only | liu_product_tfidf_same_industry_d_top5 | machine_component_sum | current_text_history | -0.013272 | 0.003698 | 0.000331 | 0.072844 | 383.0 | 88.0 | 299.0 |
| E2_likely_or_possible | ren_wang_binary_global_top10 | legacy_detail_density | ext_any | -0.005841 | 0.001629 | 0.000337 | 0.072844 | 2951.0 | 338.0 | 1180.0 |
| E2_likely_or_possible | liu_product_tfidf_global_top5 | legacy_detail_density | ext_any | -0.009192 | 0.002602 | 0.000412 | 0.079928 | 1469.0 | 337.0 | 796.0 |
| E3_likely_only | liu_product_tfidf_same_industry_d_top5 | auto_action_score | current_text_history | 0.006479 | 0.001856 | 0.000483 | 0.079928 | 383.0 | 88.0 | 299.0 |
| E3_likely_only | liu_product_tfidf_global_top20 | auto_action_score | ext_any | 0.005036 | 0.001448 | 0.000505 | 0.079928 | 1500.0 | 88.0 | 894.0 |
| E3_likely_only | liu_product_tfidf_same_industry_d_top5 | machine_specificity_score | current_text_history | -0.010846 | 0.003489 | 0.00188 | 0.221289 | 383.0 | 88.0 | 299.0 |
| E3_likely_only | ren_wang_binary_global_top5 | genai_concreteness_resid | ext_any | 0.010664 | 0.003505 | 0.002344 | 0.221289 | 369.0 | 88.0 | 260.0 |
| E3_likely_only | liu_product_tfidf_global_top10 | auto_action_score | ext_any | 0.004673 | 0.001548 | 0.002534 | 0.221289 | 746.0 | 88.0 | 509.0 |
| E2_likely_or_possible | ren_wang_binary_global_top5 | auto_action_score | current_text_history | 0.008321 | 0.002765 | 0.002618 | 0.221289 | 1459.0 | 338.0 | 725.0 |
| E4_first_likely_or_possible | annual_report_global_top5 | auto_action_score | current_text_history | 0.008593 | 0.002871 | 0.002759 | 0.221289 | 1096.0 | 257.0 | 732.0 |
| E3_likely_only | liu_product_tfidf_same_industry_d_top10 | auto_action_score | current_text_history | 0.00393 | 0.001314 | 0.002772 | 0.221289 | 763.0 | 88.0 | 536.0 |
| E4_first_likely_or_possible | ren_wang_binary_global_top20 | machine_specificity_score | ext_any | 0.003683 | 0.001232 | 0.002789 | 0.221289 | 4498.0 | 258.0 | 1722.0 |
| E2_likely_or_possible | annual_report_global_top5 | auto_action_score | current_text_history | 0.00808 | 0.002706 | 0.002829 | 0.221289 | 1437.0 | 337.0 | 765.0 |
| E2_likely_or_possible | ren_wang_binary_global_top20 | machine_specificity_score | ext_any | 0.003038 | 0.001027 | 0.003106 | 0.221289 | 5896.0 | 338.0 | 1785.0 |
| E3_likely_only | ren_wang_binary_global_top5 | genai_concreteness_raw | ext_any | 0.012546 | 0.004251 | 0.003167 | 0.221289 | 369.0 | 88.0 | 260.0 |

## Current Verdict

- The peer lane has enough sample after switching to CNINFO events; the core issue is measurement choice, not coverage.
- The most interpretable strict prior-year signal is `legacy_detail_density × ext_any` under `E2_likely_or_possible` and `E4_first_likely_or_possible`: coefficients are mostly negative and appear across several product-peer variants.
- `auto_action_score × current_text_history` is often positive and significant, but it overlaps with event-screening rules and should stay diagnostic rather than become the paper's publishable specificity measure.
- `E3_likely_only` is too small for model selection: it produces very sharp results, but signs flip across specificity measures and peer systems.
- Event-level average-effect tables are not the main design because they cannot use event fixed effects and even placebo peer systems can become significant.

## Stability by Event Definition and X

| event_def | specificity | ai_def | tests | sig_05 | sig_10 | median_coef | positive_share | min_p | median_p |
|---|---|---|---|---|---|---|---|---|---|
| E4_first_likely_or_possible | auto_action_score | current_text_history | 18.0 | 7.0 | 10.0 | 0.003175 | 1.0 | 0.000194 | 0.062258 |
| E2_likely_or_possible | legacy_detail_density | ext_any | 18.0 | 7.0 | 7.0 | -0.002018 | 0.055556 | 0.000337 | 0.131551 |
| E2_likely_or_possible | auto_action_score | current_text_history | 18.0 | 5.0 | 8.0 | 0.00261 | 1.0 | 0.002618 | 0.113592 |
| E4_first_likely_or_possible | legacy_detail_density | ext_any | 18.0 | 5.0 | 8.0 | -0.002404 | 0.111111 | 0.006196 | 0.137343 |
| E5_first_reviewable_no_denial | auto_action_score | current_text_history | 18.0 | 5.0 | 8.0 | 0.001891 | 0.944444 | 0.00908 | 0.142169 |
| E3_likely_only | auto_action_score | current_text_history | 18.0 | 5.0 | 7.0 | 0.001394 | 0.777778 | 0.0 | 0.369256 |
| E3_likely_only | machine_component_sum | current_text_history | 18.0 | 4.0 | 4.0 | -0.003359 | 0.111111 | 0.000131 | 0.289591 |
| E1_reviewable_no_denial | legacy_detail_density | current_text_history | 18.0 | 4.0 | 4.0 | 0.001432 | 0.777778 | 0.016315 | 0.449751 |
| E3_likely_only | genai_concreteness_resid | ext_any | 18.0 | 3.0 | 6.0 | 0.003543 | 0.944444 | 0.002344 | 0.273737 |
| E3_likely_only | genai_concreteness_raw | current_text_history | 18.0 | 3.0 | 5.0 | -0.003891 | 0.166667 | 1e-06 | 0.208494 |
| E5_first_reviewable_no_denial | legacy_detail_density | ext_any | 18.0 | 3.0 | 5.0 | -0.001464 | 0.055556 | 0.019819 | 0.303459 |
| E3_likely_only | machine_specificity_score | current_text_history | 18.0 | 3.0 | 4.0 | -0.001551 | 0.222222 | 0.00188 | 0.518212 |
| E3_likely_only | auto_action_score | ext_any | 18.0 | 3.0 | 3.0 | 0.000783 | 0.777778 | 0.000505 | 0.444134 |
| E3_likely_only | genai_concreteness_raw | ext_any | 18.0 | 3.0 | 3.0 | 0.00131 | 0.611111 | 0.003167 | 0.472465 |
| E4_first_likely_or_possible | machine_specificity_score | ext_any | 18.0 | 2.0 | 5.0 | 0.001787 | 0.944444 | 0.002789 | 0.32514 |
| E4_first_likely_or_possible | machine_component_sum | ext_any | 18.0 | 2.0 | 4.0 | 0.001648 | 1.0 | 0.009752 | 0.358123 |
| E2_likely_or_possible | machine_component_sum | ext_any | 18.0 | 2.0 | 3.0 | 0.00143 | 1.0 | 0.011164 | 0.380513 |
| E1_reviewable_no_denial | auto_action_score | current_text_history | 18.0 | 2.0 | 3.0 | 0.00148 | 0.944444 | 0.011358 | 0.145345 |
| E3_likely_only | genai_concreteness_resid | current_text_history | 18.0 | 2.0 | 3.0 | -0.002394 | 0.166667 | 0.011765 | 0.414334 |
| E0_all_1055 | auto_action_score | current_text_history | 18.0 | 2.0 | 3.0 | 0.000531 | 0.833333 | 0.012681 | 0.572788 |
| E5_first_reviewable_no_denial | legacy_detail_density | current_text_history | 18.0 | 2.0 | 3.0 | 0.001637 | 0.722222 | 0.038484 | 0.316818 |
| E1_reviewable_no_denial | machine_component_sum | current_text_history | 18.0 | 2.0 | 2.0 | -0.000643 | 0.388889 | 0.026175 | 0.556581 |
| E0_all_1055 | legacy_detail_density | current_text_history | 18.0 | 1.0 | 4.0 | 0.001034 | 0.777778 | 0.044142 | 0.54072 |
| E2_likely_or_possible | machine_specificity_score | ext_any | 18.0 | 1.0 | 3.0 | 0.001659 | 1.0 | 0.003106 | 0.402485 |

## Event-Level Specificity Average Effect

| event_def | method_variant | specificity | coef | se | p | q_bh_all | nobs | events | peer_firms |
|---|---|---|---|---|---|---|---|---|---|
| E3_likely_only | csmar_scope_product_text_top10 | auto_action_score | 0.024471 | 0.00165 | 0.0 | 0.0 | 771.0 | 90.0 | 556.0 |
| E3_likely_only | csmar_scope_semantic_only_top10 | auto_action_score | 0.024515 | 0.001697 | 0.0 | 0.0 | 740.0 | 90.0 | 534.0 |
| E3_likely_only | csmar_scope_product_text_top5 | auto_action_score | 0.015418 | 0.001116 | 0.0 | 0.0 | 383.0 | 90.0 | 302.0 |
| E3_likely_only | full_semantic_reranked_top10 | genai_concreteness_raw | -0.023954 | 0.001795 | 0.0 | 0.0 | 759.0 | 90.0 | 531.0 |
| E3_likely_only | csmar_scope_semantic_only_top5 | auto_action_score | 0.02435 | 0.002134 | 0.0 | 0.0 | 386.0 | 90.0 | 289.0 |
| E3_likely_only | ren_wang_binary_global_top5 | auto_action_score | 0.026627 | 0.002538 | 0.0 | 0.0 | 369.0 | 88.0 | 260.0 |
| E3_likely_only | annual_report_global_top5 | auto_action_score | 0.019314 | 0.002193 | 0.0 | 0.0 | 366.0 | 87.0 | 261.0 |
| E3_likely_only | placebo_random_top5 | auto_action_score | 0.01915 | 0.002202 | 0.0 | 0.0 | 386.0 | 90.0 | 299.0 |
| E3_likely_only | ren_wang_binary_same_industry_d_top20 | genai_concreteness_raw | -0.022908 | 0.002657 | 0.0 | 0.0 | 1476.0 | 87.0 | 908.0 |
| E3_likely_only | liu_product_tfidf_same_industry_d_top20 | genai_concreteness_raw | -0.017309 | 0.002053 | 0.0 | 0.0 | 1498.0 | 88.0 | 935.0 |
| E3_likely_only | annual_report_same_industry_d_top10 | genai_concreteness_raw | -0.022974 | 0.002781 | 0.0 | 0.0 | 740.0 | 87.0 | 523.0 |
| E3_likely_only | placebo_low_similarity_top5 | auto_action_score | 0.017989 | 0.002196 | 0.0 | 0.0 | 380.0 | 90.0 | 297.0 |
| E3_likely_only | deepseek_flash_top5 | genai_concreteness_raw | -0.026288 | 0.003276 | 0.0 | 0.0 | 382.0 | 89.0 | 290.0 |
| E3_likely_only | annual_same_only_semantic_top5 | genai_concreteness_raw | -0.024797 | 0.00315 | 0.0 | 0.0 | 299.0 | 71.0 | 219.0 |
| E3_likely_only | annual_report_global_ai_stripped_top5 | auto_action_score | 0.018872 | 0.002466 | 0.0 | 0.0 | 365.0 | 87.0 | 259.0 |
| E3_likely_only | annual_only_semantic_top5 | genai_concreteness_raw | -0.024815 | 0.003302 | 0.0 | 0.0 | 301.0 | 71.0 | 223.0 |
| E3_likely_only | placebo_random_top5 | machine_specificity_score | -0.014249 | 0.001976 | 0.0 | 0.0 | 386.0 | 90.0 | 299.0 |
| E3_likely_only | annual_same_only_semantic_top10 | genai_concreteness_raw | -0.023725 | 0.003306 | 0.0 | 0.0 | 596.0 | 71.0 | 397.0 |
| E3_likely_only | full_semantic_reranked_top5 | genai_concreteness_raw | -0.023309 | 0.003271 | 0.0 | 0.0 | 380.0 | 90.0 | 292.0 |
| E3_likely_only | annual_only_semantic_top10 | genai_concreteness_raw | -0.021433 | 0.003121 | 0.0 | 0.0 | 601.0 | 71.0 | 397.0 |

## Reading

- Treat this as a specification audit, not a final model-selection exercise.
- A usable T05 main effect should survive across event definitions and peer definitions, not merely appear in one high-dimensional combination.
- `auto_action_score` is diagnostic because it partly overlaps with event screening; it should not be the publishable specificity X.
- Static LLM/semantic peer networks remain diagnostics unless rebuilt as rolling/as-of peer sets.

## Output Files

- `results/v24_cninfo_specificity_peer_grid_20260604/event_specificity_measures.csv`
- `results/v24_cninfo_specificity_peer_grid_20260604/grid_sample_summary.csv`
- `results/v24_cninfo_specificity_peer_grid_20260604/grid_heterogeneity_regressions.csv`
- `results/v24_cninfo_specificity_peer_grid_20260604/grid_average_regressions.csv`
- `results/v24_cninfo_specificity_peer_grid_20260604/grid_stability_by_x.csv`
