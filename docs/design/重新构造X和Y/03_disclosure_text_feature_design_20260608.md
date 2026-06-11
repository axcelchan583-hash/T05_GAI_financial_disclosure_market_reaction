# T05 GenAI 公告文本特征研究设计

日期：2026-06-08

用途：在“竞争对手 + 合作性关联方”宽口径设计的基础上，重新定义 X。本文不把 `Specificity` 单独作为主 X，而是把 GenAI 公告文本拆成若干具有文献支撑的特征维度，用来解释不同关系类型公司的短窗口市场反应。

## 1. 研究问题

拟定问题：

```text
上市公司披露 GenAI initiative 时，资本市场是否根据公告文本中的可信实施信号、战略嵌入信号和宣传性/AI-washing 信号，对竞争对手和合作性关联方作出不同方向的价值重估？
```

相对于旧表述，关键变化是：

- 旧 X：`Specificity` 或 `Specificity x AIActivePeer`。
- 新 X：GenAI 公告的多维文本特征。
- 旧 Y：产品市场同行 CAR。
- 新 Y：至少保留两个关系方向：
  - `CompetitorCAR`：产品市场竞争对手异常收益，预期为负。
  - `InvestmentLinkedPartnerCAR` / `CooperativeLinkedCAR`：投资型或合作型关联方异常收益，预期相对竞争对手更正。

`Specificity` 仍保留，但降为“可信实施信号”的一个组成部分。这样可以避免论文被审成“只是又做了一次披露具体性”，也能承接 AI disclosure / AI washing 文献。

## 2. 文献锚点

### 2.1 年报/10-K 文本特征传统

这一支文献给出“披露文本可以量化”的基本工具箱：

- Li (2008, JAE) 用年报可读性和长度衡量信息处理成本。
- Loughran and McDonald (2011, JF) 构造金融语境词典，解决普通情感词典在金融文本中的误判问题。
- Loughran and McDonald (2014, JF) 讨论金融披露可读性的可复现测度，提醒 Fog 指数在金融文本中不一定稳。
- Brown and Tucker (2011, JAR) 用 MD&A 相比上一年的修改程度衡量叙述性披露的信息含量。
- Cohen, Malloy and Nguyen (2020, JF) 证明 10-K/10-Q 文本变化具有未来收益和基本面含义。
- Dyer, Lang and Stice-Lawrence (2017, JAE) 把 10-K 文本拆成长度、boilerplate、stickiness、redundancy、specificity、readability、hard information 等属性。
- Hope, Hu and Lu (2016/2018, RAST) 用算法构造风险因素披露的 `Specificity`，并将其与 10-K filing market reaction 和分析师风险评估相连。

对本项目的含义：文本 X 不能只有“AI 关键词数”。更可防守的做法是把公告内容拆成可读性、具体性、硬信息、文本变化、模板化和情感/不确定性等维度。

### 2.2 产品市场文本网络传统

Hoberg and Phillips (2010, RFS; 2016, JPE) 用 10-K 产品描述文本构造产品市场相似度和 text-based network industries。本文的竞争对手口径可以继续引用这一传统。

本项目的迁移方式：

```text
年报/经营文本 -> 产品市场邻近度/竞争网络；
GenAI 公告文本 -> 事件信号强度/可信度/战略嵌入。
```

二者不要混成一个变量。前者定义“谁受影响”，后者定义“这条披露有多强、强在哪”。

### 2.3 AI 披露与 AI-washing 文献

近期 AI 披露文献强调，AI 相关文本可能是真实投资信号，也可能是宣传或 washing：

- Barrios, Campbell, Johnson and Liu 的 `Signals or Smoke?` 将 AI 披露与 AI employment 等真实投入对照，区分信号与烟雾。
- Cheng, De Franco, Jiang and Lin (2019, Management Science) 的区块链 8-K 研究把披露分为 speculative 与 existing product，说明热点技术披露可能带来短期反应和后续反转。
- AI-washing 相关工作通常把“AI 文本强度”与“AI 真实投入/专利/招聘/资本开支”之间的错配作为核心度量。

