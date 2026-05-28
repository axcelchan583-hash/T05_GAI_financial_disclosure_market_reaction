# v8 项目大纲：GenAI 具体化披露与产品市场同行重估

日期：2026-05-28

## 一句话判断

这个项目继续做，但写法必须更保守。当前最稳的论文不是“GenAI 披露导致竞品价值损失”，而是：

> 资本市场是否会把焦点公司的具体化 GenAI 披露解读为竞争风险信号，并在短窗口内相对下调事前 AI-active 的近产品市场同行？

最新一轮检验表明，主市场反应结果仍然成立。当前版本先不纳入人工编码分支；论文主线仍使用 `Specificity_z`，但把它写成 disclosure concreteness / text-detail signal，而不是“真实落地具体性”。

## 当前可写研究问题

### 主问题

```text
Do specific GenAI disclosures by Chinese listed firms trigger negative
short-window revaluation of AI-active close product-market peers?
```

中文表述：

```text
中国上市公司更具体的 GenAI 披露，是否会被资本市场解读为竞争风险信号，
从而使事前具备 AI 活动证据的近产品市场同行出现更负的短窗相对重估？
```

### 不写成的问题

```text
GenAI 披露是否真实抢走竞争对手业务？
GenAI 披露是否导致所有同行下跌？
AI 供应链披露是否存在 DID 主效应？
产品市场同行是否随后真实增加 AI 投入？
```

这些都不是当前证据能支撑的主命题。

## 核心变量

### Main Y

```text
PeerCAR[0,+1]
```

定义：近产品市场同行在焦点 GenAI 披露交易日及后一交易日的 market-model abnormal return 加总。

### Main X

当前实证主 X：

```text
Specificity_z_e × AIActivePeer_{j,t-5}
```

测度地位：

```text
Specificity_z_e = objective text-detail / disclosure concreteness proxy
Manual coding branch = out of scope for current draft
```

### Main AIActive

主定义：

```text
ext_any =
    prior CAC filing
 OR prior broad-AI patent grant
 OR prior broad-AI hiring in previous 365 days
```

使用理由：它来自披露文本系统之外，能减轻 same-source text concern。

核心稳健性：

```text
current_text_history =
    peer firm has prior GenAI disclosure before t-5
```

注意：`current_text_history` 概念上贴近 GenAI 披露历史，但有 pre-window negative pattern；只能作为 robustness，不适合作 headline。

### Peer Definition

主样本：

```text
First focal GenAI disclosure event × Top5 product-market peers
```

产品市场近邻基于中文公司业务描述文本构造。AI-word-stripped similarity 和低相似 / 随机同行 placebo 用作有效性防御。

## 最终主样本冻结

来自：

```text
results/v8_measurement_final_checks_20260527/final_sample_summary.csv
```

冻结口径：

```text
Sample: first focal GenAI event × Top5 product-market peers
Rows: 7,805
Events: 2,177
Focal firms: 2,177
Peer firms: 3,345
Event window: 2023-01-01 to 2026-05-20
Peer ranks: 1 to 5
Announcement-cleaned: yes
Requires PeerCAR[-10,-2] and PeerCAR[-20,-2]: yes
Requires FocalCAR[0,+1]: yes
```

年度分布：

```text
2023: 866 events
2024: 211 events
2025: 1,051 events
2026: 49 events
```

后续所有 headline tables 都应以这一口径为准。旧的 8,649 行 / 2,415 事件结果只能作为 pre-freeze diagnostic，不再放主文。

## 识别设计

主规格：

