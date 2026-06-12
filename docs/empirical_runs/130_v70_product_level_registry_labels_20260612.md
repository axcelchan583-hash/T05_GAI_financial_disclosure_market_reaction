# v70 Product-Level Registry Labels

## Purpose

- Re-labels disclosure events using product-level registry text matches, not only firm-level registry existence.
- Preserves v68 firm-level timing for comparison.
- Separates strict event-ready product D1 dates from routine formal-file mentions.

## Outputs

- `results/v70_product_level_registry_labels_20260612/event_product_level_registry_labels.csv`
- `results/v70_product_level_registry_labels_20260612/event_product_match_rows.csv`
- `results/v70_product_level_registry_labels_20260612/strict_product_d1_firm_dates.csv`
- `results/v70_product_level_registry_labels_20260612/product_level_event_counts.csv`
- `results/v70_product_level_registry_labels_20260612/firm_vs_product_level_counts.csv`
- `results/v70_product_level_registry_labels_20260612/peer_car_by_product_level_timing.csv`
- `results/v70_product_level_registry_labels_20260612/focal_car_by_product_level_timing.csv`
- `results/v70_product_level_registry_labels_20260612/v70_product_level_registry_labels_20260612.xlsx`

## Product-Level Event Counts

| sample_name | event_type | firm_level_verification_timing_v68 | product_level_verification_timing | product_level_verification_type | events | firms | strict_product_d1_events |
|---|---|---|---|---|---|---|---|
| A_Dfw_stack | A | later_verified | no_product_match_recent_censored | no_product_match | 1 | 1 | 0 |
| A_Dfw_stack | A | unmatched_ambiguous | no_product_match_recent_censored | no_product_match | 22 | 20 | 0 |
| A_Dfw_stack | A | verified_at_event | no_product_match_recent_censored | no_product_match | 3 | 3 | 0 |
| A_Dfw_stack | A | later_verified | no_product_text_match | no_product_match | 18 | 17 | 0 |
| A_Dfw_stack | A | never_verified | no_product_text_match | no_product_match | 141 | 112 | 0 |
| A_Dfw_stack | A | verified_at_event | no_product_text_match | no_product_match | 7 | 6 | 0 |
| A_Dfw_stack | A | later_verified | product_later_verified | deep_synthesis | 1 | 1 | 0 |
| A_Dfw_stack | A | later_verified | product_later_verified | self_filing | 7 | 5 | 4 |
| A_Dfw_stack | A | verified_at_event | product_verified_at_event | deep_synthesis | 1 | 1 | 0 |
| A_Dfw_stack | A | verified_at_event | product_verified_at_event | self_filing | 2 | 2 | 0 |
| A_Dfw_stack | D-fw | later_verified | no_product_match_recent_censored | no_product_match | 1 | 1 | 0 |
| A_Dfw_stack | D-fw | unmatched_ambiguous | no_product_match_recent_censored | no_product_match | 23 | 23 | 0 |
| A_Dfw_stack | D-fw | verified_at_event | no_product_match_recent_censored | no_product_match | 3 | 3 | 0 |
| A_Dfw_stack | D-fw | later_verified | no_product_text_match | no_product_match | 17 | 15 | 0 |
| A_Dfw_stack | D-fw | never_verified | no_product_text_match | no_product_match | 94 | 78 | 0 |
| A_Dfw_stack | D-fw | verified_at_event | no_product_text_match | no_product_match | 3 | 3 | 0 |
| A_Dfw_stack | D-fw | later_verified | product_later_verified | app_registration | 1 | 1 | 0 |
| A_all | A | later_verified | no_product_match_recent_censored | no_product_match | 1 | 1 | 0 |
| A_all | A | unmatched_ambiguous | no_product_match_recent_censored | no_product_match | 22 | 20 | 0 |
| A_all | A | verified_at_event | no_product_match_recent_censored | no_product_match | 3 | 3 | 0 |
| A_all | A | later_verified | no_product_text_match | no_product_match | 18 | 17 | 0 |
| A_all | A | never_verified | no_product_text_match | no_product_match | 141 | 112 | 0 |
| A_all | A | verified_at_event | no_product_text_match | no_product_match | 7 | 6 | 0 |
| A_all | A | later_verified | product_later_verified | deep_synthesis | 1 | 1 | 0 |
| A_all | A | later_verified | product_later_verified | self_filing | 7 | 5 | 4 |
| A_all | A | verified_at_event | product_verified_at_event | deep_synthesis | 1 | 1 | 0 |
| A_all | A | verified_at_event | product_verified_at_event | self_filing | 2 | 2 | 0 |
| A_first_firm | A | later_verified | no_product_match_recent_censored | no_product_match | 1 | 1 | 0 |
| A_first_firm | A | unmatched_ambiguous | no_product_match_recent_censored | no_product_match | 15 | 15 | 0 |
| A_first_firm | A | verified_at_event | no_product_match_recent_censored | no_product_match | 3 | 3 | 0 |
| A_first_firm | A | later_verified | no_product_text_match | no_product_match | 17 | 17 | 0 |
| A_first_firm | A | never_verified | no_product_text_match | no_product_match | 112 | 112 | 0 |
| A_first_firm | A | verified_at_event | no_product_text_match | no_product_match | 4 | 4 | 0 |
| A_first_firm | A | later_verified | product_later_verified | deep_synthesis | 1 | 1 | 0 |
| A_first_firm | A | later_verified | product_later_verified | self_filing | 5 | 5 | 4 |
| A_first_firm | A | verified_at_event | product_verified_at_event | deep_synthesis | 1 | 1 | 0 |
| A_first_firm | A | verified_at_event | product_verified_at_event | self_filing | 1 | 1 | 0 |

