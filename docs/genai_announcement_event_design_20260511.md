# GenAI Announcement Event Design

Date: 2026-05-11

## Why This Update

The current bottleneck is the second difference in the DID. `PostGenAI` is only a common time shock. A continuous or coarsened pre-period writing-burden exposure can work as a difference-in-exposure design, but it is hard to explain as a clean treated-versus-control contrast.

The better route is to construct a firm-level event library of specific GenAI initiative announcements. Then the main treatment becomes:

```text
TreatedGenAIAnnouncement_i * PostFirstGenAIAnnouncement_it
```

This gives the design an observable firm-level treatment event instead of only an inferred exposure.

## Paper to Learn From

Local PDF:

```text
/Users/mac/computerscience/23选题探索/bib/AI文本文献/The Impact of Generative AI Announcements on Suppliers_ Evidence From the Stock Market.pdf
```

The paper's most useful contribution for this project is not the supplier channel itself. It is the event-sample construction:

- broad GenAI keyword search;
- manual review of announcement text;
- keep only specific GenAI initiatives;
- keep each firm's first GenAI initiative;
- exclude generic references to GenAI plus other information technologies;
- align event dates for market-event timing;
- remove overlapping or confounded events when the outcome is short-window stock reaction;
- use matched controls and event-based DID as robustness.

## Treatment Definition for T05

### Valid Treatment

An announcement is treatment-valid if it publicly states that the listed firm has started, adopted, integrated, deployed, or built a specific GenAI initiative.

Valid examples:

- adopting a large-language-model tool for internal workflow, office work, compliance work, knowledge management, or document processing;
- using GenAI for content generation, customer service, marketing copy, report drafting, knowledge-base generation, or intelligent Q&A;
- integrating GenAI into a product or service;
- launching a firm-specific GenAI assistant, platform, model application, or industry model;
- entering a concrete partnership with a GenAI provider to deploy a GenAI application.

### Invalid or Weak Treatment

Exclude from the main treated sample:

- generic "AI empowerment", "AI+", "digital transformation", or "embracing GenAI" language without a concrete initiative;
- traditional AI, machine learning, computer vision, industrial internet, or smart manufacturing without GenAI;
- industry commentary or policy interpretation that does not describe the firm's own adoption;
- pure investor-relations replies with no verifiable public project, unless separately flagged as weak evidence;
- subsidiary-only announcements where the listed-firm connection is not clear.

## Manual Coding Fields

Minimum event-library fields:

```text
stock_code
firm_name
announcement_date_raw
announcement_date_adjusted
source_type
source_url_or_file
announcement_title
genai_keywords_hit
is_specific_genai_initiative
first_specific_genai_announcement
mechanism_class
specificity_score
review_note
```

`mechanism_class` should use:

- `workflow_internal`
- `content_generation`
- `product_integration`
- `rd_platform`
- `generic_strategy`
- `invalid_or_traditional_ai`

`workflow_internal` and `content_generation` are closest to the disclosure-writing mechanism.

## Baseline DID

Main annual-report panel:

```text
VerifiableRiskSpecificity_it
= beta * TreatedGenAIAnnouncement_i * PostFirstGenAIAnnouncement_it
+ controls + firm FE + industry-year FE + eps_it
```

For firms without specific GenAI announcements, `PostFirstGenAIAnnouncement` can be set using matched treated-firm event timing in a matched-panel design, or implemented through a staggered DID/event-study estimator that compares not-yet-treated and never-treated firms.

## First Stage

The necessary first-stage test is:

```text
RiskSectionGAIWritingScore_it
= pi * TreatedGenAIAnnouncement_i * PostFirstGenAIAnnouncement_it
+ controls + firm FE + industry-year FE + eps_it
```

If this does not pass, the paper cannot claim that the announcement treatment changed disclosure writing through GenAI-assisted writing. The result would only be a post-GenAI-announcement disclosure-style change.

## Relationship to Old Exposure Designs

### `PostGenAI * PreRiskWritingBurden`

Keep as fallback or robustness. It is still useful because it captures where GenAI writing-cost reductions should matter most. But it is not as clean as an observed firm-level treatment event.

### Hand-coded Industry Binary

Do not use as a main X. The 2026-05-11 validation failed: the high-risk industries did not have meaningfully higher pre-period risk-disclosure length than low-risk industries.

### Data-driven High Pre-risk-burden Binary

This is better than the hand-coded industry binary but remains a coarsened exposure contrast. Use it only after acknowledging that it does not directly measure GenAI adoption.

## Outcome Hierarchy

Main Y:

```text
Verifiable Risk Disclosure Specificity
```

This should remain the primary disclosure-quality outcome only if it can be anchored by prior literature, manual validation, or external verification. Otherwise, mark it as a constructed disclosure-mechanism variable.

Secondary outcomes:

- annual-report inquiry letters;
- analyst forecast dispersion or forecast error;
- price delay or information efficiency;
- bid-ask spread or liquidity;
- short-window annual-report market reaction.

These secondary outcomes should not be the first selling point because adjacent GenAI disclosure papers have already covered many market-reaction, spread, and analyst-forecast outcomes.

## Immediate Build Plan

1. Create a broad GenAI keyword list in Chinese and English.
2. Search listed-firm announcements, CNINFO filings, official company news, and official WeChat posts.
3. Build a raw hit table with firm, date, title, source, and text snippet.
4. Manually code specific versus generic announcements.
5. Keep the first specific GenAI initiative per firm.
6. Merge event timing into the annual-report panel.
7. Run the first-stage check before treating any disclosure-outcome result as a GenAI-writing effect.