```text
PeerCAR_{e,j,[0,+1]}
  = beta_1 AIActivePeer_{j,t-5}
  + beta_2 Specificity_e × AIActivePeer_{j,t-5}
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

识别含义：

```text
Event FE 吸收焦点披露事件层面的平均信息冲击。
beta_2 来自同一个焦点事件内，AI-active peers 与 non-AI-active peers 的相对差异，
以及这种差异如何随焦点披露具体性变化。
```

这不是 IV / DID，也不是强因果设计。最安全表述是 short-window peer-side market reassessment。

## 最新主结果

### 主表稳定性

来自：

```text
docs/empirical_runs/54_v6_focal_good_news_pretrend_checks_20260525.md
results/v6_focal_good_news_pretrend_checks_20260525
```

最终 headline 样本：

```text
Top5 / first focal GenAI event / announcement-cleaned
PeerCAR[0,+1]
event FE + peer industry-week FE
PeerCAR[-10,-2] + PeerCAR[-20,-2] controls
two-way clustered by event_id and peer_code
```

结果：

```text
ext_any:
    coef = -0.002303
    p = 0.020
    N = 7,805
    events = 2,177
    peer firms = 3,345

current_text_history:
    coef = -0.002275
    p = 0.027
```

解释：焦点披露具体性增加 1 个标准差时，AI-active Top5 peers 相对 non-AI-active peers 的两日异常收益低约 23bp。

### 焦点公司自身利好控制

加入：

```text
FocalCAR[0,+1] × AIActivePeer
```

结果基本不变：

```text
ext_any:
    coef = -0.002307
    p = 0.020

current_text_history:
    coef = -0.002283
    p = 0.027
```

说明：主结果不是简单由焦点公司自身“利好/利空程度”驱动。

### Pre-trend 净化

用 `PeerCAR[-10,-2]` 净化 Y 后：

```text
ext_any:
    coef = -0.002295
    p = 0.021

current_text_history:
    coef = -0.002274
    p = 0.027
```

说明：在吸收短期 pre-window 后，主结果仍在。

### AI-theme date-shock controls

来自：

```text
docs/empirical_runs/61_v8_measurement_final_checks_20260527.md
results/v8_measurement_final_checks_20260527/ai_theme_shock_controls.csv
```

用事前 external-active firms 的日均 abnormal return 构造 AI-theme abnormal return，并与 AIActive 交互。

结果：

```text
ext_any baseline:
    coef = -0.002303
    p = 0.020

ext_any + AI-theme return × AIActive:
    coef = -0.002112
    p = 0.032

ext_any + market return × AIActive:
    coef = -0.002328
    p = 0.019

ext_any + AI-theme and market interactions:
    coef = -0.002129
    p = 0.030
```

说明：结果不是被简单的 AI 主题日行情吸收。

## 产品市场近邻有效性

来自：

```text
docs/empirical_runs/60_v7_event_time_peer_validity_20260527.md
results/v7_event_time_peer_validity_20260527
```

主要证据：

```text
Top1-3, ext_any:
    coef = -0.003252
    p = 0.016

Top6-10:
    insignificant

low-similarity peers:
    insignificant

random same-industry peers:
    insignificant
```

peer-set 描述：

```text
Mean product similarity:
    Top1-3 = 0.255
    Top4-5 = 0.206
    Top6-10 = 0.180
    random same-industry = 0.055
    low-similarity = 0.006
```

解释：结果集中在更近的产品市场同行，而不是普通同业或低相似度公司。

## AIActive 组件审计

来自：

```text
results/v8_measurement_final_checks_20260527/external_component_counts.csv
results/v8_measurement_final_checks_20260527/external_component_regs.csv
```

最终样本覆盖：

```text
prior_cac: 24 active observations, 15 active peer firms
prior_ai_patent_grant: 138 observations, 49 peer firms
prior_broad_ai_hiring_365_ge1: 1,554 observations, 746 peer firms
ext_no_hiring: 162 observations, 64 peer firms
ext_any: 1,646 observations, 773 peer firms
current_text_history: 2,061 observations, 1,102 peer firms
```

回归结果：

```text
prior_ai_patent_grant:
    coef = -0.009719
    p = 0.003

prior_broad_ai_hiring_365_ge1:
    coef = -0.001813
    p = 0.075

ext_no_hiring:
    coef = -0.008419
    p = 0.006

ext_any:
    coef = -0.002303
    p = 0.020

current_text_history:
    coef = -0.002275
    p = 0.027
