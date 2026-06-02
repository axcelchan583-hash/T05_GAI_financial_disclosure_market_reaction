# v14 Data-Processing Sensitivity Checks

Date: 2026-05-31

Purpose: diagnose whether the current peer-CAR main effect is driven by data
quality filters, outliers, variable scaling, event windows, or lag controls.

This run does **not** change the research design or introduce a new Y.

## Input

- Panel: `results/v6_external_ai_active_checks_20260524/true_panel_with_external_ai_active.csv.gz`
- Main sample: first focal GenAI event x old CSMAR-scope Top5 peers
- Main outcome: `PeerCAR[0,+1]` (`peer_car_0_p1_mm`)
- Main term: `Specificity_z x AIActivePeer`
- Main FE: `event_id + peer_industry_week`
- SE: inherited from `fit_absorbed`, two-way clustered by event and peer firm

## Data Quality Summary

| sample               |   rows |   events |   focal_firms |   peer_firms |   duplicate_event_peer_rows |   missing_peer_car_0_p1 |   missing_specificity_z |   missing_ext_any |   mean_peer_car_0_p1 |   sd_peer_car_0_p1 |   p01_peer_car_0_p1 |   p99_peer_car_0_p1 |   mean_specificity_z |   sd_specificity_z |   mean_ext_any |   mean_text_history |
|:---------------------|-------:|---------:|--------------:|-------------:|----------------------------:|------------------------:|------------------------:|------------------:|---------------------:|-------------------:|--------------------:|--------------------:|---------------------:|-------------------:|---------------:|--------------------:|
| full_true_panel      | 201240 |    20124 |          2652 |         5251 |                           0 |                   14458 |                       0 |                 0 |         -0.000156459 |          0.0472316 |          -0.115812  |            0.159817 |            1.627e-16 |           0.999978 |       0.36052  |            0.51851  |
| standard_top5_sample |   8683 |     2416 |          2416 |         3573 |                           0 |                       0 |                       0 |                 0 |         -0.00033195  |          0.0341178 |          -0.0894782 |            0.104238 |            0.188971  |           1.25988  |       0.207993 |            0.255672 |

## Main Cleaning Variants

| model                      | ai_def               |    coef |     se |      p |   nobs |   events |   peer_firms |   mean_y |
|:---------------------------|:---------------------|--------:|-------:|-------:|-------:|---------:|-------------:|---------:|
| raw_first_top5             | ext_any              | -0.001  | 0.0009 | 0.2475 |  12048 |     2652 |         4131 |   0.0016 |
| raw_first_top5             | current_text_history | -0.0017 | 0.001  | 0.0893 |  12048 |     2652 |         4131 |   0.0016 |
| base_clean_no_ann_filter   | ext_any              | -0.0011 | 0.0008 | 0.1588 |  11243 |     2646 |         3971 |  -0.0001 |
| base_clean_no_ann_filter   | current_text_history | -0.0014 | 0.0009 | 0.1027 |  11243 |     2646 |         3971 |  -0.0001 |
| headline_standard          | ext_any              | -0.0021 | 0.0009 | 0.0245 |   8649 |     2415 |         3566 |  -0.0003 |
| headline_standard          | current_text_history | -0.002  | 0.001  | 0.0357 |   8649 |     2415 |         3566 |  -0.0003 |
| drop_any_focal_or_peer_ann | ext_any              | -0.0021 | 0.0011 | 0.0648 |   6541 |     2113 |         3124 |   0.0002 |
| drop_any_focal_or_peer_ann | current_text_history | -0.0018 | 0.0012 | 0.1309 |   6541 |     2113 |         3124 |   0.0002 |
| drop_st_like_names         | ext_any              | -0.0022 | 0.001  | 0.0194 |   8379 |     2365 |         3491 |  -0.0002 |
| drop_st_like_names         | current_text_history | -0.0023 | 0.001  | 0.0203 |   8379 |     2365 |         3491 |  -0.0002 |
| same_industry_only         | ext_any              | -0.0034 | 0.0015 | 0.0235 |   3936 |     1706 |         2180 |   0.0003 |
| same_industry_only         | current_text_history | -0.0031 | 0.0014 | 0.0313 |   3936 |     1706 |         2180 |   0.0003 |
| est_obs_ge200              | ext_any              | -0.0021 | 0.0009 | 0.0247 |   8536 |     2413 |         3540 |  -0.0002 |
| est_obs_ge200              | current_text_history | -0.0018 | 0.001  | 0.0624 |   8536 |     2413 |         3540 |  -0.0002 |
| positive_similarity        | ext_any              | -0.0021 | 0.0009 | 0.0245 |   8649 |     2415 |         3566 |  -0.0003 |
| positive_similarity        | current_text_history | -0.002  | 0.001  | 0.0357 |   8649 |     2415 |         3566 |  -0.0003 |

