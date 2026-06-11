# v33 supplemental data probe

## Scope

- Input sample: v29 Table 3 sample, `combined_first_event_per_firm` and `liu_product_tfidf_same_industry_d_top10`.
- Additions: focal CAR, peer long-window CAR, peer own strict GenAI event flag, and CSMAR announcement pollution flags.
- This is a diagnostic pass, not the final cleaned main table.

## Headline Read

1. Peer own strict GenAI pollution is tiny: only 16 event-peer rows, about 0.6% of the v29 sample. Dropping these rows does not weaken the short-window negative peer reaction.
2. CSMAR announcement pollution is common. About 33.0% of rows have a title-keyword major announcement in the peer's calendar-day [-2,+2] window. After dropping these rows, Day 0 alone weakens, but `PeerCAR[0,+1]` remains negative and significant.
3. Long-window peer CARs are strongly negative in this first pass. This is useful against a simple immediate reversal story, but the `[0,+60]` coverage falls to about 59.9%, so it needs a coverage/late-event sensitivity check before being used as a main mechanism result.
4. The focal-peer mirror test does **not** support a zero-sum reallocation story in its current form. Focal CAR and peer CAR are positively related. This suggests that the current events can contain common valuation components, category-wide news, or product-market co-movement. Do not claim "focal gains are peer losses" based on this version.
5. Best current interpretation: pollution checks support a negative peer revaluation phenomenon, but the mechanism should stay at "competitive-risk reassessment among exposed peers" unless later residualized mirror / analyst revision tests give cleaner cash-flow evidence.

## Sample Flow and Pollution Flags

| metric                               |         value |
|:-------------------------------------|--------------:|
| base_rows                            | 2789          |
| base_events                          |  316          |
| base_peer_firms                      | 1384          |
| peer_own_strict_genai_m2_p2_rows     |   16          |
| peer_own_strict_genai_m2_p2_share    |    0.00573682 |
| peer_own_strict_genai_m2_p2_events   |   14          |
| peer_any_announcement_m2_p2_rows     | 1410          |
| peer_any_announcement_m2_p2_share    |    0.505558   |
| peer_any_announcement_m2_p2_events   |  307          |
| peer_major_announcement_m2_p2_rows   |  921          |
| peer_major_announcement_m2_p2_share  |    0.330226   |
| peer_major_announcement_m2_p2_events |  276          |
| genai_or_major_rows                  |  924          |
| genai_or_major_share                 |    0.331302   |

## Return-Window Coverage

| variable           | unit       |   nonmissing_rows |   total_rows |   coverage |
|:-------------------|:-----------|------------------:|-------------:|-----------:|
| focal_ar0_mm       | event      |               278 |          316 |     0.8797 |
| focal_car_0_p1_mm  | event      |               270 |          316 |     0.8544 |
| focal_car_m1_p1_mm | event      |               267 |          316 |     0.8449 |
| peer_car_0_p5_mm   | event_peer |              2621 |         2789 |     0.9398 |
| peer_car_0_p20_mm  | event_peer |              2206 |         2789 |     0.791  |
| peer_car_0_p60_mm  | event_peer |              1670 |         2789 |     0.5988 |

## Cleaned Event-Study Tests

