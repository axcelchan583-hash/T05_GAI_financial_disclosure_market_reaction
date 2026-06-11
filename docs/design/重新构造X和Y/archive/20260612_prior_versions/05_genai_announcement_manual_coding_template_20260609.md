# GenAI 公告人工编码模板（20260609）

用途：人工看 PDF 时，每条公告按下面字段一次性编码。当前先作为讨论稿，确认后再进入 Obsidian 工作台。

## 每条公告填写字段

```text
人工码：
GenAI有效性（yes/no/uncertain）：
POM方向（product/process/both/unclear/na）：
实施模式（launch/cooperation/investment_acquisition/infrastructure/contract_order/internal_process/financing_backfill/soft_noise）：
文件类型（direct_event/backfill_needed/duplicate_progress/not_event）：
事件日可用（yes/no/uncertain）：
最终事件日：
是否首次：
证据短句：
备注：
```

## 最小判定规则

`GenAI有效性=yes` 必须同时满足：

1. 有明确 GenAI 证据：生成式 AI、AIGC、大模型、大语言模型、ChatGPT、GPT、DeepSeek、讯飞星火、文心一言、通义、智谱、Kimi 等；
2. 有具体行动：发布、上线、备案、部署、接入、签署合作、投资、建设、收购、合同、中标等；
3. 行动方是上市公司或其受控子公司。

仅有“人工智能、智能化、大数据、云中心、算法模型、建筑信息模型、估值模型”不够。

## POM 方向

- `product`：面向客户/市场的产品、模型、平台、服务、新功能、解决方案、模型备案、产品发布或商业化。
- `process`：内部流程、办公、客服、营销、研发、生产、风控、运营效率、成本降低、流程自动化。
- `both`：同一公告明确同时包含 customer-facing 产品和内部流程应用。
- `unclear`：是真 GenAI initiative，但无法判断产品还是流程。
- `na`：不是有效 GenAI initiative。

## 实施模式

- `launch`：发布/上线/备案模型、平台、产品、应用或解决方案。
- `cooperation`：战略合作、合作协议、联合研发、共建实验室、联合项目。
- `investment_acquisition`：投资、增资、收购、参股 AI/大模型/算力公司或项目。
- `infrastructure`：智算中心、算力中心、训练/推理基础设施；必须明确服务大模型/AIGC/GenAI。
- `contract_order`：客户合同、中标、采购、服务订单，且直接与 GenAI/大模型/算力服务相关。
- `internal_process`：内部部署、办公/客服/营销/研发/生产/风控流程改造。
- `financing_backfill`：募投、融资预案、可研、年报等披露真项目，但公告日本身不是首次事件日。
- `soft_noise`：探索、关注、泛生态、行业趋势、否认、无收入、无具体行动。

## 文件类型

- `direct_event`：公告本身就是事件披露，日期可用。
- `backfill_needed`：是真事件，但公告日是年报、募投、可研、会议材料、进展公告，需要找更早日期。
- `duplicate_progress`：重复披露或进展公告，不作为首次事件。
- `not_event`：不是 GenAI initiative。
