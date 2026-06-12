# v65 Registry-Based Official CAC Event Study

## Scope

- Input: v64 official CAC GenAI-relevant registry master.
- Matching: high-confidence A-share match from CSMAR listed-company full names and short names. Full legal-name exact matches dominate; short-name matches require prefix or length>=4 containment.
- Event clocks: GenAI service uses record-level filing date; deep-synthesis uses CAC notice publication day; ordinary algorithm uses source-batch month-start proxy. The GenAI service filing-date clock is not necessarily the public disclosure date.
- Returns: same market-model abnormal returns cache as v23/v60/v61.
- Peer network: v22 Liu-style product-text TF-IDF same-industry-d Top10, using prior-year annual-report snapshots capped at 2025.

## Registry Matching Coverage

| registry_source | registry_rows | registry_entities | matched_rows | matched_firms |
|---|---|---|---|---|
| cac_algorithm_filing | 87.0 | 82.0 | 6.0 | 5.0 |
| cac_deep_synthesis_filing | 7059.0 | 4947.0 | 315.0 | 169.0 |
| cac_genai_service | 1358.0 | 1183.0 | 135.0 | 104.0 |

## Matching Methods

| registry_source | match_method | rows | firms |
|---|---|---|---|
| cac_algorithm_filing | full_name_exact | 5.0 | 4.0 |
| cac_algorithm_filing | short_name_prefix | 1.0 | 1.0 |
| cac_deep_synthesis_filing | full_name_exact | 214.0 | 125.0 |
| cac_deep_synthesis_filing | short_name_prefix | 61.0 | 26.0 |
| cac_deep_synthesis_filing | short_name_contained_len4 | 36.0 | 25.0 |
| cac_deep_synthesis_filing | full_name_contained | 4.0 | 3.0 |
| cac_genai_service | full_name_exact | 89.0 | 75.0 |
| cac_genai_service | short_name_prefix | 26.0 | 21.0 |
| cac_genai_service | short_name_contained_len4 | 16.0 | 10.0 |
| cac_genai_service | full_name_contained | 4.0 | 3.0 |

## Sample Counts

| sample_name | events | focal_firms | first_date | last_date | filing_rows | model_keyword_events |
|---|---|---|---|---|---|---|
| S0_exact_model_keyword_all | 199.0 | 121.0 | 2023-06-20 00:00:00 | 2026-05-06 00:00:00 | 214.0 | 153.0 |
| S0_exact_model_keyword_first_firm | 121.0 | 121.0 | 2023-06-20 00:00:00 | 2026-05-06 00:00:00 | 125.0 | 89.0 |
| S0_exact_official_all | 265.0 | 153.0 | 2023-06-20 00:00:00 | 2026-05-06 00:00:00 | 308.0 | 153.0 |
| S0_exact_official_first_firm | 153.0 | 153.0 | 2023-06-20 00:00:00 | 2026-05-06 00:00:00 | 171.0 | 84.0 |
| S1_genai_service_filing_day_all | 93.0 | 80.0 | 2023-09-04 00:00:00 | 2026-04-30 00:00:00 | 95.0 | 56.0 |
| S1_genai_service_filing_day_first_firm | 80.0 | 80.0 | 2023-09-04 00:00:00 | 2026-04-30 00:00:00 | 82.0 | 45.0 |
| S2_deep_synthesis_notice_all | 252.0 | 169.0 | 2023-06-20 00:00:00 | 2026-05-06 00:00:00 | 315.0 | 140.0 |
| S2_deep_synthesis_notice_first_firm | 169.0 | 169.0 | 2023-06-20 00:00:00 | 2026-05-06 00:00:00 | 200.0 | 90.0 |
| S3_official_genai_relevant_all | 388.0 | 209.0 | 2023-06-20 00:00:00 | 2026-05-06 00:00:00 | 456.0 | 211.0 |
| S3_official_genai_relevant_first_firm | 209.0 | 209.0 | 2023-06-20 00:00:00 | 2026-05-06 00:00:00 | 237.0 | 109.0 |
| S4_model_keyword_registry_all | 275.0 | 160.0 | 2023-06-20 00:00:00 | 2026-05-06 00:00:00 | 298.0 | 211.0 |
| S4_model_keyword_registry_first_firm | 160.0 | 160.0 | 2023-06-20 00:00:00 | 2026-05-06 00:00:00 | 169.0 | 119.0 |

## Example Events

