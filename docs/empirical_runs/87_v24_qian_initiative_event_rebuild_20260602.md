# v24 Qian Supplier Replication Event Rebuild

Date: 2026-06-02

Purpose: rebuild the treatment side before rerunning the Qian-style supplier event study. v23 should be treated as a keyword-triggered audit, not as a clean replication of Qian et al.'s GenAI initiative sample.

## Qian Screen Implemented Here

Qian et al. manually reviewed firm announcements, retained explicit GenAI initiatives, excluded broad GenAI/IT mentions, kept the earliest initiative per firm, verified announcement dates, and then linked downstream customers to listed suppliers. This v24 run mirrors the event-screening part only.

The intended funnel is therefore: broad GenAI retrieval -> listed-company event universe -> manual initiative screen -> first initiative per firm -> supplier-link and return-data filters. The broad retrieval is not the treatment.

## Inputs

- Formal CNINFO events: `results/v3_event_library_expansion_diagnostic/formal_all_events_events_before_car.csv`
- Supplemental IR/QA events: `results/v3_event_library_expansion_diagnostic/irqa_all_events_supplement_events_before_car.csv`
- CSMAR focal events used by prior T05 panels: `results/v7_ai_supply_chain_disclosure_diagnostic_20260527/all_focal_events_supply_chain_codes.csv`
- v23 first-event supplier sample markers: `results/v23_qian_supplier_replication_20260602/analysis_sample_first_valid_events.csv.gz`

## Output Files

- `event_universe_auto_classified.csv.gz`: all normalized events with rule flags.
- `manual_review_v23_upstream_focal_events.csv`: one row per v23 upstream focal event for contamination audit.
- `manual_review_qian_candidate_events.csv`: machine-prioritized candidate/review rows for building the corrected treatment.
- `manual_review_first_auto_candidate_per_firm.csv`: earliest machine-kept candidate per focal firm, not final until manually coded.
- `manual_review_supplier_linked_candidate_events.csv`: candidate/review rows that have an upstream listed-supplier link.
- `manual_review_first_supplier_linked_auto_candidate_per_firm.csv`: recommended first-pass manual queue for the replication sample.
- `manual_review_all_strict_events.csv.gz`: all strict GenAI rows for backtracking.
- `manual_review_instructions.md`: coding rules for one-by-one review.

## Summary

| metric                                            |    value |
|:--------------------------------------------------|---------:|
| all_event_rows                                    | 21177    |
| all_unique_firms                                  |  2704    |
| strict_genai_any_rows                             | 21049    |
| strict_genai_company_text_rows                    | 21014    |
| auto_keep_candidate_rows                          | 13276    |
| auto_keep_candidate_unique_firms                  |  1672    |
| first_auto_candidate_unique_firms                 |  1672    |
| supplier_linked_event_rows                        |  2154    |
| supplier_linked_auto_keep_candidate_rows          |  1364    |
| supplier_linked_auto_keep_candidate_unique_firms  |   200    |
| first_supplier_linked_auto_candidate_unique_firms |   200    |
| v23_upstream_unique_focal_events                  |   204    |
| v23_upstream_auto_keep_candidate_events           |    79    |
| v23_upstream_auto_excluded_events                 |   125    |
| v23_upstream_auto_excluded_pct                    |    61.27 |

## v23 Upstream Event Auto Labels

| qian_auto_label                           |   events |   supplier_links |
|:------------------------------------------|---------:|-----------------:|
| exclude_denial_no_current_business        |       79 |              117 |
| keep_candidate_strong_specific_initiative |       44 |               62 |
| review_possible_specific_initiative       |       35 |               55 |
| exclude_boilerplate_attention_only        |       23 |               35 |
| review_ambiguous_strict_genai             |       23 |               45 |

## Candidate Counts by Source and Label

| source_type                                    | qian_auto_label                           |    n |
|:-----------------------------------------------|:------------------------------------------|-----:|
| csmar_investor_interaction                     | keep_candidate_strong_specific_initiative | 5742 |
| csmar_investor_interaction                     | review_possible_specific_initiative       | 2518 |
| csmar_investor_interaction                     | review_ambiguous_strict_genai             | 1177 |
| csmar_investor_interaction;csmar_ir_meeting_qa | keep_candidate_strong_specific_initiative |  191 |
| csmar_investor_interaction;csmar_ir_meeting_qa | review_possible_specific_initiative       |   33 |
| csmar_investor_interaction;csmar_ir_meeting_qa | review_ambiguous_strict_genai             |    8 |
| csmar_ir_meeting_qa                            | keep_candidate_strong_specific_initiative | 3085 |
| csmar_ir_meeting_qa                            | review_ambiguous_strict_genai             | 1383 |
| csmar_ir_meeting_qa                            | review_possible_specific_initiative       | 1029 |
| formal_cninfo_announcement                     | keep_candidate_strong_specific_initiative |   17 |
| supplemental_irqa_answer                       | keep_candidate_strong_specific_initiative |  494 |
| supplemental_irqa_answer                       | review_possible_specific_initiative       |  167 |
| supplemental_irqa_answer                       | review_ambiguous_strict_genai             |  166 |

## Interpretation

The decisive next step is manual coding, not another return regression. Start with `manual_review_first_supplier_linked_auto_candidate_per_firm.csv` (200 rows). `manual_keep_qian_0_1` must become the gate for the corrected event sample. Only after that should the supplier AR0 and CAR[0,+1] tables be rerun.

## Current Limitation

The rule labels are conservative triage labels. They help sort and identify obvious exclusions, but they do not replace reading the announcement/answer text and verifying whether the company itself announced a concrete GenAI initiative.
