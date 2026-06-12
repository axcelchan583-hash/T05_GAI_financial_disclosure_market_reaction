# v60 Core Clean GenAI Launch Event Study

## Scope

- Input: v56 expanded A sample.
- Main strict sample `Core_clean_launch`: own GenAI model/app announcement, external-facing (`out=1`), launch/release/filing text hit, and no title-form noise such as board resolutions, investment, M&A, financing, framework agreements, annual reports, investor minutes, patents, or compute/capex projects.
- Ultra-strict sample `Core_realized_plus`: the same rule plus LLM field `realized=+`.
- Focal firm main timing uses strict next trading day because CNINFO disclosures are often released after market close. Peer and relation panels reuse v56/v57/v58 return panels, so they use the existing event-date-to-next-available-trading-day convention.

## Core Events

| event_date | focal_code | sec_name | announcement_title | out | mode | layer | realized |
|---|---|---|---|---|---|---|---|
| 2023-04-10 00:00:00 | 300418 | 昆仑万维 | 昆仑万维：关于发布大语言模型“天工”3.5的公告 | 1 | own | model | - |
| 2023-05-06 00:00:00 | 002230 | 科大讯飞 | 科大讯飞：关于讯飞星火认知大模型成果发布会的提示性公告 | 1 | own | model | + |
| 2023-10-12 00:00:00 | 002362 | 汉王科技 | 汉王科技：关于召开汉王天地大模型阶段成果发布会的提示性公告 | 1 | own | model | + |
| 2023-11-16 00:00:00 | 300075 | 数字政通 | 数字政通：关于公司发布新产品的公告 | 1 | own | model | + |
| 2023-11-20 00:00:00 | 300288 | 朗玛信息 | 朗玛信息：关于“39AI全科医生”大模型备案通过的公告 | 1 | own | model | - |
| 2024-02-21 00:00:00 | 002530 | 金财互联 | 金财互联：关于“欣智悦财税大模型算法”备案通过的公告 | 1 | own | model | + |
| 2024-12-24 00:00:00 | 837592 | 华信永道 | [临时公告]华信永道:关于大模型算法备案成功的公告 | 1 | own | model | + |
| 2025-09-03 00:00:00 | 002980 | 华盛昌 | 华盛昌：关于“DeepSense深度感测大模型”备案通过的自愿性信息披露公告 | 1 | own | model | - |
| 2025-09-25 00:00:00 | 300235 | 方直科技 | 方直科技：关于公司发布新产品的公告 | 1 | own | app | + |
| 2026-04-28 00:00:00 | 300075 | 数字政通 | 数字政通：关于公司发布新产品的公告 | 1 | own | app | + |

## Sample Counts

| sample_name | events | focal_firms | first_date | last_date | model_layer |
|---|---|---|---|---|---|
| Core_clean_launch_all | 10.0 | 9.0 | 2023-04-10 00:00:00 | 2026-04-28 00:00:00 | app;model |
| Core_clean_launch_first_firm | 9.0 | 9.0 | 2023-04-10 00:00:00 | 2025-09-25 00:00:00 | app;model |
| Core_realized_plus_all | 7.0 | 6.0 | 2023-05-06 00:00:00 | 2026-04-28 00:00:00 | app;model |
| Core_realized_plus_first_firm | 6.0 | 6.0 | 2023-05-06 00:00:00 | 2025-09-25 00:00:00 | app;model |

## Focal Firm Returns, Strict Next Trading Day