| sample_name | event_date | focal_code | sec_name | registry_sources | event_clocks | filing_rows | item_names | entity_names | match_methods |
|---|---|---|---|---|---|---|---|---|---|
| S0_exact_model_keyword_all | 2023-06-20 00:00:00 | 002230 | 科大讯飞 | cac_deep_synthesis_filing | notice_public_day | 2.0 | 讯飞语音识别算法；讯飞星火认知大模型算法 | 科大讯飞股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2023-09-01 00:00:00 | 002230 | 科大讯飞 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 讯飞星火认知大模型算法-SparkDesk | 科大讯飞股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2023-09-01 00:00:00 | 300418 | 昆仑万维 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 天工大语言模型算法 | 昆仑万维科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2023-09-01 00:00:00 | 300454 | 深信服 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 深信服安全文本生成算法 | 深信服科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2023-09-01 00:00:00 | 688327 | 云从科技 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 云从从容大模型算法 | 云从科技集团股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2023-09-04 00:00:00 | 002230 | 科大讯飞 | cac_genai_service | filing_date_day | 1.0 | 星火认知大模型 | 科大讯飞股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2023-11-03 00:00:00 | 300418 | 昆仑万维 | cac_genai_service | filing_date_day | 1.0 | “天工”大模型 | 昆仑万维科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2023-11-03 00:00:00 | 688111 | 金山办公 | cac_genai_service | filing_date_day | 1.0 | WPSAI | 北京金山办公软件股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2023-11-16 00:00:00 | 300288 | 朗玛信息 | cac_genai_service | filing_date_day | 1.0 | 39AI全科医生 | 贵阳朗玛信息技术股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2023-12-01 00:00:00 | 002841 | 视源股份 | cac_genai_service | filing_date_day | 1.0 | CVTE大模型 | 广州视源电子科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2023-12-01 00:00:00 | 688343 | 云天励飞 | cac_genai_service | filing_date_day | 1.0 | 云天天书大模型 | 深圳云天励飞技术股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2023-12-27 00:00:00 | 300059 | 东方财富 | cac_genai_service | filing_date_day | 1.0 | 妙想 | 东方财富信息股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-01-02 00:00:00 | 688327 | 云从科技 | cac_genai_service | filing_date_day | 1.0 | 云从从容大模型 | 云从科技集团股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-01-08 00:00:00 | 300059 | 东方财富 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 东方财富自然语言合成算法 | 东方财富信息股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-01-08 00:00:00 | 300418 | 昆仑万维 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 天工大语言模型算法-1 | 昆仑万维科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-01-17 00:00:00 | 300785 | 值得买 | cac_genai_service | filing_date_day | 1.0 | 什么值得买App“AI问答机器人”新功能 | 北京值得买科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-01-17 00:00:00 | 603533 | 掌阅科技 | cac_genai_service | filing_date_day | 1.0 | 阅爱聊小程序 | 掌阅科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-02-07 00:00:00 | 600728 | 佳都科技 | cac_genai_service | filing_date_day | 1.0 | 佳都知行大模型 | 佳都科技集团股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-02-18 00:00:00 | 000333 | 美的集团 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 美的美言大模型算法 | 美的集团股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-02-18 00:00:00 | 002362 | 汉王科技 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 汉王天地大模型算法 | 汉王科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-02-18 00:00:00 | 600588 | 用友网络 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 用友YonGPT生成算法 | 用友网络科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-02-18 00:00:00 | 688500 | 慧辰股份 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 慧辰大模型内容生成算法 | 北京慧辰资道资讯股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-03-11 00:00:00 | 002362 | 汉王科技 | cac_genai_service | filing_date_day | 1.0 | 天地大模型 | 汉王科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-03-27 00:00:00 | 600839 | 四川长虹 | cac_genai_service | filing_date_day | 1.0 | 长虹云帆 | 四川长虹电器股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-03-28 00:00:00 | 002841 | 视源股份 | cac_genai_service | filing_date_day | 1.0 | CVTE大模型（自研） | 广州视源电子科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-04-11 00:00:00 | 000977 | 浪潮信息 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 浪潮信息自然语言处理源大模型算法 | 浪潮电子信息产业股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-04-11 00:00:00 | 002416 | 爱施德 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 爱施德AI大模型算法 | 深圳市爱施德股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-04-11 00:00:00 | 300418 | 昆仑万维 | cac_deep_synthesis_filing | notice_public_day | 2.0 | 天工文生图算法-1；天工文生图算法 | 昆仑万维科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-04-11 00:00:00 | 600570 | 恒生电子 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 恒生LightGPT金融领域文本生成类算法 | 恒生电子股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-04-11 00:00:00 | 601555 | 东吴证券 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 东吴秀财大模型生成算法 | 东吴证券股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-04-11 00:00:00 | 688228 | 开普云 | cac_deep_synthesis_filing | notice_public_day | 2.0 | 开普云开悟图像生成算法-1；开普云开悟文本生成算法-1 | 开普云信息科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-04-11 00:00:00 | 688327 | 云从科技 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 云从从容大模型算法-2 | 云从科技集团股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-04-25 00:00:00 | 300454 | 深信服 | cac_genai_service | filing_date_day | 1.0 | 深信服安全大模型 | 深信服科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-04-27 00:00:00 | 688088 | 虹软科技 | cac_genai_service | filing_date_day | 1.0 | ArcMuse计算技术引擎 | 虹软科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-05-13 00:00:00 | 300364 | 中文在线 | cac_genai_service | filing_date_day | 1.0 | 中文逍遥 | 中文在线集团股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-05-21 00:00:00 | 601211 | 国泰君安 | cac_genai_service | filing_date_day | 1.0 | 君弘灵犀 | 国泰君安证券股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-06-01 00:00:00 | 688327 | 云从科技 | cac_algorithm_filing | batch_month_start_proxy | 1.0 | 云从内容安全风控算法 | 云从科技集团股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-06-12 00:00:00 | 002362 | 汉王科技 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 天地大模型算法 | 汉王科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-06-12 00:00:00 | 002657 | 中科金财 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 中科金财多场景多基座大模型算法 | 北京中科金财科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-06-12 00:00:00 | 300253 | 卫宁健康 | cac_deep_synthesis_filing | notice_public_day | 1.0 | WiNGPT卫宁健康科技集团股份有限公司文本合成算法-1 | 卫宁健康科技集团股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-06-12 00:00:00 | 300364 | 中文在线 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 中文逍遥大模型算法 | 中文在线集团股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-06-12 00:00:00 | 300418 | 昆仑万维 | cac_deep_synthesis_filing | notice_public_day | 2.0 | 天工图生文算法；天工图生文算法-1 | 昆仑万维科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-06-12 00:00:00 | 300451 | 创业慧康 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 慧能GPT智能导诊生成算法 | 创业慧康科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-06-12 00:00:00 | 300559 | 佳发教育 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 灵汩文本生成大模型算法 | 成都佳发安泰教育科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-06-12 00:00:00 | 300634 | 彩讯股份 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 彩讯睿驰大模型算法 | 彩讯科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-06-12 00:00:00 | 600060 | 海信视像 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 海信智能交互大模型算法 | 海信视像科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-06-12 00:00:00 | 600271 | 航天信息 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 爱信诺信诺GPT财税产业大语言模型算法-1 | 航天信息股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-06-12 00:00:00 | 601658 | 邮储银行 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 邮储银行智能AI定制卡文生图大模型算法 | 中国邮政储蓄银行股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-06-12 00:00:00 | 688318 | 财富趋势 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 通达信TendencyGPT大模型算法 | 深圳市财富趋势科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-06-12 00:00:00 | 688327 | 云从科技 | cac_deep_synthesis_filing | notice_public_day | 2.0 | 云从从容代码生成算法；云从智能文字识别算法 | 云从科技集团股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-06-12 00:00:00 | 688615 | 合合信息 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 合合信息天玑大模型算法 | 上海合合信息科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-07-16 00:00:00 | 000063 | 中兴通讯 | cac_genai_service | filing_date_day | 1.0 | 星云大模型 | 中兴通讯股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-07-18 00:00:00 | 300229 | 拓尔思 | cac_genai_service | filing_date_day | 1.0 | 拓天大模型 | 拓尔思信息技术股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-07-23 00:00:00 | 600718 | 东软集团 | cac_genai_service | filing_date_day | 1.0 | 领智 | 东软集团股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-08-05 00:00:00 | 002152 | 广电运通 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 广电运通望道大模型算法 | 广电运通集团股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-08-05 00:00:00 | 002987 | 京北方 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 京北方检索增强型文本生成大模型算法 | 京北方信息技术股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-08-05 00:00:00 | 603171 | 税友股份 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 犀友大模型算法 | 税友软件集团股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-08-05 00:00:00 | 688004 | 博汇科技 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 博汇学道音视频分析大模型算法 | 北京市博汇科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-08-05 00:00:00 | 688039 | 当虹科技 | cac_deep_synthesis_filing | notice_public_day | 1.0 | BlackEye多模态视听内容生成算法 | 杭州当虹科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-08-05 00:00:00 | 688095 | 福昕软件 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 福昕文档智能算法 | 福建福昕软件开发股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-08-05 00:00:00 | 688111 | 金山办公 | cac_deep_synthesis_filing | notice_public_day | 1.0 | WPSAI图像生成系列大模型算法 | 北京金山办公软件股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-08-08 00:00:00 | 002777 | 久远银海 | cac_genai_service | filing_date_day | 1.0 | 银海闻语大模型 | 四川久远银海软件股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-09-06 00:00:00 | 603039 | 泛微网络 | cac_genai_service | filing_date_day | 1.0 | 智能小e | 泛微网络科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-09-06 00:00:00 | 688615 | 合合信息 | cac_genai_service | filing_date_day | 1.0 | 天玑 | 上海合合信息科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-10-01 00:00:00 | 002657 | 中科金财 | cac_algorithm_filing | batch_month_start_proxy | 1.0 | 中科金财大模型多轮对话搜索算法 | 北京中科金财科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-10-15 00:00:00 | 300418 | 昆仑万维 | cac_genai_service | filing_date_day | 1.0 | 天工图像 | 昆仑万维科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-11-01 00:00:00 | 003005 | 竞业达 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 星空教育大模型文本生成算法 | 北京竞业达数码科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-11-01 00:00:00 | 300059 | 东方财富 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 妙想大模型算法 | 东方财富信息股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-11-01 00:00:00 | 300418 | 昆仑万维 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 天工大语言音乐生成模型算法 | 昆仑万维科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-11-01 00:00:00 | 688004 | 博汇科技 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 博汇慧视多模态内容分析大模型算法 | 北京市博汇科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-11-17 00:00:00 | 601633 | 长城汽车 | cac_genai_service | filing_date_day | 1.0 | CoffeeAgent | 长城汽车股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-11-18 00:00:00 | 688615 | 合合信息 | cac_genai_service | filing_date_day | 1.0 | 名片全能王AI | 上海合合信息科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-11-23 00:00:00 | 002230 | 科大讯飞 | cac_genai_service | filing_date_day | 1.0 | 讯飞星火教育大模型 | 科大讯飞股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-11-25 00:00:00 | 603533 | 掌阅科技 | cac_genai_service | filing_date_day | 1.0 | 掌阅AI辅助阅读 | 掌阅科技股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-12-20 00:00:00 | 000063 | 中兴通讯 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 中兴星云大模型文生图算法 | 中兴通讯股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-12-20 00:00:00 | 000776 | 广发证券 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 广发证券AI问答大模型算法 | 广发证券股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-12-20 00:00:00 | 000977 | 浪潮信息 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 浪潮信息元脑企智自然语言处理源大模型算法 | 浪潮电子信息产业股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-12-20 00:00:00 | 002508 | 老板电器 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 老板电器多模态生成算法 | 杭州老板电器股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-12-20 00:00:00 | 300047 | 天源迪科 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 课件帮多模态生成算法 | 深圳天源迪科信息技术股份有限公司 | full_name_exact |
| S0_exact_model_keyword_all | 2024-12-20 00:00:00 | 300226 | 上海钢联 | cac_deep_synthesis_filing | notice_public_day | 1.0 | 上海钢联宗师大宗商品行业垂直大模型算法 | 上海钢联电子商务股份有限公司 | full_name_exact |