| sample                                | outcome           |   nobs |   events |   peer_firms |      mean |       se |        z |        p |   positive_rate |
|:--------------------------------------|:------------------|-------:|---------:|-------------:|----------:|---------:|---------:|---------:|----------------:|
| all_v29_table3                        | peer_ar0_mm       |   2789 |      316 |         1384 | -0.002541 | 0.001098 | -2.31374 | 0.020682 |        0.457512 |
| all_v29_table3                        | peer_ar_p1_mm     |   2789 |      316 |         1384 | -0.002108 | 0.001093 | -1.9287  | 0.053768 |        0.44317  |
| all_v29_table3                        | peer_car_0_p1_mm  |   2789 |      316 |         1384 | -0.00465  | 0.001637 | -2.84099 | 0.004497 |        0.434206 |
| all_v29_table3                        | peer_car_0_p20_mm |   2206 |      294 |         1195 | -0.029266 | 0.004845 | -6.04054 | 0        |        0.378966 |
| all_v29_table3                        | peer_car_0_p60_mm |   1670 |      280 |          966 | -0.063856 | 0.007887 | -8.09647 | 0        |        0.366467 |
| drop_peer_own_strict_genai_m2_p2      | peer_ar0_mm       |   2773 |      316 |         1384 | -0.002681 | 0.001103 | -2.43076 | 0.015067 |        0.456185 |
| drop_peer_own_strict_genai_m2_p2      | peer_ar_p1_mm     |   2773 |      316 |         1384 | -0.002146 | 0.001097 | -1.95734 | 0.050308 |        0.442842 |
| drop_peer_own_strict_genai_m2_p2      | peer_car_0_p1_mm  |   2773 |      316 |         1384 | -0.004827 | 0.001649 | -2.92796 | 0.003412 |        0.433105 |
| drop_peer_own_strict_genai_m2_p2      | peer_car_0_p20_mm |   2193 |      294 |         1195 | -0.029347 | 0.004846 | -6.05628 | 0        |        0.378021 |
| drop_peer_own_strict_genai_m2_p2      | peer_car_0_p60_mm |   1661 |      280 |          966 | -0.063923 | 0.007937 | -8.05338 | 0        |        0.366045 |
| drop_peer_major_announcement_m2_p2    | peer_ar0_mm       |   1868 |      310 |         1050 | -0.001817 | 0.001153 | -1.57579 | 0.115073 |        0.458779 |
| drop_peer_major_announcement_m2_p2    | peer_ar_p1_mm     |   1868 |      310 |         1050 | -0.002407 | 0.001202 | -2.00247 | 0.045234 |        0.42773  |
| drop_peer_major_announcement_m2_p2    | peer_car_0_p1_mm  |   1868 |      310 |         1050 | -0.004224 | 0.001747 | -2.41748 | 0.015628 |        0.434154 |
| drop_peer_major_announcement_m2_p2    | peer_car_0_p20_mm |   1506 |      284 |          900 | -0.029378 | 0.005579 | -5.26586 | 0        |        0.37915  |
| drop_peer_major_announcement_m2_p2    | peer_car_0_p60_mm |   1117 |      269 |          705 | -0.063861 | 0.00906  | -7.04842 | 0        |        0.373321 |
| drop_peer_any_announcement_m2_p2      | peer_ar0_mm       |   1379 |      301 |          832 | -0.002756 | 0.001227 | -2.24632 | 0.024684 |        0.44525  |
| drop_peer_any_announcement_m2_p2      | peer_ar_p1_mm     |   1379 |      301 |          832 | -0.00293  | 0.001322 | -2.2156  | 0.026719 |        0.430022 |
| drop_peer_any_announcement_m2_p2      | peer_car_0_p1_mm  |   1379 |      301 |          832 | -0.005686 | 0.001853 | -3.06926 | 0.002146 |        0.42422  |
| drop_peer_any_announcement_m2_p2      | peer_car_0_p20_mm |   1130 |      277 |          723 | -0.029453 | 0.006117 | -4.81489 | 1e-06    |        0.39115  |
| drop_peer_any_announcement_m2_p2      | peer_car_0_p60_mm |    834 |      255 |          560 | -0.063772 | 0.00978  | -6.52041 | 0        |        0.378897 |
| drop_peer_genai_or_major_announcement | peer_ar0_mm       |   1865 |      310 |         1050 | -0.001839 | 0.001155 | -1.59146 | 0.111505 |        0.458445 |
| drop_peer_genai_or_major_announcement | peer_ar_p1_mm     |   1865 |      310 |         1050 | -0.002402 | 0.001206 | -1.99225 | 0.046343 |        0.427882 |
| drop_peer_genai_or_major_announcement | peer_car_0_p1_mm  |   1865 |      310 |         1050 | -0.004241 | 0.001752 | -2.4201  | 0.015516 |        0.434316 |
| drop_peer_genai_or_major_announcement | peer_car_0_p20_mm |   1503 |      284 |          900 | -0.029207 | 0.005551 | -5.26112 | 0        |        0.379907 |
| drop_peer_genai_or_major_announcement | peer_car_0_p60_mm |   1115 |      269 |          705 | -0.063809 | 0.009079 | -7.02815 | 0        |        0.373094 |

## Focal-Peer Mirror Tests

