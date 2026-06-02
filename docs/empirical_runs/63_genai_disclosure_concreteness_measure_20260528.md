# Run 63: GenAI Disclosure Concreteness Measurement

Date: 2026-05-28

## Objective

Build a reproducible event-level X variable:

`GenAI_Disclosure_Concreteness`

This X is a text-based disclosure-concreteness measure, not a real capability measure.

## Literature Basis

Local PDFs inspected:

- `/Users/mac/computerscience/23实证选题探索/bib/GenAI文献/EBSCO-FullText-05_28_2026.pdf`
  - Hope, Hu, and Lu (2016), Review of Accounting Studies.
  - Specificity is operationalized as concrete entity/quantitative detail density.
- `/Users/mac/computerscience/23实证选题探索/bib/GenAI文献/EBSCO-FullText-05_28_2026 (1).pdf`
  - Cheng, De Franco, Jiang, and Lin (2019), Management Science.
  - Technology-mania disclosures are separated into speculative/generic versus existing/substantive disclosures.

## Implementation

Script:

`scripts/measurement/build_genai_disclosure_concreteness.py`

Documentation:

`docs/measurement/10_genai_disclosure_concreteness_measure_20260528.md`

Input:

`results/csmar_v5_1_response_smoke_20260523/csmar_conservative_focal_events_2023_2026.csv`

Output directory:

`results/genai_concreteness_measure_20260528/`

## Smoke Test

Command:

```bash
python scripts/measurement/build_genai_disclosure_concreteness.py --smoke-test
```

Result:

- Low-concreteness example: zero concrete details; classified as `speculative_or_generic_content`.
- High-concreteness example: higher entity, operational, quantitative, total concrete counts; classified as `competitive_risk_content`.

## Full Run

Command:

```bash
python scripts/measurement/build_genai_disclosure_concreteness.py \
  --output-dir results/genai_concreteness_measure_20260528
```

Key diagnostics:

- Rows/events processed: 20,165
- Focal firms: 2,665
- Missing source text: 0
- Events with no extracted GenAI sentence after strict filtering: 1,238
- Events with zero positive GenAI sentence counted for concreteness: 7,603
- `positive_genai_claim_content` share: 0.6160
- `denial_or_no_exposure_content` share: 0.1103
- `competitive_risk_content` share: 0.5592
- `category_validation_content` share: 0.1879
- `speculative_or_generic_content` share: 0.4389
- `substantive_or_existing_content` share: 0.5983
- `genai_concreteness_raw` mean: 0.0565
- `genai_concreteness_raw` median: 0.0465
- `genai_concreteness_raw` 95th percentile: 0.1667

## Main Panel Merge Smoke Check

Main Top5 peer panel:

`results/v6_focal_good_news_pretrend_checks_20260525/analysis_sample_top5.csv.gz`

Merge key: `event_id`

Merge result:

- Main panel rows: 7,805
- Main panel events: 2,177
- Event-level X rows: 20,165
- Event-level X events: 20,165
- Matched share: 1.000
- Unmatched events: 0

Correlation with legacy event-level `specificity_z` inside the main panel:

- `corr(specificity_z, genai_concreteness_resid_z) = 0.112`
- `corr(specificity_z, genai_concreteness_z) = 0.045`

Interpretation: the new X is not mechanically the old `specificity_z`. That is useful for measurement independence, but it also means the main regression must be re-estimated before treating prior results as carrying over.

Main-panel content shares:

- `competitive_risk_content`: 0.3271
- `category_validation_content`: 0.1176
- `speculative_or_generic_content`: 0.6881
- `substantive_or_existing_content`: 0.3475

## Output Files

- `results/genai_concreteness_measure_20260528/event_genai_concreteness.csv`
- `results/genai_concreteness_measure_20260528/summary_stats.csv`
- `results/genai_concreteness_measure_20260528/correlation_with_text_controls.csv`
- `results/genai_concreteness_measure_20260528/top_bottom_examples.md`
- `results/genai_concreteness_measure_20260528/manual_validation_sample.csv`
- `results/genai_concreteness_measure_20260528/manual_validation_instructions.md`
- `results/genai_concreteness_measure_20260528/measurement_log.txt`

## Recommended Next Step

Run the peer-CAR main table again using:

- Main X: `genai_concreteness_resid_z`
- Robustness X: `genai_concreteness_z`
- Legacy comparison: old `specificity_z`

Do not assume prior `specificity_z × AIActivePeer` results survive. The new X has low correlation with the legacy variable and should be treated as a new measurement design.

