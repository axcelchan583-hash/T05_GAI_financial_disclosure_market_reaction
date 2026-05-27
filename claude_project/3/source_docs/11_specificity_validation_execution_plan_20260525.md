# Specificity Validation Execution Plan

Date: 2026-05-25

This file turns the measurement-validation concern into a concrete execution sequence.

## Goal

Answer the reviewer question:

```text
What does Specificity_z actually measure?
```

The validation should show two things:

1. positive construct validity: `Specificity_z` is associated with human / LLM-coded concrete GenAI disclosure details;
2. convergent validity: `Specificity_z` is associated with later observable AI-related actions, without turning those actions into the paper's main Y.

## Files Created

Validation sample:

```text
data/specificity_validation/specificity_validation_sample_300_20260525.csv
```

Human coding template:

```text
data/specificity_validation/specificity_validation_coding_template_300_20260525.csv
```

LLM input:

```text
data/specificity_validation/specificity_validation_llm_input_300_20260525.jsonl
```

Sample summary:

```text
data/specificity_validation/specificity_validation_sample_summary_20260525.csv
```

Codebook:

```text
docs/design/06_specificity_validation_codebook_20260525.md
```

LLM coding prompt:

```text
docs/prompts/55_specificity_validation_llm_coding_prompt_20260525.md
```

Sample construction log:

```text
docs/empirical_runs/55_specificity_validation_sample_20260525.md
```

## Positive Construct Validation

### Coding

Code the 300-event sample on these eight binary components:

```text
has_specific_product_service
has_model_platform_name
has_specific_use_case
has_customer_or_industry
has_partner_or_org
has_deployment_status
has_commercialization_or_timeline
has_quantitative_commitment
```

Also code:

```text
specificity_score_0_4
uncertain_flag
evidence_snippet
coder_notes
```

Minimum coding design:

```text
LLM codes all 300 rows.
Human codes all 300 rows if feasible.
If time constrained, human codes at least 150 rows stratified by specificity tercile and source.
```

Preferred design:

```text
human coder 1 codes all 300 rows
LLM coder codes all 300 rows
optional human coder 2 codes 100-row overlap
```

### Agreement

Report:

```text
Cohen's kappa by component
raw agreement by component
Pearson and Spearman correlation for component sums
ICC / correlation for 0-4 aggregate score
```

If a component has poor agreement, do not discard the whole validation. Collapse into broader factors:

```text
product/use-case specificity
external-verifiability specificity
implementation/commercialization specificity
quantitative specificity
```

### Construct-Validation Regression

Run:

```text
HumanScore_i
  = alpha
  + beta Specificity_z_i
  + answer length controls
  + question length controls
  + AI keyword / GenAI token controls
  + source controls
  + year FE
  + source-group FE
  + error_i
```

And:

```text
LLMScore_i
  = same RHS
```

Report both aggregate score and component sum.

The table should show:

```text
Specificity_z positively predicts human / LLM-coded specificity.
This remains after length and AI-keyword controls.
```

## Convergent / Predictive Validation

This is a measurement-validation table, not a mechanism table.

### Candidate Future Evidence

Use windows after the focal event:

```text
future CAC generative-AI service filing within 365 days
future broad-AI patent application / grant within 365 or 540 days
future GenAI patent application / grant within 365 or 540 days
future broad-AI hiring within 365 days
future GenAI hiring within 365 days
future GenAI product / service launch disclosure within 365 days
```

### Preferred Model

For binary outcomes:

```text
FutureEvidence_{i,t+365}
  = alpha
  + beta Specificity_z_{i,t}
  + baseline AI activeness controls
  + firm size / industry controls if available
  + industry FE
  + event-month FE
  + error_i
```

If controls are not yet clean, use a simpler validation specification:

```text
FutureEvidence_{i,t+365}
  = alpha
  + beta Specificity_z_{i,t}
  + source-group FE
  + event-month FE
  + error_i
```

Expected sign:

```text
beta > 0
```

Interpretation:

```text
Higher specificity is associated with later observable AI-related actions,
supporting the construct validity of the specificity measure.
```

Not allowed:

```text
Specificity causes future AI investment.
Future CAC / patents / hiring are the paper's main outcome.
```

## Main Manuscript Placement

Recommended table placement:

```text
Table 3: Specificity construct validation
    Panel A: component agreement and score correlations
    Panel B: Specificity_z predicting human / LLM scores

Table 4 or Appendix Table:
    Specificity_z predicting future external AI evidence
```

If space is tight:

```text
main text: compact validation table
appendix: full component kappas and examples
```

## Go / No-Go Threshold

Continue current measurement if:

```text
Specificity_z significantly predicts human or LLM aggregate score;
aggregate human-LLM agreement is acceptable;
at least some future external evidence outcomes have the expected positive sign.
```

Revise the specificity measure if:

```text
Specificity_z does not predict human / LLM-coded specificity;
agreement shows coders cannot identify the construct;
the measure is fully explained by length and generic AI keyword intensity.
```

If revision is needed, replace the current Hope-style proxy with a component-weighted validated score:

```text
ValidatedSpecificity = standardized sum of the reliable components
```

and re-run the peer-CAR table as a robustness check.
