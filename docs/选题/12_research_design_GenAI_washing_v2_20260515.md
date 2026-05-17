# 研究设计 v2：GenAI Washing — 能力披露与实际兑现的差距

**版本**: v2（在 v1 基础上把方法论实施根锚换为 post-2020 的 4 星论文）
**日期**: 2026-05-15
**关键词**: GenAI washing, capability disclosure-investment gap, Chinese listed firms

> 与 v1 的关键差异：方法论实施根锚从 Rogers-Stocken (2005, _TAR_) 切换为 Baker et al. (2024, _JAR_) "Diversity Washing"。Rogers-Stocken 降级为概念溯源。所有 X 测度、Y 测度、识别策略的实施模板均来自 2019-2025 之间的 4 星论文。

---

## 0. 一句话研究问题

> **中国上市公司在 GenAI 能力上的对外披露与实际 GenAI 投入/能力之间的差距（"GenAI Washing"），是否在 12-24 个月内通过多维度真实兑现失败而显现，并被机构投资者、分析师与监管部分识别。**

这是 Baker et al. (2024, _Journal of Accounting Research_) "Diversity Washing" 方法论在 GenAI 场景的直接平移。

---

## 1. 方法论根锚（全部 4 星，主要是 post-2020）

### 1.1 整篇方法论实施根

**Baker, A. C., Larcker, D. F., McClure, C. G., Saraph, D., & Watts, E. M. (2024). "Diversity Washing." _Journal of Accounting Research_, 62(5): 1661–1709.**

Baker et al. 的核心做法：

1. 抓取 voluntary disclosure 中关于 DEI 的话语强度
2. 用企业**实际**的员工性别与种族多样性作为 baseline
3. 把"discuss DEI excessively relative to actual diversity"的企业定义为 **diversity washers**
4. 检验 washers 是否获得更高 ESG 评级、吸引 ESG 基金流入、同时更可能在未来发生歧视违规

**对本设计的直接平移**：

| Baker et al. 2024 JAR | 本设计 |
|---|---|
| DEI disclosure intensity（文本） | GenAI capability disclosure intensity（文本） |
| Actual employee diversity ratio | Actual GenAI investment（AI-skilled hires + GenAI patents + GenAI products + LLM 备案） |
| "Diversity washers" = X 相对 baseline 的残差 | "GenAI washers" = X 相对 baseline 的残差 |
| Y: ESG ratings, ESG fund flows, future discrimination violations | Y: 12-24 月内多 Track 兑现失败，机构投资者流入，分析师下调，未来监管处罚 |

这一一对应使本设计的合法性来自一篇 2024 年的 JAR 4 星论文，而不是 2005 年的奠基文献。

### 1.2 技术-热潮-披露 4 星前驱

**Cheng, S. F., De Franco, G., Jiang, H., & Lin, P. (2019). "Riding the Blockchain Mania: Public Firms' Speculative 8-K Disclosures." _Management Science_, 65(12): 5901–5913.**

Cheng et al. 把 blockchain 8-K 分成 **Speculative**（vague future plan）与 **Existing**（current product），观察短窗 CAR 与 30 天反转。Bitcoin 价格越高，反应越强。

**对本设计的直接含义**：

- 我们要做的"GenAI capability disclosure"也存在 Speculative 与 Existing 两类——把 Cheng et al. 的二分类作为 X 的离散版本，与 Baker-style 残差作为连续版本互为稳健性
- ChatGPT 与 DeepSeek 节点对应 Bitcoin 价格高点，提供"热潮指数 × disclosure"的交互项识别

### 1.3 文本测度方法 4 星锚

**Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). "Firm-Level Political Risk: Measurement and Effects." _Quarterly Journal of Economics_, 134(4): 2135–2202.**

Hassan et al. 提供企业层面文本测度的金标准：

1. 用计算语言学工具从公开文本中抓取目标主题的占比
2. 通过 firm-level 真实行动（lobbying、政治捐款、股价波动）做外部验证
3. 强调 firm × time 变异占主导，行业-时期 FE 不能完全吸收

### 1.4 AI 实际投入与兑现测度 4 星锚

**Babina, T., Fedyk, A., He, A. X., & Hodson, J. (2024). "Artificial intelligence, firm growth, and product innovation." _Journal of Financial Economics_, 151: 103745.**

Babina et al. 用 AI-skilled human capital 度量企业实际 AI 投资；Y 落在产品创新、销售、就业、估值。这是 baseline capability 测度与 Y 兑现测度的双重 4 星根。

