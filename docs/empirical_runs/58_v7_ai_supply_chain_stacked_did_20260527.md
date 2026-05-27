# V7 AI Supply-Chain Disclosure Stacked Event-DID

Date: 2026-05-27

## Purpose

This run tests a DID-style version of the AI supply-chain branch:

`DailyPeerAR_{j,tau} = beta * AI_supply_chain_event_i * Post[0,+1] + pair FE + event-time FE + error`

The treatment is focal-event level. The outcome is peer daily market-model abnormal return. The primary window is trading days `[-10,+1]`, where `Post[0,+1]` equals one on event day and the next trading day. Standard errors are two-way clustered by focal event and peer firm through the existing v6 regression utility.

This is a diagnostic, not the headline v6 `Specificity_z x AIActivePeer` design.

## Sample

| panel                        |   daily_obs |   event_peer_pairs |   events |   peer_firms |   treated_events |   treated_pair_share |   mean_daily_abret |
|:-----------------------------|------------:|-------------------:|---------:|-------------:|-----------------:|---------------------:|-------------------:|
| true_top5                    |      163721 |               7805 |     2177 |         3345 |              301 |               0.1338 |            -0.0006 |
| low_similarity_same_industry |      136252 |               6507 |     2093 |         1590 |              292 |               0.1371 |            -0.0009 |

## Main DID Results

`coef` is the daily abnormal-return effect on `Post[0,+1]`. `two_day_equivalent` is `2 * coef`, roughly comparable to a two-day CAR effect.

| model                                              | term                   |    coef |     se |       z |      p |   two_day_equivalent |   nobs |   events |   peer_firms | fe                      |
|:---------------------------------------------------|:-----------------------|--------:|-------:|--------:|-------:|---------------------:|-------:|---------:|-------------:|:------------------------|
| top5_pair_tau_fe                                   | supply_post01          |  0.0006 | 0.0009 |  0.698  | 0.4852 |               0.0012 |  93660 |     2177 |         3345 | pair_id+tau_fe          |
| top5_pair_tau_calendar_date_fe                     | supply_post01          | -0.0001 | 0.0007 | -0.125  | 0.9005 |              -0.0002 |  93660 |     2177 |         3345 | pair_id+tau_fe+date_str |
| pretrend_placebo_m5_m2_pair_tau_fe                 | supply_fake_post_m5_m2 | -0.0004 | 0.0008 | -0.4807 | 0.6307 |             nan      |  70245 |     2177 |         3345 | pair_id+tau_fe          |
| pretrend_placebo_m5_m2_pair_tau_calendar_date_fe   | supply_fake_post_m5_m2 | -0.0002 | 0.0007 | -0.2895 | 0.7722 |             nan      |  70245 |     2177 |         3345 | pair_id+tau_fe+date_str |
| ddd_true_top5_vs_low_sim_pair_tau_fe               | supply_true_post01     |  0      | 0.001  |  0.0456 | 0.9637 |               0.0001 | 171514 |     2177 |         3857 | pair_id+tau_fe          |
| ddd_true_top5_vs_low_sim_pair_tau_calendar_date_fe | supply_true_post01     |  0      | 0.001  |  0.0327 | 0.9739 |               0.0001 | 171514 |     2177 |         3857 | pair_id+tau_fe+date_str |
| low_sim_pair_tau_fe                                | supply_post01          |  0.0006 | 0.0009 |  0.6334 | 0.5265 |               0.0011 |  77854 |     2093 |         1590 | pair_id+tau_fe          |
| low_sim_pair_tau_calendar_date_fe                  | supply_post01          | -0.0004 | 0.0007 | -0.5079 | 0.6115 |              -0.0007 |  77854 |     2093 |         1590 | pair_id+tau_fe+date_str |

## Dynamic Lead-Lag Check

Coefficients are `AI_supply_chain_event x event_time_tau`, with tau = -2 as the omitted base day, pair FE and event-time FE.

|   tau |    coef |     se |       z |      p |   nobs |   events |   peer_firms |
|------:|--------:|-------:|--------:|-------:|-------:|---------:|-------------:|
|   -10 | -0.0007 | 0.0015 | -0.4223 | 0.6728 | 163721 |     2177 |         3345 |
|    -9 |  0.0012 | 0.0016 |  0.7411 | 0.4586 | 163721 |     2177 |         3345 |
|    -8 |  0      | 0.0016 |  0.0125 | 0.99   | 163721 |     2177 |         3345 |
|    -7 | -0.0009 | 0.0015 | -0.5759 | 0.5647 | 163721 |     2177 |         3345 |
|    -6 |  0.0001 | 0.0015 |  0.0695 | 0.9446 | 163721 |     2177 |         3345 |
|    -5 | -0.0018 | 0.0015 | -1.1824 | 0.237  | 163721 |     2177 |         3345 |
|    -4 |  0.0002 | 0.0016 |  0.1333 | 0.8939 | 163721 |     2177 |         3345 |
|    -3 | -0.0001 | 0.0016 | -0.0452 | 0.964  | 163721 |     2177 |         3345 |
|    -1 |  0.0005 | 0.0015 |  0.307  | 0.7589 | 163721 |     2177 |         3345 |
|     0 |  0.0004 | 0.0015 |  0.2822 | 0.7778 | 163721 |     2177 |         3345 |
|     1 |  0.0005 | 0.0016 |  0.3126 | 0.7546 | 163721 |     2177 |         3345 |
|     2 |  0.0004 | 0.0014 |  0.3055 | 0.76   | 163721 |     2177 |         3345 |
|     3 |  0.002  | 0.0016 |  1.2732 | 0.203  | 163721 |     2177 |         3345 |
|     4 | -0.0013 | 0.0015 | -0.8751 | 0.3815 | 163721 |     2177 |         3345 |
|     5 | -0.0013 | 0.0016 | -0.8642 | 0.3875 | 163721 |     2177 |         3345 |
|     6 | -0.0007 | 0.0015 | -0.4457 | 0.6558 | 163721 |     2177 |         3345 |
|     7 | -0.0026 | 0.0016 | -1.6775 | 0.0934 | 163721 |     2177 |         3345 |
|     8 | -0.0009 | 0.0015 | -0.5959 | 0.5513 | 163721 |     2177 |         3345 |
|     9 | -0.0002 | 0.0014 | -0.1626 | 0.8708 | 163721 |     2177 |         3345 |
|    10 |  0.0023 | 0.0015 |  1.5391 | 0.1238 | 163721 |     2177 |         3345 |

## Interpretation Guide

- A positive and significant Top5 DID coefficient means AI supply-chain GenAI disclosures are followed by positive close-peer abnormal returns relative to the same pair's pre-event days.
- A null pretrend placebo is required for a defensible DID interpretation.
- A positive Top5 result that does not appear in low-similarity peers supports a product-market network interpretation.
- A weak or wrong-signed DDD means the result is closer to broad category validation than a close-competitor-specific effect.
