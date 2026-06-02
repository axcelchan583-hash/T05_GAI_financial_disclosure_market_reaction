# V11 GenAI Announcement Baseline Table

Date: 2026-05-29

## Purpose

This run answers a narrow question:

```text
Does the GenAI disclosure event itself have a stable average effect on similar firms?
```

The answer is **no clean negative standalone story**. The average Top5 peer reaction is not reliably different from zero. When true Top5 peers are compared with low-similarity peers within the same event, the difference is positive rather than negative; the comparison with random same-industry peers is null. Event-level supply-chain exposure also has a positive average peer effect. This supports the current paper framing: the headline result should remain the conditional peer-revaluation coefficient `Specificity_z × AIActivePeer`, not an average GenAI-announcement effect.

## Input Samples

- Frozen headline Top5 sample: `results/v6_focal_good_news_pretrend_checks_20260525/analysis_sample_top5.csv.gz`
- True / placebo market-model CAR panels with announcement cleaning flags: `results/v6_announcement_clean_checks_20260524/true_peer_market_model_car_panel_with_ann_flags.csv.gz`, `results/v6_announcement_clean_checks_20260524/placebo_peer_market_model_car_panel_with_ann_flags.csv.gz`
- Disclosure-type coded Top5 sample: `results/v7_disclosure_type_horserace_20260527/analysis_sample_top5_with_disclosure_types.csv.gz`
- Non-GenAI pseudo-event panel: `results/v6_identification_strengthening_20260524/non_genai_placebo_panel.csv.gz`

Outcome throughout: `PeerCAR[0,+1]` (`peer_car_0_p1_mm`).

## Panel A. Mean Peer CAR Against Zero

| test                                                   | sample                                                                   | coef_se              |      p |   nobs |   events |   peer_firms | cluster              |
|:-------------------------------------------------------|:-------------------------------------------------------------------------|:---------------------|-------:|-------:|---------:|-------------:|:---------------------|
| genai_true_top5_mean_peer_car_frozen                   | first focal GenAI event, announcement-cleaned, Top5 product-market peers | -0.000040 (0.000488) | 0.9344 |   7805 |     2177 |         3345 | event_id + peer_code |
| genai_true_top5_mean_peer_car_announcement_clean_panel | first focal GenAI event, announcement-cleaned true Top5 panel            | -0.000332 (0.000470) | 0.4796 |   8683 |     2416 |         3573 | event_id + peer_code |

## Panel B. Same-Event Top5 Peers Versus Placebo Peers

These regressions estimate `Top5 true product-market peer - placebo peer` within the same focal GenAI event.

| comparison                                | fe                             | coef_se               |      p |   nobs |   events |   peer_firms | cluster              |
|:------------------------------------------|:-------------------------------|:----------------------|-------:|-------:|---------:|-------------:|:---------------------|
| true_top5_vs_low_similarity_same_industry | event_fe                       | 0.001175** (0.000573) | 0.0403 |  15952 |     2431 |         4038 | event_id + peer_code |
| true_top5_vs_low_similarity_same_industry | event_fe_peer_industry_week_fe | 0.001533** (0.000661) | 0.0203 |  15952 |     2431 |         4038 | event_id + peer_code |
| true_top5_vs_random_same_industry         | event_fe                       | 0.000633 (0.000505)   | 0.2099 |  16371 |     2431 |         4550 | event_id + peer_code |
| true_top5_vs_random_same_industry         | event_fe_peer_industry_week_fe | 0.000553 (0.000548)   | 0.3132 |  16371 |     2431 |         4550 | event_id + peer_code |

## Panel C. AI-Active Versus Non-AI-Active Peers Without Specificity

These regressions ask whether AI-active peers are, on average, more negative around GenAI disclosures before using `Specificity_z`.