对本项目的含义：GenAI 公告文本应区分“可执行的能力披露”和“蹭热点式披露”。这比单一 `Specificity` 更贴近当前 AI 资本市场文献。

## 3. 文本特征三维度

建议把 GenAI 公告文本 X 拆成三组。

### 3.1 可信实施信号：Implementation Credibility

含义：公告是否传递“公司已经或即将可验证地实施 GenAI 能力”的信息。

候选指标：

| 指标 | 构造 | 预期 |
|---|---|---|
| `Specificity` | 可核验细节密度；数字、产品名、应用场景、机构名、日期、金额等 | 竞争者更负；合作方更正 |
| `HardInfo` | 数字、金额、合同期限、订单、客户数量、模型参数、备案号等硬信息占比 | 同上 |
| `ImplementedAction` | 是否出现“已上线、已发布、已应用、已落地、已签约、已部署、已接入”等已实施词 | 同上 |
| `Commercialization` | 是否出现收入、订单、客户、付费、商业化、产品销售、SaaS、解决方案等商业化信息 | 同上 |
| `OwnCapability` | 是否描述自研模型、自有平台、算法能力、算力部署、数据资源等内部能力 | 对竞争者负向更强 |

解释逻辑：

```text
市场只有在披露包含可执行、可验证和商业化内容时，才更可能把它理解为焦点公司的真实能力提升。
```

### 3.2 战略嵌入信号：Strategic Embeddedness

含义：公告是否显示 GenAI initiative 嵌入已有生态、投资关系、客户关系或合作网络，而不是孤立口号。

候选指标：

| 指标 | 构造 | 预期 |
|---|---|---|
| `NamedPartner` | 是否点名合作方、客户、供应商、投资方、联合研发方 | 合作性关联方更正；竞争者更负 |
| `BigTechPartner` | 是否点名大型云厂商/基础模型厂商/平台公司 | 增强可信度，但也可能表示焦点依赖外部能力 |
| `EquityTieMention` | 是否出现投资、参股、控股、基金、合资、并购、战略投资等股权关系词 | 投资型 partner 更正 |
| `AllianceAction` | 是否出现战略合作、联合研发、联合发布、共建生态、签署协议等合作行动 | 合作方更正 |
| `CustomerUseCase` | 是否点名客户行业或客户场景 | 竞争者更负，客户/供应链相关方可能更正 |

解释逻辑：

```text
若公告显示 GenAI 能力嵌入既有关系网络，市场不只重估焦点公司，也会重估能分享该能力的关联方。
```

这一组指标尤其适合解释当前 FactSet 投资型合作方的正向 event-weighted 信号。

### 3.3 宣传性/AI-washing 信号：Promotional or AI-washing Risk

含义：公告是否更接近热点叙事、泛泛关注或未来式口号，而非具体 initiative。

候选指标：

| 指标 | 构造 | 预期 |
|---|---|---|
| `AIKeywordIntensity` | AI/AIGC/大模型/ChatGPT/DeepSeek/GPT 等关键词密度 | 单独不应作为正向可信信号 |
| `VagueFuturePlan` | “拟、计划、未来、探索、关注、积极布局、持续跟踪”等未来式/模糊词密度 | 削弱市场反应；可能反转 |
| `DenialOrNoBusiness` | “暂无、不涉及、尚无、无相关业务、未产生收入”等否认词 | 不应作为正向 initiative |
| `PromotionalTone` | 积极形容词、宏大叙事、行业趋势词密度 | 若缺少硬信息，偏 washing |
| `BuzzNoDetail` | 高 AI 关键词密度、低 `HardInfo` 或低 `Specificity` | 竞争者反应应弱或不稳 |

解释逻辑：

```text
AI 关键词本身可能只是注意力或宣传噪声。只有当关键词与硬信息、实施动作和外部证据共同出现时，才更接近可信技术信号。
```

## 4. 推荐的综合变量

为了避免十几个文本变量一起进入主表，建议先构造三个标准化指数。

### 4.1 可信实施指数

```text
CredibleImplementation_z =
  z(Specificity)
+ z(HardInfo)
+ z(ImplementedAction)
+ z(Commercialization)
+ z(OwnCapability)
```

