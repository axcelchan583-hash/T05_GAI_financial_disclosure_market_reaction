# v39 Broad Collaborator Text Probe

Date: 2026-06-07

## Scope

This run expands v38 beyond supply-chain links. It uses machine text matching to extract listed broad collaborators from:

- event announcement text around the v36 first-event sample;
- available pre-event CNINFO texts in the local corpus;
- existing supplier/customer links from CSMAR supply-chain tables.

This is a screening run. Text-matched partner rows require manual validation before they can be used as final paper evidence.

## Source Coverage

| layer | linked_rows | events | focal_firms | related_firms |
|---|---|---|---|---|
| event_named_listed_partner_raw | 181.0 | 86.0 | 86.0 | 139.0 |
| historical_text_listed_partner_raw | 9.0 | 3.0 | 3.0 | 9.0 |
| supply_chain_existing_raw | 176.0 | 74.0 | 74.0 | 154.0 |
| broad_collaborator_union_raw | 364.0 | 144.0 | 144.0 | 285.0 |

## Sample Flow

| layer | linked_rows | events | focal_firms | related_firms | clean_car0p1_rows | clean_car0p1_events |
|---|---|---|---|---|---|---|
| v36_first_events | 363.0 | 363.0 | 363.0 |  |  |  |
| competitor_returns | 3151.0 | 319.0 | 319.0 | 1546.0 | 2790.0 | 316.0 |
| event_named_listed_partner_returns | 181.0 | 86.0 | 86.0 | 139.0 | 159.0 | 74.0 |
| historical_text_listed_partner_returns | 9.0 | 3.0 | 3.0 | 9.0 | 8.0 | 3.0 |
| supply_chain_existing_returns | 176.0 | 74.0 | 74.0 | 154.0 | 142.0 | 70.0 |
| broad_collaborator_union_returns | 364.0 | 144.0 | 144.0 | 285.0 | 307.0 | 130.0 |

## CAR[0,+1] by Relation Type

| relation_type | mean | se | p | nobs | events | related_firms | positive_share | event_weighted_mean | event_weighted_p | event_weighted_events |
|---|---|---|---|---|---|---|---|---|---|---|
| broad_collaborator_union | -0.00021 | 0.002852 | 0.941436 | 307.0 | 130.0 | 236.0 | 0.495114 | -0.001487 | 0.576882 | 130.0 |
| competitor | -0.004641 | 0.001634 | 0.004501 | 2790.0 | 316.0 | 1385.0 | 0.434409 | -0.005051 | 0.002267 | 316.0 |
| event_named_listed_partner | 0.003649 | 0.00395 | 0.3556 | 159.0 | 74.0 | 123.0 | 0.54717 | -0.002837 | 0.341016 | 74.0 |
| historical_text_listed_partner | -0.008998 | 0.004125 | 0.029152 | 8.0 | 3.0 | 8.0 | 0.625 | -0.008702 | 0.22908 | 3.0 |
| placebo_low_similarity | -0.002536 | 0.001555 | 0.102965 | 1359.0 | 322.0 | 953.0 | 0.43635 | -0.002707 | 0.079521 | 322.0 |
| supply_chain_existing | -0.004048 | 0.003826 | 0.290006 | 142.0 | 70.0 | 122.0 | 0.429577 | -0.00049 | 0.90636 | 70.0 |

## Stacked Event-FE Regressions

Baseline group is product-market competitors. Competitor event-firm rows overlapping with broad collaborators are removed.