**Brynjolfsson, E., Li, D., & Raymond, L. R. (2025). "Generative AI at Work." _Quarterly Journal of Economics_, 140(2): 889–942.**

GenAI 真实部署后的生产力变化，提供 GenAI-specific 兑现的 4 星依据。

### 1.5 市场识别 4 星锚

**Cohen, L., Malloy, C., & Nguyen, Q. (2020). "Lazy Prices." _Journal of Finance_, 75(3): 1371–1415.**

文本变化包含的信号被市场缓慢吸收，做空 "changers"做多"non-changers" 年化超额收益约 22%。给我们的"长窗 CAR 反转"假设提供 JF 级别支撑。

### 1.6 理论概念溯源（不作实施模板）

**Rogers, J. L., & Stocken, P. C. (2005). "Credibility of Management Forecasts." _The Accounting Review_, 80(4): 1233–1260.**

非财务前瞻性披露偏差 → 市场识别 → forecast bias 的奠基理论。仅在 introduction 与 hypothesis development 中作为概念溯源引用，不作为实施模板。

---

## 2. 概念模型

```
                                            ┌─────────────────────────┐
                                            │  Y (Main):              │
                                            │  Multi-Track Capability │
                                            │  Non-Realization        │
                                            │  in [t+1, t+24m]        │
                                            │  (Babina + Brynjolfsson)│
                                            └────────────▲────────────┘
                                                         │
                                                         │ (Washing)
                                                         │
   ┌────────────────────────┐         ┌─────────────────────────┐
   │  X: GenAI Washing      │         │  M:                     │
   │  Score_it              │ ──────▶ │  - 融资压力             │
   │  = TalkResidual after  │         │  - 内部人减持            │
   │    controlling for     │         │  - 财务困境              │
   │    actual GenAI        │         │  - 行业概念热度          │
   │    investment          │         │    (Cheng et al. 风格)   │
   │    (Baker et al.       │         └─────────────────────────┘
   │     2024 JAR style)    │                       │
   └────────────────────────┘                       │
              ▲                                     ▼
              │                       ┌─────────────────────────┐
   ┌────────────────────────┐         │  Y (Validation):        │
   │  Baseline GenAI        │         │  - ESG/科技基金流入      │
   │  Investment:           │         │    (Baker 等结构)         │
   │  (Babina JFE style)    │         │  - 长窗 CAR 反转          │
   │  - AI-skilled hires    │         │    (Cohen-Malloy-Nguyen) │
   │  - GenAI patents       │         │  - 分析师下调            │
   │  - GenAI products      │         │  - 监管处罚              │
   │  - LLM 备案             │         └─────────────────────────┘
   └────────────────────────┘
```

---

## 3. 假设

- **H1（Baker-style 主假设）**：GenAI Washing Score 越高，t+1 到 t+24 月内多 Track 真实兑现越低。
- **H2（资金流入假设，Baker et al. 2024 JAR Section 5）**：高 Washing 公司在短期内吸引更多科技主题基金流入与 ESG 基金流入。
- **H3（Cheng-style 热潮交互）**：在 GenAI 热潮指数高的季度（ChatGPT、DeepSeek 节点），Washing 现象更严重；类似 Cheng et al. (2019, MS) 中 Bitcoin 价格越高市场对 Speculative 8-K 反应越强。
- **H4（Cohen-Malloy-Nguyen 长窗反转）**：高 Washing 公司在 12-24 个月内出现负长窗 CAR、分析师下调、机构投资者流出。
- **H5（异质性）**：Washing → Non-Realization 在融资压力高、内部人正在减持、监管约束弱的企业中更强。

---

## 4. X：GenAI Washing Score

### 4.1 测度方法（直接平移 Baker et al. 2024 JAR）

Baker et al. 把 DEI washing 定义为：disclosure 强度相对 baseline diversity ratio 的正残差。我们做严格平行的构造：

**步骤一：抓取 GenAI capability disclosure 强度**

参考 Hassan et al. 2019 QJE 的 firm-level text construction 方法，从四个文本源抓取：

| 文本源 | 抓取重点 |
|---|---|
| 巨潮资讯网公告 | GenAI 实体词 + forward-looking 动词的句子数 |
| 年报 MD&A 与业务讨论 | GenAI 相关战略叙事 |
| 互动易 / 上证 e 互动 | Q&A 答复 |
| 投资者关系活动记录 | 机构问答的口径 |

