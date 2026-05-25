# T05 研究设计更新：供应链 / Peer GenAI 扩散

日期：2026-05-13

## 这次为什么要改

旧设计的核心问题是：

```text
本公司 GenAI 采用 -> 本公司岗位 / 披露 / 创新变化
```

这个设定太容易被内生性打穿。更早采用 GenAI 的公司，本来就可能更数字化、更有资源、更会披露、更重视组织升级。即使结果显著，审稿人也会问：这是 GenAI 采用带来的，还是优秀公司本来就在变。

因此，新设计把本公司 GenAI 采用从主 X 降级为结果或机制，把主 X 改成网络外部冲击：

```text
客户 / 供应商 / 同业 peer 的 GenAI 采用
        -> 焦点公司后续真实采用、能力升级、披露调整和信息环境变化
```

核心不是“岗位变化了”，而是：

> GenAI 是否沿企业网络扩散，并迫使未采用或低采用企业进行能力升级。

## 新主线选择

### 首选主线：客户 GenAI 采用 -> 供应商能力升级

最推荐的主问题：

> 主要客户的 GenAI 采用是否推动供应商后续 GenAI 采用与知识工作能力升级？

机制逻辑：

```text
客户采用 GenAI
        ↓
客户的产品接口、交付标准、数据协同、客服/营销/供应链流程变化
        ↓
供应商为了维持合作关系或获取订单，被迫升级数字/AI能力
        ↓
供应商后续 GenAI 采用、AI互补招聘、软件/产品更新、披露调整
```

这条比“本公司采用 -> 本公司变化”更强，因为 X 来自焦点公司外部的客户网络，而不是焦点公司的自选择采用。

### 次选主线：同业 peer GenAI 采用 -> 竞争压力 / 模仿采用

备选问题：

> 行业内重要 peer 的 GenAI 采用是否推动未采用企业跟随采用、调整招聘结构或强化 GenAI 叙事？

这个方向也能降低同公司内生性，但比供应链弱一些，因为同行 GenAI 采用更容易和行业共同趋势混在一起。

### 暂不推荐主线：供应商 GenAI 采用 -> 客户公司变化

上游供应商采用 GenAI 也可能影响焦点公司，但机制不如客户拉动供应商清楚。它更像成本、质量或交付能力改善，数据要求更高，适合放到扩展而不是主设计。

## 研究对象与样本

### 样本

- 中国 A 股上市公司。
- 样本期初步设为 2021-2026。
- GenAI 事件从 2022-11-30 ChatGPT 发布后开始识别；DeepSeek 作为 2025 年补充冲击节点。
- 供应链关系用 GenAI 事件前已经存在的客户/供应商关系，避免事后关系选择。

### 网络关系

首选使用：

- CSMAR / WIND 重要客户与重要供应商；
- 年报前五大客户/供应商文本；
- 可匹配上市主体的客户/供应商名称。

主样本优先使用事件前固定关系：

```text
PreCustomerLink_ij = 1
```

其中 `j` 是焦点公司 `i` 的主要客户。权重可用事件前销售占比：

```text
w_ij,pre = 客户 j 占供应商 i 销售额比例
```

如果销售占比缺失，先用等权重或 top customer rank weight。

## 核心 X 构造

### X1：客户 GenAI 采用暴露

公司 i 在 t 年 / 月的客户 GenAI 暴露：

```text
CustomerGenAIExposure_it
= sum_j w_ij,pre * PostFirstSpecificGenAIAdoption_jt
```

其中：

- `j` 是 i 在 GenAI 事件前已经存在的主要客户；
- `PostFirstSpecificGenAIAdoption_jt` 表示客户 j 是否已经发生首次具体 GenAI 采用事件；
- 采用事件必须来自人工筛选后的 `FirstSpecificGenAIAdoption` 事件库；
- 泛 AI、数字化转型、机器学习、智能制造、纯概念回应不进入主事件。

### X2：客户 GenAI 采用事件

事件研究 / stacked DID 版本：

```text
ExposedSupplier_i = 1[至少一个主要客户发生首次具体 GenAI 采用]
EventTime_it = t - FirstCustomerGenAIAdoptionDate_i
```

这里 `FirstCustomerGenAIAdoptionDate_i` 是焦点供应商 i 的第一个主要客户 GenAI 采用时间。

### X3：同业 peer GenAI 暴露

Peer 暴露不能只用行业均值，否则会被行业-年固定效应吸收，也容易变成行业趋势。建议用 firm-specific peer weights：

```text
PeerGenAIExposure_it
= sum_k SimilarityWeight_ik,pre * PostFirstSpecificGenAIAdoption_kt
```

权重可来自：

- 同行业内业务文本相似度；
- 同产品市场相似度；
- 同地区同行；
- 行业内头部企业 / 竞争对手；
- 预 2022 年同业共同客户或供应商 overlap。

Peer 版本最好加入行业-年固定效应，因此 X 必须在同一行业同一年内仍有公司层面的差异。

## Y 的预设层级

