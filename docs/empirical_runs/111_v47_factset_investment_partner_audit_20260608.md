# v47 FactSet Investment-Linked Partner Audit

Date: 2026-06-08

## Scope

This run audits the FactSet `PARTNER-INVESTO` and `PARTNER-EINVEST` rows that produced a positive event-weighted CAR in v43.

FactSet methodology guide definitions:

- `PARTNER-EINVEST` / Equity Investment: the source company owns an equity stake in the target entity.
- `PARTNER-INVESTO` / Investor: the target entity owns equity in the source company.

Accordingly, relative to the focal GenAI discloser:

- `investor_in_focal`: the listed related firm holds/invests in the focal firm.
- `investee_of_focal`: the focal firm holds/invests in the listed related firm.

## Sample Flow

| sample | raw_relationship_rows | raw_events | raw_focal_firms | raw_related_firms | clean_car0p1_rows | clean_car0p1_events | clean_related_firms |
|---|---|---|---|---|---|---|---|
| investment_linked_partner | 98.0 | 56.0 | 56.0 | 94.0 | 86.0 | 54.0 | 83.0 |
| investor_in_focal | 43.0 | 35.0 | 35.0 | 40.0 | 40.0 | 33.0 | 38.0 |
| investee_of_focal | 55.0 | 30.0 | 30.0 | 54.0 | 46.0 | 28.0 | 45.0 |

## CAR[0,+1] by Direction

| relation_type | outcome | window | mean | se | z | p | nobs | events | related_firms | median | positive_share | event_weighted_mean | event_weighted_se | event_weighted_z | event_weighted_p | event_weighted_events | event_positive_share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| investee_of_focal | peer_car_0_p1_mm | CAR[0,+1] | 0.006235 | 0.006721 | 0.927634 | 0.353598 | 46.0 | 28.0 | 45.0 | -5.1e-05 | 0.5 | 0.006418 | 0.005948 | 1.078961 | 0.280605 | 28.0 | 0.5 |
| investment_linked_partner | peer_car_0_p1_mm | CAR[0,+1] | 0.006571 | 0.004544 | 1.445975 | 0.148184 | 86.0 | 54.0 | 83.0 | 0.001077 | 0.511628 | 0.008396 | 0.004043 | 2.076663 | 0.037833 | 54.0 | 0.574074 |
| investor_in_focal | peer_car_0_p1_mm | CAR[0,+1] | 0.006957 | 0.004423 | 1.572976 | 0.115724 | 40.0 | 33.0 | 38.0 | 0.005961 | 0.525 | 0.006111 | 0.005112 | 1.195518 | 0.231885 | 33.0 | 0.575758 |

## AR[0] by Direction

| relation_type | outcome | window | mean | se | z | p | nobs | events | related_firms | median | positive_share | event_weighted_mean | event_weighted_se | event_weighted_z | event_weighted_p | event_weighted_events | event_positive_share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| investee_of_focal | peer_ar0_mm | AR[0] | 0.005258 | 0.002816 | 1.866757 | 0.061935 | 46.0 | 28.0 | 45.0 | 0.002463 | 0.565217 | 0.006001 | 0.002512 | 2.388745 | 0.016906 | 28.0 | 0.607143 |
| investment_linked_partner | peer_ar0_mm | AR[0] | 0.002871 | 0.002436 | 1.178311 | 0.238673 | 86.0 | 54.0 | 83.0 | 0.00184 | 0.55814 | 0.002043 | 0.002457 | 0.831608 | 0.40563 | 54.0 | 0.555556 |
| investor_in_focal | peer_ar0_mm | AR[0] | 0.000126 | 0.003376 | 0.03725 | 0.970286 | 40.0 | 33.0 | 38.0 | 0.000499 | 0.55 | -0.000905 | 0.003923 | -0.230774 | 0.81749 | 33.0 | 0.515152 |

## Leave-One-Event-Out Check

