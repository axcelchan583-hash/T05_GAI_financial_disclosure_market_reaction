# v48 GenAI Disclosure Text Feature Panel

Date: 2026-06-08

## Purpose

This run operationalizes the new disclosure-text design in `docs/design/重新构造X和Y/03_disclosure_text_feature_design_20260608.md`.

It is a machine-audit pass, not a final manual text-coding result. The text source is the v36 event title plus existing LLM reason/evidence snippets and keyword/backfill traces. It does not yet parse the full PDF body sentence by sentence.

## Verdict

The current rule-based text-feature indices do **not** replace the legacy `Specificity x AIActivePeer` mechanism.

- In the competitor panel, `CredibleImplementation x AIActivePeer` is not negative and is not significant.
- `StrategicEmbeddedness x AIActivePeer` is negative but weak and insignificant.
- The legacy `Spec x AIActivePeer` remains the only clean competitor text mechanism in this pass.
- Any `Denial` coefficient should be ignored because the feature has too few nonzero events.
- In the relationship stack, investment-linked partner interactions are positive in several windows but generally insignificant; the most useful signal is still the level/event-weighted investment-linked partner result from v47, not the v48 text interaction.

Interpretation: v48 is useful for building a manual validation sample and refining the codebook, but it is not yet evidence that the new composite text indices should become the main X.

## Event Text Feature Coverage

- Events with text features: 363
- Focal firms: 363
- Direct candidates: 298
- Keyword/backfill candidates: 65

## Text Feature Summary

| variable | n | mean | std | p25 | median | p75 | max |
|---|---|---|---|---|---|---|---|
| feature_text_len | 363.0 | 225.37741 | 80.517067 | 176.0 | 200.0 | 243.0 | 600.0 |
| feature_sentence_count | 363.0 | 12.969697 | 7.814964 | 8.0 | 10.0 | 14.0 | 68.0 |
| hard_info_count | 363.0 | 2.490358 | 2.156012 | 1.0 | 2.0 | 3.0 | 24.0 |
| implemented_action_count | 363.0 | 1.779614 | 2.052063 | 0.0 | 2.0 | 2.5 | 14.0 |
| commercialization_count | 363.0 | 0.867769 | 1.263221 | 0.0 | 0.0 | 1.0 | 8.0 |
| own_capability_count | 363.0 | 13.341598 | 7.016091 | 10.0 | 13.0 | 16.0 | 44.0 |
| named_partner_count | 363.0 | 1.090909 | 2.005517 | 0.0 | 0.0 | 2.0 | 25.0 |
| equity_tie_count | 363.0 | 1.030303 | 1.764182 | 0.0 | 0.0 | 2.0 | 10.0 |
| alliance_action_count | 363.0 | 1.002755 | 2.246543 | 0.0 | 0.0 | 1.0 | 23.0 |
| vague_future_count | 363.0 | 0.592287 | 1.045456 | 0.0 | 0.0 | 1.0 | 7.0 |
| denial_count | 363.0 | 0.002755 | 0.052486 | 0.0 | 0.0 | 0.0 | 1.0 |
| promotional_tone_count | 363.0 | 0.749311 | 1.390762 | 0.0 | 0.0 | 1.0 | 8.0 |
| ai_keyword_count | 363.0 | 11.460055 | 5.914252 | 7.0 | 10.0 | 14.0 | 40.0 |
| buzz_no_detail | 363.0 | 0.225895 | 0.418748 | 0.0 | 0.0 | 0.0 | 1.0 |
| credible_implementation_z | 363.0 | 0.0 | 1.00138 | -0.637169 | -0.100607 | 0.556376 | 4.133507 |
| strategic_embeddedness_z | 363.0 | -0.0 | 1.00138 | -0.762533 | -0.085845 | 0.667225 | 3.843533 |
| promotional_washing_z | 363.0 | -0.0 | 1.00138 | -0.776791 | -0.100417 | 0.593424 | 7.171333 |
| credible_minus_washing_z | 363.0 | -0.0 | 1.00138 | -0.63026 | 0.03105 | 0.669757 | 2.760818 |

## Competitor Mechanism: Text Feature x AIActivePeer

Specification:

`PeerCAR[0,+1] ~ AIActive + TextFeature x AIActive + PeerCAR[-10,-2] + PeerCAR[-20,-2] + event FE`

SE: two-way clustered by event and peer firm through the existing absorbed-OLS helper.