| ai_def               | fe                             | coef_se                |      p |   nobs |   events |   peer_firms | controls                          |
|:---------------------|:-------------------------------|:-----------------------|-------:|-------:|---------:|-------------:|:----------------------------------|
| ext_any              | event_fe                       | 0.000052 (0.001138)    | 0.9635 |   7805 |     2177 |         3345 | PeerCAR[-10,-2] + PeerCAR[-20,-2] |
| ext_any              | event_fe_peer_industry_week_fe | 0.000702 (0.001227)    | 0.5671 |   7805 |     2177 |         3345 | PeerCAR[-10,-2] + PeerCAR[-20,-2] |
| current_text_history | event_fe                       | -0.002552** (0.001049) | 0.015  |   7805 |     2177 |         3345 | PeerCAR[-10,-2] + PeerCAR[-20,-2] |
| current_text_history | event_fe_peer_industry_week_fe | -0.001779 (0.001169)   | 0.1281 |   7805 |     2177 |         3345 | PeerCAR[-10,-2] + PeerCAR[-20,-2] |

## Panel D. Event-Level Disclosure Type Average Effects

These rows do **not** use focal-event FE because the disclosure-type variables are event-level. They use calendar-week or focal-industry-week controls plus peer-industry-week FE and pre-window peer CAR controls.

| model                              | type              | fe                                     | coef_se                |      p |   nobs |   events |   peer_firms | controls                                                           |
|:-----------------------------------|:------------------|:---------------------------------------|:-----------------------|-------:|-------:|---------:|-------------:|:-------------------------------------------------------------------|
| separate_disclosure_type_average   | own_impl          | event_week_peer_industry_week          | 0.000677 (0.001183)    | 0.5671 |   7805 |     2177 |         3345 | PeerCAR[-10,-2] + PeerCAR[-20,-2]                                  |
| separate_disclosure_type_average   | own_impl          | focal_industry_week_peer_industry_week | -0.000787 (0.001451)   | 0.5876 |   7805 |     2177 |         3345 | PeerCAR[-10,-2] + PeerCAR[-20,-2]                                  |
| separate_disclosure_type_average   | supply_chain      | event_week_peer_industry_week          | 0.004257** (0.001747)  | 0.0148 |   7805 |     2177 |         3345 | PeerCAR[-10,-2] + PeerCAR[-20,-2]                                  |
| separate_disclosure_type_average   | supply_chain      | focal_industry_week_peer_industry_week | 0.003904** (0.001838)  | 0.0337 |   7805 |     2177 |         3345 | PeerCAR[-10,-2] + PeerCAR[-20,-2]                                  |
| separate_disclosure_type_average   | generic_attention | event_week_peer_industry_week          | 0.001091 (0.001712)    | 0.5241 |   7805 |     2177 |         3345 | PeerCAR[-10,-2] + PeerCAR[-20,-2]                                  |
| separate_disclosure_type_average   | generic_attention | focal_industry_week_peer_industry_week | 0.000956 (0.002198)    | 0.6637 |   7805 |     2177 |         3345 | PeerCAR[-10,-2] + PeerCAR[-20,-2]                                  |
| separate_disclosure_type_average   | denial_no_current | event_week_peer_industry_week          | -0.000662 (0.001490)   | 0.6567 |   7805 |     2177 |         3345 | PeerCAR[-10,-2] + PeerCAR[-20,-2]                                  |
| separate_disclosure_type_average   | denial_no_current | focal_industry_week_peer_industry_week | 0.000086 (0.001937)    | 0.9646 |   7805 |     2177 |         3345 | PeerCAR[-10,-2] + PeerCAR[-20,-2]                                  |
| joint_type_and_specificity_average | own_impl          | event_week_peer_industry_week          | 0.003612 (0.002437)    | 0.1383 |   7805 |     2177 |         3345 | all type flags + Specificity_z + PeerCAR[-10,-2] + PeerCAR[-20,-2] |
| joint_type_and_specificity_average | supply_chain      | event_week_peer_industry_week          | 0.004728*** (0.001803) | 0.0087 |   7805 |     2177 |         3345 | all type flags + Specificity_z + PeerCAR[-10,-2] + PeerCAR[-20,-2] |
| joint_type_and_specificity_average | generic_attention | event_week_peer_industry_week          | 0.005182* (0.002915)   | 0.0755 |   7805 |     2177 |         3345 | all type flags + Specificity_z + PeerCAR[-10,-2] + PeerCAR[-20,-2] |
| joint_type_and_specificity_average | denial_no_current | event_week_peer_industry_week          | 0.003694 (0.002661)    | 0.165  |   7805 |     2177 |         3345 | all type flags + Specificity_z + PeerCAR[-10,-2] + PeerCAR[-20,-2] |
| joint_type_and_specificity_average | specificity_z     | event_week_peer_industry_week          | -0.000042 (0.000472)   | 0.9296 |   7805 |     2177 |         3345 | all type flags + Specificity_z + PeerCAR[-10,-2] + PeerCAR[-20,-2] |
| joint_type_and_specificity_average | own_impl          | focal_industry_week_peer_industry_week | -0.000755 (0.002722)   | 0.7813 |   7805 |     2177 |         3345 | all type flags + Specificity_z + PeerCAR[-10,-2] + PeerCAR[-20,-2] |
| joint_type_and_specificity_average | supply_chain      | focal_industry_week_peer_industry_week | 0.004245** (0.001895)  | 0.0251 |   7805 |     2177 |         3345 | all type flags + Specificity_z + PeerCAR[-10,-2] + PeerCAR[-20,-2] |
| joint_type_and_specificity_average | generic_attention | focal_industry_week_peer_industry_week | 0.001096 (0.003359)    | 0.7441 |   7805 |     2177 |         3345 | all type flags + Specificity_z + PeerCAR[-10,-2] + PeerCAR[-20,-2] |
| joint_type_and_specificity_average | denial_no_current | focal_industry_week_peer_industry_week | 0.000390 (0.003177)    | 0.9023 |   7805 |     2177 |         3345 | all type flags + Specificity_z + PeerCAR[-10,-2] + PeerCAR[-20,-2] |
| joint_type_and_specificity_average | specificity_z     | focal_industry_week_peer_industry_week | 0.000057 (0.000564)    | 0.9191 |   7805 |     2177 |         3345 | all type flags + Specificity_z + PeerCAR[-10,-2] + PeerCAR[-20,-2] |

