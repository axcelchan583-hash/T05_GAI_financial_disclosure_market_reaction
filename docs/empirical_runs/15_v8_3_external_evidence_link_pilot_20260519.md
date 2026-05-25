# v8.3 外部证据连接试跑

日期：2026-05-19

## 1. 目的

这次不是正式回归，而是检查当前数据能否支持一个更硬的测度闭环：

```text
2024 年报 GenAI 前瞻性声明
    -> 年报披露日前是否已有公开支撑
    -> 年报披露日后是否出现 IR / 互动问答 / 下一年年报证据
```

这里的外部公开证据来自两类渠道：

- 巨潮投资者关系活动记录表。
- 上证 e 互动与深交所互动易的公司回复。

## 2. 当前变量口径

```text
HasPriorPublicIRQAEvidence
    = 同一股票代码在 2024 年报披露日前，已有 GenAI 相关 IR 或互动问答公司回复。

NoPriorPublicEvidence_Strict
    = NoCurrentAISupport_2024 = 1 且 HasPriorPublicIRQAEvidence = 0。

FuturePublicIRQAEvidence
    = 同一股票代码在 2024 年报披露日后，出现 GenAI 相关 IR 或互动问答公司回复。

FutureAnyPublicEvidence_Extended
    = FutureTypeMatchedTextEvidence_2025 = 1 或 FuturePublicIRQAEvidence = 1。
```

注意：`NoCurrentAISupport_2024` 仍来自现有 AI 投资支撑表；IR/互动问答只是在“公开可核验支撑”上补一层。

## 3. 样本概况

- 年报 GenAI 前瞻性声明句子：7469
- 涉及公司：1321
- 有高具体性声明的公司：434
- 严格无先验公开支撑且有高具体性声明的公司：25
- 严格无先验公开支撑且高具体性声明句子：44
- 这些核心公司中，后续出现任一公开证据的比例：72.00%
- 这些核心公司中，后续出现 IR/互动问答证据的比例：20.00%

## 4. 句子层 2x2

| HighSpecificity | NoPriorPublicEvidence_Strict | n_sentences | n_firms | future_type_matched_ar_rate | future_irqa_rate | future_any_public_rate | mean_prior_irqa_events | mean_future_irqa_events | mean_specificity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| False | False | 6200 | 1201 | 0.7595 | 0.3732 | 0.8082 | 0.1040 | 1.6805 | 1.3981 |
| False | True | 269 | 67 | 0.6914 | 0.2305 | 0.7138 | 0.0000 | 0.3346 | 1.3866 |
| True | False | 956 | 409 | 0.7824 | 0.3839 | 0.8295 | 0.0732 | 1.5126 | 3.1328 |
| True | True | 44 | 25 | 0.7955 | 0.2500 | 0.8182 | 0.0000 | 0.4091 | 3.1364 |

## 5. 公司层 2x2

| HasHighSpecificityClaim | NoPriorPublicEvidence_Strict | n_firms | mean_claim_sentences | future_type_matched_ar_rate | future_irqa_rate | future_any_public_rate | mean_prior_irqa_events | mean_future_irqa_events |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| False | False | 839 | 2.6865 | 0.4338 | 0.1633 | 0.4923 | 0.0572 | 0.4303 |
| False | True | 48 | 2.0833 | 0.4375 | 0.1042 | 0.4583 | 0.0000 | 0.2083 |
| True | False | 409 | 11.9853 | 0.7775 | 0.2934 | 0.7995 | 0.0636 | 1.0758 |
| True | True | 25 | 8.5200 | 0.6800 | 0.2000 | 0.7200 | 0.0000 | 0.2400 |

## 6. 极简 LPM

只用于看方向，不含行业、规模、公司基本面、固定效应，不作为正式结果。

| model | term | coef | std_err | p_value | nobs | r2 | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Y_any_public_evidence | Intercept | 0.4923 | 0.0163 | 0.0000 | 1321 | 0.0852 | numpy OLS, classical SE, no controls |
| Y_any_public_evidence | HasHighSpecificityClaim | 0.3073 | 0.0284 | 0.0000 | 1321 | 0.0852 | numpy OLS, classical SE, no controls |
| Y_any_public_evidence | NoPriorPublicEvidence_Strict | -0.0339 | 0.0699 | 0.6275 | 1321 | 0.0852 | numpy OLS, classical SE, no controls |
| Y_any_public_evidence | Interaction | -0.0456 | 0.1196 | 0.7031 | 1321 | 0.0852 | numpy OLS, classical SE, no controls |
| Y_future_irqa | Intercept | 0.1633 | 0.0137 | 0.0000 | 1321 | 0.0241 | numpy OLS, classical SE, no controls |
| Y_future_irqa | HasHighSpecificityClaim | 0.1301 | 0.0240 | 0.0000 | 1321 | 0.0241 | numpy OLS, classical SE, no controls |
| Y_future_irqa | NoPriorPublicEvidence_Strict | -0.0591 | 0.0590 | 0.3160 | 1321 | 0.0241 | numpy OLS, classical SE, no controls |
| Y_future_irqa | Interaction | -0.0343 | 0.1009 | 0.7340 | 1321 | 0.0241 | numpy OLS, classical SE, no controls |
| Y_2025_ar_type_matched | Intercept | 0.4338 | 0.0163 | 0.0000 | 1321 | 0.1022 | numpy OLS, classical SE, no controls |
| Y_2025_ar_type_matched | HasHighSpecificityClaim | 0.3437 | 0.0285 | 0.0000 | 1321 | 0.1022 | numpy OLS, classical SE, no controls |
| Y_2025_ar_type_matched | NoPriorPublicEvidence_Strict | 0.0037 | 0.0701 | 0.9585 | 1321 | 0.1022 | numpy OLS, classical SE, no controls |
| Y_2025_ar_type_matched | Interaction | -0.1012 | 0.1200 | 0.3992 | 1321 | 0.1022 | numpy OLS, classical SE, no controls |

