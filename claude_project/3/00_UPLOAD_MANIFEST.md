# Upload Manifest: T05 GenAI Disclosure and Product-Market Peer Revaluation

Date: 2026-05-26

This folder is a clean upload package for Claude / ChatGPT Pro review. It is intentionally focused on the current v6 design and excludes older abandoned designs.

## Recommended Upload Order

Upload these first:

1. `01_PROJECT_BRIEF_EN.md`
2. `02_DEEP_REVIEW_PROMPT_EN.md`
3. `source_docs/03_current_research_design_20260525.md`
4. `source_docs/07_final_review_checks_20260525.md`
5. `source_docs/08_focal_good_news_pretrend_checks_20260525.md`
6. `source_docs/09_design_freeze_20260525.md`
7. `source_docs/10_specificity_validation_codebook_20260525.md`
8. `source_docs/11_specificity_validation_execution_plan_20260525.md`

If the model needs more detail, also upload:

9. `source_docs/04_paper_outline_20260525.md`
10. `source_docs/06_identification_strengthening_checks_20260524.md`
11. `source_docs/12_specificity_validation_sample_20260525.md`
12. `results_csv/headline.csv`
13. `results_csv/task1_focal_good_news_controls.csv`
14. `results_csv/task2_pretrend_residualized_y.csv`
15. `results_csv/specificity_validation.csv`
16. `results_csv/proximity_gradient.csv`
17. `results_csv/lead_lag.csv`
18. `results_csv/external_breakdown.csv`
19. `results_csv/mechanism.csv`
20. `validation_sample/specificity_validation_sample_300_20260525.csv`
21. `validation_sample/specificity_validation_coding_template_300_20260525.csv`
22. `validation_sample/agent_coding/agent1_manual_codes_300_20260526.csv`
23. `validation_sample/agent_coding/agent1_manual_codes_300_20260526_summary.md`

Optional reproducibility file:

- `repro_scripts/run_v6_final_review_checks_20260525.py`
- `repro_scripts/build_specificity_validation_sample_20260525.py`

## Current One-Line Design

More specific focal-firm GenAI disclosures are associated with more negative short-window market revaluation among AI-active close product-market peers.

## Current Status

- Main capital-market result passes the current go/no-go bar.
- The result survives announcement cleaning, strong fixed effects, pre-window CAR controls, focal-firm good-news controls, pre-trend-adjusted outcomes, external AIActive validation, product-market proximity gradient checks, and placebo peer checks.
- Peer-disclosure diffusion does not survive the stricter 2026-05-25 mechanism specification and should not be treated as a core mechanism.
- Design is now frozen: external `ext_any` is the headline AIActive definition; text-history AIActive is robustness; DDD is placebo / robustness.
- A 300-event specificity validation sample and human/LLM coding template are included.
- An independent agent-coded 300-event specificity validation file is included for cross-coder comparison; it should be treated as one coder's labels, not final ground truth.

## What We Want From Web Models

Ask for a referee-style critique, not a rewrite. The most valuable output is:

- whether the design can plausibly support an AJG/ABS 3 submission;
- which identification threat remains most damaging;
- whether the current result should be framed as a conditional peer-revaluation paper;
- what additional tests are strictly necessary before drafting;
- what claims should be removed or softened.
