# Prompt for Claude / ChatGPT Pro Deep Review

Please review the attached research design and empirical-result files as a critical referee or senior empirical accounting/finance scholar.

The project studies Chinese A-share listed firms. The core question is whether more specific focal-firm GenAI / large-model / AIGC disclosures are interpreted by the capital market as competitive-risk signals, leading to more negative short-window revaluation of close product-market peers that were already AI-active before the focal event.

Please do not treat this as a strong causal paper. The intended paper is a capital-market revaluation paper with within-event cross-sectional identification.

## Files to Read First

1. `01_PROJECT_BRIEF_EN.md`
2. `source_docs/03_current_research_design_20260525.md`
3. `source_docs/07_final_review_checks_20260525.md`
4. `source_docs/08_focal_good_news_pretrend_checks_20260525.md`

Use the CSV files only if you need to inspect the exact rows behind the summarized results.

## Main Design

Unit:

```text
focal GenAI disclosure event e = firm i at date t
× product-market peer firm j
```

Main outcome:

```text
PeerCAR[0,+1]
```

Main regressor:

```text
Specificity_z_e × AIActivePeer_j,t-5
```

Preferred specification:

```text
PeerCAR_{e,j,[0,+1]}
  = beta_1 AIActivePeer_{j,t-5}
  + beta_2 Specificity_z_e × AIActivePeer_{j,t-5}
  + event FE_e
  + peer industry × week FE
  + peer pre-window CAR controls
  + error_{e,j}
```

Standard errors are two-way clustered by focal event and peer firm.

## What I Need From You

Please provide a structured assessment with the following sections.

### 1. Verdict

Give a clear go / revise / no-go judgment. State whether the current design is realistically publishable at:

- AJG/ABS 2 outlets;
- AJG/ABS 3 outlets;
- AJG/ABS 4 or higher outlets.

Be explicit about the ceiling and why.

### 2. Contribution

Evaluate whether the contribution is sufficiently distinct from existing AI disclosure, GenAI event-study, peer information-transfer, and product-market competition papers.

Please identify the closest published papers and explain how this project should position against them.

### 3. Identification

Evaluate the identification strategy:

- event fixed effects;
- peer industry-week fixed effects;
- two-way clustering;
- announcement cleaning;
- pre-window CAR controls;
- text-history AIActive versus external `ext_any`;
- product-market proximity gradient;
- low-similarity and random peer placebos;
- non-GenAI pseudo-event placebo.
- focal-firm good-news controls;
- pre-trend-adjusted outcome residualized on `PeerCAR[-10,-2]`.

Which remaining threat is most damaging?

### 4. Measurement

Assess the validity of:

- disclosure specificity;
- AIActivePeer;
- product-market peer definition;
- signed PeerCAR[0,+1].

What additional validation is strictly necessary before drafting?

### 5. Mechanism

The stricter peer-disclosure diffusion test is null. Should the paper:

- drop peer disclosure diffusion entirely;
- keep it only as descriptive evidence;
- replace it with another mechanism test;
- avoid mechanism claims and write the paper as market reassessment only?

### 6. Main Tables

Propose the final empirical table sequence for a manuscript. Please state which tables belong in the main text and which should be moved to the appendix.

### 7. Claims

Write:

- the strongest defensible abstract-level claim;
- the safest empirical conclusion;
- claims that should be explicitly avoided.

### 8. Additional Tests

List the 5-8 most important additional tests, ranked by necessity. Do not list generic robustness checks unless they directly address a real threat in this design.

### 9. Publication Strategy

Recommend target outlets and framing:

- finance/accounting field journal;
- China-focused outlet;
- management/strategy outlet;
- short-paper outlet.

State which target is realistic only if additional tests pass.

## Important Constraints

Please be critical and concrete. Do not simply praise the design.

Do not invent results that are not in the files. If a claim is unsupported, say so.

Do not recommend reframing the paper around hiring, patents, CAC filings, or peer disclosure diffusion as the main outcome unless you explain why that would be superior to the current PeerCAR design.

Please distinguish:

- evidence currently shown;
- evidence that is suggestive but weak;
- evidence that must be added before submission.