GenAI 实体词字典：生成式人工智能 / 大模型 / AIGC / 智能体 / RAG / Copilot / 知识库问答 / 数字员工 / 智能客服 / 代码生成。

Specificity 子维度（Hassan-QJE 的主题专门性 + Hutton-Miller-Skinner 2003 JAR 的 supplementary statements 思想）：对每条 disclosure 给 0-5 分，看是否包含产品名 / 模型名 / 场景 / 时间表 / 合作方。

```
GenAITalk_it = sum_{s} (1 + SpecificityScore_s)
```

**步骤二：构造 baseline GenAI investment**

参考 Babina et al. 2024 JFE 的 AI-skilled human capital 方法 + 中国制度特有的硬证据：

```
BaselineGenAIInvestment_it
    = w1 * AISkilledHiringShare_pre12m
    + w2 * GenAIPatentApplication_pre24m
    + w3 * GenAISoftwareCopyright_pre24m
    + w4 * GenAIProductLaunch_pre24m
    + w5 * CAC_LLM_Registration_pre24m
```

权重 w 可用 PCA 第一主成分。

**步骤三：构造 GenAI Washing Score（直接套 Baker et al. 2024 JAR Equation 1 风格）**

```
GenAITalk_it = α + β * BaselineGenAIInvestment_it + γ * X_it
             + FirmFE + IndustryQuarterFE + ε_it

GenAIWashingScore_it = ε_it    (即 OLS 残差)
```

ε_it > 0 → washer（"discuss GenAI excessively relative to actual investment"）
ε_it < 0 → masker（"actual investment exceeds disclosure"）

**步骤四：分组（Cheng et al. 2019 MS 离散版本，作稳健性）**

按 GenAIWashingScore 的行业-季度分位数：

- **Speculative GenAI Discloser**：top quartile（高 washing）
- **Existing GenAI Discloser**：bottom quartile（mascker / 低 washing）
- 中间作为对照组

### 4.2 Baker-style validation（必须）

Baker et al. 2024 JAR 用四种外部 validation 证明 washing 测度的合法性。我们做平行 validation：

1. Washing 高的公司是否在 ESG / 科技主题基金中的占比上升（Baker et al. Section 5）
2. Washing 高的公司是否有更高的财务困境与融资需求（Baker et al. Section 6）
3. Washing 高的公司是否在 Hassan-QJE 的"firm × time 变异占主导"测试中通过
4. Washing 高的公司是否在 GenAI 热潮节点（ChatGPT、DeepSeek）后增加，类似 Cheng et al. 2019 MS 的 Bitcoin 价格 → 8-K 数量关系

---

## 5. Y：Multi-Track Capability Non-Realization

### 5.1 测度根（仍是 Babina + Brynjolfsson 4 星组合）

5 Track 的构造继续用 v1 的设计，每个 Track 都有 4 星方法论根：

| Track | 测度 | 4 星方法论根 |
|---|---|---|
| **T1：AI-skilled hiring growth** | AI 互补岗位份额增长 | Babina et al. 2024 _JFE_；Acemoglu et al. 2022 _JOLE_ |
| **T2：GenAI 创新产出** | 专利 + 软著 | Babina et al. 2024 _JFE_ |
| **T3：GenAI 产品上线** | 官网、公众号、公告 | Brynjolfsson et al. 2025 _QJE_；Babina et al. 2024 _JFE_ |
| **T4：CAC 大模型 / 算法备案** | CAC 公示 | 中国制度独有；与 Hassan QJE 的 external validation 逻辑一致 |
| **T5：GenAI 任务相关运营改善** | 成本率、毛利率、人均创收同行调整 | Brynjolfsson et al. 2025 _QJE_ |

```
NonRealization_it = sum_{k=1..5} Track_k_NonRealize_it  ∈ [0, 5]
NonRealizationHigh_it = 1 if NonRealization >= 4
```

### 5.2 行业-时期调整

```
NonRealization_IndAdj_it = NonRealization_it − Median(NonRealization | IndustryQuarter)
```

排除整个行业冷却的宏观共振，与 Baker et al. 2024 JAR Section 4.3 的行业-年调整逻辑一致。

---

## 6. M：机制变量

### 6.1 直接借鉴 Baker et al. 2024 JAR Section 5-6 的机制因素

Baker et al. 检验了三类驱动 washing 的因素：

1. **External financing needs**
2. **Weak governance**
3. **Attraction from ESG-focused investors**

中国 GenAI 场景的对应：