```

解释：external AIActive 的组件异质性较强。专利和 `ext_no_hiring` 更干净但稀疏；招聘覆盖更广但较粗。主文应透明报告组件表，不要让 `ext_any` 看起来像一个无争议的“真实 GenAI 能力”指标。

## Specificity 测度处理

这一版先不纳入人工编码分支。主文只把 `Specificity_z` 定义为：

```text
objective text-detail / disclosure concreteness proxy
```

也就是说，它度量的是披露文本中可观察的信息细节和具体化程度，而不是人工判断的“真实 GenAI 落地实施具体性”。

主文需要做的测度防御是更直接的：

```text
控制 answer length / question length；
控制 AI keyword intensity；
控制 source / attention proxies；
控制 numeric-detail proxies；
说明 Specificity_z × AIActive 不是这些简单文本特征吃出来的。
```

## 经济量级

来自：

```text
results/v8_measurement_final_checks_20260527/economic_magnitude.csv
```

用最终样本中 `ext_any=1` 的 peer firm 日总市值 / 流通市值换算。

```text
Coefficient used: -0.002303
Active observations with market cap: 1,627
Coverage among active observations: 98.8%

Total market cap:
    median cap = RMB 9.48 billion
    implied median effect = RMB -21.85 million
    implied mean effect = RMB -86.91 million

Float market cap:
    median cap = RMB 7.75 billion
    implied median effect = RMB -17.85 million
    implied mean effect = RMB -79.22 million
```

解释：23bp 在事件研究里不是巨大效应，但按 AI-active peer 的市值换算并非经济上无意义。

## Placebo 与边界

### Non-GenAI pseudo-events

来自：

```text
results/v8_measurement_final_checks_20260527/non_genai_pseudo_event_summary.csv
```

结果：

```text
event FE:
    coef = 0.002349
    p = 0.358

event FE + peer industry-week FE:
    coef = 0.002284
    p = 0.372
```

解释：普通 IIP 事件不复现 GenAI 事件的负向 peer revaluation。

### Pre-window placebo

`ext_any` 在 pre-window 没有显著负向：

```text
PeerCAR[-10,-2]:
    coef = 0.000076
    p = 0.973

PeerCAR[-20,-2]:
    coef = -0.001749
    p = 0.556
```

`current_text_history` 有显著 pre-window negative pattern：

```text
PeerCAR[-10,-2]:
    coef = -0.004847
    p = 0.043

PeerCAR[-20,-2]:
    coef = -0.009149
    p = 0.003
```

解释：headline 必须用 `ext_any`，text-history 只能作为 robustness。

### AI supply-chain boundary

来自：

```text
docs/empirical_runs/57_v7_ai_supply_chain_disclosure_diagnostic_20260527.md
docs/empirical_runs/58_v7_ai_supply_chain_stacked_did_20260527.md
docs/empirical_runs/59_v7_disclosure_type_horserace_20260527.md
```

结论：

```text
AI supply-chain disclosure 的横截面平均 peer effect 为正，
更像 category validation / AI demand validation。

但 stacked DID 为 null，
不能作为主线。
```

写法：作为 boundary evidence，只写“并非所有 AI 披露都触发竞争风险重估”。

## 论文结构

### Introduction

核心写法：

```text
Firms increasingly disclose concrete GenAI activities through investor-facing channels.
Such disclosure can validate the AI category, but it can also reveal a focal firm's
strategic commitment and raise perceived competitive risk for close rivals.
We examine peer-side market revaluation rather than focal-firm announcement returns.
```

注意不要写：

```text
We identify causal business stealing.
```

### Section 2: Institutional Background and Theory

包含三条线：

1. Chinese investor-interaction platforms as timely investor-facing disclosure.
2. Product-market peer information transfer and competitive revaluation.
3. Two competing interpretations of GenAI disclosure:
   - category validation;
   - competitive-risk signal.

### Section 3: Data and Measurement

必须突出：

1. GenAI focal event construction.
2. Product-market peer construction.
3. AIActivePeer construction and component audit.
4. Specificity measurement problem and validation.

这一节要诚实写：

```text
The original text-detail score is not yet a validated GenAI-specificity measure.
We therefore either replace it with a validated component-based measure,
or treat the current result as preliminary.
```

### Section 4: Main Results

主表：

```text
Table 2:
    ext_any headline
    current_text_history robustness
    Top10 extensions
    pre-window controls
    event FE + peer industry-week FE
