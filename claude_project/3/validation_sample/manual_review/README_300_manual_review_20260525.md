# Specificity Validation 300-Event Manual Review Files

Date: 2026-05-25

This folder contains only the 300 sampled focal GenAI disclosure events for manual review. It intentionally excludes the machine pre-coding output.

## Files

- `manual_review_raw_300_20260525.csv`
  - 300 sampled events.
  - Original columns only: event identifiers, firm/date/source fields, existing specificity variables, question text, and answer text.

- `manual_review_coding_template_300_20260525.csv`
  - Same 300 events.
  - Adds blank coding columns for manual or LLM-assisted coding:
    - `has_specific_product_service`
    - `has_model_platform_name`
    - `has_specific_use_case`
    - `has_customer_or_industry`
    - `has_partner_or_org`
    - `has_deployment_status`
    - `has_commercialization_or_timeline`
    - `has_quantitative_commitment`
    - `specificity_score_0_4`
    - `uncertain_flag`
    - `evidence_snippet`
    - `coder_notes`

## Sample Construction

- Sampling frame: headline Top5 first-focal-event analysis sample.
- Sample size: 300 events.
- Stratification: 100 low, 100 mid, and 100 high observations by the current `specificity_z` tercile.
- Purpose: validate what the current `Specificity_z` proxy is actually measuring before deciding whether to keep, revise, or replace it.

