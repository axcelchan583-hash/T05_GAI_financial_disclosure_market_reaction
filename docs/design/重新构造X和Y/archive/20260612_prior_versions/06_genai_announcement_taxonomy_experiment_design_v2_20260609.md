# T05 GenAI 公告分类实验设计 v2.1（20260609）

## 1. v2.1 的核心调整

v1 的问题是把 `pom_orientation` 和 8 类 `implementation_mode` 同时推成主分类体系，容易过度工程化：

- `launch` 几乎天然偏 product，`internal_process` 天然偏 process，两个维度不正交；
- 8 类名义变量会导致人工一致性差、格子过稀；
- `launch/product` 可能只是已经显著的 `Specificity` 的粗糙替代；
- `investment-linked partners` 的正反应目前只来自小样本探索结果，不能支撑对称再分配主框架。

v2.1 因此改成：

1. **清洗层**：保留，作为最终 treatment 的必要条件；
2. **POM product/process**：保留，但只作为一个异质性切口；
3. **粗实施形态**：保留为辅助标签/稳健性，不作为主解释变量；
4. **主线回到 competitor negative + `Spec × AIActivePeer`**；
5. **investment-linked partner positive** 只作为探索性补充，不写成主假设；
6. **旧的 competitor-negative 结果全部标为 provisional**：人工清洗和 backfill 会改变事件样本和事件日，清洗完成后必须重跑；
7. **H3 只作 POM 对照诊断**：先检查 `Product_e` 与 `Specificity_e` 的相关性和样本分布，不能默认解释为独立机制。

## 2. 研究问题

主问题：

> 中国上市公司披露有效、可定位事件日的 GenAI initiative 后，资本市场是否对其产品市场竞争者作出负向短窗口重估？

机制问题：

> 这种负向重估是否集中在事前 AI-active 的近产品市场竞争者，并且是否随公告信息具体性增强？

POM 对照问题：

> POM/Qian 发现 product-oriented GenAI 公告对纵向供应商正向溢出更强；在横向竞争者场景中，product-oriented 与 process-oriented 披露是否对应不同类型的竞争威胁？

这里不预设 product 一定比 process 更强。产品/平台/模型发布是直接产品市场威胁；但内部流程、研发、营销、客服、生产效率提升也可能降低成本、改善响应速度或增强价格竞争能力。因此 POM 的 product/process 切分在本项目中首先是对照和诊断，不是主识别来源。

## 3. 编码体系

### 3.1 清洗层：主样本必要条件

这些字段用于确定最终事件样本，不是理论异质性：

`genai_validity`

- `yes`：明确 GenAI 证据 + 公司或受控子公司具体行动；
- `no`：泛 AI、行业趋势、否认、非公司行动、非 GenAI 模型；
- `uncertain`：需要二次核验。

`source_event_type`

- `direct_event`：公告本身就是可用事件；
- `backfill_needed`：是真事件，但公告日不是首次事件日；
- `duplicate_progress`：重复披露或进展；
- `not_event`：不是有效 GenAI initiative。

`event_date_usable`

- `yes`
- `no`
- `uncertain`

最终主样本只使用：

```text
genai_validity = yes
source_event_type = direct_event
event_date_usable = yes
每公司首次有效 GenAI event
```

### 3.2 POM orientation：保留为一个异质性切口

`pom_orientation`

- `product`：面向客户/市场的产品、模型、平台、服务、新功能、解决方案、模型备案、产品发布或商业化；
- `process`：内部办公、客服、营销、研发、生产、风控、流程自动化、运营效率、成本降低；
- `both`：同一公告明确包含 customer-facing 产品和内部流程应用；
- `unclear`：有效 GenAI initiative，但无法稳定判断 product/process；
- `na`：非有效 GenAI initiative。

用法：

