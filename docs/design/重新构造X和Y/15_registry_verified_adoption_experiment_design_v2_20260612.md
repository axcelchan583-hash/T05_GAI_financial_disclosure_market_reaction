# T05 备案/登记验证增强实验设计 v2（20260612）

> 基于 v1（13/14 号设计文档）修订。所有修改处以【修改】【新增】标注并附原因。
> 未标注的部分 = v1 保留项，经复核无需改动。

---

## 修改总览

| # | 修改内容 | 原因（一句话） | 影响章节 |
|---|---|---|---|
| M1 | 增加"选择问题四道防线"为独立设计模块 | `registry_match` 非随机：备案公司系统性更大、更偏软件业、AI 能力更真，Q1 vs Q4 裸比较混杂披露可信度与公司质量，审稿人必问 | §6, §7, T5/T9 |
| M2 | `registry_match` 拆为 `verified_at_event_date` 与 `verified_ex_post`，主张分强弱两层 | 备案批次滞后公示：披露日早于公示日时投资者观察不到备案状态，"市场识别行政验证"的强主张只能用事件日已公示的子样本支撑 | §1, §4, §5, T6 |
| M3 | 新增 Specificity→备案 预测验证表 | `verified_ex_post` 子样本若仍分层，机制只能是市场从披露文本推断可验证性——Spec_z 若预测最终备案，即被钉死为"可验证性的市场可观察代理"，前期度量工作全部增值 | §8, T7 |
| M4 | Q3/Q4 从 headline CAR 对比降级为场所选择分析；新增 venue determinants 表 | IIP 首提日由投资者提问时点决定，跟随股价异动与热点，CAR 天然内生污染；但"可验证产品更可能走正式公告渠道"本身是支持理论链条的一张表 | §5, §9, T3 |
| M5 | pooled interaction 升为主规格，分格冻结规格降为稳健性；新增 cell-size 预检门 | 判别标准要求 β1 显著小于 β2/β4，跨格检验只能在 pooled 里正式做；且 Q1 事件数很可能 <30，分格回归无功效 | §6 |
| M6 | 深度合成算法备案明确用途 = pre-registry 窗口（2023.1–8.15）唯一验证层 | 生成式备案 2023-08-15 才生效，而 2023 上半年恰是披露最密集期；深合成备案 2023-01-10 已施行，是这段样本唯一可用的行政验证，直接决定样本左边界 | §2, §11 |
| M7 | `registry_product_id` 的 hash 去掉 `status` 字段 | 产品跨批次状态变化（备案清单→已备案）会导致主键漂移；`source + filing_no` 已唯一 | §2 |
| M8 | `registry_match=0` 再拆 `later_verified` / `never_verified` | later vs never 对比把"产品是真的"与"事件日时可验证"分离，接近 within-product 变异，是对 M1 选择问题最便宜的一道防线 | §4, §7, T6 |

---

## 0. 一句话版本

【修改：主张分两层，原因见 M2】

> **强主张（事件日信息集内）**：当 focal firm 的 GenAI 披露在事件日已能被公开的 CAC 备案/登记记录验证时，product-market peers 是否发生更强的负向重估？
>
> **弱主张（事后可验证性）**：即使备案在事件日尚未公示，市场是否仍能通过披露内容本身（specificity）区分事后被证实与从未被证实的 GenAI claim？

非上市大模型公司不进 focal event，只做两件事（v1 保留）：
1. 重大发布日进 GenAI confound calendar；
2. 全量备案库进赛道事前竞争密度。

---

## 1. 研究对象与主张结构

### 1.1 研究对象（v1 保留）

```text
A 股上市公司披露的 GenAI initiative / adoption claim
× 该 claim 的行政可验证性（备案/登记）
```

### 1.2 主张分层【修改，原因 M2】

| 层 | 检验对象 | 所需子样本 | 支撑表述 |
|---|---|---|---|
| H1 强 | 市场 condition on 已公示备案状态 | `verified_at_event_date=1` vs 同期 unverified | "资本市场识别行政验证" |
| H2 弱 | 市场从披露内容推断可验证性 | `verified_ex_post` vs `never_verified` | "市场区分事后被证实的 claim" |
| H3 机制 | Specificity 是可验证性的可观察代理 | 全样本 | 连接 H1 与 H2 |

原因：v1 把两层混在一个 `registry_match` 里。若多数披露早于批次公示（大概率如此——公司通常在产品上线时披露、备案公示滞后数月），强主张的样本会很小，必须提前把弱主张的检验路径设计好，而不是跑完才发现 H1 没功效。