## Firm-Level v68 vs Product-Level Match

| sample_name | event_type | firm_level_verification_timing_v68 | product_level_match | events | firms |
|---|---|---|---|---|---|
| A_Dfw_stack | A | later_verified | 0 | 19 | 18 |
| A_Dfw_stack | A | later_verified | 1 | 8 | 6 |
| A_Dfw_stack | A | never_verified | 0 | 141 | 112 |
| A_Dfw_stack | A | unmatched_ambiguous | 0 | 22 | 20 |
| A_Dfw_stack | A | verified_at_event | 0 | 10 | 9 |
| A_Dfw_stack | A | verified_at_event | 1 | 3 | 3 |
| A_Dfw_stack | D-fw | later_verified | 0 | 18 | 16 |
| A_Dfw_stack | D-fw | later_verified | 1 | 1 | 1 |
| A_Dfw_stack | D-fw | never_verified | 0 | 94 | 78 |
| A_Dfw_stack | D-fw | unmatched_ambiguous | 0 | 23 | 23 |
| A_Dfw_stack | D-fw | verified_at_event | 0 | 6 | 6 |
| A_all | A | later_verified | 0 | 19 | 18 |
| A_all | A | later_verified | 1 | 8 | 6 |
| A_all | A | never_verified | 0 | 141 | 112 |
| A_all | A | unmatched_ambiguous | 0 | 22 | 20 |
| A_all | A | verified_at_event | 0 | 10 | 9 |
| A_all | A | verified_at_event | 1 | 3 | 3 |
| A_first_firm | A | later_verified | 0 | 18 | 18 |
| A_first_firm | A | later_verified | 1 | 6 | 6 |
| A_first_firm | A | never_verified | 0 | 112 | 112 |
| A_first_firm | A | unmatched_ambiguous | 0 | 15 | 15 |
| A_first_firm | A | verified_at_event | 0 | 7 | 7 |
| A_first_firm | A | verified_at_event | 1 | 2 | 2 |

## Strict Product D1 Firm-Dates

