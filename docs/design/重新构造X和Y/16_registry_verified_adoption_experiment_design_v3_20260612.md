# T05 备案/登记验证增强实验设计 v3（20260612）

> 基于 v2 和 v69--v72 实际结果修订。核心变化：产品级严格回溯不再作为主回归样本；firm-level H2 已经试跑且未通过；备案/登记层转为验证、审计、样本机制和场所选择材料，不再单独承担论文主识别轴。

---

## 0. 当前判定

这轮不是数据失败，而是主张边界被数据校准了。

1. **H1 强主张出局**：严格产品级 `verified_at_event` 样本太小，不能支撑“市场在事件日识别行政验证状态”的强因果叙述。
2. **H2 已试跑，当前不成立**：v72 中 `later_verified` 并没有比 `never_verified` 带来更强的负向 peer 反应；在 model/app、own、own×model/app、out=1×model/app 子样本中也没有显著 later-minus-never 梯度。
3. **registry 不能单独当主 X**：`never_verified` 不是干净 cheap-talk 对照组，里面混有大量不需要 CAC 产品备案的可信 compute/app/infrastructure/adoption 事件。
4. **产品级备案不是主样本，而是验证层**：它用于展示可核验案例、识别披露/备案错配、构造场所选择和安静行动表。
5. **巨潮在线补样本不是主要扩池路线**：v71 小试没有捞到新增事件型公告，不应继续无差别全量跑。

论文表述不能再写成：

```text
The market recognizes registry-verified GenAI disclosures.
```

v70--v72 后也暂时不能写成：

```text
The market reacts more strongly to GenAI disclosures that are later validated by administrative records.
```

中文版本：

```text
资本市场并不是简单追逐 GenAI 热点，而是对事后可被行政记录证实的 GenAI 披露给出更强的竞争性重估。
```

当前更稳的定位是：

```text
备案/登记制度揭示了 GenAI 披露与真实产品落地之间的错配；
市场反应主效应仍来自 GenAI 公告本身及其产品市场竞争含义，
而不是简单来自“最终是否备案”这一行政验证标签。
```

---

## 1. 已跑结果作为设计约束

### 1.1 v69 产品回溯库

输入为 v67 firm-product master：

| 指标 | 数值 |
|---|---:|
| 备案/登记产品 | 457 |
| 上市公司 | 210 |
| 本地正式公告严格 D1 产品 | 22 |
| 严格 D1 firm-date | 10 |
| 正式公告任意提及产品 | 58 |
| 正式公告任意提及公司 | 34 |

解释：备案库瓶颈已经打开，但“备案产品本身在正式公告里作为事件披露出现”的比例很低。

### 1.2 v70 产品级标签

在旧 GenAI 披露池中，产品级精确匹配结果如下：

| 样本 | 事件数 | 产品级 later verified | 产品级 verified at event | 产品级未匹配/截尾 |
|---|---:|---:|---:|---:|
| A_all | 203 | 8 | 3 | 192 |
| A_first_firm | 160 | 6 | 2 | 152 |

严格产品 D1 只有 10 个 firm-date，其中只有 4 个落在旧 A_all 的同公司同日事件里：

```text
昆仑万维 2023-04-10
科大讯飞 2023-05-06
汉王科技 2023-10-12
华盛昌 2025-09-03
```

另有 6 个是旧披露池外的备案产品事件：

```text
朗玛信息、云天励飞、华策影视、虹软科技、润建股份、广电运通
```

设计含义：严格产品级 D1 可以做案例表和验证表，不能做主回归。

### 1.3 v71 定向巨潮检索

v71 对 457 个产品生成了 2,890 个检索项，并对优先级最高的 40 条产品查询做在线 pilot。

| 指标 | 数值 |
|---|---:|
| registry products | 457 |
| listed firms | 210 |
| query terms | 2,890 |
| products with query terms | 456 |
| pilot raw hits | 0 |
| pilot same-firm hits | 0 |
| pilot same-firm event-ready title hits | 0 |

对照查询已确认巨潮接口本身可用，能查到科大讯飞、华盛昌、朗玛等已知公告。因此 pilot 为 0 的解释不是接口坏了，而是优先补样本产品在巨潮公告中没有显性事件型命中。

设计含义：不继续把全量在线巨潮检索当主路线。v71 保留为审计计划和附录材料。

### 1.4 v72 H2 主回归试跑

v72 将 v70 的 firm-level timing 并入 v56 event-peer panel，使用 preferred peer method：

```text
liu_product_tfidf_same_industry_d_top10
```

规格：

```text
PeerCAR = β1 · PeerSimilarity × later_verified
        + β2 · PeerSimilarity × never_verified
        + EventFE + PeerIndustryWeekFE
```

双向聚类：

```text
event × peer firm
```

结论：