| sample | events | base_event_weighted_mean | loo_min_mean | loo_max_mean | loo_share_positive | largest_positive_event | largest_positive_event_mean | largest_negative_event | largest_negative_event_mean |
|---|---|---|---|---|---|---|---|---|---|
| investment_linked_partner | 54.0 | 0.008396 | 0.006712 | 0.00976 | 1.0 | combined_first_event_per_firm::1215877009 | 0.09766 | combined_first_event_per_firm::1219028032 | -0.063884 |
| investor_in_focal | 33.0 | 0.006111 | 0.003583 | 0.008355 | 1.0 | combined_first_event_per_firm::1223384153 | 0.087024 | combined_first_event_per_firm::1219028032 | -0.065696 |
| investee_of_focal | 28.0 | 0.006418 | 0.003038 | 0.008955 | 1.0 | combined_first_event_per_firm::1215877009 | 0.09766 | combined_first_event_per_firm::1219028032 | -0.062072 |

## Top Event-Level Means

| event_key | event_date | focal_code | focal_name | announcement_title | relationship_rows | related_firms | mean_car0p1 | max_car0p1 | min_car0p1 | positive_share | roles | rel_types | related_names | rank_abs_contribution |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| combined_first_event_per_firm::1215877009 | 2023-02-15 00:00:00 | 300364 | 中文在线 | 中文在线：关于与北京澜舟科技有限公司签订战略合作协议的公告 | 1.0 | 1.0 | 0.09766 | 0.09766 | 0.09766 | 1.0 | investee_of_focal | PARTNER-INVESTO | New Guomai Digital Culture Co., Ltd. | 1.0 |
| combined_first_event_per_firm::1223384153 | 2025-04-29 00:00:00 | 600998 | 九州通 | 九州通：九州通致投资者的一封信（2024年度） | 1.0 | 1.0 | 0.087024 | 0.087024 | 0.087024 | 1.0 | investor_in_focal | PARTNER-EINVEST | Winning Health Technology Group Co. Ltd. | 2.0 |
| combined_first_event_per_firm::1217167900 | 2023-06-29 00:00:00 | 002599 | 盛通股份 | 盛通股份：关于全资子公司签署战略合作协议的公告 | 1.0 | 1.0 | 0.068338 | 0.068338 | 0.068338 | 1.0 | investee_of_focal | PARTNER-EINVEST | Tianjin Binhai Energy & Development Co., Ltd. | 3.0 |
| combined_first_event_per_firm::1222945893 | 2025-03-29 00:00:00 | 002063 | 远光软件 | 远光软件：关于2024年年度利润分配预案的公告 | 1.0 | 1.0 | 0.056859 | 0.056859 | 0.056859 | 1.0 | investor_in_focal | PARTNER-EINVEST | GD Power Development Co., Ltd. | 6.0 |
| combined_first_event_per_firm::1222946316 | 2025-03-29 00:00:00 | 600588 | 用友网络 | 用友网络：用友网络2024年年度报告 | 1.0 | 1.0 | 0.037883 | 0.037883 | 0.037883 | 1.0 | investee_of_focal | PARTNER-INVESTO | Yonyou Auto Information Technology (Shanghai) Co., Ltd. | 7.0 |
| combined_first_event_per_firm::1223304438 | 2025-04-25 00:00:00 | 600845 | 宝信软件 | 宝信软件：关于投资宝之云华北基地A4A5A6楼项目的公告 | 2.0 | 2.0 | 0.034911 | 0.063076 | 0.006747 | 1.0 | investor_in_focal | PARTNER-EINVEST;PARTNER-INVESTO | Shenzhen Inovance Technology Co., Ltd.; Baoshan Iron & Steel Co., Ltd. | 8.0 |
| combined_first_event_per_firm::1224808198 | 2025-11-14 00:00:00 | 000917 | 电广传媒 | 电广传媒：关于公司参与张家界旅游集团股份有限公司重整投资暨关联交易的公告 | 8.0 | 8.0 | 0.03465 | 0.13168 | -0.013745 | 0.875 | investee_of_focal;investor_in_focal | PARTNER-EINVEST;PARTNER-INVESTO | Shenzhen King Brother Electronics Technology Co., Ltd.; Beijing Hanyi Innovation Technology Co., Ltd.; Hebei Broadcasting Wireless Media Co., Ltd.; Cisen Pharmaceutical Ltd.; Wuhan Citms Technology Co., Ltd.; Shanghai OPM Biosciences Co. Ltd. | 9.0 |
| combined_first_event_per_firm::1223391534 | 2025-04-29 00:00:00 | 688288 | 鸿泉物联 | 鸿泉物联：鸿泉物联：2024年年度报告 | 1.0 | 1.0 | 0.033662 | 0.033662 | 0.033662 | 1.0 | investor_in_focal | PARTNER-INVESTO | China TransInfo Technology Co., Ltd. | 10.0 |
| combined_first_event_per_firm::1224177425 | 2025-07-15 00:00:00 | 002161 | 远 望 谷 | 远 望 谷：发行人关于本次发行方案的论证分析报告 | 1.0 | 1.0 | 0.033562 | 0.033562 | 0.033562 | 1.0 | investee_of_focal | PARTNER-INVESTO | Henan Thinker Automatic Equipment Co., Ltd. | 11.0 |
| combined_first_event_per_firm::1219612253 | 2024-04-14 00:00:00 | 688568 | 中科星图 | 中科星图：中科星图股份有限公司2024年度“提质增效重回报”行动方案 | 1.0 | 1.0 | 0.028855 | 0.028855 | 0.028855 | 1.0 | investor_in_focal | PARTNER-INVESTO | Dawning Information Industry Co., Ltd. | 13.0 |
| combined_first_event_per_firm::1224863798 | 2025-12-09 00:00:00 | 603019 | 中科曙光 | 中科曙光：中科曙光关于终止重大资产重组的公告 | 2.0 | 2.0 | 0.028748 | 0.059012 | -0.001517 | 0.5 | investee_of_focal | PARTNER-EINVEST | Hygon Information Technology Co., Ltd.; Geovis Technology Co., Ltd. | 14.0 |
| combined_first_event_per_firm::1223955587 | 2025-06-23 00:00:00 | 688591 | 泰凌微 | 泰凌微：关于端侧AI新品推广的自愿性披露公告 | 1.0 | 1.0 | 0.028304 | 0.028304 | 0.028304 | 1.0 | investor_in_focal | PARTNER-INVESTO | Beijing Teamsun Technology Co., Ltd. | 15.0 |
| combined_first_event_per_firm::1224950904 | 2026-01-26 00:00:00 | 300948 | 冠中生态 | 冠中生态：关于现金收购杭州精算家人工智能技术有限公司51%股权暨关联交易的公告 | 1.0 | 1.0 | 0.027615 | 0.027615 | 0.027615 | 1.0 | investee_of_focal | PARTNER-EINVEST | Shandong Hi-speed Co., Ltd. | 16.0 |
| combined_first_event_per_firm::1220689900 | 2024-07-19 00:00:00 | 600831 | ST广网 | ST广网：关于与北京中软国际信息技术有限公司签订《战略合作协议》的公告 | 2.0 | 2.0 | 0.026879 | 0.045671 | 0.008087 | 1.0 | investor_in_focal | PARTNER-EINVEST;PARTNER-INVESTO | Tsinghua Tongfang Co., Ltd.; Oriental Pearl Group Co. Ltd. | 17.0 |
| combined_first_event_per_firm::1224906066 | 2025-12-30 00:00:00 | 601858 | 中国科传 | 中国科传：中银国际证券股份有限公司关于中国科技出版传媒股份有限公司调整及变更部分募集资金投资项目的核查意见 | 1.0 | 1.0 | 0.024649 | 0.024649 | 0.024649 | 1.0 | investor_in_focal | PARTNER-INVESTO | China South Publishing & Media Group Co., Ltd. | 18.0 |