## Focal Firm Returns, Strict Next Trading Day

| sample_name | outcome_label | estimate | se | p | nobs | events | focal_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|
| S0_exact_model_keyword_all | AR[0] | -0.002865 | 0.001525 | 0.060254 | 188.0 | 188.0 | 115.0 | -0.00159 | 0.473404 |
| S0_exact_model_keyword_all | AR[+1] | -0.00314 | 0.001664 | 0.059229 | 188.0 | 188.0 | 115.0 | -0.003284 | 0.393617 |
| S0_exact_model_keyword_all | CAR[0,+1] | -0.006005 | 0.002631 | 0.022444 | 188.0 | 188.0 | 115.0 | -0.003079 | 0.398936 |
| S0_exact_model_keyword_all | CAR[-1,+1] | -0.007008 | 0.003102 | 0.023894 | 188.0 | 188.0 | 115.0 | -0.008858 | 0.382979 |
| S0_exact_model_keyword_first_firm | AR[0] | -0.003339 | 0.002083 | 0.108887 | 114.0 | 114.0 | 114.0 | -0.000452 | 0.5 |
| S0_exact_model_keyword_first_firm | AR[+1] | -0.005676 | 0.001935 | 0.003355 | 114.0 | 114.0 | 114.0 | -0.003945 | 0.385965 |
| S0_exact_model_keyword_first_firm | CAR[0,+1] | -0.009015 | 0.00337 | 0.007469 | 114.0 | 114.0 | 114.0 | -0.003292 | 0.394737 |
| S0_exact_model_keyword_first_firm | CAR[-1,+1] | -0.010943 | 0.003327 | 0.001003 | 114.0 | 114.0 | 114.0 | -0.009663 | 0.350877 |
| S0_exact_official_all | AR[0] | -0.000534 | 0.00147 | 0.716557 | 249.0 | 249.0 | 146.0 | -0.001004 | 0.493976 |
| S0_exact_official_all | AR[+1] | -0.002296 | 0.001502 | 0.126243 | 249.0 | 249.0 | 146.0 | -0.003073 | 0.409639 |
| S0_exact_official_all | CAR[0,+1] | -0.00283 | 0.002336 | 0.225809 | 249.0 | 249.0 | 146.0 | -0.001682 | 0.445783 |
| S0_exact_official_all | CAR[-1,+1] | -0.004622 | 0.003021 | 0.12598 | 249.0 | 249.0 | 146.0 | -0.005435 | 0.409639 |
| S0_exact_official_first_firm | AR[0] | -0.001048 | 0.001939 | 0.588914 | 144.0 | 144.0 | 144.0 | 0.000797 | 0.520833 |
| S0_exact_official_first_firm | AR[+1] | -0.004573 | 0.001946 | 0.018761 | 144.0 | 144.0 | 144.0 | -0.003934 | 0.375 |
| S0_exact_official_first_firm | CAR[0,+1] | -0.00562 | 0.003322 | 0.090706 | 144.0 | 144.0 | 144.0 | -0.002084 | 0.4375 |
| S0_exact_official_first_firm | CAR[-1,+1] | -0.010562 | 0.0035 | 0.002544 | 144.0 | 144.0 | 144.0 | -0.008817 | 0.368056 |
| S1_genai_service_filing_day_all | AR[0] | 0.000799 | 0.002246 | 0.722131 | 86.0 | 86.0 | 74.0 | -0.00143 | 0.453488 |
| S1_genai_service_filing_day_all | AR[+1] | 0.004482 | 0.004001 | 0.262726 | 86.0 | 86.0 | 74.0 | -0.002167 | 0.465116 |
| S1_genai_service_filing_day_all | CAR[0,+1] | 0.00528 | 0.005341 | 0.322849 | 86.0 | 86.0 | 74.0 | -0.002516 | 0.476744 |
| S1_genai_service_filing_day_all | CAR[-1,+1] | 0.005063 | 0.005966 | 0.396115 | 86.0 | 86.0 | 74.0 | -0.004583 | 0.418605 |
| S1_genai_service_filing_day_first_firm | AR[0] | 0.001512 | 0.00255 | 0.55326 | 74.0 | 74.0 | 74.0 | -0.001241 | 0.472973 |
| S1_genai_service_filing_day_first_firm | AR[+1] | 0.003584 | 0.004074 | 0.378998 | 74.0 | 74.0 | 74.0 | -0.003444 | 0.459459 |
| S1_genai_service_filing_day_first_firm | CAR[0,+1] | 0.005096 | 0.005405 | 0.345785 | 74.0 | 74.0 | 74.0 | 0.000398 | 0.5 |
| S1_genai_service_filing_day_first_firm | CAR[-1,+1] | 0.004097 | 0.005802 | 0.480038 | 74.0 | 74.0 | 74.0 | -0.003717 | 0.432432 |
| S2_deep_synthesis_notice_all | AR[0] | -0.001175 | 0.001662 | 0.479394 | 225.0 | 225.0 | 154.0 | 2.4e-05 | 0.502222 |
| S2_deep_synthesis_notice_all | AR[+1] | -0.003364 | 0.001728 | 0.051591 | 225.0 | 225.0 | 154.0 | -0.003073 | 0.408889 |
| S2_deep_synthesis_notice_all | CAR[0,+1] | -0.004539 | 0.002688 | 0.091305 | 225.0 | 225.0 | 154.0 | -0.001682 | 0.444444 |
| S2_deep_synthesis_notice_all | CAR[-1,+1] | -0.0087 | 0.00319 | 0.006389 | 225.0 | 225.0 | 154.0 | -0.009714 | 0.391111 |
| S2_deep_synthesis_notice_first_firm | AR[0] | -0.00092 | 0.001992 | 0.644342 | 151.0 | 151.0 | 151.0 | 0.001374 | 0.529801 |
| S2_deep_synthesis_notice_first_firm | AR[+1] | -0.00351 | 0.002092 | 0.093422 | 151.0 | 151.0 | 151.0 | -0.002963 | 0.423841 |
| S2_deep_synthesis_notice_first_firm | CAR[0,+1] | -0.00443 | 0.003265 | 0.174906 | 151.0 | 151.0 | 151.0 | -0.001568 | 0.450331 |
| S2_deep_synthesis_notice_first_firm | CAR[-1,+1] | -0.009115 | 0.003883 | 0.018902 | 151.0 | 151.0 | 151.0 | -0.009922 | 0.370861 |
| S3_official_genai_relevant_all | AR[0] | -0.000995 | 0.001214 | 0.412068 | 349.0 | 349.0 | 193.0 | -0.001004 | 0.489971 |
| S3_official_genai_relevant_all | AR[+1] | -0.000931 | 0.001414 | 0.51012 | 349.0 | 349.0 | 193.0 | -0.002442 | 0.432665 |
| S3_official_genai_relevant_all | CAR[0,+1] | -0.001926 | 0.002024 | 0.341201 | 349.0 | 349.0 | 193.0 | -0.001912 | 0.446991 |
| S3_official_genai_relevant_all | CAR[-1,+1] | -0.005099 | 0.002542 | 0.044866 | 349.0 | 349.0 | 193.0 | -0.007056 | 0.389685 |
| S3_official_genai_relevant_first_firm | AR[0] | -0.0002 | 0.001628 | 0.902257 | 190.0 | 190.0 | 190.0 | 0.000649 | 0.526316 |
| S3_official_genai_relevant_first_firm | AR[+1] | -0.002936 | 0.002176 | 0.17714 | 190.0 | 190.0 | 190.0 | -0.003629 | 0.405263 |
| S3_official_genai_relevant_first_firm | CAR[0,+1] | -0.003136 | 0.003161 | 0.321183 | 190.0 | 190.0 | 190.0 | -0.002223 | 0.442105 |
| S3_official_genai_relevant_first_firm | CAR[-1,+1] | -0.008251 | 0.003414 | 0.015652 | 190.0 | 190.0 | 190.0 | -0.00789 | 0.357895 |
| S4_model_keyword_registry_all | AR[0] | -0.00266 | 0.001312 | 0.042586 | 247.0 | 247.0 | 146.0 | -0.001479 | 0.477733 |
| S4_model_keyword_registry_all | AR[+1] | -0.000885 | 0.00172 | 0.606899 | 247.0 | 247.0 | 146.0 | -0.003214 | 0.417004 |
| S4_model_keyword_registry_all | CAR[0,+1] | -0.003545 | 0.002441 | 0.146531 | 247.0 | 247.0 | 146.0 | -0.00362 | 0.412955 |
| S4_model_keyword_registry_all | CAR[-1,+1] | -0.006732 | 0.002909 | 0.020683 | 247.0 | 247.0 | 146.0 | -0.009381 | 0.368421 |
| S4_model_keyword_registry_first_firm | AR[0] | -0.002285 | 0.001759 | 0.193907 | 145.0 | 145.0 | 145.0 | 0.000101 | 0.503448 |
| S4_model_keyword_registry_first_firm | AR[+1] | -0.001603 | 0.002516 | 0.52389 | 145.0 | 145.0 | 145.0 | -0.003529 | 0.42069 |
| S4_model_keyword_registry_first_firm | CAR[0,+1] | -0.003889 | 0.003565 | 0.27537 | 145.0 | 145.0 | 145.0 | -0.002503 | 0.427586 |
| S4_model_keyword_registry_first_firm | CAR[-1,+1] | -0.00761 | 0.00364 | 0.03657 | 145.0 | 145.0 | 145.0 | -0.008253 | 0.351724 |

