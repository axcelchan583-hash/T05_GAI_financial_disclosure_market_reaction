# Specificity Validation Sample

Date: 2026-05-25

Purpose: create a frozen 300-event sample for human + LLM validation of `Specificity_z`.

## Sampling Frame

Sampling frame is the focal-event universe used by the current headline Top5 peer-CAR specification:

```text
first focal GenAI events
Top5 product-market peer analysis sample
announcement-cleaned market-reaction pipeline
eligible focal events = 2,177
```

## Sample Construction

The script draws 300 events with deterministic seed `20260525`. It balances across `Specificity_z` terciles:

```text
{'low': 100, 'mid': 100, 'high': 100}
```

Source distribution:

```text
{'iip_only': 254, 'irqa_only': 44, 'mixed_iip_irqa': 2}
```

Year distribution:

```text
{2023: 107, 2024: 35, 2025: 152, 2026: 6}
```

## Output Files

- `data/specificity_validation/specificity_validation_sample_300_20260525.csv`
- `data/specificity_validation/specificity_validation_coding_template_300_20260525.csv`
- `data/specificity_validation/specificity_validation_llm_input_300_20260525.jsonl`
- `data/specificity_validation/specificity_validation_sample_summary_20260525.csv`

## Coding Files

Use the codebook:

```text
docs/design/06_specificity_validation_codebook_20260525.md
```

Use the LLM prompt:

```text
docs/prompts/55_specificity_validation_llm_coding_prompt_20260525.md
```

## Next Step

1. Run LLM coding on the JSONL input.
2. Human-code the CSV template or a fully overlapping subset.
3. Compute agreement and construct-validation regressions.
4. Use future CAC / AI patent / AI hiring / product launch only as convergent validity, not as main Y.
