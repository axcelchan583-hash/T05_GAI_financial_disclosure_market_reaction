# v10A Regulatory-Verified GenAI Adoption and Institutional Ownership Reallocation

**日期**：2026-05-17
**主 Y**：机构持股按基金 sleeve 拆分
**一句话**：用 CAC 生成式人工智能服务备案作为 verified GenAI adoption 的硬 X，检验机构投资者（按基金风格 sleeve 拆分）是否系统性地把仓位重新分配给验证过的 GenAI 公司。

---

## 0. 本版只回答什么

本版只回答一个问题：

> 当一家中国上市公司被网信办正式登记为面向公众提供生成式 AI 服务的主体后，不同类型的机构投资者（主动权益基金、科技主题基金、AI 主题 ETF、北向资金、被动指数基金）是否对该公司的持仓出现可识别的、按基金风格分化的重新分配？

不回答：

- 分析师预测如何变化（属 v10B 主问题）；
- 投资者短期 CAR（只作 validation）；
- claim-level specificity 是否可信（v8.1 留作第二篇）；
- 监管者之间是否传递信号（v9 路线已弃）；
- 公司经营是否兑现（real-outcome 作 Y6 锚定，不作主贡献）。

主问题的核心结构：

```text
regulator-verified GenAI deployment
    -> active institutional reallocation toward verified adopters
    -> passive funds show null effect (placebo within Y)
```

主贡献是**第一次记录监管验证信号在机构投资者层面引发的、按基金风格 sleeve 分化的资本重新分配**，配合 talk-walk × verification 2x2 网格，提供监管验证如何与公司自愿披露互动的证据。

---

## 0.1 理论命题

理论锚点：

- Baker, Larcker, McClure, Saraph, Watts (2024 JAR Diversity Washing)：washing 类设计的方法范本——monitor + rater + flow 三层 Y 的 monitor + flow 组合。
- Boyuan Li (2025 Florida WP)：AI talk-walk gap → 机构持仓反应，证明机构基金是 talk-walk 检测器（美国数据）。
- Donelson et al. (2025 SSRN 5265257)：AI washer/masker → 科技基金 + ESG 基金持仓，证明基金 sleeve 分化是可识别的（美国数据）。
- Christensen, Floyd, Liu, Maffett (2017 JAE)：mandatory disclosure → 多 intermediary 反应（监管 verification → 信息环境 lineage）。

理论命题：

> 监管者对 GenAI 采用的事后强制验证，相对于公司自愿披露，是一个更难被企业操纵的硬信号。资本市场上，对信息加工要求高、有主动选股能力的机构（主动权益基金、科技主题基金、AI 主题 ETF），会更系统性地把仓位重新分配给被验证的公司；而被动指数基金不应有这种分化（构成 Y 内部的 placebo）。

跟 Donelson 2025、Li 2025 的区别：

- 他们的 X 是公司自构造文本与外部行动的 talk-walk 差距，是市场作为验证主体；
- 我们的 X 是第三方监管者的二元验证，是国家作为验证主体；
- 中国制度独有，美国无等价。

---

## 1. 理想实验

如果能随机实验：

1. 对一组观测特征相似的中国上市公司，随机让其中一半被 CAC 备案；
2. 观察未来 4 个季度内不同类型机构投资者的持仓变化。

现实中不能随机。CAC 备案是公司申请、监管者审核、按批次公布。识别策略：staggered DiD + matched control + 报送日期与公示日期分离。

---

## 2. 分析单元

主分析单元：

```text
firm i × quarter q
```

样本期：

```text
2022Q1 - 2026Q2
```

样本筛选：

- A 股 + 港股通中国上市公司；
- 在样本期内连续上市；
- 剔除金融业（CAC 备案制度对金融业适用性不同）；
- 剔除 ST/退市。

---

## 3. 主 X

### 3.1 定义

```text
FirstCACRegistrationDate_i
    = 公司 i 或其可穿透子公司（持股 >= 50% 且经营范围覆盖该备案产品）
      首次出现在网信办「生成式人工智能服务备案」公示名单的日期

PostCAC_iq = 1[q >= QuarterOf(FirstCACRegistrationDate_i)]
EventTime_iq = q - QuarterOf(FirstCACRegistrationDate_i)
```

注释：

- 备案 vs 登记 vs 算法推荐备案：主表只用「生成式人工智能服务备案」名单（截至 2025 年底 ~748 个）；登记（~435 个）作为稳健性单独列；算法推荐备案不纳入；
- 同一上市公司有多个备案产品时，用首次备案日期；
- 后续变更/补充备案不算新事件。