| model | term | coef_fmt | se | p | feature_nonzero_events | feature_source_warning | nobs | events | related_firms | r2 |
|---|---|---|---|---|---|---|---|---|---|---|
| single_credible_implementation_x_ai | credible_implementation_x_ai | 0.0005 | 0.00117 | 0.679553 | 363.0 |  | 2789.0 | 316.0 | 1384.0 | 0.480209 |
| single_strategic_embeddedness_x_ai | strategic_embeddedness_x_ai | -0.0011 | 0.001147 | 0.351152 | 363.0 |  | 2789.0 | 316.0 | 1384.0 | 0.480286 |
| single_promotional_washing_x_ai | promotional_washing_x_ai | 0.0004 | 0.001398 | 0.795016 | 363.0 |  | 2789.0 | 316.0 | 1384.0 | 0.480198 |
| single_credible_minus_washing_x_ai | credible_minus_washing_x_ai | 0.0001 | 0.001429 | 0.931664 | 363.0 |  | 2789.0 | 316.0 | 1384.0 | 0.480187 |
| single_hard_info_x_ai | hard_info_x_ai | 0.0006 | 0.001168 | 0.587615 | 363.0 |  | 2789.0 | 316.0 | 1384.0 | 0.480225 |
| single_implemented_action_x_ai | implemented_action_x_ai | 0.0005 | 0.001373 | 0.708893 | 236.0 |  | 2789.0 | 316.0 | 1384.0 | 0.480212 |
| single_named_partner_x_ai | named_partner_x_ai | -0.0015 | 0.001272 | 0.240074 | 172.0 |  | 2789.0 | 316.0 | 1384.0 | 0.480385 |
| single_equity_tie_x_ai | equity_tie_x_ai | 0.0004 | 0.001487 | 0.778926 | 130.0 |  | 2789.0 | 316.0 | 1384.0 | 0.480201 |
| single_vague_future_x_ai | vague_future_x_ai | -0.0002 | 0.001312 | 0.850194 | 129.0 |  | 2789.0 | 316.0 | 1384.0 | 0.480191 |
| single_denial_x_ai | denial_x_ai | 0.0012*** | 7.4e-05 | 0.0 | 1.0 | low_support_do_not_interpret | 2789.0 | 316.0 | 1384.0 | 0.480288 |
| single_ai_keyword_x_ai | ai_keyword_x_ai | 0.0011 | 0.001307 | 0.402839 | 363.0 |  | 2789.0 | 316.0 | 1384.0 | 0.480305 |
| benchmark_old_spec_x_ai | spec_ai | -0.0033*** | 0.001191 | 0.004929 | 363.0 |  | 2789.0 | 316.0 | 1384.0 | 0.481319 |

## Competitor Horse Race: Three Text Indices

| model | term | coef_fmt | se | p | nobs | events | related_firms | r2 |
|---|---|---|---|---|---|---|---|---|
| horse_three_indices_x_ai | horse_credible_implementation_x_ai | 0.0004 | 0.001192 | 0.746139 | 2789.0 | 316.0 | 1384.0 | 0.480315 |
| horse_three_indices_x_ai | horse_strategic_embeddedness_x_ai | -0.0010 | 0.001185 | 0.386582 | 2789.0 | 316.0 | 1384.0 | 0.480315 |
| horse_three_indices_x_ai | horse_promotional_washing_x_ai | 0.0004 | 0.001376 | 0.763624 | 2789.0 | 316.0 | 1384.0 | 0.480315 |

## Relationship Stacked Tests

Baseline is the product-market competitor panel. Event FE absorbs the focal GenAI event. The reported term is a relation-type indicator interacted with the event-level text feature.

