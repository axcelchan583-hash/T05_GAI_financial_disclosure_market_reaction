# v6 主效应完整复核：HDFE 与多次随机 placebo

日期：2026-05-24

## 目的

这一轮只检验当前主线的市场反应主效应：

```text
焦点公司 GenAI 披露越具体，
事前已经 AI-active 的产品市场近邻竞品，
短窗 market-model CAR 是否更负？
```

对应主项：

```text
Specificity_z × AIActivePeer_{j,t-5}
```

这里 `ProductSimilarity` 不再作为三重交互的一层，而是用于定义产品市场近邻样本：

```text
true Top5 peers
true Top10 peers
```

这样可以避免三重交互过度绕，也更接近现在要讲的经济含义：具体 GenAI 披露是否构成对 AI-active 近邻竞品的竞争威胁信号。

## 数据与脚本

输入：

```text
results/v6_supplement_market_model_placebo_20260524/true_peer_market_model_car_panel.csv
results/v6_supplement_market_model_placebo_20260524/placebo_peer_market_model_car_panel.csv
results/v6_supplement_market_model_placebo_20260524/stock_returns_with_market_model_params.csv
results/v4_peer_spillover_x_pilot/v4_company_product_text_latest.csv
```

脚本：

```text
scripts/run_v6_main_effect_full_checks_20260524.py
```

输出：

```text
results/v6_main_effect_full_checks_20260524/v6_main_effect_core_hdfe_checks.csv
results/v6_main_effect_full_checks_20260524/v6_main_effect_repeated_random_placebo_draws.csv
results/v6_main_effect_full_checks_20260524/v6_main_effect_repeated_random_placebo_summary.csv
```

标准样本：

```text
每家公司首次 GenAI 披露事件
正常交易
无涨跌停
CAR[-1,+1] 三日收益完整
market-model alpha / beta 可估计
标准误双向聚类：event_id × peer_code
```

## 模型

基准模型：

```text
PeerCAR_{j,[0,+1] or [-1,+1]}
    = beta * Specificity_z_i,t × AIActivePeer_j,t-5
    + gamma * AIActivePeer_j,t-5
    + focal event FE
    + error
```

强化固定效应：

```text
focal event FE
+ peer industry × event week FE
```

这相当于进一步吸收同一周、同一竞品行业层面的 AI 概念波动。

## 核心结果

### 1. True Top5 产品市场近邻

| Outcome | FE | Coef. on `Specificity_z × AIActivePeer` | p-value | Obs. | Events | Peer firms |
|---|---:|---:|---:|---:|---:|---:|
| CAR[0,+1] | Event FE | -0.001825 | 0.0166 | 11,288 | 2,646 | 3,977 |
| CAR[-1,+1] | Event FE | -0.001921 | 0.0496 | 11,288 | 2,646 | 3,977 |
| CAR[0,+1] | Event FE + peer industry-week FE | -0.001513 | 0.0839 | 11,288 | 2,646 | 3,977 |
| CAR[-1,+1] | Event FE + peer industry-week FE | -0.001417 | 0.2261 | 11,288 | 2,646 | 3,977 |

读法：

```text
Top5 近邻中，CAR[0,+1] 是目前最稳的主窗口。
CAR[-1,+1] 在 event FE 下显著，但加入 peer industry-week FE 后明显变弱。
```

### 2. True Top10 产品市场近邻

| Outcome | FE | Coef. on `Specificity_z × AIActivePeer` | p-value | Obs. | Events | Peer firms |
|---|---:|---:|---:|---:|---:|---:|
| CAR[0,+1] | Event FE | -0.000969 | 0.0928 | 22,545 | 2,651 | 4,791 |
| CAR[-1,+1] | Event FE | -0.001120 | 0.1121 | 22,545 | 2,651 | 4,791 |
| CAR[0,+1] | Event FE + peer industry-week FE | -0.001285 | 0.0331 | 22,545 | 2,651 | 4,791 |
| CAR[-1,+1] | Event FE + peer industry-week FE | -0.001305 | 0.0788 | 22,545 | 2,651 | 4,791 |

读法：

```text
Top10 不是完全失败。
在更严格 peer industry-week FE 下，CAR[0,+1] 反而显著。
但是 Top10 的经济含义更松，主表仍应优先 Top5，Top10 放扩展样本。
```

### 3. 低相似度同行 placebo

| Outcome | FE | Coef. on `Specificity_z × AIActivePeer` | p-value | Obs. | Events | Peer firms |
|---|---:|---:|---:|---:|---:|---:|
| CAR[0,+1] | Event FE | 0.000109 | 0.8285 | 19,198 | 2,598 | 2,843 |
| CAR[-1,+1] | Event FE | 0.000208 | 0.7498 | 19,198 | 2,598 | 2,843 |
| CAR[0,+1] | Event FE + peer industry-week FE | 0.000109 | 0.8285 | 19,198 | 2,598 | 2,843 |
| CAR[-1,+1] | Event FE + peer industry-week FE | 0.000208 | 0.7498 | 19,198 | 2,598 | 2,843 |