## Outlier and Y-Transformation Variants

| model                 | ai_def               | outcome               |    coef |     se |      p |   nobs |   events |   peer_firms |
|:----------------------|:---------------------|:----------------------|--------:|-------:|-------:|-------:|---------:|-------------:|
| headline_unmodified_y | ext_any              | peer_car_0_p1_mm      | -0.0021 | 0.0009 | 0.0245 |   8649 |     2415 |         3566 |
| headline_unmodified_y | current_text_history | peer_car_0_p1_mm      | -0.002  | 0.001  | 0.0357 |   8649 |     2415 |         3566 |
| winsor_y_1_99         | ext_any              | peer_car_0_p1_w1p99   | -0.0019 | 0.0009 | 0.0298 |   8649 |     2415 |         3566 |
| winsor_y_1_99         | current_text_history | peer_car_0_p1_w1p99   | -0.0019 | 0.0009 | 0.0354 |   8649 |     2415 |         3566 |
| winsor_y_2p5_97p5     | ext_any              | peer_car_0_p1_w25p975 | -0.0017 | 0.0008 | 0.0429 |   8649 |     2415 |         3566 |
| winsor_y_2p5_97p5     | current_text_history | peer_car_0_p1_w25p975 | -0.0018 | 0.0008 | 0.0302 |   8649 |     2415 |         3566 |
| trim_y_1_99           | ext_any              | peer_car_0_p1_mm      | -0.0016 | 0.0008 | 0.051  |   8484 |     2413 |         3535 |
| trim_y_1_99           | current_text_history | peer_car_0_p1_mm      | -0.0019 | 0.0008 | 0.0228 |   8484 |     2413 |         3535 |
| trim_y_2p5_97p5       | ext_any              | peer_car_0_p1_mm      | -0.0008 | 0.0008 | 0.2613 |   8223 |     2407 |         3484 |
| trim_y_2p5_97p5       | current_text_history | peer_car_0_p1_mm      | -0.0006 | 0.0007 | 0.382  |   8223 |     2407 |         3484 |
| asinh_y               | ext_any              | peer_car_0_p1_asinh   | -0.0021 | 0.0009 | 0.0246 |   8649 |     2415 |         3566 |
| asinh_y               | current_text_history | peer_car_0_p1_asinh   | -0.002  | 0.001  | 0.0357 |   8649 |     2415 |         3566 |
| within_event_rank_y   | ext_any              | peer_car_0_p1_rank_z  | -0.0705 | 0.0354 | 0.0461 |   8552 |     2318 |         3556 |
| within_event_rank_y   | current_text_history | peer_car_0_p1_rank_z  | -0.0251 | 0.0335 | 0.4531 |   8552 |     2318 |         3556 |
| calendar_date_z_y     | ext_any              | peer_car_0_p1_date_z  | -0.0741 | 0.0301 | 0.0138 |   8641 |     2407 |         3565 |
| calendar_date_z_y     | current_text_history | peer_car_0_p1_date_z  | -0.0484 | 0.0299 | 0.1048 |   8641 |     2407 |         3565 |

## Specificity Transformations

| model                                       | ai_def               | spec_col                     |    coef |     se |      p |   nobs |   events |   peer_firms |
|:--------------------------------------------|:---------------------|:-----------------------------|--------:|-------:|-------:|-------:|---------:|-------------:|
| spec_transform_specificity_z                | ext_any              | specificity_z                | -0.0021 | 0.0009 | 0.0245 |   8649 |     2415 |         3566 |
| spec_transform_specificity_z                | current_text_history | specificity_z                | -0.002  | 0.001  | 0.0357 |   8649 |     2415 |         3566 |
| spec_transform_specificity_raw_z            | ext_any              | specificity_raw_z            | -0.0027 | 0.0012 | 0.0185 |   8649 |     2415 |         3566 |
| spec_transform_specificity_raw_z            | current_text_history | specificity_raw_z            | -0.0027 | 0.0012 | 0.0314 |   8649 |     2415 |         3566 |
| spec_transform_specificity_log1p_z          | ext_any              | specificity_log1p_z          | -0.0029 | 0.0012 | 0.0164 |   8649 |     2415 |         3566 |
| spec_transform_specificity_log1p_z          | current_text_history | specificity_log1p_z          | -0.0034 | 0.0013 | 0.0109 |   8649 |     2415 |         3566 |
| spec_transform_specificity_rank_z           | ext_any              | specificity_rank_z           | -0.0025 | 0.0012 | 0.0373 |   8649 |     2415 |         3566 |
| spec_transform_specificity_rank_z           | current_text_history | specificity_rank_z           | -0.0031 | 0.0012 | 0.0111 |   8649 |     2415 |         3566 |
| spec_transform_specificity_w_p1p99_z        | ext_any              | specificity_w_p1p99_z        | -0.0026 | 0.0012 | 0.0261 |   8649 |     2415 |         3566 |
| spec_transform_specificity_w_p1p99_z        | current_text_history | specificity_w_p1p99_z        | -0.0026 | 0.0012 | 0.033  |   8649 |     2415 |         3566 |
| spec_transform_specificity_z_w_p1p99        | ext_any              | specificity_z_w_p1p99        | -0.0027 | 0.0012 | 0.0245 |   8649 |     2415 |         3566 |
| spec_transform_specificity_z_w_p1p99        | current_text_history | specificity_z_w_p1p99        | -0.0026 | 0.0012 | 0.0357 |   8649 |     2415 |         3566 |
| spec_transform_specificity_z_by_year_recalc | ext_any              | specificity_z_by_year_recalc | -0.0021 | 0.0012 | 0.0816 |   8649 |     2415 |         3566 |
| spec_transform_specificity_z_by_year_recalc | current_text_history | specificity_z_by_year_recalc | -0.0017 | 0.0012 | 0.157  |   8649 |     2415 |         3566 |

