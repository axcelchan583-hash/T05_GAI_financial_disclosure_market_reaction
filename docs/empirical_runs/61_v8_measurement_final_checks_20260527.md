# V8 Measurement and Final-Design Closure Checks

Date: 2026-05-27

## Purpose

This run closes the reviewer-facing empirical gaps for the current capital-market peer-revaluation design. It does not pivot to a new paper. The central conclusion is deliberately conservative: the main peer-CAR result remains usable. The 300-row double-coded sample is treated as an internal construct-boundary check, not as a main-paper validation gate, because the human/Claude scores capture stricter implementation-specificity while the current `Specificity_z` is an objective text-detail / disclosure-concreteness proxy.

## 1. Final Sample Freeze

```text
        sample_name  rows  events  focal_firms  peer_firms   date_min   date_max  rank_min  rank_max   mean_y  ext_any_share  text_history_share  requires_peer_pre10_pre20  requires_focal_car  announcement_cleaned
final_headline_top5  7805    2177         2177        3345 2023-01-01 2026-05-20         1         5 -0.00004        0.21089            0.264061                       True                True                  True
```

```text
 event_year  rows  events  peer_firms
       2023  2872     866        1589
       2024   763     211         644
       2025  3988    1051        2313
       2026   182      49         175
```

Interpretation: this is the sample to use for all headline tables. Older 8,649-row tables are pre-freeze checks that did not require the same focal-CAR/pre-window-complete filters.

## 2. Specificity Double-Coding Validation

```text
                         variable   n  agent1_ones  claude_ones  agreement_rate  cohens_kappa
     has_specific_product_service 300         97.0         46.0        0.816667      0.514363
          has_model_platform_name 300         78.0         60.0        0.913333      0.756554
            has_specific_use_case 300        102.0         74.0        0.873333      0.697645
         has_customer_or_industry 300         76.0         31.0        0.843333      0.485176
               has_partner_or_org 300         26.0         13.0        0.943333      0.537373
            has_deployment_status 300         94.0         62.0        0.886667      0.709766
has_commercialization_or_timeline 300         29.0          2.0        0.910000      0.118031
      has_quantitative_commitment 300         27.0          1.0        0.913333      0.065421
            specificity_score_0_4 300          NaN          NaN        0.676667      0.432538
```

```text
                           x                            y  pearson  spearman   n
        component_sum_claude         component_sum_agent1 0.777638  0.779594 300
specificity_score_0_4_claude specificity_score_0_4_agent1 0.847737  0.829135 300
          component_sum_mean         specificity_z_agent1 0.043720  0.032536 300
      specificity_score_mean         specificity_z_agent1 0.032549  0.026483 300
        component_sum_claude         specificity_z_agent1 0.078414  0.072792 300
specificity_score_0_4_claude         specificity_z_agent1 0.065362  0.060251 300
        component_sum_agent1         specificity_z_agent1 0.015744  0.029667 300
specificity_score_0_4_agent1         specificity_z_agent1 0.004886  0.025669 300
```

```text
specificity_bin_agent1   n  mean_proxy_specificity_z  mean_claude_score  mean_agent_score  mean_score_mean  mean_component_sum_mean
                  high 100                  1.561024               0.95              1.14            1.045                    1.470
                   low 100                 -1.046879               0.65              0.95            0.800                    1.065
                   mid 100                 -0.048606               0.78              1.42            1.100                    1.555
```

Interpretation: coder-to-coder score correlation is strong, but both coders' stricter implementation-specificity scores correlate only weakly with the original `Specificity_z`. For the current paper package, do not use this as a headline validation table or as a reason to replace the main X. Treat it as evidence that the existing proxy should be described as objective disclosure detail / concreteness, not as manually coded implementation specificity.

## 3. AI-Theme Date-Shock Controls

