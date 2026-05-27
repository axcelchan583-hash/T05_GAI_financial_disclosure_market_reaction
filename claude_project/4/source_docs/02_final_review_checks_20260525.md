# v6 Final Review Checks

Date: 2026-05-25

## Purpose

This run implements the post-review go/no-go checks: headline peer-CAR with pre-window controls, specificity validation, product-market proximity gradient, lead/lag windows, external AIActive breakdown, and peer disclosure diffusion mechanism.

## Executive Read

The capital-market main effect passes the current go/no-go bar, but the peer-disclosure diffusion mechanism does not pass the stricter version used here.

Main takeaways:

- The headline Top5 result survives pre-window CAR controls and strong fixed effects. With `event FE + peer industry-week FE`, the coefficient on `Specificity_z × AIActivePeer` is `-0.002025` for text-history AIActive (`p = 0.036`) and `-0.002109` for external `ext_any` (`p = 0.024`).
- The Top10 result is also stable, especially under external `ext_any` (`coef = -0.001573`, `p = 0.010`).
- Specificity is not mechanically captured by obvious text observables. The main result survives controls for answer/question length, AI keyword intensity, source/attention proxies, numeric/component proxies, and all observable text controls together.
- Product-market proximity supports the competitive-proximity interpretation: the result is strongest for Top1-3 peers, weaker or null for Top6-10, and null for low-similarity / random same-industry peers.
- Lead/lag evidence remains mixed. Text-history AIActive has longer pre-window concerns, while external `ext_any` does not show the same pre-window pattern. This supports using `ext_any` side-by-side with text-history in main tables and keeping pre-window CAR controls in headline specifications.
- External AIActive evidence is useful, but not every component is equally clean. `prior_ai_patent_grant`, `ext_no_hiring`, and `ext_any` support the main direction; `prior_cac` is too sparse/noisy as a standalone moderator.
- The stricter peer-disclosure diffusion mechanism table is null after focal-event FE and a baseline peer GenAI-disclosure-rate control. Therefore, peer disclosure diffusion should be framed only as descriptive / supplementary evidence from earlier smoke tests, not as a core mechanism claim.

Safe interpretation:

> More specific focal GenAI disclosures are associated with more negative short-window revaluation among AI-active close product-market peers. The result is best written as capital-market reassessment of competitive risk, not as strong causal evidence of business stealing or real competitive displacement.

## 1. Headline Peer-CAR Results with Pre-Window Controls

```text
sample               ai_def      coef       se         z        p  nobs  events  peer_firms
  top5 current_text_history -0.002025 0.000964 -2.100351 0.035698  8649    2415        3566
  top5              ext_any -0.002109 0.000938 -2.249259 0.024496  8649    2415        3566
  top5     ext_plus_history -0.002265 0.000890 -2.544589 0.010941  8649    2415        3566
 top10 current_text_history -0.001393 0.000653 -2.134524 0.032800 17214    2432        4507
 top10              ext_any -0.001573 0.000613 -2.568568 0.010212 17214    2432        4507
 top10     ext_plus_history -0.001529 0.000598 -2.558915 0.010500 17214    2432        4507
```

## 2. Specificity Validation Regressions

```text
              ai_def                  control_spec      coef       se         z        p  nobs  events
current_text_history                      baseline -0.002025 0.000964 -2.100351 0.035698  8649    2415
current_text_history               length_question -0.001737 0.001000 -1.737229 0.082347  8649    2415
current_text_history          ai_keyword_intensity -0.002014 0.000979 -2.057370 0.039651  8649    2415
current_text_history              attention_source -0.002057 0.000970 -2.121132 0.033911  8649    2415
current_text_history             numeric_component -0.001901 0.000970 -1.958933 0.050121  8649    2415
current_text_history full_observable_text_controls -0.001824 0.001012 -1.803144 0.071366  8649    2415
             ext_any                      baseline -0.002109 0.000938 -2.249259 0.024496  8649    2415
             ext_any               length_question -0.002180 0.000956 -2.278944 0.022670  8649    2415
             ext_any          ai_keyword_intensity -0.002096 0.000943 -2.223155 0.026205  8649    2415
             ext_any              attention_source -0.002007 0.000940 -2.134728 0.032783  8649    2415
             ext_any             numeric_component -0.002097 0.000936 -2.239730 0.025108  8649    2415
             ext_any full_observable_text_controls -0.002246 0.000971 -2.312283 0.020762  8649    2415
```

## 3. Product-Market Proximity Gradient

```text
               peer_group               ai_def      coef       se         z        p  nobs  events  peer_firms
              true_top1_3 current_text_history -0.002472 0.001393 -1.774196 0.076031  5201    2352        2765
              true_top1_3              ext_any -0.003252 0.001344 -2.420381 0.015504  5201    2352        2765
              true_top4_5 current_text_history -0.000796 0.002980 -0.267125 0.789373  3448    2185        2152
              true_top4_5              ext_any -0.003756 0.003313 -1.133743 0.256903  3448    2185        2152
             true_top6_10 current_text_history -0.001092 0.001064 -1.025974 0.304904  8565    2411        3498
             true_top6_10              ext_any -0.001010 0.000971 -1.040127 0.298281  8565    2411        3498
      low_similarity_top5 current_text_history -0.000131 0.001002 -0.131239 0.895586  7218    2341        1679
      low_similarity_top5              ext_any -0.000136 0.001004 -0.135546 0.892180  7218    2341        1679
random_same_industry_top5 current_text_history  0.000704 0.000876  0.804233 0.421262  7662    2349        3668
random_same_industry_top5              ext_any -0.000990 0.000888 -1.114904 0.264891  7662    2349        3668
```

