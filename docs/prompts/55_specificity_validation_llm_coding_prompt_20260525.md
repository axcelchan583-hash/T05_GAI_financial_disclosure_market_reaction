# Specificity Validation LLM Coding Prompt

Use this prompt with the 300-row validation sample.

## Prompt

You are coding corporate GenAI disclosure specificity for an empirical accounting/finance study.

You will receive one event at a time. Each event contains:

- `event_id`
- `company_name`
- `event_date`
- `sources`
- `sample_question`
- `sample_answer`

Code only the information contained in `sample_answer`. Use `sample_question` only for context. Do not infer facts from outside knowledge.

The coding target is whether the company's GenAI / large-model / AIGC disclosure contains concrete, verifiable, implementation-oriented details.

For each binary field, use:

```text
1 = clearly present
0 = absent
9 = unclear / cannot determine
```

Fields:

1. `has_specific_product_service`: concrete product, service, platform, software, system, module, chatbot, assistant, or solution.
2. `has_model_platform_name`: named model or model platform, such as ChatGPT, GPT, DeepSeek, 通义, 文心, Kimi, 智谱, 星火, 盘古, 混元, 自研大模型, or another identifiable model/platform.
3. `has_specific_use_case`: concrete application scenario or business function, such as customer service, marketing, medical diagnosis, education, smart cockpit, coding, risk control, quality inspection, search, recommendation, office assistant.
4. `has_customer_or_industry`: customer type, named client, user group, downstream industry, business segment, or deployment sector.
5. `has_partner_or_org`: external partner, supplier, client, research institution, university, regulator, platform company, or named outside organization.
6. `has_deployment_status`: implementation stage such as launched, released, filed, deployed, connected, landed, internal testing, pilot, training completed, commercialized, or contracted.
7. `has_commercialization_or_timeline`: revenue implication, customer rollout, launch timeline, deadline, milestone, order, paid version, commercialization plan.
8. `has_quantitative_commitment`: number tied to GenAI activity, including investment, team size, model parameters, customer count, order value, revenue, cost reduction, launch date, product count, patent count.

Also code:

```text
llm_specificity_score_0_4:
    0 = no concrete GenAI detail
    1 = one weak concrete detail
    2 = several concrete details but no clear deployment/commercial path
    3 = concrete product/use case plus deployment or partner detail
    4 = highly concrete, with product/use case plus deployment/commercial/quantitative evidence
```

Return JSON only. No prose outside JSON.

Required JSON schema:

```json
{
  "event_id": "",
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

Rules:

- If a statement only says "关注", "探索", "布局", "赋能", "积极研究", code most components as 0.
- A named technology without a business use case can count for `has_model_platform_name` but not for `has_specific_use_case`.
- A number counts only if tied to GenAI / AI activity.
- Generic "industry opportunity is large" is not commercialization.
- Do not use outside knowledge about the company.
- Keep `evidence_snippet` short and quote only the exact part that supports the coding.
