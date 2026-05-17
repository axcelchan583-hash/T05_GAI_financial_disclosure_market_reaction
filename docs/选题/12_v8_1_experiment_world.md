# v8.1 实验世界：When Is Specific GenAI Disclosure Credible?

**日期**：2026-05-17  
**目的**：只固定主实验。暂不讨论股价、分析师、监管、投稿包装或显著性。  
**一句话**：在 claim-level 上检验 specific disclosure 的可信度是否取决于 contemporaneous observable capability support。

---

## 0. 本版只回答什么

本版只回答一个问题：

> 传统披露理论认为越具体的披露越可信；但在 GenAI 技术热潮中，具体性是否可能被企业用来制造“可验证感”？具体 GenAI 能力声明的可信度，是否取决于披露时点是否存在可观察的能力支撑？

更具体地，本版只检验一个主效应：

```text
Specificity × No Current Matched Capability Support
    -> Future Claim-Matched Realization
```

也就是说，本文不问“specificity 平均而言好不好”，而问：

> 在没有当前匹配能力证据支撑时，specificity 是否不再是 credible signal，甚至变成 verifiability illusion？

不回答：

- GenAI 声明是否影响披露日 CAR；
- 市场是否识别 GenAI washing；
- 监管是否问询；
- 分析师是否纠偏；
- 哪个结果更容易显著；
- 论文最终投哪个期刊。

这些都属于主实验成立后的后续扩展。

---

## 0.1 理论命题

传统披露理论给 specificity 一个相对正面的含义：越具体的披露越容易被外部投资者、分析师或监管者验证，因此虚假或夸大披露的声誉成本更高。按这个逻辑，specific disclosure 应该比 vague disclosure 更可信。

但 GenAI 不同。它有三个特征：

1. 技术热潮强，外部注意力高；
2. 技术边界模糊，普通投资者难以实时判断企业是否真的具备能力；
3. 具体产品名、应用场景、合作方、时间表等细节，可能被用来制造一种“似乎可验证”的印象。

因此，specificity 的含义可能是条件性的：

```text
有当前能力支撑：specificity 更像 credible signal
无当前能力支撑：specificity 更像 verifiability illusion
```

本文的主命题不是推翻 specificity 文献，而是提出一个边界条件：

> Specific disclosure is credible only when it is supported by contemporaneous observable capability.

对应到 GenAI 场景：

> Unsupported specific GenAI capability claims are less likely to be realized.

---

## 1. 理想实验

如果能随机实验，理想设计是：

1. 对同一类 GenAI capability claim，随机让部分 claim 有当前硬证据支撑，部分没有；
2. 同时随机控制 claim 的具体性高低；
3. 观察未来 4 个季度内 claim 是否被对应硬证据兑现。

现实中不能随机，所以用自然数据构造一个 claim-level 2x2 对照。

---

## 2. 分析单元

主分析单元：

```text
claim c × firm i × date/quarter t
```

每条 claim 是一条前瞻性 GenAI 能力声明。

进入主样本的 claim 必须同时满足：

1. 是 GenAI-specific，不是泛 AI / 数字化 / 智能制造；
2. 是 forward-looking capability claim，不是已经完成事项的描述；
3. 可以映射到至少一种未来硬证据类型；
4. 可以识别 claim date、firm id、source、claim type。

---

## 3. 主实验 2x2

两个维度：

```text
HighSpecificity_cit
NoCurrentMatchedCapabilitySupport_cit
```

形成四格：

| | 有当前匹配硬证据 | 无当前匹配硬证据 |
|---|---|---|
| 高具体性 | Credible specific claim | **Unsupported specific claim / verifiability illusion** |
| 低具体性 | Supported vague claim | Unsupported vague claim |

核心比较不是“高具体性 vs 低具体性”的平均差异，而是 specificity 的斜率是否取决于 current support：

> 有当前能力支撑时，specificity 是否更容易对应未来兑现；没有当前能力支撑时，specificity 是否反而更难兑现？

主效应：

```text
HighSpecificity × NoCurrentMatchedCapabilitySupport -> FutureMatchedRealization
```

预期：

```text
β3 < 0
```

解释：

> 具体性本身不是问题；问题是没有当前可观察能力支撑的具体性。它可能不再传递可信信号，而是在 GenAI 热潮中制造可验证感。

---

## 4. 主 X

