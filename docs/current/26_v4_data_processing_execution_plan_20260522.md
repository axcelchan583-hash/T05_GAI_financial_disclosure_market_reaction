# v4 数据处理执行计划：GenAI 披露的产品市场同业溢出

日期：2026-05-22

## 当前判断

这条线可以继续。当前主效应方向为负，和“竞争威胁”机制一致；题材也有现实性和发表空间。现在不应继续围绕选题本身反复摇摆，下一步要把重点转到数据质量和信噪比。

当前试跑只说明一件事：方向有线索，但数据版本还太粗，不能据此判断主效应不存在。试跑的主要噪声来自四处：

1. 事件源是互动平台回复，信息强度弱于正式公告和新闻稿。
2. 当前 Y 使用 Sina 临时行情和 `CAR[-1,+1]`，还不是正式 CSMAR 事件研究版本。
3. 当前同业关系来自 CSMAR `MAINBUSSINESS + BusinessScope` 的最新公司信息，尚未使用年度报告业务文本，也存在潜在时间错配。
4. 当前没有系统清理同日重大事项、ST、涨跌停、停牌、同行自己披露 GenAI 等干扰。

## 最终主线

```text
主 X：
    GenAIDisclosureSpecificity_it × ProductMarketSimilarity_ij

主 Y：
    Peer abnormal return around focal firm i's GenAI disclosure event

主机制：
    更具体的 GenAI 披露提高焦点公司 GenAI 应用可信度；
    对产品市场相近的同业公司，市场可能将其理解为竞争威胁。
```

## 数据处理优先级

### P0：先把事件研究 Y 做成正式版本

当前试跑使用 Sina K-line，只适合验证方向。正式版本应改成 CSMAR 日个股交易数据。

本地可用数据：

- `/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/上市公司财务信息/_daily_2021_2026/TRD_Dalyr*.xlsx`
- `/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/上市公司财务信息/_idx_batch*/IDX_Idxtrd*.xlsx`

处理规则：

- 股票日收益：优先使用 `Dretwd`，同时保留 `Dretnd` 和 `ChangeRatio` 做稳健性。
- 市场指数：先用上证指数 `000001`，后续可换为全市场指数或分市场指数。
- 市场范围：主样本保留沪深 A 股、创业板、科创板；北交所先排除或单独稳健性。
- 交易状态：主样本保留 `Trdsta == 1`，ST、*ST、N、停牌等先排除。
- 涨跌停：主样本排除事件窗口内 `LimitStatus != 0` 的 peer-event。
- 估计窗口：`[-210, -11]` 交易日。
- 主要窗口：先跑 `AR[0]`，再跑 `CAR[0,+1]` 和 `CAR[-1,+1]`。
- 事件日调整：
  - 交易日 15:00 前回复：当天为事件交易日；
  - 15:00 后回复、周末、节假日：下一交易日为事件交易日。

优先输出：

- `peer_ar0`
- `peer_car_0_p1`
- `peer_car_m1_p1`
- `peer_abs_ar0`
- `estimation_obs`
- `event_window_trading_status_flag`
- `limit_status_flag`

### P1：重做产品市场同业关系

当前同业网络来自 CSMAR 公司简介字段，只能作为 pilot。正式版本要改成年度业务文本。

当前可用过渡数据：

- `/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/v4_peer_spillover_x_pilot/v4_company_product_text_latest.csv`

正式目标：

- 用年度报告中的业务概述、主营业务、产品与服务、核心竞争力等章节构造 firm-year 产品文本。
- 对事件发生在年份 `t` 的披露，使用 `t-1` 或最近一期已披露年报文本构造同业关系，避免 look-ahead。
- 文本相似度先沿用中文 char 2-4 gram TF-IDF cosine；后续可加句向量稳健性。
- 主样本 peer：
  - same `IndustryNameD` 内 Top 3 或 Top 5；
  - 全市场高相似度 peer 作为稳健性；
  - 低相似度同行作为 placebo。

需要输出：

- `focal_code`
- `peer_code`
- `peer_rank`
- `product_similarity`
- `product_similarity_decile`
- `same_industry_d`
- `text_year_used`
- `text_source`

### P2：清理和分层事件样本

当前互动平台严格样本：

- answer-level：590
- firm-day：402
- focal firm：222

本地已有事件文件：

- `/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/plan_a_irqa_multichannel_event_study/plan_a_irqa_strict_answer_level_events.csv`
- `/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/plan_a_irqa_multichannel_event_study/plan_a_irqa_strict_firm_day_events.csv`

处理规则：

- 主事件仍使用“公司回复文本本身包含 GenAI 词”的严格口径。
- 同一公司同一日多条回复合并为 firm-day event。
- 保留 answer-level 作为具体性和文本分类来源。
- 分层标记：
  - `event_source`: 互动平台 / 正式公告 / 投资者关系活动记录 / 年报；
  - `is_first_genai_disclosure_by_firm`;
  - `is_product_oriented`;
  - `is_process_oriented`;
  - `has_customer_or_contract`;
  - `has_product_or_model_name`;
  - `has_monetary_amount`;
  - `has_partner`;
  - `has_timeline`;
  - `has_deployment_or_operation_status`。

