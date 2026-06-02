# GenAI Disclosure Concreteness Measure

Date: 2026-05-28

## Purpose

This document defines a reproducible event-level X variable:

`GenAI_Disclosure_Concreteness`

The measure captures observable textual concreteness in focal firms' GenAI-related investor-interaction disclosures. It does not measure real GenAI capability, real investment, actual commercialization, or future success. It is a disclosure-text measure available to investors at the disclosure date.

## Literature Anchors

The measure is grounded in two papers inspected from the local PDF files:

- Hope, Hu, and Lu (2016), "The Benefits of Specific Risk-Factor Disclosures", Review of Accounting Studies. Their specificity construct scales concrete, verifiable disclosure details by total words. The concrete details include entity names and quantitative information such as organizations, people, locations, percentages, money, times, and dates.
- Cheng, De Franco, Jiang, and Lin (2019), "Riding the Blockchain Mania: Public Firms' Speculative 8-K Disclosures", Management Science. Their technology-mania setting separates vague speculative disclosures from disclosures describing existing products, services, acquisitions, or substantive technology activity.

The current measure combines these ideas: first extract GenAI-relevant disclosure sentences, then count concrete detail density, and separately classify whether the content is generic/speculative, substantive/existing, competitive-risk related, or category-validation related.

## Input Dataset Audit

The pipeline inspects existing event data and uses the event-level file closest to the current project sample:

`results/csmar_v5_1_response_smoke_20260523/csmar_conservative_focal_events_2023_2026.csv`

This file contains one row per focal firm-date GenAI event and includes:

- `event_id`
- `focal_code`
- `event_date`
- `sample_answer`
- `sample_question`
- prior event-level specificity fields such as `specificity`

Other candidate files were not selected as the primary measurement input:

- `results/csmar_genai_event_library_20260523/combined_firm_day_genai_events.csv`: event-level text library, but weaker event-id alignment.
- `results/v6_focal_good_news_pretrend_checks_20260525/analysis_sample_top5.csv.gz`: final peer-event regression panel, but it is not an event-level text dataset.

## Script

Main script:

`scripts/measurement/build_genai_disclosure_concreteness.py`

Smoke test:

```bash
python scripts/measurement/build_genai_disclosure_concreteness.py --smoke-test
```

Full run:

```bash
python scripts/measurement/build_genai_disclosure_concreteness.py \
  --output-dir results/genai_concreteness_measure_20260528
```

## GenAI Sentence Extraction

The script extracts sentences containing strong GenAI terms such as:

`生成式人工智能`, `生成式AI`, `AIGC`, `大模型`, `大语言模型`, `LLM`, `ChatGPT`, `GPT`, `DeepSeek`, `Kimi`, `通义`, `文心`, `盘古`, `混元`, `智谱`, `百川`, `讯飞星火`, `豆包`, `智能体`, `Agent`, `多模态`, `RAG`, `检索增强`, `AI助手`, `AI客服`, `AI编程`.

Generic `人工智能` / `AI` sentences are not sufficient unless they also contain GenAI-adjacent context. The script also distinguishes extracted sentences from counted positive GenAI sentences:

- `genai_text`: all extracted GenAI-relevant sentences.
- `counted_genai_text`: only sentences treated as positive focal-firm GenAI claims for concreteness counting.

This distinction is important because many investor-interaction answers say "未涉及 ChatGPT" or "暂无 DeepSeek 部署". Those sentences are retained in `genai_text`, but they do not receive high concrete-detail counts unless the same disclosure also contains a positive GenAI product, deployment, customer, or application claim.

## Hope-Style Concrete Detail Counts

The pipeline counts three concrete-detail dimensions:

1. `entity_concrete_count`

Concrete named entities related to GenAI disclosure, such as product names, model names, named platforms, applications, customers, partners, subsidiaries, business lines, scenarios, or modules. Generic terms like `人工智能`, `大模型`, `平台`, `系统`, `产品`, `客户`, and `生态` are not counted by themselves.

2. `operational_concrete_count`

Operating/application details such as `发布`, `推出`, `上线`, `接入`, `部署`, `落地`, `试点`, `内测`, `公测`, `应用于`, `用于`, scenario terms such as `智能客服`, `代码生成`, `知识库`, `RAG`, and commercialization terms such as `商业化`, `订单`, `合同`, `收费`, `订阅`, `API调用`, `私有化部署`.

Negated operating phrases such as `尚未部署 DeepSeek` or `暂未应用 ChatGPT` are not counted as positive operating concreteness.

3. `quant_concrete_count`

Verifiable quantitative details, including dates, monetary values, percentages, customer/user/project counts, model parameter counts, GPU/compute quantities, API calls, performance metrics, deployment counts, revenue/order/contract amounts, and Chinese/English number formats.