- 不作为主 X；
- 只做与 POM 对照的异质性检验；
- 样本量不足时可合并为 `product` vs `non_product`。
- 编码约 100 条后先看频数表；如果 `product/process` 极度偏斜或 `process` 格子太小，H3 提前降级为描述性结果。

### 3.3 粗实施形态：辅助标签，不进 headline

`coarse_mode`

- `own_launch_or_deploy`：自己发布、上线、备案、部署模型/产品/平台；
- `relational_access`：通过合作、投资、收购、联合研发等取得 GenAI 能力或生态接入；
- `resource_commitment`：智算中心、算力、训练/推理资源承诺，且明确服务大模型/AIGC/GenAI；
- `internal_process`：内部流程提效、办公/客服/营销/研发/生产/风控应用；
- `noise_or_backfill`：噪声、软披露、否认、重复、回填材料。

用法：

- 辅助人工理解公告；
- 检查 `pom_orientation` 是否被公告形态 mechanically driven；
- 最多做 robustness 或 appendix；
- 不写成主贡献和主假设。
- 不作为人工一致性 gate，不要求 kappa，不用于决定事件是否进入主样本。

## 4. 假设体系

### H1：竞争者负向重估

有效 GenAI direct event 后，焦点公司的 product-market competitors 在短窗口内出现负向 abnormal return。

这是主结果，不依赖 product/process 分类。

### H2：AI-active peer 机制

竞争者负反应在事前 AI-active peers 中更强，尤其当焦点公告更具体时：

```text
PeerCAR_{e,p} = α_e
              + β1 AIActivePeer_p
              + β2 Specificity_e × AIActivePeer_p
              + peer controls
              + ε_{e,p}
```

这里 `Specificity` 仍是主机制变量。分类变量不能替代它。

### H3：POM product/process 对照异质性

在横向竞争者场景中，POM 的 product/process 切分可能帮助区分两类威胁：

- `product`：新产品、平台、模型、解决方案或商业化能力直接进入产品市场；
- `process`：内部效率、研发、营销、客服、生产或风控能力提升，可能通过成本下降、响应速度提升或价格竞争能力增强影响竞争者。

因此 H3 不写成“product 必然更负”。更保守的表述是：product/process 是一个与 POM 对话的异质性切口，用于观察竞争者负反应来自直接产品市场威胁，还是也包含内部能力提升带来的间接竞争压力。

保守写法：

```text
PeerCAR_{e,p} = α_e
              + β1 AIActivePeer_p
              + β2 Product_e × AIActivePeer_p
              + β3 Specificity_e × AIActivePeer_p
              + controls
              + ε_{e,p}
```

解释边界：

- 若 `Product × AIActivePeer` 显著，说明 POM 的 product/process 切分在横向竞争场景有额外描述性信息；
- 若不显著，不影响主线，因为主线是 competitor negative 和 `Spec × AIActivePeer`。
- 若 `Product_e` 与 `Specificity_e` 高度相关，则不能把 `Product × AIActivePeer` 解释为独立于公告具体性的机制。

### 探索性补充：investment-linked partners

FactSet investment-linked partners 的正反应只作为探索性补充：

- 不写成 H4；
- 不支持“所有合作方正向”；
- 不支持对称 rent redistribution；
- 只写成：初步证据显示，投资型关系可能与一般合作/经营关系不同，需要更严格关系方向审计。

## 5. 实证设计

### 5.1 事件样本

人工审核后得到：

```text
ValidDirectEvents = genai_validity=yes
                  & source_event_type=direct_event
                  & event_date_usable=yes
                  & first_valid_event_by_firm
```

`backfill_needed` 样本不直接进事件研究，只用于寻找更早首次事件。

### 5.2 主结果：competitor CAR

```text
CompetitorCAR_{e,p,[0,+1]} = α
                            + β ValidGenAIEvent_e
                            + controls
                            + ε
```

实际估计仍按现有 product-market competitor event-study 样本执行，重点报告 CAR `[0,+1]`。