## Panel E. Non-GenAI Pseudo-Events

Mean peer CAR around ordinary non-GenAI investor-interaction events:

| test                                | coef_se             |      p |   nobs |   events |   peer_firms | cluster              |
|:------------------------------------|:--------------------|-------:|-------:|---------:|-------------:|:---------------------|
| non_genai_pseudo_top5_mean_peer_car | 0.000328 (0.000416) | 0.4296 |  15601 |     2436 |         3811 | event_id + peer_code |

Pseudo-event `Specificity_z × current_text_history` check:

| fe                             | coef_se              |      p |   nobs |   events |   peer_firms | cluster              |
|:-------------------------------|:---------------------|-------:|-------:|---------:|-------------:|:---------------------|
| event_fe                       | -0.002202 (0.002044) | 0.2814 |  15601 |     2436 |         3811 | event_id + peer_code |
| event_fe_peer_industry_week_fe | -0.002798 (0.002317) | 0.2272 |  15601 |     2436 |         3811 | event_id + peer_code |

## Interpretation

1. The average Top5 peer CAR around focal GenAI disclosures is close to zero and statistically insignificant.
2. Same-event Top5-minus-low-similarity peer differences are positive, and Top5-minus-random same-industry differences are null. Neither pattern supports a negative average announcement-level peer effect.
3. AI-active peers are not uniformly more negative around GenAI disclosure events before using `Specificity_z`.
4. Disclosure type matters: AI supply-chain exposure shows a positive average peer effect, consistent with category validation rather than competitive-risk reassessment.
5. Non-GenAI pseudo-events do not reproduce the current `Specificity_z × AIActivePeer` negative pattern.

The current main paper should therefore say:

```text
The average peer reaction to GenAI disclosures is mixed and weak.
The robust pattern emerges in the conditional channel:
more specific focal GenAI disclosures are associated with more negative
short-window revaluation of AI-active close product-market peers.
```