| sample | outcome | regressor | coef_event_fmt | p_event_cluster | coef_two_way_fmt | p_two_way | nobs | events | related_firms | r2 |
|---|---|---|---|---|---|---|---|---|---|---|
| broad_union_vs_competitor | peer_ar_m1_mm | cooperative | 0.0004 | 0.870094 | 0.0004 | 0.868713 | 1174.0 | 108.0 | 802.0 | 0.314744 |
| source_flags_vs_competitor | peer_ar_m1_mm | is_event_named_listed_partner | -0.0035 | 0.267648 | -0.0035 | 0.26151 | 1191.0 | 113.0 | 814.0 | 0.32653 |
| source_flags_vs_competitor | peer_ar_m1_mm | is_historical_text_listed_partner | -0.0058 | 0.612504 | -0.0058 | 0.612628 | 1191.0 | 113.0 | 814.0 | 0.32653 |
| source_flags_vs_competitor | peer_ar_m1_mm | is_supply_chain_existing | 0.0045 | 0.14614 | 0.0045 | 0.139209 | 1191.0 | 113.0 | 814.0 | 0.32653 |
| event_named_listed_partner_vs_competitor | peer_ar_m1_mm | cooperative | -0.0031 | 0.341946 | -0.0031 | 0.335775 | 610.0 | 58.0 | 470.0 | 0.277284 |
| supply_chain_existing_vs_competitor | peer_ar_m1_mm | cooperative | 0.0039 | 0.222959 | 0.0039 | 0.215163 | 638.0 | 59.0 | 494.0 | 0.366604 |
| historical_text_listed_partner_vs_competitor | peer_ar_m1_mm | cooperative | -0.0061 | 0.669452 | -0.0061 | 0.669452 | 36.0 | 3.0 | 36.0 | 0.027137 |
| broad_union_vs_competitor | peer_ar0_mm | cooperative | 0.0014 | 0.469731 | 0.0014 | 0.474971 | 1174.0 | 108.0 | 802.0 | 0.330957 |
| source_flags_vs_competitor | peer_ar0_mm | is_event_named_listed_partner | -0.0010 | 0.699496 | -0.0010 | 0.699045 | 1191.0 | 113.0 | 814.0 | 0.33148 |
| source_flags_vs_competitor | peer_ar0_mm | is_historical_text_listed_partner | -0.0038 | 0.706023 | -0.0038 | 0.70603 | 1191.0 | 113.0 | 814.0 | 0.33148 |
| source_flags_vs_competitor | peer_ar0_mm | is_supply_chain_existing | 0.0037 | 0.153876 | 0.0037 | 0.162107 | 1191.0 | 113.0 | 814.0 | 0.33148 |
| event_named_listed_partner_vs_competitor | peer_ar0_mm | cooperative | -0.0012 | 0.670932 | -0.0012 | 0.670957 | 610.0 | 58.0 | 470.0 | 0.279558 |
| supply_chain_existing_vs_competitor | peer_ar0_mm | cooperative | 0.0040 | 0.143202 | 0.0040 | 0.150036 | 638.0 | 59.0 | 494.0 | 0.366767 |
| historical_text_listed_partner_vs_competitor | peer_ar0_mm | cooperative | -0.0042 | 0.743759 | -0.0042 | 0.743759 | 36.0 | 3.0 | 36.0 | 0.020099 |
| broad_union_vs_competitor | peer_ar_p1_mm | cooperative | -0.0016 | 0.482592 | -0.0016 | 0.472155 | 1174.0 | 108.0 | 802.0 | 0.330563 |
| source_flags_vs_competitor | peer_ar_p1_mm | is_event_named_listed_partner | -0.0018 | 0.553084 | -0.0018 | 0.549159 | 1191.0 | 113.0 | 814.0 | 0.329565 |
| source_flags_vs_competitor | peer_ar_p1_mm | is_historical_text_listed_partner | 0.0077 | 0.227055 | 0.0077 | 0.227189 | 1191.0 | 113.0 | 814.0 | 0.329565 |
| source_flags_vs_competitor | peer_ar_p1_mm | is_supply_chain_existing | -0.0015 | 0.675629 | -0.0015 | 0.671065 | 1191.0 | 113.0 | 814.0 | 0.329565 |
| event_named_listed_partner_vs_competitor | peer_ar_p1_mm | cooperative | -0.0015 | 0.633559 | -0.0015 | 0.630995 | 610.0 | 58.0 | 470.0 | 0.276279 |
| supply_chain_existing_vs_competitor | peer_ar_p1_mm | cooperative | -0.0016 | 0.653749 | -0.0016 | 0.648708 | 638.0 | 59.0 | 494.0 | 0.375299 |
| historical_text_listed_partner_vs_competitor | peer_ar_p1_mm | cooperative | 0.0082 | 0.271903 | 0.0082 | 0.271903 | 36.0 | 3.0 | 36.0 | 0.158257 |
| broad_union_vs_competitor | peer_car_0_p1_mm | cooperative | -0.0002 | 0.952271 | -0.0002 | 0.952457 | 1174.0 | 108.0 | 802.0 | 0.362263 |
| source_flags_vs_competitor | peer_car_0_p1_mm | is_event_named_listed_partner | -0.0028 | 0.450808 | -0.0028 | 0.458832 | 1191.0 | 113.0 | 814.0 | 0.362419 |
| source_flags_vs_competitor | peer_car_0_p1_mm | is_historical_text_listed_partner | 0.0039 | 0.783424 | 0.0039 | 0.783411 | 1191.0 | 113.0 | 814.0 | 0.362419 |
| source_flags_vs_competitor | peer_car_0_p1_mm | is_supply_chain_existing | 0.0022 | 0.643959 | 0.0022 | 0.645407 | 1191.0 | 113.0 | 814.0 | 0.362419 |
| event_named_listed_partner_vs_competitor | peer_car_0_p1_mm | cooperative | -0.0026 | 0.498994 | -0.0026 | 0.506281 | 610.0 | 58.0 | 470.0 | 0.305462 |
| supply_chain_existing_vs_competitor | peer_car_0_p1_mm | cooperative | 0.0024 | 0.639577 | 0.0024 | 0.640335 | 638.0 | 59.0 | 494.0 | 0.395816 |
| historical_text_listed_partner_vs_competitor | peer_car_0_p1_mm | cooperative | 0.0041 | 0.812627 | 0.0041 | 0.812627 | 36.0 | 3.0 | 36.0 | 0.117947 |
| broad_union_vs_competitor | peer_car_m1_p1_mm | cooperative | 0.0002 | 0.964878 | 0.0002 | 0.964812 | 1174.0 | 108.0 | 802.0 | 0.340629 |
| source_flags_vs_competitor | peer_car_m1_p1_mm | is_event_named_listed_partner | -0.0063 | 0.195406 | -0.0063 | 0.197545 | 1191.0 | 113.0 | 814.0 | 0.34621 |
| source_flags_vs_competitor | peer_car_m1_p1_mm | is_historical_text_listed_partner | -0.0019 | 0.941601 | -0.0019 | 0.941604 | 1191.0 | 113.0 | 814.0 | 0.34621 |
| source_flags_vs_competitor | peer_car_m1_p1_mm | is_supply_chain_existing | 0.0067 | 0.292279 | 0.0067 | 0.290712 | 1191.0 | 113.0 | 814.0 | 0.34621 |
| event_named_listed_partner_vs_competitor | peer_car_m1_p1_mm | cooperative | -0.0057 | 0.259341 | -0.0057 | 0.262766 | 610.0 | 58.0 | 470.0 | 0.313543 |
| supply_chain_existing_vs_competitor | peer_car_m1_p1_mm | cooperative | 0.0062 | 0.345965 | 0.0062 | 0.343938 | 638.0 | 59.0 | 494.0 | 0.389628 |
| historical_text_listed_partner_vs_competitor | peer_car_m1_p1_mm | cooperative | -0.0020 | 0.94886 | -0.0020 | 0.94886 | 36.0 | 3.0 | 36.0 | 0.063634 |

