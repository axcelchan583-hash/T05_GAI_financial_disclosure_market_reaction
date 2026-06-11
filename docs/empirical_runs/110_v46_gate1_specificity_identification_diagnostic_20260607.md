# v46 Gate 1: Specificity Identification Diagnostic

Date: 2026-06-07

## Key Identification Note

`Spec` is an event-level variable. Therefore, in AIActive-only or non-AIActive-only subsamples, `Spec` is constant within each event and is mechanically absorbed by event fixed effects. The original T1/T2 event-FE specifications cannot estimate a coefficient on `Spec`.

For completeness, this run first reports the original prompt specifications as absorbed, then runs a feasible no-event-FE version with peer-industry-week fixed effects and an optional peer-firm fixed effect.

## T1/T2 Original Prompt Specifications

| test | sample | spec | outcome | key_var | status | nobs | events | peer_firms | absorbed_no_contribution_obs | effective_identification_obs | key_resid_sd_after_fe | absorbed_vars |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1/T2_original_prompt | AIActive=1 | event_fe | peer_car_0_p1_mm | spec_z | key_var_absorbed_by_fe | 1253 | 278 | 549 | 0 | 1253 | 0.0000 | spec_z |
| T1/T2_original_prompt | AIActive=1 | event_plus_peer_fe | peer_car_0_p1_mm | spec_z | key_var_absorbed_by_fe | 1253 | 278 | 549 | 234 | 1019 | 0.0000 | spec_z |
| T1/T2_original_prompt | AIActive=0 | event_fe | peer_car_0_p1_mm | spec_z | key_var_absorbed_by_fe | 1536 | 309 | 978 | 0 | 1536 | 0.0000 | spec_z |
| T1/T2_original_prompt | AIActive=0 | event_plus_peer_fe | peer_car_0_p1_mm | spec_z | key_var_absorbed_by_fe | 1536 | 309 | 978 | 592 | 944 | 0.0000 | spec_z |

## T1/T2 Feasible Specifications

| test | sample | spec | outcome | key_var | status | coef | se_event | p_event | se_peer | p_peer | nobs | events | peer_firms | absorbed_no_contribution_obs | effective_identification_obs | key_resid_sd_after_fe | absorbed_vars |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1/T2_feasible_no_event_fe | AIActive=1 | peer_industry_week_fe | peer_car_0_p1_mm | spec_z | estimated | 0.0007 | 0.0044 | 0.8756 | 0.0024 | 0.7685 | 1253 | 278 | 549 | 0 | 1253 | 0.4626 |  |
| T1/T2_feasible_no_event_fe | AIActive=1 | peer_industry_week_plus_peer_fe | peer_car_0_p1_mm | spec_z | estimated | 0.0015 | 0.0037 | 0.6805 | 0.0026 | 0.5638 | 1253 | 278 | 549 | 234 | 1019 | 0.4017 |  |
| T1/T2_feasible_no_event_fe | AIActive=0 | peer_industry_week_fe | peer_car_0_p1_mm | spec_z | estimated | 0.0008 | 0.0040 | 0.8347 | 0.0029 | 0.7713 | 1536 | 309 | 978 | 0 | 1536 | 0.2911 |  |
| T1/T2_feasible_no_event_fe | AIActive=0 | peer_industry_week_plus_peer_fe | peer_car_0_p1_mm | spec_z | estimated | 0.0045 | 0.0041 | 0.2712 | 0.0040 | 0.2554 | 1536 | 309 | 978 | 592 | 944 | 0.1829 |  |

## T3 Full-Sample Decomposition

| test | sample | spec | outcome | key_var | status | coef | se_event | p_event | se_peer | p_peer | nobs | events | peer_firms | key_resid_sd_after_fe | absorbed_vars |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T3_full_sample_decomposition | full | event_fe | peer_car_0_p1_mm | spec_z | key_var_absorbed_by_fe |  |  |  |  |  | 2789 | 316 | 1384 | 0.0000 | spec_z |
| T3_full_sample_decomposition | full | event_fe | peer_car_0_p1_mm | ai | estimated | -0.0013 | 0.0013 | 0.3412 | 0.0013 | 0.3316 | 2789 | 316 | 1384 | 0.4069 | spec_z |
| T3_full_sample_decomposition | full | event_fe | peer_car_0_p1_mm | spec_ai | estimated | -0.0033 | 0.0012 | 0.0042 | 0.0013 | 0.0106 | 2789 | 316 | 1384 | 0.4176 | spec_z |
| T3_full_sample_decomposition | full | peer_industry_week_fe | peer_car_0_p1_mm | spec_z | estimated | 0.0036 | 0.0040 | 0.3632 | 0.0020 | 0.0755 | 2789 | 316 | 1384 | 0.3836 |  |
| T3_full_sample_decomposition | full | peer_industry_week_fe | peer_car_0_p1_mm | ai | estimated | -0.0008 | 0.0014 | 0.5539 | 0.0014 | 0.5590 | 2789 | 316 | 1384 | 0.4139 |  |
| T3_full_sample_decomposition | full | peer_industry_week_fe | peer_car_0_p1_mm | spec_ai | estimated | -0.0038 | 0.0013 | 0.0024 | 0.0014 | 0.0051 | 2789 | 316 | 1384 | 0.4967 |  |

## T4 Robustness for Feasible T1(a)

| test | sample | spec | outcome | key_var | status | coef | se_event | p_event | se_peer | p_peer | nobs | events | peer_firms | key_resid_sd_after_fe | absorbed_vars |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T4_feasible_T1a_robustness | AIActive=1 | PeerCAR[-1,+1]_peer_industry_week_fe | peer_car_m1_p1_mm | spec_z | estimated | 0.0028 | 0.0039 | 0.4644 | 0.0023 | 0.2192 | 1253 | 278 | 549 | 0.4626 |  |
| T4_feasible_T1a_robustness | AIActive=1 | PeerAR[0]_peer_industry_week_fe | peer_ar0_mm | spec_z | estimated | -0.0011 | 0.0028 | 0.6986 | 0.0018 | 0.5516 | 1253 | 278 | 549 | 0.4626 |  |
| T4_feasible_T1a_robustness | AIActive=1 | raw_detail_density_peer_industry_week_fe | peer_car_0_p1_mm | legacy_detail_density_raw | estimated | 0.0002 | 0.0013 | 0.8756 | 0.0007 | 0.7685 | 1253 | 278 | 549 | 1.5338 |  |

## Verdict

**DOWNGRADE.** 原 prompt 的 event-FE 子样本规格不可识别；可识别的 AIActive=1 peer-FE 规格下 Spec 也不显著，specificity 不能作为 within-peer 主线，只能保留为 event-FE 交互异质性。

## Writing Implication

Do not write that `Spec` is identified in AIActive-only event-FE regressions. With event FE, the estimable object is the interaction `Spec x AIActivePeer`, because AIActive varies across peers within the same event. If the paper needs a within-peer specificity claim, it must use a no-event-FE design with time/industry controls and explain the different identifying variation.

## Output Files

- `results/v46_gate1_specificity_identification_diagnostic_20260607/t1_t2_original_prompt.csv`
- `results/v46_gate1_specificity_identification_diagnostic_20260607/t1_t2_feasible_specs.csv`
- `results/v46_gate1_specificity_identification_diagnostic_20260607/t3_full_sample_decomposition.csv`
- `results/v46_gate1_specificity_identification_diagnostic_20260607/t4_feasible_robustness.csv`