## Focal Firm Returns, Existing Event Clock

| sample_name | outcome_label | estimate | se | p | nobs | events | focal_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|
| S0_exact_model_keyword_all | AR[0] | -0.001414 | 0.001965 | 0.471892 | 185.0 | 185.0 | 115.0 | -0.00238 | 0.454054 |
| S0_exact_model_keyword_all | CAR[0,+1] | -0.003747 | 0.002286 | 0.101124 | 185.0 | 185.0 | 115.0 | -0.003209 | 0.427027 |
| S0_exact_model_keyword_first_firm | AR[0] | -0.002497 | 0.002118 | 0.238565 | 114.0 | 114.0 | 114.0 | -0.003717 | 0.412281 |
| S0_exact_model_keyword_first_firm | CAR[0,+1] | -0.005134 | 0.00239 | 0.031716 | 114.0 | 114.0 | 114.0 | -0.003903 | 0.403509 |
| S0_exact_official_all | AR[0] | -0.00247 | 0.001841 | 0.17979 | 247.0 | 247.0 | 146.0 | -0.003322 | 0.425101 |
| S0_exact_official_all | CAR[0,+1] | -0.00348 | 0.002234 | 0.11923 | 247.0 | 247.0 | 146.0 | -0.00235 | 0.437247 |
| S0_exact_official_first_firm | AR[0] | -0.005443 | 0.001986 | 0.006128 | 144.0 | 144.0 | 144.0 | -0.005955 | 0.354167 |
| S0_exact_official_first_firm | CAR[0,+1] | -0.006471 | 0.00249 | 0.009356 | 144.0 | 144.0 | 144.0 | -0.003806 | 0.395833 |
| S1_genai_service_filing_day_all | AR[0] | -0.000872 | 0.002346 | 0.710155 | 85.0 | 85.0 | 73.0 | -0.000802 | 0.494118 |
| S1_genai_service_filing_day_all | CAR[0,+1] | -0.000492 | 0.003386 | 0.88455 | 85.0 | 85.0 | 73.0 | 0.000377 | 0.517647 |
| S1_genai_service_filing_day_first_firm | AR[0] | -0.001445 | 0.002581 | 0.575548 | 73.0 | 73.0 | 73.0 | 0.000241 | 0.506849 |
| S1_genai_service_filing_day_first_firm | CAR[0,+1] | -0.000143 | 0.00349 | 0.967298 | 73.0 | 73.0 | 73.0 | 0.000377 | 0.520548 |
| S2_deep_synthesis_notice_all | AR[0] | -0.003975 | 0.001796 | 0.026887 | 222.0 | 222.0 | 153.0 | -0.005173 | 0.373874 |
| S2_deep_synthesis_notice_all | CAR[0,+1] | -0.005457 | 0.002229 | 0.014336 | 222.0 | 222.0 | 153.0 | -0.004949 | 0.387387 |
| S2_deep_synthesis_notice_first_firm | AR[0] | -0.004826 | 0.001982 | 0.014913 | 150.0 | 150.0 | 150.0 | -0.005955 | 0.346667 |
| S2_deep_synthesis_notice_first_firm | CAR[0,+1] | -0.006032 | 0.002576 | 0.019207 | 150.0 | 150.0 | 150.0 | -0.006248 | 0.346667 |
| S3_official_genai_relevant_all | AR[0] | -0.003634 | 0.001439 | 0.011536 | 345.0 | 345.0 | 192.0 | -0.004027 | 0.408696 |
| S3_official_genai_relevant_all | CAR[0,+1] | -0.004788 | 0.001821 | 0.008561 | 345.0 | 345.0 | 192.0 | -0.004596 | 0.414493 |
| S3_official_genai_relevant_first_firm | AR[0] | -0.005552 | 0.001664 | 0.000851 | 189.0 | 189.0 | 189.0 | -0.006003 | 0.359788 |
| S3_official_genai_relevant_first_firm | CAR[0,+1] | -0.005732 | 0.002187 | 0.008779 | 189.0 | 189.0 | 189.0 | -0.004834 | 0.396825 |
| S4_model_keyword_registry_all | AR[0] | -0.00334 | 0.001715 | 0.051476 | 243.0 | 243.0 | 145.0 | -0.003029 | 0.436214 |
| S4_model_keyword_registry_all | CAR[0,+1] | -0.005437 | 0.002015 | 0.006974 | 243.0 | 243.0 | 145.0 | -0.00451 | 0.419753 |
| S4_model_keyword_registry_first_firm | AR[0] | -0.003816 | 0.001881 | 0.042539 | 144.0 | 144.0 | 144.0 | -0.004594 | 0.416667 |
| S4_model_keyword_registry_first_firm | CAR[0,+1] | -0.005377 | 0.002157 | 0.012684 | 144.0 | 144.0 | 144.0 | -0.004619 | 0.402778 |