### 3.2 报送日期与公示日期分离（关键内生性处理）

```text
ReportingDate_i  = 公司向 CAC 提交备案申请的日期（如可得）
PublicDate_i     = CAC 公开发布备案名单的批次日期
```

主表用 PublicDate_i 作为 event time。理由：

- 报送是公司决策，可能内生于公司预期；
- 公示是监管者决策（按批次、监管者审核完成统一发布），相对外生；
- 机构投资者在公示之前不可知是否被验证。

如果 ReportingDate_i 不可得，用 PublicDate_i 单独跑，并在论文中明确说明。

### 3.3 X 测的是什么

明确：CAC 备案测的是「公司向公众提供 GenAI 服务并完成法律登记」，不是「公司是否在内部使用 GenAI」。

- 有备案 → 一定有面向公众的 GenAI 产品
- 无备案 → 可能内部用 GenAI 但无面向公众产品，也可能完全不用

把 treatment 框成 **public-facing GenAI deployment**。控制组里可能存在 internal GenAI use 但不必处理，因为机构投资者关心的也是面向公众的可销售产品。

---

## 4. 主 Y 与 Y 包

### 4.1 主 Y：机构持股按 sleeve 拆分

```text
Y1a = Δ ActiveEquityFundHoldings_iq    主动权益基金持股比例季度变化
Y1b = Δ TechThemedFundHoldings_iq      科技主题基金持股比例季度变化
Y1c = Δ AIThemedETFHoldings_iq          AI 主题 ETF 持股比例季度变化
Y1d = Δ NorthboundHoldings_iq           沪深港通北向持股比例季度变化
Y1e = Δ PassiveIndexFundHoldings_iq    被动指数基金持股比例季度变化
```

预期：

```text
Y1a, Y1b, Y1c, Y1d > 0 after PostCAC
Y1e ≈ 0 after PostCAC (Y 内部 placebo)
```

如果被动基金也显著变动，说明效应来自指数权重调整或机械跟踪，不是主动选股逻辑——主效应解释失效。这是 Y 包内的关键 placebo。

### 4.2 基金 sleeve 分类的执行口径

数据源：CSMAR 基金持仓表（季频，A 股全样本）+ 基金分类信息。

分类规则：

```text
ActiveEquity:
    投资类型 = 偏股混合 / 灵活配置 / 普通股票
    且非指数型
    且基金名称不含「指数」「ETF」「成长」（基金风格分类已含成长不重复）

TechThemed:
    基金名称或基金类型含「科技」「TMT」「信息」「软件」「电子」「半导体」「计算机」
    且为主动管理

AIThemed:
    基金名称或代码含「人工智能」「AI」「智能」「大模型」「GAI」「AIGC」
    （含 ETF 与主动基金，单独列）

Northbound:
    沪股通 + 深股通 累计净持股（CSMAR/Wind 直接下载）

PassiveIndex:
    基金类型 = 被动指数型 / ETF
    且基金名称不含「人工智能」「AI」（剔除 AI 主题 ETF）
```

基金分类口径必须在论文 Appendix 给出完整匹配规则。建议每个 sleeve 给出"基金数量、基金净资产合计、持有 A 股市值合计"三个数字描述样本规模。

### 4.3 Y 包其他层

```text
Y2 = AnalystForecastDispersion_iq      分析师预测分歧（机制 Y，不作主表）
Y3 = MediaToneDispersion_iq             媒体语调分歧（Table 3 主 Y）
Y4 = ShortSellingBalance_iq             融券余额变化（仅在融券标的子样本）
Y5 = CAR(-1,+1), CAR(-3,+3)              围绕公示批次日期的短窗 CAR（validation only）
Y6 = SalesGrowth_{i,t+1}, _{t+4}         未来 1-4 季度销售增长（real-outcome 锚定）
```

层级：

- 主表：Y1a-Y1e（机构持股 sleeve）
- Table 3：Y3（媒体语调分歧）用于 talk-walk × verification 2x2
- Robustness：Y2（分析师 Y）、Y4（融券）、Y5（CAR）、Y6（销售增长）

### 4.4 为什么主 Y 选机构持股 sleeve

四个理由：