## 7. 核心格后续公开证据示例

样例文件：

`results/v8_3_external_evidence_link_pilot/core_cell_future_public_evidence_examples.csv`

前 10 条：

| Symbol | ShortName_from_filename | report_disclosure_date | event_date | event_source | matched_terms | event_text | source_url |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 000815 | 美利云 | 2025-03-14 00:00:00 | 2026-03-03 | interactive_qa_answer | AI大模型;大模型 | 董秘您好！请问公司规划的2000台AI服务器目前推进至哪一阶段？是否完成供应商遴选、机房改造等前期工作，预计何时形成标准化AI算力租赁能力？传统IDC以长期定制化租赁为主，未来是否计划针对AI创业公司、大模型团队推出短期弹性算力产品？B3/C3高密机柜预计2026年Q3/Q4投产，当前建设进度是否符合预期？投产后可承载的AI算力规模具体多少，是否已对接潜在客户？ 尊敬的投资者您好！公司主要从事数据中心机柜租赁业务，当前AI领域对灵活、按需算力的需求日益增长，契合公司未来的战略方向。但目前尚处于调研研究阶段，公司暂无具体的项目、产品、服务及相关推出计划等。与公司有关的信息，敬请以公司指定的信息披露媒体公告为准。感谢您对公司的关注！ | https://irm.cninfo.com.cn/ircs/question/questionDetail?questionId=2195758582791340032 |
| 002659 | 凯文教育 | 2025-04-25 00:00:00 | 2026-03-05 | interactive_qa_answer | 智谱 | 2月27日AI智谱北京智谱华章科技有限公司注册资本增资到4458.4万元对公司有什么影响？ 尊敬的投资者您好，您提到的问题属于其自身发展规划范畴，相关信息请以智谱华章官方披露内容为准。谢谢您的关注。 | https://irm.cninfo.com.cn/ircs/question/questionDetail?questionId=2212143702279172096 |
| 300033 | 同花顺 | 2025-02-25 00:00:00 | 2026-03-30 | interactive_qa_answer | 大模型 | 人工智能飞速发展，公司在这方面有何布局？ 尊敬的投资者，您好！在人工智能技术加速发展的背景下，公司持续推进“大模型+金融”应用落地，已在智能投顾、智能客服、智能投研、代码生成、法律咨询、办公助手、翻译等场景推出相关产品，推动金融服务效率与智能化水平提升。感谢您对公司的关注，谢谢！ | https://irm.cninfo.com.cn/ircs/question/questionDetail?questionId=2219528728625000448 |
| 300033 | 同花顺 | 2025-02-25 00:00:00 | 2026-03-30 | interactive_qa_answer | 大模型 | 翻阅贵公司2025年财报，显示贵公司依托“问财”大模型能力，公司同步推出数据可视化智能体，并荣获 2025 年中国设计智造奖。查阅中国设计智造大奖网站，没有看到贵公司获得奖项的图片，请问此消息是否真实，谢谢 尊敬的投资者，您好！ 公司“数据可视化智能体”（Mentora）已荣获2025年中国设计智造大奖优秀奖，相关信息可在官方网站查证，具体链接如下： https://www.di-award.org/collections/detail/2961.html?page_size=1000&page=1&year=2025&award_type=a5&award_group=1&category_id=304 页面中已展示获奖作品及公司信息。如您浏览时未找到，可尝试刷新页面或调整筛选条件（年份2025、奖项类型等）。 感谢您的核实与关注，谢谢！ | https://irm.cninfo.com.cn/ircs/question/questionDetail?questionId=2221781352938369024 |
| 688158 | 优刻得 | 2025-04-19 00:00:00 | 2026-05-06 | interactive_qa_answer | AI大模型;DeepSeek;大模型 | :优刻得(688158)董秘你好，4月18号媒体报道DeepSeek计划以估值100亿美金的估值开展第一轮3亿美金左右的融资，并在乌兰察布大规模招聘数据中心运维岗工程师。贵司作为去年国内首批适配DeepSeek的中立云服务商，并已经完成乌兰察布一期和二期算力数据中心的建设，今年3月计划定增18亿元建设乌兰察布三期数据中心，与DeepSeek英雄所见略同。请问贵司今后是否有计划向DeepSeek在乌兰察布开展算力租赁等服务？望回复，感谢！ 尊敬的投资者，您好！公司是国内领先的中立第三方云计算服务商，已完成DeepSeek全系列 模型 适配工作，并依托两 大 自建智算中心，为各类 AI 客户提供安全可靠、专业高效的算力支持。关于公司与 DeepSeek 的后续具体合作情况，请以公开信息为准，公司也将积极把握行业机遇，持续关注优质合作契机。感谢您的关注！ | https://sns.sseinfo.com/ajax/feeds.do?item=1706346 |
| 833030 | 立方控股 | 2025-04-28 00:00:00 | 2025-06-04 | cninfo_ir_activity | 大模型 | 投资者关系活动记录表 | https://static.cninfo.com.cn/finalpage/2025-06-05/1223788170.PDF |

## 8. 初步判断

可以继续跑，但目前适合定位为“测度闭环与样本量试验”，还不能直接当正式实证。

更稳的下一步是：

1. 对 `NoPriorPublicEvidence_Strict` 核心格抽样人工复核，确认年报句子是不是具体 GenAI 能力声明。
2. 对 `FuturePublicIRQAEvidence` 句子做类型匹配，不要只按同公司同关键词算兑现。
3. 将专利、招聘、CAC 的公司映射补上后，再把 outcome 从“文本证据”升级为更硬的行动证据。
