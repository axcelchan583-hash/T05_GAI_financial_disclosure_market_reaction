# Annual-Report Product-Market Peer Network

日期：2026-05-30

## 目的

本轮把旧的 CSMAR `MAINBUSSINESS + BusinessScope` 竞品网络升级为更接近
Hoberg and Phillips (2016, JPE) 的文本产品市场网络。核心思想保持一致：

```text
年度报告业务描述文本 -> firm text vector -> firm-pair cosine similarity -> TopK product-market peers
```

本文不能直接使用美国 TNIC 数据，因此采用 **Hoberg-Phillips-style Chinese A-share product-market peer network**。

## 与 Hoberg-Phillips 的对应

| 维度 | Hoberg and Phillips (2016) | 本项目当前实现 |
|---|---|---|
| 文本来源 | 10-K business descriptions | A 股年报业务/经营章节 TXT |
| 相似度单元 | firm-pair product-word cosine | firm-pair Chinese char 2-3 gram TF-IDF cosine |
| 同行定义 | firm-specific product-market peers | event-specific Top5/Top10 product-market peers |
| 时间口径 | 年度更新 | 按事件日期映射到已完成年报披露季的 fiscal year |
| 防 look-ahead | 使用当年可见 10-K | 事件在 5 月前用 t-2 年报，5 月后用 t-1 年报 |

## 当前数据覆盖

年报业务文本覆盖：

|   report_year |   firms |   mean_text_len |   section_rate |
|--------------:|--------:|----------------:|---------------:|
|          2021 |    4920 |         5926.12 |       0.997764 |
|          2022 |    5186 |         6049.68 |       0.994601 |
|          2023 |    5362 |         6163.5  |       0.999254 |
|          2024 |    5404 |         6458.3  |       0.999445 |
|          2025 |    5440 |         6777.05 |       0.999449 |

事件映射到的年报快照：

|   snapshot_report_year |   events |   focal_firms |
|-----------------------:|---------:|--------------:|
|                   2021 |     2348 |           834 |
|                   2022 |     5193 |           888 |
|                   2023 |     7113 |          2016 |
|                   2024 |     5170 |          1181 |
|                   2025 |      341 |           266 |

## 输出

输出目录：

```text
/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v12_annual_report_product_peers_20260530
```

主要文件：

- `annual_report_business_text_YYYY_YYYY.csv`
- `annual_report_peer_network_global_top10.csv`
- `annual_report_peer_event_global_top10.csv`
- `annual_report_peer_network_same_industry_d_top10.csv`
- `annual_report_peer_event_same_industry_d_top10.csv`
- `annual_report_peer_network_global_ai_stripped_top10.csv`
- `annual_report_peer_event_global_ai_stripped_top10.csv`
- `sample_summary.csv`
- `peer_network_overlap_summary.csv`
- `annual_report_same_industry_top5_examples.md`

## 当前限制

1. 中文文本不能逐字复刻英文 noun/proper noun 筛选，因此主口径使用 char 2-3 gram TF-IDF cosine。
2. 年报章节抽取是规则法；少数公司会退回到年报正文前段窗口，输出中用 `extracted_mode` 标记。
3. 2025 年报 TXT 文件名缺少实际披露日，当前只在保守 reporting-season cutoff 下使用。
4. 这一步只更新 peer network；后续主回归替换检验见
   `docs/empirical_runs/67_v12_annual_report_peer_main_effect_20260530.md`。

## 初步诊断

AI 词剔除前后的 annual-report global Top5 高度重合：

```text
mean overlap count  = 4.74 / 5
median overlap count = 5 / 5
mean Jaccard         = 0.915
```

这说明新产品市场网络不是单纯由“AI / 智能 / 算法 / 大模型”等词共同出现驱动。

新年报业务文本口径与旧 CSMAR 经营范围口径的 Top5 重合度较低：

```text
mean overlap count = 1.01 / 5
median overlap count = 1 / 5
mean Jaccard = 0.092
```

这说明两套 peer network 的实质信息不同。初始方法判断上，年报业务文本更接近
Hoberg-Phillips 的原始文本来源；但后续主回归替换检验显示，年报 Top5 网络没有复制旧
CSMAR 经营范围口径下的负向主效应。因此不能仅凭文献相似性把年报口径直接升为主口径。

同时，年报 global Top10 偶有模板语言导致的跨行业误配；同 `IndustryNameD` 内 Top5 / Top10
在人工抽查中更稳。但主效应替换检验未通过。后续写法应使用：

```text
Main candidate from existing results:
             CSMAR business-scope / main-business text Top5
Literature-aligned robustness:
             annual-report business text + same IndustryNameD Top5/Top10
             annual-report global Top10
             annual-report global AI-word-stripped Top10
```

该结果意味着：当前论文若继续写 peer-CAR 主线，必须承认 product-market peer measurement
是核心风险点，而不能把年报口径包装成已经验证成功的替代主口径。

## Summary

| item                                            |         value |
|:------------------------------------------------|--------------:|
| annual_report_text_rows                         |  26312        |
| event_rows                                      |  20165        |
| event_firms                                     |   2665        |
| network_global_rows                             |  50390        |
| network_global_focal_firms                      |   2611        |
| network_global_peer_firms                       |   4711        |
| network_global_mean_similarity                  |      0.375934 |
| network_global_median_similarity                |      0.362199 |
| network_global_same_industry_d_rate             |      0.458782 |
| event_global_rows                               | 197540        |
| event_global_events                             |  19754        |
| event_global_focal_firms                        |   2611        |
| event_global_peer_firms                         |   4711        |
| event_global_mean_similarity                    |      0.381809 |
| event_global_median_similarity                  |      0.372611 |
| event_global_same_industry_d_rate               |      0.495545 |
| network_same_industry_d_rows                    |  49926        |
| network_same_industry_d_focal_firms             |   2610        |
| network_same_industry_d_peer_firms              |   4824        |
| network_same_industry_d_mean_similarity         |      0.340208 |
| network_same_industry_d_median_similarity       |      0.335277 |
| network_same_industry_d_same_industry_d_rate    |      0.999419 |
| event_same_industry_d_rows                      | 196369        |
| event_same_industry_d_events                    |  19740        |
| event_same_industry_d_focal_firms               |   2610        |
| event_same_industry_d_peer_firms                |   4824        |
| event_same_industry_d_mean_similarity           |      0.350365 |
| event_same_industry_d_median_similarity         |      0.349286 |
| event_same_industry_d_same_industry_d_rate      |      0.999801 |
| network_global_ai_stripped_rows                 |  50390        |
| network_global_ai_stripped_focal_firms          |   2611        |
| network_global_ai_stripped_peer_firms           |   4719        |
| network_global_ai_stripped_mean_similarity      |      0.374891 |
| network_global_ai_stripped_median_similarity    |      0.360111 |
| network_global_ai_stripped_same_industry_d_rate |      0.456539 |
| event_global_ai_stripped_rows                   | 197540        |
| event_global_ai_stripped_events                 |  19754        |
| event_global_ai_stripped_focal_firms            |   2611        |
| event_global_ai_stripped_peer_firms             |   4719        |
| event_global_ai_stripped_mean_similarity        |      0.379984 |
| event_global_ai_stripped_median_similarity      |      0.369476 |
| event_global_ai_stripped_same_industry_d_rate   |      0.494761 |