这次不把一个 Y 赌死。为防止单个主效应不显著，预先设置 outcome families。后续不能事后乱挑显著项，而是按层级解释。

### Family A：GenAI 跟随采用

这是最贴近供应链扩散机制的主 Y。

| 变量 | 构造 |
|---|---|
| `OwnValidatedGenAIAdoption_it` | 焦点公司是否发生首次具体 GenAI 采用事件 |
| `TimeToOwnGenAIAdoption_i` | 从客户 GenAI 采用到焦点公司首次采用的时间 |
| `OwnGenAINarrative_it` | 焦点公司年报、公告、互动平台中的 GenAI 叙事强度 |
| `NarrativeToAdoptionGap_it` | GenAI 叙事强度 - 硬采用证据 |

解释：

- 如果客户采用后，供应商也更快采用 GenAI，这是最直接的扩散证据。
- 如果只提高叙事、不提高硬采用，反而是 AI washing / pressure response 方向。

### Family B：能力升级与组织重构

这是“岗位变化”应放的位置，但不再是最终故事。

| 变量 | 构造 |
|---|---|
| `AIComplementaryHiringShare_it` | AI、大模型、数据、算法、软件、产品、自动化、RAG、Agent、知识库等岗位占比 |
| `RoutineCognitiveHiringShare_it` | 文员、录入、基础客服、基础财务、行政支持、低复杂度文案等岗位占比 |
| `KnowledgeWorkUpgradingIndex_it` | 高学历、高经验、分析/判断/协调/统计/合规/沟通技能要求的综合指标 |
| `WithinJobSkillUpgrading_ijt` | 同一岗位内部 AI 工具、数据分析、高阶认知、沟通协调技能强度 |

解释：

- Family B 是机制或能力升级结果。
- 单个岗位内部变化只作为 `WithinJobSkillUpgrading`，不单独当主论文终点。

### Family C：真实创新 / 产品兑现

这是比岗位更硬的真实结果。

| 变量 | 构造 |
|---|---|
| `GenAISoftwareCopyright_it` | GenAI / AIGC / 大模型 / 智能体 / 知识库相关软件著作权 |
| `AIProductLaunch_it` | 官网、公众号、公告中的 AI 产品或功能上线 |
| `GenAIPatent_it` | GenAI 相关专利申请 |
| `InnovationEfficiency_it` | AI/软件/产品创新产出相对研发投入或研发人员的效率 |

解释：

- 如果客户 GenAI 采用能推动供应商软著、产品、功能上线，贡献比岗位变化更硬。
- 专利可能滞后，软件著作权和产品上线更适合短窗口。

### Family D：供应链关系与经营韧性

这组 Y 直接回答“供应链扩散有什么经济后果”。

| 变量 | 构造 |
|---|---|
| `CustomerRetention_it` | 是否继续保留原主要客户 |
| `CustomerConcentration_it` | 前五大客户集中度 |
| `NewMajorCustomer_it` | 是否出现新主要客户 |
| `SalesToTreatedCustomers_it` | 对已采用 GenAI 客户的销售占比 |
| `ARCollectionRisk_it` | 应收账款周转、坏账准备、回款风险 |
| `SupplyChainResilience_it` | 客户流失、收入波动、供应链风险暴露 |

解释：

- 如果能力升级能帮助供应商维持客户关系或减少客户依赖风险，这就是清楚的 “so what”。
- 数据要求更高，适合作第二主结果或扩展表。

### Family E：披露与信息环境

这组保留 T05 原来的会计/披露特色。

| 变量 | 构造 |
|---|---|
| `SupplyChainRiskDisclosureSpecificity_it` | 供应链/客户依赖/交付/技术协同相关风险披露具体性 |
| `CustomerSpecificDisclosure_it` | 是否更具体披露客户结构、客户风险、订单变化、技术协同 |
| `RegulatoryInquiry_it` | 年报问询、关注函、修订公告 |
| `AnalystForecastError_it` | 分析师预测误差 |
| `AnalystForecastDispersion_it` | 分析师预测分歧 |
| `AnalystCoverage_it` | 分析师覆盖 |

解释：

- 这组不是第一反应，而是信息生产和资本市场后果。
- 如果 Family A/B/C 有证据，Family E 可以解释市场和监管是否识别这种能力变化。

### Family F：市场反应，只做辅助

| 变量 | 构造 |
|---|---|
| `SupplierCAR` | 客户 GenAI 公告附近供应商短窗异常收益 |
| `PeerCAR` | 同业 GenAI 公告附近非事件同行异常收益 |
| `TradingVolume` | 交易量变化 |

解释：

- 不建议作为主 Y，因为已有 GenAI announcement -> suppliers stock reaction 的 POM 论文很近。
- 可以作为外部有效性或短期预期反应。

## 推荐主结果顺序

如果只能先跑一套主表，建议按这个顺序：

1. **Family A：GenAI 跟随采用**
   - 供应链扩散是否存在。
2. **Family B：AI 互补招聘 / 知识工作升级**
   - 供应商是否开始建设能力。
