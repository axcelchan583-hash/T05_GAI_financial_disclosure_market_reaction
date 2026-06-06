# T05 X/Y 重构实验设计：竞争对手与宽口径合作性关联方

日期：2026-06-07

用途：把当前已经跑出的 T05 结果、准备改造的 X/Y 方向、以及下一轮可执行实验矩阵整理成一份供外部模型/网页版 Pro 审阅的设计文档。本文不是论文草稿，也不是最终口径声明；它的目标是帮助判断：是否值得把当前“GenAI 披露 -> 同行负向重估”主线，扩展为“竞争网络与合作网络的反向市场重估”。

## 1. 当前研究问题的重新表述

旧表述偏窄：

```text
焦点公司 GenAI 披露是否使产品市场同行产生负向异常收益？
披露具体性是否加剧这种同行负向重估？
```

拟改造后的表述：

```text
焦点公司披露具体 GenAI initiative 后，资本市场是否沿企业关系网络进行方向相反的价值重估：
产品市场竞争对手因竞争威胁被下调，既有合作性经济关联方因互补收益、需求扩张或生态收益被上调？
```

核心变化：

- X 仍是焦点公司的具体 GenAI initiative 披露。
- Y 不再只看单一产品市场同行，而是区分两类受影响公司：
  - `Competitors`：产品市场竞争对手。
  - `Cooperative linked firms`：事件前已经存在合作性/交易性/互补性经济关系的公司。
- `Specificity` 从旧主线中的核心 X，改为信号可信度/执行性强度的机制变量。
- 公告中点名 GenAI 合作方不再作为唯一合作者口径。原因是样本过窄，且大量合作方是腾讯云、百度网讯、华为云、智谱、澜舟、高校/研究院、地方平台公司，并非 A 股上市公司。

## 2. 理论直觉

同一条 GenAI 披露可能同时包含两类经济含义。

第一，对产品市场竞争者而言，GenAI initiative 是焦点公司能力跃升、产品创新或效率改善的信号。若焦点公司未来更容易夺取客户、降低成本或提高产品质量，竞争者的未来租金和增长期权会被重估下调。

第二，对既有合作性经济关联方而言，焦点公司的 GenAI initiative 可能意味着新的需求、联合商业化机会、技术互补、供应链升级或生态扩张。若关联方已经与焦点公司存在客户、供应商、战略合作、联合研发或合资关系，它们更可能分享该能力信号带来的正向价值。

因此，预期不是“所有同行都跌、所有合作方都涨”的机械结果，而是：

```text
竞争暴露越强 -> 负向重估越强；
合作/互补暴露越强 -> 正向重估越强；
披露越具体、越可执行，上述关系网络重估越明显。
```

## 3. 文献位置

### 3.1 同一样本多类关联方设计

- Fee and Thomas (2004, JFE) 围绕横向并购，同时考察 customer、supplier、rival firms 的财富效应。
- Shahrur (2005, JFE) 同样在横向收购中同时研究 rivals、suppliers、corporate customers。
- Oxley, Sampson and Silverman (2009, Management Science) 研究 R&D alliance announcements 对 partners 和 rivals 的影响。该文的关键启发是：战略事件的合作方收益与竞争对手收益可以放在同一框架下解释，但 rival 的符号用于区分“竞争力增强”还是“竞争缓和”。

这些文献支持“同一焦点事件 -> 多类关联公司 CAR”的设计，但它们不是 AI/GenAI 场景。

### 3.2 竞争对手负向重估

- Lang and Stulz (1992, JFE) 提供行业内传染效应与竞争效应的分解框架。
- Foster (1981, JAE) 与 Han, Wild and Ramesh (1989, JAE) 支撑行业内信息传递。
- Chen, Ho and Ik (2005, Journal of Business) 是最贴近本项目的负向竞争先例：新产品发布会使行业竞争对手产生负向异常收益。
- Bloom, Schankerman and Van Reenen (2013, Econometrica) 提供技术溢出与 product market rivalry/business stealing 同时存在的理论框架。

### 3.3 合作性关联方正向重估

- Chan et al. (1997, JFE)、McConnell and Nantell (1985, JF)、Das, Sen and Sengupta (1998, AMJ) 证明战略联盟/合资公告通常给参与方带来正向估值。
- Cohen and Frazzini (2008, JF) 与 Menzly and Ozbas (2010, JF) 支撑经济关联企业之间的信息传导。
- Qian, Peng and Li (2025/2026, POM) 是 GenAI 场景下最直接的供应商溢出先例，但它只研究供应商，不研究竞争对手。

