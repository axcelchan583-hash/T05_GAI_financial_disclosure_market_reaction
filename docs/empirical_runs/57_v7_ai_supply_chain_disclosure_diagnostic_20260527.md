# V7 AI Supply-Chain Disclosure Diagnostic

Date: 2026-05-27

Purpose: test whether the existing `Specificity_z` signal is closer to AI supply-chain exposure disclosure than to own GenAI implementation specificity.

## Manual 300-Row Diagnostic

```text
                         group   n  mean_specificity_z  mean_claude_score  mean_agent1_score
      ai_supply_chain_exposure  36           -0.262661           1.111111           2.222222
own_genai_implementation_regex 218            0.259792           0.963303           1.344037
    generic_ai_attention_regex  29           -0.101708           0.655172           1.172414
       denial_no_current_regex  34           -0.089698           0.058824           0.117647
                all_manual_300 300            0.155180           0.793333           1.170000
```

## Correlations in Manual 300 Sample

```text
                             x                    y   n   pearson  spearman
      ai_supply_chain_exposure        specificity_z 300 -0.123007 -0.127075
      ai_supply_chain_exposure          specificity 300 -0.122190 -0.127074
      ai_supply_chain_exposure total_specific_items 300  0.023713  0.053709
      ai_supply_chain_exposure         claude_score 300  0.094035  0.084603
      ai_supply_chain_exposure         agent1_score 300  0.241543  0.252118
own_genai_implementation_regex        specificity_z 300  0.135980  0.198483
own_genai_implementation_regex          specificity 300  0.122086  0.198524
own_genai_implementation_regex total_specific_items 300  0.173352  0.244610
own_genai_implementation_regex         claude_score 300  0.222079  0.234965
own_genai_implementation_regex         agent1_score 300  0.176400  0.172383
    generic_ai_attention_regex        specificity_z 300 -0.066993 -0.083754
    generic_ai_attention_regex          specificity 300 -0.068577 -0.083754
    generic_ai_attention_regex total_specific_items 300 -0.068554 -0.070030
    generic_ai_attention_regex         claude_score 300 -0.036217 -0.019236
    generic_ai_attention_regex         agent1_score 300  0.000491  0.018538
       denial_no_current_regex        specificity_z 300 -0.069794 -0.102679
       denial_no_current_regex          specificity 300 -0.055947 -0.102495
       denial_no_current_regex total_specific_items 300 -0.157227 -0.242712
       denial_no_current_regex         claude_score 300 -0.210432 -0.234537
       denial_no_current_regex         agent1_score 300 -0.233882 -0.239079
          supply_subtype_count        specificity_z 300 -0.127393 -0.173371
          supply_subtype_count          specificity 300 -0.127565 -0.173754
          supply_subtype_count total_specific_items 300  0.000853 -0.005278
          supply_subtype_count         claude_score 300 -0.010110  0.032630
          supply_subtype_count         agent1_score 300  0.172295  0.214687
```

## Event-Level Prevalence

```text
                  sample  events  supply_events  supply_share  own_impl_regex_events  denial_events
        all_focal_events   20165           5386      0.267096                  14349            825
headline_analysis_events    2177            301      0.138264                   1526            251
```

## Peer-CAR Regressions

All regressions use the current headline Top5 sample, announcement-cleaned rows, `PeerCAR[0,+1]`, event FE + peer industry-week FE, two-way clustered by event and peer firm. Controls include `PeerCAR[-10,-2]` and `PeerCAR[-20,-2]`.

```text
                                                model      term      coef       se         z        p  nobs  events  peer_firms                           xvar               ai_def                                             controls
                              specificity_z_x_ext_any      x_ai -0.002303 0.000992 -2.321121 0.020280  7805    2177        3345                  specificity_z              ext_any            peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
                   ai_supply_chain_exposure_x_ext_any      x_ai -0.001381 0.003733 -0.369916 0.711445  7805    2177        3345       ai_supply_chain_exposure              ext_any            peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
                     supply_subtype_count_z_x_ext_any      x_ai  0.002002 0.001565  1.279065 0.200874  7805    2177        3345         supply_subtype_count_z              ext_any            peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
             own_genai_implementation_regex_x_ext_any      x_ai -0.003239 0.002759 -1.173995 0.240397  7805    2177        3345 own_genai_implementation_regex              ext_any            peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
                    horse_race_specz_supply_x_ext_any   spec_ai -0.002342 0.000991 -2.362895 0.018133  7805    2177        3345                        spec_ai              ext_any peer_car_pre10_m2_mm|peer_car_pre20_m2_mm|horse_race
                    horse_race_specz_supply_x_ext_any supply_ai -0.001936 0.003728 -0.519402 0.603480  7805    2177        3345                      supply_ai              ext_any peer_car_pre10_m2_mm|peer_car_pre20_m2_mm|horse_race
                 specificity_z_x_current_text_history      x_ai -0.002275 0.001030 -2.208437 0.027214  7805    2177        3345                  specificity_z current_text_history            peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
      ai_supply_chain_exposure_x_current_text_history      x_ai -0.000057 0.003673 -0.015653 0.987511  7805    2177        3345       ai_supply_chain_exposure current_text_history            peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
        supply_subtype_count_z_x_current_text_history      x_ai  0.000250 0.001384  0.180606 0.856677  7805    2177        3345         supply_subtype_count_z current_text_history            peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
own_genai_implementation_regex_x_current_text_history      x_ai -0.000300 0.002894 -0.103662 0.917438  7805    2177        3345 own_genai_implementation_regex current_text_history            peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
       horse_race_specz_supply_x_current_text_history   spec_ai -0.002326 0.001046 -2.222591 0.026243  7805    2177        3345                        spec_ai current_text_history peer_car_pre10_m2_mm|peer_car_pre20_m2_mm|horse_race
       horse_race_specz_supply_x_current_text_history supply_ai -0.001246 0.003709 -0.336000 0.736871  7805    2177        3345                      supply_ai current_text_history peer_car_pre10_m2_mm|peer_car_pre20_m2_mm|horse_race
```