```

### Section 5: Identification and Robustness

包含：

1. FocalCAR and FocalCAR × AIActive controls.
2. residualized Y / pre-window controls.
3. AI-theme date-shock controls.
4. non-GenAI pseudo-events.
5. low-similarity / random peer placebo.
6. AI-word-stripped similarity.

### Section 6: Product-Market Proximity and Boundary Evidence

包含：

1. Top1-3 / Top4-5 / Top6-10 gradient.
2. peer validity summary.
3. supply-chain disclosure boundary.

### Section 7: Discussion and Limitations

明确承认：

1. This is short-window revaluation, not realized competition.
2. Specificity_z measures objective disclosure detail, not manually coded implementation specificity.
3. CAC / patent / hiring components are sparse and heterogeneous.
4. Daily event-time coefficients are underpowered; [0,+1] is the economic window.

## 推荐表格与图

### Table 1: Sample and Variable Summary

内容：

```text
final sample freeze
event-year distribution
AIActive coverage
disclosure type distribution
peer similarity distribution
```

### Table 2: Main Peer-CAR Result

Headline:

```text
ext_any / Top5 / PeerCAR[0,+1] / event FE + peer industry-week FE / pre-window controls
```

### Table 3: Text-Measure Robustness

主文只放与当前主测度直接相关的防御：

```text
length controls
AI keyword intensity controls
source / attention controls
numeric-detail controls
full observable text controls
```

人工编码分支不进入当前外部评审包。

### Table 4: AIActive Component Audit

内容：

```text
prior CAC
prior AI patent grant
prior broad-AI hiring
ext_no_hiring
ext_any
current_text_history
```

### Table 5: Identification Robustness

内容：

```text
FocalCAR × AIActive
residualized Y
AI-theme × AIActive
market return × AIActive
non-GenAI pseudo-events
```

### Figure 1: Product-Market Proximity Gradient

使用：

```text
results/v7_event_time_peer_validity_20260527/proximity_gradient_coefficients.png
```

### Figure 2: Window Lead/Lag

使用：

```text
results/v7_event_time_peer_validity_20260527/window_lead_lag_coefficients.png
```

### Appendix Tables

```text
daily event-time coefficients
random placebo distribution
AI-word-stripped similarity
supply-chain stacked DID null
peer disclosure diffusion null
top disagreement rows in specificity coding
```

## 可以安全写的结论

```text
In the final sample, more specific focal GenAI disclosures are associated with
more negative two-day market-model CARs for externally AI-active Top5 product-market peers.
```

```text
The effect survives focal-firm CAR controls, pre-window CAR controls,
AI-theme date-shock controls, and non-GenAI pseudo-events.
```

```text
The effect is concentrated among close product-market peers and is absent among
low-similarity or random same-industry peers.
```

```text
The evidence is consistent with competitive-risk revaluation, not proof of
realized business stealing.
```

## 不能写的结论

```text
GenAI disclosure causes rival value destruction.
```

```text
We prove business stealing.
```

```text
Specificity_z is validated implementation-specificity or realized GenAI capability.
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

## 当前投稿判断

### 当前版本

```text
继续当前主线；
把 Specificity_z 写成 objective text-detail / disclosure concreteness proxy；
投稿定位保持“谨慎冲 AJG/ABS 3，稳妥为 AJG/ABS 2-3”。
```

## 下一步最小闭环

1. 冻结当前 final headline sample 和 Table 2 规格。
2. 主文只保留 objective text controls / keyword controls / source controls 的测度防御。
3. 外部评审包只保留当前主线测度防御，不纳入人工编码分支。
4. 继续推进论文大纲、表格顺序和写作框架。
