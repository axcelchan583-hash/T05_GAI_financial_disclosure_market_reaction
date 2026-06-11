# v38 Wide Collaborator-Competitor Probe

Date: 2026-06-07

## Scope

This is the first data probe for the redesigned T05 question:

```text
Do concrete GenAI initiative disclosures trigger relationship-dependent market revaluation,
with product-market competitors reacting negatively and pre-existing cooperative linked firms
reacting more favorably?
```

This run uses only the v36 `first event per focal firm` sample and compares:

- main competitors: `liu_product_tfidf_same_industry_d_top10`;
- upstream listed suppliers from pre-event supply-chain edges;
- downstream listed customers from the same edge file, reversing the direction;
- supplier/customer union;
- low-similarity placebo peers, for a rough sanity check.

All cooperative links require relation year in event year minus 5 through event year minus 1.

## Sample Flow

| layer | linked_rows | events | focal_firms | related_firms | clean_car0p1_rows | clean_car0p1_events |
|---|---|---|---|---|---|---|
| v36_first_events | 363.0 | 363.0 | 363.0 |  |  |  |
| supplier_links_raw | 85.0 | 41.0 | 41.0 | 74.0 |  |  |
| customer_links_raw | 92.0 | 53.0 | 53.0 | 86.0 |  |  |
| cooperative_union_raw | 176.0 | 74.0 | 74.0 | 154.0 |  |  |
| competitor_returns | 3151.0 | 319.0 | 319.0 | 1546.0 | 2790.0 | 316.0 |
| cooperative_union_returns | 176.0 | 74.0 | 74.0 | 154.0 | 142.0 | 70.0 |
| customer_returns | 92.0 | 53.0 | 53.0 | 86.0 | 71.0 | 46.0 |
| placebo_low_similarity_returns | 1625.0 | 325.0 | 325.0 | 1112.0 | 1359.0 | 322.0 |
| supplier_returns | 85.0 | 41.0 | 41.0 | 74.0 | 72.0 | 35.0 |

## CAR[0,+1] by Relation Type

| relation_type | mean | se | p | nobs | events | related_firms | positive_share | event_weighted_mean | event_weighted_p | event_weighted_events |
|---|---|---|---|---|---|---|---|---|---|---|
| competitor | -0.004641 | 0.001634 | 0.004501 | 2790.0 | 316.0 | 1385.0 | 0.434409 | -0.005051 | 0.002267 | 316.0 |
| cooperative_union | -0.004048 | 0.003826 | 0.290006 | 142.0 | 70.0 | 122.0 | 0.429577 | -0.00049 | 0.90636 | 70.0 |
| customer | -0.00522 | 0.003674 | 0.155369 | 71.0 | 46.0 | 66.0 | 0.464789 | -0.003249 | 0.457809 | 46.0 |
| placebo_low_similarity | -0.002536 | 0.001555 | 0.102965 | 1359.0 | 322.0 | 953.0 | 0.43635 | -0.002707 | 0.079521 | 322.0 |
| supplier | -0.002837 | 0.006404 | 0.657769 | 72.0 | 35.0 | 62.0 | 0.388889 | 0.00291 | 0.659169 | 35.0 |

## Stacked Event-FE Regressions

Baseline group is product-market competitors. Competitor event-firm rows that also appear in the cooperative union are removed from the competitor baseline.

| sample | outcome | regressor | coef_event_fmt | p_event_cluster | coef_two_way_fmt | p_two_way | nobs | events | related_firms | r2 |
|---|---|---|---|---|---|---|---|---|---|---|
| union_vs_competitor | peer_ar0_mm | cooperative | 0.0040 | 0.143202 | 0.0040 | 0.150036 | 638.0 | 59.0 | 494.0 | 0.366767 |
| supplier_customer_vs_competitor | peer_ar0_mm | is_supplier | 0.0029 | 0.446774 | 0.0029 | 0.454699 | 645.0 | 61.0 | 497.0 | 0.366671 |
| supplier_customer_vs_competitor | peer_ar0_mm | is_customer | 0.0043 | 0.214182 | 0.0043 | 0.213601 | 645.0 | 61.0 | 497.0 | 0.366671 |
| union_vs_competitor | peer_car_0_p1_mm | cooperative | 0.0024 | 0.639577 | 0.0024 | 0.640335 | 638.0 | 59.0 | 494.0 | 0.395816 |
| supplier_customer_vs_competitor | peer_car_0_p1_mm | is_supplier | 0.0076 | 0.271948 | 0.0076 | 0.270302 | 645.0 | 61.0 | 497.0 | 0.39873 |
| supplier_customer_vs_competitor | peer_car_0_p1_mm | is_customer | -0.0020 | 0.740953 | -0.0020 | 0.74104 | 645.0 | 61.0 | 497.0 | 0.39873 |
| union_vs_competitor | peer_car_m1_p1_mm | cooperative | 0.0062 | 0.345965 | 0.0062 | 0.343938 | 638.0 | 59.0 | 494.0 | 0.389628 |
| supplier_customer_vs_competitor | peer_car_m1_p1_mm | is_supplier | 0.0088 | 0.247532 | 0.0088 | 0.232728 | 645.0 | 61.0 | 497.0 | 0.388376 |
| supplier_customer_vs_competitor | peer_car_m1_p1_mm | is_customer | 0.0034 | 0.709241 | 0.0034 | 0.709236 | 645.0 | 61.0 | 497.0 | 0.388376 |

## Competitor-Cooperative Overlap

| metric | value |
|---|---|
| competitor_rows_before_overlap_drop | 3151.0 |
| competitor_event_firm_overlaps_with_coop | 6.0 |
| competitor_rows_after_overlap_drop | 3145.0 |
| cooperative_union_rows | 176.0 |

## Reading

- The key weak-form test is whether `cooperative > competitor` in the stacked event-FE regression.
- Absolute positive cooperative CAR is a stronger condition and should not be assumed ex ante.
- If supplier/customer union is not positive but the stacked coefficient is positive, the result can still support relation-dependent revaluation.
- If neither absolute cooperative CAR nor relative stacked difference survives, keep the paper on the conservative competitor-negative path.

## Output Files

- `results/v38_wide_collaborator_competitor_probe_20260607/sample_flow.csv`
- `results/v38_wide_collaborator_competitor_probe_20260607/relation_event_study.csv`
- `results/v38_wide_collaborator_competitor_probe_20260607/stacked_regressions.csv`
- `results/v38_wide_collaborator_competitor_probe_20260607/relation_panel.csv.gz`
- `results/v38_wide_collaborator_competitor_probe_20260607/stack_union_panel.csv.gz`
- `results/v38_wide_collaborator_competitor_probe_20260607/stack_direction_panel.csv.gz`