可先用等权平均，之后用 PCA 或因子分析做稳健性。正文优先等权，便于解释。

### 4.2 战略嵌入指数

```text
StrategicEmbeddedness_z =
  z(NamedPartner)
+ z(AllianceAction)
+ z(EquityTieMention)
+ z(CustomerUseCase)
```

如果 `BigTechPartner` 的经济含义不稳定，不建议直接放进指数；可以单独作为边界条件。

### 4.3 宣传/错配指数

```text
PromotionalWashing_z =
  z(AIKeywordIntensity)
+ z(VagueFuturePlan)
+ z(PromotionalTone)
+ z(BuzzNoDetail)
+ z(DenialOrNoBusiness)
```

其中 `DenialOrNoBusiness` 最好在主样本构造阶段剔除；若保留，应作为污染/弱事件识别项，而不是普通连续特征。

## 5. 核心假设

### H1 竞争对手负向重估

```text
焦点公司 GenAI initiative 披露后，产品市场竞争对手产生负向短窗口异常收益。
```

主 Y：competitor `CAR[0,+1]`。

### H2 可信实施信号强化竞争者负向反应

```text
当公告包含更强的可信实施信号时，竞争对手负向异常收益更强。
```

检验：

```text
CompetitorCAR_{j,e} =
  alpha + beta CredibleImplementation_e
        + controls + FE + epsilon
```

预期：`beta < 0`。

如果使用 event FE，事件层 X 会被吸收；此时应进入 competitor-only 横截面窗口、或与 peer 层暴露交互：

```text
CompetitorCAR_{j,e} =
  alpha + beta CredibleImplementation_e x AIActivePeer_{j,e}
        + EventFE_e + controls + epsilon
```

预期：`beta < 0`。

### H3 战略嵌入信号强化合作性关联方正向反应

```text
当公告显示 GenAI initiative 嵌入投资、合作、客户或生态关系时，合作性关联方相对竞争对手获得更正向的异常收益。
```

检验：

```text
CAR_{j,e} =
  alpha
  + beta_1 CooperativeLinked_{j,e}
  + beta_2 StrategicEmbeddedness_e x CooperativeLinked_{j,e}
  + EventFE_e
  + controls
  + epsilon
```

预期：`beta_2 > 0`。

若 `CooperativeLinked` 进一步区分：

```text
InvestmentLinked, StrategicPartner, Supplier, Customer
```

当前最有希望的是 `InvestmentLinked`。

### H4 宣传/AI-washing 信号削弱关系网络重估

```text
当公告更接近宣传性或 AI-washing 时，竞争对手负向反应和合作方正向反应都应减弱，或在长窗口中反转。
```

检验：

```text
CompetitorCAR_{j,e} =
  alpha + beta PromotionalWashing_e x AIActivePeer_{j,e}
        + EventFE_e + controls + epsilon
```

预期：`beta` 不应显著为负；若显著为正，说明该类披露不是竞争威胁。

对合作方：

```text
CAR_{j,e} =
  alpha
  + beta_1 CooperativeLinked_{j,e}
  + beta_2 PromotionalWashing_e x CooperativeLinked_{j,e}
  + EventFE_e
  + controls
  + epsilon
```

预期：`beta_2 <= 0`。

## 6. 样本与关系网络

### 6.1 Treatment universe

当前冻结层：

| 层级 | 数量 | 用途 |
|---|---:|---|
| raw audit rows | 533 | 审计和追溯 |
| unique candidate events | 487 | 扩展事件样本 |
| first event per focal firm | 363 | 主样本候选 |

主文优先使用 `first event per focal firm`，扩展结果使用 unique events。

### 6.2 关系方样本

建议按以下顺序进入表格：

| 关系类型 | 当前定位 | 预期 |
|---|---|---|
| Product-market competitors | 主 Y，当前证据最稳 | 负 |
| FactSet investment-linked partners | 第二主 Y 候选，需人工清洗 | 正或相对更正 |
| FactSet suppliers/customers | 稳健性/边界结果 | 未必正 |
| CSMAR listed suppliers/customers | 覆盖低，作为对照 | 未必正 |
| Event-named listed partners | 高纯度小样本 | 正，但可能太少 |