### 3.4 本项目可主张的贡献

谨慎表述：

```text
据我们所知，现有 AI/GenAI 资本市场文献尚未围绕同一批 GenAI initiative 披露事件，
同时估计产品市场竞争对手与合作性经济关联方的短窗口市场反应。
本文将横向竞争网络和纵向/合作网络放在同一事件研究框架中，
用以刻画 GenAI 能力披露如何沿企业关系网络重新分配市场价值。
```

注意：Fee and Thomas、Shahrur 的并购文献中 rivals 往往为正，因此不能把它们引用为“对手必然负”的符号证据；它们只能作为多类关联方设计前身。

## 4. 当前已有结果事实

### 4.1 当前冻结 X

当前最可信的机器辅助 GenAI treatment universe 来自 v36：

| 样本层 | 数量 |
|---|---:|
| raw audit rows | 533 |
| unique candidate events | 487 |
| first event per focal firm | 363 |

构成：

- 414 条 DeepSeek-pro direct event-date candidates。
- 119 条 keyword-recovered backfill rows，去重后形成 73 个更早候选事件。

定位：

```text
v36 是当前最好的机器辅助 X，但仍是 pre-manual-coding，不是最终论文 treatment。
```

### 4.2 竞争对手侧已有主结果

当前最能写的 peer 口径：

```text
liu_product_tfidf_same_industry_d_top10
```

含义：基于中文产品/经营文本 TF-IDF 的同业 Top10 竞争对手网络。该口径有中文文献支撑，且现有实证结果显著。

主样本：

| 项目 | 数值 |
|---|---:|
| event-study rows | 2,790 |
| events | 316 |
| peer firms | 1,385 |

事件研究结果：

| 窗口 | 均值 | p 值 | 解释 |
|---|---:|---:|---|
| AR[-1] | -0.00095 | 0.3350 | 事前一天不显著 |
| AR[0] | -0.00254 | 0.0205 | 事件日负向 |
| AR[+1] | -0.00210 | 0.0541 | 次日边际负向 |
| CAR[0,+1] | -0.00464 | 0.0045 | 当前建议主 Y |
| CAR[-1,+1] | -0.00559 | 0.0027 | 三日窗口也为负 |

污染清洗：

| 清洗口径 | CAR[0,+1] | p 值 | N |
|---|---:|---:|---:|
| 全样本 | -0.00465 | 0.0045 | 2,789 |
| 删除 peer 自身严格 GenAI 事件 | -0.00483 | 0.0034 | 2,773 |
| 删除 peer 重大公告 | -0.00422 | 0.0156 | 1,868 |
| 删除 peer 自身 GenAI 或重大公告 | -0.00422 | 0.0155 | 1,865 |

长窗口：

| 窗口 | 均值 | p 值 | 覆盖 |
|---|---:|---:|---:|
| CAR[0,+20] | -0.02927 | < 0.001 | 2,206 rows |
| CAR[0,+60] | -0.06386 | < 0.001 | 1,670 rows |

解释边界：长窗口不反转有助于排除单纯注意力/流动性轮动，但不能单独证明真实市场份额转移。

### 4.3 当前机制结果：Specificity x AIActivePeer

当前最稳的机制证据是：

```text
披露越具体，且同行越处于 AI-active 技术空间，同行 CAR[0,+1] 越负。
```

主要结果：

| 口径 | Spec x AIActivePeer | p 值 | N | events |
|---|---:|---:|---:|---:|
| v31 base controls | -0.0032 | 0.0080 | 2,719 | 316 |
| 加 Size/Beta/Volatility/MB 主效应 | -0.0026 | 0.0292 | 2,404 | 281 |
| 加 Spec x firm-character 全套交互 | -0.0025 | 0.0334 | 2,404 | 281 |

严格污染清洗后：

| 口径 | Spec x AIActivePeer | p 值 | N | events |
|---|---:|---:|---:|---:|
| base controls | -0.0030 | 0.0712 | 1,808 | 310 |
| 加 firm-style main effects | -0.0026 | 0.1082 | 1,618 | 276 |
| 加 Spec x firm-character 全套交互 | -0.0025 | 0.1292 | 1,618 | 276 |

解释：

- 主样本中机制 survives firm-character guard。
- 严格清洗样本方向和量级一致，但功效下降，不能写成“清洗后仍稳健显著”。

### 4.4 供应商窄口径现状