| Baker et al. 2024 JAR 机制 | 本设计中国对应 | 数据 |
|---|---|---|
| External financing needs | 股权质押率、定增需求、现金流紧张 | CSMAR |
| Weak governance | 监管立案历史、董事会独立性、内控缺陷披露 | CSMAR + 手工 |
| Attraction from ESG investors | GenAI 主题基金、科技基金、QFII 持股变化 | Wind / CSMAR |
| Industry concept hype | 行业 GenAI 概念热度指数；ChatGPT/DeepSeek 节点距离 | 新闻数据 + 自构造 |

### 6.2 辅助机制（Cheng et al. 2019 MS 风格）

Cheng et al. 发现 Bitcoin 价格越高，blockchain 8-K 数量越多。我们做平行：

- GenAI 概念热度指数（基于行业新闻、股价、基金持仓加权）越高，Washing Score 增加越快
- ChatGPT、DeepSeek 节点前后，Washing 程度跳跃式变化

---

## 7. 控制变量与异质性

### 7.1 控制变量

- 规模、Leverage、ROA、Tobin Q
- 上市年龄、所有制
- 分析师覆盖、机构持股
- pre-period 行业 GenAI 暴露（Eloundou et al. 2024 _Science_ 中文映射）
- pre-period 数字化基础

### 7.2 异质性维度

按 Baker et al. 2024 JAR 与 Babina et al. 2024 JFE 的标准：

- **预定 GenAI 暴露度**：高 vs 低（Eloundou-Felten）
- **既有 AI 基础**：高 vs 低（Babina-style）
- **监管约束**：曾被监管处罚 vs 无记录
- **资金压力**：高股权质押 vs 低
- **板块**：主板 / 创业板 / 科创板（市场监督强度不同）

---

## 8. 验证 Y（次要）

### 8.1 锚点

| 验证 Y | 4 星方法论锚 |
|---|---|
| 长窗 CAR 反转（t+6m 到 t+24m） | Cohen, Malloy, Nguyen 2020 _JF_ |
| 短窗 CAR 反应与后续反转 | Cheng et al. 2019 _MS_ |
| 机构投资者流入（特别是科技 / ESG 基金） | Baker et al. 2024 _JAR_ Section 5 |
| 分析师预测下调 | Hutton-Miller-Skinner 2003 _JAR_ |
| 未来监管处罚 / 立案 | Baker et al. 2024 _JAR_ Section 6（discrimination violations 对应物） |

**所有验证 Y 都不作主贡献**。

---

## 9. 识别策略

### 9.1 主回归（Baker et al. 2024 JAR Equation 2 平移）

```
NonRealization_{i, t+12to+24m}
    = β1 * GenAIWashingScore_it
    + Γ * Controls_it
    + FirmFE_i
    + IndustryYearQuarterFE_jt
    + ε_it
```

双重聚类标准误：firm-level + industry-quarter level。

### 9.2 识别威胁与缓解

| 威胁 | 缓解 | 4 星锚 |
|---|---|---|
| Washer 本来就是差公司 | Firm FE；Heckman 两阶段 | Heckman 1979 _Econometrica_；Baker et al. 2024 JAR 处理方式相同 |
| 行业-时期共同波动 | Industry × YearQuarter FE | Babina et al. 2024 _JFE_ 与 Baker et al. 2024 _JAR_ 标准做法 |
| 高基线公司多说也多兑现 | 残差化已扣除可由 baseline 预测部分 | Baker et al. 2024 _JAR_ 核心做法 |
| Y 测度受冲击 | 5 个 Track 取交集 | Hassan et al. 2019 _QJE_ multi-validation |
| 反向因果 | 严格 lead-lag + 安慰剂 | Cheng et al. 2019 _MS_ 标准 |

### 9.3 IV

```
LeaveOneOutPeerWashing_jt
    = mean(GenAIWashingScore_kt, k in industry j × quarter t, k != i)
```

锚点：Leary & Roberts 2014 _JF_ leave-one-out peer IV。

### 9.4 安慰剂

| 安慰剂 | 预期 | 锚点 |
|---|---|---|
| 用 2018-2021 pre-GenAI 时期重做 | 不显著 | Babina et al. 2024 _JFE_ |
| 用 t-2 期 X 预测 t-1 期 Y | 不显著 | Baker et al. 2024 _JAR_ |
| 用非 GenAI 概念词（"工业 4.0"、"区块链"）造伪 X | 不显著 | Cheng et al. 2019 _MS_（用 non-blockchain tech 安慰剂） |
| GenAI 中性词频（无 forward-looking 动词） | 不显著 | Hassan et al. 2019 _QJE_ |