## Bottom Event-Level Means

| event_key | event_date | focal_code | focal_name | announcement_title | relationship_rows | related_firms | mean_car0p1 | max_car0p1 | min_car0p1 | positive_share | roles | rel_types | related_names | rank_abs_contribution |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| combined_first_event_per_firm::1219028032 | 2024-01-30 00:00:00 | 600728 | 佳都科技 | 佳都科技：佳都科技2023年度业绩预盈公告 | 2.0 | 2.0 | -0.063884 | -0.062072 | -0.065696 | 0.0 | investee_of_focal;investor_in_focal | PARTNER-EINVEST;PARTNER-INVESTO | Kingfa Sci. & Tech. Co., Ltd.; CloudWalk Technology Co. Ltd. | 4.0 |
| combined_first_event_per_firm::1217022601 | 2023-06-09 00:00:00 | 600640 | 国脉文化 | 国脉文化：新国脉数字文化股份有限公司第十届董事会第三十五次会议决议公告 | 1.0 | 1.0 | -0.062284 | -0.062284 | -0.062284 | 0.0 | investor_in_focal | PARTNER-INVESTO | COL Group Co., Ltd. | 5.0 |
| combined_first_event_per_firm::1225011749 | 2026-03-16 00:00:00 | 600282 | 南钢股份 | 南钢股份：南京钢铁股份有限公司2026年度“提质增效重回报”行动方案 | 1.0 | 1.0 | -0.031497 | -0.031497 | -0.031497 | 0.0 | investee_of_focal | PARTNER-INVESTO | ZheJiang Wansheng Co., Ltd. | 12.0 |
| combined_first_event_per_firm::1220400369 | 2024-06-19 00:00:00 | 600104 | 上汽集团 | 上汽集团：上汽集团2024年度提质增效重回报行动方案 | 5.0 | 5.0 | -0.023881 | -0.002834 | -0.061931 | 0.0 | investee_of_focal;investor_in_focal | PARTNER-EINVEST;PARTNER-INVESTO | Guangdong Delian Group Co., Ltd.; Contemporary Amperex Technology Co., Ltd.; Wuhan KOTEI Informatics Co., Ltd.; Huayu Automotive Systems Co., Ltd.; Shanghai New Power Automotive Technology Co., Ltd. | 20.0 |
| combined_first_event_per_firm::1219156400 | 2024-02-22 00:00:00 | 301301 | 川宁生物 | 川宁生物：伊犁川宁生物技术股份有限公司关于签署战略合作协议的公告 | 1.0 | 1.0 | -0.022307 | -0.022307 | -0.022307 | 0.0 | investor_in_focal | PARTNER-INVESTO | Sichuan Kelun Pharmaceutical Co., Ltd. | 22.0 |
| combined_first_event_per_firm::1223307855 | 2025-04-25 00:00:00 | 688038 | 中科通达 | 中科通达：2025年度“提质增效重回报”行动方案 | 1.0 | 1.0 | -0.019605 | -0.019605 | -0.019605 | 0.0 | investor_in_focal | PARTNER-INVESTO | Hunan TV & Broadcast Intermediary Co., Ltd. | 23.0 |
| combined_first_event_per_firm::1219893154 | 2024-04-28 00:00:00 | 600551 | 时代出版 | 时代出版：2023年年度股东大会会议材料 | 1.0 | 1.0 | -0.018837 | -0.018837 | -0.018837 | 0.0 | investor_in_focal | PARTNER-EINVEST | Nexchip Semiconductor Corp. | 24.0 |
| combined_first_event_per_firm::1224118722 | 2025-07-09 00:00:00 | 300617 | 安靠智电 | 安靠智电：关于控股子公司签订青海海东绿算产业园110kV变电站EPC总承包合同的公告 | 1.0 | 1.0 | -0.017803 | -0.017803 | -0.017803 | 0.0 | investee_of_focal | PARTNER-EINVEST | Jiangsu Tianmu Lake Tourism Co., Ltd. | 26.0 |
| combined_first_event_per_firm::1223097206 | 2025-04-15 00:00:00 | 600153 | 建发股份 | 建发股份：建发股份2024年年度股东大会会议资料 | 3.0 | 3.0 | -0.016887 | 0.000107 | -0.0301 | 0.333333 | investee_of_focal | PARTNER-INVESTO | Gospell Digital Technology Co., Ltd.; Xiamen Faratronic Co., Ltd.; Hongfa Technology Co., Ltd. | 27.0 |
| combined_first_event_per_firm::1223102360 | 2025-04-15 00:00:00 | 601668 | 中国建筑 | 中国建筑：中国建筑关于估值提升计划的公告 | 4.0 | 4.0 | -0.016061 | -0.007091 | -0.023945 | 0.0 | investee_of_focal;investor_in_focal | PARTNER-EINVEST;PARTNER-INVESTO | Shenzhen Properties & Resources Development (Group) Co. Ltd.; China West Construction Co., Ltd.; Shanghai Huayi Group Corp. Ltd.; Metro Land Corp. Ltd. | 28.0 |
| combined_first_event_per_firm::1224831188 | 2025-11-27 00:00:00 | 688629 | 华丰科技 | 华丰科技：2025年度向特定对象发行A股股票预案（修订稿） | 1.0 | 1.0 | -0.012879 | -0.012879 | -0.012879 | 0.0 | investor_in_focal | PARTNER-INVESTO | Sichuan Changhong Electric Co., Ltd. | 32.0 |
| combined_first_event_per_firm::1224905196 | 2025-12-29 00:00:00 | 600621 | 华鑫股份 | 华鑫股份：华鑫股份“提质增效重回报”专项行动方案 | 1.0 | 1.0 | -0.012514 | -0.012514 | -0.012514 | 0.0 | investor_in_focal | PARTNER-INVESTO | Shanghai Foreign Service Holding Group Co., Ltd. | 34.0 |
| combined_first_event_per_firm::1220144177 | 2024-05-24 00:00:00 | 600345 | 长江通信 | 长江通信：长江通信2023年度业绩暨现金分红说明会召开情况的公告 | 1.0 | 1.0 | -0.01005 | -0.01005 | -0.01005 | 0.0 | investee_of_focal | PARTNER-EINVEST | Wuhan East Lake High Technology Group Co., Ltd. | 36.0 |
| combined_first_event_per_firm::1223421123 | 2025-04-30 00:00:00 | 600887 | 伊利股份 | 伊利股份：内蒙古伊利实业集团股份有限公司2024年年度报告 | 1.0 | 1.0 | -0.008161 | -0.008161 | -0.008161 | 0.0 | investee_of_focal | PARTNER-EINVEST | Shandong Xinjufeng Technology Packaging Co., Ltd. | 38.0 |
| combined_first_event_per_firm::1221542518 | 2024-10-28 00:00:00 | 300613 | 富瀚微 | 富瀚微：关于对外投资暨关联交易的公告 | 1.0 | 1.0 | -0.007708 | -0.007708 | -0.007708 | 0.0 | investor_in_focal | PARTNER-INVESTO | Hangzhou Hikvision Digital Technology Co., Ltd. | 41.0 |

