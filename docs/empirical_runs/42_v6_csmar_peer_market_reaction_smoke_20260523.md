# v6 CSMAR 竞品市场反应主结果 smoke test

日期：2026-05-23

## 1. 目的

本次检验 v6 的主 Y：

```text
焦点公司 GenAI 披露
× 产品市场相似度
× 竞品事前 AI-active 状态
-> 竞品短窗资本市场反应
```

此前已经跑出“产品市场同伴披露扩散”机制，但那条线的 X 和 Y 都是文本披露，距离太近。本次改用外部资本市场结果作为主 Y。

## 2. 数据与口径

输入：

- `results/csmar_v5_1_response_smoke_20260523/csmar_conservative_focal_events_2023_2026.csv`
- `results/csmar_v5_1_response_smoke_20260523/csmar_product_peer_network_top10.csv`
- CSMAR 日个股回报率文件，2021-05-24 至 2026-05-22；
- CSMAR 上证综指 `000001` 日指数收益。

样本：

```text
event-peer obs before returns = 201,240
focal events = 20,124
peer firms = 5,251
```

事件窗口：

```text
AR[0]
CAR[0,+1]
CAR[-1,+1]
```

本次是快速 smoke test，使用市场调整收益：

```text
AbRet_j,d = Ret_j,d - MarketRet_d
```

尚未使用完整 market-model CAR。因此结果只用于方向判断。

`AIActivePeer_tminus5` 定义：

```text
竞品在焦点事件日前至少 5 天，是否已经在保守 CSMAR GenAI 事件库中出现过 GenAI 披露。
```

回归为 event fixed effects 的去均值 OLS，并报告：

```text
one-way event cluster
two-way event × peer cluster
```

本文档只展示更保守的 two-way event × peer cluster 结果。

## 3. 样本覆盖

| top_n | sample | obs | events | focal_firms | peer_firms | mean_ai_active_peer | mean_ar0 | mean_car_0_p1 | mean_car_m1_p1 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | raw | 100,620 | 20,124 | 2,652 | 4,447 | 0.5288 | 0.001179 | 0.001739 | 0.003361 |
| 5 | clean_m1_p1 | 88,020 | 20,099 | 2,649 | 4,136 | 0.5554 | -0.000151 | -0.000719 | -0.000445 |
| 10 | raw | 201,240 | 20,124 | 2,652 | 5,251 | 0.5185 | 0.001124 | 0.001665 | 0.003213 |
| 10 | clean_m1_p1 | 176,129 | 20,116 | 2,652 | 4,926 | 0.5451 | -0.000178 | -0.000777 | -0.000539 |

`clean_m1_p1` 要求 `CAR[-1,+1]` 三天完整、正常交易、无涨跌停。

## 4. 全部焦点事件：主结果

核心模型：

```text
PeerCAR = β1 ProductSimilarity
        + β2 AIActivePeer_tminus5
        + β3 ProductSimilarity × AIActivePeer_tminus5
        + focal event FE
```

### Top5 clean sample

| outcome | term | coef | p |
|---|---|---:|---:|
| AR[0] | ProductSimilarity × AIActivePeer | 0.000218 | 0.902 |
| CAR[0,+1] | ProductSimilarity × AIActivePeer | -0.000929 | 0.724 |
| CAR[-1,+1] | ProductSimilarity × AIActivePeer | -0.005899 | 0.073 |

读法：

```text
Top5 的 CAR[-1,+1] 出现边际负向信号；
Top10 不稳，说明如果有竞争重估，也更可能集中在非常近的产品市场竞品。
```

### 加入披露具体性后的 Top5 clean sample

核心项：

```text
Specificity × ProductSimilarity × AIActivePeer
```

| outcome | term | coef | p |
|---|---|---:|---:|
| AR[0] | Specificity × ProductSimilarity × AIActivePeer | -0.000598 | 0.035 |
| CAR[0,+1] | Specificity × ProductSimilarity × AIActivePeer | -0.000508 | 0.191 |
| CAR[-1,+1] | Specificity × ProductSimilarity × AIActivePeer | -0.000326 | 0.529 |

