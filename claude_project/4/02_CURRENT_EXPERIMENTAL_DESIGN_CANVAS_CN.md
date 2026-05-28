# T05 当前完整实验设计：GenAI 披露具体性与产品市场同行重估

日期：2026-05-28

用途：给网页版 ChatGPT / Claude 画布讨论。本文档只保留当前主线，不纳入人工编码分支。

## 1. 一句话设计

本研究检验：中国上市公司更具体的 GenAI / 大模型 / AIGC 披露，是否会被资本市场解读为竞争风险信号，从而使事前已经具备 AI 活动证据的近产品市场同行，在短窗口内出现更负的相对市场重估。

最简模型：

```text
PeerCAR[0,+1] = beta * Specificity_z × AIActivePeer
              + event FE
              + peer industry-week FE
              + peer pre-window CAR controls
              + error
```

核心结论不是“所有同行下跌”，而是：

```text
同一个焦点 GenAI 披露事件内，
AI-active close peers 相对 non-AI-active close peers 的短窗 CAR 更负，
且这种差异随焦点披露 Specificity_z 更高而更强。
```

## 2. 理论故事

GenAI 披露对同行可以有两种方向相反的市场含义。

### 2.1 Category Validation

如果焦点公司披露 GenAI、算力、供应链、芯片、数据中心等内容，市场可能把它理解为整个 AI 需求或产业链景气被验证。这时同行未必下跌，甚至可能上涨。

预测：

```text
AI supply-chain / demand-exposure disclosure -> peers may have positive or zero CAR
```

### 2.2 Competitive-Risk Signal

如果焦点公司披露的是更具体的 GenAI 产品、应用场景、部署进度、客户方向、商业化路径或模型能力，市场更可能认为该公司具备可信 AI 战略承诺。这个信号对普通同行未必重要，但会冲击已经处于 AI 竞争空间、且产品市场接近的同行。

预测：

```text
Specific focal GenAI disclosure
    -> stronger competitive-risk signal
    -> AI-active close product-market peers have more negative PeerCAR[0,+1]
```

论文应围绕这个张力展开：GenAI 披露既可能验证赛道，也可能暴露竞争风险；负向重估只应集中在 AI-active 的近产品市场同行，而不是所有同行。

## 3. 研究问题与假设

### RQ

```text
Do specific GenAI disclosures by Chinese listed firms trigger negative short-window revaluation of AI-active close product-market peers?
```

### H1: Conditional Peer Revaluation

更具体的焦点 GenAI 披露，与 AI-active Top5 产品市场同行更负的短窗 CAR 相关。

### H2: Product-Market Proximity

负向重估应集中在最接近的产品市场同行。Top1-3 应强于 Top6-10，低相似同行和随机同业不应复现该结果。

### H3: External AI-Activeness

该结果不应只依赖历史披露文本定义的 AIActive。用事件前外部 AI 活动证据定义 AIActive，也应得到同方向结果。

### H4: Boundary: Category Validation

AI 供应链 / AI 需求暴露型披露不应产生同样的 `Specificity_z × AIActivePeer` 负向重估；它更可能对应 category validation。

## 4. 数据结构

### 4.1 观察单位

```text
focal GenAI disclosure event e × product-market peer firm j
```

### 4.2 主样本

```text
每家焦点公司首次 GenAI 披露事件 × Top5 产品市场同行
```

最终冻结样本：

```text
Rows: 7,805
Events: 2,177
Focal firms: 2,177
Peer firms: 3,345
Event window: 2023-01-01 to 2026-05-20
Announcement-cleaned: yes
Requires PeerCAR[-10,-2] and PeerCAR[-20,-2]: yes
Requires FocalCAR[0,+1]: yes
```

年度事件分布：

```text
2023: 866
2024: 211
2025: 1,051
2026: 49
```

## 5. 变量测度

### 5.1 Main Y

```text
PeerCAR[0,+1]
```

定义：产品市场同行在焦点 GenAI 披露交易日及下一交易日的 market-model abnormal return 加总。

为什么用 signed CAR 而不是 |CAR|：

```text
竞争风险机制有方向预测：AI-active close peers 应更负。
|CAR| 会把负向竞争重估和一般信息含量混在一起。
```

文献支撑：

- 短窗市场反应与信息含量：Beaver 1968；MacKinlay 1997；Kothari and Warner 2007。
- 同行业 / 同伴信息转移和竞争效应：Foster 1981；Lang and Stulz 1992。

### 5.2 Main X

```text
Specificity_z_e × AIActivePeer_{j,t-5}
```

`Specificity_z_e`：焦点 GenAI 披露文本的 objective text-detail / disclosure concreteness proxy。

当前写法边界：

```text
可以说：文本细节、披露具体化、信息密度。
不要说：真实 GenAI 落地具体性、真实能力、真实投资。
```

文献支撑：

- 披露具体性 / 文本细节：Hope, Hu and Lu 2016 的 disclosure specificity 思路。
- 技术披露具体性和 hype 辨别：Cheng et al. 2019 的 speculative / existing technology disclosure 思路可作为相邻框架。

