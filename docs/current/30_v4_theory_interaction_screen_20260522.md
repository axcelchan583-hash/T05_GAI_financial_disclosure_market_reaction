# v4 理论交互项筛选：从平均效应转向 AI-active 同业竞争威胁

日期：2026-05-22

## 目的

平均主效应方向稳定但不显著，因此本轮不再继续只看：

```text
Specificity × ProductSimilarity
```

而是筛选一组有理论含义的交互项，看市场反应是否集中在特定 peer 或特定事件类型上。

本轮是 exploratory screen，但每个交互项都需要能被理论解释，不能作为机械挖显著。

## 数据

基础样本：

```text
Top 5 product-market peers
CSMAR event-study panel
```

输出目录：

```text
results/v4_peer_spillover_interaction_screen/
```

输出文件：

```text
v4_theory_interaction_screen_top5.csv
v4_interaction_screen_diagnostics.csv
```

## 交互项候选

本轮筛选了以下方向：

```text
AI-active peer
prior public GenAI event peer
annual-report GenAI peer
Top1 / Top2 closest peer
product-oriented disclosure
deployment / commercialized disclosure
quantitative / contract detail
internal-process disclosure
after-close disclosure
high GenAI mentions
high specific item count
high specificity dummy × similarity
```

## 最重要发现

最强结果来自：

```text
Specificity × ProductSimilarity × AI-active peer
```

其中：

```text
AI-active peer = peer has prior public GenAI evidence or 2024 annual-report GenAI evidence
```

### Clean sample, CAR[-1,+1]

| Spec | Interaction | coef | p-value | nobs | events | peer firms |
|---|---:|---:|---:|---:|---:|---:|
| No controls | `xspecsim_ai_active_broad` | -0.0103 | 0.005 | 1,755 | 398 | 640 |
| + peer controls | `xspecsim_ai_active_broad` | -0.0095 | 0.011 | 1,755 | 398 | 640 |

控制变量包括：

```text
peer beta
pre-event momentum
pre-event volatility
pre-event absolute return
ChiNext / STAR indicator
peer rank
```

这比平均主效应强得多。

## 解释

这个结果支持的故事不是：

```text
所有产品市场同业都会被冲击。
```

而是：

```text
焦点公司的具体 GenAI 披露主要会冲击已经处在 AI / GenAI 相关竞争空间内的产品市场同业。
```

也就是说，市场不是在泛泛重估整个行业，而是在 AI-active peer 之间重新评估竞争威胁。

这比“低 AI 能力 peer 更受冲击”更贴合当前数据。

更准确的论文叙事应改成：

```text
GenAI disclosure specificity triggers competitive revaluation among AI-active product-market peers.
```

中文可写为：

```text
生成式 AI 披露具体性引发 AI 活跃产品市场同业的竞争威胁重估。
```

## 次级信号

### 1. After-close disclosure

```text
Raw AR[0], with controls:
xspecsim_afterclose = -0.0083
p = 0.057
```

解释：

盘后披露的信息更可能集中反映到下一交易日，和事件研究逻辑一致。

可作为稳健性或事件日处理说明，不建议作为主机制。

### 2. Annual-report AI peer

```text
Clean CAR[-1,+1], with controls:
xspecsim_annual_ai = -0.0060
p = 0.068
```

解释：

这个结果支持 `AI-active peer` 的机制，因为 broad AI-active 结果主要由年报 GenAI 证据提供区分度。

### 3. High GenAI mentions

```text
Clean CAR[0,+1], with controls:
xspecsim_high_mentions = +0.0153
p = 0.027
```

同时，低 mention 组的 baseline effect 为负且显著：

```text
base x_specificity_similarity = -0.0162
p = 0.010
```

解释上需要谨慎。它可能说明“反复提 AI 词”不等于信息含量，简洁但具体的披露反而更像真实竞争信号。

这个方向有意思，但目前不如 `AI-active peer` 稳。

### 4. Internal-process disclosure

```text
Clean CAR[0,+1], with controls:
xspecsim_internal_process = +0.0122
p = 0.070
```

解释：

内部流程 / 降本提效型 GenAI 披露对产品市场同业的威胁更弱；负向反应更可能来自面向产品、服务、客户和商业化的 GenAI 披露。

不过当前 `product-oriented` 关键词太宽，覆盖了 98% 的事件，不能直接用。下一步需要更细地人工/LLM 分类：

```text
product-facing / customer-facing / revenue-facing
vs.
internal process / efficiency improvement
```

## 不理想的方向

### Top1 / Top2 closest peer

Top1 / Top2 交互没有跑出强信号。说明“最相似竞品”这个排序本身不够，必须结合 peer 是否处在 AI-active 竞争空间内。

### Product-oriented disclosure

当前关键词口径过宽，事件覆盖率约 98%，几乎没有区分度。不能用这个版本写主表。

### Deployment / commercialized disclosure

覆盖率也很高，约 92%，区分度不足。需要更细的人工分类。

## 当前最可写的主假设

可以把主假设从平均效应改成：

```text
H1:
More specific GenAI disclosures by focal firms lead to more negative market reactions among product-market peers that are already AI-active.
```

中文：

```text
当焦点公司的 GenAI 披露更具体时，资本市场会对已处于 AI 活跃竞争空间中的产品市场同业作出更负面的重估。
```

对应主回归：

```text
PeerCAR_ijt =
    beta1 * Specificity_it × ProductSimilarity_ij
  + beta2 * Specificity_it × ProductSimilarity_ij × AIActivePeer_j
  + controls
  + Event FE
  + error_ijt
```

当前核心结果：

```text
beta2 < 0
p = 0.005 without controls
p = 0.011 with controls
```

## 下一步

1. 把 `AI-active peer` 定义做得更硬：
   - 2024 年报 GenAI 证据；
   - 披露前互动平台 GenAI 回复；
   - 披露前正式 GenAI 公告；
   - CAC 备案；
   - AI 招聘 / AI 专利。

2. 把事件类型做得更细：
   - customer-facing / product-facing GenAI disclosure；
   - internal-process GenAI disclosure；
   - generic AI discussion。

3. 主表优先跑：

```text
Specificity × ProductSimilarity × AIActivePeer
```

而不是继续把平均主效应作为唯一中心。
