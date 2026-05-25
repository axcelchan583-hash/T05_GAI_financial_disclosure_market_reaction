# 没有能力支撑的具体 GenAI 声明，会不会更难兑现？

## 基于中国 A 股上市公司 claim 层招聘与专利兑现的研究设计

近期关于企业 AI 披露的研究已经不再仅仅关注企业是否提及 AI，而是进一步追问这些 AI 叙事是否对应真实行动。相关研究通常将企业披露中的 AI 表述视为 “talk”，并以 AI 招聘、AI 专利、员工技能或经营结果作为 “walk” 的外部验证证据（Barrios et al., 2025; Li, 2025; Song et al., 2026）。这一路径为识别 AI washing 提供了重要基础，但现有研究大多停留在企业-年或企业-季层面，难以回答一个更细的问题：同一家企业在不同时间、不同渠道发布的多条 GenAI 能力声明，哪些更可能被后续行动兑现？本文由此将 AI talk-walk gap 从企业层面下沉到单条声明层面。具体而言，本文不直接声称观测企业真实能力，而是构造两个可复核的公开证据变量：一是声明发布前是否存在与该 claim 匹配的公开证据，二是声明发布后是否出现与该 claim 匹配的后续公开行动证据。通过区分“具体且有前置公开证据”的声明与“具体但无前置公开证据”的声明，本文检验 GenAI 能力声明的具体性是否真正具有信息含量，还是在技术高度不透明和投资者高度关注的环境下，仅仅制造了一种看似可验证的可信度。


---

## 一、研究摘要

传统披露理论认为，具体披露比模糊披露更可信，因为具体内容更容易被事后核查（Rogers & Stocken, 2005；Hutton, Marcus, & Tehranian, 2009）。这一逻辑成立的前提是：具体性会带来单向成本——管理层若未能兑现细节性声明，将承担声誉与诉讼成本。生成式人工智能（GenAI）浪潮提供了一个对该前提进行检验的天然实证场景。一方面，外部投资者对 AI 高度关注；另一方面，技术边界对非专业投资者高度不透明；与此同时，"听起来可被验证"的细节——产品名、合作方名、模型名、时间表——可以被低成本地制造，而对这些细节的事后核查机制相对薄弱。

本文在 claim 层提出并检验一个可信度边界框架。研究对象是中国 A 股上市公司在 2023–2026 年期间通过年报、临时公告、投资者关系活动与互动平台发布的前瞻性 GenAI 能力声明。本文要回答的核心问题是：**当企业在声明发出时缺乏当期可观察的能力支撑时，声明的具体性是否仍能预测企业后续的真实行动？**核心命题表述为：

> **GenAI 能力声明的具体性仅在伴有当期可观察能力支撑时才构成可信信号；缺乏能力支撑的具体性更像是一种"可验证感"的制造，而非可信信号。**

研究设计在三个独立度量、来源完全不同、时间尺度互补的结果变量上检验该命题：

- **结果一（短期兑现，招聘）**：声明发出后 4 个季度内，企业的 AI 相关招聘扩张。该变量衡量企业是否在声明之后实际建设了能力相关的人力资本。
- **结果二（中期兑现，专利）**：声明发出后 8 个季度内，企业的 GenAI 相关专利申请。该变量衡量声明是否被转化为可观察的创新产出。
- **结果三（claim-type 匹配兑现）**：声明发出后 4 个季度内是否出现与 claim 类型匹配的硬证据（产品发布、软著、合作生效、CAC 备案）的二元指标。该变量回应"并非每种 claim 类型都自然映射到招聘或专利"的关切。

机制检验进一步考察 unsupported specific claim 是否系统性更密集地出现于管理层短期股价激励较强的企业——CEO 股权激励敏感度（equity delta）较高、临近再融资事件、控股股东股权质押比例较高——与 Stein (1988) 和 Edmans, Fang, & Lewellen (2017) 所刻画的管理层短视行为一致。

中国制度场景在三个方面提供了不同于美国数据的识别优势：第一，深交所互动易与上证 e 互动构成了一个高频、有时间戳的投资者-公司互动公开记录；第二，控股股东股权质押在中国 A 股普遍存在且强制公开，构成了短期股价下跌厌恶动机的可测量异质性；第三，国家互联网信息办公室的生成式 AI 服务备案制度提供了一种政府盖章的能力信号，美国数据无对应物。

