# 三篇 GenAI×股市参考文献精读 + Qian 复刻失败诊断

日期：2026-06-02

用途：完成三件事——(1) 精读三篇 PDF 的数据/问题/理论；(2) 整理全部实证结果与描述性统计；
(3) 机制先行思考。并专门诊断"为什么用中国数据复刻 Qian et al. (2025) 复刻不出来"。

参考文件：

```text
reference/GenAI+stock/qian-et-al-2025-...-suppliers-evidence-from-the-stock-market.pdf
reference/GenAI+stock/How Stock Market Participants Use Generative AI ... User-Platform Interaction Data.pdf
reference/GenAI+stock/Does generative AI facilitate investor Trading_ Early evidence from ChatGPT outages.pdf
```

---

## 0. 三篇一句话定位（先建立坐标系）

| | 论文 A：Qian, Peng & Li (2025) | 论文 B：Ecker, X. Li, Y. Li & Wu (2026) | 论文 C：Cheng, Lin & Zhao (2025) |
| --- | --- | --- | --- |
| 期刊 | Production & Operations Management | Journal of Accounting Research | Journal of Accounting & Economics |
| 关系方向 | **纵向**：客户披露 → **上游供应商** | 投资者 ↔ GenAI 平台（无企业间关系） | 投资者 ↔ ChatGPT（无企业间关系） |
| 核心变量 | GenAI 公告事件 → 供应商 CAR | 110 万+ 选股 query/answer | 8 次 ChatGPT 宕机 → 交易量 |
| 符号 | **正**（+0.27% 供应商 AR） | 描述性（无单一符号） | 宕机时交易量**下降** 5.55%SD |
| 识别 | 事件研究 + PSM/IV/Heckman/DID | 关联性，明确不做因果 | 准自然实验（宕机外生冲击）+ DID |
| 市场 | 北美 | **中国 A 股**（零售主导） | 美国 |
| 与 T05 关系 | T05 的**镜像反面**（横向竞争 vs 纵向互补） | T05 的中国制度/投资者信息加工锚 | T05 的因果识别范式锚 |

一句话：**A 是"互补型纵向溢出（正）"，T05 做的是"替代型横向竞争重估（负）"。这两者本来就不是同一件事——这正是你复刻不出来的第一层原因。**

---

## 1. 论文 A：Qian, Peng & Li (2025) —— 你卡住的那篇

### 1.1 研究问题

- RQ1：下游公司 GenAI 公告对其**上游供应商**股价是否有正向溢出？
- RQ2：供应商哪些特征放大/缩小该反应？
- RQ3：产品导向 vs 流程导向 GenAI 公告，对供应商反应是否不同？

### 1.2 理论

核心理论 = **颠覆式创新的关系视角（relational perspective of disruptive innovation, Kumaraswamy et al. 2018）**：
颠覆式技术不只改变单个企业，而是重构整个生态系统内的角色、关系与交易。三条传导路径：

1. **需求路径**：下游 GenAI 投资 → 拉动上游零部件/算力需求（典型例：Nvidia GPU）。
2. **效率路径**：下游 GenAI 协同（如 Walmart "Trend-to-Product"）→ 供应商运营效率提升。
3. **创新催化路径**：下游 GenAI 创新 → 倒逼供应商开发新产品（如 Qualcomm Oryon）。

→ 预测 H1：供应商 AR 为**正**。调节假设 H2–H6（见下）。

### 1.3 数据（关键：这是复刻的瓶颈所在）

| 步骤 | 来源 | 数量 |
| --- | --- | --- |
| GenAI 公告检索 | **LexisNexis 新闻通讯社**（PR Newswire / Business Wire / GlobeNewswire），2023-01 至 2024-05 | 14,941 条潜在 |
| 限定北美上市公司 | — | 2,084 条 |
| 人工核验"具体 GenAI initiative" + 每公司只留首次 | — | 254 家公司各 1 条 |
| 匹配**上市供应商** | **Compustat Segment + FactSet** 供应链关系（事件年前 5 年） | 657 供应商 / 178 公告公司 |
| 清洗（剔供应商自身先披露、多客户重叠、[-2,+1] 混杂事件、估计期<200天、penny stock） | — | **最终 515 supplier-announcement 观测 / 277 供应商 / 117 公告公司** |

