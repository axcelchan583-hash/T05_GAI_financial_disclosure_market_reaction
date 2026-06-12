# v61 Model/App-Layer GenAI Event Study

## Scope

- Input: v56 expanded A sample.
- Main sample `ModelApp_own_out`: external-facing (`out=1`) own GenAI model/app-layer event, without requiring strict launch/release/filing wording.
- This is wider than v60 strict core launch and keeps indirect but own model/app actions such as investment, project construction, contracts, subsidiary setup, and investor-record disclosures if the LLM coded them as credible A events.
- Intermediate sample `ModelApp_clean_title`: the same model/app layer but excludes noisy title forms such as board resolutions, issuance plans, feasibility reports, investor records, contracts, M&A, cooperation agreements, and project construction.
- Focal firm main timing uses strict next trading day because CNINFO disclosures are often released after market close. Peer and relation panels reuse v56/v57/v58 return panels, so they use the existing event-date-to-next-available-trading-day convention.

## Sample Counts

| sample_name | events | focal_firms | first_date | last_date | model_layer |
|---|---|---|---|---|---|
| ModelApp_own_out_all | 61.0 | 55.0 | 2023-03-30 00:00:00 | 2026-04-28 00:00:00 | app;model |
| ModelApp_own_out_first_firm | 55.0 | 55.0 | 2023-03-30 00:00:00 | 2026-04-28 00:00:00 | app;model |
| ModelApp_clean_title_all | 14.0 | 12.0 | 2023-04-10 00:00:00 | 2026-04-28 00:00:00 | app;model |
| ModelApp_clean_title_first_firm | 12.0 | 12.0 | 2023-04-10 00:00:00 | 2026-04-28 00:00:00 | app;model |
| ModelApp_realized_plus_all | 14.0 | 12.0 | 2023-05-06 00:00:00 | 2026-04-28 00:00:00 | app;model |
| ModelApp_realized_plus_first_firm | 12.0 | 12.0 | 2023-05-06 00:00:00 | 2026-04-28 00:00:00 | app;model |
| Model_only_own_out_all | 35.0 | 32.0 | 2023-03-30 00:00:00 | 2026-04-24 00:00:00 | model |
| App_only_own_out_all | 26.0 | 25.0 | 2023-05-15 00:00:00 | 2026-04-28 00:00:00 | app |

## Layer and Category Composition

| layer | primary_pom_like_category | events | firms |
|---|---|---|---|
| app | v34_deepseek_direct_event / v34_direct_event_414 | 9.0 | 9.0 |
| app | 投资/建设/增资/收购/智算中心/大模型项目 | 9.0 | 8.0 |
| app | 签署战略合作/合作协议 | 4.0 | 4.0 |
| app | 产品/平台/模型发布、上线、成果发布 | 2.0 | 2.0 |
| app | v35_keyword_backfill_medium / v35_keyword_recovered_backfill_119 | 1.0 | 1.0 |
| app | v35_keyword_backfill_strong / v35_keyword_recovered_backfill_119 | 1.0 | 1.0 |
| model | v34_deepseek_direct_event / v34_direct_event_414 | 14.0 | 14.0 |
| model | 投资/建设/增资/收购/智算中心/大模型项目 | 11.0 | 11.0 |
| model | 产品/平台/模型发布、上线、成果发布 | 8.0 | 8.0 |
| model | v35_keyword_backfill_medium / v35_keyword_recovered_backfill_119 | 1.0 | 1.0 |
| model | 签署战略合作/合作协议 | 1.0 | 1.0 |

## Model/App Events