Qian/POM 式上游上市供应商复制目前不适合直接当主结果。

v36 first-event 样本：

| 项目 | 数值 |
|---|---:|
| input events | 363 |
| events with listed suppliers | 41 |
| supplier-event observations | 85 |
| unique listed suppliers | 74 |
| rows with AR0/CAR[0,+1] | 68 |
| event link rate | 11.29% |

上游供应商 CAR[0,+1]：

| 样本 | 均值 | p 值 | N |
|---|---:|---:|---:|
| combined first event per firm | -0.00292 | 0.4967 | 68 |
| combined unique events | -0.00516 | 0.2264 | 83 |
| direct414 unique | 0.00033 | 0.9572 | 53 |

结论：

```text
仅用上市上游供应商，覆盖率太低，方向也没有 Qian/POM 式正向结果。
该口径应作为“合作性关联方”的一个子类，而不应单独作为主 Y。
```

### 4.5 已知 null/关闭路线

跨事件 focal-peer 镜像不支持零和再分配：

| 检验 | 结果 |
|---|---:|
| FocalCAR x PeerSimilarity | 0.0003, p = 0.8264 |
| 清洗 peer GenAI/重大公告后 | 0.0017, p = 0.2823 |

这条线应关闭。当前竞争机制来自同一事件内不同 peer 的横截面梯度，而不是焦点公司涨幅越大、同行跌幅越大的跨事件镜像。

## 5. 为什么要改成宽口径合作性关联方

窄口径 GenAI 合作者的问题：

1. 一条公告通常只点名 1 个合作方，少数 2-3 个。
2. 点名合作方大量不是 A 股上市公司：腾讯云、百度网讯、华为云、智谱、澜舟、高校、研究院、地方平台。
3. 即使映射到母公司，也会引入港股/美股/非上市混合市场，事件窗口和预期收益模型复杂。
4. 单纯“谁和谁一起做 GenAI”没有宽网络设计的研究价值，容易变成公告文本抽取练习。

宽口径更合理：

```text
我们不是研究“GenAI 公告中点名的合作方是否上涨”，
而是研究“GenAI 能力披露如何沿焦点公司既有竞争网络和合作网络重新分配资本市场价值”。
```

因此，合作性关联方定义应扩大为事件前已经存在的经济关联：

- 上游供应商；
- 下游客户；
- 客户+供应商 union；
- 战略合作/联合研发/合资/共同投资关系；
- 公告点名合作方，作为高可信子样本或事件特征。

关键识别约束：

```text
所有合作性关系必须在 GenAI 披露前存在，优先使用 event_year - 5 到 event_year - 1。
```

## 6. 下一轮实验矩阵

### 6.1 Treatment event universe

至少跑三层：

| X 样本 | 定义 | 目的 |
|---|---|---|
| X1 first-event main | v36 first event per focal firm, 363 firms | 最接近 Qian/POM 的 first initiative 设计 |
| X2 unique-event extension | v36 unique candidate events, 487 events | 扩展样本量，检查 repeated events |
| X3 high-confidence direct | v34 direct event-date candidates, 414 unique direct rows/307 firms | 更干净但可能少 |

若手工核验资源有限，优先对 X1 中进入回归的事件人工抽样核验。

### 6.2 Competitor definitions

当前建议把 `C1` 作为主候选，但不要提前承诺最终主口径。

| 编号 | 口径 | 预期 | 文献/理由 |
|---|---|---|---|
| C1 | 中文产品/经营文本 TF-IDF same-industry Top10 | 负 | 当前已有显著结果；同业约束减少跨行业误配 |
| C2 | 中文产品/经营文本 TF-IDF same-industry Top5 | 负 | 更近竞争对手，应更强但 N 少 |
| C3 | annual-report business text same-industry Top5/Top10 | 负 | 更贴 Hoberg-Phillips，但旧结果未显著，适合稳健性 |
| C4 | CSMAR main-business/business-scope Top5/Top10 | 负 | 覆盖高，需警惕经营范围模板语言 |
| C5 | low-similarity/placebo peers | 约 0 | 安慰剂 |

### 6.3 Cooperative linked firm definitions

核心目标是找到既有关系网络中能支撑正向 CAR 的合理口径。

