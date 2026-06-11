# T05 GenAI 公告分类实验设计（给人工审核与外部模型讨论）

## 1. 核心想法

POM/Qian 的关键内容异质性是：GenAI 公告分为 `product-oriented` 和 `process-oriented`。它的发现是 product-oriented GenAI announcement 对供应商反应更强。

T05 不应只复刻这个二分。我们的创新可以是：在中国 A 股正式公告制度下，GenAI 披露不仅有 product/process orientation，还存在不同的 **implementation mode**。市场可能同时根据“公告内容类型”和“被重估对象的经济关系”定价。

一句话研究问题：

> 资本市场是否区分不同类型的 GenAI 披露，并对产品市场竞争者与投资型关联方作出不同方向的短窗口重估？

## 2. 人工编码目标

当前人工看 PDF 时，不只判断“是否保留为 GenAI 事件”，还要一次性编码：

1. 是否是真 GenAI initiative；
2. POM 式 product/process orientation；
3. 中国公告特有的 implementation mode；
4. 公告日是否可用作事件日；
5. 是否需要回填更早首次事件日；
6. 原文证据短句。

## 3. 编码字段

### 3.1 GenAI 有效性

`genai_validity`

- `yes`：明确出现生成式 AI / AIGC / 大模型 / 大语言模型 / ChatGPT / GPT / DeepSeek / 讯飞星火 / 文心一言 / 通义 / 智谱 / Kimi 等，并且公司或受控子公司有具体行动。
- `no`：只有人工智能、智能化、大数据、云中心、算法模型、建筑信息模型、估值模型等泛表述；或只是行业趋势、风险提示、否认。
- `uncertain`：有 GenAI 词，但行动方、行动内容或事件日不清楚。

硬规则：只有“人工智能”“算法模型”“智能平台”“云中心”不够。

### 3.2 POM 方向

`pom_orientation`

- `product`：面向客户/市场的产品、模型、平台、服务、新功能、解决方案、算法备案、产品发布或商业化。
- `process`：内部流程、办公、客服、营销、研发、生产、风控、运营效率、成本降低、流程自动化。
- `both`：同一公告明确同时包含客户-facing 产品和内部流程应用。
- `unclear`：无法判断产品还是流程。
- `na`：不是有效 GenAI initiative。

注意：战略合作、投资、智算中心本身不是 product/process。要看它服务的内容。如果合作是共同推出产品，偏 `product`；如果是内部提效系统，偏 `process`；如果只写共建生态或算力资源，先写 `unclear`。

### 3.3 Implementation Mode

`implementation_mode`

- `launch`：公司发布/上线/备案 GenAI 模型、平台、产品、应用或解决方案。
- `cooperation`：签署战略合作、合作协议、联合研发、共建实验室、联合项目。
- `investment_acquisition`：投资、增资、收购、参股 AI/大模型/算力公司或项目。
- `infrastructure`：智算中心、算力中心、数据中心、训练/推理基础设施；必须明确服务大模型/AIGC/GenAI。
- `contract_order`：客户合同、中标、采购、服务订单，且与 GenAI/大模型/算力服务直接相关。
- `internal_process`：内部部署、办公/客服/营销/研发/生产/风控流程改造。
- `financing_backfill`：募投、融资预案、可研报告、年报等披露了真项目，但公告日本身不是首次事件日。
- `soft_noise`：探索、关注、泛生态、行业趋势、否认、无收入、无具体行动。

### 3.4 文件/事件日类型

`source_event_type`

- `direct_event`：公告本身就是事件披露，日期可用。
- `backfill_needed`：是真事件，但公告日是年报、募投、可研、会议材料、进展公告，需要找更早日期。
- `duplicate_progress`：重复披露或进展公告，不作为首次事件。
- `not_event`：不是 GenAI initiative。

`event_date_usable`

- `yes`
- `no`
- `uncertain`

### 3.5 证据字段

`evidence_short`

只摘一句最关键原文，避免长段复制。例如：

- “公司发布讯飞星火认知大模型，并同步发布商业应用成果。”
- “双方将在生成式人工智能大模型在数字政务、企业服务等领域开展深度合作。”
- “智算中心为 AIGC 大模型训练及推理提供算力支撑。”

## 4. 关键判别规则

### 4.1 算力/智算中心

算，只在满足下列条件之一时：

- 明确写“大模型训练/推理”；
- 明确写“AIGC/生成式 AI 服务”；
- 明确服务具体大模型公司或具体 GenAI 应用。

不算：

- 只写云中心、大数据中心、时空大数据、算力网络、算法模型、数据链。

### 4.2 合作协议

算，只在协议内容明确含 GenAI 行动时：

