# Agent 1 Manual Coding Summary

Date: 2026-05-26
Coder: agent1 independent manual coder

## Scope

- Input: `data/specificity_validation/manual_review/manual_review_coding_template_300_20260525.csv`
- Output: `data/specificity_validation/agent_coding/agent1_manual_codes_300_20260526.csv`
- Codebook: `docs/design/06_specificity_validation_codebook_20260525.md`
- Coding rule applied: only GenAI-related content in the company answer/disclosure was coded; investor-question content alone was not counted.

## Row Count

- Total coded rows: 300
- Validation ID order preserved: yes

## Score Distribution

- score 0: 185
- score 1: 10
- score 2: 25
- score 3: 29
- score 4: 51

## Component Counts

- has_specific_product_service: 97
- has_model_platform_name: 78
- has_specific_use_case: 102
- has_customer_or_industry: 76
- has_partner_or_org: 26
- has_deployment_status: 94
- has_commercialization_or_timeline: 29
- has_quantitative_commitment: 27

## Uncertain Rows

- uncertain_flag = 1: 12

## 10 Most Likely Disagreement Cases

- SV0041: uncertain; large-model exploration is mixed with existing NLP/knowledge-graph system
- SV0069: uncertain; investee/future large-model wording rather than present deployment
- SV0075: uncertain; mostly generic robot large-model discussion with limited company-specific linkage
- SV0081: uncertain; market-demand disclosure tied to company product rather than own GenAI implementation
- SV0109: uncertain; deployed NLP projects but ChatGPT itself remains under research
- SV0116: uncertain; current NLP product plus AIGC research, not clear GenAI deployment
- SV0120: uncertain; mostly external example plus company hardware carrier, not direct GenAI implementation
- SV0184: uncertain; API calling disclosed but use case is not specified
- SV0264: uncertain; group-level deployment, company says it will follow unified arrangement
- SV0298: uncertain; company chatbot platform but ChatGPT only under research

## Coding Notes

- Negative/no-current answers such as no access, no deployment, no cooperation, no current business were coded as score 0 with all components 0 unless the same answer disclosed a separate current GenAI implementation.
- Generic industry discussions, market-benefit narratives, and non-GenAI AI applications were downgraded when they lacked company-specific GenAI implementation details.
- Infrastructure and supply-chain disclosures were coded above 0 only when the answer gave company-specific products, customers, deployment, or quantitative evidence tied to GenAI/large-model demand.