### 4.1 HighSpecificity

对每条 forward-looking GenAI claim 给 0-5 分：

```text
+1 if 具体产品 / 模型名 / 平台名
+1 if 具体业务场景
+1 if 具体时间表
+1 if 具体合作方
+1 if 具体业务线 / 部门 / 子公司主体
```

主定义：

```text
HighSpecificity = 1[SpecificityScore >= 3]
```

稳健性：

```text
SpecificityScore continuous
HighSpecificity = 1[SpecificityScore >= 2]
HighSpecificity = top tercile within claim type × source
```

### 4.2 NoCurrentMatchedCapabilitySupport

对每条 claim，在 claim date 之前到当期检查是否存在匹配硬证据：

```text
NoCurrentMatchedCapabilitySupport = 1
```

如果：

```text
current matched capability support in [t-4, t] = 0
```

这里的 `t` 可以是 claim 所在季度；如果有日度数据，则用 claim date 前 365 天到 claim date。

Current support 只能使用 claim 发生前或当期已经公开可观察的能力证据，不能使用未来证据。

### 4.3 主 X 的透明写法

主表不直接只放一个 `UnsupportedSpecificClaim` dummy，而是放完整交互。这样能同时显示 specificity 在有支撑和无支撑两种状态下的不同含义：

```text
RealizedClaim
= β1 HighSpecificity
+ β2 NoCurrentMatchedCapabilitySupport
+ β3 HighSpecificity × NoCurrentMatchedCapabilitySupport
+ controls + FE + ε
```

唯一主系数：

```text
β3
```

主解释：

```text
β3 < 0
```

即：

> 在没有当前匹配能力支撑时，高具体性 GenAI claim 的未来兑现概率更低。

---

## 5. 主 Y

### 5.1 FutureMatchedRealization

主 Y：

```text
FutureMatchedRealization_cit = 1
```

如果 claim 后未来 4 个季度内出现与该 claim 类型和内容匹配的硬证据：

```text
matched evidence in (t, t+4] > 0
```

否则：

```text
FutureMatchedRealization_cit = 0
```

### 5.2 Claim type -> evidence type 映射

| Claim type | Future matched evidence |
|---|---|
| Foundation-model claim | 自研 LLM 产品上线、CAC 备案、模型相关专利、LLM 工程师招聘 |
| Application-integration claim | 对应应用产品上线、软著、合作公告、业务流程相关招聘 |
| Specific product/application claim | 同名或同业务线产品发布、软著、备案、专利、官网/公众号上线 |
| Internal workflow claim | 内部工具上线、相关软著、相关岗位招聘、IR/公告中的落地说明 |
| Generic AI transformation | 不进入主回归；只统计为 unverifiable claim |

### 5.3 Verifiable claim filter

低具体性、无法映射证据类型的 generic claims 不直接记为未兑现。

先定义：

```text
VerifiableClaim_cit = 1
```

当且仅当该 claim 可以匹配到一个明确的 evidence type。

主回归样本：

```text
VerifiableClaim = 1
```

描述统计必须报告：

```text
unverifiable claims share
```

这是重要事实，但不是主 Y。

---

## 6. X/Y 接近性隔离规则

这是主实验能否成立的关键。

### 6.1 时间隔离

X 只用：

```text
[t-4, t]
```

Y 只用：

```text
(t, t+4]
```

同一硬证据不能同时用于 X 和 Y。

这里的时间隔离是区分 X 和 Y 的底线：

```text
X = claim 当时是否有能力支撑
Y = claim 之后是否出现匹配兑现证据
```

如果同一证据同时参与 current support 和 future realization，主实验不成立。

### 6.2 同日事件排除

如果 claim 与 evidence 同日出现：

- 若文本是“已经上线 / 已完成 / 已取得”，它不是 forward-looking claim，不进主样本；
- 若文本是“计划上线”，但同一公告附件已经给出上线证据，则该证据算 current evidence，不算 future realization；
- 同一事项后续重复公告，不算新增 realization。

### 6.3 名称匹配优先

高具体性 claim 中如有产品名、模型名、合作方名，future evidence 必须优先按名称匹配。

如果不能名称匹配，只能按 broad claim-type 匹配，则标记：

```text
MatchConfidence = broad
```

主表使用：

```text
high-confidence match
```

broad match 只作稳健性。

---

## 7. 主回归

