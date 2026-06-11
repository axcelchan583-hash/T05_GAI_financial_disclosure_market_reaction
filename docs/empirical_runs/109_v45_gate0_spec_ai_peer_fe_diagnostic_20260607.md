# v45 Gate 0: Spec x AIActive Peer-FE Diagnostic

Date: 2026-06-07

## Purpose

Diagnose whether `Spec x AIActivePeer` disappearing under peer-firm fixed effects is mainly a power / singleton / within-variation problem, or evidence that the effect is absent.

## 1. Peer-Firm Event Frequency

| metric | min | p25 | median | p75 | max | mean | peer_firms | obs |
|---|---|---|---|---|---|---|---|---|
| peer_event_frequency | 1.0000 | 1.0000 | 1.0000 | 2.0000 | 30.0000 | 2.0152 | 1384 | 2789 |

## Singleton Contribution

| peer_firms | singleton_peer_firms | singleton_peer_share | total_obs | singleton_obs | singleton_obs_share |
|---|---|---|---|---|---|
| 1384 | 826.0000 | 0.5968 | 2789 | 826 | 0.2962 |

## 2. Between/Within Variation of Spec x AIActivePeer

| variable | overall_sd | between_peer_sd_unweighted | between_peer_sd_obs_weighted | within_peer_sd | within_over_overall | within_share_of_variance | obs | peer_firms |
|---|---|---|---|---|---|---|---|---|
| spec_ai | 0.6759 | 0.5020 | 0.4268 | 0.5241 | 0.7754 | 0.6013 | 2789 | 1384 |
| spec_ai_non_singleton_peers | 0.7182 | 0.3956 | 0.3543 | 0.6248 | 0.8699 | 0.7567 | 1963 | 558 |

## 3. Same-Subsample Event-FE Check After Dropping Singleton Peers

| spec | outcome | xvars | fe | coef | se | z | p | coef_fmt | se_fmt | nobs | events | peer_firms | absorbed_no_contribution_obs | effective_identification_obs | overall_r2 | within_r2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| non_singleton_event_fe_only | peer_car_0_p1_mm | ai,spec_ai | event_key | -0.0032 | 0.0014 | -2.2256 | 0.0260 | -0.0032** | (0.0014) | 1963 | 279 | 558 | 0 | 1963 | 0.5200 | 0.0025 |
| non_singleton_event_fe_plus_pre_returns | peer_car_0_p1_mm | ai,spec_ai,peer_car_pre10_m2_mm,peer_car_pre20_m2_mm | event_key | -0.0032 | 0.0014 | -2.2102 | 0.0271 | -0.0032** | (0.0014) | 1963 | 279 | 558 | 0 | 1963 | 0.5202 | 0.0029 |

## 4. Main Specification Comparison

| spec | outcome | xvars | fe | coef | se | z | p | coef_fmt | se_fmt | nobs | events | peer_firms | absorbed_no_contribution_obs | effective_identification_obs | overall_r2 | within_r2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| event_fe_only | peer_car_0_p1_mm | ai,spec_ai | event_key | -0.0034 | 0.0012 | -2.8258 | 0.0047 | -0.0034*** | (0.0012) | 2789 | 316 | 1384 | 0 | 2789 | 0.4813 | 0.0026 |
| event_fe_plus_pre_returns | peer_car_0_p1_mm | ai,spec_ai,peer_car_pre10_m2_mm,peer_car_pre20_m2_mm | event_key | -0.0033 | 0.0012 | -2.8117 | 0.0049 | -0.0033*** | (0.0012) | 2789 | 316 | 1384 | 0 | 2789 | 0.4813 | 0.0026 |
| event_and_peer_firm_fe | peer_car_0_p1_mm | ai,spec_ai,peer_car_pre10_m2_mm,peer_car_pre20_m2_mm | event_key+peer_code | -0.0010 | 0.0018 | -0.5594 | 0.5759 | -0.0010 | (0.0018) | 2789 | 316 | 1384 | 826 | 1963 | 0.7488 | 0.0030 |

## 5. Analyst-Covered Fallback Probe

| sample | outcome | regressor | fe | nobs | events | peer_firms | coef | se | z | p | coef_fmt | se_fmt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fy1_feps_60d_covered | PeerCAR[0,+1] | AIActivePeer | no_fe | 185 | 100 | 105 | 0.0022 | 0.0065 | 0.3388 | 0.7348 | 0.0022 | (0.0065) |
| fy1_feps_60d_covered | PeerCAR[0,+1] | AIActivePeer | event_fe | 185 | 100 | 105 | 0.0015 | 0.0098 | 0.1524 | 0.8789 | 0.0015 | (0.0098) |
| fy1_feps_60d_covered | FY+1 EPS revision_scaled | AIActivePeer | no_fe | 185 | 100 | 105 | 0.1138 | 0.1058 | 1.0762 | 0.2819 | 0.1138 | (0.1058) |
| fy1_feps_60d_covered | FY+1 EPS revision_scaled | AIActivePeer | event_fe | 185 | 100 | 105 | 0.2340 | 0.1762 | 1.3278 | 0.1842 | 0.2340 | (0.1762) |
| fy1_feps_60d_covered | FY+1 EPS revision_down | AIActivePeer | no_fe | 185 | 100 | 105 | 0.0661 | 0.0766 | 0.8620 | 0.3887 | 0.0661 | (0.0766) |
| fy1_feps_60d_covered | FY+1 EPS revision_down | AIActivePeer | event_fe | 185 | 100 | 105 | -0.0890 | 0.1106 | -0.8047 | 0.4210 | -0.0890 | (0.1106) |

## Verdict

**A 主线 GO.** 剔除 singleton 后 event FE 规格仍为负且显著；本次不是 within SD 极低，而是 peer FE 改用更窄的 within-peer 对比并移除大量 singleton 识别贡献，不能据此判定 event-FE 主效应不存在。

## Table Order Recommendation

1. Keep the main Table 2 event-study result on product-market competitor CAR.
2. Put `Spec x AIActivePeer` event-FE heterogeneity as the main mechanism/heterogeneity table.
3. Put the peer-firm-FE version in robustness, explicitly noting the high singleton share and the fact that this specification asks a narrower within-peer question.
4. Use analyst-covered evidence as supporting mechanism evidence, not as the fallback main route unless later analyst revision tests become stronger.

## Output Files

- `results/v45_gate0_spec_ai_peer_fe_diagnostic_20260607/peer_frequency_by_firm.csv`
- `results/v45_gate0_spec_ai_peer_fe_diagnostic_20260607/peer_frequency_distribution.csv`
- `results/v45_gate0_spec_ai_peer_fe_diagnostic_20260607/singleton_summary.csv`
- `results/v45_gate0_spec_ai_peer_fe_diagnostic_20260607/spec_ai_variance_decomposition.csv`
- `results/v45_gate0_spec_ai_peer_fe_diagnostic_20260607/main_spec_comparison.csv`
- `results/v45_gate0_spec_ai_peer_fe_diagnostic_20260607/non_singleton_event_fe_checks.csv`
- `results/v45_gate0_spec_ai_peer_fe_diagnostic_20260607/analyst_fallback_aiactive.csv`
