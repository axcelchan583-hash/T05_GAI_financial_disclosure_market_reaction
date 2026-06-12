# v71 Targeted CNINFO Search Plan

## Purpose

- Creates a bounded targeted CNINFO search plan for all v67 registry firm-products.
- Prioritizes products without event-ready D1 from v69.
- Optional online pilot checks whether exact product queries produce same-firm formal announcements before downloading PDFs.

## Outputs

- `results/v71_targeted_cninfo_search_plan_20260612/targeted_cninfo_product_plan.csv`
- `results/v71_targeted_cninfo_search_plan_20260612/targeted_cninfo_search_terms.csv`
- `results/v71_targeted_cninfo_search_plan_20260612/targeted_cninfo_online_pilot_hits.csv`
- `results/v71_targeted_cninfo_search_plan_20260612/targeted_cninfo_online_pilot_same_firm_hits.csv`
- `results/v71_targeted_cninfo_search_plan_20260612/targeted_cninfo_online_pilot_query_counts.csv`
- `results/v71_targeted_cninfo_search_plan_20260612/v71_targeted_cninfo_search_plan_20260612.xlsx`

## Summary

| metric | value |
|---|---|
| registry_products | 457 |
| listed_firms | 210 |
| query_terms | 2890 |
| products_with_query_terms | 456 |
| pilot_raw_hits | 0 |
| pilot_same_firm_hits | 0 |
| pilot_same_firm_event_ready_title_hits | 0 |

## Product Plan By Status

| query_priority | local_traceback_status | verification_type | products | firms |
|---|---|---|---|---|
| P0_no_d1_self_or_registration | no_local_traceback | app_registration | 38 | 31 |
| P0_no_d1_self_or_registration | no_local_traceback | self_filing | 72 | 61 |
| P0_no_d1_self_or_registration | routine_formal_mention_only | app_registration | 2 | 2 |
| P0_no_d1_self_or_registration | routine_formal_mention_only | self_filing | 13 | 12 |
| P1_routine_only_needs_backfill | routine_formal_mention_only | deep_synthesis | 21 | 15 |
| P2_no_d1_deep_synthesis | no_local_traceback | deep_synthesis | 282 | 157 |
| P2_no_d1_other | no_local_traceback | ordinary_algorithm_genai_keyword | 6 | 5 |
| P3_already_event_ready_d1 | event_ready_formal_d1 | deep_synthesis | 12 | 6 |
| P3_already_event_ready_d1 | event_ready_formal_d1 | self_filing | 10 | 10 |

## Pilot Same-Firm Event-Ready Title Hits

_No rows._

## Pilot Same-Firm Hits

_No rows._

## Query-Term Sample

