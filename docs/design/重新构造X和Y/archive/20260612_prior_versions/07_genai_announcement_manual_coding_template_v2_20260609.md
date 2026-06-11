# GenAI 公告人工编码模板 v2.1（20260609）

用途：配合 `06_genai_announcement_taxonomy_experiment_design_v2_20260609.md`。v2.1 只保留清洗层、POM product/process 对照层和一个粗辅助标签。清洗层决定主样本；POM 方向只做对照诊断；粗实施形态不阻塞、不做 kappa、不决定样本进入。

## 每条公告填写字段

```text
人工码：
GenAI有效性（yes/no/uncertain）：
文件类型（direct_event/backfill_needed/duplicate_progress/not_event）：
事件日可用（yes/no/uncertain）：
最终事件日：
是否首次：
POM方向（product/process/both/unclear/na）：
粗实施形态（可选；own_launch_or_deploy/relational_access/resource_commitment/internal_process/noise_or_backfill）：
证据短句：
备注：
```

## 编码优先级

先判断能不能进主样本：

```text
GenAI有效性 = yes
文件类型 = direct_event
事件日可用 = yes
是否首次 = yes
```

再判断 POM 方向。最后才填粗实施形态。

如果 POM 方向犹豫，不要为了形成 product/process 二分而硬分；优先写 `unclear`，在备注里说明为什么无法判断。

编码约 100 条后先暂停，输出一次频数表：

```text
GenAI有效性
文件类型
事件日可用
POM方向
direct_event 中 product/process/both/unclear 的事件数
```

如果 product/process 极度偏斜，或 process 格子太小，POM 对照提前降级为描述性，不再为它额外消耗人工时间。

## GenAI 有效性

`yes` 必须同时满足：

1. 明确 GenAI 证据：生成式 AI、AIGC、大模型、大语言模型、ChatGPT、GPT、DeepSeek、讯飞星火、文心一言、通义、智谱、Kimi 等；
2. 明确公司行动：发布、上线、备案、部署、接入、签署合作、投资、建设、收购、合同、中标等；
3. 行动方是上市公司或受控子公司。

`no`：

- 只有人工智能、智能化、大数据、云中心、算法模型；
- 模型其实是估值模型、财务模型、工程模型、建筑信息模型；
- 只有行业趋势、关注、探索、风险提示、否认；
- 行动方不是上市公司或受控子公司。

`uncertain`：

- 有 GenAI 词，但行动内容、行动方或事件日不清楚。

## 文件类型

- `direct_event`：公告本身就是事件披露，公告日可作为候选事件日。
- `backfill_needed`：是真 GenAI 行动，但公告日是年报、募投、可研、会议材料、总结材料，需找更早首次日期。
- `duplicate_progress`：重复披露、进展公告、补充公告，不作为首次事件。
- `not_event`：不是有效 GenAI initiative。

## POM 方向

- `product`：面向客户/市场的产品、模型、平台、服务、新功能、解决方案、模型备案、产品发布或商业化。
- `process`：内部办公、客服、营销、研发、生产、风控、流程自动化、运营效率、成本降低。
- `both`：同一公告明确包含 customer-facing 产品和内部流程应用。
- `unclear`：是真 GenAI initiative，但无法稳定判断 product/process。
- `na`：不是有效 GenAI initiative。

如果犹豫，不要硬分；先写 `unclear`，在备注里解释。

注意：横向竞争者场景中，`product` 和 `process` 都可能构成竞争威胁。`product` 是直接产品市场威胁；`process` 可能通过成本、效率、研发、营销或客服能力形成间接威胁。因此本字段不是为了证明 product 一定更负，而是为了和 POM/Qian 的供应商场景做可比对照。

## 粗实施形态

这个字段只是辅助，不是主解释变量；看 PDF 时顺手填即可。不能因为这个字段不确定而推迟清洗判断，也不要为了它回头重看大量 PDF。

- `own_launch_or_deploy`：公司自己发布、上线、备案、部署模型/产品/平台。
- `relational_access`：通过合作、投资、收购、联合研发等获得 GenAI 能力或生态接入。
- `resource_commitment`：智算中心、算力、训练/推理资源承诺，且明确服务大模型/AIGC/GenAI。
- `internal_process`：内部流程提效、办公/客服/营销/研发/生产/风控应用。
- `noise_or_backfill`：噪声、软披露、否认、重复、回填材料。

## 常见边界

### 智算中心/算力

算 `GenAI有效性=yes` 只在明确写：

- 大模型训练/推理；
- AIGC/生成式 AI 服务；
- 服务具体大模型公司或具体 GenAI 应用。

只写云中心、大数据中心、时空大数据、算力网络、算法模型，不算。

### 合作协议

合作协议不天然算 GenAI。必须看到：

- 联合研发大模型；
- 基于某大模型训练行业模型；
- 推出 GenAI 产品/解决方案；
- 接入或部署具体大模型能力。

只写探索人工智能应用、共建生态、数字化转型、智慧城市，不算或写 `uncertain`。

### 投资/收购

投资/收购不天然算 GenAI。标的或项目必须明确与 GenAI/大模型/算力服务相关。

## 证据短句

只摘一句最关键原文，不要长段复制。例：

```text
公司发布讯飞星火认知大模型，并同步发布商业应用成果。
双方将在生成式人工智能大模型在数字政务、企业服务等领域开展深度合作。
智算中心为 AIGC 大模型训练及推理提供算力支撑。
```

## 后续诊断

编码批次完成后，必须把 `POM方向` 与既有 `Specificity` 指标合并检查：

```text
Product_e 与 Specificity_e 的 event-level 相关系数
Product_e × AIActivePeer_p 与 Specificity_e × AIActivePeer_p 的回归样本相关性/VIF
```

如果相关性高，POM 方向只能作描述性对照，不能解释为独立于公告具体性的机制。