| event_date | focal_code | sec_name | announcement_title | primary_pom_like_category | layer | realized | core_launch_text_hit | core_excluded_title_form |
|---|---|---|---|---|---|---|---|---|
| 2023-04-10 00:00:00 | 300418 | 昆仑万维 | 昆仑万维：关于发布大语言模型“天工”3.5的公告 | 产品/平台/模型发布、上线、成果发布 | model | - | True | False |
| 2023-05-06 00:00:00 | 002230 | 科大讯飞 | 科大讯飞：关于讯飞星火认知大模型成果发布会的提示性公告 | 产品/平台/模型发布、上线、成果发布 | model | + | True | False |
| 2023-07-08 00:00:00 | 688095 | 福昕软件 | 福昕软件：福建福昕软件开发股份有限公司关于使用部分超募资金投资建设新项目并向全资子公司增资的公告 | 投资/建设/增资/收购/智算中心/大模型项目 | app | - | False | True |
| 2023-07-10 00:00:00 | 301052 | 果麦文化 | 果麦文化：关于增资参股上海星图比特信息技术服务有限公司暨签署软件开发合作协议的公告 | 签署战略合作/合作协议 | app | - | False | True |
| 2023-07-14 00:00:00 | 300418 | 昆仑万维 | 昆仑万维：关于公司与B端客户签订AI技术服务协议的公告 | 签署战略合作/合作协议 | app | - | False | False |
| 2023-09-21 00:00:00 | 002657 | 中科金财 | 中科金财：关于拟设立全资子公司的公告 | 投资/建设/增资/收购/智算中心/大模型项目 | model | - | False | True |
| 2023-10-12 00:00:00 | 002362 | 汉王科技 | 汉王科技：关于召开汉王天地大模型阶段成果发布会的提示性公告 | 产品/平台/模型发布、上线、成果发布 | model | + | True | False |
| 2023-11-16 00:00:00 | 300075 | 数字政通 | 数字政通：关于公司发布新产品的公告 | 产品/平台/模型发布、上线、成果发布 | model | + | True | False |
| 2023-11-20 00:00:00 | 300288 | 朗玛信息 | 朗玛信息：关于“39AI全科医生”大模型备案通过的公告 | 产品/平台/模型发布、上线、成果发布 | model | - | True | False |
| 2024-01-26 00:00:00 | 688228 | 开普云 | 开普云：自愿性披露关于对外投资设立合资子公司的公告 | 投资/建设/增资/收购/智算中心/大模型项目 | model | - | False | True |
| 2024-02-21 00:00:00 | 002530 | 金财互联 | 金财互联：关于“欣智悦财税大模型算法”备案通过的公告 | 产品/平台/模型发布、上线、成果发布 | model | + | True | False |
| 2024-03-08 00:00:00 | 301316 | 慧博云通 | 慧博云通：关于公司与特定对象签署附条件生效的股份认购协议暨关联交易的公告 | 签署战略合作/合作协议 | model | - | False | True |
| 2024-03-15 00:00:00 | 301169 | 零点有数 | 零点有数：知识增强智能引擎研发项目可行性研究报告 | 投资/建设/增资/收购/智算中心/大模型项目 | app | - | True | True |
| 2024-03-23 00:00:00 | 603859 | 能科科技 | 能科科技：关于签订日常经营性合同的自愿性披露公告 | 签署战略合作/合作协议 | app | - | False | True |
| 2024-03-30 00:00:00 | 002261 | 拓维信息 | 拓维信息：关于控股子公司收到中标通知书的公告 | 投资/建设/增资/收购/智算中心/大模型项目 | model | - | False | True |
| 2024-06-20 00:00:00 | 688232 | 新点软件 | 新点软件：新点软件关于使用部分超募资金投资建设新项目及永久补充流动资金的公告 | 投资/建设/增资/收购/智算中心/大模型项目 | model | - | False | True |
| 2024-11-12 00:00:00 | 301169 | 零点有数 | 零点有数：知识增强智能引擎研发项目可行性研究报告 | 投资/建设/增资/收购/智算中心/大模型项目 | app | - | True | True |
| 2024-12-24 00:00:00 | 837592 | 华信永道 | [临时公告]华信永道:关于大模型算法备案成功的公告 | 产品/平台/模型发布、上线、成果发布 | model | + | True | False |
| 2025-04-10 00:00:00 | 601019 | 山东出版 | 山东出版：山东出版智慧教育平台项目（二期）可行性研究报告 | 投资/建设/增资/收购/智算中心/大模型项目 | app | - | False | True |
| 2025-05-08 00:00:00 | 002421 | 达实智能 | 达实智能：关于深圳机场至大亚湾城际客票系统项目签约的公告 | 投资/建设/增资/收购/智算中心/大模型项目 | app | - | False | False |
| 2025-05-29 00:00:00 | 300789 | 唐源电气 | 唐源电气：关于全资子公司智谷耘行投资设立合资公司的公告 | 投资/建设/增资/收购/智算中心/大模型项目 | model | - | False | True |
| 2025-08-13 00:00:00 | 300065 | 海兰信 | 海兰信：上市公司并购重组财务顾问专业意见附表第2号——重大资产重组 | 投资/建设/增资/收购/智算中心/大模型项目 | model | - | False | True |
| 2025-08-20 00:00:00 | 600653 | 申华控股 | 申华控股：申华控股关于合资设立申维探索（沈阳）科技有限公司的公告 | 投资/建设/增资/收购/智算中心/大模型项目 | app | - | False | True |
| 2025-09-03 00:00:00 | 002980 | 华盛昌 | 华盛昌：关于“DeepSense深度感测大模型”备案通过的自愿性信息披露公告 | 产品/平台/模型发布、上线、成果发布 | model | - | True | False |
| 2025-09-19 00:00:00 | 688588 | 凌志软件 | 凌志软件：凌志软件关于使用剩余超募资金投资在建项目的公告 | 投资/建设/增资/收购/智算中心/大模型项目 | model | - | False | True |
| 2025-09-25 00:00:00 | 300235 | 方直科技 | 方直科技：关于公司发布新产品的公告 | 产品/平台/模型发布、上线、成果发布 | app | + | True | False |
| 2025-09-27 00:00:00 | 002659 | 凯文教育 | 凯文教育：关于对外投资设立合资公司的公告 | 投资/建设/增资/收购/智算中心/大模型项目 | app | - | False | True |
| 2025-10-24 00:00:00 | 300232 | 洲明科技 | 洲明科技：关于投资设立控股子公司的自愿性信息披露公告 | 投资/建设/增资/收购/智算中心/大模型项目 | model | - | False | True |
| 2025-11-05 00:00:00 | 603368 | 柳药集团 | 柳药集团：广西柳药集团股份有限公司投资者交流会议记录 | 投资/建设/增资/收购/智算中心/大模型项目 | model | - | False | True |
| 2025-11-20 00:00:00 | 300036 | 超图软件 | 超图软件：关于项目中标的公告 | 投资/建设/增资/收购/智算中心/大模型项目 | app | - | False | True |
| 2025-11-27 00:00:00 | 002152 | 广电运通 | 广电运通：关于承接人工智能应用中试基地建设项目暨关联交易的公告 | 投资/建设/增资/收购/智算中心/大模型项目 | model | - | False | True |
| 2025-12-26 00:00:00 | 601226 | 华电科工 | 华电科工：华电科工：关于签署首个高海拔新能源场站1.59亿元数字化业务合同的公告 | 签署战略合作/合作协议 | app | - | False | True |
| 2026-04-08 00:00:00 | 603883 | 老百姓 | 老百姓：老百姓大药房连锁股份有限公司机构投资者交流活动会议纪要（2026年3月） | 投资/建设/增资/收购/智算中心/大模型项目 | app | + | False | True |
| 2026-04-24 00:00:00 | 300397 | 天和防务 | 天和防务：关于调整优化公司投资项目的公告 | 投资/建设/增资/收购/智算中心/大模型项目 | model | - | False | False |
| 2026-04-28 00:00:00 | 300075 | 数字政通 | 数字政通：关于公司发布新产品的公告 | 产品/平台/模型发布、上线、成果发布 | app | + | True | False |
| 2023-03-30 00:00:00 | 688327 | 云从科技 | 云从科技：第二届董事会第五次会议决议公告 | v34_deepseek_direct_event / v34_direct_event_414 | model | - | False | True |
| 2023-04-26 00:00:00 | 003005 | 竞业达 | 竞业达：2023年度向特定对象发行A股股票预案 | v34_deepseek_direct_event / v34_direct_event_414 | model | - | False | True |
| 2023-05-15 00:00:00 | 300369 | 绿盟科技 | 绿盟科技：2023年度向特定对象发行股票预案 | v34_deepseek_direct_event / v34_direct_event_414 | app | - | False | True |
| 2023-06-07 00:00:00 | 688031 | 星环科技 | 星环科技：第一届董事会第十六次会议决议公告 | v34_deepseek_direct_event / v34_direct_event_414 | model | - | False | True |
| 2023-06-21 00:00:00 | 300781 | 因赛集团 | 因赛集团：第三届监事会第十一次会议决议公告 | v34_deepseek_direct_event / v34_direct_event_414 | model | - | False | True |
| 2023-07-06 00:00:00 | 688322 | 奥比中光 | 奥比中光：2023年度向特定对象发行A股股票预案 | v34_deepseek_direct_event / v34_direct_event_414 | model | - | False | True |
| 2023-07-07 00:00:00 | 300170 | 汉得信息 | 汉得信息：上海汉得信息技术股份有限公司第五届董事会第十次（临时）会议决议公告 | v34_deepseek_direct_event / v34_direct_event_414 | app | - | False | True |
| 2023-08-07 00:00:00 | 300229 | 拓尔思 | 拓尔思：第五届监事会第十五次会议决议公告 | v34_deepseek_direct_event / v34_direct_event_414 | model | - | False | True |
| 2023-12-01 00:00:00 | 300542 | 新晨科技 | 新晨科技：新晨科技股份有限公司2023年向特定对象发行A股股票预案 | v34_deepseek_direct_event / v34_direct_event_414 | model | - | True | True |
| 2024-02-23 00:00:00 | 300479 | 神思电子 | 神思电子：关于取得发明专利证书的公告 | v34_deepseek_direct_event / v34_direct_event_414 | model | + | False | True |
| 2024-05-27 00:00:00 | 837592 | 华信永道 | [临时公告]华信永道:关于公司与智谱AI战略合作的进展公告 | v34_deepseek_direct_event / v34_direct_event_414 | model | + | True | True |
| 2024-11-20 00:00:00 | 600718 | 东软集团 | 东软集团：东软集团2024年度“提质增效重回报”行动方案 | v35_keyword_backfill_medium / v35_keyword_recovered_backfill_119 | model | + | True | True |
| 2024-12-12 00:00:00 | 002232 | 启明信息 | 启明信息：第七届董事会第十次会议决议的公告 | v34_deepseek_direct_event / v34_direct_event_414 | app | - | False | True |
| 2025-03-31 00:00:00 | 603236 | 移远通信 | 移远通信：2025年度向特定对象发行A股股票预案 | v34_deepseek_direct_event / v34_direct_event_414 | app | - | True | True |
| 2025-04-16 00:00:00 | 688296 | 和达科技 | 和达科技：和达科技2025年度“提质增效重回报”行动方案 | v35_keyword_backfill_strong / v35_keyword_recovered_backfill_119 | app | + | False | True |
| 2025-04-18 00:00:00 | 688258 | 卓易信息 | 卓易信息：卓易信息2025年度“提质增效重回报”专项行动方案 | v35_keyword_backfill_medium / v35_keyword_recovered_backfill_119 | app | - | False | True |
| 2025-04-21 00:00:00 | 300232 | 洲明科技 | 洲明科技：2024年度总经理工作报告 | v34_deepseek_direct_event / v34_direct_event_414 | model | + | True | True |
| 2025-04-28 00:00:00 | 688305 | 科德数控 | 科德数控：科德数控股份有限公司2025年度“提质增效重回报”行动方案 | v34_deepseek_direct_event / v34_direct_event_414 | model | - | False | True |
| 2025-04-29 00:00:00 | 603990 | 麦迪科技 | 麦迪科技：麦迪科技第四届监事会第十五次会议决议公告 | v34_deepseek_direct_event / v34_direct_event_414 | app | - | False | True |
| 2025-05-12 00:00:00 | 300789 | 唐源电气 | 唐源电气：第三届董事会第三十二次会议决议公告 | v34_deepseek_direct_event / v34_direct_event_414 | model | - | False | True |
| 2025-07-21 00:00:00 | 300711 | 广哈通信 | 广哈通信：2025年度向特定对象发行A股股票预案 | v34_deepseek_direct_event / v34_direct_event_414 | app | - | False | True |
| 2025-07-25 00:00:00 | 603918 | 金桥信息 | 金桥信息：上海金桥信息股份有限公司2025年度向特定对象发行股票发行方案的论证分析报告 | v34_deepseek_direct_event / v34_direct_event_414 | app | - | False | True |
| 2025-08-15 00:00:00 | 300380 | 安硕信息 | 安硕信息：2025年度向特定对象发行A股股票预案 | v34_deepseek_direct_event / v34_direct_event_414 | model | - | False | True |
| 2025-11-24 00:00:00 | 300307 | 慈星股份 | 慈星股份：宁波慈星股份有限公司2025年度以简易程序向特定对象发行A股股票预案 | v34_deepseek_direct_event / v34_direct_event_414 | app | - | False | True |
| 2025-12-17 00:00:00 | 301091 | 深城交 | 深城交：深圳市城市交通规划设计研究中心股份有限公司2025年度向特定对象发行A股股票预案 | v34_deepseek_direct_event / v34_direct_event_414 | model | - | False | True |
| 2026-04-28 00:00:00 | 300588 | 熙菱信息 | 熙菱信息：关于未弥补亏损达到实收股本总额三分之一的公告 | v34_deepseek_direct_event / v34_direct_event_414 | app | + | False | False |