样本单位 = **supplier × announcement**（一个供应商可对应多个客户公告）。

### 1.4 方法

- 期望收益：**Fama-French 四因子模型**，估计期 [-210, -11]（200 个交易日），事件日 day 0；窗口 [-1,+1]。
- H1 检验：对 AR0 做 t 检验 / Wilcoxon 符号秩 / 二项符号检验。
- H2–H6：横截面 OLS，被解释变量 = AR0，控制 size/age/MTB/leverage/关系时长/公告强度/同行业；公告公司 FE + 供应商行业 FE；按公告公司聚类；1/99 缩尾。
- 稳健性：PSM（匹配无 GenAI 公告客户的供应商）、IV（2015-19 AI 专利数为工具变量）、Heckman、双向 FE DID、120 日长期 CAR、传统 AI 对照、不同窗口、FF3/FF5。

### 1.5 实证结果（整理）

**事件研究（Table 2，N=515）：**

| | Day -1 | **Day 0** | Day 1 |
| --- | --- | --- | --- |
| 平均 AR | -0.0008 (t=-1.01) | **+0.0027*** (t=3.48)** | +0.0012 (t=1.45) |
| 中位数 AR | -0.0007 | **+0.0013*** (Z=2.78)** | +0.0013* (Z=1.87) |
| 正向占比 | 0.470 | **0.5456** (Z=2.07)** | 0.532 |

→ 供应商在公告日获得 **+0.27%** 显著正 AR；day1 衰减（市场快速吸收）。

**横截面（Table 3，因变量 AR0）：**

| 变量 | (1) | (2) | (3) | 对应假设 |
| --- | --- | --- | --- | --- |
| 供应商 R&D 强度 | 0.0221** | 0.0232*** | 0.0259*** | H2 ✓（R&D 高→反应更正） |
| 供应商销售增长 | 0.0148*** | 0.0141** | 0.0115** | H3 ✓ |
| 供应商-客户距离 | -0.0010** | -0.0011** | -0.0011*** | H4 ✓（距离近→反应更正） |
| 供应商行业集中度 | 0.0122** | 0.0011 | 0.0007 | H5b ✓（集中度高=竞争弱→反应更正） |
| 产品导向公告 | — | — | 0.0046** | H6 ✓（产品>流程） |
| 公告公司 FE / 行业 FE | Y/N | Y/Y | N/Y | |

**稳健性结论：**
- PSM 匹配供应商：公告日 **无显著 AR**（Table 4，day0 t=1.05）→ 反应来自 GenAI 而非样本构成。
- IV（AI 专利 2015-19，K-P F=23.4）：Selected 二阶段 +0.0061* → 不是不可观测选择驱动。
- Heckman：四个供应商特征系数一致；IMR 不显著。
- 长期：120 日累计 CAR 持续上升（长期正向价值创造）。
- 传统 AI 公告对照：供应商**无显著** AR → GenAI 独特。

### 1.6 A 篇的边界（作者自陈）

仅反映公告时点投资者**预期**，未拆开真实机制（创新溢出 vs 效率）；样本仅北美，未含新兴市场（明确点名"distinct social relations and political ties, Lo et al. 2018"）；只用主流通讯社可能漏事件。

---

## 2. 论文 B：Ecker, X. Li, Y. Li & Wu (2026, JAR) —— 中国平台投资者使用 GenAI

### 2.1 问题与定位

**描述性**论文（明确声明不做因果）：中国零售投资者如何用 GenAI 处理投资信息？三个维度：
(1) 信息需求/topic/task；(2) 用户-AI 交互动态；(3) query 活动与市场交易的初步关联。

### 2.2 数据

