# 研究设计 v8：Unsupported Specificity and GenAI Claim Verification

**用途**：给 ChatGPT Pro 做审稿式 deep research / research-design audit
**日期**：2026-05-16
**核心变化**：从 v7 的 firm-quarter washing gap 转为真正的 claim-level verification；只保留一个主效应。

---

## 0. 请 ChatGPT Pro 优先审的三个问题

请不要先润色这个设计。请先像审稿人一样判断以下三个问题：

1. **X 和 Y 会不会太接近？**
   - X 是否用了与 Y 相同的硬证据？
   - 即使 X 用当前/历史证据、Y 用未来证据，是否仍然只是“有基础的公司未来更容易继续有结果”？
   - `Unsupported Specific Claim` 是否会机械预测 `Claim-Matched Realization`？

2. **X 和 Y 是否都有 AJG 4 星以上或同等级顶刊文献的直接背书？**
   - `claim specificity` 是否有 JAR/TAR/JAE/JF/MS/QJE 级别的测度锚点？
   - `observable hard evidence / AI investment / product innovation` 是否有 JFE/QJE/MS 级别锚点？
   - `claim-matched realization` 是否有顶刊直接锚点，还是仍然是我们自己新构造的 Y？
   - 如果 Y 没有直接顶刊锚点，能否用 management forecast accuracy / product-announcement realization / innovation output 文献合法支撑？

3. **这个研究是否真的能发出来？**
   - 它是否只是 AI washing 文献的 claim-level 变体？
   - 它是否比 Barrios et al., Li (2025), Donelson et al., Song et al., Jia et al. 等 AI/GenAI disclosure-action gap 文献有清晰增量？
   - 目标投 JBFA / CAR / ABR / EAR 是否合理？还是更适合信息系统、管理、创新或中文期刊？

请直接给硬判断：**做 / 不做 / 怎么改后可做**。

---

## 1. 一句话研究问题

> 在 GenAI 这种快速演化的新技术场景中，企业做出的**具体但缺乏当前可观察支撑的 GenAI 能力声明**，未来是否更不可能被对应硬证据兑现？

更短的英文版：

> Are unsupported specific GenAI capability claims less likely to be realized?

---

## 2. 核心直觉

既有 disclosure 文献通常认为，越具体的披露越可信，因为具体披露更容易被事后验证，也更可能带来声誉成本或监管成本。

但在 GenAI 热潮中，specificity 可能有两种含义：

1. **Credible specificity**：企业已经有相关能力基础，所以敢说具体产品、场景、时间表或合作方。
2. **Unsupported specificity**：企业没有可观察能力基础，却给出具体 GenAI 计划，用具体性制造可信感。

因此，本文不研究简单的：

```text
Specificity -> Realization
```

而研究：

```text
Unsupported Specific Claim -> Lower Claim-Matched Realization
```

这保留了一个主效应，但比“越具体越可信”更有张力。

---

## 3. 分析单元

主分析单元是 **claim-level observation**：

```text
claim c, firm i, quarter/date t
```

每条 claim 是一条 forward-looking GenAI capability statement，例如：

- “公司计划于 2024 年上线 XX 智能客服系统。”
- “公司正在推进大模型与研发流程的深度融合。”
- “公司将接入 DeepSeek / 通义千问 / 文心千帆，改造内部知识库问答。”
- “公司正在开发金融领域大模型。”

v7 的 firm-quarter `Disclosure-Capability Gap` 不再作为主 X，只作为附录或控制变量。

---

## 4. 主 X：Unsupported Specific Claim

### 4.1 定义

```text
UnsupportedSpecificClaim_cit
    = 1[SpecificityScore_cit >= threshold]
      × 1[NoCurrentMatchedEvidence_cit = 1]
```

也可以用连续版本：

```text
UnsupportedSpecificity_cit
    = SpecificityScore_cit × NoCurrentMatchedEvidence_cit
```

主表建议同时包含两个组成项，避免把 specificity 和 no-evidence 混在一起：