3. **Family C：软件著作权 / 产品上线**
   - 能力升级是否兑现为产品或技术资产。
4. **Family E：供应链披露具体性 / 分析师信息环境**
   - 是否产生会计金融后果。
5. **Family D：客户关系与经营韧性**
   - 若数据可得，作为最有经济意义的扩展。
6. **Family F：CAR / 交易量**
   - 只作辅助，不当卖点。

这不是 p-hacking，而是预先定义的结果层级。若第一层不显著，后面结果也要按机制解释，不能只挑显著表。

## 主要实证设定

### Firm-year / firm-month 暴露模型

```text
Y_it
= beta * CustomerGenAIExposure_it
+ controls_it
+ firm FE
+ industry-year FE
+ eps_it
```

这里的识别来自同一行业同一年内，不同企业因为事件前客户结构不同而受到不同客户 GenAI 采用冲击。

控制变量：

- 规模、杠杆、ROA、成长性、TobinQ；
- 现金流、研发强度、资本开支；
- pre-period AI/数字基础；
- 分析师覆盖、机构持股；
- 客户集中度；
- 行业-年固定效应；
- 地区-年固定效应可作为稳健性。

### Stacked DID / event study

```text
Y_it
= sum_k beta_k * 1[EventTime_it = k]
+ firm FE
+ industry-year FE
+ controls_it
+ eps_it
```

事件：

```text
FirstCustomerGenAIAdoptionDate_i
```

关键要求：

- 只用事件前已经存在的客户关系；
- 事件前窗口必须通过 pre-trend；
- 对照组来自未暴露或尚未暴露的供应商；
- 若焦点公司自己已先采用 GenAI，主样本中应剔除或单独标记。

### Hazard model：跟随采用

如果 Family A 作为主 Y，可以用 adoption hazard：

```text
Pr(OwnFirstGenAIAdoption_it = 1 | not yet adopted)
= f(CustomerGenAIExposure_it, controls, firm FE / industry-year FE)
```

解释更直接：

> 主要客户采用 GenAI 后，供应商是否更快跟随采用。

## 异质性

优先异质性：

| 异质性 | 预期 |
|---|---|
| 客户销售占比高 | 效应更强 |
| 供应商数字基础强 | 更容易跟随采用和招聘升级 |
| 产品/服务定制化强 | 更容易被客户技术流程牵引 |
| 供应商融资约束弱 | 更有资源升级 |
| 供应商处于高文本/知识工作暴露行业 | 招聘和信息生产变化更强 |
| 客户是行业龙头 | 示范和议价压力更强 |
| 同城/同省 vs 跨省 | 可区分地理扩散与供应链扩散 |

## 安慰剂与排除

必要检查：

1. **伪事件时间**
   - 把客户 GenAI 采用时间提前 1-2 年，主效应不应出现。
2. **非 GenAI 技术公告**
   - 用传统 AI / 数字化公告替代 GenAI 事件，检验是否只是一般数字化趋势。
3. **非客户 peer**
   - 用非客户但同业公司采用 GenAI 对该供应商的影响，作为供应链特异性对照。
4. **排除焦点公司自身先采用**
   - 如果供应商自己已经先采用 GenAI，则不能解释为客户拉动。
5. **排除同日重大客户事件**
   - 客户业绩、重大合同、并购、监管处罚等混杂事件需标记。
6. **固定事件前关系**
   - 不用 GenAI 采用后新形成的客户关系定义暴露。

## 与旧 T05 的关系

旧 T05：

```text
本公司 GenAI 采用 / PostGenAI × 写作负担
-> 风险披露具体性
```

新 T05：

```text
客户 / peer GenAI 采用
-> 本公司 GenAI 跟随采用、招聘升级、产品兑现
-> 供应链风险披露 / 分析师信息环境 / 客户关系
```

旧设计可以保留为机制或补充：

- `OwnGenAIAdoption` 不再是主 X，而是 Family A 的 Y；
- `RiskDisclosureSpecificity` 不再单独承担主论文，而是 Family E；
- `AIComplementaryHiringShare` 不再作为最终回答，而是 Family B；
- CAR 只作短期外部有效性。

## 当前推荐版本

最稳的题目暂定：

> 客户 GenAI 采用是否推动供应商能力升级？来自中国上市公司供应链、招聘与创新证据

如果保留会计金融口径：

> 生成式人工智能采用的供应链扩散与企业信息生产调整

当前主设计：

```text
CustomerGenAIExposure_it
-> OwnValidatedGenAIAdoption_it
-> AIComplementaryHiringShare_it / GenAISoftwareCopyright_it
-> SupplyChainRiskDisclosureSpecificity_it / AnalystForecastDispersion_it
```

当前底线：

- **不要再把同公司 GenAI 采用作为主 X。**
- **不要把岗位变化当最终 Y。**
- **不要把供应商 CAR 当主论文卖点。**
- 主贡献应落在：供应链 GenAI 扩散、供应商能力升级、以及会计/信息环境后果。