1. **多主体聚合**：每个 sleeve 背后是几十到几百个基金的独立决策，cross-sectional variation 自然存在；
2. **方法范本最近**：Donelson 2025（美国 AI washer → 科技基金 + ESG 基金）的方法直接可移植，sleeve 分类已有成熟做法；
3. **被动基金 placebo 自带**：Y 内部就能跑 placebo（主动应 > 0，被动应 ≈ 0），不需要额外构造；
4. **故事直接**："监管验证的 GenAI 公司被科技主题基金加仓"是一句话能讲完的发现，审稿人和读者都容易记住。

---

## 5. X/Y 隔离规则

### 5.1 时间隔离

```text
X 测度区间：q <= QuarterOf(PublicDate_i)
Y 测度区间：q > QuarterOf(PublicDate_i)
```

机构持股变化在备案公示之后的季度计数。

### 5.2 内容隔离

X 是监管者公示，Y 是机构投资者持仓——两端完全不重叠的决策主体。不存在 X/Y 同源问题。

### 5.3 控制组净化

控制组：

- 在样本期内从未被 CAC 备案的 A 股 + 港股通公司；
- 不是 treated firm 的可穿透子公司或母公司；
- 主表对照：never-treated；
- 稳健性：not-yet-treated（Callaway-Sant'Anna 框架）。

---

## 6. 识别策略

### 6.1 主方法

Callaway-Sant'Anna (2021) staggered DiD with not-yet-treated controls。

```text
ATT(g, t) = E[Y_{i,t}(g) - Y_{i,t}(∞) | G_i = g]
聚合到 event-time:
ATT(e) = sum_g w_g * ATT(g, g+e)
```

理由：

- CAC 公示是 10-12 个批次的 staggered treatment；
- TWFE 在 staggered 下有 forbidden comparisons 问题；
- Callaway-Sant'Anna 是当前会计/金融顶刊主流估计量。

### 6.2 推断

主表：

```text
cluster by firm (基础)
```

稳健性：

```text
MacKinnon-Nielsen-Webb-Karim (2026 arXiv 2602.12043)
cluster jackknife inference for CSDID
```

CAC 批次内公司在时间上聚集，cluster jackknife 是当前推断的方法前沿。

### 6.3 Event-study 形式

```text
Y_iq = sum_{e=-4, e!=-1}^{8} beta_e * 1[EventTime_iq = e]
        + alpha_i + delta_{j(i)q} + X_iq * gamma + eps_iq
```

参照组 e = -1。

约束：

- 主表 K_pre = 4，K_post = 8（持仓数据季频，需要更长 post-window 看流入分布）；
- pre-trend 检验：β_{-4}, β_{-3}, β_{-2} 应接近 0；
- post 关注 β_0 到 β_8。

### 6.4 PSM / Entropy Balance

在 g-1 季度用以下变量做匹配：

```text
size, leverage, ROA, MTB, age,
analyst coverage 基线, institutional ownership 基线,
PriorAIDisclosure 年报 AI 词频百分位,
PriorAIPatent_count, PriorSoftwareCopyright_count,
PriorActiveFundHoldings, PriorTechFundHoldings,
2-digit industry, year
```

主表：1:3 nearest-neighbor PSM with caliper 0.05。
稳健性：entropy balance；1:1 PSM；不匹配只用 high-dim FE。

### 6.5 内生性通道处理

```text
通道 A: 备案选择内生于公司过去机构持股结构
    => PriorActiveFundHoldings, PriorTechFundHoldings 作匹配协变量
通道 B: 备案与同期重大事件混杂
    => 剔除备案当季有重大资产重组/再融资/重大诉讼/控股股东变更的样本
通道 C: 备案与行业政策冲击共时
    => industry × year-quarter FE 吸收
通道 D: ChatGPT/DeepSeek 宏观冲击交错
    => 剔除 2022-11-30 ± 30 天和 2025-01-20 ± 30 天的 batch
```

---

## 7. 主回归

### 7.1 主表

```text
Δ ActiveEquityFundHoldings_iq
    = sum_{e=-4, e!=-1}^{8} beta_e * 1[EventTime_iq = e]
    + FirmFE_i + IndustryQuarterFE_jq + eps_iq
```

主系数：

```text
beta_0, ..., beta_8 > 0 for Y1a, Y1b, Y1c, Y1d
beta_e ≈ 0 for Y1e (passive index, within-Y placebo)
beta_{-4}, beta_{-3}, beta_{-2} ≈ 0 for all Y
```

5 列并排展示（Y1a/b/c/d/e）。

平均效应（备份）：

