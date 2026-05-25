# v8.3 实验设计：When Is Specific GenAI Disclosure Credible?

**日期**：2026-05-17
**定位**：主实验设计，不讨论股价、分析师、监管、DeepSeek 或投稿包装。
**一句话**：在 GenAI 热潮中，无当前能力支撑的具体声明是否仍是 credible signal。

---

## 0. 本地 PDF 快捷链接

**文献目录**：`/Users/mac/computerscience/23选题探索/bib/GenAI文献`

| 组别 | 文献 | 本地 PDF |
|---|---|---|
| P0 主实验 | Hutton, Miller, Skinner (2003), JAR | [The Role of Supplementary Statements with Management Earnings Forecasts](</Users/mac/computerscience/23选题探索/bib/GenAI文献/The Role of Supplementary Statements with Management Earnings Forecasts.pdf>) |
| P0 主实验 | Rogers and Stocken (2005), TAR | [Credibility of Management Forecasts](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Credibility of Management Forecasts.pdf>) |
| P0 主实验 | Baker et al. (2024), JAR | [Diversity Washing](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Diversity Washing.pdf>) |
| P0 主实验 | Chu et al. (2025), RAS | [New Product Announcements, Innovation Disclosure, and Future Firm Performance](</Users/mac/computerscience/23选题探索/bib/GenAI文献/New Product Announcements, Innovation Disclosure, and Future Firm Performance.pdf>) |
| P0 主实验 | Hassan et al. (2019), QJE | [Firm-Level Political Risk - Measurement and Effects](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Firm-Level Political Risk - Measurement and Effects.pdf>) |
| P0 主实验 | Babina et al. (2024), JFE | [Artificial Intelligence, Firm Growth, and Product Innovation](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Artificial Intelligence, Firm Growth, and Product Innovation.pdf>) |
| P0 主实验 | Cheng et al. (2019), MS | [Riding the Blockchain Mania - Public Firms Speculative 8-K Disclosures](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Riding the Blockchain Mania - Public Firms Speculative 8-K Disclosures.pdf>) |
| P1 竞争文献 | Barrios, Campbell, Johnson, Liu (2025) | [Artificially Intelligent or Artificially Inflated - Determinants and Informativeness of Corporate AI Disclosures](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Artificially Intelligent or Artificially Inflated - Determinants and Informativeness of Corporate AI Disclosures.pdf>) |
| P1 竞争文献 | Jia, Li, Ma, Xu (2025), RAS | [Corporate Responses to Generative AI - Early Evidence from Conference Calls](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Corporate Responses to Generative AI - Early Evidence from Conference Calls.pdf>) |
| P1 竞争文献 | Donelson et al. (2025) | [Strategic AI Disclosures - Determinants and Consequences of Obfuscated and Overstated AI Investments](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Strategic AI Disclosures - Determinants and Consequences of Obfuscated and Overstated AI Investments.pdf>) |
| P1 竞争文献 | Li (2025) | [AI Washing](</Users/mac/computerscience/23选题探索/bib/GenAI文献/AI Washing.pdf>) |
| P1 竞争文献 | Song et al. (2026), FRL | [AI Washing - Strategic Disclosure and Backlash](</Users/mac/computerscience/23选题探索/bib/GenAI文献/AI Washing - Strategic Disclosure and Backlash.pdf>) |
| P1 竞争文献 | Bertomeu, Lin, Liu, Ni (2026) | [AI Information Processing, Misinformation, and Voluntary Disclosure - Theory and Evidence](</Users/mac/computerscience/23选题探索/bib/GenAI文献/AI Information Processing, Misinformation, and Voluntary Disclosure - Theory and Evidence.pdf>) |
| P1 竞争文献 | Bertomeu, Lin, Liu, Ni (2025), JAE forthcoming | [The Impact of Generative AI on Information Processing - Evidence from the Ban of ChatGPT in Italy](</Users/mac/computerscience/23选题探索/bib/GenAI文献/The Impact of Generative AI on Information Processing - Evidence from the Ban of ChatGPT in Italy.pdf>) |

---

## 1. 研究问题

> 在缺乏当前匹配硬证据时，GenAI 能力声明的具体性是否仍正向预测未来兑现？

