# v5 研究设计：GenAI 具体披露、竞品真实 AI 投入与短期市场信号

日期：2026-05-22

## 0. 2026-05-22 数据审计后的状态修正

本文件提出的 v5 是候选扩展设计，不应直接视为当前唯一主线。

招聘数据已经确认存在，覆盖 2014-01-07 至 2026-03-10，约 899.6 万条招聘记录。但当前最干净的互动平台事件集中在 2026-02-24 至 2026-05-19，和“事件后招聘反应”严重错位。因此，当前 v4 事件库不能直接支持 `t+1:t+2` 或 `t+1:t+4` 的 future hiring Y。

更重要的是，即使扩展到更早事件，竞品未来招聘作为主 Y 也会面临强共同趋势问题：

```text
行业 AI 热潮、同一产品赛道技术升级、竞品自身既有 AI 计划，
都可能同时解释焦点公司具体披露和竞品后续 AI 招聘。
```

因此，当前更稳的处理是：

```text
招聘数据优先用于重构 pre-event AIActivePeer / prior AI capability；
不要立即把 rival future AI hiring 升级为主 Y。
```

详细审计见：

```text
docs/current/36_recruitment_data_and_v5_y_risk_audit_20260522.md
```

## 1. 为什么需要 v5

v4 的核心是：

```text
Specificity_it × ProductSimilarity_ij × AIActivePeer_j,t-
-> PeerCAR_jt[-1,+1]
```

这条线的优点是 X 和 Y 分属不同公司，避免了“公司自己披露、自己股价反应”的普通信息含量问题。但 go/no-go 诊断后，v4 也有三个明显弱点：

1. Top5 下三重交互只边际显著，Top10 扩样本后消失；
2. `AIActivePeer` 口径承载了太多解释压力；
3. 短窗 peer CAR 即使显著，也容易被追问“然后呢”。

因此，v5 不再把短窗竞品 CAR 作为最终主 Y，而是把它降级为短期市场信号。新的终点改成：

```text
竞品公司是否在披露冲击后增加真实 AI 能力投入。
```

这能接上 `24时间序列学习/bib/orgin/chat/1` 里的方法主线：

```text
短期信号 / surrogate
-> 异质性长期结果
-> targeting / policy-learning style evaluation
```

## 2. 核心研究问题

中文问题：

```text
当一家上市公司在交易所互动平台作出更具体的 GenAI 披露时，
与其产品市场越相似的竞品，
是否会在随后增加真实 AI 人力资本投入？

短窗市场反应是否能帮助识别哪些竞品会产生这种长期真实反应？
```

英文问题：

```text
Do specific GenAI disclosures by focal firms trigger real AI investment responses among their product-market rivals?
Can short-window market signals help identify which rival-event pairs translate into subsequent AI-skilled hiring?
```

## 3. 一句话版本

```text
Main X:
    focal firm GenAI disclosure specificity × product-market similarity

Main Y:
    rival firm's future AI-skilled hiring intensity

Short-term surrogate:
    rival CAR / turnover / investor attention around the focal disclosure
```

这个版本的关键区别是：

```text
X 是焦点公司的披露文本；
Y 是竞品公司的真实资源投入；
CAR 只是中间的市场早期信号，不再是最终结果。
```

因此它不是“公司说要做 AI，所以自己后来招 AI 人”，而是：

```text
一家公司的具体 GenAI 披露是否触发产品市场竞品的真实 AI 投入反应。
```

## 4. 主 X

主解释变量是：

```text
DisclosureShock_ijt = Specificity_it × ProductSimilarity_ij
```

其中：

### 4.1 Specificity_it

焦点公司 `i` 在事件日 `t` 的 GenAI 披露具体性。主样本仍优先使用交易所互动平台严格事件：

```text
公司回复文本本身包含 GenAI / 大模型 / AIGC / LLM 内容的 firm-day 事件。
```

测度沿用 Hope, Hu, and Lu (2016) 的 Level-of-Detail 思路，不做主观打分。中文实现可以统计 GenAI 相关句段中的：

- 组织名；
- 产品 / 模型 / 平台名；
- 合作方；
- 业务场景；
- 金额、百分比、时间、日期；
- 部门、客户类型、落地环节。

第一版可以继续用现有 Hope-style proxy，正式版再升级为中文 NER + 模型名 / 产品名字典。

### 4.2 ProductSimilarity_ij

焦点公司 `i` 与竞品公司 `j` 的产品市场相似度。当前可行版本使用国泰安主营业务 / 经营范围文本；正式版优先替换为事件日前一年年报业务章节：

```text
ProductSimilarity_ij,y-1 = cosine(TF-IDF_i, TF-IDF_j)
```

主口径：

```text
Top5 closest product-market rivals
```

Top10 只作为扩展和稳健性。v4 已经显示信号主要集中在 Top5，v5 应主动把理论写成 closest rivals，而不是 broad industry peers。

## 5. 主 Y

主被解释变量是竞品公司 `j` 在事件后若干季度的 AI-skilled hiring intensity。

首选测度：

```text
FutureAIHiring_j,t+1:t+4 =
    AI-related job postings of peer firm j
    / total job postings of peer firm j
```

