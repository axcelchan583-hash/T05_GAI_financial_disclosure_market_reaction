# v69 Registry Product Traceback

## Purpose

- Implements the missing reverse-location step after v67/v68.
- Searches each listed firm-product from the CAC registry master against local CNINFO formal announcements, CNINFO investor-relation activity records, and CSMAR IIP/IRQA GenAI answer-level corpora.
- Uses same-firm product-level terms only: filing number, registry item name, application/product name, and conservative core-name variants.
- Firm name alone is never sufficient for a traceback hit.

## Outputs

- `results/v69_registry_product_traceback_20260612/registry_product_traceback_hits.csv`
- `results/v69_registry_product_traceback_20260612/registry_product_traceback_best.csv`
- `results/v69_registry_product_traceback_20260612/registry_product_traceback_summary.csv`
- `results/v69_registry_product_traceback_20260612/registry_product_traceback_by_type.csv`
- `results/v69_registry_product_traceback_20260612/registry_product_traceback_timing_counts.csv`
- `results/v69_registry_product_traceback_20260612/registry_product_search_terms.csv`
- `results/v69_registry_product_traceback_20260612/registry_product_traceback_review_queue.csv`
- `results/v69_registry_product_traceback_20260612/v69_registry_product_traceback_20260612.xlsx`

## Main Counts

| metric | value |
|---|---|
| registry_products_input | 457 |
| listed_firms_input | 210 |
| doc_index_rows | 46,392 |
| doc_index_firms | 3,774 |
| raw_hit_rows | 589 |
| accepted_hit_rows | 554 |
| accepted_event_ready_or_interactive_hit_rows | 506 |
| products_any_traceback | 22 |
| products_formal_d1 | 22 |
| products_formal_any_mention | 58 |
| products_interactive_d1_prime | 1 |
| firms_any_traceback | 10 |
| firms_formal_d1 | 10 |
| firms_formal_any_mention | 34 |
| firms_interactive_d1_prime | 1 |

## Counts By Registry Type

| verification_type | products | firms | any_traceback | formal_d1 | formal_any_mention | interactive_d1_prime |
|---|---|---|---|---|---|---|
| deep_synthesis | 315 | 170 | 12 | 12 | 33 | 1 |
| self_filing | 95 | 80 | 10 | 10 | 23 | 0 |
| app_registration | 40 | 33 | 0 | 0 | 2 | 0 |
| ordinary_algorithm_genai_keyword | 6 | 5 | 0 | 0 | 0 | 0 |

## Timing Relative To Registry Publication

| verification_type | any_first_timing_vs_registry | products | firms |
|---|---|---|---|
| app_registration |  | 40 | 33 |
| deep_synthesis |  | 303 | 167 |
| deep_synthesis | disclosure_after_registry_publication | 2 | 1 |
| deep_synthesis | disclosure_before_registry_publication | 10 | 5 |
| ordinary_algorithm_genai_keyword |  | 6 | 5 |
| self_filing |  | 85 | 72 |
| self_filing | disclosure_after_registry_publication | 3 | 3 |
| self_filing | disclosure_before_registry_publication | 7 | 7 |

## Example Product-Level Tracebacks

