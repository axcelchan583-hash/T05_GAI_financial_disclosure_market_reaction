# v42 FactSet Relationship Probe

Date: 2026-06-07

## Scope

This run connects the v36 first GenAI events to FactSet Revere Supply Chain Relationships. The conservative mapping keeps FactSet companies whose `country=CN` and primary `ticker` is a six-digit A-share code. Relationships are kept when they involve a mapped focal firm and overlap the five-year window before the GenAI event date. Related firms are then mapped back to A-share codes before calculating AR/CAR.

## Mapping Summary

- FactSet A-share history rows: `72,570`
- Unique mapped A-share codes: `5,642`
- v36 events mapped to FactSet IDs: `346` / 363

This is a conservative first pass. It may miss firms whose FactSet primary ticker is an H-share or overseas listing.

## Sample Flow

| layer | rows | events | focal_firms | related_firms | clean_car0p1_rows | clean_car0p1_events |
|---|---|---|---|---|---|---|
| v36_first_events | 363.0 | 363.0 | 363.0 |  |  |  |
| factset_mapped_focal_events | 346.0 | 346.0 | 346.0 |  |  |  |
| factset_a_share_relationship_links | 3149.0 | 297.0 | 297.0 | 1678.0 |  |  |
| factset_competitor_returns | 343.0 | 137.0 | 137.0 | 275.0 | 299.0 | 129.0 |
| factset_downstream_customer_returns | 1078.0 | 221.0 | 221.0 | 637.0 | 946.0 | 207.0 |
| factset_partner_distrib_returns | 9.0 | 8.0 | 8.0 | 4.0 | 3.0 | 3.0 |
| factset_partner_einvest_returns | 46.0 | 31.0 | 31.0 | 44.0 | 41.0 | 27.0 |
| factset_partner_investo_returns | 68.0 | 43.0 | 43.0 | 67.0 | 59.0 | 42.0 |
| factset_partner_jventur_returns | 27.0 | 17.0 | 17.0 | 27.0 | 22.0 | 15.0 |
| factset_partner_licenin_returns | 3.0 | 3.0 | 3.0 | 3.0 | 3.0 | 3.0 |
| factset_partner_licenot_returns | 5.0 | 2.0 | 2.0 | 5.0 | 5.0 | 2.0 |
| factset_partner_manufac_returns | 9.0 | 5.0 | 5.0 | 8.0 | 9.0 | 5.0 |
| factset_partner_marktng_returns | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| factset_partner_rescolb_returns | 305.0 | 117.0 | 117.0 | 227.0 | 272.0 | 114.0 |
| factset_relationship_union_returns | 2934.0 | 297.0 | 297.0 | 1678.0 | 2513.0 | 288.0 |
| factset_upstream_supplier_returns | 1255.0 | 184.0 | 184.0 | 940.0 | 1039.0 | 168.0 |

## FactSet Relation Coverage

| relation_group | relation_type | rows | events | focal_firms | related_firms | rel_types |
|---|---|---|---|---|---|---|
| competitor | factset_competitor | 343.0 | 137.0 | 137.0 | 275.0 | COMPETITOR |
| customer | factset_downstream_customer | 1078.0 | 221.0 | 221.0 | 637.0 | CUSTOMER;SUPPLIER |
| partner_high_confidence | factset_partner_rescolb | 305.0 | 117.0 | 117.0 | 227.0 | PARTNER-RESCOLB |
| partner_high_confidence | factset_partner_jventur | 27.0 | 17.0 | 17.0 | 27.0 | PARTNER-JVENTUR |
| partner_high_confidence | factset_partner_distrib | 9.0 | 8.0 | 8.0 | 4.0 | PARTNER-DISTRIB |
| partner_high_confidence | factset_partner_manufac | 9.0 | 5.0 | 5.0 | 8.0 | PARTNER-MANUFAC |
| partner_high_confidence | factset_partner_licenot | 5.0 | 2.0 | 2.0 | 5.0 | PARTNER-LICENOT |
| partner_high_confidence | factset_partner_licenin | 3.0 | 3.0 | 3.0 | 3.0 | PARTNER-LICENIN |
| partner_high_confidence | factset_partner_marktng | 1.0 | 1.0 | 1.0 | 1.0 | PARTNER-MARKTNG |
| partner_other | factset_partner_investo | 68.0 | 43.0 | 43.0 | 67.0 | PARTNER-INVESTO |
| partner_other | factset_partner_einvest | 46.0 | 31.0 | 31.0 | 44.0 | PARTNER-EINVEST |
| supplier | factset_upstream_supplier | 1255.0 | 184.0 | 184.0 | 940.0 | CUSTOMER;SUPPLIER |

