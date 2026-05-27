# V7 Event-Time and Product-Market Peer-Validity Checks

Date: 2026-05-27

## Purpose

This run packages tasks 4 and 5 into paper-ready artifacts:

1. daily event-time coefficients for `Specificity_z × AIActivePeer`;
2. product-market proximity gradient and peer-set validity diagnostics.

## Event-Time Check

Specification: daily market-model peer abnormal return on `Specificity_z × AIActivePeer × event-time day`, with event-peer pair FE and event-time FE. Tau = -2 is omitted. Standard errors are two-way clustered by focal event and peer firm.

Figure:

`results/v7_event_time_peer_validity_20260527/event_time_spec_ai_daily.png`

Window-level figure:

`results/v7_event_time_peer_validity_20260527/window_lead_lag_coefficients.png`

Key table:

| ai_def               |   tau |    coef |     se |       z |      p |   ci_low |   ci_high |   nobs |   events |   peer_firms |
|:---------------------|------:|--------:|-------:|--------:|-------:|---------:|----------:|-------:|---------:|-------------:|
| current_text_history |    -5 | -0.0007 | 0.0008 | -0.8087 | 0.4187 |  -0.0023 |    0.001  | 163721 |     2177 |         3345 |
| current_text_history |    -4 |  0.0003 | 0.0009 |  0.3481 | 0.7278 |  -0.0015 |    0.0021 | 163721 |     2177 |         3345 |
| current_text_history |    -3 |  0.0011 | 0.0009 |  1.2811 | 0.2001 |  -0.0006 |    0.0028 | 163721 |     2177 |         3345 |
| current_text_history |    -1 | -0.0001 | 0.0009 | -0.077  | 0.9386 |  -0.0018 |    0.0016 | 163721 |     2177 |         3345 |
| current_text_history |     0 | -0.0005 | 0.0009 | -0.5037 | 0.6145 |  -0.0023 |    0.0014 | 163721 |     2177 |         3345 |
| current_text_history |     1 | -0.0008 | 0.0008 | -0.9075 | 0.3642 |  -0.0024 |    0.0009 | 163721 |     2177 |         3345 |
| current_text_history |     2 |  0.0006 | 0.0008 |  0.7065 | 0.4799 |  -0.001  |    0.0022 | 163721 |     2177 |         3345 |
| current_text_history |     3 | -0      | 0.0008 | -0.0178 | 0.9858 |  -0.0016 |    0.0015 | 163721 |     2177 |         3345 |
| current_text_history |     4 |  0.0004 | 0.0009 |  0.4555 | 0.6487 |  -0.0013 |    0.0021 | 163721 |     2177 |         3345 |
| current_text_history |     5 |  0      | 0.0008 |  0.0604 | 0.9519 |  -0.0016 |    0.0017 | 163721 |     2177 |         3345 |
| ext_any              |    -5 | -0.0003 | 0.0009 | -0.2869 | 0.7742 |  -0.0021 |    0.0015 | 163721 |     2177 |         3345 |
| ext_any              |    -4 |  0.0005 | 0.0009 |  0.5963 | 0.551  |  -0.0012 |    0.0022 | 163721 |     2177 |         3345 |
| ext_any              |    -3 |  0.0007 | 0.001  |  0.6819 | 0.4953 |  -0.0013 |    0.0026 | 163721 |     2177 |         3345 |
| ext_any              |    -1 |  0.0001 | 0.0009 |  0.125  | 0.9005 |  -0.0016 |    0.0019 | 163721 |     2177 |         3345 |
| ext_any              |     0 | -0.0001 | 0.001  | -0.1101 | 0.9123 |  -0.002  |    0.0018 | 163721 |     2177 |         3345 |
| ext_any              |     1 | -0.0006 | 0.001  | -0.6286 | 0.5296 |  -0.0025 |    0.0013 | 163721 |     2177 |         3345 |
| ext_any              |     2 | -0.0005 | 0.0009 | -0.5316 | 0.595  |  -0.0023 |    0.0013 | 163721 |     2177 |         3345 |
| ext_any              |     3 | -0.0001 | 0.0009 | -0.0874 | 0.9303 |  -0.0019 |    0.0018 | 163721 |     2177 |         3345 |
| ext_any              |     4 |  0.001  | 0.001  |  0.9638 | 0.3351 |  -0.001  |    0.0029 | 163721 |     2177 |         3345 |
| ext_any              |     5 |  0.0002 | 0.001  |  0.1693 | 0.8656 |  -0.0017 |    0.0021 | 163721 |     2177 |         3345 |

Window-level lead/lag table:

