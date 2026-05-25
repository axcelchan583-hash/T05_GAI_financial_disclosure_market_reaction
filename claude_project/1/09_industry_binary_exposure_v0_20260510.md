# Industry Binary Exposure v0

Date: 2026-05-10 handoff; generated 2026-05-11

## Bottom Line

This script constructed `HighRiskDiscIndustry_i` as an industry-level 0/1 exposure for T05 and wrote the firm-year panel to:

```text
/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/data/interim/industry_binary_exposure_v0.parquet
```

Validation status: FAIL.

This variable should not replace the continuous `PreRiskWritingBurden_i` main design. In this v0 validation, the high-risk industry group is only slightly longer than the low-risk group in pre-period risk disclosure, the difference is not statistically significant, and the correlation with continuous pre-period risk length is near zero. If used at all, treat it as an exploratory contrast and not as evidence that the industry binary captures risk-disclosure writing burden.

## Classification Rule

`HighRiskDiscIndustry = 1`:

- CSRC level-1 `J` finance, `K` real estate, `B` mining, `D` utilities, and `I` information transmission/software/IT services;
- CSRC manufacturing subclasses `C25`, `C26`, and `C27`;
- CSRC transportation subclasses `G55` water transport and `G56` air transport, also captured by names containing water or air transport.

`HighRiskDiscIndustry = 0`:

- CSRC level-1 `A`, `F`, `H`, `O`, and `R`.

Excluded:

- remaining manufacturing, construction, business services, scientific services, environmental/public facilities, education, health/social work, comprehensive, and missing-industry firms.

Industry exposure is anchored on the latest available pre-2022 listing-company industry record. Firms without a pre-2022 record use their earliest post-2021 fallback industry and are flagged in `industry_anchor_source`.

## Data Sources

- Firm-year sample frame: annual reports in `iar_rept.parquet`, `Reptyp == 4`, years 2018-2025.
- Industry classification: `stk_listcoinfo.parquet`, using `IndustryCodeD` first, then `IndustryCodeC`, then `IndustryCode`.
- Pre-period risk burden validation: `existing_literature_y_specificity_similarity_2015_2025.parquet`, using firm-level 2018-2021 mean `risk_chars`.

## Validation: High vs Low Risk-disclosure Industries

Firm-level pre-period risk length, non-ST/PT firms with available 2018-2021 risk text:

| Metric | Value |
|---|---:|
| High group firms | 1,232 |
| Low group firms | 284 |
| High mean pre risk length | 468.7 |
| Low mean pre risk length | 456.6 |
| High median pre risk length | 335.2 |
| Low median pre risk length | 332.8 |
| Welch t-stat | 0.269 |
| Welch p-value | 0.7879 |
| Correlation: industry 0/1 vs mean risk length | 0.004 |

Completion checks:

- Sample-size check: PASS.
- High-group mean greater than low-group mean: PASS.
- Difference statistically significant at 5%: FAIL.
- Correlation in target 0.3-0.6 range: FLAG.

Interpretation: the high-risk industry binary has usable treatment/control sample sizes, but it does not pass the core data-driven validation. It is too weakly related to continuous pre-period risk-disclosure length to be sold as a persuasive 0/1 version of `PreRiskWritingBurden_i`.

## Risk-length Distribution by Binary Group

|   HighRiskDiscIndustry |   count |    mean |   median |      std |   min |   max |
|-----------------------:|--------:|--------:|---------:|---------:|------:|------:|
|                      0 |     284 | 456.625 |   332.75 |  482.143 |     0 |  4034 |
|                      1 |    1232 | 468.714 |   335.25 | 1216.15  |     0 | 38591 |

## Industry-level Summary

Detailed rows are grouped by CSRC detailed code because manufacturing and transportation have subclass exceptions.