- 联合研发大模型；
- 基于某大模型训练行业模型；
- 推出 GenAI 产品/解决方案；
- 接入或部署具体大模型能力。

不算：

- 只写“探索人工智能应用”“共建生态”“数字化转型”“智慧城市”。

### 4.3 投资/收购

算，只在投资标的或项目明确与 GenAI/大模型/算力服务相关时。

不算：

- 普通收购、普通项目、普通产业园；
- 只因全文里出现“模型”但其实是估值模型、财务模型、工程模型。

## 5. 预期假设

H1：有效 GenAI initiative 披露后，产品市场竞争者出现负向短窗口重估。

H2：竞争者负反应在 `product` orientation 和 `launch` mode 下更强，因为它们更像直接产品市场威胁。

H3：`process` orientation 对竞争者的负反应较弱，因为它更像内部效率提升，不直接改变产品市场竞争。

H4：`cooperation`、`investment_acquisition` 和 `infrastructure` mode 更可能使投资型关联方获得正向重估，因为这些公告显示能力获取、资源承诺或关系嵌入。

H5：`soft_noise`、`not_event`、`duplicate_progress` 不应产生稳定的关系型重估，可作为安慰剂或剔除样本。

## 6. 实证设计

### 6.1 样本层

主样本：

- 人工确认为 `genai_validity=yes`；
- `source_event_type=direct_event`；
- 每公司保留首次有效 GenAI event。

回填样本：

- `source_event_type=backfill_needed`；
- 不直接用当前公告日；
- 用于寻找更早首次事件日。

安慰剂/排除样本：

- `genai_validity=no`；
- `soft_noise`；
- `duplicate_progress`。

### 6.2 被重估对象

至少保留两类：

1. product-market competitors：预期负反应；
2. FactSet investment-linked partners：预期正反应。

供应商/客户关系暂时只做边界或补充，不作为主结果承诺。

### 6.3 主要回归

事件层类型差异：

```text
MeanCompetitorCAR_e = β1 Product_e + β2 Process_e + β3 Cooperation_e
                    + β4 Investment_e + β5 Infrastructure_e
                    + controls + industry/date FE + ε_e
```

关系层 stacked regression：

```text
CAR_{e,j,r} = α_e
            + β1 InvestmentPartner_r
            + β2 Competitor_r
            + θ1 InvestmentPartner_r × Product_e
            + θ2 InvestmentPartner_r × Cooperation_e
            + θ3 InvestmentPartner_r × InvestmentAcquisition_e
            + θ4 Competitor_r × Product_e
            + θ5 Competitor_r × Process_e
            + controls + ε
```

机制层：

```text
CompetitorCAR_{e,p} = α_e
                    + β1 AIActivePeer_p
                    + β2 AIActivePeer_p × Product_e
                    + β3 AIActivePeer_p × Launch_e
                    + β4 AIActivePeer_p × Process_e
                    + peer controls + ε
```

解释：event FE 吸收公告本身的平均好坏消息，交互项看同一事件下不同 peer 暴露的差异。

## 7. 给网页版 Pro / Claude 的讨论 prompt

请审阅下面的研究设计。背景：POM/Qian 将 GenAI announcements 区分为 product-oriented vs process-oriented，并发现 product-oriented 对供应商正向溢出更强。我们使用中国 A 股 CNINFO 正式公告，正在人工核验 1,601 条三类公告 PDF：产品/模型/平台发布，签署合作协议，投资/建设/智算中心/项目。

我想在人工审核时同时编码：

1. `genai_validity`: yes/no/uncertain；
2. `pom_orientation`: product/process/both/unclear/na；
3. `implementation_mode`: launch/cooperation/investment_acquisition/infrastructure/contract_order/internal_process/financing_backfill/soft_noise；
4. `source_event_type`: direct_event/backfill_needed/duplicate_progress/not_event；
5. `event_date_usable`: yes/no/uncertain；
6. `evidence_short`: 原文短证据。

研究问题是：资本市场是否区分不同类型的 GenAI 披露，并对 product-market competitors 与 investment-linked partners 作出不同方向的短窗口重估？

请重点评价：

- 这个 taxonomy 是否能在 POM 的 product/process 二分上形成清晰创新？
- `implementation_mode` 是否和 `pom_orientation` 概念上正交，还是会混淆？
- 哪些类别应该合并或拆分？
- 哪些类别适合做主解释变量，哪些只能做样本清洗或回填标签？
- 这个人工编码方案是否足够可复现？
- 如果投稿到会计/金融/信息系统方向，最容易被质疑的识别和测量问题是什么？

请给出严格批判，不要为了鼓励而泛泛肯定。