---

## 10. 样本与数据

### 10.1 样本

- 中国 A 股
- 文本抓取：2022 Q4 - 2025 Q4
- 兑现观测：2023 Q1 - 2026 Q4
- 主分析窗：2023 Q3 - 2024 Q4 的 disclosure spike

### 10.2 数据源

同 v1（巨潮、互动易、e 互动、CSMAR、Wind、专利局、版权中心、招聘 JD、CAC 备案）。

### 10.3 关键技术

- 中文 GenAI capability statement BERT，按 Hassan QJE 训练流程做
- Baker et al. 2024 JAR 的"discuss X relative to actual X"逻辑作为构造检查标准
- Anchor 数据集：100-300 家公司人工编码

---

## 11. Pilot 5 张表 / 图

### 表/图 1：GenAI Washing Score 的描述统计（Baker JAR Figure 1 风格）

- GenAITalk 与 Baseline 的散点图（按行业-季度分面）
- 残差分布
- Washer / Masker 行业分布

### 表/图 2：Baker-style 外部 validation

- Washer 是否：股权质押高、销售放缓、现金流紧张、上一季业绩 miss
- Washer 是否在科技 / ESG 基金中占比上升
- 时间趋势是否在 ChatGPT、DeepSeek 节点跳跃（Cheng 2019 MS 风格）

### 表/图 3：主结果

```
NonRealization_{t+12to+24m} = β * WashingScore_t + controls + FE
```

按 X 五分位画 Y 的均值条形图；OLS / Logit / Ordered Logit。

### 表/图 4：Baker-style 机制异质性

- 融资需求高 vs 低
- 监管约束弱 vs 强
- ESG 基金持仓变化高 vs 低
- 行业 GenAI 概念热度高 vs 低

### 表/图 5：市场识别（Cohen-Malloy-Nguyen 长窗 + Cheng 短窗）

- 短窗 CAR 反应
- 长窗 CAR 反转
- 分析师下调时滞
- 机构持股变化
- 未来监管立案 / 处罚

---

## 12. 限制与诚实声明

1. **24 月窗口紧张**：主样本落在 2023 H2-2024 Q4。主表用 12 月窗，附录用 24 月窗。
2. **Washing 测度依赖 baseline 测度的合法性**：Baker et al. 2024 JAR 在他们的 robustness 中详细讨论这一点；我们用 PCA + 等权双轨道稳健性，模仿其做法。
3. **CAC 备案覆盖局限**：备案只覆盖面向公众的生成式服务，B2B 内部部署不在其中。
4. **不是严格因果**：Washing 与 Non-Realization 共享潜在管理层动机；论文识别的是关联，呼应 Baker et al. 2024 JAR 的因果定位（associational evidence）。
5. **中国制度独有性**：互动易、备案、问询是中国独有的；外部有效性弱于 Baker JAR 全美国大样本，但内部多源验证更可信。

---

## 13. 与既有文献的差异化贡献

| 已有文献 | 本设计差异 |
|---|---|
| **Baker et al. 2024 _JAR_ Diversity Washing** | 把"washing"框架从 DEI 迁移到 GenAI；用中国制度独有的多源验证（公告 + 互动易 + IR + 备案 + 软著 + 招聘 + 专利）使 baseline 测度比英文文献更细致 |
| **Cheng et al. 2019 _MS_ Blockchain Mania** | 不只看短窗 CAR，而把"speculative disclosure"与中长期真实兑现联系起来 |
| **Hassan et al. 2019 _QJE_ Firm-Level Political Risk** | 同方法论用于 GenAI capability，目标主题不同 |
| **Babina et al. 2024 _JFE_** | 我们多一层"AI 投资承诺与实际投资的差距"，可以识别他们文献中谁是 talker、谁是 doer |
| **Brynjolfsson et al. 2025 _QJE_** | 用企业层面 Washing 数据扩展他们的微观 GenAI 部署效应 |
| **Cohen, Malloy, Nguyen 2020 _JF_** | 用 GenAI capability text 解释 lazy prices 在科技披露场景的具体机制 |
| **李哲 et al. 2024（会计研究）；姚树洁 et al. 2026** | 我们的方法论根从 Chinese 文献切换为 4 星英文文献，理论与方法都升级 |