```text
Y1a_iq = beta * PostCAC_iq + FirmFE + IndustryQuarterFE + eps_iq
```

### 7.2 真实兑现锚定

Table 4 Column 1-2：

```text
SalesGrowth_{i,t+1, t+4} = beta * PostCAC + Controls + FE + eps
```

预期 beta > 0。目的：证明 verified 公司不仅吸引基金流入，也确实在经营层面有兑现，反驳"纯叙事"质疑。

---

## 8. 控制变量

### 8.1 公司层

- size, leverage, ROA, MTB, age；
- analyst coverage 基线, institutional ownership 基线；
- PriorAIDisclosure（2018-2022 年报 AI 词频）；
- PriorAIPatent_count；
- PriorSoftwareCopyright_count；
- PriorActiveFundHoldings（基金风格细分）；
- SOE dummy；
- 上市板块 dummy（主板/科创板/创业板/北交所/港股通）。

### 8.2 行业-时点

industry × year-quarter FE。

### 8.3 公司

firm FE。

industry × year-quarter FE 已含 year-quarter FE，不重复叠加。

---

## 9. 异质性

按理论意义排序：

### 9.1 Talk-Walk Wedge × Verification（Table 3 核心）

```text
PriorAITalkWalkWedge = 备案前 4 个季度的 AITextIntensity 百分位
                       - 备案前 4 个季度的 AIWalkIndex 百分位
```

AIWalkIndex 用 Babina 2024 JFE / Boyuan Li 2025 / Donelson 2025 的做法本土化：

- AI 招聘岗位占比（来自智联/前程招聘 JD）
- AI 专利累计存量
- 软件著作权 GenAI 相关数量

四象限：

```text
HighTalk + Verified:     已经吹 + 监管认可 = "实质化的吹"
HighTalk + Unverified:   吹但没认可        = "潜在 washing"
LowTalk + Verified:      没吹但有认可      = "低调真做"
LowTalk + Unverified:    都没             = 控制组
```

Table 3 跑 4 象限 × Y3 媒体语调分歧 + Y5 CAR + Y4 融券余额变化。预期：

- LowTalk + Verified 公司有最强正向媒体语调改善 + 最低分歧
- HighTalk + Unverified 公司媒体语调分歧扩大（市场识别 washing）

这是 v10 最有可能被引用的表。

### 9.2 行业暴露

```text
HighGenAIExposureIndustry × PostCAC
```

文化传媒、软件、教育、金融科技反应应更强。

### 9.3 公司预 AI 基础

```text
PriorAIPatent > 0 × PostCAC
```

预期：有 AI 基础的公司效应更强（验证不是单纯标签效应，是基础设施 + 验证）。

### 9.4 所有制

```text
SOE × PostCAC
```

民企/国企机构持股反应可能不同。

### 9.5 DeepSeek 冲击（次要）

```text
PostDeepSeek (2025-01-20) × PostCAC
```

DeepSeek 之后是否放大效应。仅作探索。

---

## 10. 安慰剂与稳健性

### 10.1 Y 内部 placebo

被动指数基金持股（Y1e）必须不动。这是主表第 5 列的"内置 placebo"。

### 10.2 时间安慰剂

```text
PlaceboCAC_iq = 1 if EventTime 对齐到 PublicDate_i - 8 quarters
```

预期 β_e ≈ 0。

### 10.3 anchor 安慰剂

用 2022 年前公司发布的"传统 AI / 数字化转型"重大公告作为 FakeCAC，跑同样的 DiD。

预期：FakeCAC 不应产生与真 CAC 备案同等规模的机构持股反应。如果产生，说明效应来自一般 AI 叙事而非 GenAI 监管验证。

### 10.4 Y 安慰剂

用与 GenAI 完全无关的基金类型（医药主题基金、消费主题基金）跑同样回归。

预期：β ≈ 0。

### 10.5 X 来源稳健性

```text
主表只用「生成式人工智能服务备案」名单
稳健性：扩展到「生成式 AI 应用登记」（截至 2025 底 ~435 个）
稳健性：剔除互联网巨头（百度、阿里、腾讯）等异常值
```

### 10.6 持仓数据稳健性

```text
主表用季度末持仓
稳健性：用半年报 + 年报披露的更完整持仓（含小额持有）
稳健性：CSMAR vs Wind 数据交叉验证
```

### 10.7 同期重大事件清洗

剔除 CAC 备案当季有以下事件的样本：

