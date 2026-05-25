# v6 补充检验：market-model CAR 与 placebo peers

日期：2026-05-24

## 1. 本次补充什么

针对 v6 简化主效应，本次补两类最关键检验：

```text
1. 把 market-adjusted CAR 换成 rolling market-model CAR；
2. 构造低相似度同行 / 随机同行 placebo peers。
```

主效应仍然保持简化设定：

```text
Specificity_z × AIActivePeer -> Peer CAR
```

其中 `ProductSimilarity` 只用于定义 Top5 / Top10 产品市场近邻，不放进主交互。

## 2. market-model CAR 口径

日收益数据：

```text
CSMAR 日个股回报率，2021-05-24 至 2026-05-22
市场收益：上证综指 000001
```

市场模型：

```text
Ret_j,d = alpha_j,t + beta_j,t MarketRet_d + error_j,d
```

估计窗口：

```text
过去 200 个交易日，至少 120 个有效观测；
事件日前跳过 11 个交易日，避免事件信息污染估计窗口。
```

事件窗口：

```text
AR[0]
CAR[0,+1]
CAR[-1,+1]
```

回归：

```text
PeerCAR_ij,t = β Specificity_z_i,t × AIActivePeer_j,t-5
              + γ AIActivePeer_j,t-5
              + focal event FE
              + error
```

标准误：

```text
two-way clustered by focal event and peer firm
```

## 3. 样本覆盖

| peer_group | sample_name | top_n | obs | events | focal_firms | peer_firms | mean_ai_active | mean_car_0_p1_mm | mean_car_m1_p1_mm | mean_product_similarity |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| true_top5 | all_events | 5 | 86,320 | 20,097 | 2,648 | 4,115 | 0.5620 | -0.002549 | -0.003559 | 0.233675 |
| true_top5 | first_focal_event | 5 | 11,288 | 2,646 | 2,646 | 3,977 | 0.2600 | -0.000180 | -0.000091 | 0.234212 |
| true_top10 | all_events | 10 | 172,561 | 20,115 | 2,651 | 4,908 | 0.5521 | -0.002563 | -0.003585 | 0.208526 |
| true_top10 | first_focal_event | 10 | 22,545 | 2,651 | 2,651 | 4,791 | 0.2635 | -0.000499 | -0.000640 | 0.206227 |
| low_similarity_same_industry | first_focal_event | 10 | 19,198 | 2,598 | 2,598 | 2,843 | 0.2529 | -0.001573 | -0.001755 | 0.009680 |
| random_same_industry | first_focal_event | 10 | 20,073 | 2,598 | 2,598 | 4,658 | 0.2806 | -0.000864 | -0.000637 | 0.053914 |

## 4. market-model CAR 主结果

只展示首次披露样本，因为这是当前主设计。

核心项：

```text
Specificity_z × AIActivePeer
```

### True Top5 peers

| outcome | coef | p |
|---|---:|---:|
| CAR[0,+1] | -0.001825 | 0.0166 |
| CAR[-1,+1] | -0.001921 | 0.0496 |

加 `ProductSimilarity` 控制后：

| outcome | coef | p |
|---|---:|---:|
| CAR[0,+1] | -0.001822 | 0.0167 |
| CAR[-1,+1] | -0.001914 | 0.0503 |

读法：

```text
正式 market-model CAR 下，Top5 主结果仍成立。
幅度比 market-adjusted CAR 略小，但方向和显著性保留。
```

### True Top10 peers

| outcome | coef | p |
|---|---:|---:|
| CAR[0,+1] | -0.000969 | 0.0928 |
| CAR[-1,+1] | -0.001120 | 0.1121 |

加 `ProductSimilarity` 控制后：

| outcome | coef | p |
|---|---:|---:|
| CAR[0,+1] | -0.000958 | 0.0963 |
| CAR[-1,+1] | -0.001105 | 0.1168 |

读法：

```text
Top10 变成边际或不显著。
这符合“竞争威胁集中在最接近产品市场竞品”的解释，
但也意味着主表应优先使用 Top5，Top10 作为弱稳健性。
```

## 5. placebo peers

### 低相似度同行

在同一 `IndustryNameD` 内选择产品文本相似度最低的 peer。

| outcome | coef | p |
|---|---:|---:|
| CAR[0,+1] | 0.000109 | 0.828 |
| CAR[-1,+1] | 0.000208 | 0.750 |

读法：

```text
低相似度同行 placebo 完全不显著，且方向不再为负。
这是当前最有力的 placebo 支撑。
```

### 随机同行

在同一 `IndustryNameD` 内随机选择 peer。

| outcome | coef | p |
|---|---:|---:|
| CAR[0,+1] | -0.000390 | 0.478 |
| CAR[-1,+1] | -0.001077 | 0.083 |

读法：

```text
随机同行 CAR[0,+1] 不显著；
CAR[-1,+1] 有边际负向，说明行业日共同冲击仍可能存在。
这不是致命问题，但需要继续用 industry-week FE、随机抽样重复和竞品同日公告清洗处理。
```

## 6. 真近邻 vs placebo 差异检验

在首次披露样本中，把 true Top5 与 placebo peers 放进同一回归，检验：

```text
Specificity_z × AIActivePeer × TrueTop5
```

### True Top5 vs 低相似度同行

| outcome | coef | p |
|---|---:|---:|
| CAR[0,+1] | -0.001394 | 0.038 |
| CAR[-1,+1] | -0.001793 | 0.037 |

读法：

```text
真 Top5 近邻的负向效应显著强于低相似度同行。
这支持产品市场近邻竞争威胁解释。
```

### True Top5 vs 随机同行

| outcome | coef | p |
|---|---:|---:|
| CAR[0,+1] | -0.001157 | 0.091 |
| CAR[-1,+1] | -0.001258 | 0.129 |

读法：

```text
真 Top5 相对随机同行方向更负，但差异不够强。
后续需要对随机 placebo 做多次抽样均值，或加入更强的行业-周固定效应。
```

## 7. 当前判断

本轮补充后，v6 主线比昨天更稳：

```text
1. market-model CAR 下 Top5 主结果仍成立；
2. 低相似度同行 placebo 不成立；
3. 真 Top5 显著强于低相似度同行；
4. 随机同行 placebo 仍有一点边际负向，需要继续处理行业共同冲击。
```

目前可写的谨慎结论：

```text
在产品市场最接近的竞品中，
焦点公司首次 GenAI 披露越具体，
事前 AI-active 竞品出现更负面的短窗 market-model CAR；
这一效应不存在于低相似度同行。
```

## 8. 下一步

下一步优先级：

1. 加 `industry × week` 或 `calendar week` 固定效应，处理随机同行边际负向；
2. 多次随机 placebo 抽样，报告 placebo coefficient distribution；
3. 用 CAC / 招聘 / 专利 / 年报重构外部 `AIActivePeer`；
4. 清理 peer 自身同日重大公告；
5. 将同伴披露扩散作为机制表接在主表后。

输出目录：

```text
results/v6_supplement_market_model_placebo_20260524
```

关键文件：

- `true_peer_market_model_car_panel.csv`
- `placebo_peer_market_model_car_panel.csv`
- `placebo_peer_networks_low_random.csv`
- `v6_supplement_sample_summary.csv`
- `v6_supplement_regressions.csv`
- `v6_supplement_true_vs_placebo_difference.csv`