| formal_first_date | listed_code | listed_name | products | verification_types | matched_terms | item_names | title | announcement_id | event_id | announcement_title | product_level_verification_timing | in_old_A_all_same_firm_date |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2023-04-10 | 300418 | 昆仑万维 | 5 | deep_synthesis;self_filing | “天工”;天工 | “天工”大模型;天工图生文算法;天工图生文算法-1;天工文生图算法;天工文生图算法-1 | 昆仑万维：关于发布大语言模型“天工”3.5的公告 | 1216367373 | 1216367373 | 昆仑万维：关于发布大语言模型“天工”3.5的公告 | product_later_verified | 1 |
| 2023-05-06 | 002230 | 科大讯飞 | 3 | deep_synthesis;self_filing | 星火认知大模型;讯飞星火认知大模型 | 星火认知大模型;讯飞星火认知大模型算法;讯飞星火认知大模型算法-SparkDesk | 科大讯飞：关于讯飞星火认知大模型成果发布会的提示性公告 | 1216758016 | 1216758016 | 科大讯飞：关于讯飞星火认知大模型成果发布会的提示性公告 | product_later_verified | 1 |
| 2023-05-12 | 300288 | 朗玛信息 | 2 | deep_synthesis;self_filing | 39AI全科医生 | 39AI全科医生;39健康医疗内容生成算法 | 关于召开国家健康医疗大数据西部中心人工智能建设成果——“朗玛·39AI全科医生”发布会的提示性公告 | 1216811847 |  |  |  | 0 |
| 2023-10-12 | 002362 | 汉王科技 | 3 | deep_synthesis;self_filing | 天地大模型;汉王天地大模型 | 天地大模型;天地大模型算法;汉王天地大模型算法 | 汉王科技：关于召开汉王天地大模型阶段成果发布会的提示性公告 | 1218014039 | 1218014039 | 汉王科技：关于召开汉王天地大模型阶段成果发布会的提示性公告 | product_later_verified | 1 |
| 2024-03-23 | 688343 | 云天励飞 | 1 | self_filing | 云天天书 | 云天天书大模型 | 云天励飞：关于收购深圳市岍丞技术有限公司股权暨开展新业务的公告 | 1219388587 |  |  |  | 0 |
| 2024-07-24 | 300133 | 华策影视 | 1 | self_filing | “有风” | “有风”大模型 | 华策影视：关于全资子公司与专业投资机构共同投资的公告 | 1220720345 |  |  |  | 0 |
| 2025-04-15 | 688088 | 虹软科技 | 3 | deep_synthesis;self_filing | ArcMuse计算技术引擎;PhotoStudio® AI | ArcMuse计算技术引擎;PSAI内容深度合成类算法;PSAI试衣视频生成算法 | 虹软科技：关于使用剩余超募资金投资建设新项目的公告 | 1223097344 |  |  |  | 0 |
| 2025-09-03 | 002980 | 华盛昌 | 2 | deep_synthesis;self_filing | DeepSense深度感测大模型 | DeepSense深度感测大模型;DeepSense深度感测大模型算法 | 华盛昌：关于“DeepSense深度感测大模型”备案通过的自愿性信息披露公告 | 1224635424 | 1224635424 | 华盛昌：关于“DeepSense深度感测大模型”备案通过的自愿性信息披露公告 | product_later_verified | 1 |
| 2025-09-17 | 002929 | 润建股份 | 1 | self_filing | 曲尺通信运维大模型 | 曲尺通信运维大模型 | 润建股份：关于中标候选人公示的提示性公告 | 1224664616 |  |  |  | 0 |
| 2025-11-20 | 002152 | 广电运通 | 1 | self_filing | 望道 | 望道 | 广电运通：关于收到中标通知书的公告 | 1224814906 |  |  |  | 0 |

## Peer CAR Diagnostic