暂不建议把“所有合作方 union”直接作为主 Y。关系类型异质性太强，容易把正负通道混在一起。

## 7. 实证表顺序

### Table 1 样本构造与文本特征描述

Panel A：事件漏斗。

Panel B：文本特征描述性统计：

- `Specificity`
- `HardInfo`
- `ImplementedAction`
- `Commercialization`
- `NamedPartner`
- `AllianceAction`
- `EquityTieMention`
- `AIKeywordIntensity`
- `VagueFuturePlan`
- `PromotionalWashing`
- 三个综合指数。

Panel C：文本特征相关系数，重点显示：

- `Specificity` 不等同于文本长度；
- `AIKeywordIntensity` 不等同于 `CredibleImplementation`；
- `StrategicEmbeddedness` 与 `CredibleImplementation` 相关但不同。

### Table 2 基准事件研究：关系类型分组

按关系类型报告：

| Relation type | AR[-1] | AR[0] | AR[+1] | CAR[0,+1] | N | Events | Firms |
|---|---:|---:|---:|---:|---:|---:|---:|
| Competitors | 负 | 负 | 负 | 负 |  |  |  |
| Investment-linked partners |  | 正/相对正 |  | 正/相对正 |  |  |  |
| Suppliers |  |  |  |  |  |  |  |
| Customers |  |  |  |  |  |  |  |

目前事实判断：

- Competitors 负向已经可写。
- Investment-linked partners 只有 event-weighted CAR[0,+1] 显著，ordinary mean 不显著，需人工清洗后再定级。

### Table 3 Stacked relationship regression

目的：不强迫合作方绝对为正，而是检验相对竞争者是否更正。

```text
CAR_{j,e} =
  alpha
  + beta_1 InvestmentLinked_{j,e}
  + beta_2 Supplier_{j,e}
  + beta_3 Customer_{j,e}
  + controls
  + EventFE_e
  + epsilon_{j,e}
```

基准组：product-market competitors。

预期：

- `InvestmentLinked > 0`。
- Supplier/customer 不一定显著。

### Table 4 文本特征机制：competitor sample

先放 competitor-only，主 Y 为 `CAR[0,+1]`：

```text
CompetitorCAR_{j,e} =
  alpha
  + beta_1 CredibleImplementation_e x AIActivePeer_{j,e}
  + beta_2 StrategicEmbeddedness_e x AIActivePeer_{j,e}
  + beta_3 PromotionalWashing_e x AIActivePeer_{j,e}
  + EventFE_e
  + controls
  + epsilon_{j,e}
```

建议先分列跑，不要三项全塞一列。预期：

- `CredibleImplementation x AIActivePeer < 0`。
- `StrategicEmbeddedness x AIActivePeer < 0`，但解释为生态/合作增强焦点公司威胁。
- `PromotionalWashing x AIActivePeer` 弱或不显著。

### Table 5 文本特征机制：investment-linked / cooperative sample

```text
CAR_{j,e} =
  alpha
  + beta_1 RelationType_{j,e}
  + beta_2 CredibleImplementation_e x RelationType_{j,e}
  + beta_3 StrategicEmbeddedness_e x RelationType_{j,e}
  + beta_4 PromotionalWashing_e x RelationType_{j,e}
  + EventFE_e
  + controls
  + epsilon_{j,e}
```

如果样本不够，改成事件层 event-weighted：

```text
MeanPartnerCAR_e =
  alpha
  + beta_1 CredibleImplementation_e
  + beta_2 StrategicEmbeddedness_e
  + beta_3 PromotionalWashing_e
  + controls
  + epsilon_e
```

### Table 6 稳健性和污染清洗

至少包括：

- 删除 peer/related firm 自身 GenAI 事件。
- 删除重大公告污染。
- `AR[0]`、`CAR[-1,+1]`、`CAR[0,+5]`、`CAR[0,+20]`。
- first-event vs unique-event。
- Top5 vs Top10 competitor。
- ordinary mean vs event-weighted mean。