---

## 二、研究动机与问题

### 2.1 现象与悖论

GenAI 普遍被认为具有通用目的技术的特征（Brynjolfsson, Rock, & Syverson, 2021；Babina, Fedyk, He, & Hodson, 2024）。其落地依赖于人力资本、组织能力与数据基础设施等大量无形投资，兑现周期长、实时验证困难。投资者的高度关注与实时可验证性的不足共同形成了"披露强调多、真实投入少"的策略性披露动机——新近美国证据将其概括为 "AI washing"（Barrios, Campbell, Johnson, & Liu, 2025；Li, 2025）。

已有文献在公司-年或公司-季层面记录了 AI 言-行（talk-walk）的平均缺口。但现代 GenAI 披露的两个事实使企业层面的推断面临局限。其一，同一家企业在多个渠道、多个时点会发出多条 GenAI 声明，这些声明在具体性、内容、可信度上差异极大。其二，监管者与投资者评价的是单条声明，而非企业-年聚合值。**究竟哪些声明可信、具体性本身在何种条件下携带信息**——这一问题尚未在 claim 层得到回答。

### 2.2 理论张力

现有披露文献对具体性在 GenAI 声明中的作用给出两种对立预测。

**"具体性传递可信"观点**：具体披露伪造成本更高，因而能起到分离信号的作用——只有具备真实能力的企业才会发出细节性声明（Rogers & Stocken, 2005；Hope, Hu, & Lu, 2016）。这一观点下，具体性应当单调地预测兑现。

**"可验证感的制造"观点**：参照 ESG、多元化、区块链领域已有的 washing 研究（Cheng, de Franco, Jiang, & Lin, 2019；Dikolli, Frank, Guo, & Lynch, 2022；Aswani, Raghunandan, & Rajgopal, 2024；Baker, Larcker, McClure, Saraph, & Watts, 2024），当外部核查机制薄弱或延迟时，细节本身可以作为低成本信号被策略性制造。这一观点下，具体性的预测内容应当取决于披露发出时企业是否存在能力的独立证据。

本文将第二种观点形式化为条件性命题并直接检验。

### 2.3 研究问题

本文回答一个主问题：

> **前瞻性 GenAI 能力声明的具体性，在企业缺乏当期可观察能力支撑时，是否仍能预测后续的真实行动？**

以及一个机制问题：

> **unsupported specific claim 是否系统性更频繁地出现在管理层短期股价激励较强的企业中？**

---

## 三、研究假设

三条结果假设在三个相互独立的"行动"度量上检验核心命题。三条假设均按 Rogers & Stocken (2005) 关于管理层预测可信度的传统，以**信息含量条件性**框架表述，而非因果处理效应表述。

**H1（短期招聘）**：高具体性 GenAI 能力声明对预测后续 AI 相关招聘的信息含量，条件于当期可观察能力支撑。具体而言，当不存在当期能力支撑时，具体性对后续招聘的边际预测价值显著更低——或非正。

**H2（中期专利）**：高具体性 GenAI 能力声明对预测后续 GenAI 相关专利申请的信息含量，条件于当期可观察能力支撑。当不存在当期能力支撑时，具体性对后续专利申请的边际预测价值显著更低——或非正。

**H3（claim-type 匹配完整兑现）**：高具体性 GenAI 能力声明对预测后续 claim-type 匹配硬证据兑现的信息含量，条件于当期可观察能力支撑。当不存在当期能力支撑时，具体性的边际预测价值显著更低——或非正。

第四条假设检验管理层激励机制：

**H4（机制）**：unsupported specific GenAI 声明不成比例地出现在管理层短期股权激励较强的企业——CEO 股权激励敏感度（delta）较高、临近再融资事件、控股股东股权质押比例较高。若该模式可在声明前的企业可观察特征上识别，则支持"高具体性 + 无支撑联合分布"的策略性披露解释，并与随机噪声解释相区分。

H1 至 H3 在三套独立度量、独立数据源、不同时间尺度上检验同一核心命题，三者是**并列的主结果**，而非互为稳健性检验。

---

## 四、实证策略

### 4.1 研究场景与样本

实证场景为中国 A 股上市公司 2023 年第一季度至 2026 年第一季度。该窗口的起点对应中国 GenAI 披露的实质性出现——2022 年 11 月 ChatGPT 发布之后，以及 2023 年 8 月《生成式人工智能服务管理暂行办法》生效之后。