## Focal Firm Returns, Strict Next Trading Day

| sample_name | outcome_label | estimate | se | p | nobs | events | focal_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|
| ModelApp_own_out_all | AR[0] | -0.005532 | 0.004512 | 0.220172 | 54.0 | 54.0 | 49.0 | -0.003881 | 0.425926 |
| ModelApp_own_out_all | AR[+1] | -0.005237 | 0.003998 | 0.190265 | 54.0 | 54.0 | 49.0 | -0.009672 | 0.388889 |
| ModelApp_own_out_all | CAR[0,+1] | -0.010768 | 0.00738 | 0.144537 | 54.0 | 54.0 | 49.0 | -0.013106 | 0.296296 |
| ModelApp_own_out_all | CAR[-1,+1] | -0.012888 | 0.007764 | 0.096936 | 54.0 | 54.0 | 49.0 | -0.011931 | 0.37037 |
| ModelApp_own_out_first_firm | AR[0] | -0.006135 | 0.004628 | 0.185014 | 49.0 | 49.0 | 49.0 | -0.00693 | 0.408163 |
| ModelApp_own_out_first_firm | AR[+1] | -0.006385 | 0.004217 | 0.129982 | 49.0 | 49.0 | 49.0 | -0.010706 | 0.387755 |
| ModelApp_own_out_first_firm | CAR[0,+1] | -0.01252 | 0.007505 | 0.095255 | 49.0 | 49.0 | 49.0 | -0.014955 | 0.265306 |
| ModelApp_own_out_first_firm | CAR[-1,+1] | -0.015113 | 0.007994 | 0.05867 | 49.0 | 49.0 | 49.0 | -0.009904 | 0.367347 |
| ModelApp_clean_title_all | AR[0] | -0.001014 | 0.012538 | 0.935544 | 10.0 | 10.0 | 8.0 | -0.005785 | 0.4 |
| ModelApp_clean_title_all | AR[+1] | 0.002782 | 0.012305 | 0.821143 | 10.0 | 10.0 | 8.0 | -0.002435 | 0.5 |
| ModelApp_clean_title_all | CAR[0,+1] | 0.001768 | 0.023107 | 0.939013 | 10.0 | 10.0 | 8.0 | -0.014353 | 0.3 |
| ModelApp_clean_title_all | CAR[-1,+1] | -0.012958 | 0.017683 | 0.463698 | 10.0 | 10.0 | 8.0 | -0.020335 | 0.3 |
| ModelApp_clean_title_first_firm | AR[0] | -0.00452 | 0.014426 | 0.754019 | 8.0 | 8.0 | 8.0 | -0.010839 | 0.25 |
| ModelApp_clean_title_first_firm | AR[+1] | 0.00384 | 0.015123 | 0.799561 | 8.0 | 8.0 | 8.0 | -0.005244 | 0.5 |
| ModelApp_clean_title_first_firm | CAR[0,+1] | -0.000681 | 0.027464 | 0.98023 | 8.0 | 8.0 | 8.0 | -0.020379 | 0.125 |
| ModelApp_clean_title_first_firm | CAR[-1,+1] | -0.019909 | 0.018525 | 0.282513 | 8.0 | 8.0 | 8.0 | -0.022978 | 0.25 |
| ModelApp_realized_plus_all | AR[0] | -0.012395 | 0.006462 | 0.055095 | 10.0 | 10.0 | 9.0 | -0.009967 | 0.3 |
| ModelApp_realized_plus_all | AR[+1] | -0.005264 | 0.004539 | 0.246134 | 10.0 | 10.0 | 9.0 | -0.002435 | 0.5 |
| ModelApp_realized_plus_all | CAR[0,+1] | -0.017658 | 0.007309 | 0.01569 | 10.0 | 10.0 | 9.0 | -0.013991 | 0.2 |
| ModelApp_realized_plus_all | CAR[-1,+1] | -0.017027 | 0.015915 | 0.284691 | 10.0 | 10.0 | 9.0 | -0.022678 | 0.3 |
| ModelApp_realized_plus_first_firm | AR[0] | -0.015391 | 0.006479 | 0.017521 | 9.0 | 9.0 | 9.0 | -0.013003 | 0.222222 |
| ModelApp_realized_plus_first_firm | AR[+1] | -0.005143 | 0.005023 | 0.305924 | 9.0 | 9.0 | 9.0 | 0.001481 | 0.555556 |
| ModelApp_realized_plus_first_firm | CAR[0,+1] | -0.020534 | 0.007838 | 0.008796 | 9.0 | 9.0 | 9.0 | -0.016725 | 0.111111 |
| ModelApp_realized_plus_first_firm | CAR[-1,+1] | -0.01687 | 0.017678 | 0.339935 | 9.0 | 9.0 | 9.0 | -0.023128 | 0.333333 |
| Model_only_own_out_all | AR[0] | -0.007287 | 0.006012 | 0.225535 | 29.0 | 29.0 | 27.0 | -0.003895 | 0.448276 |
| Model_only_own_out_all | AR[+1] | -0.002379 | 0.005316 | 0.654506 | 29.0 | 29.0 | 27.0 | -0.00463 | 0.448276 |
| Model_only_own_out_all | CAR[0,+1] | -0.009666 | 0.010204 | 0.343524 | 29.0 | 29.0 | 27.0 | -0.005296 | 0.310345 |
| Model_only_own_out_all | CAR[-1,+1] | -0.013808 | 0.011357 | 0.224038 | 29.0 | 29.0 | 27.0 | -0.002211 | 0.482759 |
| App_only_own_out_all | AR[0] | -0.003496 | 0.006351 | 0.581995 | 25.0 | 25.0 | 24.0 | -0.002896 | 0.4 |
| App_only_own_out_all | AR[+1] | -0.008551 | 0.005771 | 0.138398 | 25.0 | 25.0 | 24.0 | -0.011799 | 0.32 |
| App_only_own_out_all | CAR[0,+1] | -0.012048 | 0.009917 | 0.224438 | 25.0 | 25.0 | 24.0 | -0.016725 | 0.28 |
| App_only_own_out_all | CAR[-1,+1] | -0.01182 | 0.009938 | 0.234287 | 25.0 | 25.0 | 24.0 | -0.013959 | 0.24 |