```text
                    model               ai_def      coef       se         z        p  nobs  events  peer_firms                                                       controls
                 baseline              ext_any -0.002303 0.000992 -2.321121 0.020280  7805    2177        3345                               PeerCAR[-10,-2], PeerCAR[-20,-2]
        add_ai_theme_x_ai              ext_any -0.002112 0.000983 -2.148079 0.031707  7805    2177        3345 AI-theme abnormal return[0,+1] x AIActive, pre-window controls
          add_market_x_ai              ext_any -0.002328 0.000992 -2.347234 0.018913  7805    2177        3345            Market return[0,+1] x AIActive, pre-window controls
add_theme_and_market_x_ai              ext_any -0.002129 0.000982 -2.168515 0.030119  7805    2177        3345    AI-theme x AIActive, market x AIActive, pre-window controls
                 baseline current_text_history -0.002275 0.001030 -2.208437 0.027214  7805    2177        3345                               PeerCAR[-10,-2], PeerCAR[-20,-2]
        add_ai_theme_x_ai current_text_history -0.001835 0.001031 -1.779950 0.075084  7805    2177        3345 AI-theme abnormal return[0,+1] x AIActive, pre-window controls
          add_market_x_ai current_text_history -0.002302 0.001028 -2.239792 0.025104  7805    2177        3345            Market return[0,+1] x AIActive, pre-window controls
add_theme_and_market_x_ai current_text_history -0.001868 0.001029 -1.814872 0.069544  7805    2177        3345    AI-theme x AIActive, market x AIActive, pre-window controls
```

Interpretation: the headline coefficient is stable after controlling for AI-theme abnormal-return shocks interacted with AIActive.

## 4. External AIActive Component Audit on Final Sample

```text
                       ai_def  obs_active  obs_share  active_peer_firms  total_peer_firms  active_events  total_events
                    prior_cac          24   0.003075                 15              3345             23          2177
        prior_ai_patent_grant         138   0.017681                 49              3345            130          2177
     prior_genai_patent_grant          21   0.002691                  9              3345             21          2177
prior_broad_ai_hiring_365_ge1        1554   0.199103                746              3345           1058          2177
prior_broad_ai_hiring_365_ge3         716   0.091736                367              3345            577          2177
   prior_genai_hiring_365_ge1         532   0.068161                315              3345            456          2177
                ext_no_hiring         162   0.020756                 64              3345            153          2177
                      ext_any        1646   0.210890                773              3345           1097          2177
                   ext_strict         835   0.106983                409              3345            658          2177
             ext_genai_strict         560   0.071749                325              3345            473          2177
             ext_plus_history        2588   0.331582               1293              3345           1448          2177
         current_text_history        2061   0.264061               1102              3345           1201          2177
```

```text
                       ai_def      coef       se         z        p  nobs  events  peer_firms                         controls
                    prior_cac  0.001305 0.010165  0.128354 0.897869  7805    2177        3345 PeerCAR[-10,-2], PeerCAR[-20,-2]
        prior_ai_patent_grant -0.009719 0.003292 -2.952131 0.003156  7805    2177        3345 PeerCAR[-10,-2], PeerCAR[-20,-2]
     prior_genai_patent_grant -0.011650 0.009928 -1.173465 0.240609  7805    2177        3345 PeerCAR[-10,-2], PeerCAR[-20,-2]
prior_broad_ai_hiring_365_ge1 -0.001813 0.001018 -1.780490 0.074996  7805    2177        3345 PeerCAR[-10,-2], PeerCAR[-20,-2]
prior_broad_ai_hiring_365_ge3 -0.000422 0.001473 -0.286741 0.774311  7805    2177        3345 PeerCAR[-10,-2], PeerCAR[-20,-2]
   prior_genai_hiring_365_ge1  0.000052 0.001623  0.031803 0.974630  7805    2177        3345 PeerCAR[-10,-2], PeerCAR[-20,-2]
                ext_no_hiring -0.008419 0.003067 -2.744805 0.006055  7805    2177        3345 PeerCAR[-10,-2], PeerCAR[-20,-2]
                      ext_any -0.002303 0.000992 -2.321121 0.020280  7805    2177        3345 PeerCAR[-10,-2], PeerCAR[-20,-2]
                   ext_strict -0.001885 0.001394 -1.352749 0.176136  7805    2177        3345 PeerCAR[-10,-2], PeerCAR[-20,-2]
             ext_genai_strict -0.000443 0.001603 -0.276310 0.782310  7805    2177        3345 PeerCAR[-10,-2], PeerCAR[-20,-2]
             ext_plus_history -0.002400 0.000961 -2.497433 0.012510  7805    2177        3345 PeerCAR[-10,-2], PeerCAR[-20,-2]
         current_text_history -0.002275 0.001030 -2.208437 0.027214  7805    2177        3345 PeerCAR[-10,-2], PeerCAR[-20,-2]
```

Interpretation: `ext_any` should remain the headline AIActive because it is external to the disclosure text. The components are heterogeneous; `prior_ai_patent_grant` and `ext_no_hiring` are cleaner but sparse, while hiring supplies broad coverage.

