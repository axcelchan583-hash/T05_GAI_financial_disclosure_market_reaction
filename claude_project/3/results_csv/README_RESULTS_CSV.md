# Results CSV Index

These CSV files are from:

`results/v6_final_review_checks_20260525`

They correspond to the 2026-05-25 final go/no-go checks.

## Files

- `headline.csv`: headline peer-CAR regressions, including no-prewindow and with-prewindow versions, Top5/Top10, text-history AIActive, external `ext_any`, and `ext_plus_history`.
- `specificity_validation.csv`: main result after controlling for observable text features such as length, AI keyword intensity, attention/source proxies, numeric/component proxies, and all controls together.
- `specificity_feature_correlations.csv`: correlations between specificity and observable text features.
- `specificity_component_summary.csv`: descriptive statistics for heuristic specificity components.
- `proximity_gradient.csv`: Top1-3, Top4-5, Top6-10, low-similarity peers, and random same-industry peer checks.
- `lead_lag.csv`: pre-window, event-window, and post-window CAR checks for text-history AIActive and external `ext_any`.
- `external_breakdown.csv`: component-by-component external AIActive checks, including CAC, AI patent grants, AI hiring, and composite measures.
- `mechanism.csv`: stricter peer-disclosure diffusion mechanism tests. These are null and should not be treated as core mechanism evidence.

## Main Rows To Inspect

For the current headline result, inspect `headline.csv` rows where:

```text
control_spec == "with_prewindow_controls"
fe_name == "event_fe_peer_industry_week_fe"
sample in ["top5", "top10"]
```

For the current safest AIActive validation, inspect:

```text
ai_def == "ext_any"
```