## Product-Market Peer Returns

| sample_name | outcome_label | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|
| S0_exact_model_keyword_all | AR[0] | -0.000999 | 0.001535 | 0.515264 | 1380.0 | 154.0 | 472.0 | -0.001063 | 0.481884 |
| S0_exact_model_keyword_all | CAR[0,+1] | -0.002305 | 0.001989 | 0.246489 | 1380.0 | 154.0 | 472.0 | -0.002032 | 0.465217 |
| S0_exact_model_keyword_first_firm | AR[0] | -0.001575 | 0.001951 | 0.419329 | 822.0 | 92.0 | 439.0 | -0.001583 | 0.46472 |
| S0_exact_model_keyword_first_firm | CAR[0,+1] | -0.001003 | 0.002528 | 0.691458 | 822.0 | 92.0 | 439.0 | -0.001254 | 0.482968 |
| S0_exact_official_all | AR[0] | -0.001476 | 0.001473 | 0.31655 | 1779.0 | 198.0 | 542.0 | -0.001456 | 0.470489 |
| S0_exact_official_all | CAR[0,+1] | -0.002769 | 0.001868 | 0.138309 | 1779.0 | 198.0 | 542.0 | -0.002363 | 0.460371 |
| S0_exact_official_first_firm | AR[0] | -0.001645 | 0.00188 | 0.381347 | 1001.0 | 112.0 | 508.0 | -0.001814 | 0.45954 |
| S0_exact_official_first_firm | CAR[0,+1] | -0.002044 | 0.002338 | 0.382078 | 1001.0 | 112.0 | 508.0 | -0.002054 | 0.470529 |
| S1_genai_service_filing_day_all | AR[0] | -0.001783 | 0.002068 | 0.388492 | 655.0 | 73.0 | 354.0 | -0.001916 | 0.459542 |
| S1_genai_service_filing_day_all | CAR[0,+1] | 7.5e-05 | 0.002686 | 0.977649 | 655.0 | 73.0 | 354.0 | -0.000598 | 0.490076 |
| S1_genai_service_filing_day_first_firm | AR[0] | -0.002303 | 0.002076 | 0.267402 | 575.0 | 64.0 | 346.0 | -0.001916 | 0.45913 |
| S1_genai_service_filing_day_first_firm | CAR[0,+1] | 0.001346 | 0.002699 | 0.617947 | 575.0 | 64.0 | 346.0 | -0.000119 | 0.497391 |
| S2_deep_synthesis_notice_all | AR[0] | -0.002793 | 0.001766 | 0.113832 | 1556.0 | 175.0 | 573.0 | -0.002011 | 0.460154 |
| S2_deep_synthesis_notice_all | CAR[0,+1] | -0.005967 | 0.002147 | 0.005444 | 1556.0 | 175.0 | 573.0 | -0.005183 | 0.420951 |
| S2_deep_synthesis_notice_first_firm | AR[0] | -0.002273 | 0.002224 | 0.306722 | 1000.0 | 113.0 | 539.0 | -0.001571 | 0.467 |
| S2_deep_synthesis_notice_first_firm | CAR[0,+1] | -0.00497 | 0.002721 | 0.067778 | 1000.0 | 113.0 | 539.0 | -0.004444 | 0.44 |
| S3_official_genai_relevant_all | AR[0] | -0.002985 | 0.001305 | 0.022209 | 2430.0 | 273.0 | 657.0 | -0.002402 | 0.451852 |
| S3_official_genai_relevant_all | CAR[0,+1] | -0.004741 | 0.001609 | 0.00321 | 2430.0 | 273.0 | 657.0 | -0.00422 | 0.434979 |
| S3_official_genai_relevant_first_firm | AR[0] | -0.003392 | 0.001789 | 0.057966 | 1282.0 | 144.0 | 618.0 | -0.002273 | 0.446958 |
| S3_official_genai_relevant_first_firm | CAR[0,+1] | -0.003315 | 0.002149 | 0.122889 | 1282.0 | 144.0 | 618.0 | -0.002978 | 0.458658 |
| S4_model_keyword_registry_all | AR[0] | -0.002991 | 0.001419 | 0.035063 | 1794.0 | 201.0 | 550.0 | -0.002369 | 0.457079 |
| S4_model_keyword_registry_all | CAR[0,+1] | -0.004833 | 0.001761 | 0.006068 | 1794.0 | 201.0 | 550.0 | -0.004412 | 0.434225 |
| S4_model_keyword_registry_first_firm | AR[0] | -0.003377 | 0.001892 | 0.07435 | 1036.0 | 116.0 | 516.0 | -0.002345 | 0.449807 |
| S4_model_keyword_registry_first_firm | CAR[0,+1] | -0.003607 | 0.002361 | 0.126568 | 1036.0 | 116.0 | 516.0 | -0.003379 | 0.452703 |

