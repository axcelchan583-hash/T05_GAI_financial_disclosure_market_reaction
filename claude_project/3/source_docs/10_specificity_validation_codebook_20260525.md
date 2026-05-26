# Specificity Validation Codebook

Date: 2026-05-25

Purpose: validate that `Specificity_z` measures concrete GenAI disclosure specificity rather than length, generic AI buzzwords, or noise.

## Coding Unit

One focal GenAI disclosure event:

```text
firm i × event date t
```

Coders should read:

1. `sample_question`
2. `sample_answer`
3. `sources`
4. `company_name`
5. `event_date`

The coding target is the GenAI-related content in the answer/disclosure, not the investor's question alone.

## Core Concept

Specificity means the disclosure contains concrete, verifiable, implementation-oriented details about GenAI / large-model / AIGC activity.

High specificity:

```text
names a product, model, use case, customer, partner, deployment status, timeline, or quantitative commitment.
```

Low specificity:

```text
only says the company is paying attention, exploring, researching, empowering, actively laying out, or following industry trends.
```

## Component Coding

Each component is binary:

```text
1 = clearly present
0 = absent
9 = unclear / cannot determine
```

Use `9` sparingly. If a detail is vague but still interpretable, code the closest binary judgment and explain in `coder_notes`.

### C1. Specific Product / Service

Variable:

```text
has_specific_product_service
```

Code `1` if the disclosure names or clearly identifies a concrete product, service, platform, application, software, system, module, model product, digital assistant, chatbot, or solution.

Examples that usually count:

```text
公司已推出 XX 智能客服系统。
公司正在将大模型接入 XX 平台。
公司的 XX 产品已使用 AIGC 功能。
```

Examples that do not count:

```text
公司持续关注人工智能发展。
公司积极探索相关技术。
```

### C2. Named Model / Platform

Variable:

```text
has_model_platform_name
```

Code `1` if the disclosure names a model, foundation-model platform, GenAI platform, or identifiable AI technical platform.

Examples:

```text
ChatGPT, GPT, DeepSeek, 通义千问, 文心一言, Kimi, 智谱, 星火, 盘古, 混元, 自研大模型, XX大模型平台。
```

Generic "大模型技术" without a named model/platform is normally `0`.

### C3. Specific Use Case

Variable:

```text
has_specific_use_case
```

Code `1` if the disclosure identifies a concrete application scenario or business function.

Examples:

```text
智能客服、营销文案生成、医疗辅助诊断、教育批改、智能座舱、代码生成、风控、质检、投研问答、搜索推荐、办公助手。
```

Generic "赋能业务" or "提升效率" without a concrete function is `0`.

### C4. Customer / Industry Segment

Variable:

```text
has_customer_or_industry
```

Code `1` if the disclosure identifies a customer type, client, user group, downstream industry, business segment, or deployment sector.

Examples:

```text
银行客户、医院、教育行业、汽车主机厂、政务场景、B端客户、C端用户、制造业客户。
```

Generic "市场需求" without a target segment is `0`.

### C5. Partner / External Organization

Variable:

```text
has_partner_or_org
```

Code `1` if the disclosure names a partner, supplier, customer, research institution, university, regulator, platform company, or external organization.

Examples:

```text
与华为合作、接入百度文心、与某银行联合试点、与 XX 大学共建实验室。
```

The company itself does not count as an external partner unless the statement names a subsidiary, joint venture, lab, or platform as a distinct organization.

### C6. Deployment / Implementation Status

Variable:

```text
has_deployment_status
```

Code `1` if the disclosure states a concrete stage of implementation.

Examples:

```text
已上线、已发布、已备案、已部署、已接入、已落地、正在内测、正在试点、已完成训练、已商业化、已签约。
```

Generic future-oriented wording such as "计划探索" or "未来将布局" is `0` unless paired with a concrete stage.

### C7. Commercialization / Timeline

Variable:

```text
has_commercialization_or_timeline
```

Code `1` if the disclosure states a commercialization path, revenue implication, customer rollout, launch timeline, deadline, project period, or planned milestone.

Examples:

```text
预计 2024 年上线。
将在下半年推出。
已形成收入。
已签订订单。
将面向客户推广收费版本。
```

Generic "未来商业空间广阔" is `0`.

### C8. Quantitative Commitment / Numeric Detail

Variable:

```text
has_quantitative_commitment
```

Code `1` if the disclosure gives numbers tied to GenAI activity.

Examples:

```text
投入金额、团队人数、模型参数、客户数量、订单金额、收入金额、成本下降比例、上线日期、产品数量、专利数量。
```

Numbers unrelated to GenAI should not count.

## Aggregate Scores

After component coding:

```text
human_component_sum = sum(C1-C8, treating 9 as missing)
human_specificity_score_0_4:
    0 = no concrete GenAI detail
    1 = one weak concrete detail
    2 = several concrete details but no clear deployment/commercial path
    3 = concrete product/use case plus deployment or partner detail
    4 = highly concrete, with product/use case plus deployment/commercial/quantitative evidence
```

The 0-4 score should reflect coder judgment and does not need to mechanically equal the component sum.

## LLM Coding Prompt Requirements

When using an LLM coder, require JSON output only:

```json
{
  "event_id": "...",
  "has_specific_product_service": 0,
  "has_model_platform_name": 0,
  "has_specific_use_case": 0,
  "has_customer_or_industry": 0,
  "has_partner_or_org": 0,
  "has_deployment_status": 0,
  "has_commercialization_or_timeline": 0,
  "has_quantitative_commitment": 0,
  "llm_specificity_score_0_4": 0,
  "uncertain_flag": 0,
  "evidence_snippet": "",
  "coder_notes": ""
}
```

The LLM must not infer facts outside the provided text.

## Agreement Statistics

Report at least:

```text
Cohen's kappa for each binary component
agreement rate for each binary component
Pearson / Spearman correlation between human and LLM component sum
ICC or correlation for the 0-4 aggregate score
```

Minimum acceptable target:

```text
component kappas mostly above 0.60;
aggregate human-LLM correlation above 0.70.
```

If agreement is weaker, collapse noisy components into broader categories:

```text
product/use-case specificity
external-verifiability specificity
implementation/commercialization specificity
quantitative specificity
```

## Construct Validation Regressions

After coding, run:

```text
HumanSpecificityScore
    = Specificity_z
    + answer length
    + question length
    + AI keyword intensity
    + source controls
    + year FE
    + source FE

LLMSpecificityScore
    = Specificity_z
    + same controls
```

Expected:

```text
Specificity_z should positively predict human and LLM specificity scores.
```

## Convergent / Predictive Validation

Use future external AI evidence only as measurement validation:

```text
FutureExternalEvidence_{i,t+365}
    = Specificity_z_{i,t}
    + controls
    + industry FE
    + month FE
```

Candidate Y variables:

1. future CAC generative-AI service filing;
2. future AI / GenAI patent application;
3. future AI hiring within 365 days;
4. future GenAI product or service launch disclosure.

This table should be framed as validating the specificity measure, not as a main result.

## Coding Workflow

1. Draw 300 validation events from the frozen headline event universe.
2. Run LLM coding using this codebook.
3. Human-code at least the same 300 events or a high-overlap subset.
4. Reconcile obvious text parsing errors but do not force agreement.
5. Compute agreement.
6. Run construct validation regressions.
7. Run future external evidence validation if matched future evidence is available.
