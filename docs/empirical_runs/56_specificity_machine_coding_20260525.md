# Specificity Machine Pre-Coding

Date: 2026-05-25

This is a reproducible machine pre-code for the 300-event specificity validation sample. It is not a substitute for human coding or API-based LLM coding; use it as a first pass for review and error correction.

## Inputs

- `data/specificity_validation/specificity_validation_sample_300_20260525.csv`
- `docs/design/06_specificity_validation_codebook_20260525.md`

## Outputs

- `data/specificity_validation/specificity_validation_machine_coding_300_20260525.csv`
- `data/specificity_validation/specificity_validation_machine_coding_300_20260525.jsonl`
- `data/specificity_validation/specificity_validation_machine_coding_summary_20260525.csv`
- `data/specificity_validation/specificity_validation_machine_coding_correlations_20260525.csv`

## Coding Logic

The script extracts GenAI-context sentences, handles explicit negative/no-current-involvement statements, and codes eight codebook components:

```text
['has_specific_product_service', 'has_model_platform_name', 'has_specific_use_case', 'has_customer_or_industry', 'has_partner_or_org', 'has_deployment_status', 'has_commercialization_or_timeline', 'has_quantitative_commitment']
```

Explicit negative/no-current-involvement statements coded as zero-component disclosures:

```text
119
```

## Score Distribution

```text
{0: 174, 1: 5, 2: 42, 3: 71, 4: 8}
```

## Means by Specificity Tercile

```text
                machine_component_sum       machine_specificity_score_0_4      
                                 mean count                          mean count
specificity_bin                                                                
high                             1.45   100                          1.07   100
low                              1.36   100                          0.98   100
mid                              1.74   100                          1.29   100
```

## Correlations with Existing Specificity Proxy

```text
                            y                    x   n  pearson  spearman
        machine_component_sum        specificity_z 300 0.016374  0.048788
machine_specificity_score_0_4        specificity_z 300 0.023695  0.063598
        machine_component_sum          specificity 300 0.006120  0.048612
machine_specificity_score_0_4          specificity 300 0.013672  0.063427
        machine_component_sum total_specific_items 300 0.409498  0.385858
machine_specificity_score_0_4 total_specific_items 300 0.382728  0.392417
```

## Next Step

Human review should focus first on:

1. rows where machine score is high but `specificity_bin` is low;
2. rows where machine score is low but `specificity_bin` is high;
3. rows with negative/no-current-involvement notes;
4. rows with `machine_uncertain_flag = 1`.

After human or API-LLM coding is available, compute kappa / agreement against this machine pre-code only as a diagnostic. The publishable validation should use human and LLM/human overlap, not this deterministic pre-code alone.
