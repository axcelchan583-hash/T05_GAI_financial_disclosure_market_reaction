# V6 Focal Good-News and Pre-Trend Checks

Date: 2026-05-25

Scope: only the two requested robustness checks. Sample is the current headline sample: first focal GenAI event, Top5 product-market peers, announcement-cleaned observations.

Fixed effects: `event_id + peer_industry_week`.

Standard errors: two-way clustered by `event_id` and `peer_code`.

## Task 1: Add Focal-Firm Good-News Controls

Coefficient reported: `Spec_z x AIActive`.

| AIActive     | Spec                        | Spec_z x AIActive coef (SE)   |     p |    N |   Events |   Peer firms | Controls                                                                    |
|:-------------|:----------------------------|:------------------------------|------:|-----:|---------:|-------------:|:----------------------------------------------------------------------------|
| text_history | baseline_prewindow_controls | -0.002275** (0.001030)        | 0.027 | 7805 |     2177 |         3345 | PeerCAR[-10,-2], PeerCAR[-20,-2]                                            |
| text_history | add_focal_car               | -0.002275** (0.001030)        | 0.027 | 7805 |     2177 |         3345 | FocalCAR[0,+1], PeerCAR[-10,-2], PeerCAR[-20,-2]                            |
| text_history | add_focal_car_x_ai          | -0.002283** (0.001029)        | 0.027 | 7805 |     2177 |         3345 | FocalCAR[0,+1], FocalCAR[0,+1] x AIActive, PeerCAR[-10,-2], PeerCAR[-20,-2] |
| ext_any      | baseline_prewindow_controls | -0.002303** (0.000992)        | 0.02  | 7805 |     2177 |         3345 | PeerCAR[-10,-2], PeerCAR[-20,-2]                                            |
| ext_any      | add_focal_car               | -0.002303** (0.000992)        | 0.02  | 7805 |     2177 |         3345 | FocalCAR[0,+1], PeerCAR[-10,-2], PeerCAR[-20,-2]                            |
| ext_any      | add_focal_car_x_ai          | -0.002307** (0.000991)        | 0.02  | 7805 |     2177 |         3345 | FocalCAR[0,+1], FocalCAR[0,+1] x AIActive, PeerCAR[-10,-2], PeerCAR[-20,-2] |

Note: `FocalCAR[0,+1]` is event-level and is absorbed by event fixed effects. The informative added control is `FocalCAR[0,+1] x AIActive`.

## Task 2: Pre-Trend-Adjusted Outcome

Outcome is residualized from a first-stage regression of `PeerCAR[0,+1]` on `PeerCAR[-10,-2]`; coefficient reported remains `Spec_z x AIActive`.

| AIActive     | Spec                          | Spec_z x AIActive coef (SE)   |     p |    N |   Events |   Peer firms | Controls                                                                                            |
|:-------------|:------------------------------|:------------------------------|------:|-----:|---------:|-------------:|:----------------------------------------------------------------------------------------------------|
| text_history | residual_y_baseline           | -0.002274** (0.001028)        | 0.027 | 7805 |     2177 |         3345 | Outcome residualized on PeerCAR[-10,-2]; RHS controls PeerCAR[-20,-2]                               |
| text_history | residual_y_add_focal_car      | -0.002274** (0.001028)        | 0.027 | 7805 |     2177 |         3345 | Outcome residualized on PeerCAR[-10,-2]; FocalCAR[0,+1], PeerCAR[-20,-2]                            |
| text_history | residual_y_add_focal_car_x_ai | -0.002281** (0.001027)        | 0.026 | 7805 |     2177 |         3345 | Outcome residualized on PeerCAR[-10,-2]; FocalCAR[0,+1], FocalCAR[0,+1] x AIActive, PeerCAR[-20,-2] |
| ext_any      | residual_y_baseline           | -0.002295** (0.000992)        | 0.021 | 7805 |     2177 |         3345 | Outcome residualized on PeerCAR[-10,-2]; RHS controls PeerCAR[-20,-2]                               |
| ext_any      | residual_y_add_focal_car      | -0.002295** (0.000992)        | 0.021 | 7805 |     2177 |         3345 | Outcome residualized on PeerCAR[-10,-2]; FocalCAR[0,+1], PeerCAR[-20,-2]                            |
| ext_any      | residual_y_add_focal_car_x_ai | -0.002300** (0.000990)        | 0.02  | 7805 |     2177 |         3345 | Outcome residualized on PeerCAR[-10,-2]; FocalCAR[0,+1], FocalCAR[0,+1] x AIActive, PeerCAR[-20,-2] |

## Files

- `results/v6_focal_good_news_pretrend_checks_20260525/task1_focal_good_news_controls.csv`
- `results/v6_focal_good_news_pretrend_checks_20260525/task2_pretrend_residualized_y.csv`
- `results/v6_focal_good_news_pretrend_checks_20260525/analysis_sample_top5.csv.gz`