当前巨潮正式公告候选只有约 20 个具体候选，不足以单独做主样本，但可作为强事件子样本或人工校验集。

### P3：干扰事件清理

这一步很可能比简单扩样更重要。产品市场同业反应本来就弱，若同日有财报、并购、再融资、重大合同、监管、停复牌，噪声会直接淹没结果。

主清理对象：

- focal firm 同日重大公告；
- peer firm 事件窗口内重大公告；
- peer firm 自己在此前或同窗口披露 GenAI；
- 财报披露日；
- 并购重组、重大资产交易；
- 再融资、股权激励、可转债、回购；
- 监管问询、处罚、诉讼；
- 涨跌停、ST、停牌、上市初期。

最低可执行版本：

- 先用 CSMAR 日交易状态排除 ST、停牌、涨跌停。
- 再用本地巨潮公告标题文本做关键词清理。
- 清理窗口先用 `[-1,+1]`，稳健性用 `[-2,+1]`。

### P4：做机制分组，而不是只赌平均主效应

平均效应可能混合两个方向：

```text
竞争威胁：产品越相似，peer CAR 越低。
行业机会：同赛道被重新估值，peer CAR 越高。
```

所以主效应为负但不显著并不意外。更应该优先处理异质性：

主机制分组：

- `LowPeerAICapability`：披露前没有 GenAI 相关公告、互动回复、CAC 备案、AI 专利或 AI 招聘证据的 peer。
- `HighPeerAICapability`：披露前已有上述证据的 peer。

优先假设：

```text
Specificity_it × ProductSimilarity_ij × LowPeerAICapability_jt < 0
```

经济解释：

产品相近但 AI 能力弱的同业，最容易被市场理解为被替代或被竞争挤压；产品相近且已有 AI 能力的同业，则可能同时获得行业机会重估。

## 下一批应跑的表

### Table 0：样本覆盖和清理漏斗

目的：说明每一步处理到底损失多少样本。

行：

1. strict IR firm-day events
2. matched to product peer network
3. matched to CSMAR daily returns
4. non-ST and normal trading
5. no limit-up / limit-down in event window
6. sufficient estimation-window observations
7. no major peer/focal confounding announcements

列：

- events
- focal firms
- peer-event observations
- peer firms

### Table 1：同业平均反应检验

先不要直接上复杂回归，先看事件层面有没有反应。

结果：

- Top 1 peer `AR[0]`
- Top 3 peer portfolio `AR[0]`
- Top 5 peer portfolio `AR[0]`
- Top 3 high-similarity minus low-similarity peer spread

检验：

- mean t-test
- Wilcoxon signed-rank
- sign test

### Table 2：主回归

主规格：

```text
PeerAR0_ijt =
    beta * Specificity_it × ProductSimilarity_ij
  + controls
  + Event FE
  + error_ijt
```

核心变体：

- `AR[0]`
- `CAR[0,+1]`
- `CAR[-1,+1]`
- Top 3 peer
- Top 5 peer
- high-similarity threshold peer

### Table 3：AI 能力异质性

```text
PeerAR0_ijt =
    beta1 * Specificity_it × ProductSimilarity_ij
  + beta2 * Specificity_it × ProductSimilarity_ij × LowPeerAICapability_jt
  + controls
  + Event FE
  + error_ijt
```

核心判断：

- 如果 `beta2 < 0` 且显著，这条线就很有价值。
- 如果主效应不显著但 `beta2` 显著，可以把论文主叙事改成“竞争威胁取决于 peer 的既有 AI 能力”。

## 立即执行顺序

1. 把 CSMAR 日个股交易和指数数据转成干净 panel，替换 Sina 结果。
2. 先重跑 `AR[0]`、`CAR[0,+1]`、`CAR[-1,+1]` 三个窗口。
3. 加入 ST、停牌、涨跌停过滤。
4. 把 Top 5 改成 Top 3 和 Top 1 portfolio spread 同步试。
5. 加入互动平台披露前的 peer GenAI 能力分组。
6. 再考虑用年报文本重做产品市场同业关系。

## 停止规则

如果完成 P0 到 P3 后，以下三类结果都没有方向一致的证据，应暂停这条线：

1. Top 1 / Top 3 peer 的 `AR[0]` 平均反应没有方向；
2. `Specificity × ProductSimilarity` 在 `AR[0]` 和 `CAR[0,+1]` 中方向不稳定；
3. `LowPeerAICapability` 三重交互没有更强负向结果。

如果出现以下结果，则继续投入：

1. `AR[0]` 比 `CAR[-1,+1]` 明显更强；
2. Top 1 / Top 3 peer 比 Top 5 更强；
3. 低 AI 能力 peer 的负向反应显著强于高 AI 能力 peer；
4. 排除涨跌停、ST 和重大公告后，系数绝对值上升或标准误下降。

## 当前结论

这条线的问题不是“没有价值”，而是当前数据版本还没有达到参考论文那种事件研究清洁度。下一步应停止抽象争论，优先做正式行情、事件日校准、交易状态过滤、干扰公告清理和 AI 能力异质性。