## CAR[0,+1] by Relation Type

| relation_type | mean | se | p | nobs | events | related_firms | positive_share | event_weighted_mean | event_weighted_p | event_weighted_events |
|---|---|---|---|---|---|---|---|---|---|---|
| factset_competitor | -0.008111 | 0.003179 | 0.010718 | 299.0 | 129.0 | 241.0 | 0.384615 | -0.009223 | 0.000491 | 129.0 |
| factset_downstream_customer | -0.000589 | 0.00204 | 0.772947 | 946.0 | 207.0 | 551.0 | 0.440803 | -0.00264 | 0.194337 | 207.0 |
| factset_partner_distrib | -0.018747 | 0.01325 | 0.157101 | 3.0 | 3.0 | 3.0 | 0.0 | -0.018747 | 0.247988 | 3.0 |
| factset_partner_einvest | 0.00326 | 0.005436 | 0.548661 | 41.0 | 27.0 | 40.0 | 0.414634 | 0.008736 | 0.136029 | 27.0 |
| factset_partner_investo | 0.007571 | 0.0055 | 0.168685 | 59.0 | 42.0 | 58.0 | 0.542373 | 0.00706 | 0.135173 | 42.0 |
| factset_partner_jventur | -0.015092 | 0.006348 | 0.017429 | 22.0 | 15.0 | 22.0 | 0.272727 | -0.012896 | 0.065907 | 15.0 |
| factset_partner_licenin | -0.01411 | 0.001185 | 0.0 | 3.0 | 3.0 | 3.0 | 0.0 | -0.01411 | 0.0 | 3.0 |
| factset_partner_licenot | 0.008371 | 0.019951 | 0.674791 | 5.0 | 2.0 | 5.0 | 0.6 | 0.034822 | 0.429597 | 2.0 |
| factset_partner_manufac | -0.007326 | 0.016054 | 0.648166 | 9.0 | 5.0 | 8.0 | 0.555556 | -0.022415 | 0.323082 | 5.0 |
| factset_partner_marktng | 0.001652 |  |  | 1.0 | 1.0 | 1.0 | 1.0 | 0.001652 |  | 1.0 |
| factset_partner_rescolb | -0.005677 | 0.003188 | 0.074901 | 272.0 | 114.0 | 198.0 | 0.375 | -0.001548 | 0.599354 | 114.0 |
| factset_relationship_union | -0.002845 | 0.002887 | 0.324369 | 2513.0 | 288.0 | 1408.0 | 0.421409 | -0.002065 | 0.189824 | 288.0 |
| factset_upstream_supplier | -0.004144 | 0.005619 | 0.460825 | 1039.0 | 168.0 | 769.0 | 0.407122 | 0.000614 | 0.804281 | 168.0 |

## Stacked Event-FE Regressions

Baseline group is the existing product-market competitor panel. Product-competitor rows overlapping with FactSet relation rows are removed.