| csrc_l1_code   | csrc_l1_name                     | csrc_code   | csrc_name                                |   n_firms |   mean_risk_length_pre |   HighRiskDiscIndustry |
|:---------------|:---------------------------------|:------------|:-----------------------------------------|----------:|-----------------------:|-----------------------:|
| A              | 农、林、牧、渔业                 | A01         | 农业                                     |        17 |                431.191 |                      0 |
| A              | 农、林、牧、渔业                 | A02         | 林业                                     |         3 |                368.417 |                      0 |
| A              | 农、林、牧、渔业                 | A03         | 畜牧业                                   |        17 |                844.108 |                      0 |
| A              | 农、林、牧、渔业                 | A04         | 渔业                                     |         6 |                279.5   |                      0 |
| A              | 农、林、牧、渔业                 | A05         | 农、林、牧、渔专业及辅助性活动           |         1 |                  0     |                      0 |
| F              | 批发和零售业                     | F51         | 批发业                                   |        79 |                512.051 |                      0 |
| F              | 批发和零售业                     | F52         | 零售业                                   |        95 |                436.454 |                      0 |
| H              | 住宿和餐饮业                     | H61         | 住宿业                                   |         6 |                359.625 |                      0 |
| H              | 住宿和餐饮业                     | H62         | 餐饮业                                   |         3 |                396.25  |                      0 |
| O              | 居民服务、修理和其他服务业       | O81         | 机动车、电子产品和日用产品修理业         |         1 |                310.5   |                      0 |
| R              | 文化、体育和娱乐业               | R86         | 新闻和出版业                             |        23 |                364.457 |                      0 |
| R              | 文化、体育和娱乐业               | R87         | 广播、电视、电影和录音制作业             |        23 |                380.736 |                      0 |
| R              | 文化、体育和娱乐业               | R88         | 文化艺术业                               |         8 |                268.031 |                      0 |
| R              | 文化、体育和娱乐业               | R89         | 体育                                     |         2 |                181.625 |                      0 |
| B              | 采矿业                           | B06         | 煤炭开采和洗选业                         |        23 |                479.902 |                      1 |
| B              | 采矿业                           | B07         | 石油和天然气开采业                       |         7 |               1912.69  |                      1 |
| B              | 采矿业                           | B08         | 黑色金属矿采选业                         |         3 |                259     |                      1 |
| B              | 采矿业                           | B09         | 有色金属矿采选业                         |        23 |                790.873 |                      1 |
| B              | 采矿业                           | B10         | 非金属矿采选业                           |         1 |                461.25  |                      1 |
| B              | 采矿业                           | B11         | 开采专业及辅助性活动                     |        15 |                620.45  |                      1 |
| C              | 制造业                           | C25         | 石油、煤炭及其他燃料加工业               |        15 |                358.083 |                      1 |
| C              | 制造业                           | C26         | 化学原料和化学制品制造业                 |       264 |                558.714 |                      1 |
| C              | 制造业                           | C27         | 医药制造业                               |       261 |                435.1   |                      1 |
| D              | 电力、热力、燃气及水生产和供应业 | D44         | 电力、热力生产和供应业                   |        73 |                468.315 |                      1 |
| D              | 电力、热力、燃气及水生产和供应业 | D45         | 燃气生产和供应业                         |        28 |                351.048 |                      1 |
| D              | 电力、热力、燃气及水生产和供应业 | D46         | 水的生产和供应业                         |        17 |                518.147 |                      1 |
| G              | 交通运输、仓储和邮政业           | G55         | 水上运输业                               |        29 |                410.586 |                      1 |
| G              | 交通运输、仓储和邮政业           | G56         | 航空运输业                               |        12 |                469.125 |                      1 |
| I              | 信息传输、软件和信息技术服务业   | I63         | 电信、广播电视和卫星传输服务             |        17 |                498.25  |                      1 |
| I              | 信息传输、软件和信息技术服务业   | I64         | 互联网和相关服务                         |        66 |                464.095 |                      1 |
| I              | 信息传输、软件和信息技术服务业   | I65         | 软件和信息技术服务业                     |       258 |                387.109 |                      1 |
| J              | 金融业                           | J66         | 货币金融服务                             |         1 |                920.5   |                      1 |
| J              | 金融业                           | J67         | 资本市场服务                             |         3 |                330.167 |                      1 |
| J              | 金融业                           | J69         | 其他金融业                               |         6 |                387.333 |                      1 |
| K              | 房地产业                         | K70         | 房地产业                                 |       110 |                402.635 |                      1 |
| C              | 制造业                           | C13         | 农副食品加工业                           |        50 |                703.29  |                    nan |
| C              | 制造业                           | C14         | 食品制造业                               |        60 |                736.265 |                    nan |
| C              | 制造业                           | C15         | 酒、饮料和精制茶制造业                   |        42 |                385.726 |                    nan |
| C              | 制造业                           | C17         | 纺织业                                   |        43 |                353.733 |                    nan |
| C              | 制造业                           | C18         | 纺织服装、服饰业                         |        38 |                534.197 |                    nan |
| C              | 制造业                           | C19         | 皮革、毛皮、羽毛及其制品和制鞋业         |        11 |                409.485 |                    nan |
| C              | 制造业                           | C20         | 木材加工和木、竹、藤、棕、草制品业       |         6 |                334     |                    nan |
| C              | 制造业                           | C21         | 家具制造业                               |        24 |                358.924 |                    nan |
| C              | 制造业                           | C22         | 造纸和纸制品业                           |        34 |                334.647 |                    nan |
| C              | 制造业                           | C23         | 印刷和记录媒介复制业                     |        14 |                288.708 |                    nan |
| C              | 制造业                           | C24         | 文教、工美、体育和娱乐用品制造业         |        20 |                344.688 |                    nan |
| C              | 制造业                           | C28         | 化学纤维制造业                           |        26 |                332.769 |                    nan |
| C              | 制造业                           | C29         | 橡胶和塑料制品业                         |        93 |                365.318 |                    nan |
| C              | 制造业                           | C30         | 非金属矿物制品业                         |        96 |                491.338 |                    nan |
| C              | 制造业                           | C31         | 黑色金属冶炼和压延加工业                 |        29 |                482.428 |                    nan |
| C              | 制造业                           | C32         | 有色金属冶炼和压延加工业                 |        77 |                413.587 |                    nan |
| C              | 制造业                           | C33         | 金属制品业                               |        76 |                357.433 |                    nan |
| C              | 制造业                           | C34         | 通用设备制造业                           |       144 |                366.764 |                    nan |
| C              | 制造业                           | C35         | 专用设备制造业                           |       274 |                425.245 |                    nan |
| C              | 制造业                           | C36         | 汽车制造业                               |       146 |                385.923 |                    nan |
| C              | 制造业                           | C37         | 铁路、船舶、航空航天和其他运输设备制造业 |        62 |                414.823 |                    nan |
| C              | 制造业                           | C38         | 电气机械和器材制造业                     |       260 |                374.889 |                    nan |
| C              | 制造业                           | C39         | 计算机、通信和其他电子设备制造业         |       429 |                405.18  |                    nan |
| C              | 制造业                           | C40         | 仪器仪表制造业                           |        63 |                346.831 |                    nan |
| C              | 制造业                           | C41         | 其他制造业                               |        18 |                363.588 |                    nan |
| C              | 制造业                           | C42         | 废弃资源综合利用业                       |         8 |                803.312 |                    nan |
| E              | 建筑业                           | E47         | 房屋建筑业                               |         2 |                884     |                    nan |
| E              | 建筑业                           | E48         | 土木工程建筑业                           |        68 |                570.268 |                    nan |
| E              | 建筑业                           | E49         | 建筑安装业                               |         2 |                513.75  |                    nan |
| E              | 建筑业                           | E50         | 建筑装饰、装修和其他建筑业               |        26 |                417.657 |                    nan |
| G              | 交通运输、仓储和邮政业           | G53         | 铁路运输业                               |         5 |                443.4   |                    nan |
| G              | 交通运输、仓储和邮政业           | G54         | 道路运输业                               |        34 |                571.669 |                    nan |
| G              | 交通运输、仓储和邮政业           | G58         | 多式联运和运输代理业                     |         8 |                546.177 |                    nan |
| G              | 交通运输、仓储和邮政业           | G59         | 装卸搬运和仓储业                         |         9 |                494.963 |                    nan |
| G              | 交通运输、仓储和邮政业           | G60         | 邮政业                                   |         5 |               1424.6   |                    nan |
| L              | 租赁和商务服务业                 | L71         | 租赁业                                   |         3 |               2241.67  |                    nan |
| L              | 租赁和商务服务业                 | L72         | 商务服务业                               |        57 |                448.465 |                    nan |
| M              | 科学研究和技术服务业             | M73         | 研究和试验发展                           |        12 |                297.708 |                    nan |
| M              | 科学研究和技术服务业             | M74         | 专业技术服务业                           |        50 |                512.4   |                    nan |
| M              | 科学研究和技术服务业             | M75         | 科技推广和应用服务业                     |         2 |                139.5   |                    nan |
| N              | 水利、环境和公共设施管理业       | N77         | 生态保护和环境治理业                     |        60 |                391.15  |                    nan |
| N              | 水利、环境和公共设施管理业       | N78         | 公共设施管理业                           |        17 |                217.961 |                    nan |
| P              | 教育                             | P83         | 教育                                     |        11 |                458.061 |                    nan |
| Q              | 卫生和社会工作                   | Q84         | 卫生                                     |        11 |                506.909 |                    nan |
| S              | 综合                             | S91         | 综合                                     |        13 |                377.667 |                    nan |