### 7.1 Claim-level LPM

```text
FutureMatchedRealization_cit
    = β1 HighSpecificity_cit
    + β2 NoCurrentMatchedCapabilitySupport_cit
    + β3 HighSpecificity_cit × NoCurrentMatchedCapabilitySupport_cit
    + ClaimControls_cit
    + FirmControls_it
    + FirmFE_i
    + ClaimTypeFE_k
    + SourceFE_s
    + IndustryQuarterFE_jt
    + ε_cit
```

主系数：

```text
β3 < 0
```

### 7.2 Logit

稳健性：

```text
Pr(FutureMatchedRealization = 1)
    = Logit(HighSpecificity
            + NoCurrentMatchedCapabilitySupport
            + HighSpecificity × NoCurrentMatchedCapabilitySupport
            + controls + FE)
```

### 7.3 标准误

主表：

```text
cluster by firm
```

稳健性：

```text
two-way cluster by firm and quarter
cluster by industry-quarter
```

---

## 8. 控制变量

### 8.1 Claim controls

- claim length;
- forward-looking strength;
- source: annual report / announcement / IIP / IR;
- claim type;
- document position;
- repeated claim indicator;
- whether product/model/partner name appears.

### 8.2 Firm controls

- size;
- leverage;
- ROA;
- Tobin Q / MTB;
- analyst coverage;
- institutional ownership;
- prior AI/digital foundation;
- prior innovation output;
- prior regulatory scrutiny;
- industry GenAI exposure.

---

## 9. 最小 pilot

### 9.1 Pilot 样本

先做 100-300 条 claim，不做全市场。

来源优先级：

1. 2023-2025 年公告；
2. 年报 MD&A / 业务讨论；
3. 投资者关系活动记录；
4. 互动易 / e 互动。

### 9.2 Pilot 要回答三件事

1. claim 能否稳定抽取？
2. claim 能否被分成 verifiable / unverifiable？
3. 未来 evidence matching 的人工一致性是否足够？

### 9.3 Go / no-go 门槛

继续推进的最低门槛：

```text
verifiable claim share >= 30%
high-confidence match precision >= 80%
four-cell minimum count >= 30 per cell in pilot expansion
future realization event count >= 50 after first expansion
inter-coder kappa >= 0.70
```

如果达不到，主实验不成立，不进入全样本。

---

## 10. 主表

只保留四张主表。

### Table 1: Claim taxonomy

- claim count by source;
- claim type distribution;
- specificity distribution;
- verifiable / unverifiable share;
- current evidence share;
- future realization share.

### Table 2: 2x2 realization rates

四格均值表：

| | Current support = 1 | Current support = 0 |
|---|---|---|
| High specificity = 1 | realization rate | realization rate |
| High specificity = 0 | realization rate | realization rate |

核心描述事实：

```text
High specificity 在 no-current-support 组是否反而兑现率更低。
```

### Table 3: Main regression

主回归：

```text
HighSpecificity × NoCurrentMatchedCapabilitySupport -> FutureMatchedRealization
```

### Table 4: Measurement robustness

- high-confidence vs broad match;
- t+4 vs t+8;
- formal-only vs all channels;
- alternative specificity threshold;
- excluding repeated claims;
- excluding same-event evidence.

---

## 11. 暂时不进入主实验的内容

以下内容不进入 v8.1 主实验：

- disclosure-day CAR;
- long-window BHAR;
- analyst forecast revision;
- regulatory inquiry;
- institutional ownership change;
- DeepSeek transition matrix;
- firm-quarter GenAI washing gap;
- Good Walker / Washer / Stealth Doer / Silent classification.

这些可以作为后续论文包装或第二阶段扩展，但不能干扰主实验。

---

## 12. 当前版本的硬判断

本实验世界成立的条件不是回归显著，而是：

1. claim 能否被清楚抽取；
2. high specificity 和 current support 能否独立编码；
3. future matched realization 能否被高置信度匹配；
4. 四格样本是否足够；
5. `HighSpecificity × NoCurrentMatchedCapabilitySupport` 是否有清晰解释。

如果这些成立，主实验就是：

```text
Unsupported Specificity -> Future Claim-Matched Realization
```

如果这些不成立，就不应该再用股价、分析师或监管结果去补救。

最终论文问题可以写成：

```text
When is specific disclosure credible?
Evidence from GenAI capability claims
```