```text
RealizedClaim_cit
    = beta1 * SpecificityScore_cit
    + beta2 * NoCurrentMatchedEvidence_cit
    + beta3 * SpecificityScore_cit × NoCurrentMatchedEvidence_cit
    + controls + FE + eps
```

论文唯一主效应是：

```text
beta3 < 0
```

解释为：具体性本来可能提高可信度，但当具体声明没有当前可观察能力证据支撑时，其未来兑现概率显著下降。

### 4.2 SpecificityScore

对每条 forward-looking GenAI claim 给 0-5 分：

```text
+1 if 具体产品 / 模型名 / 平台名
+1 if 具体业务场景
+1 if 具体时间表
+1 if 具体合作方
+1 if 具体业务线 / 部门 / 子公司主体
```

需要 ChatGPT Pro 判断：这个 specificity score 是否能被 Hutton, Miller, and Skinner (2003, JAR), Rogers and Stocken (2005, TAR), or related disclosure-specificity / management-forecast literature 充分支撑。

### 4.3 NoCurrentMatchedEvidence

对每条 claim，在 claim date 之前或当期检查是否存在与该 claim 类型匹配的 observable hard evidence。

```text
NoCurrentMatchedEvidence_cit = 1
```

如果在 claim date 前 `t-4` 到 `t` 没有 claim-type matched evidence。

Hard evidence sources:

- AI / GenAI-skilled hiring;
- GenAI-related patent applications;
- GenAI software copyrights;
- GenAI product launches;
- CAC generative AI service filings / algorithm filings;
- concrete cooperation or procurement contracts, if independently observable.

需要注意：这里的 current evidence 不能是未来 Y 的同一事件。它只衡量 claim 发生时企业是否已有可观察能力基础。

---

## 5. 主 Y：Claim-Matched Realization

### 5.1 定义

```text
RealizedClaim_cit = 1
```

如果在 claim 后 `t+1` 到 `t+4` 个季度内，出现与该 claim 类型和内容相匹配的硬证据。

例如：

| Claim 类型 | 未来 matched hard evidence |
|---|---|
| Foundation-model claim | 自研 LLM 产品上线、CAC 备案、模型相关专利、LLM 工程师招聘 |
| Application-integration claim | 对应应用产品上线、软件著作权、合作公告、业务流程相关招聘 |
| Specific product/application claim | 同名或同业务线产品发布、软著、备案、专利、官网/公众号上线 |
| Generic transformation claim | 原则上不进入主样本；只作 descriptive 的 unverifiable claims |

### 5.2 样本限定

主样本只包括 **verifiable forward-looking GenAI claims**。

低 specificity、无法映射到证据类型的 generic claims 不直接编码为 `RealizedClaim = 0`，而是先进入：

```text
VerifiableClaim_cit = 0
```

描述统计中报告“有多少 GenAI claims are unverifiable by design”。这本身可以作为制度性发现，但不是主回归的 Y。

主回归只在：

```text
VerifiableClaim_cit = 1
```

的样本中估计。

---

## 6. 主假设

**H1：Unsupported specificity predicts lower realization.**

> Among verifiable forward-looking GenAI capability claims, claims with higher specificity but no current matched observable evidence are less likely to be realized within the following four quarters.

中文：

> 在可验证的前瞻性 GenAI 能力声明中，缺乏当前可观察能力证据支撑的高具体性声明，未来四个季度内被对应硬证据兑现的概率更低。

这是唯一主假设。

---

## 7. 主回归

### 7.1 Linear Probability Model

```text
RealizedClaim_cit
    = beta1 * SpecificityScore_cit
    + beta2 * NoCurrentMatchedEvidence_cit
    + beta3 * SpecificityScore_cit × NoCurrentMatchedEvidence_cit
    + ClaimControls_cit
    + FirmControls_it
    + FirmFE_i
    + ClaimTypeFE_c
    + SourceFE_s
    + IndustryQuarterFE_jt
    + eps_cit
```

主系数：

```text
beta3 < 0
```

### 7.2 Logit / Conditional Logit

作为稳健性：