### 5.3 AIActivePeer

主定义：

```text
ext_any =
    prior CAC filing
 OR prior broad-AI patent grant
 OR prior broad-AI hiring in previous 365 days
```

要求：所有组件都必须在事件 t-5 前可观察，避免 look-ahead。

解释：`ext_any` 是外部 AI 活动证据，不是精确 GenAI 能力测度。

文献支撑：

- AI hiring / AI-skilled labor demand：Babina et al. 2024。
- patent-based innovation / technology evidence：Kogan et al. 2017 提供专利价值框架；本研究这里只把 prior AI patent grant 作为外部 AI 活动证据。
- CAC 备案：制度性监管证据，无成熟会计金融主测度文献，作为中国 GenAI 服务外部可观察证据。

稳健性定义：

```text
current_text_history =
    peer firm had prior GenAI disclosure before event date t-5
```

注意：`current_text_history` 概念上贴近 GenAI 披露历史，但存在 pre-window negative pattern，所以只做 robustness，不做 headline。

### 5.4 Product-Market Peers

主样本使用 Top5 产品市场近邻。产品市场相似度基于中文业务描述文本构造，逻辑上对应 Hoberg and Phillips 的 text-based product market / TNIC 方法。

有效性防御：

```text
Top1-3 / Top4-5 / Top6-10 梯度
low-similarity peers placebo
random same-industry non-Top10 peers placebo
AI-word-stripped similarity
```

文献支撑：

- Hoberg and Phillips 2016：文本产品市场网络。
- peer / rival CAR 文献中使用产品市场同行识别竞争关系。

## 6. 基准回归

### 6.1 主规格

```text
PeerCAR_{e,j,[0,+1]}
  = beta_1 AIActivePeer_{j,t-5}
  + beta_2 Specificity_z_e × AIActivePeer_{j,t-5}
  + theta_1 PeerCAR_{j,[-10,-2]}
  + theta_2 PeerCAR_{j,[-20,-2]}
  + EventFE_e
  + PeerIndustryWeekFE_{j,t}
  + epsilon_{e,j}
```

推断：

```text
Two-way clustered by event_id and peer_code
```

### 6.2 识别含义

`event FE` 吸收焦点披露事件层面的全部平均冲击，包括焦点公司新闻、市场当天对该事件的平均反应、Specificity_z 的事件层面主效应。

因此 `beta_2` 的来源是：

```text
同一个焦点披露事件内，
AI-active peers 与 non-AI-active peers 的 CAR 差异；
并且这个差异是否随焦点披露 Specificity_z 更高而更负。
```

`peer industry-week FE` 进一步吸收同一周同一同行行业的市场波动。

`PeerCAR[-10,-2]` 和 `PeerCAR[-20,-2]` 控制同行事件前短期趋势。

这不是 IV，不是标准 DID，也不能写成强因果。最安全表述是：

```text
short-window peer-side market reassessment conditional on focal GenAI disclosure.
```

## 7. 已有主结果

### 7.1 Headline

样本：

```text
Top5 / first focal GenAI event / announcement-cleaned
PeerCAR[0,+1]
event FE + peer industry-week FE
PeerCAR[-10,-2] + PeerCAR[-20,-2]
two-way clustered by event_id and peer_code
```

结果：

```text
ext_any:
    coef = -0.002303
    p = 0.020

current_text_history:
    coef = -0.002275
    p = 0.027
```

经济量级：

```text
median total market-cap effect ≈ RMB -21.85 million
median float market-cap effect ≈ RMB -17.85 million
```

### 7.2 Focal Good-News / Pretrend Controls

加入焦点公司自身 CAR 和 `FocalCAR × AIActive` 后：

```text
ext_any / residualized Y + FocalCAR[0,+1] × AIActive:
    coef = -0.002300
    p = 0.020
```

解释：结果不是简单由焦点公司自身利好 / 利空程度驱动。

### 7.3 AI Theme Date-Shock Controls

加入 AI-theme abnormal return × AIActive 后：

```text
ext_any:
    coef = -0.002112
    p = 0.032
```

解释：结果不完全是 AI 主题交易日冲击。

## 8. 异质性与边界检验

### 8.1 Product-Market Proximity Gradient

```text
Top1-3 / ext_any:
    coef = -0.003252
    p = 0.016

Top6-10:
    not significant

low-similarity peers:
    not significant

random same-industry peers:
    not significant
```

解释：负向重估集中于最接近的产品市场同行，支持 competitive-risk signal，而不是一般行业共振。

### 8.2 AI-Word-Stripped Similarity

剔除 AI / AIGC / 大模型 / 智能 / 算法等词后重构产品相似度，Top5 结果仍为负并显著。

作用：反驳“产品相似度只是 AI 词共同出现导致”的质疑。

### 8.3 Disclosure-Type Horse Race

加入披露类型 × AIActive 后，主交互不被吸收：

```text
ext_any:
    Specificity_z × AIActive = -0.002394
    p = 0.015

current_text_history:
    Specificity_z × AIActive = -0.002107
    p = 0.045
```

