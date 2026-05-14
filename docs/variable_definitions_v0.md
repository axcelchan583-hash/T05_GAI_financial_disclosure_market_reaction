# Variable Definitions v0

## Treatment and Exposure

### TreatedGenAIAnnouncement

Firm-level treatment indicator equal to one for firms with at least one manually verified specific GenAI initiative announcement during the sample period.

The announcement must describe a specific GenAI action, not just a generic AI narrative. Candidate valid actions:

- adoption of GenAI tools for internal workflow, office productivity, knowledge management, content generation, customer service, or R&D support;
- integration of large language models or other GenAI tools into products or services;
- deployment of a firm-built GenAI platform, assistant, model application, or knowledge-base system;
- explicit cooperation with a GenAI platform provider for business process or product integration.

Exclude or separately tag:

- broad "AI+" or digital-transformation slogans without a concrete GenAI initiative;
- traditional AI, machine learning, computer vision, industrial internet, or smart manufacturing without GenAI;
- media commentary about GenAI that does not involve the firm adopting or deploying it;
- announcements made only by unrelated subsidiaries if the listed firm connection is unclear.

### FirstGenAIAnnouncementDate

The first public date on which a listed firm announces a specific GenAI initiative.

Possible source hierarchy:

- exchange announcements and listed-company filings;
- CNINFO announcements;
- official company news releases or official WeChat posts;
- major business-news wires, if the firm and event date can be verified;
- investor-relations Q&A only as a weaker source, separately flagged.

If the announcement is on a non-trading day or after market close, keep the original calendar date and also build an adjusted next-trading-day date for event-study outcomes.

Related event-library flag:

```text
FirstSpecificGenAIAnnouncement = 1
```

for the retained first specific GenAI initiative per firm. Later specific GenAI announcements by the same firm can be kept for descriptive checks but should not define the main treatment timing.

### PostFirstGenAIAnnouncement

Firm-year post indicator equal to one for fiscal-year disclosure observations whose annual-report drafting and disclosure window occurs after the firm's first specific GenAI announcement.

For annual-report outcomes, the conservative rule should consider both the fiscal year and the report disclosure date:

- if the GenAI announcement occurs before the annual report is drafted or disclosed, `PostFirstGenAIAnnouncement = 1`;
- if it occurs after the annual report disclosure date, keep that report as pre-treatment;
- if timing is ambiguous, flag the observation and test a conservative exclusion.

### AnnouncementMechanismClass

Manual category describing how close the GenAI initiative is to disclosure-writing production.

Candidate categories:

- `workflow_internal`: internal office, knowledge management, productivity, document work, compliance, or management process use;
- `content_generation`: text, image, customer-service, marketing, document, or knowledge-base generation;
- `product_integration`: GenAI embedded into products or services sold to customers;
- `rd_platform`: model, software, algorithm, or platform R&D;
- `generic_strategy`: generic AI or GenAI strategy language with limited mechanism clarity;
- `invalid_or_traditional_ai`: not a usable GenAI treatment.

`workflow_internal` and `content_generation` are the closest mechanism classes for GAI-assisted disclosure writing. `product_integration` can be retained for a broad adoption sample but should be separated in mechanism and heterogeneity tests.

### PostGenAI

Candidate definitions:

- `PostGenAI = 1` for fiscal-year reports whose drafting window is plausibly after public GenAI access.
- Conservative China A-share definition: 2023 annual reports and later.
- Transition definition: treat 2022 annual reports as ambiguous and exclude them in the main specification.

Reason: ChatGPT was released on 2022-11-30, but A-share annual reports are drafted and disclosed after fiscal year-end, so 2022 reports may partly overlap the shock.

This is now a fallback or auxiliary public-shock variable. The preferred main design uses `TreatedGenAIAnnouncement * PostFirstGenAIAnnouncement`.

### RiskSectionGAIWritingScore

The score should measure writing patterns consistent with generative-AI assistance in the annual-report risk-disclosure section.

Do not rely on a single black-box AI detector as the sole measure. Candidate construction:

- compare original risk-disclosure paragraphs with LLM-rewritten paragraphs;
- train or calibrate a classifier on Chinese disclosure text;
- focus on new text after removing repeated prior-year boilerplate;
- compute scores inside risk sections first, then optionally compare MD&A and other sections;
- validate by manual review on a stratified paragraph sample.

### PreRiskWritingBurden

Pre-period firm-level exposure to GenAI-assisted risk-disclosure writing.

Candidate measures:

- average pre-2023 risk-disclosure length;
- average pre-2023 risk-category breadth;
- average pre-2023 risk-disclosure annual modification burden;
- average pre-2023 risk-section complexity or low-readability score;
- number of business segments;
- number of subsidiaries or geographic segments;
- debt, guarantee, litigation, supply-chain, or cash-flow risk exposure before the GenAI shock;
- pre-period analyst coverage;
- investor-relations resource proxy if available;
- history of long or complex risk disclosures.

Avoid defining `PreRiskWritingBurden` with the same post-treatment ingredients used in the primary outcome. The exposure should be measured in pre-period years only, preferably 2018-2021 or 2019-2021.

Current status: useful as fallback DID exposure, matching covariate, or heterogeneity variable. It should not override the announcement-event treatment if a clean event library can be built.

### PreAITechCapability

Pre-period AI or digital technical capability.

This is not the main treatment because pre-2023 AI technology foundations are not equivalent to GenAI-assisted disclosure writing. Use it as a moderator or heterogeneity variable.

Candidate measures:

- pre-2023 AI patent or AI knowledge-network score;
- pre-2023 AI-related invention patents;
- pre-2023 digital-technology capability;
- pre-2023 software or data-processing capability if available.

Main use:

```text
PostGenAI * PreRiskWritingBurden * PreAITechCapability
```

Interpretation: firms with stronger pre-existing AI or digital foundations may be more able to absorb the GenAI writing shock.

## Outcomes

### Verifiable Risk Disclosure Specificity

Primary disclosure-quality outcome.

The outcome should capture whether risk disclosure becomes more concrete, verifiable, and non-boilerplate rather than merely longer or more fluent.

Candidate components:

- numeric information: amounts, percentages, dates, maturities, quantities;
- entity-specific information: customers, suppliers, banks, creditors, guarantors, litigation parties;
- risk-category coverage: financing, cash flow, credit, supply chain, technology, policy, legal, compliance, overseas;
- concrete mitigation actions: monitoring, control, adjustment, reserve, optimization, insurance, legal response;
- lower generic-boilerplate intensity;
- lower lagged text similarity or higher annual modification when risk conditions change.

Possible labels:

- `risk_specificity_index`;
- `risk_verifiability_index`;
- `verifiable_risk_specificity_index`;
- `risk_similarity_lag` as an inverse boilerplate or repetition diagnostic.

### Analyst Forecast Dispersion

Secondary information-uncertainty outcome. Measure around annual-report disclosure dates or fiscal-year forecast windows.

### Price Delay

Secondary price-efficiency outcome. Use a standard price-delay construction if daily return data are available.

### Forecast Error

Secondary outcome. Useful only when analyst forecasts are sufficiently frequent.

### Market Reaction

Short-window CAR around annual-report announcement dates can be used as a secondary outcome, not the main outcome, because the sign of reaction is theoretically ambiguous.

### Post-Disclosure Reversal

Useful for the credibility-discount channel. If smooth GAI-assisted disclosure temporarily misleads investors, stronger later reversal should appear.

## Controls

Baseline controls should include:

- firm size;
- book-to-market;
- leverage;
- ROA;
- loss indicator;
- growth;
- stock turnover;
- institutional ownership if available;
- analyst coverage;
- audit quality;
- industry-year controls.

## Fixed Effects

Baseline:

```text
firm FE + year FE
```

Preferred extensions:

```text
firm FE + industry-year FE
```

or

```text
firm FE + province-year FE
```

depending on the final sample and shock definition.
