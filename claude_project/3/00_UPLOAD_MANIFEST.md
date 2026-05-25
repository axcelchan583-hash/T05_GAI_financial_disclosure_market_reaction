# Upload Manifest: T05 GenAI Disclosure and Product-Market Peer Revaluation

Date: 2026-05-25

This folder is a clean upload package for Claude / ChatGPT Pro review. It is intentionally focused on the current v6 design and excludes older abandoned designs.

## Recommended Upload Order

Upload these first:

1. `01_PROJECT_BRIEF_EN.md`
2. `02_DEEP_REVIEW_PROMPT_EN.md`
3. `source_docs/03_current_research_design_20260525.md`
4. `source_docs/07_final_review_checks_20260525.md`
5. `source_docs/08_focal_good_news_pretrend_checks_20260525.md`

If the model needs more detail, also upload:

6. `source_docs/04_paper_outline_20260525.md`
7. `source_docs/06_identification_strengthening_checks_20260524.md`
8. `results_csv/headline.csv`
9. `results_csv/task1_focal_good_news_controls.csv`
10. `results_csv/task2_pretrend_residualized_y.csv`
11. `results_csv/specificity_validation.csv`
12. `results_csv/proximity_gradient.csv`
13. `results_csv/lead_lag.csv`
14. `results_csv/external_breakdown.csv`
15. `results_csv/mechanism.csv`

Optional reproducibility file:

- `repro_scripts/run_v6_final_review_checks_20260525.py`

## Current One-Line Design

More specific focal-firm GenAI disclosures are associated with more negative short-window market revaluation among AI-active close product-market peers.

## Current Status

- Main capital-market result passes the current go/no-go bar.
- The result survives announcement cleaning, strong fixed effects, pre-window CAR controls, focal-firm good-news controls, pre-trend-adjusted outcomes, external AIActive validation, product-market proximity gradient checks, and placebo peer checks.
- Peer-disclosure diffusion does not survive the stricter 2026-05-25 mechanism specification and should not be treated as a core mechanism.

## What We Want From Web Models

Ask for a referee-style critique, not a rewrite. The most valuable output is:

- whether the design can plausibly support an AJG/ABS 3 submission;
- which identification threat remains most damaging;
- whether the current result should be framed as a conditional peer-revaluation paper;
- what additional tests are strictly necessary before drafting;
- what claims should be removed or softened.