| sample | outcome | regressor | coef_event_fmt | p_event_cluster | coef_two_way_fmt | p_two_way | nobs | events | related_firms | r2 |
|---|---|---|---|---|---|---|---|---|---|---|
| factset_relation_vs_product_competitor | peer_ar_m1_mm | is_factset_competitor | 0.0014 | 0.405276 | 0.0014 | 0.409102 | 7111.0 | 288.0 | 2123.0 | 0.262909 |
| factset_relation_vs_product_competitor | peer_ar_m1_mm | is_factset_upstream_supplier | -0.0001 | 0.914079 | -0.0001 | 0.915534 | 7111.0 | 288.0 | 2123.0 | 0.262909 |
| factset_relation_vs_product_competitor | peer_ar_m1_mm | is_factset_downstream_customer | -0.0006 | 0.63479 | -0.0006 | 0.640696 | 7111.0 | 288.0 | 2123.0 | 0.262909 |
| factset_relation_vs_product_competitor | peer_ar_m1_mm | is_factset_relationship_union | -0.0004 | 0.709526 | -0.0004 | 0.714947 | 7111.0 | 288.0 | 2123.0 | 0.262909 |
| factset_relation_vs_product_competitor | peer_ar_m1_mm | is_factset_partner_distrib | -0.0029 | 0.275641 | -0.0029 | 0.276067 | 7111.0 | 288.0 | 2123.0 | 0.262909 |
| factset_relation_vs_product_competitor | peer_ar_m1_mm | is_factset_partner_einvest | -0.0018 | 0.560027 | -0.0018 | 0.565806 | 7111.0 | 288.0 | 2123.0 | 0.262909 |
| factset_relation_vs_product_competitor | peer_ar_m1_mm | is_factset_partner_investo | 0.0013 | 0.694954 | 0.0013 | 0.695923 | 7111.0 | 288.0 | 2123.0 | 0.262909 |
| factset_relation_vs_product_competitor | peer_ar_m1_mm | is_factset_partner_jventur | -0.0024 | 0.390171 | -0.0024 | 0.392031 | 7111.0 | 288.0 | 2123.0 | 0.262909 |
| factset_relation_vs_product_competitor | peer_ar_m1_mm | is_factset_partner_licenin | -0.0113 | 0.132771 | -0.0113 | 0.131889 | 7111.0 | 288.0 | 2123.0 | 0.262909 |
| factset_relation_vs_product_competitor | peer_ar_m1_mm | is_factset_partner_licenot | 0.0039 | 0.682491 | 0.0039 | 0.681899 | 7111.0 | 288.0 | 2123.0 | 0.262909 |
| factset_relation_vs_product_competitor | peer_ar_m1_mm | is_factset_partner_manufac | -0.0017 | 0.751918 | -0.0017 | 0.750822 | 7111.0 | 288.0 | 2123.0 | 0.262909 |
| factset_relation_vs_product_competitor | peer_ar_m1_mm | is_factset_partner_marktng | 0.0492*** | 0.0 | 0.0492*** | 0.0 | 7111.0 | 288.0 | 2123.0 | 0.262909 |
| factset_relation_vs_product_competitor | peer_ar0_mm | is_factset_competitor | -0.0001 | 0.93318 | -0.0001 | 0.931231 | 7111.0 | 288.0 | 2123.0 | 0.270282 |
| factset_relation_vs_product_competitor | peer_ar0_mm | is_factset_upstream_supplier | 0.0012 | 0.382912 | 0.0012 | 0.387903 | 7111.0 | 288.0 | 2123.0 | 0.270282 |
| factset_relation_vs_product_competitor | peer_ar0_mm | is_factset_downstream_customer | -0.0002 | 0.900208 | -0.0002 | 0.899222 | 7111.0 | 288.0 | 2123.0 | 0.270282 |
| factset_relation_vs_product_competitor | peer_ar0_mm | is_factset_relationship_union | 0.0006 | 0.624877 | 0.0006 | 0.622788 | 7111.0 | 288.0 | 2123.0 | 0.270282 |
| factset_relation_vs_product_competitor | peer_ar0_mm | is_factset_partner_distrib | -0.0154 | 0.320578 | -0.0154 | 0.320568 | 7111.0 | 288.0 | 2123.0 | 0.270282 |
| factset_relation_vs_product_competitor | peer_ar0_mm | is_factset_partner_einvest | 0.0027 | 0.293243 | 0.0027 | 0.288456 | 7111.0 | 288.0 | 2123.0 | 0.270282 |
| factset_relation_vs_product_competitor | peer_ar0_mm | is_factset_partner_investo | 0.0034 | 0.175059 | 0.0034 | 0.176608 | 7111.0 | 288.0 | 2123.0 | 0.270282 |
| factset_relation_vs_product_competitor | peer_ar0_mm | is_factset_partner_jventur | -0.0045 | 0.349434 | -0.0045 | 0.351577 | 7111.0 | 288.0 | 2123.0 | 0.270282 |
| factset_relation_vs_product_competitor | peer_ar0_mm | is_factset_partner_licenin | 0.0073 | 0.274104 | 0.0073 | 0.271409 | 7111.0 | 288.0 | 2123.0 | 0.270282 |
| factset_relation_vs_product_competitor | peer_ar0_mm | is_factset_partner_licenot | 0.0098 | 0.584447 | 0.0098 | 0.584767 | 7111.0 | 288.0 | 2123.0 | 0.270282 |
| factset_relation_vs_product_competitor | peer_ar0_mm | is_factset_partner_manufac | 0.0062*** | 3e-06 | 0.0062 |  | 7111.0 | 288.0 | 2123.0 | 0.270282 |
| factset_relation_vs_product_competitor | peer_ar0_mm | is_factset_partner_marktng | 0.0109*** | 0.0 | 0.0109*** | 0.0 | 7111.0 | 288.0 | 2123.0 | 0.270282 |
| factset_relation_vs_product_competitor | peer_ar_p1_mm | is_factset_competitor | -0.0029** | 0.041776 | -0.0029* | 0.052107 | 7111.0 | 288.0 | 2123.0 | 0.283471 |
| factset_relation_vs_product_competitor | peer_ar_p1_mm | is_factset_upstream_supplier | 0.0025* | 0.080799 | 0.0025* | 0.081256 | 7111.0 | 288.0 | 2123.0 | 0.283471 |
| factset_relation_vs_product_competitor | peer_ar_p1_mm | is_factset_downstream_customer | 0.0013 | 0.405608 | 0.0013 | 0.401701 | 7111.0 | 288.0 | 2123.0 | 0.283471 |
| factset_relation_vs_product_competitor | peer_ar_p1_mm | is_factset_relationship_union | 0.0015 | 0.217933 | 0.0015 | 0.216014 | 7111.0 | 288.0 | 2123.0 | 0.283471 |
| factset_relation_vs_product_competitor | peer_ar_p1_mm | is_factset_partner_distrib | -0.0123*** | 9.2e-05 | -0.0123*** | 9e-05 | 7111.0 | 288.0 | 2123.0 | 0.283471 |
| factset_relation_vs_product_competitor | peer_ar_p1_mm | is_factset_partner_einvest | 0.0051 | 0.165899 | 0.0051 | 0.163917 | 7111.0 | 288.0 | 2123.0 | 0.283471 |
| factset_relation_vs_product_competitor | peer_ar_p1_mm | is_factset_partner_investo | 0.0061* | 0.094988 | 0.0061* | 0.093658 | 7111.0 | 288.0 | 2123.0 | 0.283471 |
| factset_relation_vs_product_competitor | peer_ar_p1_mm | is_factset_partner_jventur | 0.0012 | 0.694542 | 0.0012 | 0.693642 | 7111.0 | 288.0 | 2123.0 | 0.283471 |
| factset_relation_vs_product_competitor | peer_ar_p1_mm | is_factset_partner_licenin | -0.0034 | 0.198975 | -0.0034 | 0.199227 | 7111.0 | 288.0 | 2123.0 | 0.283471 |
| factset_relation_vs_product_competitor | peer_ar_p1_mm | is_factset_partner_licenot | -0.0024 | 0.537938 | -0.0024 | 0.54628 | 7111.0 | 288.0 | 2123.0 | 0.283471 |
| factset_relation_vs_product_competitor | peer_ar_p1_mm | is_factset_partner_manufac | -0.0124 | 0.259003 | -0.0124 | 0.283287 | 7111.0 | 288.0 | 2123.0 | 0.283471 |
| factset_relation_vs_product_competitor | peer_ar_p1_mm | is_factset_partner_marktng | -0.0172*** | 0.0 | -0.0172*** | 0.0 | 7111.0 | 288.0 | 2123.0 | 0.283471 |
| factset_relation_vs_product_competitor | peer_car_0_p1_mm | is_factset_competitor | -0.0030 | 0.156905 | -0.0030 | 0.167726 | 7111.0 | 288.0 | 2123.0 | 0.306133 |
| factset_relation_vs_product_competitor | peer_car_0_p1_mm | is_factset_upstream_supplier | 0.0037* | 0.089752 | 0.0037* | 0.089621 | 7111.0 | 288.0 | 2123.0 | 0.306133 |
| factset_relation_vs_product_competitor | peer_car_0_p1_mm | is_factset_downstream_customer | 0.0011 | 0.619668 | 0.0011 | 0.617852 | 7111.0 | 288.0 | 2123.0 | 0.306133 |
| factset_relation_vs_product_competitor | peer_car_0_p1_mm | is_factset_relationship_union | 0.0021 | 0.261168 | 0.0021 | 0.262399 | 7111.0 | 288.0 | 2123.0 | 0.306133 |
| factset_relation_vs_product_competitor | peer_car_0_p1_mm | is_factset_partner_distrib | -0.0277 | 0.113163 | -0.0277 | 0.113187 | 7111.0 | 288.0 | 2123.0 | 0.306133 |
| factset_relation_vs_product_competitor | peer_car_0_p1_mm | is_factset_partner_einvest | 0.0078* | 0.066142 | 0.0078* | 0.06144 | 7111.0 | 288.0 | 2123.0 | 0.306133 |
| factset_relation_vs_product_competitor | peer_car_0_p1_mm | is_factset_partner_investo | 0.0096** | 0.027767 | 0.0096** | 0.027745 | 7111.0 | 288.0 | 2123.0 | 0.306133 |
| factset_relation_vs_product_competitor | peer_car_0_p1_mm | is_factset_partner_jventur | -0.0033 | 0.540087 | -0.0033 | 0.541607 | 7111.0 | 288.0 | 2123.0 | 0.306133 |
| factset_relation_vs_product_competitor | peer_car_0_p1_mm | is_factset_partner_licenin | 0.0038 | 0.651585 | 0.0038 | 0.650687 | 7111.0 | 288.0 | 2123.0 | 0.306133 |
| factset_relation_vs_product_competitor | peer_car_0_p1_mm | is_factset_partner_licenot | 0.0074 | 0.73469 | 0.0074 | 0.735798 | 7111.0 | 288.0 | 2123.0 | 0.306133 |
| factset_relation_vs_product_competitor | peer_car_0_p1_mm | is_factset_partner_manufac | -0.0062 | 0.590418 | -0.0062 | 0.601691 | 7111.0 | 288.0 | 2123.0 | 0.306133 |
| factset_relation_vs_product_competitor | peer_car_0_p1_mm | is_factset_partner_marktng | -0.0063*** | 0.0 | -0.0063*** | 0.0 | 7111.0 | 288.0 | 2123.0 | 0.306133 |
| factset_relation_vs_product_competitor | peer_car_m1_p1_mm | is_factset_competitor | -0.0017 | 0.498966 | -0.0017 | 0.50466 | 7111.0 | 288.0 | 2123.0 | 0.263124 |
| factset_relation_vs_product_competitor | peer_car_m1_p1_mm | is_factset_upstream_supplier | 0.0036 | 0.133002 | 0.0036 | 0.138339 | 7111.0 | 288.0 | 2123.0 | 0.263124 |
| factset_relation_vs_product_competitor | peer_car_m1_p1_mm | is_factset_downstream_customer | 0.0004 | 0.863414 | 0.0004 | 0.863311 | 7111.0 | 288.0 | 2123.0 | 0.263124 |
| factset_relation_vs_product_competitor | peer_car_m1_p1_mm | is_factset_relationship_union | 0.0017 | 0.401943 | 0.0017 | 0.40456 | 7111.0 | 288.0 | 2123.0 | 0.263124 |
| factset_relation_vs_product_competitor | peer_car_m1_p1_mm | is_factset_partner_distrib | -0.0306** | 0.040728 | -0.0306** | 0.0407 | 7111.0 | 288.0 | 2123.0 | 0.263124 |
| factset_relation_vs_product_competitor | peer_car_m1_p1_mm | is_factset_partner_einvest | 0.0059 | 0.284435 | 0.0059 | 0.284793 | 7111.0 | 288.0 | 2123.0 | 0.263124 |
| factset_relation_vs_product_competitor | peer_car_m1_p1_mm | is_factset_partner_investo | 0.0109** | 0.029604 | 0.0109** | 0.02985 | 7111.0 | 288.0 | 2123.0 | 0.263124 |
| factset_relation_vs_product_competitor | peer_car_m1_p1_mm | is_factset_partner_jventur | -0.0057 | 0.396983 | -0.0057 | 0.400494 | 7111.0 | 288.0 | 2123.0 | 0.263124 |
| factset_relation_vs_product_competitor | peer_car_m1_p1_mm | is_factset_partner_licenin | -0.0075 | 0.345493 | -0.0075 | 0.347151 | 7111.0 | 288.0 | 2123.0 | 0.263124 |
| factset_relation_vs_product_competitor | peer_car_m1_p1_mm | is_factset_partner_licenot | 0.0113 | 0.718419 | 0.0113 | 0.719016 | 7111.0 | 288.0 | 2123.0 | 0.263124 |
| factset_relation_vs_product_competitor | peer_car_m1_p1_mm | is_factset_partner_manufac | -0.0079 | 0.601141 | -0.0079 | 0.600573 | 7111.0 | 288.0 | 2123.0 | 0.263124 |
| factset_relation_vs_product_competitor | peer_car_m1_p1_mm | is_factset_partner_marktng | 0.0429*** | 0.0 | 0.0429*** | 0.0 | 7111.0 | 288.0 | 2123.0 | 0.263124 |