| sample_name | outcome_label | estimate | se | p | nobs | events | focal_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|
| Core_clean_launch_all | AR[0] | 0.007607 | 0.015985 | 0.634144 | 6.0 | 6.0 | 5.0 | -0.005785 | 0.333333 |
| Core_clean_launch_all | AR[+1] | 0.006479 | 0.019852 | 0.744157 | 6.0 | 6.0 | 5.0 | -0.00916 | 0.333333 |
| Core_clean_launch_all | CAR[0,+1] | 0.014086 | 0.035112 | 0.688294 | 6.0 | 6.0 | 5.0 | -0.015134 | 0.333333 |
| Core_clean_launch_all | CAR[-1,+1] | -0.027475 | 0.012995 | 0.034498 | 6.0 | 6.0 | 5.0 | -0.022978 | 0.166667 |
| Core_clean_launch_first_firm | AR[0] | 0.006213 | 0.019419 | 0.748992 | 5.0 | 5.0 | 5.0 | -0.008675 | 0.2 |
| Core_clean_launch_first_firm | AR[+1] | 0.009045 | 0.023252 | 0.69729 | 5.0 | 5.0 | 5.0 | -0.011968 | 0.4 |
| Core_clean_launch_first_firm | CAR[0,+1] | 0.015258 | 0.041897 | 0.715721 | 5.0 | 5.0 | 5.0 | -0.024971 | 0.2 |
| Core_clean_launch_first_firm | CAR[-1,+1] | -0.029282 | 0.015345 | 0.056366 | 5.0 | 5.0 | 5.0 | -0.023727 | 0.2 |
| Core_realized_plus_all | AR[0] | -0.009008 | 0.008222 | 0.273259 | 4.0 | 4.0 | 3.0 | -0.007949 | 0.25 |
| Core_realized_plus_all | AR[+1] | -0.018522 | 0.006774 | 0.006251 | 4.0 | 4.0 | 3.0 | -0.014823 | 0.0 |
| Core_realized_plus_all | CAR[0,+1] | -0.027529 | 0.011903 | 0.020729 | 4.0 | 4.0 | 3.0 | -0.032978 | 0.25 |
| Core_realized_plus_all | CAR[-1,+1] | -0.042382 | 0.013519 | 0.001719 | 4.0 | 4.0 | 3.0 | -0.042341 | 0.0 |
| Core_realized_plus_first_firm | AR[0] | -0.016869 | 0.007663 | 0.027704 | 3.0 | 3.0 | 3.0 | -0.013003 | 0.0 |
| Core_realized_plus_first_firm | AR[+1] | -0.022578 | 0.006473 | 0.000487 | 3.0 | 3.0 | 3.0 | -0.017678 | 0.0 |
| Core_realized_plus_first_firm | CAR[0,+1] | -0.039448 | 0.006492 | 0.0 | 3.0 | 3.0 | 3.0 | -0.040984 | 0.0 |
| Core_realized_plus_first_firm | CAR[-1,+1] | -0.050362 | 0.011523 | 1.2e-05 | 3.0 | 3.0 | 3.0 | -0.062453 | 0.0 |

## Product-Market Peer Returns

| sample_name | outcome_label | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|
| Core_clean_launch_all | AR[0] | -0.000718 | 0.007651 | 0.925235 | 77.0 | 9.0 | 72.0 | -0.003732 | 0.376623 |
| Core_clean_launch_all | CAR[0,+1] | 0.003731 | 0.005669 | 0.510399 | 77.0 | 9.0 | 72.0 | -0.001293 | 0.467532 |
| Core_clean_launch_first_firm | AR[0] | 0.001347 | 0.008104 | 0.867986 | 70.0 | 8.0 | 68.0 | -0.003532 | 0.4 |
| Core_clean_launch_first_firm | CAR[0,+1] | 0.006546 | 0.0055 | 0.233935 | 70.0 | 8.0 | 68.0 | -0.000297 | 0.485714 |
| Core_realized_plus_all | AR[0] | 0.007947 | 0.009256 | 0.390565 | 52.0 | 6.0 | 47.0 | -0.001266 | 0.461538 |
| Core_realized_plus_all | CAR[0,+1] | 0.006497 | 0.007199 | 0.366838 | 52.0 | 6.0 | 47.0 | -0.001479 | 0.461538 |
| Core_realized_plus_first_firm | AR[0] | 0.012507 | 0.009481 | 0.187131 | 45.0 | 5.0 | 43.0 | 0.00083 | 0.511111 |
| Core_realized_plus_first_firm | CAR[0,+1] | 0.011306 | 0.006479 | 0.080963 | 45.0 | 5.0 | 43.0 | -2.7e-05 | 0.488889 |

## Peer Minus Focal, Same Existing Event Clock

| sample_name | events | peer_minus_focal_mean | se | p | median | positive_share | mean_peer_car | mean_focal_car |
|---|---|---|---|---|---|---|---|---|
| Core_clean_launch_all | 6.0 | 0.027467 | 0.011866 | 0.020621 | 0.02454 | 0.833333 | -0.006487 | -0.033954 |
| Core_clean_launch_first_firm | 5.0 | 0.035427 | 0.010777 | 0.001012 | 0.032949 | 1.0 | -0.0029 | -0.038326 |
| Core_realized_plus_all | 4.0 | 0.019341 | 0.01173 | 0.099185 | 0.02454 | 0.75 | -0.004519 | -0.02386 |
| Core_realized_plus_first_firm | 3.0 | 0.029898 | 0.00723 | 3.5e-05 | 0.032949 | 1.0 | 0.002114 | -0.027784 |

## CSMAR Listed Supplier Benchmark

| sample_name | edge_family | outcome_label | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|---|
| Core_clean_launch_all | union | AR[0] | -0.011057 | 0.001615 | 0.0 | 2.0 | 1.0 | 2.0 | -0.011057 | 0.0 |
| Core_clean_launch_all | union | CAR[0,+1] | -0.01147 | 0.000493 | 0.0 | 2.0 | 1.0 | 2.0 | -0.01147 | 0.0 |
| Core_clean_launch_first_firm | union | AR[0] | -0.011057 | 0.001615 | 0.0 | 2.0 | 1.0 | 2.0 | -0.011057 | 0.0 |
| Core_clean_launch_first_firm | union | CAR[0,+1] | -0.01147 | 0.000493 | 0.0 | 2.0 | 1.0 | 2.0 | -0.01147 | 0.0 |

## FactSet Supplier/Customer Benchmark