### 1.3 与 POM/Qian 的关系（v1 保留）

不复制公告事件本身，借鉴其事件研究与人工筛选方法，加入中国行政验证层。

---

## 2. v67：firm-product registry master

### 2.1 输入（v1 保留 + 修改）

- 生成式 AI 服务已备案/已登记附件 1–11（附件 3–11 待本地补全）；
- 既有 v64/v65/v66 官方备案主库；
- 【修改，原因 M6】深度合成服务算法备案：**不再是泛泛的"补充验证层"**，明确两个用途：
  (a) 2023-01-10 至 2023-08-15 pre-registry 窗口的**唯一**行政验证层；
  (b) 2023-08-15 之后作为 `verification_type` 的第三档。

### 2.2 主键规则【修改，原因 M7】

```text
registry_product_id = hash(registry_source + filing_no)
```

`status`、`entity`、`product_name` 不入 hash（状态会跨批次变化、主体名会有全半角差异，均导致主键漂移）。状态变化以 `status_history` 子表记录：

```text
registry_status_history.csv: registry_product_id | status | public_batch | batch_public_date
```

### 2.3 新增字段【新增，原因 M2】

在 v1 字段表基础上增加：

| 字段 | 含义 |
|---|---|
| `batch_public_date` | 该产品**首次**出现在公开批次附件的日期（≠ filing_date） |
| `pre_registry_era` | 0/1，filing 依据是否为深合成备案（2023-08-15 前唯一验证层） |

原因：`filing_date`（表内备案时间）是行政流程日期，`batch_public_date` 才是投资者信息集进入日。H1/H2 的划分完全依赖后者，v1 没有这个字段，整个信息集分析做不了。

其余字段表、文件命名（registry_firm_product_master.csv 等四件套）、"已登记单独保留为 adoption verification"规则，v1 保留。

---

## 3. v68：反向定位首次披露日

v1 的检索键优先级、D1/D1' 定义、timing_type 字段全部保留。新增一列：

| 字段 | 含义 |
|---|---|
| `verified_at_event_date` | 0/1，`batch_public_date ≤ first_public_date` 【新增，原因 M2】 |

### 3.1 时序解释表【修改】

v1 的四行时序表保留，但增加信息集标注：

| 时序 | washing 解释（v1） | 信息集含义【新增】 |
|---|---|---|
| 先备案公示，后披露 | 真实产品 | H1 样本：市场可观察验证状态 |
| 先披露，备案随后公示 | 可接受 | H2 样本：事件日不可观察，事后可验证 |
| 先吹很久，始终无备案 | washing 风险高 | `never_verified`，H2 对照组 |
| 互动平台先提，公告后发 | backfill | 场所选择分析用，不进 CAR 主表 |

---

## 4. v69：验证标签

v1 的 join 逻辑、LLM 只做产品名模糊匹配确认、三层 verification_level，全部保留。字段增改：

【修改，原因 M2/M8】`registry_match` 替换为四值变量：

```text
verification_timing ∈ {
  verified_at_event,   # 事件日已公示 —— H1
  later_verified,      # 事件日未公示、此后任意时点公示 —— H2 处理组
  never_verified,      # 截至样本期末从未出现在任何批次 —— H2 对照组
  unmatched_ambiguous  # 产品名匹配不确定，进 review queue
}
```

原因（M8）：`later_verified` vs `never_verified` 的对比中，两组在事件日的**公开信息环境相同**（都查不到备案），差异只在产品最终真实性。这接近 within-product-truth 的变异，把"披露的是真产品"与"市场能查到验证"分离——这是对选择问题（M1）最便宜的一道防线，且 v1 的 timing_type 字段已采集到所需原料，只差这个重组。

---

## 5. 主对比结构【修改，原因 M4/M5】

### 5.1 主战场收缩为正式公告内的 1×3

v1 的 2×2 四格保留为**描述性总表（T3 Panel A）**，但 CAR 推断主战场改为：

```text
正式公告（CNINFO）内：
  C1: verified_at_event     （H1 处理组）
  C2: later_verified        （H2 处理组）
  C3: never_verified        （对照组）
```

原因（M4）：IIP 首提日 = 投资者提问日，提问跟随股价异动与热点，Q3/Q4 的事件日内生。在其上比较 CAR，估计的是"被问到的时点效应"而非披露效应。IIP 格子改为两个用途：
(a) **场所选择分析**（§9）；
(b) 延伸表：加 PeerCAR[-10,-2]、[-20,-2] 前期走势控制后报告，明确标注内生性 caveat。