## Focal Firm Returns, Existing Event Clock

| sample_name | outcome_label | estimate | se | p | nobs | events | focal_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|
| ModelApp_own_out_all | AR[0] | -0.003669 | 0.005806 | 0.527449 | 55.0 | 55.0 | 50.0 | -3.7e-05 | 0.490909 |
| ModelApp_own_out_all | CAR[0,+1] | -0.006304 | 0.006416 | 0.325832 | 55.0 | 55.0 | 50.0 | -0.012089 | 0.436364 |
| ModelApp_own_out_first_firm | AR[0] | -0.004288 | 0.006753 | 0.525431 | 50.0 | 50.0 | 50.0 | 0.001184 | 0.5 |
| ModelApp_own_out_first_firm | CAR[0,+1] | -0.007225 | 0.007071 | 0.306882 | 50.0 | 50.0 | 50.0 | -0.012619 | 0.44 |
| ModelApp_clean_title_all | AR[0] | -0.014725 | 0.015825 | 0.352111 | 10.0 | 10.0 | 8.0 | -0.016225 | 0.4 |
| ModelApp_clean_title_all | CAR[0,+1] | -0.015739 | 0.015011 | 0.294385 | 10.0 | 10.0 | 8.0 | -0.018227 | 0.2 |
| ModelApp_clean_title_first_firm | AR[0] | -0.019228 | 0.024334 | 0.429418 | 8.0 | 8.0 | 8.0 | -0.016225 | 0.375 |
| ModelApp_clean_title_first_firm | CAR[0,+1] | -0.023749 | 0.020241 | 0.240687 | 8.0 | 8.0 | 8.0 | -0.025736 | 0.125 |
| ModelApp_realized_plus_all | AR[0] | 0.000632 | 0.010634 | 0.952641 | 10.0 | 10.0 | 9.0 | -0.010211 | 0.4 |
| ModelApp_realized_plus_all | CAR[0,+1] | -0.011763 | 0.01342 | 0.380753 | 10.0 | 10.0 | 9.0 | -0.018227 | 0.3 |
| ModelApp_realized_plus_first_firm | AR[0] | 0.003665 | 0.011437 | 0.748666 | 9.0 | 9.0 | 9.0 | -0.006403 | 0.444444 |
| ModelApp_realized_plus_first_firm | CAR[0,+1] | -0.011727 | 0.014912 | 0.431628 | 9.0 | 9.0 | 9.0 | -0.024365 | 0.333333 |
| Model_only_own_out_all | AR[0] | -0.004737 | 0.01012 | 0.639757 | 30.0 | 30.0 | 28.0 | 0.002857 | 0.6 |
| Model_only_own_out_all | CAR[0,+1] | -0.008276 | 0.010314 | 0.422304 | 30.0 | 30.0 | 28.0 | -0.015529 | 0.433333 |
| App_only_own_out_all | AR[0] | -0.002387 | 0.005999 | 0.690655 | 25.0 | 25.0 | 24.0 | -0.011213 | 0.36 |
| App_only_own_out_all | CAR[0,+1] | -0.003938 | 0.007545 | 0.601733 | 25.0 | 25.0 | 24.0 | -0.011648 | 0.44 |