```text
Pr(RealizedClaim_cit = 1)
    = Logit(beta1 SpecificityScore
            + beta2 NoCurrentMatchedEvidence
            + beta3 SpecificityScore × NoCurrentMatchedEvidence
            + controls + FE)
```

### 7.3 Standard Errors

至少 firm-level clustering。可考虑 firm and quarter two-way clustering，或 industry-quarter clustering。

---

## 8. 控制变量

### Claim-level controls

- claim length;
- forward-looking strength;
- claim source: annual report / announcement / investor-interaction platform / IR record;
- claim type: foundation model / application integration / specific application / generic transformation;
- whether a partner/model/product name is mentioned;
- document position;
- whether the claim is repeated from prior filings.

### Firm-level controls

- size;
- leverage;
- ROA;
- Tobin Q / MTB;
- analyst coverage;
- institutional ownership;
- pre-period AI/digital foundation;
- industry GenAI exposure;
- prior innovation output;
- prior regulatory scrutiny.

---

## 9. 文献锚点：请 ChatGPT Pro 审核是否足够硬

### 9.1 X 的锚点

**Specificity / claim specificity**

候选锚点：

- Hutton, Miller, and Skinner (2003, JAR): supplementary statements and management forecast credibility;
- Rogers and Stocken (2005, TAR): management forecast credibility;
- Hassan et al. (2019, QJE): firm-level topic text measurement;
- disclosure specificity / quantitative disclosure literature if stronger papers exist.

请 ChatGPT Pro 判断：这些是否足够直接支持 claim-level specificity，还是需要换更贴近的 4* 文献。

**Observable hard evidence / capability baseline**

候选锚点：

- Babina, Fedyk, He, and Hodson (2024, JFE): AI-skilled human capital and product innovation;
- Brynjolfsson, Li, and Raymond (2025, QJE): GenAI deployment and productivity;
- Acemoglu et al. (2022, JOLE): AI-related vacancies;
- Cheng et al. (2019, Management Science): speculative versus existing technology disclosures.

请 ChatGPT Pro 判断：`NoCurrentMatchedEvidence` 是否有足够文献背书，还是仍然像我们自己拼的 variable。

### 9.2 Y 的锚点

`Claim-Matched Realization` 是最大风险。可能的文献锚点包括：

- management forecast accuracy / forecast realization;
- product-announcement realization;
- innovation output: patents, product launches, trademarks;
- AI investment and product innovation literature.

请 ChatGPT Pro 明确判断：

```text
Claim-Matched Realization 是否仍然属于我们自己构造的新 Y？
如果是，它能否因为 claim-level verification framing 而被接受？
有没有 AJG 4* 以上文献已经使用类似 “claim-level realization / forecast-to-realization” 的 Y？
```

---

## 10. 与已有 AI / GenAI washing 文献的关系

已有或相近文献：

- Barrios, Campbell, Johnson, and Liu: AI disclosure vs AI employment / suspected AI washing;
- Li (2025): AI talk vs AI walk;
- Donelson et al. (2025): strategic AI disclosures;
- Song et al. (2026, FRL): AI washing, will-do AI vs done AI;
- Jia et al. (2025, RAS): GenAI responses in conference calls;
- Chu et al. (2025, RAS): residual innovation/product disclosure and future performance;
- Baker et al. (2024, JAR): diversity washing.

v8 的 intended difference：

```text
这些文献多数是 firm-level talk-walk gap。
v8 是 claim-level verification:
specific claim -> matched future hard evidence.
```

请 ChatGPT Pro 判断这个差异是否足够，还是只是把 firm-level washing 换成 claim-level washing。

---

## 11. X/Y 接近性的专门处理

这是本设计最需要被审的地方。

### 11.1 时间切割

X 中的 current evidence 只使用 claim date 之前或当期可观察证据。

Y 只使用 claim date 之后 `t+1` 到 `t+4` 的新增证据。

### 11.2 事件排除

如果同一事件同时生成 claim 和 evidence，则不允许同时进入 X 与 Y。

例如：