| listed_code | listed_name | verification_type | item_name | application_product | batch_public_date | any_first_date | any_first_timing_vs_registry | any_first_source_type | any_first_match_basis | any_first_matched_term | any_first_title |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 300418 | 昆仑万维 | deep_synthesis | 天工图生文算法-1 | -- | 2024-06-12 | 2023-04-10 | disclosure_before_registry_publication | cninfo_formal_pom_like | product_core_exact | 天工 | 昆仑万维：关于发布大语言模型“天工”3.5的公告 |
| 002929 | 润建股份 | self_filing | 曲尺通信运维大模型 |  | 2025-07-11 | 2025-09-17 | disclosure_after_registry_publication | cninfo_formal_pom_like | item_name_exact | 曲尺通信运维大模型 | 润建股份：关于中标候选人公示的提示性公告 |
| 300133 | 华策影视 | self_filing | “有风”大模型 |  | 2024-08-08 | 2024-07-24 | disclosure_before_registry_publication | cninfo_formal_pom_like | product_core_exact | “有风” | 华策影视：关于全资子公司与专业投资机构共同投资的公告 |
| 300288 | 朗玛信息 | deep_synthesis | 39健康医疗内容生成算法 | 39AI全科医生(小程序)、39AI全科医生(APP)、39AI全科医生(网站) | 2024-02-18 | 2023-05-12 | disclosure_before_registry_publication | cninfo_formal_raw_genai | application_product_exact | 39AI全科医生 | 关于召开国家健康医疗大数据西部中心人工智能建设成果——“朗玛·39AI全科医生”发布会的提示性公告 |
| 002152 | 广电运通 | self_filing | 望道 |  | 2025-07-11 | 2025-11-20 | disclosure_after_registry_publication | cninfo_formal_pom_like | item_name_exact | 望道 | 广电运通：关于收到中标通知书的公告 |
| 688343 | 云天励飞 | self_filing | 云天天书大模型 |  | 2024-04-02 | 2024-03-23 | disclosure_before_registry_publication | cninfo_formal_pom_like | product_core_exact | 云天天书 | 云天励飞：关于收购深圳市岍丞技术有限公司股权暨开展新业务的公告 |
| 300418 | 昆仑万维 | deep_synthesis | 天工图生文算法 | 天工AI助手(APP)、天工AI搜索(小程序)、天工AI助手(网站) | 2024-06-12 | 2023-04-10 | disclosure_before_registry_publication | cninfo_formal_pom_like | product_core_exact | 天工 | 昆仑万维：关于发布大语言模型“天工”3.5的公告 |
| 300418 | 昆仑万维 | self_filing | “天工”大模型 |  | 2024-04-02 | 2023-04-10 | disclosure_before_registry_publication | cninfo_formal_pom_like | product_core_exact | “天工” | 昆仑万维：关于发布大语言模型“天工”3.5的公告 |
| 688088 | 虹软科技 | deep_synthesis | PSAI内容深度合成类算法 | PhotoStudio® AI(网站) | 2024-06-12 | 2025-04-15 | disclosure_after_registry_publication | cninfo_formal_pom_like | application_product_exact | PhotoStudio® AI | 虹软科技：关于使用剩余超募资金投资建设新项目的公告 |
| 002230 | 科大讯飞 | deep_synthesis | 讯飞星火认知大模型算法-SparkDesk | 讯飞星火（小程序）、讯飞星火认知大模型（网站）、讯飞星火（APP） | 2023-09-01 | 2023-04-20 | disclosure_before_registry_publication | csmar_irqa_answer | application_product_exact | 讯飞星火 | 002230 科大讯飞：2023年4月20日投资者关系活动（业绩说明会）记录表.pdf |
| 002362 | 汉王科技 | deep_synthesis | 天地大模型算法 | -- | 2024-06-12 | 2023-10-12 | disclosure_before_registry_publication | cninfo_formal_pom_like | product_core_exact | 天地大模型 | 汉王科技：关于召开汉王天地大模型阶段成果发布会的提示性公告 |
| 688088 | 虹软科技 | self_filing | ArcMuse计算技术引擎 |  | 2024-08-08 | 2025-04-15 | disclosure_after_registry_publication | cninfo_formal_pom_like | item_name_exact | ArcMuse计算技术引擎 | 虹软科技：关于使用剩余超募资金投资建设新项目的公告 |
| 002230 | 科大讯飞 | self_filing | 星火认知大模型 |  | 2024-04-02 | 2023-05-06 | disclosure_before_registry_publication | cninfo_formal_pom_like | item_name_exact | 星火认知大模型 | 科大讯飞：关于讯飞星火认知大模型成果发布会的提示性公告 |
| 002362 | 汉王科技 | deep_synthesis | 汉王天地大模型算法 | 汉王天地(APP)、AI口语陪练(APP)、AI绘画(APP)、汉王天地大模型(网站)、AI助手(APP)、作文批改(APP) | 2024-02-18 | 2023-10-12 | disclosure_before_registry_publication | cninfo_formal_pom_like | product_core_exact | 汉王天地大模型 | 汉王科技：关于召开汉王天地大模型阶段成果发布会的提示性公告 |
| 002230 | 科大讯飞 | deep_synthesis | 讯飞星火认知大模型算法 | -- | 2023-06-20 | 2023-05-06 | disclosure_before_registry_publication | cninfo_formal_pom_like | product_core_exact | 讯飞星火认知大模型 | 科大讯飞：关于讯飞星火认知大模型成果发布会的提示性公告 |
| 300288 | 朗玛信息 | self_filing | 39AI全科医生 |  | 2024-04-02 | 2023-05-12 | disclosure_before_registry_publication | cninfo_formal_raw_genai | item_name_exact | 39AI全科医生 | 关于召开国家健康医疗大数据西部中心人工智能建设成果——“朗玛·39AI全科医生”发布会的提示性公告 |
| 002980 | 华盛昌 | self_filing | DeepSense深度感测大模型 |  | 2025-09-10 | 2025-09-03 | disclosure_before_registry_publication | cninfo_formal_pom_like | item_name_exact | DeepSense深度感测大模型 | 华盛昌：关于“DeepSense深度感测大模型”备案通过的自愿性信息披露公告 |
| 002362 | 汉王科技 | self_filing | 天地大模型 |  | 2024-04-02 | 2023-10-12 | disclosure_before_registry_publication | cninfo_formal_pom_like | item_name_exact | 天地大模型 | 汉王科技：关于召开汉王天地大模型阶段成果发布会的提示性公告 |
| 300418 | 昆仑万维 | deep_synthesis | 天工文生图算法 | 天工AI助手(APP)、天工AI搜索(小程序)、天工AI助手(网站) | 2024-04-11 | 2023-04-10 | disclosure_before_registry_publication | cninfo_formal_pom_like | product_core_exact | 天工 | 昆仑万维：关于发布大语言模型“天工”3.5的公告 |
| 688088 | 虹软科技 | deep_synthesis | PSAI试衣视频生成算法 | PhotoStudio® AI(网站) | 2024-06-12 | 2025-04-15 | disclosure_after_registry_publication | cninfo_formal_pom_like | application_product_exact | PhotoStudio® AI | 虹软科技：关于使用剩余超募资金投资建设新项目的公告 |
| 002980 | 华盛昌 | deep_synthesis | DeepSense深度感测大模型算法 | DeepSense深度感测大模型(网站) | 2026-01-07 | 2025-09-03 | disclosure_before_registry_publication | cninfo_formal_pom_like | product_core_exact | DeepSense深度感测大模型 | 华盛昌：关于“DeepSense深度感测大模型”备案通过的自愿性信息披露公告 |
| 300418 | 昆仑万维 | deep_synthesis | 天工文生图算法-1 | -- | 2024-04-11 | 2023-04-10 | disclosure_before_registry_publication | cninfo_formal_pom_like | product_core_exact | 天工 | 昆仑万维：关于发布大语言模型“天工”3.5的公告 |