## Product-Market Peer Returns

| sample_name | outcome_label | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|
| ModelApp_own_out_all | AR[0] | -0.001153 | 0.002728 | 0.672509 | 506.0 | 57.0 | 327.0 | -0.001805 | 0.466403 |
| ModelApp_own_out_all | CAR[0,+1] | -0.005166 | 0.003795 | 0.173407 | 506.0 | 57.0 | 327.0 | -0.004589 | 0.420949 |
| ModelApp_own_out_first_firm | AR[0] | -0.001747 | 0.002918 | 0.549263 | 463.0 | 52.0 | 324.0 | -0.002221 | 0.457883 |
| ModelApp_own_out_first_firm | CAR[0,+1] | -0.005643 | 0.004076 | 0.16618 | 463.0 | 52.0 | 324.0 | -0.0046 | 0.414687 |
| ModelApp_clean_title_all | AR[0] | -0.004797 | 0.006171 | 0.436954 | 113.0 | 13.0 | 97.0 | -0.005635 | 0.362832 |
| ModelApp_clean_title_all | CAR[0,+1] | -0.004356 | 0.005836 | 0.455436 | 113.0 | 13.0 | 97.0 | -0.005364 | 0.39823 |
| ModelApp_clean_title_first_firm | AR[0] | -0.004527 | 0.007073 | 0.522181 | 97.0 | 11.0 | 92.0 | -0.003838 | 0.360825 |
| ModelApp_clean_title_first_firm | CAR[0,+1] | -0.003102 | 0.006649 | 0.640791 | 97.0 | 11.0 | 92.0 | -0.005364 | 0.402062 |
| ModelApp_realized_plus_all | AR[0] | 0.004956 | 0.008296 | 0.550285 | 96.0 | 11.0 | 81.0 | -0.00044 | 0.489583 |
| ModelApp_realized_plus_all | CAR[0,+1] | 0.001856 | 0.009048 | 0.837476 | 96.0 | 11.0 | 81.0 | -0.002602 | 0.458333 |
| ModelApp_realized_plus_first_firm | AR[0] | 0.007026 | 0.008683 | 0.418402 | 89.0 | 10.0 | 78.0 | 0.001472 | 0.516854 |
| ModelApp_realized_plus_first_firm | CAR[0,+1] | 0.003923 | 0.009493 | 0.679468 | 89.0 | 10.0 | 78.0 | -0.001664 | 0.47191 |
| Model_only_own_out_all | AR[0] | -0.000507 | 0.003522 | 0.885511 | 297.0 | 33.0 | 222.0 | -0.001696 | 0.468013 |
| Model_only_own_out_all | CAR[0,+1] | -0.00343 | 0.004776 | 0.472625 | 297.0 | 33.0 | 222.0 | -0.002907 | 0.441077 |
| App_only_own_out_all | AR[0] | -0.002071 | 0.004144 | 0.617226 | 209.0 | 24.0 | 166.0 | -0.002615 | 0.464115 |
| App_only_own_out_all | CAR[0,+1] | -0.007634 | 0.006154 | 0.214835 | 209.0 | 24.0 | 166.0 | -0.006832 | 0.392344 |