本文不问：

```text
Specificity 平均而言是否有用
```

而问：

```text
Specificity 的可信度是否取决于 current observable capability support
```

**前人怎么做**：
[Hutton, Miller, and Skinner (2003, JAR)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/The Role of Supplementary Statements with Management Earnings Forecasts.pdf>) 研究管理层预测中的 supplementary statements，核心逻辑是：更具体、可验证的补充信息会提高披露可信度。[Rogers and Stocken (2005, TAR)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Credibility of Management Forecasts.pdf>) 从理论上说明，披露可信度取决于外部识别偏误的能力。

**我们为什么这样做**：
GenAI 热潮下，具体性可能不是单纯的可信信号，而可能被企业用来制造“可验证感”。所以本文把传统 specificity-as-credible-signal 命题条件化：specificity 是否可信，取决于披露当时是否存在可观察能力支撑。

---

## 2. 实证模型

```text
HighSpecificity ──► FutureMatchedRealization
        │
        │  conditional on
        ▼
NoCurrentMatchedCapabilitySupport
```

主命题：

```text
∂Realization / ∂Specificity | NoSupport=1 ≤ 0
```

**前人怎么做**：
[Baker et al. (2024, JAR)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Diversity Washing.pdf>) 不是 DID，而是把披露与真实 workforce diversity 做相对位置比较，再用 penalties、negative news、future hiring、ESG ownership 等外部结果验证。[Chu et al. (2025, RAS)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/New Product Announcements, Innovation Disclosure, and Future Firm Performance.pdf>) 也不是 DID，而是用 disclosure residual 预测未来销售、SG&A、earnings 和公告期 CAR。

**我们为什么这样做**：
本文也不硬做 DID。主实验是 claim-level credibility validation：用披露时点的 specificity 和 current support 预测未来 claim-matched realization。识别语言应写成 lead-lag validation / credibility test，而不是 causal DID。

---

## 3. 分析单元

```text
claim c × firm i × claim date / quarter t
```

进入主样本的 claim 必须同时满足：

```text
GenAI-specific
forward-looking
verifiable
```

即它必须是关于 GenAI 能力的前瞻性声明，并且能映射到至少一种未来硬证据类型。

**前人怎么做**：
[Chu et al. (2025, RAS)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/New Product Announcements, Innovation Disclosure, and Future Firm Performance.pdf>) 同时在 announcement-level 和 firm-quarter-level 构造 innovation disclosure，并用未来公司表现做验证。[Hutton et al. (2003, JAR)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/The Role of Supplementary Statements with Management Earnings Forecasts.pdf>) 的补充说明本质上也是 disclosure-event / forecast-level 的信息内容测试。

**我们为什么这样做**：
本文研究的是“单条 GenAI capability claim 是否可信”，所以分析单元必须下沉到 claim-level。若聚合到 firm-quarter，claim specificity、current support 和 future realization 会被混在一起，容易重新变成 firm-level talk-walk gap。

---

## 4. 变量

### 4.1 X：HighSpecificity

```text
HighSpecificity_cit ∈ {0,1}
```

五项打分：

```text
产品 / 模型名
业务场景
时间表
合作方
业务主体 / 部门 / 子公司
```

主定义：

```text
HighSpecificity = 1[SpecificityScore ≥ 3]
```

**前人怎么做**：
[Hutton et al. (2003, JAR)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/The Role of Supplementary Statements with Management Earnings Forecasts.pdf>) 的关键不是“字数多”，而是披露是否带有可验证补充信息。[Chu et al. (2025, RAS)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/New Product Announcements, Innovation Disclosure, and Future Firm Performance.pdf>) 的 innovation words 也先经过词典构造和人工语境检查，避免把普通修辞当作创新披露。

**我们为什么这样做**：
本文的 specificity 不用泛泛的文本长度或 AI 词频，而只数能让 claim 更可核验的细节。0-5 分不是直接照搬 Hutton，而是把其“可验证补充信息”思想迁移到 GenAI capability claims。

### 4.2 Z：NoCurrentMatchedCapabilitySupport

```text
NoCurrentMatchedCapabilitySupport_cit ∈ {0,1}
```