- 重大资产重组、再融资公告；
- 业绩预增/预亏修正；
- 控股股东变更；
- 重大诉讼、监管处罚；
- 重大客户/供应商公告；
- 重大股东减持/增持。

### 10.8 选择偏误（Heckman）

```text
第一阶段：Pr(CACFiling_i) = f(Industry, PriorAIPatent, PriorRD, Size, ...)
第二阶段：主回归带入 Inverse Mills Ratio
```

讨论：识别的是「条件于公司有意申请」的总体处理效应。这是政策相关的研究总体。

---

## 11. Pilot 与 go/no-go

### 11.1 第一步：X 覆盖性核查

任务：抓 2023Q3 到 2026Q1 全部 CAC 生成式 AI 服务备案批次，穿透到上市公司主体。

时间：3-5 天。

Go/no-go：

```text
treated firms (备案) >= 150
treated firms (备案 + 登记) >= 250
staggered batches >= 8
```

### 11.2 第二步：Y 数据可得性

任务：从 CSMAR 抓 2022Q1-2026Q2 全部 A 股基金持仓季度数据；建立基金 sleeve 分类映射表。

时间：3-5 天。

Go/no-go：

```text
treated firm 池内基金持仓数据覆盖率 >= 95%
ActiveEquity / TechThemed / AIThemed / Northbound / Passive 5 个 sleeve
    每个均有 >= 50 只独立基金/通道
基金分类映射 inter-coder 一致性 >= 0.85
```

### 11.3 第三步：Pre-trend 与基率

最小版本 event study（不带匹配）：

```text
Y1a 在 β_{-4}, β_{-3}, β_{-2} 是否接近 0
Y1a 在 β_0, β_1, β_2 是否有正向迹象
Y1e 在所有 β 是否都 ≈ 0
```

Go/no-go：

```text
pre-trend joint F-test p-value > 0.20
Y1a 至少在 β_0 或 β_1 显著正
Y1e 全部不显著（关键 placebo）
```

任一不过，要么换 Y1e 定义，要么改识别。

---

## 12. 主表与图

### Table 1：样本构造与描述统计

- treated / never-treated / not-yet-treated 三组样本量；
- CAC 备案批次按季度分布；
- 基金 sleeve 样本规模（基金数量、净资产、持 A 股市值）；
- pre-period 协变量均值差异（PSM 前 vs 后）。

### Table 2：Pre-trend & event-study

- 主回归 β_{-4} 到 β_8 报告；
- 五个 Y（Y1a-Y1e）并列；
- pre-trend joint F-test；
- 配 Figure 1 event-study plot。

### Table 3：talk-walk × verification 2x2 网格

- 四象限的 Y3（媒体语调分歧）、Y5（CAR(-3,+3)）、Y4（融券余额变化）；
- 跨象限差异 t-test。

### Table 4：稳健性与真实兑现

- 时间 placebo、anchor placebo、Y placebo；
- 主表跨匹配方法对照；
- Heckman 自选择修正；
- Real-outcome：Y6 销售增长。

### Figure 1：Event-time path of Y1a-Y1e

横轴 -4 到 +8 quarters；纵轴 ATT ± 95% CI；五线分别对应五个 sleeve。

### Figure 2：CAR around batch date with placebo

CAR(-5,+5) 真 batch 日 vs 10 个随机 placebo 日。

---

## 13. 暂时不进入主实验的内容

- 分析师预测变化（v10B 主问题，不放本文）；
- claim-level specificity × verified support（v8.1，第二篇）；
- 供应链 GenAI 扩散（v10 supply-chain，第二篇）；
- DeepSeek 单独事件研究；
- AI washing 重做。

---

## 14. 当前版本的硬判断

本实验成立的条件：

1. CAC 备案能穿透 ≥ 150 家上市公司；
2. 备案批次在 staggered 8 批以上分布；
3. 基金持仓数据 5 个 sleeve 都有足够规模；
4. pre-trend 通过；
5. 被动指数基金 Y placebo 通过（关键）；
6. Y anchor placebo（医药/消费基金）通过。

任一不通过，不补救。

最终论文问题：

```text
Regulatory verification and institutional reallocation:
Evidence from China's GenAI service registration
```

主贡献：

1. 首次用第三方监管验证（CAC 备案）作为 GenAI 采用的硬 X；
2. 首次记录监管验证信号引发的、按基金风格 sleeve 分化的机构资本重新分配；
3. talk-walk × verification 2x2 网格区分实质化采用与潜在 washing。