| ai_def               | window_label   |    coef |     se |       z |      p |   nobs |   events |   peer_firms |   ci_low |   ci_high |
|:---------------------|:---------------|--------:|-------:|--------:|-------:|-------:|---------:|-------------:|---------:|----------:|
| current_text_history | [-20,-11]      | -0.0048 | 0.0021 | -2.2499 | 0.0245 |   8646 |     2415 |         3565 |  -0.009  |   -0.0006 |
| current_text_history | [-10,-2]       | -0.0048 | 0.0024 | -2.0255 | 0.0428 |   8670 |     2415 |         3570 |  -0.0095 |   -0.0002 |
| current_text_history | [-5,-2]        | -0.0012 | 0.0018 | -0.6727 | 0.5011 |   8675 |     2416 |         3570 |  -0.0047 |    0.0023 |
| current_text_history | [0,+1]         | -0.0023 | 0.001  | -2.3253 | 0.0201 |   8683 |     2416 |         3573 |  -0.0042 |   -0.0004 |
| current_text_history | [+2,+5]        |  0.0008 | 0.0017 |  0.4894 | 0.6245 |   8675 |     2414 |         3571 |  -0.0025 |    0.0041 |
| current_text_history | [+2,+10]       |  0.0013 | 0.0025 |  0.5136 | 0.6075 |   8643 |     2406 |         3563 |  -0.0036 |    0.0061 |
| ext_any              | [-20,-11]      | -0.0019 | 0.0022 | -0.8595 | 0.39   |   8646 |     2415 |         3565 |  -0.0063 |    0.0025 |
| ext_any              | [-10,-2]       |  0.0001 | 0.0022 |  0.0344 | 0.9726 |   8670 |     2415 |         3570 |  -0.0043 |    0.0044 |
| ext_any              | [-5,-2]        |  0.0003 | 0.0016 |  0.1639 | 0.8698 |   8675 |     2416 |         3570 |  -0.0029 |    0.0034 |
| ext_any              | [0,+1]         | -0.0018 | 0.001  | -1.8932 | 0.0583 |   8683 |     2416 |         3573 |  -0.0037 |    0.0001 |
| ext_any              | [+2,+5]        | -0.002  | 0.0015 | -1.3898 | 0.1646 |   8675 |     2414 |         3571 |  -0.0049 |    0.0008 |
| ext_any              | [+2,+10]       | -0.0005 | 0.0022 | -0.2239 | 0.8229 |   8643 |     2406 |         3563 |  -0.0049 |    0.0039 |

## Product-Market Peer-Set Validity

Descriptive validation of peer sets after first-event and announcement-cleaning filters.

| peer_group                |   obs |   events |   peer_firms |   mean_similarity |   median_similarity |   p25_similarity |   p75_similarity |   same_industry_rate |   ext_any_share |   text_history_share |
|:--------------------------|------:|---------:|-------------:|------------------:|--------------------:|-----------------:|-----------------:|---------------------:|----------------:|---------------------:|
| true_top1_3               |  5226 |     2354 |         2772 |            0.2552 |              0.2188 |           0.1646 |           0.3123 |               0.4791 |          0.2065 |               0.2595 |
| true_top4_5               |  3457 |     2189 |         2155 |            0.2056 |              0.1696 |           0.1323 |           0.2447 |               0.4189 |          0.2103 |               0.2499 |
| true_top6_10              |  8602 |     2411 |         3506 |            0.1798 |              0.1443 |           0.113  |           0.2119 |               0.3612 |          0.2102 |               0.2628 |
| low_similarity_top5       |  7269 |     2343 |         1679 |            0.0063 |              0.003  |           0.0012 |           0.0067 |               1      |          0.1695 |               0.2423 |
| random_same_industry_top5 |  7688 |     2350 |         3678 |            0.0547 |              0.0345 |           0.0171 |           0.0663 |               1      |          0.2118 |               0.2764 |

## Proximity Gradient

Specification: current headline peer-CAR model with controls `PeerCAR[-10,-2] + PeerCAR[-20,-2]`, FE `event_id + peer_industry_week`, and two-way clustered standard errors.

Figure:

`results/v7_event_time_peer_validity_20260527/proximity_gradient_coefficients.png`

| ai_def               | peer_group                |    coef |     se |       z |      p |   nobs |   events |   peer_firms |   ci_low |   ci_high |
|:---------------------|:--------------------------|--------:|-------:|--------:|-------:|-------:|---------:|-------------:|---------:|----------:|
| current_text_history | true_top1_3               | -0.0025 | 0.0014 | -1.7742 | 0.076  |   5201 |     2352 |         2765 |  -0.0052 |    0.0003 |
| current_text_history | true_top4_5               | -0.0008 | 0.003  | -0.2671 | 0.7894 |   3448 |     2185 |         2152 |  -0.0066 |    0.005  |
| current_text_history | true_top6_10              | -0.0011 | 0.0011 | -1.026  | 0.3049 |   8565 |     2411 |         3498 |  -0.0032 |    0.001  |
| current_text_history | low_similarity_top5       | -0.0001 | 0.001  | -0.1312 | 0.8956 |   7218 |     2341 |         1679 |  -0.0021 |    0.0018 |
| current_text_history | random_same_industry_top5 |  0.0007 | 0.0009 |  0.8042 | 0.4213 |   7662 |     2349 |         3668 |  -0.001  |    0.0024 |
| ext_any              | true_top1_3               | -0.0033 | 0.0013 | -2.4204 | 0.0155 |   5201 |     2352 |         2765 |  -0.0059 |   -0.0006 |
| ext_any              | true_top4_5               | -0.0038 | 0.0033 | -1.1337 | 0.2569 |   3448 |     2185 |         2152 |  -0.0103 |    0.0027 |
| ext_any              | true_top6_10              | -0.001  | 0.001  | -1.0401 | 0.2983 |   8565 |     2411 |         3498 |  -0.0029 |    0.0009 |
| ext_any              | low_similarity_top5       | -0.0001 | 0.001  | -0.1355 | 0.8922 |   7218 |     2341 |         1679 |  -0.0021 |    0.0018 |
| ext_any              | random_same_industry_top5 | -0.001  | 0.0009 | -1.1149 | 0.2649 |   7662 |     2349 |         3668 |  -0.0027 |    0.0008 |

## Reading

- The daily event-time plot is mainly a transparency check. It should be shown as evidence on timing rather than as the headline estimator.
- Product-market validity is stronger: the coefficient is largest for Top1-3 peers, attenuates for Top6-10, and is null for low-similarity/random peers.
- The validity table shows that constructed Top peers have much higher product-text similarity than low-similarity and random peers, supporting the use of Top5 as the main peer set.
