# V9 GenAI Concreteness Main-Effect Checks

Date: 2026-05-28

## Purpose

Re-estimate the current Top5 peer-CAR main effect using the new Hope/Cheng-style event-level X:

`genai_concreteness_resid_z`

This run is deliberately a measurement handoff check. The old `specificity_z` result should not be assumed to carry over because the new X is only weakly correlated with the legacy variable.

## Sample

Input panel:

`results/v6_focal_good_news_pretrend_checks_20260525/analysis_sample_top5.csv.gz`

Event-level X:

`results/genai_concreteness_measure_20260528/event_genai_concreteness.csv`

Sample summary:

| metric                                  |        value |
|:----------------------------------------|-------------:|
| rows                                    | 7805         |
| events                                  | 2177         |
| focal_firms                             | 2177         |
| peer_firms                              | 3345         |
| ext_any_share_obs                       |    0.21089   |
| text_history_share_obs                  |    0.264061  |
| competitive_risk_share_events           |    0.324299  |
| category_validation_share_events        |    0.120349  |
| speculative_generic_share_events        |    0.688103  |
| substantive_existing_share_events       |    0.344511  |
| corr_legacy_specificity_new_resid_event |    0.116975  |
| corr_legacy_specificity_new_z_event     |    0.0570277 |

## Main X Horse-Race

Outcome: `PeerCAR[0,+1]`.

FE: `event_id + peer_industry_week`.

SE: two-way clustered by `event_id + peer_code`.

Controls:

- baseline: `PeerCAR[-10,-2] + PeerCAR[-20,-2]`
- focal-control version: baseline + `FocalCAR[0,+1] + FocalCAR[0,+1] x AIActive`
- residual-y version: outcome residualized on `PeerCAR[-10,-2]`, then controls `FocalCAR[0,+1] + FocalCAR[0,+1] x AIActive + PeerCAR[-20,-2]`

| ai_def       | x_key                      | model                                   | outcome                        | coef_se                |      p |   nobs |   events |   peer_firms |
|:-------------|:---------------------------|:----------------------------------------|:-------------------------------|:-----------------------|-------:|-------:|---------:|-------------:|
| ext_any      | legacy_specificity_z       | baseline_prewindow_controls             | peer_car_0_p1_mm               | -0.002303** (0.000992) | 0.0203 |   7805 |     2177 |         3345 |
| ext_any      | legacy_specificity_z       | add_focal_car_and_focal_car_x_ai        | peer_car_0_p1_mm               | -0.002307** (0.000991) | 0.0198 |   7805 |     2177 |         3345 |
| ext_any      | legacy_specificity_z       | residual_y_on_pre10_plus_focal_controls | peer_car_0_p1_resid_pre10_newx | -0.002300** (0.000990) | 0.0201 |   7805 |     2177 |         3345 |
| ext_any      | genai_concreteness_z       | baseline_prewindow_controls             | peer_car_0_p1_mm               | -0.000990 (0.001325)   | 0.4549 |   7805 |     2177 |         3345 |
| ext_any      | genai_concreteness_z       | add_focal_car_and_focal_car_x_ai        | peer_car_0_p1_mm               | -0.001016 (0.001290)   | 0.4306 |   7805 |     2177 |         3345 |
| ext_any      | genai_concreteness_z       | residual_y_on_pre10_plus_focal_controls | peer_car_0_p1_resid_pre10_newx | -0.001044 (0.001286)   | 0.4169 |   7805 |     2177 |         3345 |
| ext_any      | genai_concreteness_resid_z | baseline_prewindow_controls             | peer_car_0_p1_mm               | 0.000587 (0.001329)    | 0.6589 |   7805 |     2177 |         3345 |
| ext_any      | genai_concreteness_resid_z | add_focal_car_and_focal_car_x_ai        | peer_car_0_p1_mm               | 0.000574 (0.001313)    | 0.6619 |   7805 |     2177 |         3345 |
| ext_any      | genai_concreteness_resid_z | residual_y_on_pre10_plus_focal_controls | peer_car_0_p1_resid_pre10_newx | 0.000588 (0.001312)    | 0.6542 |   7805 |     2177 |         3345 |
| text_history | legacy_specificity_z       | baseline_prewindow_controls             | peer_car_0_p1_mm               | -0.002275** (0.001030) | 0.0272 |   7805 |     2177 |         3345 |
| text_history | legacy_specificity_z       | add_focal_car_and_focal_car_x_ai        | peer_car_0_p1_mm               | -0.002283** (0.001029) | 0.0266 |   7805 |     2177 |         3345 |
| text_history | legacy_specificity_z       | residual_y_on_pre10_plus_focal_controls | peer_car_0_p1_resid_pre10_newx | -0.002281** (0.001027) | 0.0264 |   7805 |     2177 |         3345 |
| text_history | genai_concreteness_z       | baseline_prewindow_controls             | peer_car_0_p1_mm               | -0.000118 (0.001149)   | 0.9182 |   7805 |     2177 |         3345 |
| text_history | genai_concreteness_z       | add_focal_car_and_focal_car_x_ai        | peer_car_0_p1_mm               | -0.000092 (0.001136)   | 0.9354 |   7805 |     2177 |         3345 |
| text_history | genai_concreteness_z       | residual_y_on_pre10_plus_focal_controls | peer_car_0_p1_resid_pre10_newx | -0.000100 (0.001136)   | 0.93   |   7805 |     2177 |         3345 |
| text_history | genai_concreteness_resid_z | baseline_prewindow_controls             | peer_car_0_p1_mm               | 0.001493 (0.001330)    | 0.2616 |   7805 |     2177 |         3345 |
| text_history | genai_concreteness_resid_z | add_focal_car_and_focal_car_x_ai        | peer_car_0_p1_mm               | 0.001502 (0.001332)    | 0.2593 |   7805 |     2177 |         3345 |
| text_history | genai_concreteness_resid_z | residual_y_on_pre10_plus_focal_controls | peer_car_0_p1_resid_pre10_newx | 0.001545 (0.001334)    | 0.2466 |   7805 |     2177 |         3345 |