## Event Windows and Lag Controls

| model                        | ai_def               | outcome               |    coef |     se |      p |   nobs |   events |   peer_firms |
|:-----------------------------|:---------------------|:----------------------|--------:|-------:|-------:|-------:|---------:|-------------:|
| window_peer_ar0_mm           | ext_any              | peer_ar0_mm           | -0.0009 | 0.0007 | 0.1513 |   8649 |     2415 |         3566 |
| window_peer_ar0_mm           | current_text_history | peer_ar0_mm           | -0.0012 | 0.0008 | 0.1405 |   8649 |     2415 |         3566 |
| window_peer_car_0_p1_mm      | ext_any              | peer_car_0_p1_mm      | -0.0021 | 0.0009 | 0.0245 |   8649 |     2415 |         3566 |
| window_peer_car_0_p1_mm      | current_text_history | peer_car_0_p1_mm      | -0.002  | 0.001  | 0.0357 |   8649 |     2415 |         3566 |
| window_peer_car_m1_0_mm      | ext_any              | peer_car_m1_0_mm      | -0.0009 | 0.0009 | 0.303  |   8649 |     2415 |         3566 |
| window_peer_car_m1_0_mm      | current_text_history | peer_car_m1_0_mm      | -0.0005 | 0.001  | 0.6262 |   8649 |     2415 |         3566 |
| window_peer_car_m1_p1_mm     | ext_any              | peer_car_m1_p1_mm     | -0.002  | 0.0011 | 0.0663 |   8649 |     2415 |         3566 |
| window_peer_car_m1_p1_mm     | current_text_history | peer_car_m1_p1_mm     | -0.0013 | 0.0011 | 0.2452 |   8649 |     2415 |         3566 |
| window_peer_car_p1_p2_mm     | ext_any              | peer_car_p1_p2_mm     | -0.0014 | 0.001  | 0.1775 |   8649 |     2415 |         3566 |
| window_peer_car_p1_p2_mm     | current_text_history | peer_car_p1_p2_mm     |  0.0001 | 0.001  | 0.9261 |   8649 |     2415 |         3566 |
| window_peer_car_post2_p5_mm  | ext_any              | peer_car_post2_p5_mm  | -0.0022 | 0.0015 | 0.1373 |   8641 |     2413 |         3564 |
| window_peer_car_post2_p5_mm  | current_text_history | peer_car_post2_p5_mm  |  0.0011 | 0.0017 | 0.4992 |   8641 |     2413 |         3564 |
| window_peer_car_post2_p10_mm | ext_any              | peer_car_post2_p10_mm | -0.0009 | 0.0023 | 0.7017 |   8609 |     2405 |         3556 |
| window_peer_car_post2_p10_mm | current_text_history | peer_car_post2_p10_mm |  0.0022 | 0.0023 | 0.3363 |   8609 |     2405 |         3556 |
| window_peer_car_pre5_m2_mm   | ext_any              | peer_car_pre5_m2_mm   |  0.0003 | 0.0016 | 0.8698 |   8675 |     2416 |         3570 |
| window_peer_car_pre5_m2_mm   | current_text_history | peer_car_pre5_m2_mm   | -0.0012 | 0.0018 | 0.5011 |   8675 |     2416 |         3570 |
| window_peer_car_pre10_m2_mm  | ext_any              | peer_car_pre10_m2_mm  |  0.0001 | 0.0022 | 0.9726 |   8670 |     2415 |         3570 |
| window_peer_car_pre10_m2_mm  | current_text_history | peer_car_pre10_m2_mm  | -0.0048 | 0.0024 | 0.0428 |   8670 |     2415 |         3570 |
| window_peer_car_pre20_m11_mm | ext_any              | peer_car_pre20_m11_mm | -0.0019 | 0.0022 | 0.39   |   8646 |     2415 |         3565 |
| window_peer_car_pre20_m11_mm | current_text_history | peer_car_pre20_m11_mm | -0.0048 | 0.0021 | 0.0245 |   8646 |     2415 |         3565 |