| 样本 | 子样本 | events | later-minus-never p（含 pre controls） | 方向 |
|---|---|---:|---:|---|
| A_first_firm | all | 122 | 0.332 | later 不更负 |
| A_first_firm | model_app | 77 | 0.620 | later 不更负 |
| A_first_firm | own_model_app | 60 | 0.698 | later 不更负 |
| A_all | all | 152 | 0.272 | later 不更负 |
| A_all | model_app | 90 | 0.472 | later 不更负 |
| A_all | own_model_app | 67 | 0.731 | later 不更负 |

均值诊断也不支持 H2：

| 样本 | 子样本 | later CAR[0,+1] | never CAR[0,+1] |
|---|---|---:|---:|
| A_first_firm | all | -0.16% | -0.74% |
| A_first_firm | model_app | -0.18% | -0.49% |
| A_all | all | -0.39% | -0.68% |
| A_all | model_app | -0.45% | -0.34% |

设计含义：H2 不能作为论文主线。继续硬救 registry 标签会把文章推向错误方向。备案/登记层应退回到“外部验证与样本审计”，帮助解释哪些 GenAI 披露是真产品、哪些是真但未披露、哪些是披露与备案错配，而不是直接预测 peer CAR。

---

## 2. 两套标签，职责分开

### 2.1 主回归标签：firm-level administrative timing

来源：v68/v69 旧披露池标签。

```text
firm_admin_timing ∈ {
  verified_at_event,
  later_verified,
  never_verified,
  unmatched_ambiguous,
  censored
}
```

用途：

- 主回归使用 `later_verified` vs `never_verified`；
- `verified_at_event` 只作描述或并入 pooled interaction 的辅助项；
- `censored` 不进入 never 对照组；
- `unmatched_ambiguous` 不进入主检验。

理由：firm-level 标签牺牲产品精确性，但保住样本量和事件研究可估性。现在论文主线必须先用它判断 H2 是否成立。

### 2.2 验证标签：product-level strict match

来源：v70。

```text
product_strict_timing ∈ {
  product_verified_at_event,
  product_later_verified,
  no_product_text_match,
  no_product_match_recent_censored
}
```

用途：

- 做产品级验证表；
- 做案例表；
- 对主回归结果做方向一致性审计；
- 不作为主回归分组，除非未来新增事件把产品级 matched cell 提高到至少 30 个事件。

---

## 3. 主研究问题

### 3.1 主问题（v72 后修订）

```text
上市公司 GenAI 披露是否会让 product-market peers 出现负向短窗 CAR；
备案/登记记录能否解释这种市场反应背后的“真实落地 / 披露错配 / 场所选择”？
```

### 3.2 可发表贡献

不是“发现备案公告有反应”。真正贡献是：

1. 在 AI-washing 环境里，用 CAC 备案/登记制度审计 GenAI 披露的真实落地；
2. 说明“未备案”不等于 cheap talk，因为 compute、adoption、第三方模型接入、行业应用不一定对应自研大模型备案；
3. 将备案/登记从主 X 降级为验证层，用来修正样本选择、解释场所选择，并支持机制讨论。

### 3.3 不再主打的说法

以下表述只做背景或附录，不作为主 claim：

- 市场能实时查到并使用备案状态；
- 自研大模型备案公告本身引发大样本市场反应；
- 非上市模型发布冲击 A 股企业；
- 产品级备案 D1 样本可以直接估计主效应。

---

## 4. 回归规格的当前地位

### 4.1 H2 pooled interaction（已跑，作为否定性审计）

v72 已按 v6 冻结口径试跑：

```text
PeerCAR_{e,p} =
  β1 · PeerExposure_{e,p} × LaterVerified_e
+ β2 · PeerExposure_{e,p} × NeverVerified_e
+ EventFE_e
+ PeerIndustryWeekFE_{p,w}
+ ε_{e,p}
```

双向聚类：

```text
event × peer firm
```

原主判别：

```text
β1 < 0
β1 - β2 < 0
Wald p < 0.10
```

实跑解释：

- `LaterVerified` 没有显著更负；
- `NeverVerified` 在 all / own 口径反而更负；
- model/app restriction 后差异变小但仍不支持 later > never 的竞争威胁梯度；
- 因此 registry timing 不能作为主 X。

### 4.2 样本规则

主样本：

```text
A_first_firm 或 A_all 正式公告事件
```

报告顺序：

1. A_first_firm：每公司首次，最干净；
2. A_all：保留所有 A 类正式公告，作为样本量增强；
3. A_Dfw_stack：把 D-fw 加入 placebo/contrast，不当主表。

排除：

- `unmatched_ambiguous`;
- `censored`;
- 事件日落入非上市大模型重大发布 ±2 交易日窗口的稳健性版本；
- focal 自身或 peer 自身同日发生备案公示/备案公告的污染版本。

---

## 5. 表序 v3