- 中国某头部 GenAI 平台（月活 1000 万+），2024 H1。
- 4.78 亿 query-answer → 关键词锚定 A 股公司名 + 微调中文 BERT 过滤选股相关 → **174.6 万 query-answer / 5,278 家公司**。
- 83% firm-specific，17% general。CSMAR 提供财务/行情。
- 用 LDA + 商用 LLM 做 topic 分类；按 **Blankespoor et al. (2020)** 的 awareness/acquisition/integration 三阶段框架做 task 分类。

### 2.3 理论锚

- Kim & Verrecchia (1994)：公开披露在事件窗会**扩大**异质投资者间的信息差。
- Blankespoor et al. (2020)：信息加工成本 = awareness + acquisition + integration。
- 零售投资者忽视会计信息、偏好被加工/摘要过的信息（Lawrence 2013 等）。

### 2.4 实证结果（整理）

**描述性（Table 1 关键，firm-day N≈597k）：**
- query 量从 1 月日均 ~2,000 增至 6 月 >8,000；约 40% 早期用户只问 1 次，仅 8.5% 问 ≥20 次（高度右偏）。
- topic 前六：业务展望 26.3% / 生产运营 25.6% / 财务业绩 23.3% / 产品技术 22.3% / 股价表现 19.6% / 竞争 18.0%。
- task：integration 77.6% > acquisition 44.5% > awareness 38.8%；information search 单项最高 32.7%；summarization 仅 3.3%。
- 序列演化：首次 query >50% 是 awareness，随使用下降；acquisition 上升；integration 全程 72–81% 高位。