GenAI 能力声明从四类渠道抽取：

- 年度报告（管理层讨论与分析、业务概述等章节）；
- 交易所公告与临时披露；
- 投资者关系活动记录；
- 投资者互动平台（深交所互动易、上证 e 互动）。

进入主样本的 claim 必须同时满足：（i）GenAI-specific，即明确涉及生成式 AI、大模型、AIGC 等概念，而非泛泛的 AI、数字化、智能制造；（ii）forward-looking，即对未来能力或行动的前瞻性描述，而非已完成事项的回顾；（iii）可映射到至少一种可验证证据类型。文本抽取流程采用按年训练的动态 Word2Vec 词嵌入，方法上借鉴 Kalyani, Bloom, Carvalho, Hassan, Lerner, & Tahoun (2025) 在专利、招聘信息与电话会议三语料中识别新技术相关短语的研究框架，并参照 Houston et al. (2024) 与 Li (2025) 对中文上市公司披露文本的适配。其后由 LLM 二次过滤，仅保留前瞻性、内生能力建设性质的声明（参照 Huang, Wang, & Yang, 2023 与 Barrios et al., 2025）。本设计在 4.2 与 4.3 节进一步在披露文本、招聘数据与专利登记三个独立语料上做交叉验证（triangulation），其方法学思路与 Kalyani et al. (2025) 的三语料设计直接对应。

分析单元为单条声明：

$$
\text{claim } c \times \text{企业 } i \times \text{季度 } t.
$$

### 4.2 主自变量

两个 claim 层指标共同定义关注的处理变量。

**具体性**。对每条声明按以下五个维度评分（每项 0/1）：（i）是否给出具体产品、模型或平台名；（ii）是否给出具体业务场景；（iii）是否给出明确时间表；（iv）是否给出具体合作方或对手方；（v）是否给出具体业务线、部门或子公司主体。二元主指标为

$$
\text{HighSpecificity}_{cit} = \mathbf{1}[\text{Score} \geq 3].
$$

该分维度评分借鉴 Hope, Hu, & Lu (2016) 对风险披露具体性的多维度刻画，通过人工编码与 LLM 编码相结合的方式实现，目标编码者间一致性（kappa）≥ 0.70。

**当期能力支撑**。如果在声明发生前 4 个季度至声明季度（[t-4Q, t]）内，企业不存在与该声明类型匹配的可观察证据，则该声明被分类为缺乏当期能力支撑。证据池严格限定于公开可核查的信号，且不与结果变量重叠：

| Claim 类型 | 当期能力支撑证据池 |
|---|---|
| 自研基础模型类 | CAC 生成式 AI 服务备案、自研 LLM 产品已上线、命名匹配的已公开专利（仅限模型同名） |
| 应用集成类 | 对应应用产品已上线、相关软件著作权、已生效合作协议 |
| 具体产品/应用类 | 同名产品已发布、软著、备案、命名匹配专利 |
| 内部工作流类 | 已披露的内部工具上线证据 |
| 泛 AI 转型类 | 不进入主样本 |

证据池有两条关键限制。第一，**AI 相关招聘完全不进入证据池**，仅出现在结果变量侧。第二，**专利仅以命名匹配（claim-specific）形式进入证据池**：一项专利能作为支撑，必须其专利名称显式引用声明中提到的产品、模型或平台。企业层面的泛 AI 专利存量不进入证据池。两条限制都是为了避免同一可观察信号同时作为处理变量与结果变量所引入的机械相关。匹配程序遵循"命名匹配优先"原则：当高具体性 claim 包含产品名、模型名或合作方名时，未来证据匹配必须使用命名匹配；更宽的 claim-type 层级匹配仅用于低具体性 claim，并作为稳健性单独报告。

二元主指标为

$$
\text{NoCurrentSupport}_{cit} = \mathbf{1}[\text{[t-4Q, t] 内不存在匹配证据}].
$$

核心处理变量为交互项：

$$
\text{HighSpecificity}_{cit} \times \text{NoCurrentSupport}_{cit}.
$$

### 4.3 主结果变量

**结果一（招聘）**。企业 i 在声明 c 发出后 4 个季度内的 AI 相关招聘占比：