## Peer Minus Focal, Same Existing Event Clock

| sample_name | events | peer_minus_focal_mean | se | p | median | positive_share | mean_peer_car | mean_focal_car |
|---|---|---|---|---|---|---|---|---|
| ModelApp_own_out_all | 53.0 | -2.9e-05 | 0.006442 | 0.996463 | 0.000702 | 0.509434 | -0.006399 | -0.00637 |
| ModelApp_own_out_first_firm | 48.0 | 0.000294 | 0.006971 | 0.966348 | 0.00084 | 0.520833 | -0.007042 | -0.007336 |
| ModelApp_clean_title_all | 10.0 | 0.00284 | 0.018052 | 0.874981 | 0.015008 | 0.7 | -0.012899 | -0.015739 |
| ModelApp_clean_title_first_firm | 8.0 | 0.010959 | 0.021586 | 0.611651 | 0.02454 | 0.875 | -0.012789 | -0.023749 |
| ModelApp_realized_plus_all | 9.0 | 0.006466 | 0.009085 | 0.476596 | -0.001716 | 0.444444 | -0.003786 | -0.010253 |
| ModelApp_realized_plus_first_firm | 8.0 | 0.008816 | 0.009951 | 0.375626 | 0.007208 | 0.5 | -0.001207 | -0.010023 |
| Model_only_own_out_all | 30.0 | 0.002116 | 0.009949 | 0.831553 | 0.004747 | 0.533333 | -0.00616 | -0.008276 |
| App_only_own_out_all | 23.0 | -0.002826 | 0.007431 | 0.703715 | -0.010221 | 0.478261 | -0.00671 | -0.003884 |

## CSMAR Listed Supplier Benchmark