定义：

```text
claim date 前 365 天至 claim date
不存在与该 claim type 匹配的公开能力证据
```

这里不用 `M`，避免被误解为 mediator。它是 moderator / conditioning variable。

**前人怎么做**：
[Baker et al. (2024, JAR)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Diversity Washing.pdf>) 把 DEI disclosure 与实际 workforce diversity 分开测量，核心是 disclosure 与 underlying action 的相对差异。[Barrios et al.](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Artificially Intelligent or Artificially Inflated - Determinants and Informativeness of Corporate AI Disclosures.pdf>) 的 AI disclosure 文献也用 AI human capital 作为企业真实 AI 投入的 baseline。

**我们为什么这样做**：
本文把“真实支撑”放到 claim date 之前，只判断披露当时是否已有可观察能力基础。这样 current support 是 X 的条件变量，而不是未来兑现结果。

### 4.3 Y：FutureMatchedRealization

```text
FutureMatchedRealization_cit ∈ {0,1}
```

定义：

```text
claim date 后 4 个季度内
出现与该 claim type 匹配的硬证据
```

**前人怎么做**：
[Chu et al. (2025, RAS)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/New Product Announcements, Innovation Disclosure, and Future Firm Performance.pdf>) 用未来销售、SG&A 和 earnings 检验 innovation disclosure 是否包含未来信息。[Baker et al. (2024, JAR)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Diversity Washing.pdf>) 用 future diversity hiring 检验 diversity washers 是否只是提前披露未来改善。[Babina et al. (2024, JFE)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Artificial Intelligence, Firm Growth, and Product Innovation.pdf>) 用 AI human capital 与产品创新等真实结果刻画 AI 投资兑现。

**我们为什么这样做**：
本文的 Y 不是再测一遍披露文本，而是看未来是否出现 claim-matched hard evidence。它的功能是验证 claim 的事后兑现，而不是直接判定企业是否造假。

---

## 5. 证据映射

| Claim type | Matched hard evidence |
|---|---|
| Foundation-model claim | CAC 备案、模型产品上线、模型专利、LLM 工程师招聘 |
| Application-integration claim | 应用产品上线、软著、合作公告、业务流程相关招聘 |
| Specific-product claim | 同名产品发布、软著、备案、专利、官网/公众号上线 |
| Internal-workflow claim | 内部工具上线、相关软著、岗位招聘、后续 IR / 公告落地说明 |

Generic AI transformation 不进主回归，只统计为 unverifiable claims。

**前人怎么做**：
[Baker et al. (2024, JAR)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Diversity Washing.pdf>) 的说服力来自多源外部验证，不只依赖一份 SEC filing。[Hassan et al. (2019, QJE)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Firm-Level Political Risk - Measurement and Effects.pdf>) 的文本测度也强调主题词、语境与外部经济变量之间的验证，而不是纯词频。

**我们为什么这样做**：
GenAI claim 的可验证性取决于 claim type。基础模型、应用接入、具体产品和内部流程不能用同一套证据机械匹配。分类型映射可以降低“自造 Y”的风险。

---

## 6. 时间隔离

```text
Current support: claim date 前 365 天至 claim date
Future realization: claim date 后 4 个季度
```

硬规则：

```text
同一证据不得同时进入 Z 与 Y
同日“已完成 / 已上线 / 已取得”不算 forward-looking claim
同一事项重复公告不算新增 realization
```

**前人怎么做**：
[Chu et al. (2025, RAS)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/New Product Announcements, Innovation Disclosure, and Future Firm Performance.pdf>) 用 disclosure residual 预测未来表现，而不是把同期结果混入主 Y。[Baker et al. (2024, JAR)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Diversity Washing.pdf>) 在回应 aspirational disclosure 解释时，也看未来 workforce diversity 是否改善。

**我们为什么这样做**：
这是区分 X/Z 与 Y 的底线。没有时间隔离，本文会被质疑为“用同一组硬证据同时定义支撑和兑现”。

---

## 7. 主回归