## High/Low Relationship Examples for Manual Validation

| event_date | focal_code | focal_name | related_code | related_factset_name | investment_role | investment_direction_cn | rel_type | focal_side | relation_start | relation_age_days | peer_car_0_p1_mm | peer_ar0_mm | peer_ar_p1_mm | announcement_title | match_evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025-11-14 00:00:00 | 000917 | 电广传媒 | 301041 | Shenzhen King Brother Electronics Technology Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2023-08-08 | 829.0 | 0.13168 | 0.026193 | 0.105486 | 电广传媒：关于公司参与张家界旅游集团股份有限公司重整投资暨关联交易的公告 | ; ; ; ;  |
| 2023-02-15 00:00:00 | 300364 | 中文在线 | 600640 | New Guomai Digital Culture Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2019-11-07 | 1196.0 | 0.09766 | 0.033991 | 0.063668 | 中文在线：关于与北京澜舟科技有限公司签订战略合作协议的公告 | ; ; ; ;  |
| 2025-04-29 00:00:00 | 600998 | 九州通 | 300253 | Winning Health Technology Group Co. Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-EINVEST | target | 2024-04-19 | 375.0 | 0.087024 | 0.049956 | 0.037069 | 九州通：九州通致投资者的一封信（2024年度） | ; ; ; ;  |
| 2023-06-29 00:00:00 | 002599 | 盛通股份 | 000695 | Tianjin Binhai Energy & Development Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-EINVEST | source | 2022-12-06 | 205.0 | 0.068338 | 0.037386 | 0.030952 | 盛通股份：关于全资子公司签署战略合作协议的公告 | ; ; ; ;  |
| 2025-04-25 00:00:00 | 600845 | 宝信软件 | 600019 | Baoshan Iron & Steel Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-INVESTO | source | 2014-02-14 | 4088.0 | 0.063076 | 0.019001 | 0.044074 | 宝信软件：关于投资宝之云华北基地A4A5A6楼项目的公告 | ; ; ; ;  |
| 2025-12-09 00:00:00 | 603019 | 中科曙光 | 688568 | Geovis Technology Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-EINVEST | source | 2024-04-17 | 601.0 | 0.059012 | -0.015064 | 0.074076 | 中科曙光：中科曙光关于终止重大资产重组的公告 | ; ; ; ;  |
| 2025-11-14 00:00:00 | 000917 | 电广传媒 | 688038 | Wuhan Citms Technology Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2024-05-02 | 561.0 | 0.058736 | 0.020894 | 0.037842 | 电广传媒：关于公司参与张家界旅游集团股份有限公司重整投资暨关联交易的公告 | ; ; ; ;  |
| 2025-03-29 00:00:00 | 002063 | 远光软件 | 600795 | GD Power Development Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-EINVEST | target | 2024-04-17 | 346.0 | 0.056859 | 0.021951 | 0.034908 | 远光软件：关于2024年年度利润分配预案的公告 | software; ; ; ;  |
| 2024-07-19 00:00:00 | 600831 | ST广网 | 600100 | Tsinghua Tongfang Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-EINVEST | target | 2021-09-22 | 1031.0 | 0.045671 | 0.020298 | 0.025373 | ST广网：关于与北京中软国际信息技术有限公司签订《战略合作协议》的公告 | ; ; ; ;  |
| 2025-03-29 00:00:00 | 600588 | 用友网络 | 688479 | Yonyou Auto Information Technology (Shanghai) Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2023-10-09 | 537.0 | 0.037883 | -0.000103 | 0.037986 | 用友网络：用友网络2024年年度报告 | ; ; ; ;  |
| 2025-11-14 00:00:00 | 000917 | 电广传媒 | 301270 | Beijing Hanyi Innovation Technology Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2023-04-28 | 931.0 | 0.037462 | 0.008404 | 0.029058 | 电广传媒：关于公司参与张家界旅游集团股份有限公司重整投资暨关联交易的公告 | ; ; ; ;  |
| 2025-04-29 00:00:00 | 688288 | 鸿泉物联 | 002373 | China TransInfo Technology Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-INVESTO | source | 2022-11-16 | 895.0 | 0.033662 | 0.001344 | 0.032318 | 鸿泉物联：鸿泉物联：2024年年度报告 | ; ; ; ;  |
| 2025-07-15 00:00:00 | 002161 | 远 望 谷 | 603508 | Henan Thinker Automatic Equipment Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2024-04-15 | 456.0 | 0.033562 | 0.022767 | 0.010795 | 远 望 谷：发行人关于本次发行方案的论证分析报告 | ; ; ; ;  |
| 2024-04-14 00:00:00 | 688568 | 中科星图 | 603019 | Dawning Information Industry Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-INVESTO | source | 2022-12-12 | 489.0 | 0.028855 | -0.011578 | 0.040434 | 中科星图：中科星图股份有限公司2024年度“提质增效重回报”行动方案 | ; ; ; ;  |
| 2025-06-23 00:00:00 | 688591 | 泰凌微 | 600410 | Beijing Teamsun Technology Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-INVESTO | source | 2024-05-22 | 397.0 | 0.028304 | 0.011494 | 0.01681 | 泰凌微：关于端侧AI新品推广的自愿性披露公告 | ; ; ; ;  |
| 2025-12-10 00:00:00 | 301551 | 无线传媒 | 000917 | Hunan TV & Broadcast Intermediary Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-EINVEST | target | 2023-07-14 | 880.0 | 0.028304 | 0.020344 | 0.00796 | 无线传媒：关于控股子公司参与传媒集团公开招标暨关联交易的公告 | ; ; ; ;  |
| 2026-01-26 00:00:00 | 300948 | 冠中生态 | 600350 | Shandong Hi-speed Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-EINVEST | source | 2024-05-08 | 628.0 | 0.027615 | 0.010676 | 0.016939 | 冠中生态：关于现金收购杭州精算家人工智能技术有限公司51%股权暨关联交易的公告 | ; ; ; ;  |
| 2025-12-30 00:00:00 | 601858 | 中国科传 | 601098 | China South Publishing & Media Group Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-INVESTO | source | 2020-07-10 | 1999.0 | 0.024649 | 0.000642 | 0.024008 | 中国科传：中银国际证券股份有限公司关于中国科技出版传媒股份有限公司调整及变更部分募集资金投资项目的核查意见 | ; ; ; ;  |
| 2023-08-07 00:00:00 | 300229 | 拓尔思 | 300608 | SI-TECH Information Technology Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2022-11-16 | 264.0 | 0.024038 | 0.02283 | 0.001207 | 拓尔思：第五届监事会第十五次会议决议公告 | ; ; ; ;  |
| 2023-11-21 00:00:00 | 603888 | 新华网 | 600050 | China United Network Communications Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-INVESTO | source | 2019-11-27 | 1455.0 | 0.022797 | -0.002001 | 0.024798 | 新华网：新华网股份有限公司关于举办“走进上市公司”活动情况的公告 | ; ; ; ;  |
| 2024-01-30 00:00:00 | 600728 | 佳都科技 | 600143 | Kingfa Sci. & Tech. Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-EINVEST | target | 2019-10-16 | 1567.0 | -0.065696 | -0.051527 | -0.014169 | 佳都科技：佳都科技2023年度业绩预盈公告 | YUESHANG HI-TECH CO LTD.; ; ; ;  |
| 2023-06-09 00:00:00 | 600640 | 国脉文化 | 300364 | COL Group Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-INVESTO | source | 2019-11-07 | 1310.0 | -0.062284 | -0.046728 | -0.015556 | 国脉文化：新国脉数字文化股份有限公司第十届董事会第三十五次会议决议公告 | ; ; ; ;  |
| 2024-01-30 00:00:00 | 600728 | 佳都科技 | 688327 | CloudWalk Technology Co. Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2023-08-07 | 176.0 | -0.062072 | -0.005635 | -0.056437 | 佳都科技：佳都科技2023年度业绩预盈公告 | ; ; ; ;  |
| 2024-06-19 00:00:00 | 600104 | 上汽集团 | 301221 | Wuhan KOTEI Informatics Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2022-07-07 | 713.0 | -0.061931 | -0.009888 | -0.052043 | 上汽集团：上汽集团2024年度提质增效重回报行动方案 | ; ; ; ;  |
| 2024-06-19 00:00:00 | 600104 | 上汽集团 | 600841 | Shanghai New Power Automotive Technology Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2021-04-08 | 1168.0 | -0.034352 | -0.008678 | -0.025674 | 上汽集团：上汽集团2024年度提质增效重回报行动方案 | SAIC Iveco Commercial Vehicle Investment Co., Ltd; ; ; ;  |
| 2026-03-16 00:00:00 | 600282 | 南钢股份 | 603010 | ZheJiang Wansheng Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2024-04-05 | 710.0 | -0.031497 | -0.005307 | -0.02619 | 南钢股份：南京钢铁股份有限公司2026年度“提质增效重回报”行动方案 | ; ; ; ;  |
| 2025-04-15 00:00:00 | 600153 | 建发股份 | 600885 | Hongfa Technology Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2022-06-13 | 1037.0 | -0.0301 | -0.003851 | -0.026249 | 建发股份：建发股份2024年年度股东大会会议资料 | ; ; ; ;  |
| 2024-06-04 00:00:00 | 601360 | 三六零 | 688030 | Hillstone Networks Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2023-08-02 | 307.0 | -0.028302 | -0.034771 | 0.006469 | 三六零：三六零安全科技股份有限公司2024年度“提质增效重回报”行动方案 | ; ; ; ;  |
| 2024-08-28 00:00:00 | 600019 | 宝钢股份 | 601825 | Shanghai Rural Commercial Bank Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2023-04-28 | 488.0 | -0.027345 | 0.009751 | -0.037096 | 宝钢股份：宝钢股份2024年半年度主要经营数据公告 | ; ; ; ;  |
| 2025-04-15 00:00:00 | 601668 | 中国建筑 | 002302 | China West Construction Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-EINVEST | target | 2024-04-07 | 373.0 | -0.023945 | -0.008751 | -0.015194 | 中国建筑：中国建筑关于估值提升计划的公告 | ; ; ; ;  |
| 2025-04-15 00:00:00 | 601668 | 中国建筑 | 000011 | Shenzhen Properties & Resources Development (Group) Co. Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2020-09-16 | 1672.0 | -0.022309 | -0.010526 | -0.011783 | 中国建筑：中国建筑关于估值提升计划的公告 | supplier; ; ; ;  |
| 2024-02-22 00:00:00 | 301301 | 川宁生物 | 002422 | Sichuan Kelun Pharmaceutical Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-INVESTO | source | 2023-09-27 | 148.0 | -0.022307 | -0.010244 | -0.012063 | 川宁生物：伊犁川宁生物技术股份有限公司关于签署战略合作协议的公告 | ; ; ; ;  |
| 2025-04-15 00:00:00 | 600153 | 建发股份 | 600563 | Xiamen Faratronic Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2020-08-04 | 1715.0 | -0.020669 | 0.000489 | -0.021158 | 建发股份：建发股份2024年年度股东大会会议资料 | ; ; ; ;  |
| 2025-04-25 00:00:00 | 688038 | 中科通达 | 000917 | Hunan TV & Broadcast Intermediary Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-INVESTO | source | 2024-05-02 | 358.0 | -0.019605 | 0.006301 | -0.025905 | 中科通达：2025年度“提质增效重回报”行动方案 | ; ; ; ;  |
| 2024-04-28 00:00:00 | 600551 | 时代出版 | 688249 | Nexchip Semiconductor Corp. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-EINVEST | target | 2024-03-04 | 55.0 | -0.018837 | 0.003116 | -0.021953 | 时代出版：2023年年度股东大会会议材料 | ; ; ; ;  |
| 2025-07-09 00:00:00 | 300617 | 安靠智电 | 603136 | Jiangsu Tianmu Lake Tourism Co., Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-EINVEST | source | 2024-02-05 | 520.0 | -0.017803 | -0.010366 | -0.007438 | 安靠智电：关于控股子公司签订青海海东绿算产业园110kV变电站EPC总承包合同的公告 | ; ; ; ;  |
| 2025-11-14 00:00:00 | 000917 | 电广传媒 | 688293 | Shanghai OPM Biosciences Co. Ltd. | investee_of_focal | 焦点公司持有/投资关联方 | PARTNER-INVESTO | target | 2023-02-21 | 997.0 | -0.013745 | 0.013777 | -0.027521 | 电广传媒：关于公司参与张家界旅游集团股份有限公司重整投资暨关联交易的公告 | ; ; ; ;  |
| 2025-11-27 00:00:00 | 688629 | 华丰科技 | 600839 | Sichuan Changhong Electric Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-INVESTO | source | 2024-05-09 | 567.0 | -0.012879 | -0.010369 | -0.00251 | 华丰科技：2025年度向特定对象发行A股股票预案（修订稿） | ; ; ; ;  |
| 2025-12-29 00:00:00 | 600621 | 华鑫股份 | 600662 | Shanghai Foreign Service Holding Group Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-INVESTO | source | 2024-04-12 | 626.0 | -0.012514 | -0.00942 | -0.003094 | 华鑫股份：华鑫股份“提质增效重回报”专项行动方案 | ; ; ; ;  |
| 2024-06-19 00:00:00 | 600104 | 上汽集团 | 002666 | Guangdong Delian Group Co., Ltd. | investor_in_focal | 关联方持有/投资焦点公司 | PARTNER-EINVEST | target | 2024-04-24 | 56.0 | -0.012285 | 0.004185 | -0.01647 | 上汽集团：上汽集团2024年度提质增效重回报行动方案 | ; ; ; ;  |

## Reading

- The positive investment-linked result is not obviously a pure direction story: both `investor_in_focal` and `investee_of_focal` have positive relationship-level mean CARs.
- The event-weighted positive result should be treated as a promising second finding, not yet as final main evidence, because it needs manual validation of FactSet investment links and direction semantics in Chinese cases.
- If retained, the safest label is `investment-linked partners`, not generic collaborators or operating partners.

## Output Files

- `results/v47_factset_investment_partner_audit_20260608/investment_sample_flow.csv`
- `results/v47_factset_investment_partner_audit_20260608/investment_event_study_by_direction.csv`
- `results/v47_factset_investment_partner_audit_20260608/investment_event_level_contribution.csv`
- `results/v47_factset_investment_partner_audit_20260608/investment_leave_one_event_out.csv`
- `results/v47_factset_investment_partner_audit_20260608/investment_relationship_examples.csv`