### 5.2 cell-size 预检门【新增，原因 M5】

跑任何回归前先产出：

```text
results/v70_cell_size_precheck_20260612/cell_counts.csv
```

规则：
- C1 ≥ 30 events → H1 主表可做分格稳健性；
- C1 ∈ [10,30) → H1 只在 pooled interaction 里报告，明确标注低功效；
- C1 < 10 → H1 降为描述性，论文主张以 H2 为主线（这不是失败，是主张校准）。

---

## 6. 基准回归规格【修改，原因 M5/M1】

### 6.1 主规格 = pooled interaction（v1 的备选升为主）

```text
PeerCAR_{e,p} =
  β1 · PeerExposure_{e,p} × C1_e
+ β2 · PeerExposure_{e,p} × C2_e
+ β3 · PeerExposure_{e,p} × C3_e
+ EventFE_e + PeerIndustryWeekFE_{p,w} + ε_{e,p}
```

双向聚类（event × peer firm）。判别：β1 < 0 显著；β1 vs β3、β2 vs β3 的 Wald 检验——**这两个跨组检验是论文核心主张，只能在 pooled 里做**（M5 原因）。分格冻结规格降为 T3 Panel B 稳健性。

### 6.2 选择问题修正规格【新增，原因 M1】

在 6.1 基础上叠加，按防线递进：

```text
(a) + FocalControls_e × PeerExposure（规模、行业、AI能力代理、上市年限）
(b) within-firm：限定"同一 focal firm 既有 verified 又有 never_verified 披露"
    的子样本，加 FocalFirmFE_f × PeerExposure
(c) 熵平衡：以 C3 为基准对 C1/C2 的 focal 特征加权
(d) later vs never（C2 vs C3）作为准 within-product 对比单独成表
```

(b) 是最硬的一道：firm FE 吃掉所有公司层面不变混杂后，格子差异若存活，"firm quality 故事"基本出局。预先承认 (b) 子样本会小，作为 T5 的 Panel B 而非唯一证据。

### 6.3 Focal 与 peer−focal 诊断（v1 保留）

事件层回归，focal firm 与 calendar week 聚类，不放 event FE。v1 的三分支解释逻辑保留。

---

## 7. 选择问题四道防线【新增整节，原因 M1】

独立成节的原因：这是 T3 主表的第一审稿压力点，必须在设计阶段而非回应阶段处理。

| 防线 | 操作 | 杀伤的混杂 | 所在表 |
|---|---|---|---|
| D1 控制 | focal 特征 × exposure 交互 | 可观察公司差异 | T3 列(2) |
| D2 firm FE | within-firm 子样本 | 全部公司层不变量 | T5 Panel B |
| D3 熵平衡 | C1/C2 向 C3 加权 | 可观察分布差异 | T9 |
| D4 later vs never | C2 vs C3 主对比 | "产品真实性"与"可查验证"分离 | T6 |

预registered 解释纪律：若 D1–D4 中 ≥3 道存活（方向一致、p<0.10），主张成立；若仅 D1 存活，主张降为"与公司特征相关的可信度溢价"，不写因果。

---

## 8. v71：Specificity→备案 预测验证【新增整节，原因 M3】

```text
P(verification_timing ∈ {verified_at_event, later_verified})
  = f(Spec_z, specificity_components, FocalControls, IndustryFE, YearFE)
```

两个用途：
1. **H3 机制**：Spec_z 预测力强（AUC > 0.65 量级）→ specificity 被确立为可验证性的市场可观察代理，H2 的"市场从内容推断"机制闭环；
2. **度量增值**：v1–v5 全部 specificity 工作从"强度调节"升级为"可验证性代理"，前期投入直接进主线。

报告：logit + 线性概率，specificity 分量级（数量/时间/客户/技术）分别进入，看哪类细节最"可验证"。

---

## 9. 场所选择表【新增整节，原因 M4】

```text
P(disclosure via formal CNINFO | GenAI claim)
  = f(verification_timing, Spec_z, FocalControls, FE)
```

预测：可验证产品 → 更可能走高信披责任渠道（正式公告）。这张表把理论链条"可验证性 → 渠道选择 → 市场反应"的第一环显式钉住——v1 从 T2 直接跳 T3 主表，渠道选择机制悬空（M4 原因）。理论锚：自愿披露的可验证性理论 + 互动平台低法律责任属性（Lee & Zhong 2022 JAE 一支）。

---

## 10. 非上市模型两用途（v1 §8 全部保留）