## 5. Economic Magnitude

```text
       cap_basis  coef_used  active_obs_with_cap  coverage_share_active_obs  median_cap_rmb  mean_cap_rmb  p25_cap_rmb  p75_cap_rmb  median_effect_rmb  mean_effect_rmb  sum_effect_across_active_obs_rmb
total_market_cap  -0.002303                 1627                   0.988457    9484800000.0  3.773195e+10 4815338760.0 2.495347e+10      -2.184607e+07    -8.690693e+07                     -1.413976e+11
float_market_cap  -0.002303                 1627                   0.988457    7750535650.0  3.439345e+10 3691920920.0 2.149479e+10      -1.785159e+07    -7.921747e+07                     -1.288868e+11
```

Interpretation: multiply by -0.002303, the final-sample `ext_any` coefficient from the focal-good-news/pretrend table. CSMAR daily market caps are in thousand RMB before conversion.

## 6. Existing Placebo Evidence

### Non-GenAI pseudo-events

```text
                         model          outcome         term     coef       se        z        p  nobs  events  peer_firms    mean_y               ai_def                        fe_spec
non_genai_iip_pseudo_event_ddd peer_car_0_p1_mm spec_ai_true 0.002349 0.002554 0.919798 0.357678 14790    2436        3679 -0.000726 current_text_history                       event_fe
non_genai_iip_pseudo_event_ddd peer_car_0_p1_mm spec_ai_true 0.002284 0.002558 0.892764 0.371984 14790    2436        3679 -0.000726 current_text_history event_fe_peer_industry_week_fe
```

### Pre-window placebo

```text
            model              outcome    term      coef       se         z        p  nobs  events  peer_firms   mean_y peer_group               ai_def                        fe_spec
prewindow_placebo peer_car_pre10_m2_mm spec_ai -0.004847 0.002393 -2.025534 0.042813  8670    2415        3570 0.008466  true_top5 current_text_history event_fe_peer_industry_week_fe
prewindow_placebo peer_car_pre20_m2_mm spec_ai -0.009149 0.003113 -2.938725 0.003296  8649    2415        3566 0.012778  true_top5 current_text_history event_fe_peer_industry_week_fe
prewindow_placebo peer_car_pre10_m2_mm spec_ai  0.000076 0.002212  0.034372 0.972580  8670    2415        3570 0.008466  true_top5              ext_any event_fe_peer_industry_week_fe
prewindow_placebo peer_car_pre20_m2_mm spec_ai -0.001749 0.002973 -0.588290 0.556338  8649    2415        3566 0.012778  true_top5              ext_any event_fe_peer_industry_week_fe
prewindow_placebo peer_car_pre10_m2_mm spec_ai -0.004496 0.003084 -1.457922 0.144862  7236    2341        1679 0.004781   low_top5 current_text_history event_fe_peer_industry_week_fe
prewindow_placebo peer_car_pre20_m2_mm spec_ai -0.006644 0.004459 -1.490064 0.136207  7218    2341        1679 0.007921   low_top5 current_text_history event_fe_peer_industry_week_fe
prewindow_placebo peer_car_pre10_m2_mm spec_ai -0.002293 0.002880 -0.796073 0.425990  7236    2341        1679 0.004781   low_top5              ext_any event_fe_peer_industry_week_fe
prewindow_placebo peer_car_pre20_m2_mm spec_ai -0.003615 0.004158 -0.869452 0.384600  7218    2341        1679 0.007921   low_top5              ext_any event_fe_peer_industry_week_fe
```

## Output Files

- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_measurement_final_checks_20260527/final_sample_summary.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_measurement_final_checks_20260527/final_sample_by_year.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_measurement_final_checks_20260527/specificity_coder_agreement.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_measurement_final_checks_20260527/specificity_coder_correlations.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_measurement_final_checks_20260527/specificity_coder_bin_summary.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_measurement_final_checks_20260527/specificity_validated_scores_300.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_measurement_final_checks_20260527/ai_theme_shock_controls.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_measurement_final_checks_20260527/external_component_regs.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_measurement_final_checks_20260527/external_component_counts.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_measurement_final_checks_20260527/economic_magnitude.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_measurement_final_checks_20260527/non_genai_pseudo_event_summary.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_measurement_final_checks_20260527/prewindow_placebo_summary.csv`