## Event-Level Supply-Chain Disclosure Regressions

These regressions estimate the average Top5 peer revaluation effect of event-level supply-chain exposure. They do not include event FE because the supply-chain variable is focal-event-level. They instead use calendar-week or focal-industry-week controls plus peer industry-week FE, with the same two-way event/peer clustering.

```text
                                                         model                     term      coef       se         z        p  nobs  events  peer_firms                                fe_spec                                  controls
                           supply_main_week_peer_industry_week ai_supply_chain_exposure  0.004257 0.001747  2.437159 0.014803  7805    2177        3345          event_week+peer_industry_week peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
                            specz_main_week_peer_industry_week            specificity_z -0.000133 0.000473 -0.281681 0.778188  7805    2177        3345          event_week+peer_industry_week peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
               horse_race_supply_specz_week_peer_industry_week ai_supply_chain_exposure  0.004250 0.001748  2.430544 0.015076  7805    2177        3345          event_week+peer_industry_week peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
               horse_race_supply_specz_week_peer_industry_week            specificity_z -0.000022 0.000473 -0.047131 0.962409  7805    2177        3345          event_week+peer_industry_week peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
            supply_main_focal_industry_week_peer_industry_week ai_supply_chain_exposure  0.003904 0.001838  2.123515 0.033711  7805    2177        3345 focal_industry_week+peer_industry_week peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
             specz_main_focal_industry_week_peer_industry_week            specificity_z -0.000066 0.000569 -0.115981 0.907668  7805    2177        3345 focal_industry_week+peer_industry_week peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
horse_race_supply_specz_focal_industry_week_peer_industry_week ai_supply_chain_exposure  0.003928 0.001831  2.145811 0.031888  7805    2177        3345 focal_industry_week+peer_industry_week peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
horse_race_supply_specz_focal_industry_week_peer_industry_week            specificity_z  0.000061 0.000569  0.107122 0.914692  7805    2177        3345 focal_industry_week+peer_industry_week peer_car_pre10_m2_mm|peer_car_pre20_m2_mm
```

## Supply-Chain Examples

```text
validation_id company_name event_date specificity_bin  specificity_z  claude_score  agent1_score
       SV0235         中国交建 2025-02-13            high       2.525772             4             4
       SV0283         澳弘电子 2025-04-03            high       2.419382             0             0
       SV0297         北京银行 2025-10-20            high       1.033834             4             4
       SV0280         中国石化 2025-04-02            high       1.006959             3             4
       SV0140         雅克科技 2025-02-19             mid       0.371369             0             0
       SV0199          NaN 2025-08-25             mid       0.371369             0             2
       SV0194          NaN 2024-12-20             mid       0.322564             0             3
       SV0112          易华录 2023-02-17             mid       0.266641             1             4
       SV0106         中京电子 2023-02-06             mid       0.036240             0             0
       SV0191          NaN 2023-09-08             mid       0.018601             0             4
       SV0183         中孚实业 2025-12-24             mid       0.018601             3             4
       SV0120         苏大维格 2023-04-12             mid      -0.107387             0             1
       SV0167         皖仪科技 2025-03-20             mid      -0.121468             3             4
       SV0145         高测股份 2025-02-19             mid      -0.194578             0             0
       SV0147          飞荣达 2025-02-20             mid      -0.240375             0             4
       SV0128         铁建重工 2024-05-16             mid      -0.273110             1             2
       SV0200         华如科技 2023-06-13             mid      -0.335366             1             4
       SV0132         镇海股份 2024-12-17             mid      -0.373363             0             0
       SV0118         法本信息 2023-03-23             mid      -0.395452             1             2
       SV0186          NaN 2023-04-18             mid      -0.437564             0             2
       SV0024         韦尔股份 2023-03-17             low      -0.515738             0             0
       SV0094          NaN 2025-04-29             low      -0.542620             0             0
       SV0095          NaN 2025-05-16             low      -0.559546             0             0
       SV0067          一心堂 2025-04-29             low      -0.559546             3             4
       SV0065         春秋电子 2025-03-07             low      -0.559546             0             2
       SV0074          NaN 2023-02-02             low      -0.767457             0             2
       SV0091          NaN 2024-10-14             low      -0.825521             0             2
       SV0098          NaN 2026-05-08             low      -0.923449             3             4
       SV0081          NaN 2023-07-01             low      -0.985107             0             2
       SV0087          NaN 2024-05-15             low      -1.304278             0             0
```

## Initial Interpretation

This diagnostic separates two constructs:

1. `own_genai_implementation_regex`: focal firm says it deploys, connects, develops, or uses GenAI / large-model systems itself.
2. `ai_supply_chain_exposure`: focal firm links GenAI / large-model demand to its hardware, compute, data-center, optical, semiconductor, cooling, AIPC, or data-resource products.

If `ai_supply_chain_exposure × AIActivePeer` explains peer CAR better than original `Specificity_z × AIActivePeer`, the paper should pivot toward AI supply-chain exposure disclosure. If it does not, keep this only as a measurement diagnostic and do not rewrite the study around it.