| 编号 | 口径 | 预期 | 风险 |
|---|---|---|---|
| L1 | upstream listed suppliers | 正 | 当前覆盖低且结果不正；不能单独当主口径 |
| L2 | downstream listed customers | 正 | 需要从 CSMAR 关系表确认方向和覆盖 |
| L3 | suppliers + customers union | 正 | 样本更大，但关系异质 |
| L4 | direction-specific: suppliers vs customers separately | supplier/customer 可不同 | 用于判断正向是否只来自某一侧 |
| L5 | strategic partners / JV / co-R&D relations from announcement/network data | 正 | 关系抽取成本高，覆盖未知 |
| L6 | event-named listed partner | 正 | 纯度高但大概率样本过小，只作补充 |
| L7 | event has named partner / big-tech partner / research partner as event feature | 对 competitor 更负；对 linked firms 更正 | 不是 Y，而是 X/机制特征 |

### 6.4 Outcomes

主窗口建议：

| Y | 用途 |
|---|---|
| AR[0] | 和 Qian/POM 对齐，但中国披露时间不精确 |
| CAR[0,+1] | 当前建议主 Y |
| CAR[-1,+1] | 检查提前泄露/盘前盘后 |
| CAR[0,+5] | 短期持续性 |
| CAR[0,+20] | 排除快速反转，适合作为稳健性 |

优先级：

```text
主文：CAR[0,+1]
辅助：AR[0], CAR[-1,+1]
稳健性：CAR[0,+5], CAR[0,+20]
```

### 6.5 Estimation

#### 事件研究表

对每种 relation type 单独报告：

```text
mean AR[-1], AR[0], AR[+1]
mean CAR[0,+1]
median
positive share
t-test / sign test
N, events, related firms
```

判断方向：

- competitors: expected negative。
- cooperative linked firms: expected positive。
- low-similarity/placebo peers: expected near zero。

#### Stacked related-firm 回归

把 competitors 和 cooperative linked firms 堆叠到同一个 event-related-firm panel：

```text
CAR_{j,e} = alpha
          + beta_1 CooperativeLinked_{j,e}
          + beta_2 RelationStrength_{j,e}
          + Controls_{j,e}
          + EventFE_e
          + epsilon_{j,e}
```

解释：

- 基准组是 competitor。
- `beta_1 > 0` 表示合作性关联方相对竞争对手反应更正。
- Event FE 吸收同一 GenAI 披露事件的共同冲击。
- 标准误至少按 event 聚类；主表可用 event + related firm 双向聚类。

如果同时估计 relation direction：

```text
CAR_{j,e} = alpha
          + beta_s Supplier_{j,e}
          + beta_c Customer_{j,e}
          + beta_p StrategicPartner_{j,e}
          + EventFE_e
          + Controls_{j,e}
          + epsilon_{j,e}
```

基准组仍为 competitor。

#### 机制/异质性

已有机制保留：

```text
CAR_{peer,e} = alpha + beta Spec_e x AIActivePeer_j + EventFE_e + Controls + epsilon
```

新增机制：

```text
CAR_{j,e} = alpha
          + beta_1 CooperativeLinked_{j,e}
          + beta_2 Specificity_e x CooperativeLinked_{j,e}
          + beta_3 NamedPartner_e x CooperativeLinked_{j,e}
          + beta_4 BigTechPartner_e x CooperativeLinked_{j,e}
          + EventFE_e
          + Controls
          + epsilon_{j,e}
```

预期：

- `Specificity x Competitor` 更负，或者在 competitor-only 样本中 `Spec x AIActivePeer < 0`。
- `Specificity x CooperativeLinked` 更正。
- `NamedPartner/BigTechPartner` 提高披露可信度，可能使竞争者更负、合作性关联方更正。

## 7. 选择主口径的规则

为了避免“看到哪个显著用哪个”的明显问题，下一轮应作为测量有效性审计来做。可以全跑合理 grid，但主文口径必须满足以下条件：

1. 符号符合理论：competition negative, cooperative positive。
2. 样本量可解释：至少有足够事件数和 related-firm 行数，不能靠十几二十行样本。
3. 临近口径同向：Top5/Top10、supplier/customer/union 等相邻口径不能完全相反。
4. 不只靠 AR[0]：CAR[0,+1] 至少同向，最好显著。
5. 关系在事件前存在：不能用事件后形成的合作关系。
6. 有明确文献支撑：competitor 使用 product-market rivalry 文献，cooperative linked firms 使用 economic links/supply-chain/alliance 文献。
7. 透明报告 grid：即使最终只选一个主口径，也应在附录报告主要候选口径的方向和 N。

建议对外表述：