$$
\text{AIHiringShare}_{c,i,(t,t+4Q]} = \frac{\sum_{(\tau,j) \in (t,t+4Q]} \mathbf{1}[j \in \text{GenAI 词典}]}{\sum_{(\tau,j) \in (t,t+4Q]} \mathbf{1}[j \text{ 有有效描述}]}.
$$

岗位通过上市主体识别码匹配到企业，并通过 Babina 式 AI-relatedness score 过滤——仅保留与核心 GenAI 关键词共现率超过阈值的技能。LLM 二次分类剔除仅外围提及 GenAI 的岗位（参照 Babina et al., 2024；Li, 2025；Kalyani et al., 2025）。

进一步构造 claim-type 匹配版本：将 GenAI 词典限定为与声明类型相对应的子集，例如自研基础模型类声明仅匹配 LLM 工程师、提示工程、预训练相关岗位。主表同时报告广义版本与 claim-type 匹配版本。

中国 A 股招聘数据来源包括 CSMAR 与 Wind 结构化招聘数据库，在预试阶段辅以前程无忧、智联招聘、BOSS 直聘与猎聘四大招聘平台的上市公司账号直接抓取。

**结果二（专利）**。企业 i 在声明 c 发出后 8 个季度内的 GenAI 相关专利申请数：

$$
\text{AIPatentFiling}_{c,i,(t,t+8Q]} = (t,t+8Q] \text{ 内的 GenAI 专利申请条数}.
$$

专利来源为国家知识产权局（CNIPA）专利检索及分析系统，对中国申请人在美国专利商标局（USPTO）的申请进行补充。GenAI 分类采用 Giczy, Pairolero, & Toole (2022) 的 8 类 AI 专利分类体系：AI 硬件、进化计算、知识处理、机器学习、自然语言处理、规划与控制、语音、视觉。专利经济价值的构造遵循 Kogan, Papanikolaou, Seru, & Stoffman (2017)。

专利结果的 8 个季度窗口反映了专利申请到公开通常 18 个月的滞后；稳健性中报告 4 个季度与 12 个季度窗口。

**结果三（claim-type 匹配的完整兑现）**。一个二元指标，记录声明 c 之后 4 个季度内是否出现与 claim 类型匹配的硬证据：

$$
\text{ClaimMatchedRealization}_{c,i,(t,t+4Q]} = \mathbf{1}[(t,t+4Q] \text{ 内出现匹配证据}].
$$

匹配证据池在类型上与 4.2 节定义的当期能力支撑证据池完全对称，但完全位于声明后窗口内。对于自研基础模型类声明，匹配证据池包括新的 CAC 生成式 AI 服务备案、新的自研 LLM 产品发布、命名匹配的新公开专利；对于应用集成类声明，包括新的应用产品发布、新的软著、新生效合作协议。这一完整兑现度量回应了如下关切：并非每种 claim 类型都能自然映射到招聘或专利结果——例如"与某云厂商合作上线客服大模型"的真实兑现更适合通过产品是否后续发布、合作是否生效来检验，而非招聘或专利申请。

**三个结果在平行规范下分别检验，并以结构相同的三张主表分别呈现。它们不是互为稳健性检查的关系**：每个度量分别测度不同的经济构念（人力资本能力、创新产出、或 claim-type 匹配的完整兑现），使用独立数据源，作用于不同时间尺度。预期模式是 $\beta_3 < 0$ 在三个结果上一致同向显著，这构成跨异质 Y 度量与异质数据源的内部 replication。

### 4.4 识别策略

对每个结果变量，主回归为

$$
Y_{c,i,h} = \beta_1 \text{HighSpec}_{cit} + \beta_2 \text{NoSupport}_{cit} + \beta_3 \text{HighSpec}_{cit} \times \text{NoSupport}_{cit} + X_{cit}'\gamma + \alpha_i + \alpha_{kt} + \alpha_s + \alpha_{jt} + \varepsilon_{c,i,h},
$$

其中 $Y$ 为招聘、专利或 claim-matched realization 结果之一，$\alpha_i$ 为企业固定效应，$\alpha_{kt}$ 为 claim 类型-季度固定效应，$\alpha_s$ 为披露渠道固定效应（年报、公告、IR、互动平台），$\alpha_{jt}$ 为行业-季度固定效应。

