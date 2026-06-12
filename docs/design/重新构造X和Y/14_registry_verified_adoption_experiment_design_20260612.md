# T05 备案/登记验证增强实验设计（20260612）

## 0. 一句话版本

把 T05 从“GenAI 公告是否影响 peer”改成：

> 资本市场是否能区分上市公司 GenAI 披露的行政可验证性？当 focal firm 的 GenAI disclosure 能被 CAC 备案/登记产品反向验证时，product-market peers 是否发生更强的负向重估；当披露只有互动平台或无备案/登记支撑时，peer 反应是否消失？

这个设计不把非上市大模型公司当 focal event。非上市模型只做两件事：

1. 重大发布日进入 GenAI confound calendar；
2. 全量备案库进入赛道事前竞争密度。

## 1. 研究对象与核心贡献

### 1.1 研究对象

对象不是“所有大模型发布”，也不是“上市公司说过 AI”。对象是：

```text
A 股上市公司披露的 GenAI initiative / adoption claim
```

并进一步问：

```text
该 claim 是否能被官方备案/登记产品验证？
```

### 1.2 中国制度贡献

中国 GenAI 监管形成了两个有用的行政层：

- `已备案`：更接近模型/服务提供方的自研或服务提供能力；
- `已登记`：更接近应用/功能通过 API 等方式调用已备案模型能力后的上线登记，适合验证 adoption，而不是验证自研。

因此，T05 可以把传统 GenAI announcement event study 升级为：

```text
announcement credibility under administrative verification
```

### 1.3 与 POM/Qian 的关系

POM/Qian 的单位是上市公司的 GenAI announcement / initiative。它不会覆盖大量非上市模型公司，这不是漏洞，而是研究边界。

T05 不复制“公告事件本身”，而是借鉴其事件研究和人工筛选方法，加入中国特有的备案/登记验证层。

## 2. 数据主表：firm-product registry master

### 2.1 输入

先补全 CAC 备案/登记库，至少包括：

- 生成式人工智能服务已备案/已登记附件，含附件 3-11；
- 既有 v64/v65/v66 官方备案主库；
- 深度合成服务算法备案与普通算法备案中的 GenAI 相关记录，作为补充验证层，不作为生成式服务登记的替代。

### 2.2 产出主键表

产出一张：

```text
上市公司 × 备案产品 × 备案/登记日期
```

建议文件：

```text
results/v67_registry_firm_product_master_20260612/
  registry_firm_product_master.csv
  registry_firm_product_candidates_all.csv
  registry_product_match_review_queue.csv
  registry_product_master_counts.csv
```

核心字段：

| 字段 | 含义 |
|---|---|
| `registry_product_id` | 稳定主键，建议 hash(source + filing_no + entity + product_name + status) |
| `registry_source` | genai_service / deep_synthesis / algorithm |
| `registry_status` | 已备案 / 已登记 / 备案清单 |
| `verification_type` | self_filing / app_registration / algorithm_or_deep_synthesis |
| `registry_entity` | 备案/登记主体 |
| `registry_product_name` | 模型、服务、应用或功能名 |
| `filing_no` | 备案号/登记号 |
| `filing_date` | 表内备案/登记日期 |
| `public_batch` | 公示批次 |
| `listed_code` | 关联 A 股代码 |
| `listed_name` | A 股简称 |
| `relation_to_listed` | direct / subsidiary / branch / group_related / uncertain |
| `match_method` | full_name_exact / subsidiary_map / product_text / manual |
| `match_confidence` | high / medium / low / manual_keep / manual_drop |
| `source_file` | 官方附件 |
| `source_url` | 官方链接 |

### 2.3 关键规则

`已登记` 单独保留为 adoption verification，不要把它写成自研模型。

```text
已备案 = 更接近 service/model provider verification
已登记 = 更接近 application/function adoption verification
```

市场事件日不优先使用备案批次公示日。备案/登记日期用于验证和时序，不自动等于资本市场 event day。

## 3. 反向定位首次披露日

### 3.1 目标

对每个 `registry_product_id`，反向找它在两类上市公司信息源中的首次出现：

```text
D1  = 巨潮/正式公告首披日
D1' = 互动易/上证e互动首提日
```

### 3.2 检索键

按优先级：

1. `filing_no` / 备案号 / 登记号；
2. `registry_product_name` 精确名；
3. 产品名别名、模型名别名；
4. `registry_entity + product_name`；
5. `listed_name + product_name`。