```text
我们比较多种文献可支撑的关系网络口径，以检验结果是否依赖某一种测量方式。
主口径依据理论贴合度、样本覆盖、事件前可观测性和相邻口径稳定性确定。
```

不建议表述：

```text
我们尝试了很多口径，选择显著的作为主结果。
```

## 8. 当前最可能的可写结构

### 结构 A：保守版

主结果仍是 competitor negative。

- H1：GenAI initiative 披露使产品市场竞争者产生负向短窗口异常收益。
- H2：该负向重估在 `Specificity x AIActivePeer` 位置更强。
- H3：若事件存在点名合作方/BigTechPartner，竞争者负向反应更强。
- 合作性关联方只作为补充探索，不作为并列主 Y。

适用情形：宽口径合作方仍不显著或样本太小。

### 结构 B：双网络版

主结果变为 competitor vs cooperative linked firms。

- H1：GenAI initiative 披露对产品市场竞争者产生负向异常收益。
- H2：GenAI initiative 披露对既有合作性经济关联方产生正向异常收益。
- H3：二者差异在披露更具体、点名合作方、或焦点公司更具 AI 执行能力时更强。

适用情形：合作性关联方 union 或 customer/supplier 至少一个口径出现正向且样本量可接受，同时 competitor 保持负向。

### 结构 C：价值重估差异版

如果合作方均值不显著，但 stacked 回归中 `CooperativeLinked - Competitor` 显著为正，则可写成：

```text
市场反应不是简单地对所有关联方同向定价，而是按照关系性质产生差异化重估。
合作性关联方的反应显著高于产品市场竞争者。
```

此时不强称“合作方绝对正收益”，而写“相对竞争者更正”。

## 9. 需要 Pro 审阅的问题

请重点审以下问题：

1. 研究问题是否应该从“peer negative reaction”升级为“relationship-dependent revaluation”？
2. 宽口径 cooperative linked firms 是否比窄口径 GenAI named partners 更有理论价值？
3. Fee and Thomas (2004)、Shahrur (2005)、Oxley et al. (2009) 是否足以支撑“同一事件、多类关联方”的设计迁移？
4. 对 GenAI 披露而言，cooperative linked firms 预期为正是否过强？是否应改成“相对 competitors 更正”？
5. 如果 suppliers 不正，但 customers 或 union 正，理论应如何解释？
6. 如果只拿到 competitor negative 和 `Spec x AIActivePeer`，但合作方不显著，是否仍值得作为单边竞争风险论文推进？
7. 主口径选择规则是否足以避免 p-hacking 质疑？还需要哪些透明报告或多重检验处理？
8. 哪种 fixed effects/cluster 最适合 stacked competitor-cooperative panel？
9. 是否需要在正文主表里保留 event FE，以吸收同一 GenAI 公告的共同冲击？
10. 是否应把 `CAR[0,+1]` 作为唯一主窗口，并把 AR[0] 降为辅助？

## 10. 下一步执行清单

1. 在现有 v36 first-event 363 样本上构造 cooperative linked firm panel。
2. 先跑 CSMAR 供应链关系：
   - upstream supplier；
   - downstream customer；
   - supplier + customer union；
   - relation window: event_year - 5 到 event_year - 1。
3. 对所有 linked firms 计算 AR[0]、CAR[0,+1]、CAR[-1,+1]、CAR[0,+5]。
4. 和现有 competitor panel 合并，生成 stacked event-related-firm panel。
5. 输出：
   - sample-flow table；
   - relation-type event-study table；
   - stacked regression table；
   - grid summary；
   - sensitivity: first-event vs unique-events, Top5 vs Top10, AR0 vs CAR[0,+1]。
6. 如果合作方样本仍很小，再尝试从公告文本中抽取 event-named listed partners，但仅作为补充。
7. 若 union/客户/供应商任一口径有正向结果且样本量可接受，再更新理论和主表结构。

## 11. 当前判断

当前证据足以支持：

```text
GenAI initiative 披露后，产品市场竞争对手出现负向短窗口重估；
该负向重估在披露更具体且同行更 AI-active 的位置更强。
```

当前证据尚不足以支持：

```text
GenAI initiative 披露使所有合作性关联方获得正向重估。
```

下一轮实验的价值在于确认：

```text
合作性经济关联方能否形成与竞争对手方向相反、或至少相对更正的市场反应。
```

如果能，论文可升级为“双网络价值重估”设计；如果不能，保守回到“竞争性同行重估 + 披露具体性/AI-active 机制”的单边设计。