或使用变化量：

```text
DeltaAIHiring_j,t+1:t+4 =
    mean(AIHiringShare_j,t+1:t+4)
  - mean(AIHiringShare_j,t-4:t-1)
```

文献锚点：

```text
Babina, Fedyk, He, and Hodson (2024, Journal of Financial Economics)
```

主 Y 必须使用 broad AI hiring，而不是一开始就做 GenAI-only hiring。原因是 broad AI hiring 更接近 Babina et al. 的原始测度，也更不容易被质疑为自造词表。GenAI-only hiring 可以放在稳健性或机制分析。

备选 Y：

- `log(1 + AI job postings)`，控制总招聘；
- `AI job postings / pre-event total employment proxy`；
- 后续 AI / GenAI 专利；
- 软著、CAC 备案、产品上线，作为外部验证或机制，不作为第一主 Y。

## 6. 短期 surrogate

v4 的竞品 CAR 不丢弃，而是改成短期 surrogate：

```text
ShortTermSignal_ijt:
    PeerCAR_jt[-1,+1]
    Peer abnormal turnover
    Peer attention / search / discussion signal if available
```

它回答的问题不是“这篇论文的最终 Y 是不是显著”，而是：

```text
市场在披露日附近对竞品的短期重估，
能否帮助识别哪些竞品随后会增加 AI 投入？
```

这对应 `Targeting for Long-Term Outcomes` 和 `Doing More with Less` 的基本思想：

```text
长期结果滞后、稀疏或观测不完整时，
短期信号可以作为长期反应的 surrogate / screening signal。
```

注意：这里的 targeting 不是企业真实干预，而是研究者、投资者或监管者对“哪些披露具有真实竞争影响”的识别策略。因此写作时要用 `screening` 或 `early signal`，不要夸张成真实部署的 managerial policy。

## 7. 主回归设计

样本单位：

```text
focal GenAI disclosure event i,t × product-market rival j
```

主模型：

```text
FutureAIHiring_j,t+1:t+4 =
    beta * Specificity_it × ProductSimilarity_ij
  + EventFE_it
  + PeerFE_j
  + PeerPreControls_j,t-
  + error_ijt
```

或使用变化量：

```text
DeltaAIHiring_j,t+1:t+4 =
    beta * Specificity_it × ProductSimilarity_ij
  + EventFE_it
  + PeerFE_j
  + error_ijt
```

解释：

- `EventFE_it` 吸收同一焦点披露事件当天的共同冲击；
- `PeerFE_j` 吸收竞品公司长期 AI 招聘倾向；
- 识别来自同一披露事件下，不同相似度竞品的后续 AI 投入差异，以及不同 specificity 事件对这种相似度梯度的放大；
- 标准误至少双向聚类到 event 和 peer firm。

核心假设：

```text
H1: beta > 0
```

中文表述：

```text
焦点公司的 GenAI 披露越具体，与其产品市场越相似的竞品越可能在随后增加 AI 人力资本投入。
```

英文表述：

```text
More specific GenAI disclosures by focal firms are followed by stronger AI-skilled hiring responses among closer product-market rivals.
```

## 8. Surrogate / targeting 检验

第二层分析不直接追求因果估计，而是验证短期市场信号是否具有长期筛选价值。

### 8.1 Surrogate validation

```text
DeltaAIHiring_j,t+1:t+4 =
    theta1 * DisclosureShock_ijt
  + theta2 * ShortTermSignal_ijt
  + theta3 * DisclosureShock_ijt × ShortTermSignal_ijt
  + EventFE_it
  + PeerFE_j
  + error_ijt
```

可检验：

- 负向 PeerCAR 是否预示后续 AI hiring catch-up；
- 高 abnormal turnover 是否预示披露更被市场当成竞争冲击；
- `Specificity × Similarity` 的长期效应是否集中在短期市场反应更强的 peer-event。

这里的 sign 需要谨慎：

```text
PeerCAR < 0:
    更像竞争威胁 / 被动追赶；

PeerCAR > 0:
    更像行业机会 / 技术扩散共同利好。
```

因此主分析可以同时报告 signed CAR 与 `abs(CAR)` / abnormal turnover，避免过早押单一解释。

### 8.2 Screening / policy value

把长期 AI hiring response 定义为：

```text
LongResponse_ijt = 1{
    DeltaAIHiring_j,t+1:t+4 is in top tercile
}
```

比较几种筛选规则：

1. 只按 `Specificity` 选；
2. 只按 `ProductSimilarity` 选；
3. 按 `Specificity × ProductSimilarity` 选；
4. 加入短期市场信号 `PeerCAR / turnover`；
5. 加入 prior AI capability / AIActivePeer。

评价指标：

```text
平均后续 AI hiring response
top-k hit rate
out-of-sample ranking performance
```

这部分对应 causal-ML 文献里的 policy learning / off-policy evaluation 精神，但第一版不用上复杂模型。可以先做透明的样本外排序和 top-k portfolio。

## 9. 数据窗口约束

这是 v5 的硬门槛。

招聘数据目前据称覆盖到：

```text
2014-2026.3
```