### 5.3 机制：event FE 下的 peer-level heterogeneity

```text
PeerCAR_{e,p,[0,+1]} = α_e
                      + β1 Specificity_e × AIActivePeer_p
                      + β2 AIActivePeer_p
                      + PeerControls_p
                      + ε_{e,p}
```

关键解释：

- `α_e` 吸收焦点公告平均好坏消息；
- 识别来自同一事件内 AI-active 与 non-AI-active peers 的差异；
- 已知 peer FE 下会弱化或消失，因此不能过度声称 within-peer 强识别。

### 5.4 POM 对照异质性

进入回归前先做两个诊断：

1. 在 event 层计算 `Product_e` 与 `Specificity_e` 的相关系数；
2. 在 peer-event 回归样本中检查 `Product_e × AIActivePeer_p` 与 `Specificity_e × AIActivePeer_p` 的相关性/VIF。

判定规则：

- 若 `|corr(Product, Specificity)| > 0.5`，或交互项明显共线，则 H3 只作描述性对照，不声称 product/process 有独立机制含义；
- 若 `product/process` 分布严重偏斜，例如 process 有效事件少于约 30 个，H3 不进入主表；
- 不论诊断结果如何，H3 都不能替代 H2 的 `Specificity × AIActivePeer`。

```text
PeerCAR_{e,p,[0,+1]} = α_e
                      + β1 AIActivePeer_p
                      + β2 Product_e × AIActivePeer_p
                      + β3 Specificity_e × AIActivePeer_p
                      + controls
                      + ε_{e,p}
```

报告顺序：

1. `Product × AIActivePeer` 单独版本；
2. `Specificity × AIActivePeer` 单独版本；
3. 两者同时放入版本。

若 1 显著、3 不稳定，解释为 product 切分可能吸收了公告具体性，不作强结论。

如果事件数不足：

```text
Product_e = 1 if pom_orientation in {product, both}
NonProduct_e = process / unclear
```

不做 product/process × coarse_mode 的多格交互。

### 5.5 粗实施形态 robustness

只做三件事：

1. 检查主结果是否被 `own_launch_or_deploy` 单类驱动；
2. 检查剔除 `noise_or_backfill` 后结果是否稳定；
3. 描述性报告各类样本量，不做主表强解释。

### 5.6 清洗后必须重跑既有结果

当前已经跑出的 competitor-negative CAR 和 `Spec × AIActivePeer` 结果来自未经完整人工核验的旧事件口径。v2.1 编码会改变两件事：

1. 一部分旧事件会被剔除为 `no`、`not_event`、`duplicate_progress` 或 `backfill_needed`；
2. `backfill_needed` 事件需要回填更早首次事件日，CAR 窗口会整体平移。

因此旧的 v44/v45/v46 结果只能作为研究设计线索。人工清洗完成后，必须用新的 `ValidDirectEvents` 和回填后的首次事件日重跑：

- competitor CAR `[0,+1]`；
- `Spec × AIActivePeer` event FE 机制；
- peer-characteristic guard；
- POM product/process 对照；
- investment-linked partner 探索性结果。

论文中不能把旧日期结果写成最终估计。

### 5.7 编码早期停点

不要等 1,601 条全部看完才判断设计是否可行。编码到约 100 条有效候选后，先输出：

1. `genai_validity` 频数；
2. `source_event_type` 频数；
3. `event_date_usable` 频数；
4. `pom_orientation` 频数；
5. `Product_e` 与 `Specificity_e` 的相关系数；
6. direct-event 里 product/process/both/unclear 的事件数。

如果此时发现：

- direct event 保留率很低；
- product/process 极度偏斜；
- `Product_e` 与 `Specificity_e` 高度相关；
- backfill 占比很高；

则立即调整：H3 降级或删除，优先保证清洗层和 H1/H2。

### 5.8 `AIActivePeer` 的 peer-characteristic guard

