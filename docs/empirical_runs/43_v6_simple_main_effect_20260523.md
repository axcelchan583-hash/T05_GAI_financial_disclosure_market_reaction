# v6 简化主效应：Specificity × AIActivePeer

日期：2026-05-23

## 1. 为什么重跑

上一版 v6 主结果使用：

```text
Specificity × ProductSimilarity × AIActivePeer
```

这个设定虽然有信号，但解释上像“三个调节”。本次把产品市场相似度改为样本定义：

```text
Top5 / Top10 product-market peers
```

主交互只保留一个：

```text
Specificity × AIActivePeer
```

这样主问题更清楚：

```text
在产品市场近邻竞品中，
焦点公司 GenAI 披露越具体，
事前 AI-active 的竞品是否出现更负面的短窗市场反应？
```

## 2. 样本与变量

输入面板：

```text
results/v6_csmar_peer_market_reaction_smoke_20260523/v6_peer_event_market_adjusted_car_panel.csv
```

主样本：

- `Top5`: 产品市场文本相似度最高的 5 家竞品；
- `Top10`: 产品市场文本相似度最高的 10 家竞品；
- `clean_m1_p1`: `CAR[-1,+1]` 三天完整、正常交易、无涨跌停。

主变量：

```text
Specificity_z:
    焦点事件 GenAI 披露具体性，1/99 winsorize 后标准化。

AIActivePeer_tminus5:
    竞品在焦点事件日前至少 5 天，是否已在 CSMAR GenAI 披露事件库中出现过。

Main term:
    Specificity_z × AIActivePeer_tminus5
```

模型：

```text
PeerCAR_ij,t = β · Specificity_z_i,t × AIActivePeer_j,t-5
              + γ · AIActivePeer_j,t-5
              + focal event FE
              + ε
```

由于加入 focal event FE，`Specificity_z_i,t` 本身被事件固定效应吸收。

报告标准误：

```text
two-way clustered by focal event and peer firm
```

本次仍是 smoke test，Y 使用 market-adjusted return：

```text
AbRet_j,d = Ret_j,d - MarketRet_d
```

正式版本还需要 market-model CAR。

## 3. 样本覆盖

| sample_name | top_n | clean | obs | events | focal_firms | peer_firms | mean_ai_active | mean_specificity | mean_ar0 | mean_car_0_p1 | mean_car_m1_p1 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all_events | 5 | clean_m1_p1 | 88,020 | 20,099 | 2,649 | 4,136 | 0.5554 | 3.9250 | -0.000151 | -0.000719 | -0.000445 |
| all_events | 10 | clean_m1_p1 | 176,129 | 20,116 | 2,652 | 4,926 | 0.5451 | 3.9259 | -0.000178 | -0.000777 | -0.000539 |
| first_focal_event | 5 | clean_m1_p1 | 11,589 | 2,647 | 2,647 | 4,046 | 0.2562 | 4.3535 | 0.000851 | 0.001359 | 0.002947 |
| first_focal_event | 10 | clean_m1_p1 | 23,176 | 2,652 | 2,652 | 4,854 | 0.2596 | 4.3576 | 0.000698 | 0.000984 | 0.002433 |

## 4. 全部事件样本

核心项：

```text
Specificity_z × AIActivePeer
```

### Top5 clean

| outcome | coef | p |
|---|---:|---:|
| AR[0] | -0.000456 | 0.053 |
| CAR[0,+1] | -0.000386 | 0.242 |
| CAR[-1,+1] | -0.000364 | 0.397 |

### Top10 clean

| outcome | coef | p |
|---|---:|---:|
| AR[0] | -0.000163 | 0.305 |
| CAR[0,+1] | -0.000140 | 0.546 |
| CAR[-1,+1] | -0.000126 | 0.705 |

读法：

```text
全部事件样本中，负向方向存在，但窗口结果不稳。
这说明重复披露可能稀释了首次 GenAI 披露冲击。
```

## 5. 首次披露样本

每个焦点公司只保留最早一次 GenAI 披露事件。

### Top5 clean

| outcome | coef | p |
|---|---:|---:|
| AR[0] | -0.000746 | 0.193 |
| CAR[0,+1] | -0.001669 | 0.024 |
| CAR[-1,+1] | -0.002659 | 0.014 |

加 `ProductSimilarity` 控制后几乎不变：

| outcome | coef | p |
|---|---:|---:|
| AR[0] | -0.000746 | 0.192 |
| CAR[0,+1] | -0.001672 | 0.024 |
| CAR[-1,+1] | -0.002658 | 0.014 |

### Top10 clean

| outcome | coef | p |
|---|---:|---:|
| AR[0] | -0.000164 | 0.676 |
| CAR[0,+1] | -0.000841 | 0.142 |
| CAR[-1,+1] | -0.002113 | 0.041 |

加 `ProductSimilarity` 控制后：

| outcome | coef | p |
|---|---:|---:|
| AR[0] | -0.000157 | 0.687 |
| CAR[0,+1] | -0.000834 | 0.145 |
| CAR[-1,+1] | -0.002100 | 0.042 |

读法：

```text
主效应在首次披露样本中成立。
Top5 更强，Top10 的 CAR[-1,+1] 仍显著。
这比三重交互设定更适合作为论文主表。
```

## 6. 当前可写的主结论

目前最合适的表述是：

```text
在产品市场近邻竞品中，
焦点公司首次 GenAI 披露越具体，
事前 AI-active 竞品的短窗市场反应越负。
```

对应研究问题：

```text
Does specific GenAI disclosure trigger competitive revaluation among AI-active product-market peers?
```

这个版本比上一版更好：

- X/Y 距离更远：X 是焦点公司披露文本，Y 是竞品资本市场反应；
- 只有一个核心调节：`AIActivePeer`；
- `ProductSimilarity` 是 peer sample definition，不再作为主交互；
- 同伴披露扩散可以自然放到机制表。

## 7. 还不能声称的内容

现在还不能写成：

```text
所有 GenAI 披露都会导致竞品下跌。
```

也不能写成：

```text
全部事件样本都稳健显著。
```

更准确的是：

```text
首次 GenAI 披露的具体性，对事前 AI-active 的近邻竞品具有负向竞争重估效应。
```

## 8. 下一步

优先补四件事：

1. 用 market-model CAR 重算主表；
2. 做低相似度 peer / 随机 peer placebo；
3. 用外部数据重构 `AIActivePeer_tminus5`，例如 CAC、招聘、专利、年报；
4. 清理竞品自身同日重大公告。

输出目录：

```text
results/v6_simple_main_effect_20260523
```

关键文件：

- `v6_simple_main_effect_sample_summary.csv`
- `v6_simple_main_effect_regressions.csv`