| registry_product_id | listed_code | listed_name | registry_item_name | registry_application_product | verification_type | query_priority | local_traceback_status | query_term | query_kind | query_priority_rank | query_norm | product_query_order |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fb70df3f10eda84c | 000063 | 中兴通讯 | 星云大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | Guangdong-NebulaLM-202406210001 | filing_no_exact | 1 | guangdong-nebulalm-202406210001 | 1 |
| fb70df3f10eda84c | 000063 | 中兴通讯 | 星云大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 星云大模型 | item_name_exact | 2 | 星云大模型 | 2 |
| fb70df3f10eda84c | 000063 | 中兴通讯 | 星云大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 星云大模型 备案 | item_name_exact_plus_filing | 12 | 星云大模型备案 | 3 |
| fb70df3f10eda84c | 000063 | 中兴通讯 | 星云大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 星云大模型 发布 | item_name_exact_plus_launch | 14 | 星云大模型发布 | 4 |
| 957b5f56a610fbff | 000156 | 华数传媒 | 华数诗画文旅大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | ZheJiang-HuaShuShiHuaWenLvDaMoXing-20250609000026 | filing_no_exact | 1 | zhejiang-huashushihuawenlvdamoxing-20250609000026 | 1 |
| 957b5f56a610fbff | 000156 | 华数传媒 | 华数诗画文旅大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 华数诗画文旅大模型 | item_name_exact | 2 | 华数诗画文旅大模型 | 2 |
| 957b5f56a610fbff | 000156 | 华数传媒 | 华数诗画文旅大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 华数诗画文旅 | product_core_exact | 4 | 华数诗画文旅 | 3 |
| 957b5f56a610fbff | 000156 | 华数传媒 | 华数诗画文旅大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 华数诗画文旅大 | product_core_exact | 4 | 华数诗画文旅大 | 4 |
| 957b5f56a610fbff | 000156 | 华数传媒 | 华数诗画文旅大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 华数诗画文旅大模型 备案 | item_name_exact_plus_filing | 12 | 华数诗画文旅大模型备案 | 5 |
| 957b5f56a610fbff | 000156 | 华数传媒 | 华数诗画文旅大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 华数诗画文旅大模型 发布 | item_name_exact_plus_launch | 14 | 华数诗画文旅大模型发布 | 6 |
| 20c9d5e358645717 | 000725 | 京东方A | 蓝鲸 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | Beijing-LanJing-202511150159 | filing_no_exact | 1 | beijing-lanjing-202511150159 | 1 |
| ad3593d55609207a | 000776 | 广发证券 | 广发易淘金大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | Guangdong-GuangFaYiTaoJin-20260420S0042 | filing_no_exact | 1 | guangdong-guangfayitaojin-20260420s0042 | 1 |
| ad3593d55609207a | 000776 | 广发证券 | 广发易淘金大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | 广发易淘金大模型 | item_name_exact | 2 | 广发易淘金大模型 | 2 |
| ad3593d55609207a | 000776 | 广发证券 | 广发易淘金大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | 广发易淘金 | product_core_exact | 4 | 广发易淘金 | 3 |
| ad3593d55609207a | 000776 | 广发证券 | 广发易淘金大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | 广发易淘金大 | product_core_exact | 4 | 广发易淘金大 | 4 |
| ad3593d55609207a | 000776 | 广发证券 | 广发易淘金大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | 广发易淘金大模型 备案 | item_name_exact_plus_filing | 12 | 广发易淘金大模型备案 | 5 |
| ad3593d55609207a | 000776 | 广发证券 | 广发易淘金大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | 广发易淘金大模型 发布 | item_name_exact_plus_launch | 14 | 广发易淘金大模型发布 | 6 |
| f2739623aa7326f3 | 000776 | 广发证券 | 广发GPT大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | Guangdong-GuangFaGPT-20250710S0018 | filing_no_exact | 1 | guangdong-guangfagpt-20250710s0018 | 1 |
| f2739623aa7326f3 | 000776 | 广发证券 | 广发GPT大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | 广发GPT大模型 | item_name_exact | 2 | 广发gpt大模型 | 2 |
| f2739623aa7326f3 | 000776 | 广发证券 | 广发GPT大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | 广发GPT | product_core_exact | 4 | 广发gpt | 3 |
| f2739623aa7326f3 | 000776 | 广发证券 | 广发GPT大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | 广发GPT大 | product_core_exact | 4 | 广发gpt大 | 4 |
| f2739623aa7326f3 | 000776 | 广发证券 | 广发GPT大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | 广发GPT大模型 备案 | item_name_exact_plus_filing | 12 | 广发gpt大模型备案 | 5 |
| f2739623aa7326f3 | 000776 | 广发证券 | 广发GPT大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | 广发GPT大模型 发布 | item_name_exact_plus_launch | 14 | 广发gpt大模型发布 | 6 |
| f456d12833a6ac86 | 000783 | 长江证券 | 长江灵曦大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | Hubei-ChangJiangLingXi-20250417S0001 | filing_no_exact | 1 | hubei-changjianglingxi-20250417s0001 | 1 |
| f456d12833a6ac86 | 000783 | 长江证券 | 长江灵曦大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | 长江灵曦大模型 | item_name_exact | 2 | 长江灵曦大模型 | 2 |
| f456d12833a6ac86 | 000783 | 长江证券 | 长江灵曦大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | 长江灵曦 | product_core_exact | 4 | 长江灵曦 | 3 |
| f456d12833a6ac86 | 000783 | 长江证券 | 长江灵曦大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | 长江灵曦大 | product_core_exact | 4 | 长江灵曦大 | 4 |
| f456d12833a6ac86 | 000783 | 长江证券 | 长江灵曦大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | 长江灵曦大模型 备案 | item_name_exact_plus_filing | 12 | 长江灵曦大模型备案 | 5 |
| f456d12833a6ac86 | 000783 | 长江证券 | 长江灵曦大模型 |  | app_registration | P0_no_d1_self_or_registration | no_local_traceback | 长江灵曦大模型 发布 | item_name_exact_plus_launch | 14 | 长江灵曦大模型发布 | 6 |
| 0a4834a2b110dc69 | 000901 | 航天科技 | 天玄·成务 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | Beijing-TianXuanChengWu-202511150154 | filing_no_exact | 1 | beijing-tianxuanchengwu-202511150154 | 1 |
| 0a4834a2b110dc69 | 000901 | 航天科技 | 天玄·成务 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 天玄·成务 | item_name_exact | 2 | 天玄·成务 | 2 |
| 0a4834a2b110dc69 | 000901 | 航天科技 | 天玄·成务 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 天玄·成务 备案 | item_name_exact_plus_filing | 12 | 天玄·成务备案 | 3 |
| 0a4834a2b110dc69 | 000901 | 航天科技 | 天玄·成务 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 天玄·成务 发布 | item_name_exact_plus_launch | 14 | 天玄·成务发布 | 4 |
| b700cea65cafb20e | 000901 | 航天科技 | 天玄·开物 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | Beijing-TianXuanKaiWu-202511150153 | filing_no_exact | 1 | beijing-tianxuankaiwu-202511150153 | 1 |
| b700cea65cafb20e | 000901 | 航天科技 | 天玄·开物 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 天玄·开物 | item_name_exact | 2 | 天玄·开物 | 2 |
| b700cea65cafb20e | 000901 | 航天科技 | 天玄·开物 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 天玄·开物 备案 | item_name_exact_plus_filing | 12 | 天玄·开物备案 | 3 |
| b700cea65cafb20e | 000901 | 航天科技 | 天玄·开物 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 天玄·开物 发布 | item_name_exact_plus_launch | 14 | 天玄·开物发布 | 4 |
| fa0050989f6fe069 | 000901 | 航天科技 | 天玄·千河 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | Beijing-TianXuanQianHe-202511150155 | filing_no_exact | 1 | beijing-tianxuanqianhe-202511150155 | 1 |
| fa0050989f6fe069 | 000901 | 航天科技 | 天玄·千河 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 天玄·千河 | item_name_exact | 2 | 天玄·千河 | 2 |
| fa0050989f6fe069 | 000901 | 航天科技 | 天玄·千河 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 天玄·千河 备案 | item_name_exact_plus_filing | 12 | 天玄·千河备案 | 3 |
| fa0050989f6fe069 | 000901 | 航天科技 | 天玄·千河 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 天玄·千河 发布 | item_name_exact_plus_launch | 14 | 天玄·千河发布 | 4 |
| 987f0545e5229a6b | 000931 | 中关村 | 如如大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | Beijing-RuRu-202404280012 | filing_no_exact | 1 | beijing-ruru-202404280012 | 1 |
| 987f0545e5229a6b | 000931 | 中关村 | 如如大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 如如大模型 | item_name_exact | 2 | 如如大模型 | 2 |
| 987f0545e5229a6b | 000931 | 中关村 | 如如大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 如如大模型 备案 | item_name_exact_plus_filing | 12 | 如如大模型备案 | 3 |
| 987f0545e5229a6b | 000931 | 中关村 | 如如大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 如如大模型 发布 | item_name_exact_plus_launch | 14 | 如如大模型发布 | 4 |
| 977c91977e0d64b7 | 002212 | 天融信 | 天问 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | Beijing-TianWen-202409250036 | filing_no_exact | 1 | beijing-tianwen-202409250036 | 1 |
| 8f49fb549475e1f3 | 002230 | 科大讯飞 | 讯飞星火教育大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | Anhui-XunFeiXingHuoJiaoYuDaMoXing-202409190001 | filing_no_exact | 1 | anhui-xunfeixinghuojiaoyudamoxing-202409190001 | 1 |
| 8f49fb549475e1f3 | 002230 | 科大讯飞 | 讯飞星火教育大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 讯飞星火教育大模型 | item_name_exact | 2 | 讯飞星火教育大模型 | 2 |
| 8f49fb549475e1f3 | 002230 | 科大讯飞 | 讯飞星火教育大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 讯飞星火教育 | product_core_exact | 4 | 讯飞星火教育 | 3 |
| 8f49fb549475e1f3 | 002230 | 科大讯飞 | 讯飞星火教育大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 讯飞星火教育大 | product_core_exact | 4 | 讯飞星火教育大 | 4 |
| 8f49fb549475e1f3 | 002230 | 科大讯飞 | 讯飞星火教育大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 讯飞星火教育大模型 备案 | item_name_exact_plus_filing | 12 | 讯飞星火教育大模型备案 | 5 |
| 8f49fb549475e1f3 | 002230 | 科大讯飞 | 讯飞星火教育大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 讯飞星火教育大模型 发布 | item_name_exact_plus_launch | 14 | 讯飞星火教育大模型发布 | 6 |
| c5f711ec686f1b96 | 002230 | 科大讯飞 | 星火课堂分析大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | Guangdong-XingHuoKeTangFenXi-202505090039 | filing_no_exact | 1 | guangdong-xinghuoketangfenxi-202505090039 | 1 |
| c5f711ec686f1b96 | 002230 | 科大讯飞 | 星火课堂分析大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 星火课堂分析大模型 | item_name_exact | 2 | 星火课堂分析大模型 | 2 |
| c5f711ec686f1b96 | 002230 | 科大讯飞 | 星火课堂分析大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 星火课堂分析 | product_core_exact | 4 | 星火课堂分析 | 3 |
| c5f711ec686f1b96 | 002230 | 科大讯飞 | 星火课堂分析大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 星火课堂分析大 | product_core_exact | 4 | 星火课堂分析大 | 4 |
| c5f711ec686f1b96 | 002230 | 科大讯飞 | 星火课堂分析大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 星火课堂分析大模型 备案 | item_name_exact_plus_filing | 12 | 星火课堂分析大模型备案 | 5 |
| c5f711ec686f1b96 | 002230 | 科大讯飞 | 星火课堂分析大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 星火课堂分析大模型 发布 | item_name_exact_plus_launch | 14 | 星火课堂分析大模型发布 | 6 |
| 359b6308338ad435 | 002354 | 天娱数科 | Behavision |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | ZheJiang-Behavision-202511130050 | filing_no_exact | 1 | zhejiang-behavision-202511130050 | 1 |
| 359b6308338ad435 | 002354 | 天娱数科 | Behavision |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | Behavision | item_name_exact | 2 | behavision | 2 |
| 359b6308338ad435 | 002354 | 天娱数科 | Behavision |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | Behavision 备案 | item_name_exact_plus_filing | 12 | behavision备案 | 3 |
| 359b6308338ad435 | 002354 | 天娱数科 | Behavision |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | Behavision 发布 | item_name_exact_plus_launch | 14 | behavision发布 | 4 |
| c5ea2cd2a73868d9 | 002401 | 中远海科 | HiDolphin |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | Shanghai-HiDolphin-202510170082 | filing_no_exact | 1 | shanghai-hidolphin-202510170082 | 1 |
| c5ea2cd2a73868d9 | 002401 | 中远海科 | HiDolphin |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | HiDolphin | item_name_exact | 2 | hidolphin | 2 |
| c5ea2cd2a73868d9 | 002401 | 中远海科 | HiDolphin |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | HiDolphin 备案 | item_name_exact_plus_filing | 12 | hidolphin备案 | 3 |
| c5ea2cd2a73868d9 | 002401 | 中远海科 | HiDolphin |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | HiDolphin 发布 | item_name_exact_plus_launch | 14 | hidolphin发布 | 4 |
| 8cdbeb13cf7dedd7 | 002410 | 广联达 | GlodonGPT |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | Beijing-GlodonGPT-202603050193 | filing_no_exact | 1 | beijing-glodongpt-202603050193 | 1 |
| 8cdbeb13cf7dedd7 | 002410 | 广联达 | GlodonGPT |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | GlodonGPT | item_name_exact | 2 | glodongpt | 2 |
| 8cdbeb13cf7dedd7 | 002410 | 广联达 | GlodonGPT |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | GlodonGPT 备案 | item_name_exact_plus_filing | 12 | glodongpt备案 | 3 |
| 8cdbeb13cf7dedd7 | 002410 | 广联达 | GlodonGPT |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | GlodonGPT 大模型 | item_name_exact_plus_model | 13 | glodongpt大模型 | 4 |
| 8cdbeb13cf7dedd7 | 002410 | 广联达 | GlodonGPT |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | GlodonGPT 发布 | item_name_exact_plus_launch | 14 | glodongpt发布 | 5 |
| 81f156514b280919 | 002415 | 海康威视 | 海康威视观澜大模型 |  | self_filing | P0_no_d1_self_or_registration | routine_formal_mention_only | ZheJiang-HaiKangWeiShiGuanLanDaMoXing-202508220037 | filing_no_exact | 1 | zhejiang-haikangweishiguanlandamoxing-202508220037 | 1 |
| 81f156514b280919 | 002415 | 海康威视 | 海康威视观澜大模型 |  | self_filing | P0_no_d1_self_or_registration | routine_formal_mention_only | 海康威视观澜大模型 | item_name_exact | 2 | 海康威视观澜大模型 | 2 |
| 81f156514b280919 | 002415 | 海康威视 | 海康威视观澜大模型 |  | self_filing | P0_no_d1_self_or_registration | routine_formal_mention_only | 海康威视观澜大模型 备案 | item_name_exact_plus_filing | 12 | 海康威视观澜大模型备案 | 3 |
| 81f156514b280919 | 002415 | 海康威视 | 海康威视观澜大模型 |  | self_filing | P0_no_d1_self_or_registration | routine_formal_mention_only | 海康威视观澜大模型 发布 | item_name_exact_plus_launch | 14 | 海康威视观澜大模型发布 | 4 |
| 19983326f50a6270 | 002439 | 启明星辰 | 泰合安全 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | Beijing-TaiHeAnQuan-202601050183 | filing_no_exact | 1 | beijing-taiheanquan-202601050183 | 1 |
| 19983326f50a6270 | 002439 | 启明星辰 | 泰合安全 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 泰合安全 | item_name_exact | 2 | 泰合安全 | 2 |
| 19983326f50a6270 | 002439 | 启明星辰 | 泰合安全 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 泰合安全 备案 | item_name_exact_plus_filing | 12 | 泰合安全备案 | 3 |
| 19983326f50a6270 | 002439 | 启明星辰 | 泰合安全 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | 泰合安全 发布 | item_name_exact_plus_launch | 14 | 泰合安全发布 | 4 |
| 4aee671924155188 | 002508 | 老板电器 | 老板食神AI烹饪大模型 |  | self_filing | P0_no_d1_self_or_registration | no_local_traceback | ZheJiang-LaoBanShiShenAIPengRen-202510100046 | filing_no_exact | 1 | zhejiang-laobanshishenaipengren-202510100046 | 1 |

## Interpretation

The pilot is a discovery gate. Same-firm event-ready title hits should be downloaded and passed through the v69 traceback classifier; routine-title hits are useful only as backfill evidence, not event-study dates.