- 同一天公告“已上线 XX AI 产品”，这不是 forward-looking claim，不进入主样本；
- 同一天公告“计划上线 XX AI 产品”，但附件已披露产品上线证据，视为 current evidence，不算 future realization；
- 后续重复公告同一事项，不算新增 realization。

### 11.3 主样本限定

只保留 forward-looking claims。已完成事项 claims 作为 current evidence / descriptive，不进入主因果样本。

### 11.4 Verifiability filter

Generic claims 不直接编码为 non-realization，以免把“不可验证”误当“未兑现”。

---

## 12. 数据计划

### 12.1 Claim extraction

文本源：

- CNINFO / 巨潮公告;
- annual reports;
- exchange announcements;
- investor-interaction platform responses;
- investor relations activity records.

主样本可先限制为 formal disclosures：

- announcements;
- annual reports.

IIP / IR 先用于 robustness 或 specificity mechanism。

### 12.2 Claim classification

人工标注 2,000-3,000 条 sentence / claim：

- GenAI or not;
- forward-looking or current;
- claim type;
- specificity score;
- verifiable or not;
- matched evidence type.

训练中文 RoBERTa / FinBERT-style classifier，报告 precision, recall, F1, Cohen's kappa。

### 12.3 Evidence databases

构造 matched hard evidence 库：

- GenAI hiring;
- GenAI patents;
- GenAI software copyrights;
- GenAI product launches from company websites / official WeChat / announcements;
- CAC GenAI service filings;
- cooperation / procurement contracts.

每条 evidence 必须有：

```text
firm_id
date
evidence_type
product/model/entity_name
business_scenario
source_url_or_file
confidence_score
```

### 12.4 Matching

Claim-evidence matching rules:

- exact entity match if product/model/platform name appears;
- fuzzy match for business scenario and claim type;
- manual audit for high-specificity claims;
- separate high-confidence and broad-match versions.

主表用 high-confidence match；broad-match 作稳健性。

---

## 13. 预期表格

只保留 4 张主表。

### Table 1: Claim taxonomy and verifiability

- claim count by source;
- claim type distribution;
- specificity distribution;
- share of unverifiable claims;
- share with current matched evidence.

### Table 2: Main effect

```text
Specificity × NoCurrentMatchedEvidence -> RealizedClaim
```

主系数 `beta3 < 0`。

### Table 3: Robustness and validation

- alternative specificity threshold;
- high-confidence vs broad matching;
- formal-only vs all channels;
- t+4 vs t+8 realization window;
- exclude repeated claims.

### Table 4: Recognition

外部后果，只作验证，不抢主线：

- regulatory inquiry / comment letter after unsupported specific claims;
- analyst forecast revision / dispersion;
- market reaction or long-window correction.

---

## 14. 可能的结论结构

如果主结果成立，本文的结论不是：

```text
GenAI washing exists.
```

而是：

```text
Specific GenAI capability claims are not uniformly credible.
Specificity predicts realization only when it is supported by current observable capability evidence.
Unsupported specificity is associated with lower claim-matched realization.
```

这比 firm-level washing 更窄，但更符合 claim verification。

---

## 15. 请 ChatGPT Pro 给出的最终输出

请输出以下内容：

1. **Verdict**：做 / 不做 / 改后做。
2. **X-Y proximity audit**：逐条说明 X 和 Y 是否太近，如何改。
3. **AJG 4* anchor audit**：
   - X 的每个组成部分有哪些顶刊锚点；
   - Y 是否有顶刊锚点；
   - 哪些地方仍然是我们自己构造。
4. **Competition audit**：是否已有 exact 或 near-exact 文献。
5. **Publishability audit**：JBFA / CAR / ABR / EAR / JCAE / 中文顶刊哪个最合适。
6. **Minimal pilot**：如果只做 100-300 条 claim，应该先验证哪三件事。
7. **Go / no-go threshold**：
   - verifiable claim share 至少多少；
   - matching precision 至少多少；
   - realization event count 至少多少；
   - 主结果需要在什么表里成立才值得继续。

请直接批判，不要为了鼓励而鼓励。