**核心关联结果：**
1. **披露 informativeness 与 GenAI 依赖的替代**：管理层预告越详细/覆盖话题越广 → 同期 GenAI query 越**少**（GenAI 用于填补披露不完整时的信息缺口）。
2. **答案属性 ↔ 反馈/留存**：signal alignment(方向准确)↑ → 点赞/分享/复制↑、后续再用↑；但答案过长/外链多/specificity 过高 → 留存↓（厌恶冗长）。
3. **用户学习**：早期 answer 的 specificity / 财务指标 → 显著影响用户后续 query 的措辞与指标使用。
4. **市场层面（Table 6，firm-day FE+date FE，按 firm&date 聚类）**：
   - Log(1+#Specific_Queries) 对 AbnSpread **+0.296***、Amihud +0.235***、AbnVol +0.325***、VPIN +0.103*** 全显著正。
   - 读法：GenAI 使用↑ → 流动性↓ + 异常成交量↑ + 知情交易代理↑ ⇒ **加大投资者间信息不对称**（部分人变得更知情）。
5. **情绪 ↔ 同日异常收益（Table 7）**：answer 平均情绪 → 同日 AbnReturn 正相关，在获正反馈的答案中更强。

### 2.5 对 T05 的直接价值

- T05 用的就是**中国互动平台/调研问答（IIP/IR_QA）GenAI 披露**——B 篇是同一信息生态的权威背书，可引为"中国零售主导市场、GenAI 改变信息加工"的制度与文献锚。
- B 篇的 **Specificity 度量、forward-looking/subjectivity/sentiment、按 firm-day 聚合 + abnormal return/turnover** 与 T05 的 Specificity_z、PeerCAR、abnormal turnover 高度同构，可直接对标方法。

---

## 3. 论文 C：Cheng, Lin & Zhao (2025, JAE) —— ChatGPT 宕机

### 3.1 问题与识别

两个问题：(1) 投资者在多大程度依赖 GenAI 做专业任务？(2) GenAI 辅助交易如何影响股价信息含量？
识别 = **8 次 ChatGPT 宕机（2023-02 至 08，交易时段，18–240 分钟，均值 119）作为对 GenAI 可得性的外生冲击**。
因果逻辑：若投资者依赖 ChatGPT 做信息处理，宕机 → 工作流中断 → 交易能力下降 → 交易量下降。

### 3.2 数据与设计

- TAQ 5 分钟分笔；对照期 = 同一 firm 前 5 个交易日同一时段。最终 **2,615,434 个 security-date-5min 观测 / 2,553 只股票**。
- OLS：TradingVolume = β·Outage + 控制 + firm FE + 5min interval FE，按 firm&date 聚类。

### 3.3 实证结果（整理）

| 发现 | 结果 |
| --- | --- |
| 主效应（Table 3 col2） | Outage 系数 **-0.084 (t=-3.25)**，= -5.55% 样本 SD（≈ -9.88% 均值） |
| 动态 | 宕机后 **约 30 分钟才显著**，结束后无明显"补单"→ 用于信息处理而非直接下单 |
| 机制1（新闻） | 宕机日有公司新闻时，交易量下降更大（信息处理需求更高） |
| 机制2（投资者类型） | 零售/非零售均降，**非零售（尤其 transient 机构）降更多** → GenAI 偏向强化机构信息优势 |
| 市场质量 | 短期 price impact↓、return variance↓、bid-ask spread↓ → 宕机时知情交易减少（量级温和） |
| 长期（DID） | 用宕机期交易量降幅做 firm 级 GenAI-辅助交易强度代理；ChatGPT 发布后，高强度 firm 的**股价信息含量提升更多**（Bai et al. 2016 / Kacperczyk et al. 2021 度量） |
| 证伪 | 用 t-1 作伪宕机日 → 无效应 |

### 3.4 对 T05 的价值

- C 篇是**因果识别的范式样板**：外生冲击 + 高维 FE + 证伪 + 动态图。T05 当前是"事件内横截面异质性"而非外生冲击，C 篇提示了 T05 识别强度的天花板与可借鉴的稳健性结构（动态/lead-lag 图、伪事件、聚类）。
- C 篇的 transient institution 异质性与"GenAI 强化信息优势"机制，可用于 T05 解释"为何重估集中在事前 AI-active 近邻竞品"。

---

## 4. 核心诊断：为什么用中国数据复刻 Qian (A 篇) 复刻不出来

你已经在 `docs/empirical_runs/20_v3_supplier_spillover_sample_diagnostic_20260522.md` 跑过供应商放大诊断。结论很硬：**正式公告路径下，A 股客户 GenAI 事件 × 上市供应商，CAR 可连观测只有 14–18 个**（Qian 是 515）。这不是 bug，是结构性的。原因分五层：

### 4.1 第一层（决定性）：样本根本起不来——供应链链路 + 事件源双重稀释

A 篇 515 的样本来自**两次放大**：
1. 事件源是 **LexisNexis 新闻通讯社**（14,941 条），而非交易所正式公告；
2. 单位是 **supplier × announcement**，且供应链关系来自 **Compustat Segment + FactSet**（美国 SFAS 131 强制披露 ≥10% 营收的主要客户，第三方数据库把供应链织得很密）。

中国这两条同时塌掉：
- **正式公告**里"首次具体 GenAI initiative"的客户公司本就少（你的诊断里 formal 只有 20 个事件）；
- **CSMAR 前五大客户/供应商表**只给前五名、且大量是**非上市**或**匿名**（"第一大客户"无名称），(GenAI 客户) × (A 股上市供应商) 的交集极小（你诊断里只剩 14–18）。

→ 30 倍的样本差距主要来自这里。即使把事件源换成互动平台（IRQA）可放大到 992 客户事件，但能连上上市供应商 CAR 的仍只有约 145–179，且关系质量存疑。

### 4.2 第二层：经济机制在中国样本里根本不成立

A 篇的正向溢出依赖"下游 GenAI → 真实拉动可识别上市供应商需求"（GPU/半导体/算力）。
你诊断里匹配出的 pair（九州通医药分销、朗玛 AI 全科医生、水电新能源关联采购）**根本不是 GenAI 硬件/算力供应链**，而是偶发的关联交易/采购关系。
→ 即使凑出样本，需求溢出机制也没有载体，符号自然不稳。

### 4.3 第三层（你可能混淆的概念）：纵向供应商 ≠ 横向竞品，符号本就相反

A 篇研究 **纵向、互补** 关系（供应商），预测**正**号。
T05 主线研究 **横向、替代** 关系（产品市场竞品），预测**负**号。
如果你是想用 A 篇的"供应商溢出"设计、却套到产品市场 peer 上，**复刻不出来是必然的，而且方向相反**——这恰恰说明 T05 不是 A 篇的复刻，而是它的"竞争侧镜像"。这是好事：原创性更强。

### 4.4 第四层：制度/微观结构与方法差异

- **涨跌停（±10%/20%）** 截断异常收益分布；ST、停牌、IPO 次新使"估计期≥200 日 + 干净事件窗"难满足。
- **2023 AI 行情高度同日聚集**（DeepSeek 时刻、政策日），A 篇靠"剔除 [-2,+1] 混杂事件"得到干净事件日的假设在中国密集 AI 行情下大面积失效，跨事件污染严重。
- FF 四因子在 A 股的构造、零售主导的微观结构都与北美不同。

### 4.5 第五层：A 篇本身的"首次 + 通讯社"放大不可移植

"每公司只留首次 GenAI initiative"配合宽口径新闻源，在美国能在 16 个月里铺开 254 家。中国正式披露里真正"具体首次 GenAI"叠加"有上市供应商"是结构性稀缺。

### 4.6 结论与建议

> **不要继续把 A 篇当成"待复刻目标"。** A 篇是纵向互补正向溢出，数据可得性靠美国供应链数据库；中国正式披露 + CSMAR 供应链无法支撑同一设计。你项目真正在做、且已跑出稳健信号的，是它的**横向竞争反面**（v4→v6→v8 主线：Specificity_z × AIActivePeer → 负向 PeerCAR）。

可保留 A 篇的两类用途：
1. **文献对照/foil**：T05 引言可写"与供应链互补溢出（Qian et al. 2025 发现供应商正向 AR）相对，本文识别产品市场竞品的负向竞争性重估"。
2. **机制边界**：A 篇的"产品导向 > 流程导向"、"距离近更强"可启发 T05 的披露类型 horse-race 与 Top1-3/Top6-10 proximity gradient（你已做）。

若仍想保留一个"供应链分支"，把它定位为 **category validation 边界检验**（你 v7 AI 供应链披露诊断已显示横截面正向 peer 效应 +0.004225, p=0.026），而不是 DID 主线。

---

## 5. 机制先行思考（对 T05 主线）

三篇共同给出的机制语言，可整合成 T05 的"竞争风险信号"故事：

```text
焦点公司具体化 GenAI 披露（Specificity_z↑，B 篇式 disclosure concreteness）
   → 被资本市场解读为可信竞争承诺信号（A 篇关系视角的"竞争侧"：颠覆重构关系，但对替代者是威胁而非需求）
   → 投资者（含 C 篇式"更知情的机构/transient"）重新评估处于同一 AI 竞争空间、产品市场最近邻的竞品
   → AI-active 近邻竞品出现更负 PeerCAR[0,+1]（B 篇式 GenAI 加大信息不对称、影响 abnormal return 的同信息加工通道）
```

三条可检验机制分支（建议优先级）：

1. **信息加工/投资者注意通道（借 B+C）**：负向重估是否在投资者注意更高、知情交易更活跃时更强？可用 IIP query 强度、abnormal turnover、（若有）机构持股 transient 占比交叉。——与 B 篇 query↔流动性、C 篇 transient 机构一致。
2. **竞争接近度通道（已做，最稳）**：Top1-3 > Top6-10 > 随机/低相似 ≈ 0。这是 H2 的核心，建议作为机制主图（lead-lag + proximity gradient）。
3. **披露内容类型边界（已做）**：own_impl/competitive 信号为负；supply_chain 披露为 category validation（正或零）。——直接对应 A 篇"需求侧正向 vs 竞争侧负向"的张力。

不能升级为强机制（README 已界定）：peer disclosure diffusion（严口径不显著）、纯 business stealing（focal CAR 符号分解不支持）。

---

## 6. 给三件事的交付小结

1. **精读（数据/问题/理论）**：见 §1–§3。三篇分别覆盖 纵向供应链溢出(正) / 中国零售投资者 GenAI 使用(描述) / GenAI 外生冲击对交易与信息含量(因果)。
2. **实证结果 + 描述性统计整理**：见 §1.5、§2.4、§3.3 的表格（含 N、系数、t/Z、显著性）。
3. **机制先行**：见 §5。T05 定位 = A 篇的横向竞争镜像，用 B/C 的信息加工通道讲"市场把具体 GenAI 披露读成竞争风险信号"。

**最重要的一句**：Qian 复刻不出来不是你的执行问题，是设计不可移植 + 概念方向相反。继续打 T05 现有主线（v8），把 A 篇降级为引言对照与 category-validation 边界即可。

---

## 7. 三篇机制 + 异质性 + 理论锚 合并总表（2026-06-02 补）

### 7.1 一页总表

| | A: Qian et al. 2025 (POM) | B: Ecker et al. 2026 (JAR) | C: Cheng et al. 2025 (JAE) |
| --- | --- | --- | --- |
| 关系/符号 | 纵向供应商，**正** +0.27% | 投资者↔平台，描述性 | 投资者↔ChatGPT，宕机交易量**-5.55%SD** |
| 识别 | 事件研究+PSM/IV/Heckman/DID | 关联，非因果 | 宕机外生冲击+DID+证伪 |
| **主机制** | 颠覆式创新关系视角的需求/效率/创新溢出 | ①披露信息量↔GenAI依赖**替代**；②需求跟**媒体中介**不跟原始披露；③答案**镜像**用户语言；④感知有用性(方向准/主观/情绪+，具体/复杂−)；⑤用户学习；⑥使用↑→信息不对称↑ | ①用于**信息加工**(宕机30min后才掉、无补单)；②有新闻时降更多；③知情交易↓(price impact/return variance)；④信息不对称↓(价差)；⑤长期信息含量↑；⑥API宕机→算法交易↓ |
| **主异质性** | 供应商R&D↑/销售增长↑/距离近/低竞争行业/产品导向 → 反应更正 | 用户:参与度×老练度(高→integration/财报分析)；事件:负面盈余>正面(控媒体后消失)；好消息长/广→替代更强；机构持股→query负相关 | 散户vs非散户(**非散户降更多**)；机构类型(**仅transient显著**)；有新闻时更强 |
| **理论锚** | Kumaraswamy et al. 2018 关系视角；Cheng-Nault 2012 IT溢出 | Blankespoor et al. 2020(三阶段成本)；Kim-Verrecchia 1994(信息差扩大)；Skinner 1994(好消息可信度)；Umar 2022(认知成本) | Blankespoor et al. 2020；Hirshleifer 2009/deHaan 2017(有限注意)；Acemoglu 2024(任务互补)；Kyle 1985；Glosten-Milgrom 1985；Bai 2016/Kacperczyk 2021(信息含量) |
| 对 T05 | 横向竞争**镜像**(foil) + category-validation 边界 | 中国制度+信息加工**锚**；同构 specificity 度量 | **因果识别范式** + transient机构异质性接口 |

### 7.2 两条贯穿主线
1. **Blankespoor, deHaan & Marinovic (2020) 信息加工成本框架**（awareness/acquisition/integration）：B、C 共享，统摄 task 分类、替代机制、用户能力异质性。
2. **Kim & Verrecchia (1994) 信息不对称扩大**：B（使用↑→VPIN↑）与 C（宕机→价差↓，transient 机构最敏感）一致指向——**GenAI 偏向更知情子集，扩大而非缩小信息差**。这正是 T05"AI-active 近邻竞品被更知情投资者先重估"的理论接口。

---

## 8. AJG3+ 相关文献扫描（2026-06-02）

背景：直接搜 "generative AI + stock" 结果少，因为多数仍是 SSRN/arXiv 工作论文，且关键词碎片化（ChatGPT / LLM / AI exposure / firm value 各自命名）。下表区分**已发表 AJG3+** 与**高质量在投 WP**。

### 8.1 已发表在 AJG3+（核心集合，约 6 篇）

| 论文 | 期刊(AJG) | 一句话 | 与 T05 关系 |
| --- | --- | --- | --- |
| Eisfeldt, Schubert, Zhang & Taska, *Generative AI and Firm Values* | **Journal of Finance** (4*, forthcoming/已接受；原 NBER WP31222) | 构造劳动力 GenAI 暴露，ChatGPT 发布后 AMH 组合两周 +5%；劳动替代渠道 | firm-level GenAI 暴露与短窗 CAR 的奠基，T05 焦点公司侧参照 |
| Lopez-Lira & Tang, *Can ChatGPT Forecast Stock Price Movements?* | **Journal of Financial Economics** (4*, forthcoming) | GPT 从新闻标题预测收益，尤其小盘/负面 | GenAI 处理信息→可预测性，机制层面 |
| Bertomeu, Lin, Liu & Ni, *Impact of GenAI on Information Processing: Ban of ChatGPT in Italy* | **Journal of Accounting and Economics** (4*, 2025, 80(1):101782) | 意大利禁令→分析师 AI 使用↓、预测↓、信息不对称↑ | C 篇的姊妹外生冲击；信息不对称机制 |
| Cheng, Lin & Zhao, *ChatGPT outages* | **JAE** (4*, 2025) | 见本文 §3 | 因果识别范式 |
| Ecker, Li, Li & Wu, *User-Platform Interaction Data* | **Journal of Accounting Research** (4*, 2026) | 见本文 §2 | 中国制度+信息加工锚 |
| Qian, Peng & Li, *GenAI Announcements on Suppliers* | **Production & Operations Management** (4, 2025/26) | 见本文 §1 | 纵向镜像 foil |

### 8.2 高质量在投 WP（大概率落 AJG3+，引用前需查最新状态）

| 论文 | 现状 | 一句话 |
| --- | --- | --- |
| Kim, Muhn & Nikolaev, *Bloated Disclosures: Can ChatGPT Help Investors Process Information?* | arXiv 2306.10224 / Chicago Booth | GPT 摘要更短但信息量更高，更能解释市场反应 |
| Jha, Qian, Weber & Yang, *ChatGPT and Corporate Policies* | NBER WP32161 | 用电话会构造 firm-level ChatGPT 投资分，预测 capex/收益 |
| Kim, Muhn & Nikolaev, *Financial Statement Analysis with LLMs* | WP | LLM 做财报分析预测盈余方向 |

### 8.3 相关但属"广义 AI"（非 GenAI，仍 AJG4*，对 T05 的 AIActive 有用）

| 论文 | 期刊 | 用处 |
| --- | --- | --- |
| Babina, Fedyk, He & Hodson (2024), *Artificial intelligence, firm growth, and product innovation* | **JFE** (4*) | AI 招聘→增长/产品创新；T05 的 AIActivePeer(AI 招聘)度量直接引用 |
| Eisfeldt & Schubert, *Generative AI and Finance* | **Annual Review of Financial Economics** (3) | 综述，可当文献地图 |

### 8.4 更好的检索词（避免漏检）

```text
关键词扩展：ChatGPT, large language models, LLM, "generative AI",
            "AI exposure", "AI adoption", firm value, "information processing",
            "informed trading", disclosure, analyst forecast
事件设定：  ChatGPT release / DeepSeek release / ChatGPT outage / Italy ban
检索源：    SSRN(eLibrary) + NBER + arXiv q-fin + Google Scholar
注意：      DeepSeek 事件研究目前多见于低档期刊/WP（如 Future Business Journal 非 AJG3），
            引用需谨慎。
```

> 结论：**已发表 AJG3+ 的 GenAI×资本市场论文目前就是个位数**，且高度集中在 JAE/JAR/JF/JFE。你"结果不多"的感觉是对的——这反而说明 T05 选题处在一个**尚未拥挤**的窗口。