## Peer Minus Focal

| sample_name | events | peer_minus_focal_mean | se | p | median | positive_share | mean_peer_car | mean_focal_car |
|---|---|---|---|---|---|---|---|---|
| S0_exact_model_keyword_all | 147.0 | -0.000576 | 0.002326 | 0.80436 | -0.00011 | 0.496599 | -0.003197 | -0.002621 |
| S0_exact_model_keyword_first_firm | 88.0 | 0.001336 | 0.002551 | 0.600357 | 0.00097 | 0.522727 | -0.002662 | -0.003998 |
| S0_exact_official_all | 189.0 | -0.00219 | 0.002067 | 0.289412 | -0.00127 | 0.481481 | -0.003772 | -0.001582 |
| S0_exact_official_first_firm | 107.0 | -1.9e-05 | 0.002543 | 0.993886 | 0.001145 | 0.53271 | -0.00407 | -0.00405 |
| S1_genai_service_filing_day_all | 69.0 | 0.000644 | 0.002954 | 0.827342 | -0.002819 | 0.492754 | 0.00116 | 0.000515 |
| S1_genai_service_filing_day_first_firm | 60.0 | 0.002208 | 0.003211 | 0.491778 | -0.001398 | 0.5 | 0.002824 | 0.000616 |
| S2_deep_synthesis_notice_all | 158.0 | -0.002583 | 0.002247 | 0.250236 | -0.000223 | 0.481013 | -0.007674 | -0.005091 |
| S2_deep_synthesis_notice_first_firm | 103.0 | -0.001065 | 0.002427 | 0.660758 | -7.8e-05 | 0.495146 | -0.00697 | -0.005905 |
| S3_official_genai_relevant_all | 248.0 | -0.001388 | 0.001722 | 0.420169 | -0.000285 | 0.483871 | -0.00559 | -0.004203 |
| S3_official_genai_relevant_first_firm | 133.0 | 0.00024 | 0.002152 | 0.911044 | 0.001145 | 0.526316 | -0.004889 | -0.005129 |
| S4_model_keyword_registry_all | 183.0 | -0.000758 | 0.00204 | 0.710349 | -0.001353 | 0.480874 | -0.00543 | -0.004672 |
| S4_model_keyword_registry_first_firm | 107.0 | 0.000406 | 0.002268 | 0.857798 | -0.00011 | 0.495327 | -0.004635 | -0.005041 |

## Output Files

- `results/v65_registry_based_event_study_20260612/registry_matched_a_share_high_confidence.csv`
- `results/v65_registry_based_event_study_20260612/registry_event_samples.csv`
- `results/v65_registry_based_event_study_20260612/focal_returns_strict_next_day_summary.csv`
- `results/v65_registry_based_event_study_20260612/peer_returns_summary.csv`
- `results/v65_registry_based_event_study_20260612/peer_minus_focal_summary.csv`
- `results/v65_registry_based_event_study_20260612/v65_registry_based_event_study_20260612.xlsx`

## Immediate Read

This is a rescue-path diagnostic, not yet the final paper design. The first useful question is whether a registry event is a credible public information event. Deep-synthesis notice dates are cleaner for that purpose than GenAI service filing dates, because the latter are record-level filing dates inside a periodically updated public attachment.