| sample_name | event_type | verification_timing | verification_type | nobs | events | focal_firms | mean | se | z | p | median | positive_share | event_weighted_nobs | event_weighted_mean | event_weighted_se | event_weighted_p | event_weighted_median | event_weighted_positive_share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A_Dfw_stack | A | no_product_match_recent_censored | no_product_match | 174 | 20 | 18 | -0.0064 | 0.0039 | -1.6478 | 0.0994 | -0.0087 | 0.3621 | 18 | -0.0065 | 0.0065 | 0.3128 | -0.0098 | 0.2222 |
| A_Dfw_stack | A | no_product_text_match | no_product_match | 1417 | 151 | 122 | -0.0028 | 0.0014 | -2.0691 | 0.0385 | -0.0038 | 0.4474 | 151 | -0.0028 | 0.0028 | 0.3199 | -0.0036 | 0.4371 |
| A_Dfw_stack | A | product_later_verified | deep_synthesis | 8 | 1 | 1 | -0.0476 | 0.0164 | -2.8980 | 0.0038 | -0.0439 | 0.1250 | 1 | -0.0476 |  |  | -0.0476 | 0.0000 |
| A_Dfw_stack | A | product_later_verified | self_filing | 69 | 7 | 5 | -0.0116 | 0.0118 | -0.9840 | 0.3251 | -0.0054 | 0.3768 | 7 | -0.0115 | 0.0151 | 0.4475 | -0.0081 | 0.2857 |
| A_Dfw_stack | A | product_verified_at_event | self_filing | 20 | 2 | 2 | 0.0213 | 0.0116 | 1.8423 | 0.0654 | 0.0116 | 0.6500 | 2 | 0.0213 | 0.0226 | 0.3446 | 0.0213 | 0.5000 |
| A_Dfw_stack | D-fw | no_product_match_recent_censored | no_product_match | 219 | 25 | 25 | 0.0030 | 0.0031 | 0.9695 | 0.3323 | 0.0011 | 0.5160 | 23 | 0.0024 | 0.0041 | 0.5667 | 0.0041 | 0.5217 |
| A_Dfw_stack | D-fw | no_product_text_match | no_product_match | 992 | 105 | 89 | 0.0021 | 0.0016 | 1.3377 | 0.1810 | -0.0022 | 0.4698 | 105 | 0.0023 | 0.0030 | 0.4349 | 0.0001 | 0.5048 |
| A_Dfw_stack | D-fw | product_later_verified | app_registration | 10 | 1 | 1 | 0.0183 | 0.0147 | 1.2392 | 0.2153 | 0.0064 | 0.6000 | 1 | 0.0183 |  |  | 0.0183 | 1.0000 |
| A_all | A | no_product_match_recent_censored | no_product_match | 174 | 20 | 18 | -0.0064 | 0.0039 | -1.6478 | 0.0994 | -0.0087 | 0.3621 | 18 | -0.0065 | 0.0065 | 0.3128 | -0.0098 | 0.2222 |
| A_all | A | no_product_text_match | no_product_match | 1417 | 151 | 122 | -0.0028 | 0.0014 | -2.0691 | 0.0385 | -0.0038 | 0.4474 | 151 | -0.0028 | 0.0028 | 0.3199 | -0.0036 | 0.4371 |
| A_all | A | product_later_verified | deep_synthesis | 8 | 1 | 1 | -0.0476 | 0.0164 | -2.8980 | 0.0038 | -0.0439 | 0.1250 | 1 | -0.0476 |  |  | -0.0476 | 0.0000 |
| A_all | A | product_later_verified | self_filing | 69 | 7 | 5 | -0.0116 | 0.0118 | -0.9840 | 0.3251 | -0.0054 | 0.3768 | 7 | -0.0115 | 0.0151 | 0.4475 | -0.0081 | 0.2857 |
| A_all | A | product_verified_at_event | self_filing | 20 | 2 | 2 | 0.0213 | 0.0116 | 1.8423 | 0.0654 | 0.0116 | 0.6500 | 2 | 0.0213 | 0.0226 | 0.3446 | 0.0213 | 0.5000 |
| A_first_firm | A | no_product_match_recent_censored | no_product_match | 115 | 13 | 13 | -0.0124 | 0.0038 | -3.2966 | 0.0010 | -0.0156 | 0.2957 | 12 | -0.0125 | 0.0071 | 0.0785 | -0.0162 | 0.1667 |
| A_first_firm | A | no_product_text_match | no_product_match | 1118 | 120 | 120 | -0.0024 | 0.0016 | -1.5380 | 0.1241 | -0.0029 | 0.4535 | 120 | -0.0025 | 0.0033 | 0.4510 | -0.0018 | 0.4500 |
| A_first_firm | A | product_later_verified | deep_synthesis | 8 | 1 | 1 | -0.0476 | 0.0164 | -2.8980 | 0.0038 | -0.0439 | 0.1250 | 1 | -0.0476 |  |  | -0.0476 | 0.0000 |
| A_first_firm | A | product_later_verified | self_filing | 50 | 5 | 5 | 0.0023 | 0.0069 | 0.3352 | 0.7375 | -0.0023 | 0.4200 | 5 | 0.0023 | 0.0111 | 0.8354 | -0.0081 | 0.4000 |
| A_first_firm | A | product_verified_at_event | self_filing | 10 | 1 | 1 | 0.0439 | 0.0208 | 2.1073 | 0.0351 | 0.0281 | 0.9000 | 1 | 0.0439 |  |  | 0.0439 | 1.0000 |

