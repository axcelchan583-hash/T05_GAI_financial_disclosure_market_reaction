# v58 v56 FactSet supplier/customer benchmark

## Scope

- Input events: v56 expanded v52+v55 LLM-coded samples.
- Relationship source: FactSet Revere Supply Chain Relationships, already downloaded locally.
- Mapping: reuse v42 conservative A-share FactSet company history, then keep relationships overlapping the five-year pre-event window.
- Important distinction: this is broader FactSet Revere relationship coverage, not the narrow CSMAR/Qian-style listed supplier benchmark.

## Input And Mapping

- Event rows across requested samples: `969`
- FactSet A-share company-history rows: `72,570`

| sample_name | input_events | input_firms | mapped_events | mapped_firms | mapped_event_rate |
|---|---|---|---|---|---|
| A_Dfw_stack | 345.0 | 259.0 | 333.0 | 248.0 | 0.965217 |
| A_all | 203.0 | 160.0 | 199.0 | 156.0 | 0.980296 |
| A_first_firm | 160.0 | 160.0 | 156.0 | 156.0 | 0.975 |
| A_old363_reaudited_first | 119.0 | 119.0 | 115.0 | 115.0 | 0.966387 |
| Dfw_all | 142.0 | 123.0 | 134.0 | 116.0 | 0.943662 |

## FactSet Coverage

| sample_name | relation_type | input_events | linked_events | event_link_rate | linked_rows | related_firms | clean_car0p1_rows | clean_car0p1_events |
|---|---|---|---|---|---|---|---|---|
| A_Dfw_stack | factset_downstream_customer | 345.0 | 216.0 | 0.626087 | 1004.0 | 471.0 | 904.0 | 202.0 |
| A_Dfw_stack | factset_relationship_union | 345.0 | 283.0 | 0.82029 | 2537.0 | 1317.0 | 2219.0 | 273.0 |
| A_Dfw_stack | factset_upstream_supplier | 345.0 | 162.0 | 0.469565 | 1044.0 | 761.0 | 888.0 | 153.0 |
| A_all | factset_downstream_customer | 203.0 | 131.0 | 0.64532 | 608.0 | 307.0 | 554.0 | 125.0 |
| A_all | factset_relationship_union | 203.0 | 168.0 | 0.827586 | 1228.0 | 636.0 | 1100.0 | 161.0 |
| A_all | factset_upstream_supplier | 203.0 | 91.0 | 0.448276 | 332.0 | 236.0 | 294.0 | 86.0 |
| A_first_firm | factset_downstream_customer | 160.0 | 100.0 | 0.625 | 485.0 | 303.0 | 441.0 | 96.0 |
| A_first_firm | factset_relationship_union | 160.0 | 132.0 | 0.825 | 946.0 | 619.0 | 843.0 | 127.0 |
| A_first_firm | factset_upstream_supplier | 160.0 | 72.0 | 0.45 | 264.0 | 231.0 | 230.0 | 67.0 |
| A_old363_reaudited_first | factset_downstream_customer | 119.0 | 77.0 | 0.647059 | 367.0 | 250.0 | 337.0 | 75.0 |
| A_old363_reaudited_first | factset_relationship_union | 119.0 | 98.0 | 0.823529 | 758.0 | 530.0 | 680.0 | 96.0 |
| A_old363_reaudited_first | factset_upstream_supplier | 119.0 | 58.0 | 0.487395 | 230.0 | 206.0 | 201.0 | 55.0 |
| Dfw_all | factset_downstream_customer | 142.0 | 85.0 | 0.598592 | 396.0 | 286.0 | 350.0 | 77.0 |
| Dfw_all | factset_relationship_union | 142.0 | 115.0 | 0.809859 | 1309.0 | 944.0 | 1119.0 | 112.0 |
| Dfw_all | factset_upstream_supplier | 142.0 | 71.0 | 0.5 | 712.0 | 592.0 | 594.0 | 67.0 |

## FactSet Event Study

