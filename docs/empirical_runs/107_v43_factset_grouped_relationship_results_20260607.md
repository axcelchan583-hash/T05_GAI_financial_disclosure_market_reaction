# v43 FactSet Grouped Relationship Results

Date: 2026-06-07

## Scope

This run reuses v42 FactSet A-share relationship links and collapses granular partner subtypes into interpretable groups. It does not rescan the FactSet 20GB relationship file.

Grouped relation types:

- `factset_competitor`
- `factset_upstream_supplier`
- `factset_downstream_customer`
- `factset_partner_high_confidence`: non-investment operational partner types such as research collaboration, joint venture, technology, licensing, distribution, manufacturing, and marketing.
- `factset_partner_investment`: `PARTNER-INVESTO` and `PARTNER-EINVEST`.
- `factset_partner_all`
- `factset_relationship_union`

## Sample Flow

| relation_type | linked_rows | events | focal_firms | related_firms | clean_car0p1_rows | clean_car0p1_events | clean_related_firms |
|---|---|---|---|---|---|---|---|
| factset_competitor | 343.0 | 137.0 | 137.0 | 275.0 | 299.0 | 129.0 | 241.0 |
| factset_downstream_customer | 1078.0 | 221.0 | 221.0 | 637.0 | 946.0 | 207.0 | 551.0 |
| factset_partner_all | 443.0 | 157.0 | 157.0 | 336.0 | 388.0 | 149.0 | 292.0 |
| factset_partner_high_confidence | 354.0 | 133.0 | 133.0 | 266.0 | 311.0 | 126.0 | 233.0 |
| factset_partner_investment | 98.0 | 56.0 | 56.0 | 94.0 | 86.0 | 54.0 | 83.0 |
| factset_relationship_union | 2934.0 | 297.0 | 297.0 | 1678.0 | 2513.0 | 288.0 | 1408.0 |
| factset_upstream_supplier | 1255.0 | 184.0 | 184.0 | 940.0 | 1039.0 | 168.0 | 769.0 |

## Coverage

| relation_group | relation_type | rows | events | focal_firms | related_firms | rel_types |
|---|---|---|---|---|---|---|
| competitor | factset_competitor | 343.0 | 137.0 | 137.0 | 275.0 | COMPETITOR |
| customer | factset_downstream_customer | 1078.0 | 221.0 | 221.0 | 637.0 | CUSTOMER;SUPPLIER |
| factset_union | factset_relationship_union | 2934.0 | 297.0 | 297.0 | 1678.0 | COMPETITOR;CUSTOMER;PARTNER-DISTRIB;PARTNER-EINVEST;PARTNER-INVESTO;PARTNER-JVENTUR;PARTNER-LICENIN;PARTNER-LICENOT;PARTNER-MANUFAC;PARTNER-RESCOLB;SUPPLIER |
| partner_all | factset_partner_all | 443.0 | 157.0 | 157.0 | 336.0 | PARTNER-DISTRIB;PARTNER-EINVEST;PARTNER-INVESTO;PARTNER-JVENTUR;PARTNER-LICENIN;PARTNER-LICENOT;PARTNER-MANUFAC;PARTNER-MARKTNG;PARTNER-RESCOLB |
| partner_high_confidence | factset_partner_high_confidence | 354.0 | 133.0 | 133.0 | 266.0 | PARTNER-DISTRIB;PARTNER-JVENTUR;PARTNER-LICENIN;PARTNER-LICENOT;PARTNER-MANUFAC;PARTNER-MARKTNG;PARTNER-RESCOLB |
| partner_investment | factset_partner_investment | 98.0 | 56.0 | 56.0 | 94.0 | PARTNER-EINVEST;PARTNER-INVESTO |
| supplier | factset_upstream_supplier | 1255.0 | 184.0 | 184.0 | 940.0 | CUSTOMER;SUPPLIER |

## CAR[0,+1] by Grouped Relation Type

| relation_type | mean | se | p | nobs | events | related_firms | positive_share | event_weighted_mean | event_weighted_p | event_weighted_events |
|---|---|---|---|---|---|---|---|---|---|---|
| factset_competitor | -0.008111 | 0.003179 | 0.010718 | 299.0 | 129.0 | 241.0 | 0.384615 | -0.009223 | 0.000491 | 129.0 |
| factset_downstream_customer | -0.000589 | 0.00204 | 0.772947 | 946.0 | 207.0 | 551.0 | 0.440803 | -0.00264 | 0.194337 | 207.0 |
| factset_partner_all | -0.003072 | 0.002749 | 0.263782 | 388.0 | 149.0 | 292.0 | 0.409794 | 0.000563 | 0.815186 | 149.0 |
| factset_partner_high_confidence | -0.00634 | 0.003015 | 0.035469 | 311.0 | 126.0 | 233.0 | 0.37299 | -0.002104 | 0.439232 | 126.0 |
| factset_partner_investment | 0.006571 | 0.004544 | 0.148184 | 86.0 | 54.0 | 83.0 | 0.511628 | 0.008396 | 0.037833 | 54.0 |
| factset_relationship_union | -0.002845 | 0.002887 | 0.324369 | 2513.0 | 288.0 | 1408.0 | 0.421409 | -0.002065 | 0.189824 | 288.0 |
| factset_upstream_supplier | -0.004144 | 0.005619 | 0.460825 | 1039.0 | 168.0 | 769.0 | 0.407122 | 0.000614 | 0.804281 | 168.0 |