## 8. 手工核验方案

文本特征不能完全靠正则。建议分两层：

### 8.1 规则先打底

先用规则生成所有特征，便于全样本跑。

规则输出每条事件的证据句：

- `implemented_action_sentences`
- `hard_info_sentences`
- `partner_sentences`
- `equity_tie_sentences`
- `washing_risk_sentences`
- `denial_sentences`

### 8.2 人工/LLM 双重抽样核验

抽样对象：

- `first event per focal firm` 中进入 competitor 回归的事件。
- investment-linked partner positive/negative 的 top/bottom 事件。
- 文本指数最高/最低各 50 条。

每条事件人工打四个 0/1/2 分：

| 字段 | 含义 |
|---|---|
| `initiative_validity` | 是否真的是 GenAI initiative |
| `implementation_credibility` | 是否有可执行/已执行证据 |
| `strategic_embeddedness` | 是否有明确合作/投资/客户/生态嵌入 |
| `promotional_washing_risk` | 是否更像宣传或蹭概念 |

主样本不必完全人工编码，但必须有抽样一致性和若干典型案例。

## 9. 当前可执行的脚本方向

下一步脚本建议命名：

```text
scripts/run_v48_disclosure_text_feature_panel_20260608.py
```

输出目录：

```text
results/v48_disclosure_text_feature_panel_20260608/
```

核心输出：

| 文件 | 内容 |
|---|---|
| `event_text_features.csv` | 每个 v36 事件的文本特征 |
| `event_text_feature_evidence_sentences.csv` | 每个特征对应证据句 |
| `text_feature_summary.csv` | 描述性统计 |
| `text_feature_correlations.csv` | 相关系数 |
| `competitor_text_feature_regressions.csv` | competitor 机制回归 |
| `relationship_text_feature_regressions.csv` | relationship stacked 回归 |
| `manual_validation_sample.csv` | 人工核验样本 |

## 10. 结果解释规则

### 可以升级为主线的条件

满足以下条件时，可以把论文主线升级为“文本特征驱动的关系网络重估”：

1. `CompetitorCAR[0,+1]` 继续显著为负。
2. `CredibleImplementation x AIActivePeer` 或相近项为负，并通过基本文本控制。
3. `InvestmentLinked` 或 `InvestmentLinked x StrategicEmbeddedness` 相对 competitor 显著为正。
4. washing 指标不复制主结果，或能解释弱事件/反转。
5. 手工核验显示高 `CredibleImplementation` 样本确实是具体 initiative，不是“暂无/关注/蹭热点”。

### 只能作为机制/异质性的条件

如果 competitor 主效应稳，但文本指数只在部分设定显著：

```text
文本特征作为机制和边界条件；
主线仍是 GenAI initiative 披露引发 product-market competitor negative revaluation。
```

### 应放弃文本主 X 的条件

如果文本指数主要由长度、关键词密度或公告类型驱动，且手工核验无法区分真实 initiative 与宣传：

```text
不把文本特征作为主 X；
只保留 v36 initiative event 本身和关系类型差异。
```

## 11. 当前建议

当前最合理的论文路线是：

```text
GenAI initiative disclosures and relationship-dependent market revaluation
```

主干：

1. GenAI initiative 披露使产品市场竞争对手负向重估。
2. 投资型合作关联方出现相对正向/事件等权正向信号，但需人工清洗后确认。
3. 公告文本特征解释这种关系网络重估：
   - 可信实施信号强化竞争者负向反应；
   - 战略嵌入信号强化投资/合作关联方相对正向反应；
   - 宣传/AI-washing 信号削弱上述效果或产生噪声。

谨慎边界：

- 不再写“Specificity 是主 X”。它是 `CredibleImplementation` 的组成部分。
- 不把所有合作方统称为 collaborator。当前更准确的正向候选是 `investment-linked partners`。
- 不承诺供应商复制 Qian。中国 A 股上市供应商覆盖低，现有结果不支持供应商正向主效应。
- 不把文本特征跑成无理论的 horse race。每个特征必须归入可信实施、战略嵌入或 washing 三类之一。