| sample_name | relation_type | outcome_label | mean | se | p | nobs | events | related_firms | median | positive_share | event_weighted_mean | event_weighted_p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Core_clean_launch_all | factset_downstream_customer | AR[0] | -0.002098 | 0.002973 | 0.480408 | 19.0 | 6.0 | 15.0 | -0.001548 | 0.421053 | 0.000328 | 0.930353 |
| Core_clean_launch_all | factset_downstream_customer | CAR[0,+1] | 0.001142 | 0.006538 | 0.861361 | 19.0 | 6.0 | 15.0 | -0.002722 | 0.421053 | 0.007156 | 0.46735 |
| Core_clean_launch_all | factset_upstream_supplier | AR[0] | -0.01242 | 0.006148 | 0.043364 | 12.0 | 3.0 | 11.0 | -0.015423 | 0.333333 | -0.014513 | 0.308256 |
| Core_clean_launch_all | factset_upstream_supplier | CAR[0,+1] | -0.013754 | 0.008018 | 0.086297 | 12.0 | 3.0 | 11.0 | -0.014466 | 0.333333 | -0.021719 | 0.107949 |
| Core_clean_launch_first_firm | factset_downstream_customer | AR[0] | -0.002098 | 0.002973 | 0.480408 | 19.0 | 6.0 | 15.0 | -0.001548 | 0.421053 | 0.000328 | 0.930353 |
| Core_clean_launch_first_firm | factset_downstream_customer | CAR[0,+1] | 0.001142 | 0.006538 | 0.861361 | 19.0 | 6.0 | 15.0 | -0.002722 | 0.421053 | 0.007156 | 0.46735 |
| Core_clean_launch_first_firm | factset_upstream_supplier | AR[0] | -0.01242 | 0.006148 | 0.043364 | 12.0 | 3.0 | 11.0 | -0.015423 | 0.333333 | -0.014513 | 0.308256 |
| Core_clean_launch_first_firm | factset_upstream_supplier | CAR[0,+1] | -0.013754 | 0.008018 | 0.086297 | 12.0 | 3.0 | 11.0 | -0.014466 | 0.333333 | -0.021719 | 0.107949 |
| Core_realized_plus_all | factset_downstream_customer | AR[0] | -0.001778 | 0.003213 | 0.579931 | 18.0 | 5.0 | 15.0 | -0.001251 | 0.444444 | 0.001964 | 0.634406 |
| Core_realized_plus_all | factset_downstream_customer | CAR[0,+1] | 0.001753 | 0.00689 | 0.799214 | 18.0 | 5.0 | 15.0 | -0.00254 | 0.444444 | 0.010557 | 0.350813 |
| Core_realized_plus_all | factset_upstream_supplier | AR[0] | -0.014114 | 0.007122 | 0.0475 | 11.0 | 2.0 | 10.0 | -0.016126 | 0.272727 | -0.02488 | 0.141373 |
| Core_realized_plus_all | factset_upstream_supplier | CAR[0,+1] | -0.014086 | 0.008887 | 0.112966 | 11.0 | 2.0 | 10.0 | -0.016006 | 0.363636 | -0.02753 | 0.192538 |
| Core_realized_plus_first_firm | factset_downstream_customer | AR[0] | -0.001778 | 0.003213 | 0.579931 | 18.0 | 5.0 | 15.0 | -0.001251 | 0.444444 | 0.001964 | 0.634406 |
| Core_realized_plus_first_firm | factset_downstream_customer | CAR[0,+1] | 0.001753 | 0.00689 | 0.799214 | 18.0 | 5.0 | 15.0 | -0.00254 | 0.444444 | 0.010557 | 0.350813 |
| Core_realized_plus_first_firm | factset_upstream_supplier | AR[0] | -0.014114 | 0.007122 | 0.0475 | 11.0 | 2.0 | 10.0 | -0.016126 | 0.272727 | -0.02488 | 0.141373 |
| Core_realized_plus_first_firm | factset_upstream_supplier | CAR[0,+1] | -0.014086 | 0.008887 | 0.112966 | 11.0 | 2.0 | 10.0 | -0.016006 | 0.363636 | -0.02753 | 0.192538 |

## Output Files

- `results/v60_core_clean_launch_event_study_20260612/core_event_samples.csv`
- `results/v60_core_clean_launch_event_study_20260612/core_classification_all_A.csv`
- `results/v60_core_clean_launch_event_study_20260612/focal_returns_strict_next_day_summary.csv`
- `results/v60_core_clean_launch_event_study_20260612/peer_returns_summary.csv`
- `results/v60_core_clean_launch_event_study_20260612/csmar_supplier_summary.csv`
- `results/v60_core_clean_launch_event_study_20260612/factset_relation_summary.csv`
- `results/v60_core_clean_launch_event_study_20260612/peer_minus_focal_summary.csv`
- `results/v60_core_clean_launch_event_study_20260612/v60_core_clean_launch_event_study_20260612.xlsx`