`AIActivePeer` 可能同时代表“大型科技 peer”“高研发 peer”或“高波动 peer”。因此清洗后重跑 H2 时，至少保留一组 guard：

```text
Spec_e × AIActivePeer_p
Spec_e × Size_p
Spec_e × Beta_p
Spec_e × Volatility_p
Spec_e × MB_p
```

如果可取得更好的技术密度变量，也应加入 `Spec_e × TechDensity_p` 或同类指标。解释时要说清楚：event FE 下识别的是同一公告内不同 peer 的相对反应，peer FE 下会弱化或消失，说明主要证据来自 peer 技术空间/特征差异，而不是同一 peer 的强 within 变化。

## 6. 人工一致性要求

优先保证这些字段的一致性：

1. `genai_validity`
2. `source_event_type`
3. `event_date_usable`
4. `pom_orientation`

`coarse_mode` 是辅助字段，一致性要求低于前三者，不作为 gate。

若做双人编码：

- `genai_validity` kappa ≥ 0.70；
- `source_event_type` kappa ≥ 0.70；
- `pom_orientation` 若 kappa < 0.70，则只保留 `product` vs `non_product`。

## 7. 给网页版 Pro / Claude 的 v2.1 prompt

请审阅这个 v2.1 研究设计。背景：POM/Qian 将 GenAI announcements 区分为 product-oriented vs process-oriented，并发现 product-oriented 对供应商正向溢出更强。我们研究中国 A 股 CNINFO 正式公告，目标不是复刻供应商正向溢出，而是研究 GenAI 披露后 product-market competitors 的负向短窗口重估，以及 `Specificity × AIActivePeer` 机制。

v2.1 编码方案：

1. 清洗层：
   - `genai_validity`: yes/no/uncertain
   - `source_event_type`: direct_event/backfill_needed/duplicate_progress/not_event
   - `event_date_usable`: yes/no/uncertain
2. POM 对照层：
   - `pom_orientation`: product/process/both/unclear/na
3. 辅助层：
   - `coarse_mode`: own_launch_or_deploy / relational_access / resource_commitment / internal_process / noise_or_backfill

主样本只取 `genai_validity=yes & source_event_type=direct_event & event_date_usable=yes & first_valid_event_by_firm`。

主线假设：

- H1：有效 GenAI direct event 后，product-market competitors 短窗口 CAR 为负。
- H2：负反应在 `Specificity × AIActivePeer` 下更强。
- H3：POM 的 product/process 只作为异质性切口，检验 product-oriented 与 process-oriented 是否对应不同类型的横向竞争威胁；不预设 product 一定更负。

关键约束：

- 当前旧 competitor-negative 结果来自未完全人工核验事件口径，只能作为 provisional；清洗和 backfill 后必须重跑；
- `Product_e` 可能与 `Specificity_e` 高度相关，编码后先做相关性/VIF诊断；
- 编码约 100 条后先看 `pom_orientation` 频数，如果 product/process 极度偏斜，H3 降级为描述性；
- `coarse_mode` 非阻塞、无 kappa、无 gate，只做 robustness/appendix；
- `AIActivePeer` 需要用 peer characteristics interaction guard 排除“大型科技 peer”解释。

`coarse_mode` 不作为主解释变量，只做 robustness/appendix。FactSet investment-linked partner positive 只作为探索性补充，不写成主假设。

请严格评价：

- H3 是否已经足够保守，避免把 product/process 误写成独立机制？
- `Product_e` 与 `Specificity_e` 的共线诊断和报告顺序是否充分？
- 清洗后重跑旧 v44/v45/v46 的流程是否覆盖了事件日变化风险？
- `AIActivePeer × peer characteristics` guard 是否足以回应“大型科技 peer”质疑？
- `coarse_mode` 作为非阻塞 appendix/robustness 是否仍会带来不必要负担？
- reviewer 最可能继续质疑什么？