## Main Measures

Raw density:

```text
genai_concreteness_raw = total_concrete_count / max(genai_token_count, 1)
```

where:

```text
total_concrete_count =
  entity_concrete_count
  + operational_concrete_count
  + quant_concrete_count
```

Additional measures:

- `genai_concreteness_char_density = total_concrete_count / max(genai_char_count, 1)`
- `genai_concreteness_z`: full-sample z-score.
- `genai_concreteness_z_by_year`: z-score within event year.
- `genai_concreteness_resid_z`: residualized z-score after regressing raw concreteness on log token count, log character count, AI keyword count, GenAI sentence count, and event year-month fixed effects.

Recommended main X for regressions:

`genai_concreteness_resid_z`

Recommended first robustness:

`genai_concreteness_z`

The residualized version is useful because reviewers may worry that concreteness is only a proxy for answer length, AI keyword intensity, or event timing.

## Cheng-Style Content Classification

The script creates non-mutually-exclusive low-level categories:

- `generic_ai_talk`
- `future_plan`
- `governance_personnel`
- `product_service`
- `deployment_commercialization`
- `customer_exposure`
- `infrastructure_ecosystem`
- `investment_subsidiary_partner`
- `industry_trend_only`
- `denial_or_no_exposure_content`
- `positive_genai_claim_content`

It then creates high-level indicators:

- `speculative_or_generic_content`: generic AI talk, future plans without operating details, governance/personnel content, industry-trend-only language, or denial/no-exposure content.
- `substantive_or_existing_content`: concrete product/service, deployment, customer, commercialization, or existing-project information.
- `competitive_risk_content`: product/service, deployment/commercialization, customer exposure, application scenarios, model capability, or named product details that could plausibly signal product-market competitive risk.
- `category_validation_content`: AI infrastructure, computing power, data centers, chips, servers, ecosystem partnerships, or broad AI supply-chain / demand-validation content.

`content_category_primary` is a priority label for readability only:

1. `competitive_risk_content`
2. `category_validation_content`
3. `substantive_or_existing_content`
4. `speculative_or_generic_content`
5. `uncategorized_or_low_signal`

The binary indicators remain non-mutually-exclusive.

## Full-Run Outputs

Output directory:

`results/genai_concreteness_measure_20260528/`

Files:

- `event_genai_concreteness.csv`
- `summary_stats.csv`
- `correlation_with_text_controls.csv`
- `top_bottom_examples.md`
- `manual_validation_sample.csv`
- `manual_validation_instructions.md`
- `measurement_log.txt`

Full-run headline diagnostics:

- Events processed: 20,165
- Focal firms: 2,665
- Missing source text count: 0
- Events with no extracted GenAI sentence after strict filtering: 1,238
- Events with no positive GenAI sentence counted for concreteness: 7,603
- `positive_genai_claim_content` share: 0.616
- `denial_or_no_exposure_content` share: 0.110
- `competitive_risk_content` share: 0.559
- `category_validation_content` share: 0.188
- `speculative_or_generic_content` share: 0.439
- `genai_concreteness_raw` mean: 0.0565
- `genai_concreteness_raw` median: 0.0465
- `genai_concreteness_raw` 95th percentile: 0.1667

## Recommended Merge Into Main Regression

Merge at `event_id`:

```python
import pandas as pd

panel = pd.read_csv("results/v6_focal_good_news_pretrend_checks_20260525/analysis_sample_top5.csv.gz")
x = pd.read_csv("results/genai_concreteness_measure_20260528/event_genai_concreteness.csv")

keep = [
    "event_id",
    "genai_concreteness_z",
    "genai_concreteness_z_by_year",
    "genai_concreteness_resid_z",
    "competitive_risk_content",
    "category_validation_content",
    "speculative_or_generic_content",
    "substantive_or_existing_content",
    "content_category_primary",
]

panel2 = panel.merge(x[keep], on="event_id", how="left", validate="many_to_one")
```

Main regression replacement:

- Replace old `specificity_z` with `genai_concreteness_resid_z`.
- Keep old `specificity_z` as a robustness or legacy comparison.
- Headline interaction: `genai_concreteness_resid_z × AIActivePeer`.

## Limitations

This is deterministic dictionary/regex measurement. It is reproducible and auditable, but it is not semantic understanding. It can still misclassify:

- broad NLP / intelligent-customer-service content as GenAI-adjacent;
- third-party or subsidiary claims as focal-firm content;
- short but highly concrete statements as high-density observations;
- supply-chain/infrastructure disclosures that validate the AI category rather than signal direct product-market rivalry.

These limitations should be handled through robustness tests, top/bottom example review, and content-category controls. The measure should not be interpreted as real capability or verified commercialization.

