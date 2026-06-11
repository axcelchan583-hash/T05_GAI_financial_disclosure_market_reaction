# T05 当前研究问题与样本审计备忘录

日期：2026-06-09

## 当前结论

这条线可以继续写，但现在应收紧为：

```text
具体 GenAI initiative 披露后，资本市场是否沿既有经济关系重新分配预期价值：
产品市场竞争者被负向重估，投资关联方被正向重估。
```

暂时不要写成“泛合作伙伴正反应”。目前支持正反应的是 FactSet `PARTNER-INVESTO` / `PARTNER-EINVEST` 投资型关系，不是经营合作、供应商、客户或全部 partner。

最大的风险不在理论包装，而在两件事：

1. X 事件日期和事件资格是否已经从 11 万公告和互动平台线索中正确选出。
2. FactSet investment-linked partner 的关系方向、语义和中国案例映射是否人工核准。

## 现有证据

### 1. Product-market competitor 负反应

当前最干净的主结果候选仍是 competitor 短窗负反应。

- v29/v44 product-market competitor:
  - Day 0 AR = `-0.0025`, p = `0.0205`;
  - Day +1 AR = `-0.0021`, p = `0.0541`;
  - CAR[0,+1] = `-0.0047`, p = `0.0045`;
  - sample = 2,789/2,790 event-peer rows, 316 usable events.
- FactSet competitor validation:
  - CAR[0,+1] mean = `-0.008111`, p = `0.010718`;
  - event-weighted mean = `-0.009223`, p = `0.000491`.
- Pollution checks:
  - removing peer own GenAI events, major announcements, or any peer announcements keeps CAR[0,+1] negative.

写法：这是短窗资本市场 revaluation，不是已证明真实 business stealing。

### 2. `Spec x AIActivePeer` 机制

当前机制证据支持“同一事件内 AI-active / 技术相关 peer 的相对负向重估”，但不支持强 within-peer 因果叙事。

- v31:
  - `Spec x AIActivePeer` on PeerAR[0] = `-0.001806`, p = `0.0224`;
  - `Spec x AIActivePeer` on PeerCAR[0,+1] = `-0.003194`, p = `0.0080`.
- v36 firm-characteristic guard:
  - 加 peer size、beta、volatility、MB 主效应和 `Spec x` firm-style interactions 后，
  - `Spec x AIActivePeer` 约 `-0.0025`, p = `0.0334`.
- v45 peer-FE diagnostic:
  - event FE 规格显著；
  - event + peer-firm FE 变为 `-0.0010`, p = `0.5759`;
  - singleton peer firms 占 `59.68%`，peer FE 问的是更窄的 within-peer 问题。
- v46:
  - `Spec` 本身是 event-level，在 event FE 下被吸收；
  - 不应写 AIActive-only event-FE 子样本中的 specificity 主效应。

写法：机制是 `Spec x AIActivePeer` 的 within-event heterogeneity，不是 specificity 本身的独立 event-FE 效应。

### 3. Investment-linked partner 正反应

这是有希望的第二发现，但还不能写成 final main evidence。

- v43 grouped FactSet:
  - `factset_partner_investment` CAR[0,+1] relationship-level mean = `0.006571`, p = `0.148184`;
  - event-weighted mean = `0.008396`, p = `0.037833`;
  - stacked event-FE vs product-market competitor: `+0.0103`, p = `0.002856`.
- v47 investment audit:
  - clean rows = `86`, events = `54`, related firms = `83`;
  - `investor_in_focal` 与 `investee_of_focal` 的 relationship-level mean 都为正；
  - leave-one-event-out 均保持正均值。

风险：高贡献事件中有年报、利润分配、提质增效、重整投资、投资者信等标题。必须确认这些是真正 GenAI initiative 事件日，或回填到更早更合适的事件日。

## 研究问题判断

### 可以写的版本

```text
When a listed firm discloses a concrete GenAI initiative, do capital markets
reallocate value across pre-existing economic relationships?
```

中文组会版：

```text
上市公司披露具体 GenAI 行动后，市场是否把这条信号理解为
对产品市场竞争者的威胁，同时也理解为对投资关联方的价值确认？
```

这个问题有现实必要性，因为 GenAI 披露高度无形、真假难辨、能力边界不透明。市场不能直接观察真实能力，只能通过公告内容和既有经济关系推断谁受威胁、谁受益。

### 暂时不能写的版本