## Stacked Event-FE Regressions

Baseline is the existing product-market competitor panel, with overlapping product-competitor event-firm rows removed.

| sample | outcome | regressor | coef_event_fmt | p_event_cluster | coef_two_way_fmt | p_two_way | nobs | events | related_firms | r2 |
|---|---|---|---|---|---|---|---|---|---|---|
| core_grouped_relations_vs_product_competitor | peer_ar_m1_mm | is_factset_competitor | 0.0014 | 0.434937 | 0.0014 | 0.438955 | 4837.0 | 277.0 | 2118.0 | 0.27254 |
| core_grouped_relations_vs_product_competitor | peer_ar_m1_mm | is_factset_upstream_supplier | 0.0001 | 0.956441 | 0.0001 | 0.956999 | 4837.0 | 277.0 | 2118.0 | 0.27254 |
| core_grouped_relations_vs_product_competitor | peer_ar_m1_mm | is_factset_downstream_customer | -0.0007 | 0.627899 | -0.0007 | 0.633225 | 4837.0 | 277.0 | 2118.0 | 0.27254 |
| core_grouped_relations_vs_product_competitor | peer_ar_m1_mm | is_factset_partner_high_confidence | -0.0007 | 0.627401 | -0.0007 | 0.620354 | 4837.0 | 277.0 | 2118.0 | 0.27254 |
| core_grouped_relations_vs_product_competitor | peer_ar_m1_mm | is_factset_partner_investment | 0.0011 | 0.691176 | 0.0011 | 0.693251 | 4837.0 | 277.0 | 2118.0 | 0.27254 |
| core_grouped_relations_vs_product_competitor | peer_ar0_mm | is_factset_competitor | 0.0005 | 0.775126 | 0.0005 | 0.768212 | 4837.0 | 277.0 | 2118.0 | 0.291224 |
| core_grouped_relations_vs_product_competitor | peer_ar0_mm | is_factset_upstream_supplier | 0.0019 | 0.223998 | 0.0019 | 0.229738 | 4837.0 | 277.0 | 2118.0 | 0.291224 |
| core_grouped_relations_vs_product_competitor | peer_ar0_mm | is_factset_downstream_customer | -0.0002 | 0.923006 | -0.0002 | 0.921898 | 4837.0 | 277.0 | 2118.0 | 0.291224 |
| core_grouped_relations_vs_product_competitor | peer_ar0_mm | is_factset_partner_high_confidence | -0.0005 | 0.769549 | -0.0005 | 0.790151 | 4837.0 | 277.0 | 2118.0 | 0.291224 |
| core_grouped_relations_vs_product_competitor | peer_ar0_mm | is_factset_partner_investment | 0.0038* | 0.094195 | 0.0038* | 0.089221 | 4837.0 | 277.0 | 2118.0 | 0.291224 |
| core_grouped_relations_vs_product_competitor | peer_ar_p1_mm | is_factset_competitor | -0.0035** | 0.024816 | -0.0035** | 0.033668 | 4837.0 | 277.0 | 2118.0 | 0.293235 |
| core_grouped_relations_vs_product_competitor | peer_ar_p1_mm | is_factset_upstream_supplier | 0.0029* | 0.083459 | 0.0029* | 0.084145 | 4837.0 | 277.0 | 2118.0 | 0.293235 |
| core_grouped_relations_vs_product_competitor | peer_ar_p1_mm | is_factset_downstream_customer | 0.0009 | 0.591569 | 0.0009 | 0.588754 | 4837.0 | 277.0 | 2118.0 | 0.293235 |
| core_grouped_relations_vs_product_competitor | peer_ar_p1_mm | is_factset_partner_high_confidence | 0.0012 | 0.512367 | 0.0012 | 0.517558 | 4837.0 | 277.0 | 2118.0 | 0.293235 |
| core_grouped_relations_vs_product_competitor | peer_ar_p1_mm | is_factset_partner_investment | 0.0065** | 0.018888 | 0.0065** | 0.017495 | 4837.0 | 277.0 | 2118.0 | 0.293235 |
| core_grouped_relations_vs_product_competitor | peer_car_0_p1_mm | is_factset_competitor | -0.0030 | 0.193981 | -0.0030 | 0.207396 | 4837.0 | 277.0 | 2118.0 | 0.321417 |
| core_grouped_relations_vs_product_competitor | peer_car_0_p1_mm | is_factset_upstream_supplier | 0.0048* | 0.05717 | 0.0048* | 0.055546 | 4837.0 | 277.0 | 2118.0 | 0.321417 |
| core_grouped_relations_vs_product_competitor | peer_car_0_p1_mm | is_factset_downstream_customer | 0.0008 | 0.747241 | 0.0008 | 0.744517 | 4837.0 | 277.0 | 2118.0 | 0.321417 |
| core_grouped_relations_vs_product_competitor | peer_car_0_p1_mm | is_factset_partner_high_confidence | 0.0006 | 0.822198 | 0.0006 | 0.838994 | 4837.0 | 277.0 | 2118.0 | 0.321417 |
| core_grouped_relations_vs_product_competitor | peer_car_0_p1_mm | is_factset_partner_investment | 0.0103*** | 0.002856 | 0.0103*** | 0.002151 | 4837.0 | 277.0 | 2118.0 | 0.321417 |
| core_grouped_relations_vs_product_competitor | peer_car_m1_p1_mm | is_factset_competitor | -0.0017 | 0.527678 | -0.0017 | 0.533139 | 4837.0 | 277.0 | 2118.0 | 0.283102 |
| core_grouped_relations_vs_product_competitor | peer_car_m1_p1_mm | is_factset_upstream_supplier | 0.0049* | 0.075075 | 0.0049* | 0.078425 | 4837.0 | 277.0 | 2118.0 | 0.283102 |
| core_grouped_relations_vs_product_competitor | peer_car_m1_p1_mm | is_factset_downstream_customer | 0.0000 | 0.988411 | 0.0000 | 0.988348 | 4837.0 | 277.0 | 2118.0 | 0.283102 |
| core_grouped_relations_vs_product_competitor | peer_car_m1_p1_mm | is_factset_partner_high_confidence | -0.0000 | 0.987898 | -0.0000 | 0.988714 | 4837.0 | 277.0 | 2118.0 | 0.283102 |
| core_grouped_relations_vs_product_competitor | peer_car_m1_p1_mm | is_factset_partner_investment | 0.0114*** | 0.00772 | 0.0114*** | 0.006235 | 4837.0 | 277.0 | 2118.0 | 0.283102 |
| factset_partner_all_vs_product_competitor | peer_ar_m1_mm | is_factset_partner_all | -0.0003 | 0.813878 | -0.0003 | 0.809045 | 1622.0 | 140.0 | 919.0 | 0.320087 |
| factset_partner_all_vs_product_competitor | peer_ar0_mm | is_factset_partner_all | -0.0002 | 0.928521 | -0.0002 | 0.931254 | 1622.0 | 140.0 | 919.0 | 0.372807 |
| factset_partner_all_vs_product_competitor | peer_ar_p1_mm | is_factset_partner_all | 0.0022 | 0.246617 | 0.0022 | 0.242811 | 1622.0 | 140.0 | 919.0 | 0.330004 |
| factset_partner_all_vs_product_competitor | peer_car_0_p1_mm | is_factset_partner_all | 0.0021 | 0.481161 | 0.0021 | 0.495808 | 1622.0 | 140.0 | 919.0 | 0.401813 |
| factset_partner_all_vs_product_competitor | peer_car_m1_p1_mm | is_factset_partner_all | 0.0017 | 0.608984 | 0.0017 | 0.613818 | 1622.0 | 140.0 | 919.0 | 0.35586 |
| factset_relationship_union_vs_product_competitor | peer_ar_m1_mm | is_factset_relationship_union | -0.0004 | 0.696767 | -0.0004 | 0.701181 | 4550.0 | 258.0 | 2086.0 | 0.272011 |
| factset_relationship_union_vs_product_competitor | peer_ar0_mm | is_factset_relationship_union | 0.0007 | 0.581228 | 0.0007 | 0.577841 | 4550.0 | 258.0 | 2086.0 | 0.296759 |
| factset_relationship_union_vs_product_competitor | peer_ar_p1_mm | is_factset_relationship_union | 0.0011 | 0.390065 | 0.0011 | 0.385554 | 4550.0 | 258.0 | 2086.0 | 0.289771 |
| factset_relationship_union_vs_product_competitor | peer_car_0_p1_mm | is_factset_relationship_union | 0.0017 | 0.355219 | 0.0017 | 0.353918 | 4550.0 | 258.0 | 2086.0 | 0.321246 |
| factset_relationship_union_vs_product_competitor | peer_car_m1_p1_mm | is_factset_relationship_union | 0.0013 | 0.513094 | 0.0013 | 0.512132 | 4550.0 | 258.0 | 2086.0 | 0.285721 |

## Reading

- FactSet competitor is strongly negative in the raw event-study mean.
- FactSet supplier/customer are much larger than CSMAR supply-chain links but do not show a positive absolute CAR in this first pass.
- Investment-type partners show the clearest positive relative coefficient versus product-market competitors, but this is not the same as operational GenAI collaboration.
- High-confidence operational partners are not yet positive; they need manual validation or a narrower theory before becoming a main collaborator Y.

## Output Files

- `results/v43_factset_grouped_relationship_results_20260607/factset_grouped_links.csv`
- `results/v43_factset_grouped_relationship_results_20260607/factset_grouped_relation_panel.csv.gz`
- `results/v43_factset_grouped_relationship_results_20260607/factset_grouped_event_study.csv`
- `results/v43_factset_grouped_relationship_results_20260607/factset_grouped_stacked_regressions.csv`