## Focal CAR Diagnostic

| sample_name | event_type | verification_timing | verification_type | nobs | events | focal_firms | mean | se | z | p | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A_all | A | no_product_match_recent_censored | no_product_match | 23 | 26 | 24 | -0.0085 | 0.0119 | -0.7108 | 0.4772 | -0.0071 | 0.3478 |
| A_all | A | no_product_text_match | no_product_match | 149 | 166 | 134 | -0.0004 | 0.0065 | -0.0653 | 0.9480 | -0.0113 | 0.3960 |
| A_all | A | product_later_verified | deep_synthesis | 1 | 1 | 1 | -0.0230 |  |  |  | -0.0230 | 0.0000 |
| A_all | A | product_later_verified | self_filing | 7 | 7 | 5 | 0.0879 | 0.0428 | 2.0523 | 0.0401 | 0.0929 | 0.7143 |
| A_all | A | product_verified_at_event | deep_synthesis | 1 | 1 | 1 | 0.0402 |  |  |  | 0.0402 | 1.0000 |
| A_all | A | product_verified_at_event | self_filing | 2 | 2 | 2 | -0.0003 | 0.0037 | -0.0913 | 0.9272 | -0.0003 | 0.5000 |
| A_first_firm | A | no_product_match_recent_censored | no_product_match | 17 | 19 | 19 | -0.0139 | 0.0156 | -0.8952 | 0.3707 | -0.0107 | 0.2941 |
| A_first_firm | A | no_product_text_match | no_product_match | 120 | 133 | 133 | -0.0028 | 0.0068 | -0.4105 | 0.6814 | -0.0101 | 0.4000 |
| A_first_firm | A | product_later_verified | deep_synthesis | 1 | 1 | 1 | -0.0230 |  |  |  | -0.0230 | 0.0000 |
| A_first_firm | A | product_later_verified | self_filing | 5 | 5 | 5 | 0.0996 | 0.0595 | 1.6733 | 0.0943 | 0.0929 | 0.6000 |
| A_first_firm | A | product_verified_at_event | deep_synthesis | 1 | 1 | 1 | 0.0402 |  |  |  | 0.0402 | 1.0000 |
| A_first_firm | A | product_verified_at_event | self_filing | 1 | 1 | 1 | -0.0041 |  |  |  | -0.0041 | 0.0000 |

## Interpretation

Product-level verification is much stricter than v68's firm-level administrative tag. The strict D1 dates are suitable as validation or supplementary event evidence, not as the main sample unless additional targeted CNINFO retrieval raises the cell size materially.