## Examples

| event_date | focal_code | focal_name | related_code | related_factset_name | relation_type | rel_type | focal_side | relation_start | relation_end | match_evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023-03-24 00:00:00 | 002362 | 汉王科技 | 600701 | Harbin Gong Da High-tech Enterprise Development Co., Ltd. | factset_competitor | COMPETITOR | target | 2019-12-16 00:00:00 | 2019-12-16 00:00:00 | IT services; ; ; ;  |
| 2023-04-18 00:00:00 | 002122 | 天马股份 | 600592 | Fujian Longxi Bearing (Group) Co., Ltd. | factset_competitor | COMPETITOR | target | 2021-09-20 00:00:00 | 2024-05-14 00:00:00 | bearings; ; ; ;  |
| 2023-04-18 00:00:00 | 002122 | 天马股份 | 002046 | Sinomach Precision Industry Co., Ltd. | factset_competitor | COMPETITOR | target | 2018-10-23 00:00:00 | 2018-10-23 00:00:00 | bearing products; machine tool equipment; ; ;  |
| 2023-04-26 00:00:00 | 002065 | 东华软件 | 603927 | Sinosoft Co., Ltd. | factset_competitor | COMPETITOR | target | 2020-09-16 00:00:00 | 2020-09-16 00:00:00 | medical and health informationization; ; ; ;  |
| 2023-05-05 00:00:00 | 002230 | 科大讯飞 | 300205 | Wuhan Tianyu Information Industry Co., Ltd. | factset_competitor | COMPETITOR | target | 2021-09-10 00:00:00 | 2021-09-10 00:00:00 | Education Cloud Platform; ; ; ;  |
| 2023-05-05 00:00:00 | 002230 | 科大讯飞 | 300479 | Synthesis Electronic Technology Co., Ltd. | factset_competitor | COMPETITOR | target | 2020-08-11 00:00:00 | 2020-08-11 00:00:00 | industrial robot; ; ; ;  |
| 2023-05-05 00:00:00 | 002230 | 科大讯飞 | 601801 | Anhui Xinhua Media Co., Ltd. | factset_competitor | COMPETITOR | target | 2020-07-09 00:00:00 | 2020-07-09 00:00:00 | ; ; ; ;  |
| 2023-05-15 00:00:00 | 300369 | 绿盟科技 | 600651 | Feilo Acoustics Co., Ltd. Shanghai | factset_competitor | COMPETITOR | target | 2022-05-11 00:00:00 | 2023-06-26 00:00:00 | internet security; ; ; ;  |
| 2023-05-15 00:00:00 | 300369 | 绿盟科技 | 600701 | Harbin Gong Da High-tech Enterprise Development Co., Ltd. | factset_competitor | COMPETITOR | target | 2019-12-16 00:00:00 | 2019-12-16 00:00:00 | IT services; ; ; ;  |
| 2023-05-15 00:00:00 | 300369 | 绿盟科技 | 002439 | Venustech Group Inc. | factset_competitor | COMPETITOR | target | 2018-07-05 00:00:00 | 2018-07-05 00:00:00 | ; ; ; ;  |
| 2023-06-28 00:00:00 | 688158 | 优刻得 | 300383 | Beijing Sinnet Technology Co., Ltd. | factset_competitor | COMPETITOR | source | 2020-11-11 00:00:00 | 2024-05-20 00:00:00 | public cloud IaaS; ; ; ;  |
| 2023-07-06 00:00:00 | 688322 | 奥比中光 | 603893 | Rockchip Electronics Co., Ltd. | factset_competitor | COMPETITOR | source | 2023-05-15 00:00:00 | 2023-05-15 00:00:00 | 3D visual perception technology; ; ; ;  |
| 2023-07-09 00:00:00 | 301052 | 果麦文化 | 301231 | Ronshin Group | factset_competitor | COMPETITOR | target | 2023-04-28 00:00:00 | 2023-04-28 00:00:00 | ; ; ; ;  |
| 2023-07-23 00:00:00 | 002929 | 润建股份 | 688387 | CICT Mobile Communication Technology Co., Ltd. | factset_competitor | COMPETITOR | target | 2023-04-25 00:00:00 | 2023-04-25 00:00:00 | mobile communication technology service; ; ; ;  |
| 2023-07-23 00:00:00 | 300657 | 弘信电子 | 605058 | Changzhou Aohong Electronics Co., Ltd. | factset_competitor | COMPETITOR | target | 2021-03-30 00:00:00 | 2021-03-30 00:00:00 | PCB; ; ; ;  |
| 2023-08-02 00:00:00 | 300668 | 杰恩设计 | 301365 | Matrix Design Co., Ltd. | factset_competitor | COMPETITOR | target | 2023-04-26 00:00:00 | 2023-04-26 00:00:00 | ; ; ; ;  |
| 2023-08-04 00:00:00 | 300275 | 梅安森 | 301195 | Nanjing Bestway Intelligent Control Technology Co., Ltd. | factset_competitor | COMPETITOR | target | 2023-07-21 00:00:00 | 2023-07-21 00:00:00 | intelligent mine; ; ; ;  |
| 2023-08-07 00:00:00 | 300229 | 拓尔思 | 600242 | Zhongchang Big Data Corp. Ltd. | factset_competitor | COMPETITOR | target | 2019-09-28 00:00:00 | 2019-09-28 00:00:00 | Search Engine Optimization; Search Engine Marketing; ; ;  |
| 2023-08-18 00:00:00 | 002698 | 博实股份 | 603960 | Shanghai Kelai Mechatronics Engineering Co., Ltd. | factset_competitor | COMPETITOR | target | 2021-06-10 00:00:00 | 2262-04-11 00:00:00 | automatic equipment manufacturing industry; ; ; ;  |
| 2023-08-18 00:00:00 | 002698 | 博实股份 | 600579 | KraussMaffei Co. Ltd. | factset_competitor | COMPETITOR | target | 2019-10-22 00:00:00 | 2019-10-22 00:00:00 | chemical equipment industry; ; ; ;  |
| 2023-09-22 00:00:00 | 002530 | 金财互联 | 002171 | Anhui Truchum Advanced Materials & Technology Co., Ltd. | factset_competitor | COMPETITOR | target | 2021-05-31 00:00:00 | 2021-05-31 00:00:00 | equipment manufacturing; ; ; ;  |
| 2023-09-25 00:00:00 | 603985 | 恒润股份 | 605123 | Wuxi Paike New Materials Technology Co., Ltd. | factset_competitor | COMPETITOR | target | 2021-08-13 00:00:00 | 2021-08-13 00:00:00 | Flanges; Forgings; ; ;  |
| 2023-10-21 00:00:00 | 600100 | 同方股份 | 600261 | Zhejiang Yankon Group Co., Ltd. | factset_competitor | COMPETITOR | target | 2022-11-29 00:00:00 | 2022-11-29 00:00:00 | LED Lights; ; ; ;  |
| 2023-11-16 00:00:00 | 300075 | 数字政通 | 688568 | Geovis Technology Co., Ltd. | factset_competitor | COMPETITOR | target | 2021-11-22 00:00:00 | 2021-11-22 00:00:00 | GIS; ; ; ;  |
| 2023-11-16 00:00:00 | 300075 | 数字政通 | 002152 | GRG Banking Equipment Co., Ltd. | factset_competitor | COMPETITOR | target | 2019-11-07 00:00:00 | 2019-11-07 00:00:00 | Smart government solutions; ; ; ;  |
| 2023-12-22 00:00:00 | 688521 | 芯原股份 | 600756 | Inspur Software Co., Ltd. | factset_competitor | COMPETITOR | source | 2021-08-09 00:00:00 | 2024-03-29 00:00:00 | semiconductor chips; ; ; ;  |
| 2023-12-22 00:00:00 | 688521 | 芯原股份 | 688256 | Cambricon Technologies Corp. Ltd. | factset_competitor | COMPETITOR | target | 2021-08-09 00:00:00 | 2021-08-09 00:00:00 | Terminal intelligent processor IP; ; ; ;  |
| 2024-01-02 00:00:00 | 002042 | 华孚时尚 | 605189 | Wuhu Fuchun Dye & Weave Co., Ltd. | factset_competitor | COMPETITOR | target | 2023-05-17 00:00:00 | 2023-05-17 00:00:00 | Textile and Garment; ; ; ;  |
| 2024-01-12 00:00:00 | 300872 | 天阳科技 | 000034 | Digital China Group Co., Ltd. | factset_competitor | COMPETITOR | source | 2021-08-25 00:00:00 | 2021-08-25 00:00:00 | IT Solutions; ; ; ;  |
| 2024-01-12 00:00:00 | 300872 | 天阳科技 | 300085 | Shenzhen Infogem Technologies Co., Ltd. | factset_competitor | COMPETITOR | source | 2021-08-25 00:00:00 | 2021-08-25 00:00:00 | IT Solutions; ; ; ;  |
| 2024-01-12 00:00:00 | 300872 | 天阳科技 | 300339 | Jiangsu Hoperun Software Co., Ltd. | factset_competitor | COMPETITOR | source | 2021-08-25 00:00:00 | 2021-08-25 00:00:00 | IT Solutions; ; ; ;  |
| 2024-01-12 00:00:00 | 300872 | 天阳科技 | 300348 | Shenzhen Sunline Tech Co., Ltd. | factset_competitor | COMPETITOR | source | 2021-08-25 00:00:00 | 2021-08-25 00:00:00 | IT Solutions; ; ; ;  |
| 2024-01-12 00:00:00 | 300872 | 天阳科技 | 300380 | Shanghai Amarsoft Information & Technology Co., Ltd. | factset_competitor | COMPETITOR | source | 2021-08-25 00:00:00 | 2021-08-25 00:00:00 | IT Solutions; ; ; ;  |
| 2024-01-12 00:00:00 | 300872 | 天阳科技 | 300465 | Global Infotech Co., Ltd. | factset_competitor | COMPETITOR | source | 2021-08-25 00:00:00 | 2021-08-25 00:00:00 | IT Solutions; ; ; ;  |
| 2024-01-12 00:00:00 | 300872 | 天阳科技 | 300663 | Client Service International, Inc. | factset_competitor | COMPETITOR | source | 2021-08-25 00:00:00 | 2021-08-25 00:00:00 | IT Solutions; ; ; ;  |
| 2024-01-12 00:00:00 | 300872 | 天阳科技 | 300674 | Yusys Technologies Co., Ltd. | factset_competitor | COMPETITOR | source | 2021-08-25 00:00:00 | 2021-08-25 00:00:00 | IT Solutions; ; ; ;  |
| 2024-01-12 00:00:00 | 300872 | 天阳科技 | 600570 | Hundsun Technologies, Inc. | factset_competitor | COMPETITOR | source | 2021-08-25 00:00:00 | 2021-08-25 00:00:00 | IT Solutions; ; ; ;  |
| 2024-01-12 00:00:00 | 300872 | 天阳科技 | 600571 | Sunyard Technology Co., Ltd. | factset_competitor | COMPETITOR | source | 2021-08-25 00:00:00 | 2021-08-25 00:00:00 | IT Solutions; ; ; ;  |
| 2024-01-30 00:00:00 | 600728 | 佳都科技 | 300462 | Shanghai Huaming Intelligent Terminal Equipment Co., Ltd. | factset_competitor | COMPETITOR | target | 2020-01-16 00:00:00 | 2020-01-16 00:00:00 | AFC system; ; ; ;  |
| 2024-01-30 00:00:00 | 600728 | 佳都科技 | 002152 | GRG Banking Equipment Co., Ltd. | factset_competitor | COMPETITOR | target | 2019-11-07 00:00:00 | 2019-11-07 00:00:00 | Security Solutions; ; ; ;  |

## Reading

- This is a data-availability probe, not a final table.
- `CUSTOMER` and `SUPPLIER` are converted relative to the focal firm, so the output labels `factset_upstream_supplier` and `factset_downstream_customer` are focal-relative.
- Partner rows are split into granular `factset_partner_*` types and can be collapsed later into a high-confidence collaborator group.
- The next improvement is to add an H-share/name-based crosswalk for dual-listed firms whose FactSet primary ticker is not the A-share code.

## Output Files

- `results/v42_factset_relationship_probe_20260607/factset_a_share_company_history.csv`
- `results/v42_factset_relationship_probe_20260607/factset_event_focal_map.csv`
- `results/v42_factset_relationship_probe_20260607/factset_event_relationship_links.csv`
- `results/v42_factset_relationship_probe_20260607/factset_relation_event_study.csv`
- `results/v42_factset_relationship_probe_20260607/factset_stacked_regressions.csv`
- `results/v42_factset_relationship_probe_20260607/factset_relation_panel.csv.gz`
