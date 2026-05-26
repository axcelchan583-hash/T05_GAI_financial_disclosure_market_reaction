# Handoff - Specificity Validation Coding (claude_opus_coder)

## What's here
- `specificity_validation_codes_partial_SV0001-0160_20260526.csv`
  The 300-row coding template. Rows SV0001–SV0160 are CODED (coder_id, coding_date,
  8 components, specificity_score_0_4, uncertain_flag, evidence_snippet, coder_notes).
  Rows SV0161–SV0300 are BLANK and need coding.
- `coding_guidelines.md`
  The exact decision rules used for rows 1–160. Read first; follow to keep 161–300 consistent.

## Prompt to give Claude Code
"Read coding_guidelines.md. It defines how rows SV0001–SV0160 were coded in
specificity_validation_codes_partial_SV0001-0160_20260526.csv. Continue coding rows
SV0161–SV0300 in the same file, reading each sample_answer and judging by hand —
do NOT keyword-match, do NOT consult agent1 codes while coding. Keep the same
columns and SV order. Save the completed 300-row coder2 file as
validation_sample/claude_coding/claude_manual_codes_300_20260526.csv and write a
short summary as validation_sample/claude_coding/claude_manual_codes_300_20260526_summary.md.
Do not compute agreement yet unless an agent1 file is explicitly provided later."

## Coded-so-far distribution (SV0001–SV0160, sanity reference)
- score 0–4: {0:106, 1:24, 2:15, 3:10, 4:5}   (~66% zeros)
- uncertain_flag=1: 10
- component 1-counts: product 18, model 20, use_case 39, customer 9, partner 4,
  deploy 26, commercialization 0, quantitative 0
  (commercialization & quantitative were genuinely absent in these 160 — expect a few in 161–300)

## Note for the paper
This is one independent coder's labels, to be compared against agent1 — not ground
truth. The high zero rate is driven by the strict GenAI-vs-AI boundary (rule #1 in
guidelines): rich but non-generative AI disclosures are coded 0. That boundary is the
main axis on which coders may disagree, so it's worth checking agent1 applied it the
same way before computing final kappa.