| sample_name | edge_family | outcome_label | estimate | se | p | nobs | events | peer_firms | median | positive_share |
|---|---|---|---|---|---|---|---|---|---|---|
| ModelApp_own_out_all | union | AR[0] | -0.003791 | 0.003793 | 0.317557 | 9.0 | 7.0 | 9.0 | -0.007273 | 0.222222 |
| ModelApp_own_out_all | union | CAR[0,+1] | 0.014983 | 0.01896 | 0.429376 | 9.0 | 7.0 | 9.0 | -0.006963 | 0.222222 |
| ModelApp_own_out_first_firm | union | AR[0] | -0.003791 | 0.003793 | 0.317557 | 9.0 | 7.0 | 9.0 | -0.007273 | 0.222222 |
| ModelApp_own_out_first_firm | union | CAR[0,+1] | 0.014983 | 0.01896 | 0.429376 | 9.0 | 7.0 | 9.0 | -0.006963 | 0.222222 |
| ModelApp_clean_title_all | union | AR[0] | -0.011057 | 0.001615 | 0.0 | 2.0 | 1.0 | 2.0 | -0.011057 | 0.0 |
| ModelApp_clean_title_all | union | CAR[0,+1] | -0.01147 | 0.000493 | 0.0 | 2.0 | 1.0 | 2.0 | -0.01147 | 0.0 |
| ModelApp_clean_title_first_firm | union | AR[0] | -0.011057 | 0.001615 | 0.0 | 2.0 | 1.0 | 2.0 | -0.011057 | 0.0 |
| ModelApp_clean_title_first_firm | union | CAR[0,+1] | -0.01147 | 0.000493 | 0.0 | 2.0 | 1.0 | 2.0 | -0.01147 | 0.0 |
| ModelApp_realized_plus_all | union | AR[0] | -0.024169 |  |  | 1.0 | 1.0 | 1.0 | -0.024169 | 0.0 |
| ModelApp_realized_plus_all | union | CAR[0,+1] | -0.037228 |  |  | 1.0 | 1.0 | 1.0 | -0.037228 | 0.0 |
| ModelApp_realized_plus_first_firm | union | AR[0] | -0.024169 |  |  | 1.0 | 1.0 | 1.0 | -0.024169 | 0.0 |
| ModelApp_realized_plus_first_firm | union | CAR[0,+1] | -0.037228 |  |  | 1.0 | 1.0 | 1.0 | -0.037228 | 0.0 |
| Model_only_own_out_all | union | AR[0] | -0.002283 | 0.004512 | 0.61282 | 5.0 | 4.0 | 5.0 | -0.00065 | 0.2 |
| Model_only_own_out_all | union | CAR[0,+1] | 0.001302 | 0.013195 | 0.921414 | 5.0 | 4.0 | 5.0 | -0.010977 | 0.2 |
| App_only_own_out_all | union | AR[0] | -0.005677 | 0.006838 | 0.406429 | 4.0 | 3.0 | 4.0 | -0.007447 | 0.25 |
| App_only_own_out_all | union | CAR[0,+1] | 0.032085 | 0.032955 | 0.33025 | 4.0 | 3.0 | 4.0 | -0.004091 | 0.25 |

## FactSet Supplier/Customer Benchmark

