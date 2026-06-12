# v72 Registry H2 Pooled Interaction

## Purpose

- Tests the v3 design's H2 main claim: later-verified GenAI disclosures vs never-verified disclosures.
- Uses firm-level administrative timing as the main label and product-level strict matches only as audit columns.
- Preferred peer method: `liu_product_tfidf_same_industry_d_top10`.
- FE: event + peer industry-week. SE: two-way clustered by event and peer firm.
- Subgroups: all, model/app only, own only, own model/app, and out=1 model/app.

## Outputs

- `results/v72_registry_h2_pooled_interaction_20260612/analysis_panel_with_registry_labels.csv.gz`
- `results/v72_registry_h2_pooled_interaction_20260612/registry_h2_cell_counts.csv`
- `results/v72_registry_h2_pooled_interaction_20260612/registry_h2_grouped_means.csv`
- `results/v72_registry_h2_pooled_interaction_20260612/registry_h2_pooled_interactions.csv`
- `results/v72_registry_h2_pooled_interaction_20260612/registry_h2_product_audit_means.csv`
- `results/v72_registry_h2_pooled_interaction_20260612/v72_registry_h2_pooled_interaction_20260612.xlsx`

## Cell Counts

| subgroup | sample_name | event_type | verification_timing | events | focal_firms | product_level_matched_events | recent_censored_events |
|---|---|---|---|---|---|---|---|
| all | A_Dfw_stack | A | later_verified | 27.0 | 24.0 | 8.0 | 1.0 |
| all | A_Dfw_stack | A | never_verified | 125.0 | 99.0 | 0.0 | 0.0 |
| all | A_Dfw_stack | A | unmatched_ambiguous | 15.0 | 14.0 | 0.0 | 15.0 |
| all | A_Dfw_stack | A | verified_at_event | 11.0 | 9.0 | 2.0 | 2.0 |
| all | A_Dfw_stack | D-fw | later_verified | 19.0 | 17.0 | 1.0 | 1.0 |
| all | A_Dfw_stack | D-fw | never_verified | 85.0 | 71.0 | 0.0 | 0.0 |
| all | A_Dfw_stack | D-fw | unmatched_ambiguous | 19.0 | 19.0 | 0.0 | 19.0 |
| all | A_Dfw_stack | D-fw | verified_at_event | 6.0 | 6.0 | 0.0 | 3.0 |
| all | A_all | A | later_verified | 27.0 | 24.0 | 8.0 | 1.0 |
| all | A_all | A | never_verified | 125.0 | 99.0 | 0.0 | 0.0 |
| all | A_all | A | unmatched_ambiguous | 15.0 | 14.0 | 0.0 | 15.0 |
| all | A_all | A | verified_at_event | 11.0 | 9.0 | 2.0 | 2.0 |
| all | A_first_firm | A | later_verified | 24.0 | 24.0 | 6.0 | 1.0 |
| all | A_first_firm | A | never_verified | 98.0 | 98.0 | 0.0 | 0.0 |
| all | A_first_firm | A | unmatched_ambiguous | 9.0 | 9.0 | 0.0 | 9.0 |
| all | A_first_firm | A | verified_at_event | 7.0 | 7.0 | 1.0 | 2.0 |
| model_app | A_Dfw_stack | A | later_verified | 23.0 | 21.0 | 8.0 | 1.0 |
| model_app | A_Dfw_stack | A | never_verified | 67.0 | 61.0 | 0.0 | 0.0 |
| model_app | A_Dfw_stack | A | unmatched_ambiguous | 12.0 | 11.0 | 0.0 | 12.0 |
| model_app | A_Dfw_stack | A | verified_at_event | 6.0 | 6.0 | 2.0 | 2.0 |
| model_app | A_Dfw_stack | D-fw | later_verified | 13.0 | 13.0 | 1.0 | 1.0 |
| model_app | A_Dfw_stack | D-fw | never_verified | 56.0 | 50.0 | 0.0 | 0.0 |
| model_app | A_Dfw_stack | D-fw | unmatched_ambiguous | 18.0 | 18.0 | 0.0 | 18.0 |
| model_app | A_Dfw_stack | D-fw | verified_at_event | 3.0 | 3.0 | 0.0 | 2.0 |
| model_app | A_all | A | later_verified | 23.0 | 21.0 | 8.0 | 1.0 |
| model_app | A_all | A | never_verified | 67.0 | 61.0 | 0.0 | 0.0 |
| model_app | A_all | A | unmatched_ambiguous | 12.0 | 11.0 | 0.0 | 12.0 |
| model_app | A_all | A | verified_at_event | 6.0 | 6.0 | 2.0 | 2.0 |
| model_app | A_first_firm | A | later_verified | 20.0 | 20.0 | 6.0 | 1.0 |
| model_app | A_first_firm | A | never_verified | 57.0 | 57.0 | 0.0 | 0.0 |
| model_app | A_first_firm | A | unmatched_ambiguous | 7.0 | 7.0 | 0.0 | 7.0 |
| model_app | A_first_firm | A | verified_at_event | 4.0 | 4.0 | 1.0 | 2.0 |
| own | A_Dfw_stack | A | later_verified | 26.0 | 24.0 | 7.0 | 1.0 |
| own | A_Dfw_stack | A | never_verified | 85.0 | 69.0 | 0.0 | 0.0 |
| own | A_Dfw_stack | A | unmatched_ambiguous | 5.0 | 5.0 | 0.0 | 5.0 |
| own | A_Dfw_stack | A | verified_at_event | 6.0 | 5.0 | 2.0 | 0.0 |
| own | A_Dfw_stack | D-fw | never_verified | 1.0 | 1.0 | 0.0 | 0.0 |
| own | A_all | A | later_verified | 26.0 | 24.0 | 7.0 | 1.0 |
| own | A_all | A | never_verified | 85.0 | 69.0 | 0.0 | 0.0 |
| own | A_all | A | unmatched_ambiguous | 5.0 | 5.0 | 0.0 | 5.0 |
| own | A_all | A | verified_at_event | 6.0 | 5.0 | 2.0 | 0.0 |
| own | A_first_firm | A | later_verified | 24.0 | 24.0 | 6.0 | 1.0 |
| own | A_first_firm | A | never_verified | 66.0 | 66.0 | 0.0 | 0.0 |
| own | A_first_firm | A | unmatched_ambiguous | 3.0 | 3.0 | 0.0 | 3.0 |
| own | A_first_firm | A | verified_at_event | 4.0 | 4.0 | 1.0 | 0.0 |
| own_model_app | A_Dfw_stack | A | later_verified | 22.0 | 21.0 | 7.0 | 1.0 |
| own_model_app | A_Dfw_stack | A | never_verified | 45.0 | 40.0 | 0.0 | 0.0 |
| own_model_app | A_Dfw_stack | A | unmatched_ambiguous | 4.0 | 4.0 | 0.0 | 4.0 |
| own_model_app | A_Dfw_stack | A | verified_at_event | 2.0 | 2.0 | 2.0 | 0.0 |
| own_model_app | A_Dfw_stack | D-fw | never_verified | 1.0 | 1.0 | 0.0 | 0.0 |
| own_model_app | A_all | A | later_verified | 22.0 | 21.0 | 7.0 | 1.0 |
| own_model_app | A_all | A | never_verified | 45.0 | 40.0 | 0.0 | 0.0 |
| own_model_app | A_all | A | unmatched_ambiguous | 4.0 | 4.0 | 0.0 | 4.0 |
| own_model_app | A_all | A | verified_at_event | 2.0 | 2.0 | 2.0 | 0.0 |
| own_model_app | A_first_firm | A | later_verified | 20.0 | 20.0 | 6.0 | 1.0 |
| own_model_app | A_first_firm | A | never_verified | 40.0 | 40.0 | 0.0 | 0.0 |
| own_model_app | A_first_firm | A | unmatched_ambiguous | 3.0 | 3.0 | 0.0 | 3.0 |
| own_model_app | A_first_firm | A | verified_at_event | 1.0 | 1.0 | 1.0 | 0.0 |
| out1_model_app | A_Dfw_stack | A | later_verified | 21.0 | 19.0 | 8.0 | 1.0 |
| out1_model_app | A_Dfw_stack | A | never_verified | 50.0 | 46.0 | 0.0 | 0.0 |
| out1_model_app | A_Dfw_stack | A | unmatched_ambiguous | 8.0 | 8.0 | 0.0 | 8.0 |
| out1_model_app | A_Dfw_stack | A | verified_at_event | 6.0 | 6.0 | 2.0 | 2.0 |
| out1_model_app | A_Dfw_stack | D-fw | never_verified | 1.0 | 1.0 | 0.0 | 0.0 |
| out1_model_app | A_all | A | later_verified | 21.0 | 19.0 | 8.0 | 1.0 |
| out1_model_app | A_all | A | never_verified | 50.0 | 46.0 | 0.0 | 0.0 |
| out1_model_app | A_all | A | unmatched_ambiguous | 8.0 | 8.0 | 0.0 | 8.0 |
| out1_model_app | A_all | A | verified_at_event | 6.0 | 6.0 | 2.0 | 2.0 |
| out1_model_app | A_first_firm | A | later_verified | 18.0 | 18.0 | 6.0 | 1.0 |
| out1_model_app | A_first_firm | A | never_verified | 40.0 | 40.0 | 0.0 | 0.0 |
| out1_model_app | A_first_firm | A | unmatched_ambiguous | 6.0 | 6.0 | 0.0 | 6.0 |
| out1_model_app | A_first_firm | A | verified_at_event | 4.0 | 4.0 | 1.0 | 2.0 |