| model | outcome | term | coef_fmt | se | p | feature_nonzero_events | feature_source_warning | nobs | events | related_firms | r2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| stack_credible_implementation_is_factset_partner_investment | peer_ar0_mm | partner_investment_x_credible_implementation | 0.0017 | 0.002364 | 0.479511 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.27232 |
| stack_credible_implementation_is_factset_partner_investment | peer_car_0_p1_mm | partner_investment_x_credible_implementation | 0.0018 | 0.002111 | 0.381485 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.284707 |
| stack_credible_implementation_is_factset_partner_investment | peer_car_m1_p1_mm | partner_investment_x_credible_implementation | 0.0031 | 0.00305 | 0.316384 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.255694 |
| stack_credible_implementation_is_factset_partner_high_confidence | peer_ar0_mm | partner_high_confidence_x_credible_implementation | -0.0023 | 0.001545 | 0.129008 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.272661 |
| stack_credible_implementation_is_factset_partner_high_confidence | peer_car_0_p1_mm | partner_high_confidence_x_credible_implementation | -0.0041** | 0.001802 | 0.022222 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.285222 |
| stack_credible_implementation_is_factset_partner_high_confidence | peer_car_m1_p1_mm | partner_high_confidence_x_credible_implementation | -0.0039* | 0.002105 | 0.065182 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.255972 |
| stack_strategic_embeddedness_is_factset_partner_investment | peer_ar0_mm | partner_investment_x_strategic_embeddedness | 0.0018 | 0.00129 | 0.157924 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.272327 |
| stack_strategic_embeddedness_is_factset_partner_investment | peer_car_0_p1_mm | partner_investment_x_strategic_embeddedness | 0.0010 | 0.002688 | 0.712979 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.284684 |
| stack_strategic_embeddedness_is_factset_partner_investment | peer_car_m1_p1_mm | partner_investment_x_strategic_embeddedness | -0.0004 | 0.00366 | 0.918069 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.255636 |
| stack_strategic_embeddedness_is_factset_partner_high_confidence | peer_ar0_mm | partner_high_confidence_x_strategic_embeddedness | 0.0007 | 0.00204 | 0.728587 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.272284 |
| stack_strategic_embeddedness_is_factset_partner_high_confidence | peer_car_0_p1_mm | partner_high_confidence_x_strategic_embeddedness | 0.0006 | 0.003017 | 0.849747 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.284682 |
| stack_strategic_embeddedness_is_factset_partner_high_confidence | peer_car_m1_p1_mm | partner_high_confidence_x_strategic_embeddedness | 0.0024 | 0.00329 | 0.46762 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.25571 |
| stack_promotional_washing_is_factset_partner_investment | peer_ar0_mm | partner_investment_x_promotional_washing | -0.0017 | 0.001936 | 0.393994 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.272305 |
| stack_promotional_washing_is_factset_partner_investment | peer_car_0_p1_mm | partner_investment_x_promotional_washing | -0.0016 | 0.003316 | 0.621173 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.284694 |
| stack_promotional_washing_is_factset_partner_investment | peer_car_m1_p1_mm | partner_investment_x_promotional_washing | -0.0072* | 0.00392 | 0.067467 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.255882 |
| stack_promotional_washing_is_factset_partner_high_confidence | peer_ar0_mm | partner_high_confidence_x_promotional_washing | -0.0001 | 0.001136 | 0.896775 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.272264 |
| stack_promotional_washing_is_factset_partner_high_confidence | peer_car_0_p1_mm | partner_high_confidence_x_promotional_washing | 0.0005 | 0.00192 | 0.807961 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.284682 |
| stack_promotional_washing_is_factset_partner_high_confidence | peer_car_m1_p1_mm | partner_high_confidence_x_promotional_washing | -0.0013 | 0.001793 | 0.479314 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.255666 |
| stack_credible_minus_washing_is_factset_partner_investment | peer_ar0_mm | partner_investment_x_credible_minus_washing | 0.0019 | 0.00217 | 0.378156 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.272341 |
| stack_credible_minus_washing_is_factset_partner_investment | peer_car_0_p1_mm | partner_investment_x_credible_minus_washing | 0.0020 | 0.002166 | 0.34959 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.284715 |
| stack_credible_minus_washing_is_factset_partner_investment | peer_car_m1_p1_mm | partner_investment_x_credible_minus_washing | 0.0055** | 0.002319 | 0.018358 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.255833 |
| stack_credible_minus_washing_is_factset_partner_high_confidence | peer_ar0_mm | partner_high_confidence_x_credible_minus_washing | -0.0015 | 0.001292 | 0.250123 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.272432 |
| stack_credible_minus_washing_is_factset_partner_high_confidence | peer_car_0_p1_mm | partner_high_confidence_x_credible_minus_washing | -0.0030* | 0.001655 | 0.070166 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.284982 |
| stack_credible_minus_washing_is_factset_partner_high_confidence | peer_car_m1_p1_mm | partner_high_confidence_x_credible_minus_washing | -0.0019 | 0.001871 | 0.306163 | 363.0 |  | 5668.0 | 347.0 | 2338.0 | 0.255722 |

## Investment-Linked Partner Event-Weighted Diagnostic

| sample | x | events | corr_with_mean_partner_car0p1 | mean_partner_car0p1 |
|---|---|---|---|---|
| investment_partner_event_weighted | credible_implementation_z | 54.0 | -0.020913 | 0.008396 |
| investment_partner_event_weighted | strategic_embeddedness_z | 54.0 | 0.204359 | 0.008396 |
| investment_partner_event_weighted | promotional_washing_z | 54.0 | 0.00193 | 0.008396 |
| investment_partner_event_weighted | credible_minus_washing_z | 54.0 | -0.016213 | 0.008396 |

## Reading

This pass should be read as a screen:

- If `CredibleImplementation x AIActivePeer` is negative, it supports treating concrete implementation language as a competitive-risk signal.
- If `StrategicEmbeddedness x investment-linked partner` is positive, it supports the investment-linked partner route.
- If `PromotionalWashing x AIActivePeer` is negative in the same way as credible implementation, the text measure is not discriminating enough and needs manual recoding.

## Required Next Step

Manual validation should prioritize:

1. top and bottom `CredibleImplementation`;
2. top `StrategicEmbeddedness`;
3. top `PromotionalWashing` and `Denial`;
4. investment-linked partner events with large positive or negative CAR.

## Output Files

- `results/v48_disclosure_text_feature_panel_20260608/event_text_features.csv`
- `results/v48_disclosure_text_feature_panel_20260608/event_text_feature_evidence_sentences.csv`
- `results/v48_disclosure_text_feature_panel_20260608/text_feature_summary.csv`
- `results/v48_disclosure_text_feature_panel_20260608/text_feature_correlations.csv`
- `results/v48_disclosure_text_feature_panel_20260608/competitor_text_feature_regressions.csv`
- `results/v48_disclosure_text_feature_panel_20260608/competitor_text_feature_horserace.csv`
- `results/v48_disclosure_text_feature_panel_20260608/relationship_text_feature_regressions.csv`
- `results/v48_disclosure_text_feature_panel_20260608/investment_partner_event_feature_correlations.csv`
- `results/v48_disclosure_text_feature_panel_20260608/manual_validation_sample.csv`
