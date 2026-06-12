# v66 Registry Full-Recall Matching

## Scope

- Input: v64 official CAC GenAI-relevant registry master.
- Purpose: recall every textual A-share candidate, including low-confidence name and model/app-text hits.
- Guardrail: this is a manual-review universe, not a clean event-study sample.

## Files

- `results/v66_registry_full_recall_matching_20260612/registry_all_candidate_matches.csv`
- `results/v66_registry_full_recall_matching_20260612/registry_row_candidate_summary.csv`
- `results/v66_registry_full_recall_matching_20260612/registry_best_tier_candidates_keep_ties.csv`
- `results/v66_registry_full_recall_matching_20260612/registry_full_recall_review_queue.csv`
- `/Users/mac/Documents/Obsidian Vault/23-5/T05_备案主体A股全召回复核工作台_v66_20260612.md`
- `/Users/mac/Documents/Obsidian Vault/23-5/T05_备案主体A股全召回复核队列_v66_20260612.csv`

## Counts By Source

| registry_source | registry_rows | registry_entities | rows_with_candidates | candidate_pairs | candidate_firms |
|---|---|---|---|---|---|
| cac_algorithm_filing | 87.0 | 82.0 | 11.0 | 17.0 | 9.0 |
| cac_deep_synthesis_filing | 7059.0 | 4947.0 | 688.0 | 1076.0 | 284.0 |
| cac_genai_service | 1358.0 | 1183.0 | 201.0 | 325.0 | 156.0 |

## Counts By Status

| registry_source | registry_status | registry_rows | rows_with_candidates | candidate_pairs |
|---|---|---|---|---|
| cac_algorithm_filing | 备案清单 | 87.0 | 11.0 | 17.0 |
| cac_deep_synthesis_filing | 备案清单 | 7059.0 | 688.0 | 1076.0 |
| cac_genai_service | 已备案 | 847.0 | 135.0 | 214.0 |
| cac_genai_service | 已登记 | 511.0 | 66.0 | 111.0 |

## Candidate Methods

| match_scope | match_method | candidate_pairs | registry_rows | firms |
|---|---|---|---|---|
| entity_name | full_name_exact | 308.0 | 308.0 | 153.0 |
| entity_name | short_name_contained_len2 | 303.0 | 294.0 | 101.0 |
| entity_name | short_name_prefix_len4plus | 207.0 | 207.0 | 85.0 |
| entity_name | short_name_contained_len4plus | 130.0 | 130.0 | 67.0 |
| entity_name | short_name_contained_len3 | 73.0 | 73.0 | 30.0 |
| entity_name | short_name_prefix_len2 | 61.0 | 60.0 | 28.0 |
| entity_name | short_name_prefix_len3 | 54.0 | 54.0 | 26.0 |
| entity_name | full_name_contained | 8.0 | 8.0 | 5.0 |
| entity_name | short_name_exact_entity | 1.0 | 1.0 | 1.0 |
| entity_name | short_name_prefix_risky_next_char | 1.0 | 1.0 | 1.0 |
| item_product_text | stock_short_in_item_text_len3 | 143.0 | 141.0 | 39.0 |
| item_product_text | stock_short_in_item_text_len4plus | 129.0 | 127.0 | 63.0 |

## GenAI Service Rows

| registry_source | registry_status | registry_rows | rows_with_candidates | candidate_pairs |
|---|---|---|---|---|
| cac_genai_service | 已备案 | 847.0 | 135.0 | 214.0 |
| cac_genai_service | 已登记 | 511.0 | 66.0 | 111.0 |

## P0 Examples