## CAR[0,+1] Group Means

| sample_name | subgroup | verification_timing | estimate | se | p | nobs | events | peer_firms | median | positive_share | product_level_matched_events |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A_all | all | later_verified | -0.003884 | 0.005077 | 0.444304 | 233.0 | 27.0 | 170.0 | -0.002047 | 0.446352 | 8.0 |
| A_all | model_app | later_verified | -0.004489 | 0.005533 | 0.417159 | 196.0 | 23.0 | 155.0 | -0.00191 | 0.454082 | 8.0 |
| A_all | own | later_verified | -0.003303 | 0.005251 | 0.529385 | 224.0 | 26.0 | 170.0 | -0.001453 | 0.459821 | 7.0 |
| A_all | own_model_app | later_verified | -0.003822 | 0.005762 | 0.507103 | 187.0 | 22.0 | 155.0 | -0.001319 | 0.470588 | 7.0 |
| A_all | out1_model_app | later_verified | -0.005264 | 0.005911 | 0.3732 | 182.0 | 21.0 | 142.0 | -0.003096 | 0.434066 | 8.0 |
| A_all | all | never_verified | -0.00684 | 0.002763 | 0.013306 | 1118.0 | 125.0 | 651.0 | -0.005428 | 0.421288 | 0.0 |
| A_all | model_app | never_verified | -0.003443 | 0.003494 | 0.324393 | 609.0 | 67.0 | 438.0 | -0.003062 | 0.449918 | 0.0 |
| A_all | own | never_verified | -0.00797 | 0.003442 | 0.020588 | 761.0 | 85.0 | 463.0 | -0.006729 | 0.407359 | 0.0 |
| A_all | own_model_app | never_verified | -0.006282 | 0.004552 | 0.167553 | 411.0 | 45.0 | 290.0 | -0.004759 | 0.416058 | 0.0 |
| A_all | out1_model_app | never_verified | -0.002329 | 0.0039 | 0.550374 | 455.0 | 50.0 | 320.0 | -0.003673 | 0.446154 | 0.0 |
| A_all | all | verified_at_event | 0.003697 | 0.006372 | 0.561786 | 93.0 | 11.0 | 77.0 | 0.000663 | 0.537634 | 2.0 |
| A_all | model_app | verified_at_event | 0.0084 | 0.011318 | 0.457958 | 48.0 | 6.0 | 48.0 | 0.001806 | 0.5625 | 2.0 |
| A_all | own | verified_at_event | 0.002396 | 0.004082 | 0.557319 | 51.0 | 6.0 | 43.0 | 0.003062 | 0.568627 | 2.0 |
| A_all | own_model_app | verified_at_event | 0.00992 | 0.005134 | 0.053303 | 15.0 | 2.0 | 15.0 | 0.009019 | 0.666667 | 2.0 |
| A_all | out1_model_app | verified_at_event | 0.0084 | 0.011318 | 0.457958 | 48.0 | 6.0 | 48.0 | 0.001806 | 0.5625 | 2.0 |
| A_first_firm | all | later_verified | -0.001612 | 0.005406 | 0.76561 | 205.0 | 24.0 | 168.0 | -0.000962 | 0.478049 | 6.0 |
| A_first_firm | model_app | later_verified | -0.001817 | 0.006038 | 0.763469 | 168.0 | 20.0 | 144.0 | -0.000373 | 0.494048 | 6.0 |
| A_first_firm | own | later_verified | -0.001612 | 0.005406 | 0.76561 | 205.0 | 24.0 | 168.0 | -0.000962 | 0.478049 | 6.0 |
| A_first_firm | own_model_app | later_verified | -0.001817 | 0.006038 | 0.763469 | 168.0 | 20.0 | 144.0 | -0.000373 | 0.494048 | 6.0 |
| A_first_firm | out1_model_app | later_verified | -0.002489 | 0.006552 | 0.703955 | 154.0 | 18.0 | 131.0 | -0.001306 | 0.474026 | 6.0 |
| A_first_firm | all | never_verified | -0.007357 | 0.003193 | 0.021238 | 872.0 | 98.0 | 635.0 | -0.004836 | 0.422018 | 0.0 |
| A_first_firm | model_app | never_verified | -0.004929 | 0.003899 | 0.206179 | 516.0 | 57.0 | 408.0 | -0.002848 | 0.445736 | 0.0 |
| A_first_firm | own | never_verified | -0.007772 | 0.004028 | 0.053663 | 589.0 | 66.0 | 445.0 | -0.005692 | 0.409168 | 0.0 |
| A_first_firm | own_model_app | never_verified | -0.007571 | 0.005025 | 0.13187 | 365.0 | 40.0 | 287.0 | -0.004489 | 0.410959 | 0.0 |
| A_first_firm | out1_model_app | never_verified | -0.004161 | 0.00451 | 0.356215 | 362.0 | 40.0 | 279.0 | -0.003262 | 0.439227 | 0.0 |
| A_first_firm | all | verified_at_event | -0.001146 | 0.004473 | 0.797771 | 57.0 | 7.0 | 55.0 | 0.000414 | 0.526316 | 1.0 |
| A_first_firm | model_app | verified_at_event | -0.005135 | 0.006691 | 0.44286 | 30.0 | 4.0 | 30.0 | -0.003601 | 0.433333 | 1.0 |
| A_first_firm | own | verified_at_event | 0.006253 | 0.00461 | 0.175008 | 34.0 | 4.0 | 34.0 | 0.008972 | 0.676471 | 1.0 |
| A_first_firm | own_model_app | verified_at_event | 0.017699 | 0.010913 | 0.104831 | 7.0 | 1.0 | 7.0 | 0.025727 | 0.857143 | 1.0 |
| A_first_firm | out1_model_app | verified_at_event | -0.005135 | 0.006691 | 0.44286 | 30.0 | 4.0 | 30.0 | -0.003601 | 0.433333 | 1.0 |