## Firm-year Sample Counts

|   year |   high_1 |   low_0 |   excluded_nan |
|-------:|---------:|--------:|---------------:|
|   2018 |     1202 |     274 |           2213 |
|   2019 |     1269 |     274 |           2350 |
|   2020 |     1403 |     290 |           2701 |
|   2021 |     1522 |     309 |           3021 |
|   2022 |     1608 |     315 |           3298 |
|   2023 |     1639 |     319 |           3481 |
|   2024 |     1645 |     309 |           3528 |
|   2025 |      497 |      76 |           1019 |

## Main Continuous vs Binary Exposure Compatibility

The current binary exposure is compared against firm-level mean pre-period risk-disclosure length, a direct continuous proxy for `PreRiskWritingBurden_i`.

- Correlation with continuous pre-period risk length: `0.004`.
- High group internal mean: `468.7`.
- Low group internal mean: `456.6`.

This is not a DID result. It only checks whether the industry binary carries a plausible pre-period risk-writing-burden signal.

## Caveats

1. Manufacturing exclusions are substantial by design. The rule keeps only `C25`, `C26`, and `C27` as high-risk manufacturing and leaves the rest as middle/excluded.
2. Finance is included in the high-risk group because it is naturally risk-disclosure intensive, but journal reviewers may object that finance follows sector-specific accounting and regulatory regimes. A non-financial-only robustness version may be needed.
3. 2022 reports should remain transition-period sensitive, consistent with the main T05 design. This file only constructs exposure and does not decide the regression window.
4. Firms without a pre-period risk-text record are kept in the panel but `in_sample = 0`.
5. The variable is intended as a robustness contrast for continuous exposure DID, not as proof that identification is valid.

## Open Questions

1. Should the final robustness table exclude finance entirely after using finance in the validation step?
2. Should the industry binary be crossed with `PostGenAI` directly, or used only as a split-sample check around the continuous `PreRiskWritingBurden_i`?
3. Should the post-2021 fallback industry firms be excluded from the regression sample to keep exposure strictly pre-determined?