## 4. Lead/Lag Window Checks

```text
               window               ai_def      coef       se         z        p  nobs  events
peer_car_pre20_m11_mm current_text_history -0.004816 0.002141 -2.249860 0.024458  8646    2415
 peer_car_pre10_m2_mm current_text_history -0.004847 0.002393 -2.025534 0.042813  8670    2415
  peer_car_pre5_m2_mm current_text_history -0.001197 0.001780 -0.672726 0.501121  8675    2416
     peer_car_0_p1_mm current_text_history -0.002298 0.000988 -2.325282 0.020057  8683    2416
 peer_car_post2_p5_mm current_text_history  0.000821 0.001677  0.489443 0.624528  8675    2414
peer_car_post2_p10_mm current_text_history  0.001267 0.002466  0.513625 0.607514  8643    2406
peer_car_pre20_m11_mm              ext_any -0.001916 0.002229 -0.859528 0.390049  8646    2415
 peer_car_pre10_m2_mm              ext_any  0.000076 0.002212  0.034372 0.972580  8670    2415
  peer_car_pre5_m2_mm              ext_any  0.000266 0.001623  0.163928 0.869788  8675    2416
     peer_car_0_p1_mm              ext_any -0.001800 0.000951 -1.893203 0.058331  8683    2416
 peer_car_post2_p5_mm              ext_any -0.002042 0.001469 -1.389818 0.164584  8675    2414
peer_car_post2_p10_mm              ext_any -0.000502 0.002241 -0.223854 0.822871  8643    2406
```

## 5. External AIActive Breakdown

```text
         peer_group                        ai_def      coef       se         z        p  nobs  events
          true_top5                     prior_cac  0.001701 0.010197  0.166792 0.867534  8649    2415
          true_top5         prior_ai_patent_grant -0.009036 0.003246 -2.783982 0.005370  8649    2415
          true_top5 prior_broad_ai_hiring_365_ge1 -0.001709 0.000954 -1.790175 0.073426  8649    2415
          true_top5 prior_broad_ai_hiring_365_ge3 -0.000304 0.001421 -0.213802 0.830701  8649    2415
          true_top5                 ext_no_hiring -0.007829 0.003021 -2.591824 0.009547  8649    2415
          true_top5                       ext_any -0.002109 0.000938 -2.249259 0.024496  8649    2415
          true_top5                    ext_strict -0.001499 0.001359 -1.102987 0.270033  8649    2415
          true_top5              ext_plus_history -0.002265 0.000890 -2.544589 0.010941  8649    2415
         true_top10                     prior_cac  0.007858 0.007508  1.046615 0.295277 17214    2432
         true_top10         prior_ai_patent_grant -0.005211 0.001892 -2.753774 0.005891 17214    2432
         true_top10 prior_broad_ai_hiring_365_ge1 -0.001362 0.000594 -2.294497 0.021762 17214    2432
         true_top10 prior_broad_ai_hiring_365_ge3 -0.000551 0.000837 -0.658861 0.509985 17214    2432
         true_top10                 ext_no_hiring -0.003586 0.002041 -1.757129 0.078896 17214    2432
         true_top10                       ext_any -0.001573 0.000613 -2.568568 0.010212 17214    2432
         true_top10                    ext_strict -0.001011 0.000836 -1.208447 0.226875 17214    2432
         true_top10              ext_plus_history -0.001529 0.000598 -2.558915 0.010500 17214    2432
low_similarity_top5                     prior_cac -0.006669 0.002690 -2.478909 0.013179  7218    2341
low_similarity_top5         prior_ai_patent_grant -0.011048 0.003356 -3.291661 0.000996  7218    2341
low_similarity_top5 prior_broad_ai_hiring_365_ge1  0.000376 0.001032  0.363721 0.716066  7218    2341
low_similarity_top5 prior_broad_ai_hiring_365_ge3  0.000203 0.001213  0.167553 0.866935  7218    2341
low_similarity_top5                 ext_no_hiring -0.009689 0.002643 -3.665074 0.000247  7218    2341
low_similarity_top5                       ext_any -0.000136 0.001004 -0.135546 0.892180  7218    2341
low_similarity_top5                    ext_strict -0.001152 0.001282 -0.898975 0.368666  7218    2341
low_similarity_top5              ext_plus_history  0.000013 0.000885  0.014442 0.988478  7218    2341
```

## 6. Peer Disclosure Diffusion Mechanism

```text
 top_n  window_days      coef       se         z        p  nobs  events  response_rate  baseline_rate_mean
     5           60 -0.000580 0.007088 -0.081807 0.934800  9709    2586       0.122155            0.057678
     5           90  0.003968 0.008058  0.492427 0.622417  9697    2583       0.147984            0.057750
     5          180  0.001246 0.008678  0.143606 0.885812  9592    2547       0.183278            0.058278
    10           60 -0.005182 0.005178 -1.000845 0.316902 19334    2617       0.118444            0.056377
    10           90 -0.002572 0.005800 -0.443452 0.657439 19310    2613       0.143397            0.056396
    10          180 -0.003607 0.006104 -0.590857 0.554616 19103    2577       0.175051            0.056954
```

## Output Files

- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v6_final_review_checks_20260525/headline.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v6_final_review_checks_20260525/specificity_validation.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v6_final_review_checks_20260525/specificity_feature_correlations.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v6_final_review_checks_20260525/specificity_component_summary.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v6_final_review_checks_20260525/proximity_gradient.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v6_final_review_checks_20260525/lead_lag.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v6_final_review_checks_20260525/external_breakdown.csv`
- `/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v6_final_review_checks_20260525/mechanism.csv`