| sample_name | relation_type | window | mean | se | p | nobs | events | related_firms | median | positive_share | event_weighted_mean | event_weighted_p | event_weighted_events |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A_all | factset_downstream_customer | AR[0] | -0.000487 | 0.001242 | 0.694992 | 554.0 | 125.0 | 280.0 | -0.000717 | 0.471119 | -0.002986 | 0.036798 | 125.0 |
| A_all | factset_downstream_customer | CAR[0,+1] | -0.00333 | 0.001434 | 0.020226 | 554.0 | 125.0 | 280.0 | -0.003908 | 0.384477 | -0.004936 | 0.020672 | 125.0 |
| A_all | factset_upstream_supplier | AR[0] | 0.002358 | 0.001891 | 0.212294 | 294.0 | 86.0 | 206.0 | -0.000246 | 0.489796 | 0.000475 | 0.805464 | 86.0 |
| A_all | factset_upstream_supplier | CAR[0,+1] | 0.003938 | 0.003311 | 0.234277 | 294.0 | 86.0 | 206.0 | -0.000116 | 0.496599 | 4.6e-05 | 0.990038 | 86.0 |
| A_first_firm | factset_downstream_customer | AR[0] | -0.000606 | 0.001375 | 0.659535 | 441.0 | 96.0 | 276.0 | -0.000456 | 0.47619 | -0.002277 | 0.140552 | 96.0 |
| A_first_firm | factset_downstream_customer | CAR[0,+1] | -0.003427 | 0.001507 | 0.022965 | 441.0 | 96.0 | 276.0 | -0.003832 | 0.376417 | -0.004065 | 0.092635 | 96.0 |
| A_first_firm | factset_upstream_supplier | AR[0] | 0.001864 | 0.002032 | 0.359066 | 230.0 | 67.0 | 201.0 | -0.000232 | 0.491304 | -7.5e-05 | 0.970826 | 67.0 |
| A_first_firm | factset_upstream_supplier | CAR[0,+1] | 0.003364 | 0.003833 | 0.380163 | 230.0 | 67.0 | 201.0 | -0.000575 | 0.482609 | -0.0006 | 0.893149 | 67.0 |
| A_old363_reaudited_first | factset_downstream_customer | AR[0] | -0.000721 | 0.001742 | 0.678913 | 337.0 | 75.0 | 228.0 | -0.000585 | 0.480712 | -0.00278 | 0.137152 | 75.0 |
| A_old363_reaudited_first | factset_downstream_customer | CAR[0,+1] | -0.003474 | 0.001961 | 0.07647 | 337.0 | 75.0 | 228.0 | -0.004655 | 0.350148 | -0.004239 | 0.152147 | 75.0 |
| A_old363_reaudited_first | factset_upstream_supplier | AR[0] | 0.002167 | 0.00206 | 0.292704 | 201.0 | 55.0 | 178.0 | -0.000247 | 0.482587 | 0.000163 | 0.937023 | 55.0 |
| A_old363_reaudited_first | factset_upstream_supplier | CAR[0,+1] | 0.003849 | 0.004019 | 0.338242 | 201.0 | 55.0 | 178.0 | 0.000471 | 0.507463 | -0.002569 | 0.474494 | 55.0 |

## CSMAR vs FactSet

| source | sample_name | relation_type | window | mean | p | nobs | events | related_firms | event_weighted_mean | event_weighted_p |
|---|---|---|---|---|---|---|---|---|---|---|
| CSMAR listed supplier union | A_all | supplier_union | CAR[0,+1] | 0.012467 | 0.135437 | 21.0 | 12.0 | 20.0 |  |  |
| FactSet Revere | A_all | factset_downstream_customer | CAR[0,+1] | -0.00333 | 0.020226 | 554.0 | 125.0 | 280.0 | -0.004936 | 0.020672 |
| FactSet Revere | A_all | factset_upstream_supplier | CAR[0,+1] | 0.003938 | 0.234277 | 294.0 | 86.0 | 206.0 | 4.6e-05 | 0.990038 |

## Output Files

- `results/v58_v56_factset_supplier_benchmark_20260612/factset_event_focal_map.csv`
- `results/v58_v56_factset_supplier_benchmark_20260612/factset_event_relationship_links.csv`
- `results/v58_v56_factset_supplier_benchmark_20260612/factset_grouped_links.csv`
- `results/v58_v56_factset_supplier_benchmark_20260612/factset_relation_panel.csv.gz`
- `results/v58_v56_factset_supplier_benchmark_20260612/factset_coverage_summary.csv`
- `results/v58_v56_factset_supplier_benchmark_20260612/factset_event_study.csv`
- `results/v58_v56_factset_supplier_benchmark_20260612/csmar_vs_factset_supplier_check.csv`
- `results/v58_v56_factset_supplier_benchmark_20260612/v58_v56_factset_supplier_benchmark_20260612.xlsx`