**核心贡献定位**：
> 我们提供首篇把 Baker et al. (2024, _JAR_) Diversity Washing 方法论从 ESG/DEI 领域扩展到技术能力披露领域的实证研究。通过 Hassan-style (2019, _QJE_) 文本测度构造 GenAI Washing Score，并用 Babina-style (2024, _JFE_) 与 Brynjolfsson-style (2025, _QJE_) 多维度真实兑现进行事后验证。

---

## 14. 参考文献

### 核心 4 星根锚（post-2020 优先）

- Baker, A. C., Larcker, D. F., McClure, C. G., Saraph, D., & Watts, E. M. (2024). Diversity Washing. _Journal of Accounting Research_, 62(5): 1661–1709.
- Babina, T., Fedyk, A., He, A. X., & Hodson, J. (2024). Artificial intelligence, firm growth, and product innovation. _Journal of Financial Economics_, 151: 103745.
- Brynjolfsson, E., Li, D., & Raymond, L. R. (2025). Generative AI at Work. _Quarterly Journal of Economics_, 140(2): 889–942.
- Cheng, S. F., De Franco, G., Jiang, H., & Lin, P. (2019). Riding the Blockchain Mania: Public Firms' Speculative 8-K Disclosures. _Management Science_, 65(12): 5901–5913.
- Cohen, L., Malloy, C., & Nguyen, Q. (2020). Lazy Prices. _Journal of Finance_, 75(3): 1371–1415.
- Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-Level Political Risk: Measurement and Effects. _Quarterly Journal of Economics_, 134(4): 2135–2202.

### 4 星辅助

- Acemoglu, D., Autor, D., Hazell, J., & Restrepo, P. (2022). AI and Jobs: Evidence from Online Vacancies. _Journal of Labor Economics_, 40(S1): S293–S340.
- Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2024). GPTs are GPTs: Labor market impact potential of LLMs. _Science_, 384(6702): 1306–1308.
- Hutton, A. P., Miller, G. S., & Skinner, D. J. (2003). The Role of Supplementary Statements with Management Earnings Forecasts. _Journal of Accounting Research_, 41(5): 867–890.
- Leary, M. T., & Roberts, M. R. (2014). Do Peer Firms Affect Corporate Financial Policy? _Journal of Finance_, 69(1): 139–178.
- Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. _Journal of Finance_, 66(1): 35–65.
- Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. _Journal of Accounting Research_, 54(4): 1187–1230.
- Rogers, J. L., & Stocken, P. C. (2005). Credibility of Management Forecasts. _The Accounting Review_, 80(4): 1233–1260. **【概念溯源，不作实施模板】**

### 中文场景文献（辅助 / 制度背景）

- 陈运森, 邓祎璐, 李哲 (2019). 非行政处罚性监管能改善市场信息环境吗？《管理世界》, (3): 169–185.
- 李哲, 李心武, 焦焰 (2024). "多言寡行"的数字化转型披露与分析师预测行为. 《会计研究》, (9): 61–75.
- 吴非, 胡慧芷, 林慧妍, 任晓怡 (2021). 企业数字化转型与资本市场表现. 《管理世界》, 37(7): 130–144.
- 姚树洁, 洪涛, 陈锡毅 (2026). 人工智能概念炒作与分析师盈余预测. 《广东财经大学学报》, 41(1): 4–16.

### 主动剔除

- Bingler et al. 2022 _Finance Research Letters_（AJG 2）：方法论根锚不够硬
- Bingler et al. 2024 _Journal of Banking & Finance_（AJG 3）：辅助文献，不作根锚
- Marquis et al. 2016 _Organization Science_：仅作 ESG washing 概念溯源
- Cui, Pittman, Tao 2024 _Review of Accounting Studies_（AJG 3）：仅作辅助

---

## 15. 下一步具体动作

1. **手工编码 100-300 家 pilot**：建立 GenAI capability disclosure 与 baseline investment 的 anchor 数据集，按 Baker et al. 2024 JAR Section 3 的人工编码标准。
2. **训练中文 BERT**：在通用中文 BERT 上做 GenAI capability statement 微调。Hassan QJE 训练流程。
3. **建立 5 Track 数据流水线**：招聘、专利、软著、产品、备案。
4. **跑表/图 1-3**：判断 Washing Score 是否有可观察的右尾与机制异质性。
5. **若 pilot 通过**：扩全样本，做异质性、IV、安慰剂、长窗 + 短窗市场识别。

---

**结束。本文件为 v2 内部讨论稿。所有方法论实施根锚为 2019-2025 之间的 4 星论文，Rogers-Stocken 2005 仅作概念溯源。**