- 不能写“合作伙伴显著正反应”。
- 不能写“供应商/客户受益”。
- 不能写“经营协作关系被市场正向确认”。
- 不能写“Specificity 证明企业真实 GenAI 能力”。
- 不能写成 DID、IV 或强因果。

### 模型准确性

当前最准确的模型是短窗关系依赖型信息传递：

```text
GenAI initiative disclosure
-> market inference about focal firm's future AI/product capability
-> negative revaluation of close product-market competitors
-> positive or less negative revaluation of investment-linked partners
```

其中 competitor 通道相对扎实；investment-linked partner 通道需要重新命名为投资关联、股权关联或战略投资网络，不应和 operating collaborator 混在一起。

## 样本选择审计清单

### A. Formal announcement X

1. 不再把旧 1,055/1,066 当最终 treatment。
2. 先完成 v55 的 750 行人工表：
   - A1 direct-event confirm: 484 行；
   - A2 backfill date recovery: 83 行；
   - A4 earlier suspicious disclosures: 141 行；
   - B1 low priority frame: 41 行；
   - A3 old-pool unresolved: 1 行。
3. 人工码使用 v55 codebook：
   - `1` = 保留为直接事件；
   - `2` = 保留但需回填/修正事件日；
   - `3/4` = 剔除；
   - `5` = 不确定二审。
4. 每个保留事件必须记录：
   - final event date；
   - source_primary / source_support / source_layer；
   - event_date_source；
   - 原文证据；
   - 是否公司自身具体 GenAI 行动；
   - 是否 first event per firm。
5. 对年报、ESG、融资文件、提质增效、利润分配、投资者信、会议材料：
   - 原则上不能直接作为事件日；
   - 若含真 initiative，标记为 backfill/support，回溯更早公告、互动回复、公司新闻或证券媒体来源。

### B. 11 万公告漏斗

v52 已说明旧 1,055 池不完整：

- 旧 1,055 外的 2,000 行 LLM leakage sample 中：
  - direct rows = 71；
  - backfill rows = 654；
  - keep-any rows = 725。
- 权重估计：
  - weighted direct leakage 约 `461.9`；
  - weighted keep-any leakage 约 `8,677.6`。

解释：真正干净的 direct leakage 没有到不可控，但 backfill/support 线索很多。下一步不是人工读完 11 万，而是用分层规则把 direct candidates 和 high-confidence backfill candidates 变成可审计队列。

### C. 互动平台 B 组

v50 的 CSMAR investor-interaction 数据是 2,460,811 行原始互动，2023-2026 reply-date 口径下有：

- expanded IIP firm-day candidates = 17,275；
- first expanded IIP candidate per firm = 2,742；
- priority firm reply action candidate = 25,028 answer-level rows。

互动平台不应默认并入 formal announcement treatment。更安全的用途是：

1. 支持 formal announcement 的 claim evidence；
2. 为年报/ESG/融资文件中的 backfill_needed 行回溯更早日期；
3. 单独做 B-source robustness 或 adoption-timeline sample；
4. 只有当公司回复本身是首个公开、公司署名、具体 GenAI 行动，并且 timing 可解释时，才进入直接事件候选。

### D. Relationship audit

1. 对 v47 的 54 个 investment-linked events 做事件层人工核验。
2. 对高绝对贡献事件优先核验 X 是否合格，包括：
   - 中文在线、九州通、盛通股份、佳都科技、国脉文化、远光软件、用友网络、宝信软件、电广传媒、鸿泉物联等。
3. 对每条 FactSet investment relation 核验：
   - `PARTNER-EINVEST` / `PARTNER-INVESTO` 的 source-target 方向；
   - 是否相对 focal firm 正确翻译为 investor_in_focal 或 investee_of_focal；
   - relation_start 是否早于 event；
   - relation_end 是否过期或异常；
   - 是否实际为集团、子公司、上市主体错配；
   - 是否同时是 competitor/supplier/customer。
4. 关系标签最终只写 investment-linked partners，除非人工证据能证明 operating collaboration。

## 下一步顺序

1. 完成 v55 batch1 人工编码，先不重写理论。
2. 生成 human-validated final X table，并重建 first-event-per-firm。
3. 用 final X 重跑：
   - product-market competitor event study；
   - `Spec x AIActivePeer` mechanism；
   - FactSet grouped relationship event study；
   - v47 investment-linked audit。
4. 对重跑后仍显著的 investment-linked cases 做 FactSet 人工关系核验。
5. 只有当 competitor 负反应和 investment-linked 正反应在 final X 下都保留，再进入论文故事包装。