如果主 Y 使用事件后 4 个季度，则事件必须足够早：

```text
t + 4Q <= 2026Q1
```

也就是说，主样本不能只依赖 2026 年互动平台事件。当前 v4 的 2026 互动平台样本适合跑短窗 CAR，但不适合跑长期 AI hiring。

可执行策略：

1. 主 smoke test 先用 `t+1:t+2` 两季度窗口；
2. 正式版优先使用 2023-2025Q1 的 GenAI 事件；
3. 扩展事件来源：
   - 互动平台；
   - 上证 e 互动；
   - 巨潮公告；
   - 投资者关系活动记录；
   - 年报 GenAI 段落；
   - 官网 / 公众号产品发布。

如果不能获得足够早的 GenAI 事件，v5 就无法成立为长期 hiring paper，只能退回 v4 的资本市场短窗设计。

## 10. 识别风险与处理

### 10.1 焦点公司披露内生

公司可能在竞争格局变化时才披露 GenAI。处理：

- 加 `EventFE`，只比较同一事件下不同竞品；
- 控制竞品自身 pre-trend；
- 用 pseudo peers 做负控；
- 排除同日重大公告污染。

### 10.2 竞品本来就会招 AI 人

处理：

- 加 `PeerFE`；
- 控制 pre-event AI hiring share 和 AI hiring trend；
- 使用 `DeltaAIHiring`；
- 做 pre-event placebo：

```text
DeltaAIHiring_j,t-4:t-1
```

不应被未来 focal disclosure 解释。

### 10.3 X/Y 仍然太近

v5 的防守点是：

```text
X = 焦点公司的公开披露文本；
Y = 竞品公司的后续真实招聘行为。
```

这比“焦点公司披露 -> 焦点公司招聘”远得多。论文不能写成“披露兑现”，而要写成：

```text
competitive response / rival capability investment
```

### 10.4 招聘数据噪声

处理：

- broad AI hiring 为主；
- GenAI-only hiring 只做稳健性；
- 最低招聘量门槛；
- `log(1 + AI postings)` 与 share 双口径；
- 公司名称匹配人工抽查；
- 行业 × 季度固定效应或 peer 行业趋势。

## 11. 与 v4 的关系

v4 不废弃，但定位改变：

```text
v4:
    短窗资本市场重估 / market surrogate

v5:
    后续真实 AI 投入 / long-term real response
```

最理想的证据链是：

```text
Specific GenAI disclosure
-> Top5 closest rivals show stronger short-term market signal
-> those rivals subsequently increase AI-skilled hiring
```

如果第二步弱、第三步强，论文仍然可以写成真实竞争反应 paper。

如果第二步强、第三步弱，只能写资本市场短期重估，不能写真实能力反应。

如果第二步和第三步都弱，v5 不继续。

## 12. 最小可行试跑

第一轮不追求完整 causal ML，只做三张表。

### Table 1: 样本连接

```text
event-peer rows
matched peer hiring rows
events with t+1:t+2 coverage
events with t+1:t+4 coverage
unique focal firms
unique peer firms
```

### Table 2: 主回归 smoke test

```text
DeltaAIHiring_j,t+1:t+2 =
    beta * Specificity_it × ProductSimilarity_ij
  + EventFE
  + PeerFE
  + controls
```

同时跑：

- Top5；
- Top10；
- low-sim pseudo peers；
- non-AI hiring placebo。

### Table 3: short-term surrogate

```text
Does PeerCAR / turnover improve ranking of future AI hiring response?
```

先用分组均值和 top-k 排序即可，不急着上 causal forest / DML。

## 13. 当前 Go / No-Go 标准

继续 v5 的最低标准：

```text
1. t+1:t+2 hiring coverage 下至少 1,000 个有效 event-peer rows；
2. Specificity × ProductSimilarity 对 future AI hiring 的方向为正；
3. low-sim pseudo peers 或 non-AI hiring placebo 不出现同样模式；
4. 短期 CAR / turnover 至少能解释一部分 future response 的横截面。
```

如果第 2 条完全不成立，不要用 causal ML 硬救。那说明 GenAI 披露对竞品真实 AI 投入这条主线不通。

## 14. 暂定标题

英文：

```text
Do Specific GenAI Disclosures Trigger Rivals' Real AI Investment?
Evidence from Chinese Investor Interaction Platforms
```

中文：

```text
生成式 AI 具体披露会触发竞品真实 AI 投入吗？
来自互动平台、产品市场网络与招聘大数据的证据
```

更方法导向的英文副标题：

```text
Short-Term Market Signals and Long-Term Rival Responses
```

## 15. 结论

v5 比 v4 更值得认真试，因为它把研究终点从短窗市场波动推进到真实资源投入，并且自然连接到 causal ML / surrogate / targeting 文献。

但 v5 的数据要求也更高：

```text
必须补齐并匹配招聘数据；
必须有足够早的 GenAI 事件；
必须证明结果不是一般招聘扩张或行业热度。
```

当前建议：

```text
先跑最小 hiring smoke test。
如果 future AI hiring 方向有信号，再把短期 CAR 升级为 surrogate / screening 模块。
```