| unit            | outcome               | regressor         |   nobs |     coef |       se |         t |     p |   events |   peer_firms |         z |
|:----------------|:----------------------|:------------------|-------:|---------:|---------:|----------:|------:|---------:|-------------:|----------:|
| event_mean_peer | mean_peer_car_0_p1_mm | focal_car_0_p1_mm |    270 | 0.208339 | 0.041062 |   5.07373 | 0     |      nan |          nan | nan       |
| event_mean_peer | mean_peer_ar0_mm      | focal_ar0_mm      |    278 | 0.247095 | 0.045696 |   5.40736 | 0     |      nan |          nan | nan       |
| event_peer_rows | peer_car_0_p1_mm      | focal_car_0_p1_mm |   2421 | 0.202002 | 0.041687 | nan       | 1e-06 |      270 |         1250 |   4.84568 |
| event_peer_rows | peer_ar0_mm           | focal_ar0_mm      |   2473 | 0.246772 | 0.045326 | nan       | 0     |      278 |         1268 |   5.44435 |

## Announcement Hit Examples

| event_key                                 |   peer_code_norm | declare_dt          | Title                                                                                    | major_title_flag   |
|:------------------------------------------|-----------------:|:--------------------|:-----------------------------------------------------------------------------------------|:-------------------|
| combined_first_event_per_firm::1215877009 |           601811 | 2023-02-14 00:00:00 | 新华文轩：新华文轩独立董事关于第五届董事会2023年第一次会议相关事项的独立意见             | False              |
| combined_first_event_per_firm::1215877009 |           601811 | 2023-02-14 00:00:00 | 新华文轩：新华文轩关于调整公司高级管理人员的公告                                         | False              |
| combined_first_event_per_firm::1215989543 |           300287 | 2023-02-27 00:00:00 | 飞利信：关于公司控股股东及一致行动人之杨振华先生、曹忻军先生部分股份解除冻结的公告       | True               |
| combined_first_event_per_firm::1215989543 |           603322 | 2023-03-01 00:00:00 | 超讯通信：超讯通信：董监高减持股份结果公告                                               | True               |
| combined_first_event_per_firm::1215989543 |           603322 | 2023-03-01 00:00:00 | 超讯通信：超讯通信：关于股东违规减持公司股票及致歉的公告                                 | True               |
| combined_first_event_per_firm::1215989543 |           688038 | 2023-02-28 00:00:00 | 2022年度业绩快报公告                                                                     | True               |
| combined_first_event_per_firm::1216137139 |           002174 | 2023-03-16 00:00:00 | 游族网络：北京国枫律师事务所关于游族网络股份有限公司2023年第一次临时股东大会的法律意见书 | False              |
| combined_first_event_per_firm::1216137139 |           002174 | 2023-03-16 00:00:00 | 游族网络：2023年第一次临时股东大会决议公告                                               | False              |
| combined_first_event_per_firm::1216137139 |           002174 | 2023-03-18 00:00:00 | 游族网络：关于公司股东部分股份解除质押的公告                                             | True               |
| combined_first_event_per_firm::1216137139 |           002174 | 2023-03-18 00:00:00 | 游族网络：关于股东协议转让股份过户完成暨公司第一大股东发生变更的公告                     | False              |
| combined_first_event_per_firm::1216137139 |           002602 | 2023-03-17 00:00:00 | 关于易方达网上直销平台暂停工商银行卡快速赎回业务的通知                                   | False              |
| combined_first_event_per_firm::1216137139 |           002602 | 2023-03-18 00:00:00 | 世纪华通：关于公司子公司仲裁事项进展的公告                                               | True               |
| combined_first_event_per_firm::1216137139 |           002602 | 2023-03-18 00:00:00 | 世纪华通：关于委托理财的公告                                                             | False              |
| combined_first_event_per_firm::1216137139 |           002602 | 2023-03-18 00:00:00 | 世纪华通：第五届监事会第十五次会议决议公告                                               | False              |
| combined_first_event_per_firm::1216137139 |           002602 | 2023-03-18 00:00:00 | 世纪华通：关于公司股东所持股份被冻结的公告                                               | False              |
| combined_first_event_per_firm::1216137139 |           002602 | 2023-03-18 00:00:00 | 世纪华通：第五届董事会第十八次会议决议公告                                               | False              |
| combined_first_event_per_firm::1216137139 |           002602 | 2023-03-18 00:00:00 | 世纪华通：独立董事对第五届董事会第十八次会议相关事项的事前认可意见                       | False              |
| combined_first_event_per_firm::1216137139 |           002602 | 2023-03-18 00:00:00 | 世纪华通：关于2023年度日常关联交易预计的公告                                             | True               |
| combined_first_event_per_firm::1216137139 |           002602 | 2023-03-18 00:00:00 | 世纪华通：独立董事对第五届董事会第十八次会议相关事项的独立意见                           | False              |
| combined_first_event_per_firm::1216137139 |           002602 | 2023-03-18 00:00:00 | 世纪华通：关于召开公司2023年第三次临时股东大会的通知                                     | False              |