## Content-Type Horse-Race With New X

Outcome: `PeerCAR[0,+1]`.

Main X: `genai_concreteness_resid_z x AIActive`.

| ai_def       | model                               | term                         | coef_se               |      p |   nobs |   events |   peer_firms |
|:-------------|:------------------------------------|:-----------------------------|:----------------------|-------:|-------:|---------:|-------------:|
| ext_any      | concreteness_plus_content_type_x_ai | x_ai                         | 0.001559 (0.001442)   | 0.2794 |   7805 |     2177 |         3345 |
| ext_any      | concreteness_plus_content_type_x_ai | competitive_risk_ai          | -0.015644* (0.008562) | 0.0677 |   7805 |     2177 |         3345 |
| ext_any      | concreteness_plus_content_type_x_ai | category_validation_ai       | 0.003030 (0.004068)   | 0.4563 |   7805 |     2177 |         3345 |
| ext_any      | concreteness_plus_content_type_x_ai | speculative_or_generic_ai    | 0.005872 (0.005053)   | 0.2452 |   7805 |     2177 |         3345 |
| ext_any      | concreteness_plus_content_type_x_ai | substantive_or_existing_ai   | 0.017121* (0.009123)  | 0.0605 |   7805 |     2177 |         3345 |
| ext_any      | content_specific_concreteness_x_ai  | competitive_risk_x_ai        | -0.004015 (0.007043)  | 0.5687 |   7805 |     2177 |         3345 |
| ext_any      | content_specific_concreteness_x_ai  | category_validation_x_ai     | -0.006654* (0.003842) | 0.0833 |   7805 |     2177 |         3345 |
| ext_any      | content_specific_concreteness_x_ai  | speculative_or_generic_x_ai  | -0.006801 (0.004414)  | 0.1233 |   7805 |     2177 |         3345 |
| ext_any      | content_specific_concreteness_x_ai  | substantive_or_existing_x_ai | -0.005001 (0.008658)  | 0.5636 |   7805 |     2177 |         3345 |
| text_history | concreteness_plus_content_type_x_ai | x_ai                         | 0.001923 (0.001370)   | 0.1605 |   7805 |     2177 |         3345 |
| text_history | concreteness_plus_content_type_x_ai | competitive_risk_ai          | 0.001139 (0.010240)   | 0.9114 |   7805 |     2177 |         3345 |
| text_history | concreteness_plus_content_type_x_ai | category_validation_ai       | 0.003920 (0.004509)   | 0.3847 |   7805 |     2177 |         3345 |
| text_history | concreteness_plus_content_type_x_ai | speculative_or_generic_ai    | 0.004083 (0.004116)   | 0.3211 |   7805 |     2177 |         3345 |
| text_history | concreteness_plus_content_type_x_ai | substantive_or_existing_ai   | 0.000614 (0.010535)   | 0.9536 |   7805 |     2177 |         3345 |
| text_history | content_specific_concreteness_x_ai  | competitive_risk_x_ai        | 0.012237 (0.010189)   | 0.2297 |   7805 |     2177 |         3345 |
| text_history | content_specific_concreteness_x_ai  | category_validation_x_ai     | -0.000954 (0.004845)  | 0.8439 |   7805 |     2177 |         3345 |
| text_history | content_specific_concreteness_x_ai  | speculative_or_generic_x_ai  | 0.003611 (0.003523)   | 0.3054 |   7805 |     2177 |         3345 |
| text_history | content_specific_concreteness_x_ai  | substantive_or_existing_x_ai | -0.019493 (0.012367)  | 0.115  |   7805 |     2177 |         3345 |

## Content-Flag Subsamples

Each row estimates the main `genai_concreteness_resid_z x AIActive` coefficient within events carrying the listed content flag.

| ai_def       | model                                     | coef_se              |      p |   nobs |   events |   peer_firms |
|:-------------|:------------------------------------------|:---------------------|-------:|-------:|---------:|-------------:|
| ext_any      | subsample_competitive_risk_content        | -0.000434 (0.001590) | 0.7851 |   2553 |      706 |         1665 |
| text_history | subsample_competitive_risk_content        | 0.001247 (0.001401)  | 0.3735 |   2553 |      706 |         1665 |
| ext_any      | subsample_category_validation_content     | -0.000452 (0.003342) | 0.8924 |    918 |      262 |          742 |
| text_history | subsample_category_validation_content     | -0.000544 (0.005323) | 0.9186 |    918 |      262 |          742 |
| ext_any      | subsample_speculative_or_generic_content  | -0.002774 (0.003699) | 0.4533 |   5371 |     1498 |         2823 |
| text_history | subsample_speculative_or_generic_content  | 0.004857 (0.003331)  | 0.1447 |   5371 |     1498 |         2823 |
| ext_any      | subsample_substantive_or_existing_content | -0.000482 (0.001555) | 0.7566 |   2712 |      750 |         1735 |
| text_history | subsample_substantive_or_existing_content | 0.000590 (0.001406)  | 0.675  |   2712 |      750 |         1735 |

## Interpretation Note

If `genai_concreteness_resid_z x AIActive` is weak or unstable while the old `specificity_z x AIActive` remains significant, the existing peer-revaluation result is not yet secured by the new Hope/Cheng-style X. In that case the paper should either:

1. keep the legacy `specificity_z` as the empirical X and use this new measure as a validation/robustness branch, or
2. revise the new measure before treating it as the headline X.