confound calendar 字段表、"不用批次公示日当 shock 日"、±2 交易日污染窗口、competition density 三个计数变量与方向不预设——均无修改。仅一处衔接：confound calendar 的排除检验从 v1 判别标准第 4 条移入 T3 主表的标准列（每个规格都报告排除后系数），而非单独一张表后置。

---

## 11. pre-registry 窗口处理【新增整节，原因 M6】

时间轴：

```text
2023-01-10  深度合成管理规定施行（深合成算法备案可用）
2023-08-15  生成式 AI 暂行办法施行
2023-08-31  首批生成式备案公示
2024-04-02  国家网信办首次集中公告（附件1）
```

规则：
- 2023-01-10 至 2023-08-15 的披露事件：`verification_type` 只能取 `deep_synthesis` 或 `none`，单独 `pre_registry_era=1` 标记；
- 主表默认**包含**该窗口（它是披露最密集期，砍掉伤 N），但 era dummy 与 verification 交互；
- 稳健性：剔除该窗口重跑，报告系数稳定性；
- 明确不做的事：不把 2023 上半年的"无生成式备案"解释为 cheap talk——当时制度不存在，never_verified 的定义对该窗口只能基于深合成备案。

---

## 12. 表序【修改】

| 表 | 内容 | 相对 v1 的变化 |
|---|---|---|
| T1 | 样本 funnel：203池→扩池→备案匹配→C1/C2/C3 分布 | 四格分布改为 timing 三组分布 |
| T2 | registry master 描述 + batch_public_date 滞后分布 | 新增公示滞后描述（H1 可行性证据） |
| **T2.5** | **场所选择 determinants** | 【新增，M4】 |
| T3 | 主表：pooled interaction（C1/C2/C3），Panel A 含 2×2 描述 | pooled 升主位【M5】 |
| T4 | focal 与 peer−focal 诊断 | 不变 |
| T5 | 验证梯度 + within-firm Panel B | 增加 D2 防线【M1】 |
| T6 | timing：verified_at_event / later / never 三组对比 | 由 washing 时序表升级为 H1/H2 分层主证据【M2/M8】 |
| **T7** | **Spec_z → 备案预测** | 【新增，M3】 |
| T8 | competition density 异质性 | 不变 |
| T9 | 熵平衡 + 产品匹配质量稳健性 | 合并 v1 T9 与 D3 防线 |

---

## 13. 判别标准【修改】

设计成立的最低信号（替换 v1 §7）：

1. pooled 规格中 β1(C1) < 0 显著，或——若 C1 功效不足——β2(C2) < 0 显著且 β2 ≠ β3（Wald p<0.10）；
2. C3（never_verified）peer 反应不显著；
3. 选择问题防线 D1–D4 至少 3 道存活；
4. T7 中 Spec_z 显著预测最终备案（H3 闭环）;
5. 排除非上市 confound 窗口后结论不变；
6. 高置信产品匹配子样本方向一致。

主张校准规则【新增】：
- C1 功效足 + 防线存活 → 写强主张 H1；
- 仅 C2/C3 分层 → 写弱主张 H2 + H3 机制，标题与摘要相应收缩；
- 两者皆无 → 进入 §14 回查，不换题。

---

## 14. 失败回查顺序

v1 §11 七条全部保留，新增三条插入队首：

```text
0a. C1/C2/C3 分组是否正确使用 batch_public_date（最常见错误：误用 filing_date）
0b. later_verified 是否被截尾污染（样本期末附近的事件没给备案留出时间——
    对 event_date > 样本期末−180天 的事件，never_verified 标签不可信，应标 censored）
0c. pre_registry_era 事件是否被错误计入 never_verified
```

0b 是 v1 完全没有的截尾问题：2026 年的披露"尚未备案"≠"永不备案"。处理：never_verified 的定义要求事件日距样本期末 ≥180 天，不足的标 `censored` 排除出 C3。

---

## 15. 执行顺序

```text
v67 registry master（含 batch_public_date、深合成层、主键修正）
v68 traceback（含 verified_at_event_date）
v69 verification labels（四值 timing 变量、censoring 规则）
v70 cell-size precheck → 主张校准决策 → 主表
v71 Spec→备案预测 + 场所选择表
v72 nonlisted confound calendar + competition density（v1 的 v71 顺延）
```

瓶颈不变：v67 的附件 3–11 本地补全先行。v70 的 cell-size 预检是新增的决策闸门——它决定论文写 H1 还是 H2 主线，必须在写任何结果叙述前完成。