| sample_name | relation_type | outcome_label | mean | se | p | nobs | events | related_firms | median | positive_share | event_weighted_mean | event_weighted_p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ModelApp_own_out_all | factset_downstream_customer | AR[0] | -0.001932 | 0.001554 | 0.213709 | 209.0 | 39.0 | 136.0 | -0.002371 | 0.38756 | -0.003433 | 0.175937 |
| ModelApp_own_out_all | factset_upstream_supplier | AR[0] | 0.000897 | 0.003014 | 0.765909 | 90.0 | 29.0 | 75.0 | -0.000278 | 0.477778 | -0.002437 | 0.445339 |
| ModelApp_own_out_all | factset_downstream_customer | CAR[0,+1] | -0.003602 | 0.002144 | 0.0929 | 209.0 | 39.0 | 136.0 | -0.003904 | 0.37799 | -0.004242 | 0.299354 |
| ModelApp_own_out_all | factset_upstream_supplier | CAR[0,+1] | 0.00124 | 0.004451 | 0.780493 | 90.0 | 29.0 | 75.0 | -0.001928 | 0.466667 | -0.00244 | 0.589154 |
| ModelApp_own_out_first_firm | factset_downstream_customer | AR[0] | -0.003041 | 0.001361 | 0.025433 | 188.0 | 35.0 | 135.0 | -0.003112 | 0.361702 | -0.004027 | 0.147848 |
| ModelApp_own_out_first_firm | factset_upstream_supplier | AR[0] | 0.000263 | 0.003127 | 0.933027 | 83.0 | 27.0 | 75.0 | -0.000309 | 0.46988 | -0.002355 | 0.477487 |
| ModelApp_own_out_first_firm | factset_downstream_customer | CAR[0,+1] | -0.00466 | 0.002181 | 0.032642 | 188.0 | 35.0 | 135.0 | -0.00451 | 0.351064 | -0.004541 | 0.302062 |
| ModelApp_own_out_first_firm | factset_upstream_supplier | CAR[0,+1] | 0.001126 | 0.00477 | 0.813333 | 83.0 | 27.0 | 75.0 | -0.002526 | 0.457831 | -0.001934 | 0.684702 |
| ModelApp_clean_title_all | factset_downstream_customer | AR[0] | -0.000475 | 0.002784 | 0.864445 | 26.0 | 8.0 | 21.0 | -0.000959 | 0.423077 | 0.000344 | 0.905393 |
| ModelApp_clean_title_all | factset_upstream_supplier | AR[0] | -0.010543 | 0.004049 | 0.009224 | 18.0 | 4.0 | 17.0 | -0.013633 | 0.333333 | -0.012581 | 0.219882 |
| ModelApp_clean_title_all | factset_downstream_customer | CAR[0,+1] | 0.003132 | 0.005398 | 0.561722 | 26.0 | 8.0 | 21.0 | -0.002851 | 0.423077 | 0.008339 | 0.253435 |
| ModelApp_clean_title_all | factset_upstream_supplier | CAR[0,+1] | -0.014768 | 0.005673 | 0.009232 | 18.0 | 4.0 | 17.0 | -0.014466 | 0.333333 | -0.020489 | 0.033422 |
| ModelApp_clean_title_first_firm | factset_downstream_customer | AR[0] | -0.000475 | 0.002784 | 0.864445 | 26.0 | 8.0 | 21.0 | -0.000959 | 0.423077 | 0.000344 | 0.905393 |
| ModelApp_clean_title_first_firm | factset_upstream_supplier | AR[0] | -0.010543 | 0.004049 | 0.009224 | 18.0 | 4.0 | 17.0 | -0.013633 | 0.333333 | -0.012581 | 0.219882 |
| ModelApp_clean_title_first_firm | factset_downstream_customer | CAR[0,+1] | 0.003132 | 0.005398 | 0.561722 | 26.0 | 8.0 | 21.0 | -0.002851 | 0.423077 | 0.008339 | 0.253435 |
| ModelApp_clean_title_first_firm | factset_upstream_supplier | CAR[0,+1] | -0.014768 | 0.005673 | 0.009232 | 18.0 | 4.0 | 17.0 | -0.014466 | 0.333333 | -0.020489 | 0.033422 |
| ModelApp_realized_plus_all | factset_downstream_customer | AR[0] | -0.002531 | 0.001095 | 0.020776 | 44.0 | 10.0 | 37.0 | -0.003329 | 0.409091 | -0.001522 | 0.512308 |
| ModelApp_realized_plus_all | factset_upstream_supplier | AR[0] | -0.002404 | 0.005416 | 0.657136 | 38.0 | 7.0 | 37.0 | -0.000856 | 0.447368 | -0.010005 | 0.167301 |
| ModelApp_realized_plus_all | factset_downstream_customer | CAR[0,+1] | -0.001826 | 0.003873 | 0.637299 | 44.0 | 10.0 | 37.0 | -0.003346 | 0.363636 | 0.001213 | 0.890827 |
| ModelApp_realized_plus_all | factset_upstream_supplier | CAR[0,+1] | -0.006248 | 0.005368 | 0.24441 | 38.0 | 7.0 | 37.0 | -0.000575 | 0.473684 | -0.013292 | 0.064133 |
| ModelApp_realized_plus_first_firm | factset_downstream_customer | AR[0] | -0.003338 | 0.000948 | 0.00043 | 40.0 | 9.0 | 34.0 | -0.004519 | 0.375 | -0.002306 | 0.345489 |
| ModelApp_realized_plus_first_firm | factset_upstream_supplier | AR[0] | -0.002404 | 0.005416 | 0.657136 | 38.0 | 7.0 | 37.0 | -0.000856 | 0.447368 | -0.010005 | 0.167301 |
| ModelApp_realized_plus_first_firm | factset_downstream_customer | CAR[0,+1] | -0.003896 | 0.003232 | 0.227993 | 40.0 | 9.0 | 34.0 | -0.006785 | 0.3 | -0.000749 | 0.938014 |
| ModelApp_realized_plus_first_firm | factset_upstream_supplier | CAR[0,+1] | -0.006248 | 0.005368 | 0.24441 | 38.0 | 7.0 | 37.0 | -0.000575 | 0.473684 | -0.013292 | 0.064133 |
| Model_only_own_out_all | factset_downstream_customer | AR[0] | -0.002785 | 0.001634 | 0.088289 | 134.0 | 22.0 | 91.0 | -0.003197 | 0.343284 | -0.000677 | 0.721816 |
| Model_only_own_out_all | factset_upstream_supplier | AR[0] | 0.003948 | 0.004184 | 0.34541 | 58.0 | 19.0 | 48.0 | 0.002066 | 0.551724 | 0.000163 | 0.970734 |
| Model_only_own_out_all | factset_downstream_customer | CAR[0,+1] | -0.004801 | 0.002736 | 0.079258 | 134.0 | 22.0 | 91.0 | -0.005372 | 0.343284 | -0.002617 | 0.571917 |
| Model_only_own_out_all | factset_upstream_supplier | CAR[0,+1] | 0.004226 | 0.005568 | 0.447872 | 58.0 | 19.0 | 48.0 | 0.001166 | 0.551724 | 0.000683 | 0.903906 |
| App_only_own_out_all | factset_downstream_customer | AR[0] | -0.000408 | 0.00273 | 0.881206 | 75.0 | 17.0 | 55.0 | -0.000801 | 0.466667 | -0.006999 | 0.182026 |
| App_only_own_out_all | factset_upstream_supplier | AR[0] | -0.004631 | 0.003254 | 0.154702 | 32.0 | 10.0 | 31.0 | -0.008163 | 0.34375 | -0.007378 | 0.041372 |
| App_only_own_out_all | factset_downstream_customer | CAR[0,+1] | -0.001461 | 0.002976 | 0.623515 | 75.0 | 17.0 | 55.0 | -0.001808 | 0.44 | -0.006346 | 0.388464 |
| App_only_own_out_all | factset_upstream_supplier | CAR[0,+1] | -0.004171 | 0.007788 | 0.59223 | 32.0 | 10.0 | 31.0 | -0.006859 | 0.3125 | -0.008375 | 0.265479 |

## Output Files

- `results/v61_modelapp_layer_event_study_20260612/modelapp_event_samples.csv`
- `results/v61_modelapp_layer_event_study_20260612/modelapp_classification_all_A.csv`
- `results/v61_modelapp_layer_event_study_20260612/modelapp_sample_counts.csv`
- `results/v61_modelapp_layer_event_study_20260612/modelapp_category_counts.csv`
- `results/v61_modelapp_layer_event_study_20260612/focal_returns_strict_next_day_summary.csv`
- `results/v61_modelapp_layer_event_study_20260612/peer_returns_summary.csv`
- `results/v61_modelapp_layer_event_study_20260612/csmar_supplier_summary.csv`
- `results/v61_modelapp_layer_event_study_20260612/factset_relation_summary.csv`
- `results/v61_modelapp_layer_event_study_20260612/peer_minus_focal_summary.csv`
- `results/v61_modelapp_layer_event_study_20260612/v61_modelapp_layer_event_study_20260612.xlsx`