## Alternative Pre-Window Controls

| model                    | ai_def               |    coef |     se |      p |   nobs |   events |   peer_firms | controls                                                      |
|:-------------------------|:---------------------|--------:|-------:|-------:|-------:|---------:|-------------:|:--------------------------------------------------------------|
| no_pre_controls          | ext_any              | -0.0018 | 0.001  | 0.0583 |   8683 |     2416 |         3573 | none                                                          |
| no_pre_controls          | current_text_history | -0.0023 | 0.001  | 0.0201 |   8683 |     2416 |         3573 | none                                                          |
| control_pre5_m2          | ext_any              | -0.002  | 0.0009 | 0.0368 |   8675 |     2416 |         3570 | peer_car_pre5_m2_mm                                           |
| control_pre5_m2          | current_text_history | -0.002  | 0.001  | 0.0339 |   8675 |     2416 |         3570 | peer_car_pre5_m2_mm                                           |
| control_pre10_m2         | ext_any              | -0.0021 | 0.0009 | 0.0259 |   8670 |     2415 |         3570 | peer_car_pre10_m2_mm                                          |
| control_pre10_m2         | current_text_history | -0.002  | 0.001  | 0.034  |   8670 |     2415 |         3570 | peer_car_pre10_m2_mm                                          |
| control_pre20_m11        | ext_any              | -0.002  | 0.0009 | 0.0307 |   8646 |     2415 |         3565 | peer_car_pre20_m11_mm                                         |
| control_pre20_m11        | current_text_history | -0.0019 | 0.001  | 0.048  |   8646 |     2415 |         3565 | peer_car_pre20_m11_mm                                         |
| control_pre10_and_pre20  | ext_any              | -0.0021 | 0.0009 | 0.0245 |   8649 |     2415 |         3566 | peer_car_pre10_m2_mm+peer_car_pre20_m2_mm                     |
| control_pre10_and_pre20  | current_text_history | -0.002  | 0.001  | 0.0357 |   8649 |     2415 |         3566 | peer_car_pre10_m2_mm+peer_car_pre20_m2_mm                     |
| control_pre5_pre10_pre20 | ext_any              | -0.0021 | 0.0009 | 0.0249 |   8649 |     2415 |         3566 | peer_car_pre5_m2_mm+peer_car_pre10_m2_mm+peer_car_pre20_m2_mm |
| control_pre5_pre10_pre20 | current_text_history | -0.002  | 0.001  | 0.0407 |   8649 |     2415 |         3566 | peer_car_pre5_m2_mm+peer_car_pre10_m2_mm+peer_car_pre20_m2_mm |

## Alternative AIActive Lag / Source Definitions

| model                       | ai_def               |    coef |     se |      p |   nobs |   events |   peer_firms |
|:----------------------------|:---------------------|--------:|-------:|-------:|-------:|---------:|-------------:|
| ai_def_ext_any              | ext_any              | -0.0021 | 0.0009 | 0.0245 |   8649 |     2415 |         3566 |
| ai_def_ext_any_hiring180    | ext_any_hiring180    | -0.0025 | 0.0011 | 0.024  |   8649 |     2415 |         3566 |
| ai_def_ext_ai_hiring_ge3    | ext_ai_hiring_ge3    | -0.0015 | 0.0014 | 0.27   |   8649 |     2415 |         3566 |
| ai_def_ext_no_hiring        | ext_no_hiring        | -0.0078 | 0.003  | 0.0095 |   8649 |     2415 |         3566 |
| ai_def_ext_genai_any        | ext_genai_any        |  0.0001 | 0.0015 | 0.9396 |   8649 |     2415 |         3566 |
| ai_def_ext_plus_history     | ext_plus_history     | -0.0023 | 0.0009 | 0.0109 |   8649 |     2415 |         3566 |
| ai_def_current_text_history | current_text_history | -0.002  | 0.001  | 0.0357 |   8649 |     2415 |         3566 |

## Mechanical Summary

- ext_any negative at p < 0.10 in 29 of 40 diagnostic specifications.
- text-history negative at p < 0.10 in 27 of 40 diagnostic specifications.

## Interpretation Rules

1. If the coefficient only survives untrimmed / unwinsorized Y, the result is
   outlier-sensitive.
2. If it only survives `PeerCAR[0,+1]` but not adjacent windows, the event-time
   interpretation should stay short-window and cautious.
3. If it disappears under rank / log specificity transformations, the X is
   scale-sensitive.
4. If it disappears under stricter source-lag AIActive definitions, the
   external AIActive claim should be softened.