关注系数为 $\beta_3$，预期符号为 $\beta_3 < 0$。系数按 Rogers & Stocken (2005) 的传统以**信息含量条件性**框架解释：在控制企业层与行业-季度层冲击、claim 类型构成、披露渠道选择之后，**当声明发出时不存在当期能力支撑时，具体性对后续真实行动的边际预测价值不再为正**。该估计不解读为具体性对行动的处理效应，而解读为披露信息含量对外部条件的依赖关系。

主回归采用企业层 cluster 标准误。稳健性报告 firm 与 quarter 双向 cluster 与 industry-quarter cluster（Petersen, 2009；Bertrand, Duflo, & Mullainathan, 2004）。

三类识别威胁专门处理：

**披露选择**。发出 GenAI 声明的企业并非随机选样。设计上部分通过企业固定效应（关注企业内不同 claim 之间的具体性-支撑联合分布变异）与样本限制（仅保留至少发出一条 GenAI 声明的企业）应对。$\beta_3$ 的识别来自企业内、行业-季度内不同 claim 之间，具体性与能力支撑的联合分布差异。

**具体-模糊声明的选择性**。这是识别的核心威胁。如果企业根据未来兑现的私有信息策略性选择声明的具体性，$\beta_3$ 可能反映的是逆向选择而非具体性-可信度的条件关系。H4 的机制检验部分回应这一威胁：unsupported specific claim 的联合分布**集中于声明发出之前即可观察的管理层短期激励特征**——如果策略性披露假说成立，那么 unsupported specific claim 的分布必然系统性偏向短期激励较强的企业，而非随机分散。机制检验可在预披露可观察变量上识别出来，构成对策略性披露解释的支持，并相对于"随机噪声"假说构成区分。本框架不消除基于私有信息的根本选择性问题；它记录的是，具体声明的信息含量条件于声明前可观察的能力支撑。

**能力支撑的测量**。人工编码的证据池可能遗漏某些真实能力。为缓解这一担忧，主回归采用高置信度匹配证据（claim 与证据通过命名匹配）；放宽的匹配规则作为测量稳健性。

### 4.5 估计方法

鉴于三个主结果变量统计性质不同，本文在三张主表中采用不同估计量。

对 **AIHiringShare**（[0, 1] 区间内的连续占比变量），主回归采用高维固定效应 OLS，通过 `reghdfe` 估计量实现（Correia, 2017）。这一选择与本文献中 Babina, Fedyk, He, & Hodson (2024) 和 Li (2025) 对类似招聘类结果变量的估计方法保持一致。OLS 设定下交互项 $\beta_3$ 具有透明的线性边际效应解释（Ai & Norton, 2003），且符合 Bertrand, Duflo, & Mullainathan (2004) 所确立的高维固定效应面板回归传统。稳健性中报告 fractional logit（Papke & Wooldridge, 1996, 2008）以处理边界观测值。

对 **AIPatentFiling**（计数变量，零观测密集），主回归采用带高维固定效应的 Poisson 伪极大似然估计，通过 `ppmlhdfe` 估计量实现（Correia, Guimarães, & Zylkin, 2020）。这一选择遵循 Silva & Tenreyro (2006) 对非负计数结果变量的方法论建议，并直接响应 Cohn, Liu, & Wardlaw (2022) 的批评：该文证明公司金融研究中常用的 $\log(1+y)$ OLS 线性回归处理计数变量时，所得系数无自然解释，且存在显著的符号偏误概率。Poisson PML 在严格弱于 Poisson 分布假设的条件下即可一致且有效估计（Cohn, Liu, & Wardlaw, 2022），并支持与招聘设定相同的高维固定效应结构。Poisson 设定下的交互项以乘性效应解释（Ai & Norton, 2003）。稳健性中报告 $\log(1+y)$ OLS（用于与 Li (2025) 的可比性参考）、负二项与零膨胀 Poisson 设定（用于检验条件均值-方差等式假设）。

对 **ClaimMatchedRealization**（二元结果），主回归采用带高维固定效应的线性概率模型（LPM），同样通过 `reghdfe` 实现。LPM 的选择理由是其交互项解释的透明性（Ai & Norton, 2003），以及与招聘 Y 的 OLS 设定保持直接可比。固定效应 logit 作为稳健性报告，其交互效应通过 partial-effects 方法评估。