### 3.3 产出字段

建议文件：

```text
results/v68_registry_product_first_disclosure_traceback_20260612/
  registry_product_cninfo_first_mentions.csv
  registry_product_iip_first_mentions.csv
  registry_product_disclosure_timeline.csv
```

核心字段：

| 字段 | 含义 |
|---|---|
| `registry_product_id` | 备案产品主键 |
| `listed_code` | A 股代码 |
| `D1_cninfo_date` | 正式公告首披日 |
| `D1_cninfo_announcement_id` | 巨潮公告 ID |
| `D1_cninfo_title` | 公告标题 |
| `D1_iip_date` | 互动平台首提日 |
| `D1_iip_id` | 互动平台问答 ID |
| `first_public_date` | min(D1, D1') |
| `first_public_source` | cninfo / iip |
| `days_disclosure_to_filing` | filing_date - first_public_date |
| `timing_type` | pre_disclosure_filing / post_disclosure_filing / same_day / unknown |
| `product_mention_match` | filing_no / exact_product / fuzzy_product / manual |
| `llm_confirm_needed` | 0/1 |

### 3.4 时序解释

时序本身是 washing 证据：

| 时序 | 解释 |
|---|---|
| `先备案/登记，后公告` | 更像真实 adoption/产品上线后的披露 |
| `公告后很快备案/登记` | 可接受，可能是披露领先于行政公示 |
| `先吹很久，后无备案/登记` | cheap talk / washing 风险较高 |
| `互动平台先提，正式公告后发` | 互动平台可作 backfill 或 claim-support |

## 4. 给 GenAI 披露池打验证标签

### 4.1 输入披露池

至少覆盖：

- 当前 `203` 池；
- v56/v52 扩池后的全部 GenAI disclosure；
- 后续从 111k CNINFO universe 召回出的候选；
- 互动平台扩展样本，单独保留来源标签。

### 4.2 join 逻辑

对每条披露事件，匹配到 `registry_firm_product_master`：

```text
listed_code × product_name / filing_no / model_name / application_name
```

需要 LLM 的只是一件事：

```text
披露文本中的产品/模型/应用名称 是否与备案产品名指向同一对象？
```

不需要 LLM 重新判断整条披露是否 A/B/C/D-fw。

### 4.3 验证字段

建议输出：

```text
results/v69_disclosure_registry_verification_labels_20260612/
  genai_disclosures_with_registry_verification.csv
  product_match_llm_review_queue.csv
  verification_matrix_counts.csv
```

核心字段：

| 字段 | 含义 |
|---|---|
| `event_id` | 披露事件 ID |
| `listed_code` | A 股代码 |
| `event_date` | 披露事件日 |
| `disclosure_source` | formal_cninfo / iip / ir_minutes / other |
| `manual_verdict_v33` | A / B / C / D-fw / D / U |
| `registry_match` | 0/1 |
| `matched_registry_product_id` | 匹配到的备案产品 |
| `verification_type` | self_filing / app_registration / algorithm_or_deep_synthesis / none |
| `verification_level` | 2 / 1 / 0 |
| `timing_type` | pre_disclosure_filing / post_disclosure_filing / no_registry |
| `days_disclosure_to_filing` | filing_date - event_date |
| `product_match_confidence` | exact_filing_no / exact_product / llm_confirmed / fuzzy_uncertain |

### 4.4 三层可信度

主变量不只是一枚 `verified` dummy，应保留三层：

| 层级 | 定义 | 解释 |
|---|---|---|
| `verification_level=2` | 自研/服务提供主体有备案 | 最硬，接近自研或服务能力验证 |
| `verification_level=1` | 应用/功能已登记 | 中等，验证 adoption 或应用上线 |
| `verification_level=0` | 公告有 GenAI claim，但无备案/登记匹配 | cheap talk / unverified contrast |

## 5. 第一张主表：四格验证矩阵

### 5.1 四格定义

主表先做 2×2，避免过度细分：

|  | `registry_match=1` | `registry_match=0` |
|---|---|---|
| 正式公告 / CNINFO | Q1: verified formal disclosure | Q2: unverified formal disclosure |
| 互动平台 / IIP | Q3: verified IIP claim | Q4: unverified IIP claim |

其中 Q1 再拆三层：

```text
Q1a: formal + self_filing
Q1b: formal + app_registration
Q1c: formal + other registry support
```

### 5.2 待报告 outcome

每个格子报告：

```text
peer CAR[0,+1]
focal CAR[0,+1]
peer - focal CAR[0,+1]
```

同时报告：

```text
events
focal firms
peer-event observations
matched registry products
```

### 5.3 规格提醒

四格是事件层分类。如果在 pooled peer panel 中直接加入四格 dummy，`event FE` 会把它吸收。

因此 peer 主表用两种可行做法：

1. **分四格分样本跑冻结规格**：每个格子内沿用 v6 口径；
2. **pooled interaction**：用 peer-level exposure 与四格交互，例如 `PeerExposure × Q1`，再加入 event FE。

建议第一版采用做法 1，最直观。

对 `focal CAR` 和 `peer - focal CAR`，它们是事件层 outcome，不能同时放 event FE。作为诊断表报告事件层均值、标准误、按 focal firm 与 calendar week 聚类的回归即可。

## 6. 基准回归规格

### 6.1 Peer panel 冻结规格

对每个四格子样本分别估计：

```text
PeerCAR_{e,p} = beta * PeerExposure_{e,p}
              + EventFE_e
              + PeerIndustryWeekFE_{p,w}
              + error_{e,p}
```

其中：

- `e` 是 focal disclosure event；
- `p` 是 product-market peer；
- `PeerExposure` 使用既有 v6/v22 product-market peer 构造；
- 标准误按 `event` 与 `peer firm` 双向聚类。

如果当前实现是 top-N peer 均值而不是 peer-vs-nonpeer panel，则第一版先报告事件层 peer 平均 CAR，并在正式主表前补出 peer-level exposure panel。

### 6.2 Pooled interaction 备选规格

```text
PeerCAR_{e,p} =
  beta1 * PeerExposure_{e,p} * Q1_verified_formal_e
+ beta2 * PeerExposure_{e,p} * Q2_unverified_formal_e
+ beta3 * PeerExposure_{e,p} * Q3_verified_iip_e
+ beta4 * PeerExposure_{e,p} * Q4_unverified_iip_e
+ EventFE_e
+ PeerIndustryWeekFE_{p,w}
+ error_{e,p}
```

判别重点：

```text
beta1 < 0 且显著；
beta4 约等于 0；
beta1 显著小于 beta2 / beta4。
```

### 6.3 Focal 与 peer-focal 诊断

事件层：

```text
FocalCAR_e = alpha + gamma1 Q1_e + gamma2 Q2_e + gamma3 Q3_e + controls + error_e

PeerMinusFocalCAR_e = alpha + gamma1 Q1_e + gamma2 Q2_e + gamma3 Q3_e + controls + error_e
```

`peer - focal` 是解释防守关键：

- 如果 peer 显著负、focal 不负或更少负，支持竞争性重估；
- 如果 peer 与 focal 都显著负，说明市场可能在惩罚 GenAI hype / 投资成本 / 非上市模型竞争压力；
- 如果 peer-focal 不分层，不能讲纯粹 business stealing。

## 7. 判别标准

设计成立的最低信号：

1. `Q1 verified formal disclosure` 的 peer CAR 显著为负；
2. `Q4 unverified IIP claim` 不显著；
3. 验证强度有梯度：

```text
self_filing stronger than app_registration stronger than no_registry
```

4. 排除 GenAI confound calendar 后，Q1 结果不消失；
5. 产品匹配高置信子样本中方向一致。

如果四格完全不分层，先回查：

1. 产品名匹配质量；
2. 备案产品和公告事件的时序；
3. IIP 是否被投资者提问时点污染；
4. 是否被 DeepSeek/Kimi/智谱等非上市重大发布日污染；
5. 是否把登记 adoption 误解释为自研。

只有在这些都排除后，才判断设计失败。

## 8. 非上市模型的两个用途

### 8.1 Confound calendar

建立：

```text
nonlisted_model_release_calendar.csv
```

字段：

| 字段 | 含义 |
|---|---|
| `model_event_id` | 非上市模型事件 ID |
| `model_name` | DeepSeek / Kimi / GLM / MiniMax / Baichuan 等 |
| `entity_name` | 发布主体 |
| `event_date` | 发布会/产品发布日期 |
| `release_type` | model_launch / major_version / API_open / price_cut / open_source |
| `major_event` | 0/1 |
| `source_url` | 来源 |
| `notes` | 备注 |

规则：

- 用发布会日、产品上线日、开源日、API 开放日；
- 不用 CAC 批次公示日作为非上市模型 shock 日；
- 对 focal disclosure 标记 `within_nonlisted_model_release_pm2`。

主表至少做：

```text
排除 ±2 交易日污染窗口
加入 confound dummy
单独列出污染样本数量
```

### 8.2 赛道事前竞争密度

用全量备案库，包括非上市主体，构造 focal 进入赛道时的竞争密度：

```text
pre_event_same_category_registry_count
pre_event_same_category_nonlisted_count
pre_event_same_category_listed_count
```

赛道分类可从产品名/用途生成：

```text
通用对话/办公/代码/图像/视频/数字人/金融/医疗/教育/汽车/工业/政务/客服/搜索/RAG/Agent
```

机制表：

```text
PeerCAR = beta1 * PeerExposure * Verified
        + beta2 * PeerExposure * Verified * CompetitionDensity
        + FE
```

竞争密度方向不强行预设：

- 高密度可能意味着进入拥挤赛道，边际威胁较弱；
- 也可能意味着同类替代更强，peer 重估更负。

先作为机制/异质性，不作为主识别。

## 9. 样本构造流程

### Step 1: 补全备案库并建 firm-product 主键表

目标：

```text
上市公司 × 备案产品 × 备案/登记日期
```

预计人工确认后有 200-300 个可用产品候选。

注意：

- `已登记` 单独列出；
- 子公司、分公司、研究院主体必须人工确认关系；
- 非上市主体保留在全量库，但不进 focal event。

### Step 2: 反向定位备案产品首次披露

对每个备案产品，定向检索：

```text
产品名 + 备案号 + 主体名
```

到：

- 巨潮正式公告库；
- 互动易 / 上证e互动库。

产出 `D1` 与 `D1'`。

### Step 3: 给 203 池和扩池 GenAI 披露打验证标签

join 到产品主键表，形成：

```text
registry_match
verification_type
verification_level
timing_type
```

LLM 只用于模糊产品名确认。

### Step 4: 四格主表

生成：

```text
Q1 verified formal
Q2 unverified formal
Q3 verified IIP
Q4 unverified IIP
```

报告：

```text
peer CAR
focal CAR
peer - focal
```

### Step 5: 非上市模型辅助层

只做：

1. confound calendar；
2. competition density moderator。

不做供给冲击主设计。

## 10. 表序建议

| 表 | 内容 | 目的 |
|---|---|---|
| T1 | 样本构造 funnel：203 池、扩池、备案匹配、四格分布 | 说明样本不是随意挑 |
| T2 | firm-product registry master 描述 | 说明行政验证层来源 |
| T3 | 四格 peer CAR 主表 | 核心结果 |
| T4 | 四格 focal CAR 与 peer-focal 诊断 | 防止误讲 focal good news |
| T5 | self_filing / app_registration / no_registry 梯度 | 证明验证强度有经济含义 |
| T6 | timing：先披露后备案 vs 先备案后披露 | washing 时序证据 |
| T7 | 排除非上市模型 confound calendar | 干净度 |
| T8 | competition density 异质性 | 机制 |
| T9 | 产品匹配质量与人工复核稳健性 | 数据可信度 |

## 11. 失败回查顺序

如果结果不显著或四格不分层，按下面顺序查，不要立刻换题：

1. 产品匹配：是否把通用产品名误配到备案产品；
2. 备案主体：是否把非上市主体或同集团主体错归到 A 股；
3. 登记解释：是否把 adoption 登记误写成自研；
4. 事件日：是否用错备案批次公示日，而不是披露首日；
5. 混杂日：是否落在非上市模型重大发布窗口；
6. 样本池：203 池是否太窄，需要扩到全部 GenAI disclosure；
7. peer 网络：是否 top-N peer 定义过窄或行业-week FE 吃掉有效变异。

## 12. 当前执行结论

这条路线比“纯 GenAI launch”更可行，也比“外部供给冲击 × 暴露度”更贴近 T05。

当前应优先执行：

```text
v67 firm-product registry master
v68 product first disclosure traceback
v69 disclosure registry verification labels
v70 four-cell main tables
v71 nonlisted confound calendar + competition density
```

主线暂定为：

> 备案/登记行政验证能否区分 GenAI corporate disclosure 的可信度，并解释 product-market peer 的负向重估。