| 表 | 内容 | 目的 |
|---|---|---|
| T1 | 样本 funnel：363/203/160、v67 457 产品、v69/v70/v71 各层命中 | 先交代为什么主线收缩 |
| T2 | firm-level timing 分布：verified_at_event / later / never / censored | 主回归分组来源 |
| T3 | v70 产品级验证表：11/203、8/160、10 个严格 D1 firm-date | 证明产品级严检过小，只作验证 |
| T4 | v72 H2 pooled interaction，later vs never | 否定性审计，不再是论文核心 |
| T5 | focal CAR 与 peer-minus-focal 诊断 | 解释竞争效应是否来自 focal 自身好消息 |
| T6 | 选择问题防线：controls、within-firm、entropy balance、pre-trend | 回应 verified firm 选择性 |
| T7 | specificity -> later verified 预测 | 若继续做，只能解释“披露文本是否预测备案”，不再支撑主 CAR |
| T8 | 场所选择/安静行动：备案产品是否正式披露、例行提及、未披露 | 利用 457 产品全库 |
| T9 | 非上市 confound calendar 与赛道竞争密度异质性 | 污染控制和机制 |
| Appendix A | v71 定向巨潮检索计划与 pilot 0 命中 | 说明已尝试补样本 |
| Appendix B | v65/S2 备案公示日诊断，修正 calendar-date 聚类和 peer 自事件剔除 | 不作为主因果表 |

---

## 6. 接下来一一执行

### v72：H2 主回归（已完成）

输入：

```text
v68/v70 event labels
v6 frozen event-peer panel
firm_admin_timing
```

输出：

```text
results/v72_registry_h2_pooled_interaction_20260612/
docs/empirical_runs/132_v72_registry_h2_pooled_interaction_20260612.md
```

已包含：

- A_first_firm 与 A_all；
- later vs never；
- event FE + peer industry-week FE；
- event × peer firm 双向聚类；
- Wald 检验；
- 排除 censored / ambiguous；
- 加入 product-level matched indicator 的审计列。

结果：不支持 H2。后续不再沿 registry timing 主表继续追加复杂稳健性。

### v73：产品级验证附表

输入：

```text
v70 product-level labels
strict_product_d1_firm_dates.csv
```

输出：

- 产品级 matched vs unmatched 的描述表；
- 10 个严格 D1 firm-date 案例表；
- old A pool 内 4 个同日命中案例说明。

注意：不报告会被误读为主结果的显著性星号。

### v74：场所选择/安静行动

输入：

```text
v69 registry_product_traceback_best.csv
v71 targeted_cninfo_product_plan.csv
```

分类：

```text
event_ready_formal_d1
routine_formal_mention_only
interactive_only
no_local_traceback
```

问题：

```text
完成备案/登记的上市公司产品，为什么多数没有作为正式 GenAI 事件披露？
```

这张表可以解释 POM 为什么样本看起来大：它研究的是“上市公司公告说了什么”，不是“市场上有多少备案模型”。

### v75：修正 v65/S2 诊断

必须修：

1. 按 calendar date 聚类或 calendar-time portfolio；
2. 剔除 peer 自身同日备案/公示/公告事件；
3. 把 S2 明确写成“备案公示日诊断”，不进入主因果链。

### v76：confound calendar 与 competition density

非上市模型只做两件事：

1. 重大产品发布日进入污染日历；
2. 用全量备案库计算 focal 产品进入赛道的事前竞争密度。

---

## 7. 判别标准

原 H2 主线成立的最低条件：

1. v72 中 `LaterVerified × PeerExposure` 为负；
2. later vs never 的 Wald 差异至少在 A_first_firm 或 A_all 中 p < 0.10；
3. never 组本身不稳定显著为负；
4. focal CAR 不能完全解释 peer 负反应；
5. 排除非上市重大发布污染日后方向不变；
6. product-level matched 子样本方向不反向，哪怕无功效。

若只满足 1--2，不满足 3--6：

```text
降为 suggestive evidence，不写强因果。
```

v72 已经不成立，因此执行：

```text
不继续硬救 registry timing 主线。
回到 GenAI announcement 本身的产品市场竞争效应；
备案/登记只作为外部验证、场所选择、安静行动、披露错配和样本审计层。
```

---

## 8. 当前文件定位

关键结果文件：

```text
results/v69_registry_product_traceback_20260612/
results/v70_product_level_registry_labels_20260612/
results/v71_targeted_cninfo_search_plan_20260612/
```

关键文档：

```text
docs/empirical_runs/129_v69_registry_product_traceback_20260612.md
docs/empirical_runs/130_v70_product_level_registry_labels_20260612.md
docs/empirical_runs/131_v71_targeted_cninfo_search_plan_20260612.md
docs/empirical_runs/132_v72_registry_h2_pooled_interaction_20260612.md
```

本文件是 2026-06-12 晚上 v70--v72 之后的执行版。v2 保留为事前设计，不再作为当前执行口径。