三个主设定均以企业层 cluster 标准误。稳健性报告 firm 与 quarter 双向 cluster、industry-quarter cluster（Petersen, 2009；Bertrand, Duflo, & Mullainathan, 2004）。

### 4.6 机制检验

机制检验遵循 Stein (1988) 与 Li (2025)。对每个管理层激励变量 $M_{it}$，估计三重交互：

$$
Y_{c,i,h} = \beta_3 \text{HighSpec} \times \text{NoSupport} + \beta_7 \text{HighSpec} \times \text{NoSupport} \times M_{it} + \text{低阶项} + \text{控制变量} + \text{FE} + \varepsilon.
$$

估计量沿用 4.5 节按结果变量分类的规则：招聘 Y 用高维固定效应 OLS，专利 Y 用高维固定效应 Poisson PML。

预期符号 $\beta_7 < 0$：管理层短期股权激励越强，unsupported 具体性对后续真实行动的负向预测越强。

三个激励变量分别构造：

**CEO 股权激励敏感度（delta）**：采用 Coles, Daniel, & Naveen (2006) 的 Black-Scholes-Merton 方法，应用于 CSMAR 高管薪酬与持股数据。

**临近再融资事件**：二元指标，标记声明是否落在再融资公告前 2 个季度——涵盖定向增发、可转债发行、配股、IPO 后窗口。

**控股股东股权质押比例**：声明日控股股东累计股权质押比例。这是衡量短期股价下跌厌恶动机的指标——质押比例越高，控股股东对股价下跌的避损动机越强。中国 A 股市场质押普遍而集中，相对美国数据为该机制提供了更强的识别力（Anderson & Reeb, 2003 提供一般理论锚点）。

国有 vs. 民营所有制作为异质性维度纳入分析：民营企业管理层面临的股价激励更强，而国有企业管理层面临的监管与政策约束更强。预期机制在民营企业中更显著。

---

## 五、数据来源

| 数据类型 | 数据源 |
|---|---|
| 声明文本（年报、公告、IR）| 巨潮资讯、上海证券交易所、深圳证券交易所、北京证券交易所 |
| 声明文本（投资者互动）| 深交所互动易、上证 e 互动 |
| 招聘数据（结构化）| CSMAR、Wind 招聘数据库 |
| 招聘数据（原始抓取，预试）| 前程无忧、智联招聘、BOSS 直聘、猎聘 |
| 专利 | CNIPA 专利检索及分析系统、USPTO |
| 软件著作权 | 中国版权保护中心 |
| GenAI 服务备案 | 国家互联网信息办公室公示 |
| 监管问询函（控制变量）| 上交所/深交所问询函数据库 |
| 财务与所有制数据 | CSMAR、Wind |
| 高管薪酬与股权质押 | CSMAR 高管薪酬表、股权激励计划、股权质押公告 |
| 分析师数据（控制变量）| CSMAR 分析师预测 |

所有数据源均为公开可获取或通过标准学术许可可访问。研究不依赖任何专有或受限访问数据。

---

## 六、预试与时间表

### 6.1 预试阶段

200–300 条人工编码声明（取自 2023–2025 年披露）的预试将完成以下核查：

- HighSpecificity 与 NoCurrentSupport 编码的编码者间一致性（目标 kappa ≥ 0.70）；
- 四格样本分布与最小单元格数量（目标每格 ≥ 30）；
- 4 个季度窗口内招聘数据在企业-季度层的覆盖情况；
- 8 个季度窗口内专利数据在企业-季度层的覆盖情况；
- 两个结果变量的预试回归 $\beta_3$ 估计符号（方向一致性检查，非显著性检验）。

未达 kappa 或样本量阈值将触发对具体性评分规则或 claim 来源池的重新设计，而不直接推进到全样本分析。

### 6.2 时间表

预试计划于 2026 年第三季度完成。全样本数据构造计划于 2026 年第四季度至 2027 年第一季度完成。初稿与内部研讨会计划于 2027 年第二至第三季度。

---

## 七、预期贡献

本文预期贡献于三条文献。

**披露可信度文献**。本文延伸 Rogers & Stocken (2005)、Hutton, Marcus, & Tehranian (2009)、Hope, Hu, & Lu (2016)、Bourveau, Chowdhury, Le, & Rouen (2023)、Skinner (2024) 关于具体披露可信度的研究，识别出一个具体性-可信度关系非单调而是条件性的场景。条件变量——当期可观察能力支撑——本身来自声明发出时即可获取的公开信息，使得这一框架对投资者、监管者与研究者均具有可操作性。