读法：

```text
全部事件样本中，具体性三重项只在 AR[0] 上有负向信号；
窗口拉长后不稳。
```

## 5. 每家公司首次 GenAI 披露：更干净的事件冲击

为了避免重复披露稀释，本次额外保留每个焦点公司最早的 GenAI 披露事件。

样本：

| top_n | sample | obs | events | focal_firms | peer_firms | mean_ai_active_peer | mean_ar0 | mean_car_0_p1 | mean_car_m1_p1 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | clean_m1_p1 | 11,589 | 2,647 | 2,647 | 4,046 | 0.2562 | 0.000851 | 0.001359 | 0.002947 |
| 10 | clean_m1_p1 | 23,176 | 2,652 | 2,652 | 4,854 | 0.2596 | 0.000698 | 0.000984 | 0.002433 |

### Specificity × Similarity × AI-active

| top_n | outcome | coef | p |
|---:|---|---:|---:|
| 5 | AR[0] | -0.000518 | 0.491 |
| 5 | CAR[0,+1] | -0.001924 | 0.032 |
| 5 | CAR[-1,+1] | -0.003057 | 0.022 |
| 10 | AR[0] | -0.000288 | 0.626 |
| 10 | CAR[0,+1] | -0.001208 | 0.142 |
| 10 | CAR[-1,+1] | -0.002390 | 0.033 |

读法：

```text
首次披露事件中，Specificity × ProductSimilarity × AIActivePeer 出现更清楚的负向信号。
这比“同伴披露扩散”更适合作主结果，因为 Y 是外部资本市场反应。
```

但要注意：

```text
ProductSimilarity × AIActivePeer 本身在首次披露样本中不显著；
当前更像是“具体 GenAI 披露触发 AI-active 近邻竞品负向重估”，
而不是“所有 GenAI 披露都会让 AI-active 竞品下跌”。
```

## 6. 暂定结论

这次 v6 smoke test 不能说已经稳了，但方向比预期更有价值：

```text
主结果候选：
    焦点公司首次 GenAI 披露越具体，
    产品市场越相似、且事前 AI-active 的竞品，
    短窗 CAR 越负。

机制表：
    焦点公司 GenAI 披露后，
    产品市场越相似的竞品越可能在后续 60/90/180 天内首次跟进 GenAI 披露。
```

因此，目前更合理的论文链条是：

```text
Specific GenAI disclosure
    -> competitive revaluation of AI-active product-market peers
    -> subsequent peer disclosure diffusion
```

## 7. 不能过度解读的地方

当前还不是正式结果，原因：

- 本次 CAR 是 market-adjusted CAR，不是完整 market-model CAR；
- CSMAR 事件日期没有精确回复时间，尚未处理盘后披露；
- AIActivePeer 目前来自同一 CSMAR GenAI 事件库，需要补专利、招聘、CAC、年报等外部 pre-event AI activity；
- 还没做低相似度 / 随机 peer placebo；
- 还没剔除竞品自身同日重大公告；
- 还没加入 industry × week 或 calendar-week 固定效应；
- 首次披露结果比全部事件更强，需要防止被解释为样本筛选。

## 8. 下一步

优先顺序：

1. 用 market-model CAR 复算 `AR[0]`、`CAR[0,+1]`、`CAR[-1,+1]`；
2. 对首次披露样本做低相似度 peer 和随机 peer placebo；
3. 用外部数据重构 `AIActivePeer_tminus5`；
4. 加入 calendar-week / industry-month 固定效应；
5. 把 `peer disclosure diffusion` 放到机制表，而不是主表。

输出目录：

```text
results/v6_csmar_peer_market_reaction_smoke_20260523
```

关键文件：

- `v6_peer_event_market_adjusted_car_panel.csv`
- `v6_peer_market_reaction_sample_summary.csv`
- `v6_peer_market_reaction_event_fe_regressions.csv`
- `v6_peer_market_reaction_sample_summary_first_focal.csv`
- `v6_peer_market_reaction_event_fe_regressions_first_focal.csv`