## Match Examples

| event_date | focal_code | focal_name | related_code | related_name | relation_type | matched_alias | announcement_title | match_evidence |
|---|---|---|---|---|---|---|---|---|
| 2024-05-16 00:00:00 | 688367 | 工大高科 | 002230 | 科大讯飞 | event_named_listed_partner | 科大讯飞 | 工大高科：工大高科关于自愿披露与科大讯飞股份有限公司签订战略合作框架协议的公告 | 工大高科：工大高科关于自愿披露与科大讯飞股份有限公司签订战略合作框架协议的公告 与科大讯飞签订战略合作框架协议，明确在星火认知大模型、工业视觉大模型等方向合作，属于具体GenAI行动。 双方将在智能语音交互、工业六感、星 |
| 2025-11-14 00:00:00 | 000917 | 电广传媒 | 000430 | 张家界 | event_named_listed_partner | 张家界 | 电广传媒：关于公司参与张家界旅游集团股份有限公司重整投资暨关联交易的公告 | 电广传媒：关于公司参与张家界旅游集团股份有限公司重整投资暨关联交易的公告 公告明确提及联合芒果超媒利用大模型、AIGC等技术积累对旅游项目赋能改造 乙方将联合芒果超媒…在内容创意、大模型、AIGC、元宇宙等领 |
| 2025-11-14 00:00:00 | 300413 | 芒果超媒 | 000430 | 张家界 | event_named_listed_partner | 张家界 | 芒果超媒：关于公司参与张家界旅游集团股份有限公司重整投资暨关联交易的公告 | 芒果超媒：关于公司参与张家界旅游集团股份有限公司重整投资暨关联交易的公告 公告称将利用大模型、AIGC等技术积累对旅游项目深度赋能，属于具体行动。 在内容创意、大模型、AIGC等领域的技术积累，对甲方优质旅游 |
| 2023-02-08 00:00:00 | 002229 | 鸿博股份 | 300612 | 宣亚国际 | event_named_listed_partner | 宣亚国际 | 鸿博股份：关于股价异动的公告 | 鸿博股份：关于股价异动的公告 公告明确披露子公司与合作伙伴推进AIGC商业应用开发，具体行动。 将与战略合作伙伴宣亚国际等就AIGC相关延展技术的商业应用开发进行落地推进 证券代码：002229     证券简称：鸿博股份        公告编号：2023-003                   |
| 2023-04-26 00:00:00 | 300264 | 佳创视讯 | 600050 | 中国联通 | event_named_listed_partner | 中国联通 | 佳创视讯：关于未弥补亏损达到实收股本总额三分之一的公告 | ，满足市场需求，在未来 获得新兴业务市场增长红利；同时，公司向特定对象发行股票的募集资金已到位，将由电信运 营商事业部、VR业务产品线重点推进与电信运营商的业务运营合作，加速完成与中国联通、中 国电信方战略框架合作协议以及元宇宙联合实验室合作范围内5G视频应用、视频云平台、CDN 分发、VR等具体项目工程及募投项目的落地工作，进一步推动公司产业升级转型战略目标达成， |
| 2023-07-23 00:00:00 | 300657 | 弘信电子 | 688795 | 摩尔线程 | event_named_listed_partner | 摩尔线程 | 弘信电子：关于拟对外投资的公告 | 能遇到芯片供应紧张的风险。继 2022 年年 10 月美国政府对出 口中国的人工智能（AI）芯片施加限制后，美国政府正考虑进一步扩大相关出口 管制。公司虽然与上海燧原科技有限公司、摩尔线程智能科技（北京）有限责任 公司已成为战略合作伙伴关系，但也可能受此影响芯片的供应；   （4）本次投资是基于公司战略发展的需要及对行业市场前景的判断，但宏 观环境、行业政策、市场 |
| 2023-08-18 00:00:00 | 002698 | 博实股份 | 000932 | 华菱钢铁 | event_named_listed_partner | 华菱钢铁 | 博实股份：关于与哈工大签订战略合作框架协议暨关联交易的公告 | 云 创”）签订《关于共同推进制造业数字化转型战略合作框架协议》，详见《关于签 订战略合作框架协议的公告》（公告编号：2020-051）。华联云创为湖南钢铁集团 有限公司（原名“湖南华菱钢铁集团有限责任公司”）的子公司，自该协议签订以 来，双方发挥各自资源与优势，展开技术对接和商业合作。截至本公告披露日，公 司及子公司累计与湖南钢铁集团有限公司下属公司签订产品销售合同 |
| 2023-08-25 00:00:00 | 300825 | 阿尔特 | 300750 | 宁德时代 | event_named_listed_partner | 宁德时代 | 阿尔特：关于签署《阿尔特AI创新赋能中心三方合作协议》的公告 |  2022年3月28日       利运营管理有限责任公司关于天津博郡汽                     协议终止        车有限公司之合作协议书》        《宁德时代新能源科技股份有限公司与深        圳壁虎新能源汽车科技有限公司、阿尔特  2                             2022年11月21日   正常履行中 |
| 2023-10-12 00:00:00 | 002607 | 中公教育 | 300688 | 创业黑马 | event_named_listed_partner | 创业黑马 | 中公教育：关于签署战略合作框架协议的公告 | 中公教育：关于签署战略合作框架协议的公告 公司与创业黑马签署战略合作框架协议，共同成立合资公司推进大模型、AIGC等合作，且公司已成立人工智能与教育研究院探索生成式大语言模型应用。 公司成立人工智能与教育研究院，逐步探索垂直领域内数字人 |
| 2024-01-26 00:00:00 | 000818 | 航锦科技 | 600036 | 招商银行 | event_named_listed_partner | 招商银行 | 航锦科技：关于子公司与紫光晓通签订战略合作框架协议的公告 | 年签署的框架协议及执行情况。2023 年 5 月 6 日，公司与招 商银行公司就长期合作关系签署了《战略合作协议》，详细信息请参见公司于 2023 年 5 月 9 日披露的《关于与招商银行签订战略合作协议的公告》（公告编号： 2023-027）。截至本公告日，该协议未履行完毕。   2、本协议签署前三个月内公司控股股东、持股 5%以上股东、董监高持股变 动情况。20 |
| 2024-11-12 00:00:00 | 300469 | 信息发展 | 601628 | 中国人寿 | event_named_listed_partner | 中国人寿 | 信息发展：关于签署战略合作协议的公告 |  2024年9月18日，公司披露了《关于签署产融服务战略合作框架协议暨关联 交易的公告》（公告编号：2024-069），公司与江苏省创新创业研究会江苏国有 企业科技创新工作委员会、中国人寿财产保险股份有限公司江苏省分公司、中国 物流与采购联合会物流与供应链金融分会、苏交控商业保理（广州）有限公司、 浙商银行股份有限公司南京分行、交信（上海）私募基金管理有限公司（原名 |
| 2024-11-12 00:00:00 | 300469 | 信息发展 | 601916 | 浙商银行 | event_named_listed_partner | 浙商银行 | 信息发展：关于签署战略合作协议的公告 | 公司与江苏省创新创业研究会江苏国有 企业科技创新工作委员会、中国人寿财产保险股份有限公司江苏省分公司、中国 物流与采购联合会物流与供应链金融分会、苏交控商业保理（广州）有限公司、 浙商银行股份有限公司南京分行、交信（上海）私募基金管理有限公司（原名： 交通运输通信信息集团上海股权投资基金管理有限公司）于2024年9月13日签署 了《产融服务战略合作框架协议》，目前该 |
| 2025-03-31 00:00:00 | 688777 | 中控技术 | 603606 | 东方电缆 | event_named_listed_partner | 东方电缆 | 中控技术：中控技术股份有限公司2025年度“提质增效重回报”行动方案 | 域供应链生 态、高校科研院所生态诚邀全球伙伴共创未来，构建“数字化产业生态联盟”。 报告期内，公司的生态合作不断拓展和深化，在与全球合作伙伴增进合作关系的 同时，与用友、中国五环、东方电缆、印尼国家天然气公司、中国天辰、浙资运 营、迦智科技等国内外众多头部企业新签战略合作协议，与大华成立“视觉 AI 联合实验室”推进技术与业务共研，与培慕科技、达美盛等合作伙伴首次达 |
| 2025-04-03 00:00:00 | 600179 | 安通控股 | 000905 | 厦门港务 | event_named_listed_partner | 厦门港务 | 安通控股：2024年年度股东大会会议资料 | 履行独立董事职责。   ②调研走访与沟通交流   本人于 2024 年 6 月中旬，前往公司东南片区刘五店网点进行现场走访调 研，深入了解网点业务开展情况及员工工作状态，并实地拜访厦门港务控股集 团，围绕深化战略合作与业务协同开展了座谈，就当前内贸航运市场最新动态、 未来发展趋势以及潜在的合作契机展开探讨。   ③重大事项参与   11 月下旬及 12 月上旬，本人 |
| 2025-10-17 00:00:00 | 300474 | 景嘉微 | 003029 | 吉大正元 | event_named_listed_partner | 吉大正元 | 景嘉微：关于公司签署战略合作协议的公告（一） | 景嘉微：关于公司签署战略合作协议的公告（一） 公告为签署战略合作协议，合作方吉大正元主营涉及大模型应用，但公告片段未明确合作内容包含GenAI，需人工核验。 吉大正元以密码技术为核心，融合大模型应用、算力、存力等内外部能力 证券代码：300474   证券简称：景 |
| 2026-03-31 00:00:00 | 688070 | 纵横股份 | 600941 | 中国移动 | event_named_listed_partner | 中国移动 | 纵横股份：成都纵横自动化技术股份有限公司2026年度“提质增效重回报”行动方案 | 机产品的国 内外项目进度，尽早完成交付，并持续开展相关资质申办，保障该业务的快速增 长。   3、加强产业生态建设，构建低空经济合作共同体。秉持开放共赢理念，持 续深化与中国电信、中国移动、中国铁塔等运营商的战略合作，发挥各自在网络 覆盖、数据服务、场景落地等方面的互补优势，共同拓展低空经济应用市场。   加强与央国企、地方平台公司及行业龙头企业的协同联动，在技术融 |
| 2026-03-31 00:00:00 | 688070 | 纵横股份 | 601728 | 中国电信 | event_named_listed_partner | 中国电信 | 纵横股份：成都纵横自动化技术股份有限公司2026年度“提质增效重回报”行动方案 | 固定翼无人机产品的国 内外项目进度，尽早完成交付，并持续开展相关资质申办，保障该业务的快速增 长。   3、加强产业生态建设，构建低空经济合作共同体。秉持开放共赢理念，持 续深化与中国电信、中国移动、中国铁塔等运营商的战略合作，发挥各自在网络 覆盖、数据服务、场景落地等方面的互补优势，共同拓展低空经济应用市场。   加强与央国企、地方平台公司及行业龙头企业的协同联动 |
| 2026-04-03 00:00:00 | 300261 | 雅本化学 | 600276 | 恒瑞医药 | event_named_listed_partner | 恒瑞医药 | 雅本化学：雅本化学股份有限公司2026年度向特定对象发行A股股票预案 | 外标准化生产基地、全流 程质量管控体系以及全链条研发能力建设，持续拓展并深化与国内外优质医药企 业的战略合作，赢得合作客户的广泛认可与高度信赖。此外，公司成功与国内创 新药头部企业恒瑞医药建立合作并持续深化，双方合作从早期小规模阶段起步， 并于 2025 年 8 月签署《供应战略协议》，合作范围覆盖肿瘤、代谢、心血管、 免疫、呼吸系统及神经科学等多个重大疾病领域。公 |
| 2023-03-30 00:00:00 | 688327 | 云从科技 | 000673 |  | supply_chain_existing |  | 云从科技：第二届董事会第五次会议决议公告 | network_customer_lists_supplier;topfive_purchase_customer_lists_supplier |
| 2023-03-30 00:00:00 | 688327 | 云从科技 | 002544 |  | supply_chain_existing |  | 云从科技：第二届董事会第五次会议决议公告 | network_supplier_lists_customer;topfive_sale_supplier_lists_customer |
| 2023-03-30 00:00:00 | 688327 | 云从科技 | 300188 |  | supply_chain_existing |  | 云从科技：第二届董事会第五次会议决议公告 | network_customer_lists_supplier;topfive_purchase_customer_lists_supplier |
| 2023-04-24 00:00:00 | 300081 | 恒信东方 | 000728 |  | supply_chain_existing |  | 恒信东方：人工智能算力中心平台建设及运营项目可行性研究报告 | network_supplier_lists_customer |
| 2023-04-24 00:00:00 | 300081 | 恒信东方 | 000788 |  | supply_chain_existing |  | 恒信东方：人工智能算力中心平台建设及运营项目可行性研究报告 | network_supplier_lists_customer;topfive_sale_supplier_lists_customer |
| 2023-04-24 00:00:00 | 300081 | 恒信东方 | 002635 |  | supply_chain_existing |  | 恒信东方：人工智能算力中心平台建设及运营项目可行性研究报告 | network_supplier_lists_customer |
| 2023-04-24 00:00:00 | 300081 | 恒信东方 | 002931 |  | supply_chain_existing |  | 恒信东方：人工智能算力中心平台建设及运营项目可行性研究报告 | network_supplier_lists_customer |
| 2023-04-24 00:00:00 | 300081 | 恒信东方 | 300366 |  | supply_chain_existing |  | 恒信东方：人工智能算力中心平台建设及运营项目可行性研究报告 | network_supplier_lists_customer;topfive_sale_supplier_lists_customer |
| 2023-04-24 00:00:00 | 300081 | 恒信东方 | 601728 |  | supply_chain_existing |  | 恒信东方：人工智能算力中心平台建设及运营项目可行性研究报告 | network_supplier_lists_customer |
| 2023-04-26 00:00:00 | 002065 | 东华软件 | 002261 |  | supply_chain_existing |  | 东华软件：关于与腾讯云计算（北京）有限责任公司签署深化战略合作协议的公告 | network_supplier_lists_customer;topfive_sale_supplier_lists_customer |
| 2023-04-26 00:00:00 | 002065 | 东华软件 | 300231 |  | supply_chain_existing |  | 东华软件：关于与腾讯云计算（北京）有限责任公司签署深化战略合作协议的公告 | network_customer_lists_supplier;topfive_purchase_customer_lists_supplier |
| 2023-04-26 00:00:00 | 300264 | 佳创视讯 | 002368 |  | supply_chain_existing |  | 佳创视讯：关于未弥补亏损达到实收股本总额三分之一的公告 | network_supplier_lists_customer;topfive_sale_supplier_lists_customer |

## Output Files

- `results/v39_broad_collaborator_text_probe_20260607/company_dictionary.csv`
- `results/v39_broad_collaborator_text_probe_20260607/broad_collaborator_links_raw.csv`
- `results/v39_broad_collaborator_text_probe_20260607/relation_event_study.csv`
- `results/v39_broad_collaborator_text_probe_20260607/stacked_regressions.csv`
- `results/v39_broad_collaborator_text_probe_20260607/relation_panel.csv.gz`
- `results/v39_broad_collaborator_text_probe_20260607/stack_union_panel.csv.gz`