**AI 言-行差距文献**。现有 AI 披露文献在公司-年或公司-季层面记录了 talk-walk 的平均差距（Babina et al., 2024；Barrios et al., 2025；Li, 2025；Sun, Wen, Zhao, Almugren, & Galgotia, 2026）。本文将这一分析下沉到 claim 层。由于同一企业通常发出多条具体性与支撑度各异的 GenAI 声明，企业-年聚合会掩盖企业内 claim 间的可信度异质性。claim 层方法使得 AI 披露文献的核心问题——AI talk 在什么情况下携带信息——可以被应用到单条声明而非企业-年聚合。

**策略性披露与管理层激励文献**。机制证据将 GenAI 披露场景与管理层短视、激励驱动的策略性沟通文献相连接（Stein, 1988；Bergstresser & Philippon, 2006；Coles, Daniel, & Naveen, 2006；Edmans, Fang, & Lewellen, 2017；Larcker & Zakolyukina, 2012）。中国制度场景提供了一种独特的检验：控股股东股权质押在中国普遍且高度可观察，构成了对短期股价下跌厌恶动机的可测量异质性，这是美国数据无法提供的。

---

## 附录甲、后续研究议程

本研究构造的 claim 层数据集与 GenAI 招聘度量基础设施可支撑一项独立的后续研究，方向是中国 A 股 GenAI 招聘的跨企业扩散。本文聚焦于 claim 层可信度边界——unsupported specific claim 是否被企业层后续真实行动跟随；一个自然的延伸是在 Kalyani, Bloom, Carvalho, Hassan, Lerner, & Tahoun (2025) 的方法论框架下，进一步考察同一批声明对 GenAI 招聘在企业间、行业间、地区间扩散的影响。

拟议中的 Paper 2 将分析单元从单条声明上移至行业-季度或地区-季度，回答如下问题：某行业-季度内发出 GenAI 声明的企业比例，是否预测后续 GenAI 招聘向同行业未披露企业的扩散？这些声明的可信度构成（supported vs. unsupported 的占比）是否塑造扩散的速度与广度？Kalyani et al. (2025) 在美国数据上记录了新技术招聘的地理扩散约需 50 年完成，且早期高技能招聘随时间向低技能岗位拓展。中国 GenAI 场景提供了一个压缩的、高频的类比版本：一项快速演进的通用目的技术，配合丰富的 claim 层披露与可与真实能力清晰区分的数据基础。

两篇论文共享 GenAI claim 词典、招聘度量基础设施、企业层专利与能力支撑数据，但回答不同的问题：本文（Paper 1）问**哪些具体声明可信**；Paper 2 问 **GenAI 招聘如何在中国 A 股全体企业中传播**。二者作为同一套实证基础设施的互补产出，而非合并为单一扩展分析。Paper 2 的详细设计延后至单独的研究方案中。

---

## 参考文献

Ai, C., & Norton, E. C. (2003). Interaction terms in logit and probit models. *Economics Letters*, 80(1), 123–129.

Allee, K. D., DeAngelis, M. D., & Moon, J. R., Jr. (2018). Disclosure "scriptability." *Journal of Accounting Research*, 56(2), 363–430.

Anderson, R. C., & Reeb, D. M. (2003). Founding-family ownership and firm performance: Evidence from the S&P 500. *Journal of Finance*, 58(3), 1301–1328.

Aswani, J., Raghunandan, A., & Rajgopal, S. (2024). Are carbon emissions associated with stock returns? *Review of Finance*, 28(1), 75–106.

Babina, T., Fedyk, A., He, A., & Hodson, J. (2024). Artificial intelligence, firm growth, and product innovation. *Journal of Financial Economics*, 151, 103745.

Baker, A. C., Larcker, D. F., McClure, C. G., Saraph, D., & Watts, E. M. (2024). Diversity washing. *Journal of Accounting Research*, forthcoming.

Barrios, J. M., Campbell, J. L., Johnson, R. G., & Liu, C. (2025). Artificially intelligent or artificially inflated? Determinants and informativeness of corporate AI disclosures. Working paper.

Bergstresser, D., & Philippon, T. (2006). CEO incentives and earnings management. *Journal of Financial Economics*, 80(3), 511–529.