## CAR[0,+1] Pooled Interaction

| sample_name | subgroup | with_pre_controls | sim_later_coef | sim_later_se | sim_later_p | sim_never_coef | sim_never_se | sim_never_p | later_minus_never_coef | later_minus_never_se | later_minus_never_p | nobs | events | peer_firms | within_r2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A_first_firm | all | 0.0 | 0.081994 | 0.071169 | 0.24928 | 0.019406 | 0.029227 | 0.506709 | 0.062588 | 0.077406 | 0.418766 | 1077.0 | 122.0 | 709.0 | 0.002227 |
| A_first_firm | all | 1.0 | 0.092256 | 0.069193 | 0.182432 | 0.018716 | 0.029136 | 0.520641 | 0.07354 | 0.075798 | 0.331939 | 1077.0 | 122.0 | 709.0 | 0.01221 |
| A_first_firm | model_app | 0.0 | 0.079189 | 0.073372 | 0.280458 | 0.049605 | 0.030923 | 0.108676 | 0.029584 | 0.081302 | 0.715947 | 684.0 | 77.0 | 501.0 | 0.005211 |
| A_first_firm | model_app | 1.0 | 0.086194 | 0.069361 | 0.213983 | 0.047724 | 0.032126 | 0.137399 | 0.03847 | 0.077538 | 0.619795 | 684.0 | 77.0 | 501.0 | 0.008079 |
| A_first_firm | own | 0.0 | 0.081994 | 0.071169 | 0.24928 | 0.002233 | 0.044264 | 0.959769 | 0.079761 | 0.084495 | 0.345183 | 794.0 | 90.0 | 533.0 | 0.002137 |
| A_first_firm | own | 1.0 | 0.092331 | 0.068803 | 0.179609 | 0.002702 | 0.043614 | 0.950604 | 0.089629 | 0.082697 | 0.278443 | 794.0 | 90.0 | 533.0 | 0.012454 |
| A_first_firm | own_model_app | 0.0 | 0.079189 | 0.073372 | 0.280458 | 0.053036 | 0.046341 | 0.252431 | 0.026154 | 0.089306 | 0.769631 | 533.0 | 60.0 | 390.0 | 0.004896 |
| A_first_firm | own_model_app | 1.0 | 0.08532 | 0.068248 | 0.211246 | 0.052031 | 0.047276 | 0.27108 | 0.033289 | 0.085923 | 0.698436 | 533.0 | 60.0 | 390.0 | 0.00701 |
| A_first_firm | out1_model_app | 0.0 | 0.093329 | 0.121876 | 0.443814 | 0.040635 | 0.033141 | 0.220153 | 0.052694 | 0.126859 | 0.677865 | 516.0 | 58.0 | 372.0 | 0.004159 |
| A_first_firm | out1_model_app | 1.0 | 0.104224 | 0.115277 | 0.365934 | 0.039194 | 0.034896 | 0.261364 | 0.06503 | 0.119865 | 0.587455 | 516.0 | 58.0 | 372.0 | 0.008848 |
| A_all | all | 0.0 | 0.080558 | 0.068686 | 0.240856 | 0.010682 | 0.023417 | 0.648272 | 0.069876 | 0.073094 | 0.339084 | 1351.0 | 152.0 | 726.0 | 0.001553 |
| A_all | all | 1.0 | 0.090399 | 0.067799 | 0.182422 | 0.010948 | 0.023349 | 0.639135 | 0.079451 | 0.072254 | 0.271506 | 1351.0 | 152.0 | 726.0 | 0.011084 |
| A_all | model_app | 0.0 | 0.077789 | 0.070307 | 0.268542 | 0.027368 | 0.028568 | 0.33807 | 0.050421 | 0.077493 | 0.515266 | 805.0 | 90.0 | 534.0 | 0.003219 |
| A_all | model_app | 1.0 | 0.080255 | 0.067252 | 0.232734 | 0.026919 | 0.029035 | 0.353864 | 0.053336 | 0.07408 | 0.471537 | 805.0 | 90.0 | 534.0 | 0.003652 |
| A_all | own | 0.0 | 0.088366 | 0.069534 | 0.20379 | 0.00779 | 0.037547 | 0.835646 | 0.080576 | 0.079767 | 0.312428 | 985.0 | 111.0 | 552.0 | 0.002076 |
| A_all | own | 1.0 | 0.100461 | 0.068664 | 0.143445 | 0.007513 | 0.036924 | 0.838768 | 0.092948 | 0.078736 | 0.237804 | 985.0 | 111.0 | 552.0 | 0.015196 |
| A_all | own_model_app | 0.0 | 0.086288 | 0.07118 | 0.22542 | 0.061058 | 0.046008 | 0.184473 | 0.02523 | 0.087465 | 0.772999 | 598.0 | 67.0 | 398.0 | 0.005787 |
| A_all | own_model_app | 1.0 | 0.089975 | 0.067266 | 0.181029 | 0.060936 | 0.046999 | 0.19479 | 0.029039 | 0.084423 | 0.730863 | 598.0 | 67.0 | 398.0 | 0.006645 |
| A_all | out1_model_app | 0.0 | 0.089648 | 0.112116 | 0.42394 | 0.01432 | 0.030437 | 0.638018 | 0.075328 | 0.116976 | 0.519598 | 637.0 | 71.0 | 413.0 | 0.002507 |
| A_all | out1_model_app | 1.0 | 0.091735 | 0.107561 | 0.393734 | 0.014612 | 0.030981 | 0.637179 | 0.077123 | 0.111542 | 0.489299 | 637.0 | 71.0 | 413.0 | 0.00355 |