| review_priority | registry_source | registry_status | entity_name | item_name | focal_code | stock_name | match_scope | match_method | match_text | match_rank | firms_for_registry_row |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 国泰海通证券股份有限公司 | 君弘灵犀内容生成算法 | 600837 | 海通证券 | entity_name | full_name_contained | 海通证券股份有限公司 | 90.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 国泰海通证券股份有限公司 | 君弘灵犀内容生成算法 | 600837 | 海通证券 | entity_name | short_name_contained_len4plus | 海通证券 | 70.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 科沃斯家用机器人有限公司 | 科沃斯机器人大模型算法 | 603486 | 科沃斯 | entity_name | short_name_prefix_len3 | 科沃斯 | 76.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 中电科东方通信集团有限公司 | 电科东信百灵交互式对话算法 | 600776 | 东方通信 | entity_name | short_name_contained_len4plus | 东方通信 | 70.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 上海新致软件股份有限公司 | 新致司法类案检索LSTM生成合成算法 | 688590 | 新致软件 | entity_name | short_name_contained_len4plus | 新致软件 | 70.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 北京市博汇科技股份有限公司 | 博汇学道音视频分析大模型算法 | 688004 | 博汇科技 | entity_name | short_name_contained_len4plus | 博汇科技 | 70.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 京北方信息技术股份有限公司 | 京北方检索增强型文本生成大模型算法 | 002987 | 京北方 | entity_name | short_name_prefix_len3 | 京北方 | 76.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 北京市博汇科技股份有限公司 | 博汇慧视多模态内容分析大模型算法 | 688004 | 博汇科技 | entity_name | short_name_contained_len4plus | 博汇科技 | 70.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 浪潮软件科技有限公司 | 浪潮焱宇运营商知识服务大模型算法 | 600756 | 浪潮软件 | entity_name | short_name_prefix_len4plus | 浪潮软件 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 长城汽车股份有限公司徐水哈弗销售分公司 | GWM聊天助手文本生成算法 | 601633 | 长城汽车 | entity_name | full_name_contained | 长城汽车股份有限公司 | 90.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 长城汽车股份有限公司徐水哈弗销售分公司 | GWM聊天助手文本生成算法 | 601633 | 长城汽车 | entity_name | short_name_prefix_len4plus | 长城汽车 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 中兴通讯股份有限公司 | 中兴星云大模型文生图算法 | 000063 | 中兴通讯 | entity_name | short_name_prefix_len4plus | 中兴通讯 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 世纪恒通科技股份有限公司 | 小兔内容生成算法 | 301428 | 世纪恒通 | entity_name | short_name_prefix_len4plus | 世纪恒通 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 中兴通讯股份有限公司 | 中兴星云大模型文本生成算法 | 000063 | 中兴通讯 | entity_name | short_name_prefix_len4plus | 中兴通讯 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 国金证券股份有限公司 | 国金证券大模型产业链图谱挖掘算法 | 600109 | 国金证券 | entity_name | short_name_prefix_len4plus | 国金证券 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 国金证券股份有限公司 | 国金证券AI问答大模型算法 | 600109 | 国金证券 | entity_name | short_name_prefix_len4plus | 国金证券 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 长城汽车股份有限公司 | CoffeeAgent大模型算法 | 601633 | 长城汽车 | entity_name | short_name_prefix_len4plus | 长城汽车 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 中兴通讯股份有限公司 | 中兴星云语言大模型算法 | 000063 | 中兴通讯 | entity_name | short_name_prefix_len4plus | 中兴通讯 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 国金证券股份有限公司 | 国金证券AI意图识别大模型算法 | 600109 | 国金证券 | entity_name | short_name_prefix_len4plus | 国金证券 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 华泰证券股份有限公司 | 华泰乐问生成合成类算法 | 601688 | 华泰证券 | entity_name | short_name_prefix_len4plus | 华泰证券 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 国泰海通证券股份有限公司 | 国泰海通语音生成算法 | 600837 | 海通证券 | entity_name | full_name_contained | 海通证券股份有限公司 | 90.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 国泰海通证券股份有限公司 | 国泰海通语音生成算法 | 600837 | 海通证券 | entity_name | short_name_contained_len4plus | 海通证券 | 70.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 兴业证券股份有限公司 | 兴业证券机智猫内容生成算法 | 601377 | 兴业证券 | entity_name | short_name_prefix_len4plus | 兴业证券 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 中兴通讯股份有限公司 | 中兴星云多模态大模型算法 | 000063 | 中兴通讯 | entity_name | short_name_prefix_len4plus | 中兴通讯 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 长城汽车股份有限公司 | 长城汽车标准知识大模型算法 | 601633 | 长城汽车 | entity_name | short_name_prefix_len4plus | 长城汽车 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 国信证券股份有限公司 | 国信证券金太阳大模型算法 | 002736 | 国信证券 | entity_name | short_name_prefix_len4plus | 国信证券 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 中国石化销售股份有限公司 | 易捷加油AI数字员工文本生成算法 | 600028 | 中国石化 | entity_name | short_name_prefix_len4plus | 中国石化 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 申万宏源证券有限公司 | 申万宏源智能问答生成类算法 | 000166 | 申万宏源 | entity_name | short_name_prefix_len4plus | 申万宏源 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_deep_synthesis_filing | 备案清单 | 申万宏源证券有限公司 | 申万宏源智能问答生成类算法 | 000562 | 宏源证券 | entity_name | short_name_contained_len4plus | 宏源证券 | 70.0 | 2.0 |
| P0-同一备案多候选 | cac_genai_service | 已备案 | 中兴通讯股份有限公司 | 星云大模型 | 000063 | 中兴通讯 | entity_name | short_name_prefix_len4plus | 中兴通讯 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_genai_service | 已备案 | 长城汽车股份有限公司 | CoffeeAgent | 601633 | 长城汽车 | entity_name | short_name_prefix_len4plus | 长城汽车 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_genai_service | 已备案 | 中科曙光南京研究院有限公司 | 曙光神玑大模型 | 603019 | 中科曙光 | entity_name | short_name_prefix_len4plus | 中科曙光 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_genai_service | 已登记 | 华泰证券股份有限公司 | 涨乐 | 601688 | 华泰证券 | entity_name | short_name_prefix_len4plus | 华泰证券 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_genai_service | 已登记 | 中国工商银行股份有限公司常州分行 | 网点厅堂机器人 | 601398 | 工商银行 | entity_name | full_name_contained | 中国工商银行股份有限公司 | 90.0 | 2.0 |
| P0-同一备案多候选 | cac_genai_service | 已登记 | 中国工商银行股份有限公司常州分行 | 网点厅堂机器人 | 601398 | 工商银行 | entity_name | short_name_contained_len4plus | 工商银行 | 70.0 | 2.0 |
| P0-同一备案多候选 | cac_genai_service | 已登记 | 中国石化销售股份有限公司 | 易捷加油AI数字员工 | 600028 | 中国石化 | entity_name | short_name_prefix_len4plus | 中国石化 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_genai_service | 已备案 | 中国航天科技创新研究院 | 天玄·开物 | 000901 | 航天科技 | entity_name | short_name_contained_len4plus | 航天科技 | 70.0 | 2.0 |
| P0-同一备案多候选 | cac_genai_service | 已备案 | 中国航天科技创新研究院 | 天玄·成务 | 000901 | 航天科技 | entity_name | short_name_contained_len4plus | 航天科技 | 70.0 | 2.0 |
| P0-同一备案多候选 | cac_genai_service | 已备案 | 中国航天科技创新研究院 | 天玄·千河 | 000901 | 航天科技 | entity_name | short_name_contained_len4plus | 航天科技 | 70.0 | 2.0 |
| P0-同一备案多候选 | cac_genai_service | 已登记 | 国信证券股份有限公司 | 国信证券金太阳大模型 | 002736 | 国信证券 | entity_name | short_name_prefix_len4plus | 国信证券 | 82.0 | 2.0 |
| P0-同一备案多候选 | cac_genai_service | 已登记 | 国金证券股份有限公司 | 国金证券AI问答大模型 | 600109 | 国金证券 | entity_name | short_name_prefix_len4plus | 国金证券 | 82.0 | 2.0 |
| P0-极低置信名称召回 | cac_algorithm_filing | 备案清单 | 西藏佳斯特信息技术有限公司 | 西藏佳斯特信息技术有限公司网约车分单算法 | 000070 | ST 特信 | entity_name | short_name_contained_len2 | 特信 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_algorithm_filing | 备案清单 | 浙江山迅网络科技有限公司 | 浙江山迅网络融媒体视音频多模态指纹信息检索算法 | 600389 | 江山股份 | entity_name | short_name_contained_len2 | 江山 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_algorithm_filing | 备案清单 | 杭州金诚信息安全科技有限公司 | 金诚AI大模型攻击过滤算法 | 603979 | 金诚信 | entity_name | short_name_contained_len3 | 金诚信 | 54.0 | 1.0 |
| P0-极低置信名称召回 | cac_algorithm_filing | 备案清单 | 广州市品高软件股份有限公司 | 品高多模态分级信息检索算法 | 688227 | 品高股份 | entity_name | short_name_contained_len2 | 品高 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京红棉小冰科技有限公司 | 红棉小冰语言模型算法 | 000523 | 红棉股份 | entity_name | short_name_contained_len2 | 红棉 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京红棉小冰科技有限公司 | 小冰歌声合成算法 | 000523 | 红棉股份 | entity_name | short_name_contained_len2 | 红棉 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京红棉小冰科技有限公司 | 小冰语音合成算法 | 000523 | 红棉股份 | entity_name | short_name_contained_len2 | 红棉 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京东港瑞宏科技有限公司 | 东港-生成合成算法 | 002117 | 东港股份 | entity_name | short_name_contained_len2 | 东港 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 武汉莱博信息技术有限公司 | 笔杆论文思路辅助算法 | 600083 | 博信股份 | entity_name | short_name_contained_len2 | 博信 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 湖北鼎森智能科技有限公司 | Magook开放域自然对话算法 | 300824 | 北鼎股份 | entity_name | short_name_contained_len2 | 北鼎 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 达闼机器人股份有限公司 | 达闼大模型算法 | 300024 | 机器人 | entity_name | short_name_contained_len3 | 机器人 | 54.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 上海宽娱数码科技有限公司 | 哔哩哔哩语音合成算法 | 600700 | ST 数码 | entity_name | short_name_contained_len2 | 数码 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 达闼机器人股份有限公司 | 达闼RobotGPT多模态具身大模型算法 | 300024 | 机器人 | entity_name | short_name_contained_len3 | 机器人 | 54.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 上海宽娱数码科技有限公司 | 哔哩哔哩评论弹幕生成算法 | 600700 | ST 数码 | entity_name | short_name_contained_len2 | 数码 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 新华智云科技有限公司 | 智云2D数字人合成算法 | 300097 | ST 智云 | entity_name | short_name_contained_len2 | 智云 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 新华智云科技有限公司 | 智云3D数字人合成算法 | 300097 | ST 智云 | entity_name | short_name_contained_len2 | 智云 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 新华智云科技有限公司 | TTS语音合成算法 | 300097 | ST 智云 | entity_name | short_name_contained_len2 | 智云 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京红棉小冰科技有限公司 | 红棉小冰文本生成算法 | 000523 | 红棉股份 | entity_name | short_name_contained_len2 | 红棉 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京值得买科技股份有限公司 | 什么值得买文本生成算法 | 300785 | 值得买 | entity_name | short_name_contained_len3 | 值得买 | 54.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 浙江同花顺网络科技有限公司 | 同花顺HithinkGPT大模型算法 | 300033 | 同花顺 | entity_name | short_name_contained_len3 | 同花顺 | 54.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京奇点星宇科技有限公司 | 片羽图像生成算法 | 601799 | 星宇股份 | entity_name | short_name_contained_len2 | 星宇 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 上海大智慧信息科技有限公司 | 大智慧生成合成算法 | 601519 | 大智慧 | entity_name | short_name_contained_len3 | 大智慧 | 54.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 上海星云爱店科技有限公司 | 小in大模型算法 | 300648 | 星云股份 | entity_name | short_name_contained_len2 | 星云 | 38.0 | 2.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 上海星云爱店科技有限公司 | 小in大模型算法 | 603115 | 海星股份 | entity_name | short_name_contained_len2 | 海星 | 38.0 | 2.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京红棉小冰科技有限公司 | 小冰数字人合成算法 | 000523 | 红棉股份 | entity_name | short_name_contained_len2 | 红棉 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京红棉小冰科技有限公司 | 小冰歌声合成服务算法 | 000523 | 红棉股份 | entity_name | short_name_contained_len2 | 红棉 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京红棉小冰科技有限公司 | 小冰嘴形驱动服务算法 | 000523 | 红棉股份 | entity_name | short_name_contained_len2 | 红棉 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京慧辰资道资讯股份有限公司 | 慧辰大模型内容生成算法 | 688500 | 慧辰股份 | entity_name | short_name_contained_len2 | 慧辰 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京红棉小冰科技有限公司 | 小冰语音合成服务算法 | 000523 | 红棉股份 | entity_name | short_name_contained_len2 | 红棉 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京红棉小冰科技有限公司 | 小冰嘴形驱动算法 | 000523 | 红棉股份 | entity_name | short_name_contained_len2 | 红棉 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 上海天壤智能科技有限公司 | 天壤小白开放平台大语言生成模型算法 | 603759 | 海天股份 | entity_name | short_name_contained_len2 | 海天 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京一亩田新农网络科技有限公司 | 一亩田小田智能客服算法 | 002942 | 新农股份 | entity_name | short_name_contained_len2 | 新农 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京红棉小冰科技有限公司 | 小冰人脸生成算法 | 000523 | 红棉股份 | entity_name | short_name_contained_len2 | 红棉 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 北京红棉小冰科技有限公司 | 小冰图像生成算法 | 000523 | 红棉股份 | entity_name | short_name_contained_len2 | 红棉 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 金叶天成（北京）科技有限公司 | 金叶天成医学生成合成算法 | 600112 | ST 天成 | entity_name | short_name_contained_len2 | 天成 | 38.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 同方知网数字科技有限公司 | CNKIAI学术研究助手算法 | 600100 | 同方股份 | entity_name | short_name_prefix_len2 | 同方 | 50.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 同方知网数字科技有限公司 | 知网智能文档生成算法 | 600100 | 同方股份 | entity_name | short_name_prefix_len2 | 同方 | 50.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 百川智能科技有限公司 | 百川大模型算法-1 | 002455 | 百川股份 | entity_name | short_name_prefix_len2 | 百川 | 50.0 | 1.0 |
| P0-极低置信名称召回 | cac_deep_synthesis_filing | 备案清单 | 百川智能科技有限公司 | 百川大模型算法 | 002455 | 百川股份 | entity_name | short_name_prefix_len2 | 百川 | 50.0 | 1.0 |