读法：

```text
低相似度同行完全不成立。
这对“产品市场近邻竞争威胁”机制是有利的。
```

### 4. 单次随机同行 placebo

| Outcome | FE | Coef. on `Specificity_z × AIActivePeer` | p-value | Obs. | Events | Peer firms |
|---|---:|---:|---:|---:|---:|---:|
| CAR[0,+1] | Event FE | -0.000390 | 0.4778 | 20,073 | 2,598 | 4,658 |
| CAR[-1,+1] | Event FE | -0.001077 | 0.0832 | 20,073 | 2,598 | 4,658 |
| CAR[0,+1] | Event FE + peer industry-week FE | -0.000390 | 0.4778 | 20,073 | 2,598 | 4,658 |
| CAR[-1,+1] | Event FE + peer industry-week FE | -0.001077 | 0.0832 | 20,073 | 2,598 | 4,658 |

读法：

```text
单次随机 placebo 的 CAR[-1,+1] 有边际负向，不能只看一次随机抽样。
因此这一轮补了 100 次随机同行 placebo。
```

## 100 次随机同行 placebo

每次在同一行业内随机抽取 10 个非 true Top10 peer，重复估计同一个主项。

| Outcome | FE | Random mean coef. | Random p5 | Random median | Random p95 | True Top5 coef. | Share random <= true |
|---|---:|---:|---:|---:|---:|---:|---:|
| CAR[0,+1] | Event FE | -0.000131 | -0.000962 | -0.000160 | 0.000654 | -0.001825 | 0.00 |
| CAR[0,+1] | Event FE + peer industry-week FE | -0.000131 | -0.000962 | -0.000160 | 0.000654 | -0.001513 | 0.00 |
| CAR[-1,+1] | Event FE | -0.000173 | -0.001209 | -0.000130 | 0.000825 | -0.001921 | 0.00 |
| CAR[-1,+1] | Event FE + peer industry-week FE | -0.000173 | -0.001209 | -0.000130 | 0.000825 | -0.001417 | 0.01 |

读法：

```text
真 Top5 的负系数明显处在随机同业 placebo 分布的左尾之外。

CAR[0,+1]:
    100 次随机抽样中，没有一次比真 Top5 更负。

CAR[-1,+1]:
    event FE 下没有一次比真 Top5 更负；
    加 peer industry-week FE 后，只有 1% 的随机抽样比真 Top5 更负。
```

这说明当前主结果不是“随便抽一批同业也会出现同样负反应”。

## 当前判断

这一轮之后，主效应可以暂时保留，且最稳写法应收窄为：

```text
在每家公司首次 GenAI 披露事件中，
披露越具体，事前已经 AI-active 的 Top5 产品市场近邻竞品
在 [0,+1] 窗口出现更负的 market-model CAR。
```

不建议现在写成：

```text
所有竞品在 [-1,+1] 都显著下跌。
```

原因：

```text
1. 平均效应本来就会混合 category validation 与 competitive displacement；
2. [-1,+1] 在更严格 peer industry-week FE 下不稳；
3. Top10 可以支持方向，但不如 Top5 干净；
4. 当前 AIActivePeer 仍主要来自同一 CSMAR GenAI 事件库，需要补外部 pre-event AIActivePeer。
```

## 推荐主表结构

主表可以先这样排：

```text
Panel A: True product-market peers
    Top5, CAR[0,+1], Event FE
    Top5, CAR[0,+1], Event FE + peer industry-week FE
    Top10, CAR[0,+1], Event FE
    Top10, CAR[0,+1], Event FE + peer industry-week FE

Panel B: Placebo peers
    Low-similarity same-industry peers
    Random same-industry peers, one draw
    100 repeated random-placebo distribution

Panel C: Alternative window
    CAR[-1,+1]
```

## 下一步

最重要的不是再换题，而是把当前主效应的测量可信度补强：

1. 用外部数据重构 `AIActivePeer_{t-1}`：
   - CAC 生成式 AI 服务备案；
   - 深度合成算法备案；
   - 事前 AI 招聘；
   - 事前 AI / 大模型专利；
   - 事前年报 GenAI / AI 披露。
2. 清洗竞品自身同日重大公告：
   - 业绩预告；
   - 年报 / 季报；
   - 并购重组；
   - 股权激励；
   - 停复牌 / 监管问询。
3. 增加交易层面的信息含量结果：
   - abnormal turnover；
   - abnormal trading value；
   - abnormal volume。
4. 机制表保留：
   - 焦点 GenAI 披露后，产品市场近邻是否更快跟进 GenAI 披露。

如果以上补强后 `CAR[0,+1]` 的 Top5 结果仍能保留，这条主线值得继续。