## Product-Level Audit Means

| sample_name | subgroup | product_match_group | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|---|
| A_all | all | not_product_matched | -0.005813 | 0.002489 | 0.01952 | 1360.0 | 153.0 | 717.0 | -0.004233 | 0.433824 |
| A_all | model_app | not_product_matched | -0.002953 | 0.003189 | 0.354334 | 769.0 | 86.0 | 513.0 | -0.002591 | 0.461638 |
| A_all | own | not_product_matched | -0.006811 | 0.003001 | 0.023235 | 961.0 | 108.0 | 529.0 | -0.0046 | 0.424558 |
| A_all | own_model_app | not_product_matched | -0.005596 | 0.00399 | 0.1607 | 538.0 | 60.0 | 360.0 | -0.003962 | 0.436803 |
| A_all | out1_model_app | not_product_matched | -0.002183 | 0.003531 | 0.53645 | 601.0 | 67.0 | 392.0 | -0.002898 | 0.455907 |
| A_all | all | product_matched | -0.003599 | 0.006348 | 0.570702 | 84.0 | 10.0 | 64.0 | -0.001884 | 0.416667 |
| A_all | model_app | product_matched | -0.003599 | 0.006348 | 0.570702 | 84.0 | 10.0 | 64.0 | -0.001884 | 0.416667 |
| A_all | own | product_matched | -0.00183 | 0.006888 | 0.790513 | 75.0 | 9.0 | 64.0 | -0.001293 | 0.453333 |
| A_all | own_model_app | product_matched | -0.00183 | 0.006888 | 0.790513 | 75.0 | 9.0 | 64.0 | -0.001293 | 0.453333 |
| A_all | out1_model_app | product_matched | -0.003599 | 0.006348 | 0.570702 | 84.0 | 10.0 | 64.0 | -0.001884 | 0.416667 |
| A_first_firm | all | not_product_matched | -0.006198 | 0.002792 | 0.02641 | 1076.0 | 122.0 | 692.0 | -0.003848 | 0.436803 |
| A_first_firm | model_app | not_product_matched | -0.004361 | 0.003424 | 0.202741 | 656.0 | 74.0 | 474.0 | -0.002462 | 0.457317 |
| A_first_firm | own | not_product_matched | -0.005914 | 0.003399 | 0.081918 | 770.0 | 87.0 | 511.0 | -0.003848 | 0.436364 |
| A_first_firm | own_model_app | not_product_matched | -0.005815 | 0.004323 | 0.178559 | 482.0 | 54.0 | 354.0 | -0.003285 | 0.441909 |
| A_first_firm | out1_model_app | not_product_matched | -0.003897 | 0.003852 | 0.311725 | 488.0 | 55.0 | 345.0 | -0.002768 | 0.44877 |
| A_first_firm | all | product_matched | -0.002445 | 0.008887 | 0.783197 | 58.0 | 7.0 | 54.0 | -0.001719 | 0.448276 |
| A_first_firm | model_app | product_matched | -0.002445 | 0.008887 | 0.783197 | 58.0 | 7.0 | 54.0 | -0.001719 | 0.448276 |
| A_first_firm | own | product_matched | -0.002445 | 0.008887 | 0.783197 | 58.0 | 7.0 | 54.0 | -0.001719 | 0.448276 |
| A_first_firm | own_model_app | product_matched | -0.002445 | 0.008887 | 0.783197 | 58.0 | 7.0 | 54.0 | -0.001719 | 0.448276 |
| A_first_firm | out1_model_app | product_matched | -0.002445 | 0.008887 | 0.783197 | 58.0 | 7.0 | 54.0 | -0.001719 | 0.448276 |

## Interpretation

H2 is not supported in this executable test. In the all-sample diagnostic means, `never_verified` is more negative than `later_verified`; restricting to model/app, own, own-model/app, or out=1 model/app weakens the never group but does not produce a significant later-vs-never gradient. The pooled interaction table also shows positive or near-zero `sim_later` coefficients and insignificant later-minus-never Wald tests. Product-level matched events are too few and are not more negative than unmatched events.

Design implication: registry verification should not be the main identifying axis unless the label definition is changed. The current evidence says that `never_verified` is not a clean cheap-talk control because many credible GenAI announcements do not need CAC product filing or do not disclose product names in a matchable way.
