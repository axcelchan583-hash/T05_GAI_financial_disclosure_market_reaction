# Coding Task for Claude Code

This is not a paper-review task. It is a data-labeling task.

## Goal

Continue the independent Claude web coding of the 300-row GenAI disclosure specificity validation sample.

Rows `SV0001` to `SV0160` have already been coded by Claude web in:

- `claude_project/3/specificity_validation_codes_partial_SV0001-0160_20260526.csv`

Your immediate task is to code rows `SV0161` to `SV0300` using the same rules.

## Input Files

Use these project-relative paths:

- `claude_project/3/HANDOFF_README.md`
- `claude_project/3/coding_guidelines.md`
- `claude_project/3/specificity_validation_codes_partial_SV0001-0160_20260526.csv`
- `claude_project/3/validation_sample/manual_review/manual_review_coding_template_300_20260525.csv`
- `claude_project/3/source_docs/10_specificity_validation_codebook_20260525.md`

If a path is not visible, search the repository for the filename.

## Output Files

Create:

- `claude_project/3/validation_sample/claude_coding/claude_manual_codes_300_20260526.csv`
- `claude_project/3/validation_sample/claude_coding/claude_manual_codes_300_20260526_summary.md`

## Required Output Columns

The final CSV must contain exactly 300 rows and these columns:

```text
validation_id,event_id,focal_code,company_name,event_date,source_group,specificity_bin,specificity_z,sample_question,sample_answer,
has_specific_product_service,has_model_platform_name,has_specific_use_case,has_customer_or_industry,has_partner_or_org,has_deployment_status,has_commercialization_or_timeline,has_quantitative_commitment,specificity_score_0_4,uncertain_flag,evidence_snippet,coder_notes
```

## Coding Rules

- One row is one focal GenAI disclosure event.
- Preserve existing Claude web coding for `SV0001` to `SV0160`.
- Fill only `SV0161` to `SV0300`.
- Read `sample_question` and `sample_answer`, but code only the company's answer/disclosure.
- Investor question content alone does not count as company disclosure.
- Component columns must be `0` or `1`. Use `9` only if truly impossible to judge.
- Negative/no-current answers such as "not involved", "not connected", "no cooperation", "no current business", or "only following/exploring/researching" should usually be all `0` and score `0`, unless the same answer separately discloses concrete company GenAI implementation.
- Generic industry explanations, such as "ChatGPT can be used in film/robots/medicine", should be low specificity unless the company states its own product, scenario, deployment, partner, commercialization, or quantitative commitment.
- Score `0` to `4` according to the codebook.
- `evidence_snippet` should quote the shortest supporting Chinese phrase from `sample_answer`.
- `coder_notes` should briefly explain the judgment.

## Summary File

The summary should report:

- total coded rows
- score distribution
- count of `1`s for each component
- uncertain_flag count
- 10 `validation_id`s most likely to have coding disagreement

## Do Not Do

- Do not evaluate the paper.
- Do not suggest new research designs.
- Do not summarize the research package.
- Do not compare with another coder before completing the 300-row coding.
- Do not use any agent-coded output while coding.