## Highest-Score Hits

| listed_code | listed_name | verification_type | item_name | doc_date | source_type | match_score | match_basis | matched_term | title |
|---|---|---|---|---|---|---|---|---|---|
| 002230 | 科大讯飞 | self_filing | 星火认知大模型 | 2023-05-06 | cninfo_formal_pom_like | 109 | item_name_exact | 星火认知大模型 | 科大讯飞：关于讯飞星火认知大模型成果发布会的提示性公告 |
| 002230 | 科大讯飞 | self_filing | 星火认知大模型 | 2023-05-06 | cninfo_formal_raw_genai | 109 | item_name_exact | 星火认知大模型 | 关于讯飞星火认知大模型成果发布会的提示性公告 |
| 300288 | 朗玛信息 | self_filing | 39AI全科医生 | 2023-05-12 | cninfo_formal_raw_genai | 109 | item_name_exact | 39AI全科医生 | 关于召开国家健康医疗大数据西部中心人工智能建设成果——“朗玛·39AI全科医生”发布会的提示性公告 |
| 300288 | 朗玛信息 | self_filing | 39AI全科医生 | 2023-05-29 | cninfo_formal_pom_like | 109 | item_name_exact | 39AI全科医生 | 朗玛信息：关于召开国家健康医疗大数据西部中心人工智能建设成果——“朗玛·39AI全科医生”发布会的公告 |
| 300288 | 朗玛信息 | self_filing | 39AI全科医生 | 2023-05-29 | cninfo_formal_raw_genai | 109 | item_name_exact | 39AI全科医生 | 关于召开国家健康医疗大数据西部中心人工智能建设成果——“朗玛·39AI全科医生”发布会的公告 |
| 002230 | 科大讯飞 | self_filing | 星火认知大模型 | 2023-06-07 | cninfo_formal_pom_like | 109 | item_name_exact | 星火认知大模型 | 科大讯飞：关于讯飞星火认知大模型升级发布会的提示性公告 |
| 002230 | 科大讯飞 | self_filing | 星火认知大模型 | 2023-06-07 | cninfo_formal_raw_genai | 109 | item_name_exact | 星火认知大模型 | 关于讯飞星火认知大模型升级发布会的提示性公告 |
| 002230 | 科大讯飞 | self_filing | 星火认知大模型 | 2023-08-15 | cninfo_formal_pom_like | 109 | item_name_exact | 星火认知大模型 | 科大讯飞：关于讯飞星火认知大模型升级发布会的提示性公告 |
| 002230 | 科大讯飞 | self_filing | 星火认知大模型 | 2023-08-15 | cninfo_formal_raw_genai | 109 | item_name_exact | 星火认知大模型 | 关于讯飞星火认知大模型升级发布会的提示性公告 |
| 002362 | 汉王科技 | self_filing | 天地大模型 | 2023-10-12 | cninfo_formal_pom_like | 109 | item_name_exact | 天地大模型 | 汉王科技：关于召开汉王天地大模型阶段成果发布会的提示性公告 |
| 002362 | 汉王科技 | self_filing | 天地大模型 | 2023-10-12 | cninfo_formal_raw_genai | 109 | item_name_exact | 天地大模型 | 关于召开汉王天地大模型阶段成果发布会的提示性公告 |
| 300288 | 朗玛信息 | self_filing | 39AI全科医生 | 2023-11-20 | cninfo_formal_pom_like | 109 | item_name_exact | 39AI全科医生 | 朗玛信息：关于“39AI全科医生”大模型备案通过的公告 |
| 300288 | 朗玛信息 | self_filing | 39AI全科医生 | 2023-11-20 | cninfo_formal_raw_genai | 109 | item_name_exact | 39AI全科医生 | 关于“39AI全科医生”大模型备案通过的公告 |
| 300288 | 朗玛信息 | self_filing | 39AI全科医生 | 2024-02-19 | cninfo_formal_pom_like | 109 | item_name_exact | 39AI全科医生 | 朗玛信息：关于“39AI全科医生”内容生成算法备案通过的公告 |
| 002980 | 华盛昌 | self_filing | DeepSense深度感测大模型 | 2025-09-03 | cninfo_formal_pom_like | 109 | item_name_exact | DeepSense深度感测大模型 | 华盛昌：关于“DeepSense深度感测大模型”备案通过的自愿性信息披露公告 |
| 002980 | 华盛昌 | self_filing | DeepSense深度感测大模型 | 2025-09-03 | cninfo_formal_raw_genai | 109 | item_name_exact | DeepSense深度感测大模型 | 关于“DeepSense深度感测大模型”备案通过的自愿性信息披露公告 |
| 300418 | 昆仑万维 | self_filing | “天工”大模型 | 2023-07-14 | cninfo_formal_pom_like | 101 | item_name_exact | “天工”大模型 | 昆仑万维：关于公司与B端客户签订AI技术服务协议的公告 |
| 688590 | 新致软件 | self_filing | 新致新知 | 2024-01-30 | cninfo_formal_qian_priority_2023_2026 | 101 | item_name_exact | 新致新知 | 新致软件：2023年年度业绩预盈公告 |
| 300288 | 朗玛信息 | deep_synthesis | 39健康医疗内容生成算法 | 2024-02-19 | cninfo_formal_pom_like | 101 | item_name_exact | 39健康医疗内容生成算法 | 朗玛信息：关于“39AI全科医生”内容生成算法备案通过的公告 |
| 688590 | 新致软件 | self_filing | 新致新知 | 2024-02-25 | cninfo_formal_qian_priority_2023_2026 | 101 | item_name_exact | 新致新知 | 新致软件：2023年度业绩快报公告 |
| 688111 | 金山办公 | self_filing | WPSAI | 2024-03-20 | cninfo_formal_qian_priority_2023_2026 | 101 | item_name_exact | WPSAI | 金山办公：2024年金山办公“提质增效重回报”行动方案 |
| 300364 | 中文在线 | self_filing | 中文逍遥 | 2024-04-21 | cninfo_formal_qian_priority_2023_2026 | 101 | item_name_exact | 中文逍遥 | 中文在线：2023年度财务决算报告 |
| 601360 | 三六零 | self_filing | 360安全 | 2024-06-03 | cninfo_formal_qian_priority_2023_2026 | 101 | item_name_exact | 360安全 | 三六零：三六零安全科技股份有限公司2024年度“提质增效重回报”行动方案 |
| 600839 | 四川长虹 | self_filing | 长虹云帆 | 2024-06-14 | cninfo_formal_qian_priority_2023_2026 | 101 | item_name_exact | 长虹云帆 | 四川长虹：四川长虹2023年年度股东大会会议资料 |
| 002362 | 汉王科技 | self_filing | 天地大模型 | 2024-08-28 | cninfo_formal_pom_like | 101 | item_name_exact | 天地大模型 | 汉王科技：关于向控股孙公司增资暨关联交易的公告 |

## Review Queue

- Rows needing manual/LLM confirmation or no-hit diagnosis: 938

## Interpretation Caveat

This run is an executable traceback index, not a final causal sample. Low-score core-name hits and no-hit products are intentionally separated into the review queue before v70 product-level relabeling.