解释：结果不是简单由某一种披露类型 dummy 吃掉。

### 8.4 AI Supply-Chain Boundary

供应链类 GenAI 披露：

```text
average peer effect without event FE:
    coef = +0.004225
    p = 0.026

supply_chain × AIActive:
    not significant

stacked event-DID:
    null
```

解释：AI 供应链披露更像 category validation / AI demand validation，不是本文主机制的 competitive-risk signal。

## 9. 机制安排

### 主机制

当前主机制是资本市场解释机制，而不是企业真实行为机制：

```text
Specific GenAI disclosure
    -> credible competitive-risk signal
    -> investors reassess AI-active close peers
    -> more negative PeerCAR[0,+1]
```

### 不作为强机制的部分

`peer disclosure diffusion` 在更严格口径下不稳定，不应作为主机制。最多放 appendix 或描述性后续反应。

招聘、专利、CAC 后续行为当前只适合做额外验证或未来扩展，不作为主 Y。

## 10. 主要稳健性清单

必须保留：

```text
1. event FE + peer industry-week FE
2. two-way clustered SE by event_id and peer_code
3. PeerCAR[-10,-2] and PeerCAR[-20,-2]
4. FocalCAR[0,+1] and FocalCAR[0,+1] × AIActive controls
5. AI-theme return × AIActive controls
6. text controls: length, AI keyword intensity, source / attention, numeric-detail
7. external AIActive component audit
8. Top1-3 / Top4-5 / Top6-10 proximity gradient
9. low-similarity and random peer placebos
10. non-GenAI pseudo-event placebo
11. AI-word-stripped similarity
```

## 11. 推荐表格顺序

### Table 1: Sample and Variables

```text
sample construction
event-year distribution
AIActive coverage
peer similarity distribution
summary statistics
```

### Table 2: Main Peer-CAR Result

主列：

```text
Top5 / ext_any / PeerCAR[0,+1]
event FE + peer industry-week FE
pre-window controls
two-way clustered SE
```

并列 robustness：

```text
current_text_history
Top10 extension
ext_plus_history
```

### Table 3: Text-Measure Robustness

```text
answer length
question length
AI keyword intensity
source / attention controls
numeric-detail controls
full observable text controls
```

### Table 4: AIActive Component Audit

```text
prior CAC
prior AI patent grant
prior broad-AI hiring
ext_no_hiring
ext_any
current_text_history
```

### Table 5: Identification Robustness

```text
FocalCAR controls
FocalCAR × AIActive
residualized Y
AI-theme × AIActive
non-GenAI pseudo-events
```

### Table 6 / Figure 1: Product-Market Proximity

```text
Top1-3
Top4-5
Top6-10
low-sim
random same-industry peers
AI-word-stripped similarity
```

### Table 7: Disclosure-Type Boundary

```text
type × AIActive horse race
supply-chain boundary
category validation vs competitive-risk interpretation
```

Appendix:

```text
daily event-time coefficients
window lead/lag
random placebo distribution
peer disclosure diffusion diagnostics
CAC / patent / hiring matching notes
```

## 12. 可以安全写的结论

```text
More specific focal GenAI disclosures are associated with more negative two-day CARs for externally AI-active Top5 product-market peers.
```

```text
The result is identified within focal disclosure events and survives peer industry-week fixed effects, peer pre-window CAR controls, focal-firm CAR controls, and AI-theme date-shock controls.
```

```text
The effect concentrates among close product-market peers and is absent among low-similarity or random same-industry peers.
```

```text
The evidence is consistent with competitive-risk revaluation rather than realized business stealing.
```

## 13. 不能写的结论

```text
GenAI disclosure causes rival value destruction.
```

```text
We prove business stealing.
```

```text
Specificity_z measures true GenAI implementation quality.
```

```text
ext_any precisely measures GenAI capability.
```

```text
Supply-chain disclosure is the main mechanism.
```

```text
Peer disclosure diffusion is a strong mechanism.
```

## 14. 当前可发表性判断

当前设计适合写成：

```text
capital-market revaluation paper
event-study + within-event cross-sectional heterogeneity
competitive-risk signal / category-validation boundary
```

不适合写成：

```text
strong causal DID / IV paper
real competition outcome paper
business stealing paper
```

投稿判断：

```text
AJG/ABS 2: 稳妥目标
AJG/ABS 3: 可以谨慎冲，但必须保守写 claim
AJG/ABS 4: 当前识别强度不够
```

## 15. 给画布讨论的关键问题

1. 当前 `Specificity_z × AIActivePeer` 是否应作为唯一 headline X？
2. `ext_any` 是否比 `current_text_history` 更适合做主 AIActive？
3. 主故事应叫 competitive-risk signal，还是 peer-side market reassessment？
4. AI supply-chain boundary 是否放主文，还是只做 appendix？
5. Table 2 是否只放 Top5/ext_any/headline，其他全部 robustness？
6. 是否还需要补一个更清楚的理论锚：information transfer vs competitive effect？
7. AJG/ABS 3 的最短补强路径是什么？