## Peer Own GenAI Hit Examples

| event_key                                 |   peer_code_norm | genai_event_dt      | title                                                                                                                      |
|:------------------------------------------|-----------------:|:--------------------|:---------------------------------------------------------------------------------------------------------------------------|
| combined_first_event_per_firm::1216555958 |           300264 | 2023-04-26 00:00:00 | 佳创视讯：关于未弥补亏损达到实收股本总额三分之一的公告                                                                     |
| combined_first_event_per_firm::1219388587 |           300166 | 2024-03-24 00:00:00 | 东方国信：关于对外投资的公告                                                                                               |
| combined_first_event_per_firm::1219388587 |           300166 | 2024-03-24 00:00:00 | 东方国信：第五届董事会第二十三次会议决议公告                                                                               |
| combined_first_event_per_firm::1219828363 |           688225 | 2024-04-27 00:00:00 | 亚信安全：2024年度“提质增效重回报”行动方案                                                                                 |
| combined_first_event_per_firm::1219920071 |           603636 | 2024-04-29 00:00:00 | 南威软件：南威软件：第四届董事会第三十五次会议决议公告                                                                     |
| combined_first_event_per_firm::1222951786 |           603236 | 2025-03-31 00:00:00 | 移远通信：2025年度向特定对象发行A股股票预案                                                                                |
| combined_first_event_per_firm::1223212161 |           688038 | 2025-04-25 00:00:00 | 中科通达：2025年度“提质增效重回报”行动方案                                                                                 |
| combined_first_event_per_firm::1223212161 |           688619 | 2025-04-23 00:00:00 | 罗普特：罗普特科技集团股份有限公司关于2024年度“提质增效重回报”专项行动方案的评估报告暨2025年度“提质增效重回报”专项行动方案 |
| combined_first_event_per_firm::1223221311 |           688038 | 2025-04-25 00:00:00 | 中科通达：2025年度“提质增效重回报”行动方案                                                                                 |
| combined_first_event_per_firm::1223238300 |           688038 | 2025-04-25 00:00:00 | 中科通达：2025年度“提质增效重回报”行动方案                                                                                 |
| combined_first_event_per_firm::1223238300 |           688619 | 2025-04-23 00:00:00 | 罗普特：罗普特科技集团股份有限公司关于2024年度“提质增效重回报”专项行动方案的评估报告暨2025年度“提质增效重回报”专项行动方案 |
| combined_first_event_per_firm::1223307855 |           688619 | 2025-04-23 00:00:00 | 罗普特：罗普特科技集团股份有限公司关于2024年度“提质增效重回报”专项行动方案的评估报告暨2025年度“提质增效重回报”专项行动方案 |
| combined_first_event_per_firm::1224462981 |           603496 | 2025-08-14 00:00:00 | 恒为科技：关于2025年度“提质增效重回报”行动方案的公告                                                                       |
| combined_first_event_per_firm::1224815528 |           300036 | 2025-11-19 00:00:00 | 超图软件：关于项目中标的公告                                                                                               |
| combined_first_event_per_firm::1224815886 |           301172 | 2025-11-19 00:00:00 | 君逸数码：关于对外投资的自愿性披露公告                                                                                     |
| combined_first_event_per_firm::1224863798 |           301191 | 2025-12-08 00:00:00 | 菲菱科思：关于与专业投资机构拟共同对外投资暨关联交易的公告                                                                 |
| combined_first_event_per_firm::1225188890 |           300397 | 2026-04-23 00:00:00 | 天和防务：关于调整优化公司投资项目的公告                                                                                   |

## Output Files

- `results/v33_supplement_data_probe_20260605/panel_with_supplement_flags.csv.gz`
- `results/v33_supplement_data_probe_20260605/sample_flow.csv`
- `results/v33_supplement_data_probe_20260605/return_window_coverage.csv`
- `results/v33_supplement_data_probe_20260605/cleaned_event_study_tests.csv`
- `results/v33_supplement_data_probe_20260605/focal_peer_mirror_tests.csv`
- `results/v33_supplement_data_probe_20260605/event_level_mirror_panel.csv`
- `results/v33_supplement_data_probe_20260605/peer_announcement_window_hits.csv.gz`
- `results/v33_supplement_data_probe_20260605/peer_own_genai_window_hits.csv`