Bertrand, M., Duflo, E., & Mullainathan, S. (2004). How much should we trust differences-in-differences estimates? *Quarterly Journal of Economics*, 119(1), 249–275.

Bourveau, T., Chowdhury, M., Le, A., & Rouen, E. (2023). Human capital disclosures. Working paper.

Brynjolfsson, E., Rock, D., & Syverson, C. (2021). The productivity J-curve: How intangibles complement general purpose technologies. *American Economic Journal: Macroeconomics*, 13(1), 333–372.

Cheng, S. F., De Franco, G., Jiang, H., & Lin, P. (2019). Riding the blockchain mania: Public firms' speculative 8-K disclosures. *Management Science*, 65(12), 5901–5913.

Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. *Journal of Financial Economics*, 146(2), 529–551.

Coles, J. L., Daniel, N. D., & Naveen, L. (2006). Managerial incentives and risk-taking. *Journal of Financial Economics*, 79(2), 431–468.

Correia, S. (2017). Linear models with high-dimensional fixed effects: An efficient and feasible estimator. Working paper, Duke University.

Correia, S., Guimarães, P., & Zylkin, T. (2020). Fast Poisson estimation with high-dimensional fixed effects. *The Stata Journal*, 20(1), 95–115.

Dikolli, S. S., Frank, M. M., Guo, Z. M., & Lynch, L. J. (2022). Walk the talk: ESG mutual fund voting on shareholder proposals. *Review of Accounting Studies*, 27(3), 864–896.

Edmans, A., Fang, V. W., & Lewellen, K. A. (2017). Equity vesting and investment. *Review of Financial Studies*, 30(7), 2229–2271.

Giczy, A. V., Pairolero, N. A., & Toole, A. A. (2022). Identifying artificial intelligence (AI) invention: A novel AI patent dataset. *Journal of Technology Transfer*, 47(2), 476–505.

Hope, O.-K., Hu, D., & Lu, H. (2016). The benefits of specific risk-factor disclosures. *Review of Accounting Studies*, 21(4), 1005–1045.

Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. *Contemporary Accounting Research*, 40(2), 806–841.

Hutton, A. P., Marcus, A. J., & Tehranian, H. (2009). Opaque financial reports, R-squared, and crash risk. *Journal of Financial Economics*, 94(1), 67–86.

Kalyani, A., Bloom, N., Carvalho, M., Hassan, T. A., Lerner, J., & Tahoun, A. (2025). The diffusion of new technologies. *Quarterly Journal of Economics*, 140(2), 1299–1365.

Kogan, L., Papanikolaou, D., Seru, A., & Stoffman, N. (2017). Technological innovation, resource allocation, and growth. *Quarterly Journal of Economics*, 132(2), 665–712.

Larcker, D. F., & Zakolyukina, A. A. (2012). Detecting deceptive discussions in conference calls. *Journal of Accounting Research*, 50(2), 495–540.

Li, B. (2025). AI washing. Working paper, University of Florida.

Papke, L. E., & Wooldridge, J. M. (1996). Econometric methods for fractional response variables with an application to 401(k) plan participation rates. *Journal of Applied Econometrics*, 11(6), 619–632.

Papke, L. E., & Wooldridge, J. M. (2008). Panel data methods for fractional response variables with an application to test pass rates. *Journal of Econometrics*, 145(1–2), 121–133.

Petersen, M. A. (2009). Estimating standard errors in finance panel data sets: Comparing approaches. *Review of Financial Studies*, 22(1), 435–480.

Rogers, J. L., & Stocken, P. C. (2005). Credibility of management forecasts. *Accounting Review*, 80(4), 1233–1260.

Silva, J. M. C. S., & Tenreyro, S. (2006). The log of gravity. *Review of Economics and Statistics*, 88(4), 641–658.

Skinner, A. N. (2024). Subject matter complexity and disclosure channel richness. *Accounting Review*, 99(1), 393–425.

Stein, J. C. (1988). Takeover threats and managerial myopia. *Journal of Political Economy*, 96(1), 61–80.

Sun, Z., Wen, Y., Zhao, L., Almugren, I., & Galgotia, A. (2026). Unveiling AI washing: Bridging corporate technological gaps through a cognitive dissonance lens. *Technological Forecasting and Social Change*, 225, 124511.