```text
Y_cit = β1 HighSpecificity_cit
      + β2 NoCurrentMatchedCapabilitySupport_cit
      + β3 HighSpecificity_cit × NoCurrentMatchedCapabilitySupport_cit
      + ClaimControls_cit
      + FirmControls_it
      + FirmFE
      + ClaimTypeFE
      + SourceFE
      + IndustryQuarterFE
      + ε_cit
```

主检验：

```text
β3 < 0
```

含义：

```text
无当前能力支撑会削弱 specificity 对未来兑现的正向预测力
```

强检验：

```text
β1 + β3 ≤ 0
```

含义：

```text
在无当前能力支撑时，specificity 不再是 credible signal
```

标准误：

```text
cluster by firm
robustness: two-way cluster by firm and quarter
```

**前人怎么做**：
[Baker et al. (2024, JAR)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Diversity Washing.pdf>) 主体是 logit / OLS validation regressions；[Chu et al. (2025, RAS)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/New Product Announcements, Innovation Disclosure, and Future Firm Performance.pdf>) 用 panel OLS、固定效应和 firm / fiscal-quarter 双重聚类；两者都不是 DID。v6 已明确本项目应定位为 association rather than causation。

**我们为什么这样做**：
本文的主系数不是处理效应，而是 credibility slope change。`β3` 检验 current support 是否改变 specificity 的含义，`β1 + β3` 检验无支撑时 specificity 的净效应是否非正。

---

## 8. H1

> 在缺乏当前匹配硬证据时，更高的具体性不再正向预测未来兑现，甚至转为负向。

对应检验：

```text
主检验：β3 < 0
强检验：β1 + β3 ≤ 0
```

**前人怎么做**：
[Hutton et al. (2003, JAR)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/The Role of Supplementary Statements with Management Earnings Forecasts.pdf>) 给出 specificity / verifiability 提升可信度的基准命题。[Rogers and Stocken (2005, TAR)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Credibility of Management Forecasts.pdf>) 说明可信度会随着管理层激励和外部识别能力变化。[Cheng et al. (2019, MS)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Riding the Blockchain Mania - Public Firms Speculative 8-K Disclosures.pdf>) 说明技术热潮中存在 speculative technology disclosure。

**我们为什么这样做**：
H1 不是说 specificity 本身坏，而是说在 GenAI hype setting 中，unsupported specificity 可能成为 verifiability illusion。

---

## 9. Pilot 门槛

```text
verifiable claim share              ≥ 30%
high-confidence match precision     ≥ 80%
inter-coder kappa                   ≥ 0.70
four-cell minimum sample            ≥ 30
core cell sample                    ≥ 50
future realization events           ≥ 50
```

其中 core cell 指：

```text
HighSpecificity = 1 且 NoCurrentMatchedCapabilitySupport = 1
```

未过门槛：

```text
不进全样本
不改用股价 / 分析师 / 监管结果补救
```

**前人怎么做**：
[Baker et al. (2024, JAR)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/Diversity Washing.pdf>) 依赖多源 external validation 支撑 washing proxy；[Chu et al. (2025, RAS)](</Users/mac/computerscience/23选题探索/bib/GenAI文献/New Product Announcements, Innovation Disclosure, and Future Firm Performance.pdf>) 对 innovation dictionary 做人工语境检查；文本测度类顶刊通常报告人工标注一致性、误判审计或外部验证。

**我们为什么这样做**：
v8.3 最大风险不是没有 DID，而是 claim extraction、specificity coding 和 hard-evidence matching 不可靠。Pilot 门槛用于先判断测度是否能站住，而不是为了追显著性。

---

## 10. 本版不做什么

暂不进入主实验：

```text
disclosure-day CAR
long-window BHAR
analyst forecast revision
regulatory inquiry
institutional ownership
DeepSeek transition matrix
firm-quarter GenAI washing gap
Good Walker / Washer / Stealth Doer / Silent classification
```

这些可以作为后续扩展，但不能干扰主实验。

---

## 11. 最终定位

本文不是 DID 论文。

更准确的定位是：

```text
claim-level disclosure credibility validation design
```

最终论文问题：

```text
When is specific disclosure credible?
Evidence from GenAI capability claims
```

最小可发表主线：

```text
Specificity × No Current Capability Support
    -> Future Claim-Matched Realization
```
