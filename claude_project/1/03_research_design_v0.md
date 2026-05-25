# Research Design v0

## OPEN QUESTIONS

1. Whether an A-share firm-level event library of first specific GenAI initiatives can be constructed with enough treated firms.
2. Whether the announcement screen can cleanly separate specific GenAI adoption/integration/workflow use from generic AI or digital-transformation slogans.
3. Whether `TreatedGenAIAnnouncement * PostFirstGenAIAnnouncement` has a strong first stage for risk-section GAI-writing scores.
4. Whether China A-share 2025 annual reports can provide enough post-announcement disclosure observations beyond 2023-2024 reports.
5. Whether a Chinese annual-report GAI-writing score can be validated without relying on a single generic AI detector.
6. Whether the primary outcome should be the broad risk-specificity index or the narrower verifiable-risk-specificity index.

## Baseline Framing

The paper asks whether generative AI changes the production of financial disclosure text and thereby changes the specificity and verifiability of corporate risk disclosure.

This is different from three adjacent topics:

- Corporate AI capability: whether the firm uses AI in its operations.
- AI disclosure: whether the firm talks about AI in filings.
- AI washing: whether AI narratives are unsupported by real capability.

Here, the focal variable is disclosure-writing production: annual reports or other financial disclosure texts contain writing patterns consistent with generative-AI assistance.

## Core Mechanisms

### Writing-Cost Channel

GAI-assisted writing may reduce the cost of drafting detailed risk disclosure. Firms with heavier pre-period risk-disclosure writing burdens should benefit more from the GenAI shock.

Expected outcomes:

- higher verifiable risk-disclosure specificity;
- more numeric, entity-specific, and risk-category-specific content;
- lower boilerplate intensity;
- lower year-to-year repetition when risk conditions change.

### Polished-Boilerplate Channel

GAI-assisted writing may make risk disclosure smoother without adding hard information. If this channel dominates, disclosure may become more fluent but not more specific or verifiable.

Expected outcomes:

- higher GAI-writing scores with no increase in verifiable specificity;
- longer or more polished risk text without more numeric/entity-specific information;
- higher template similarity or weaker annual modification;
- possible later inquiry-letter or reversal evidence in risky firms.

## Preferred Main Design

### Event-based DID from Specific GenAI Announcements

Because GenAI is a common-time shock, a simple post-treatment DID is weak. The current preferred design is an event-based DID around each firm's first specific GenAI initiative announcement:

```text
RiskSpecificity_it
= beta * TreatedGenAIAnnouncement_i * PostFirstGenAIAnnouncement_it
+ controls + firm FE + industry-year FE + eps_it
```

The treatment event should be the first public announcement that the firm is actually adopting, integrating, deploying, or building around GenAI. Generic statements such as "embracing AI", traditional AI projects, smart manufacturing without GenAI, or broad digital-transformation slogans should not define treatment.

This route is more defensible than a pure continuous exposure because the second difference is no longer an inferred pre-period writing burden. It is a concrete firm-level event with observable timing.

### Data-processing Template from GenAI-announcement Literature

The local reference paper is:

```text
/Users/mac/computerscience/23选题探索/bib/AI文本文献/The Impact of Generative AI Announcements on Suppliers_ Evidence From the Stock Market.pdf
```

The useful lesson is its event-sample discipline:

1. Start with a broad GenAI keyword search.
2. Keep only listed firms with traceable public announcements.
3. Manually review each hit and retain only specific GenAI initiatives.
4. Keep each firm's first GenAI initiative during the sample window.
5. Align non-trading-day or after-hours announcements to the next trading day when event timing matters.
6. Drop observations with overlapping firm events or major confounding announcements when estimating short-window market outcomes.
7. Use matched untreated firms or event-based DID only after the event sample is clean.

For this project, the event library should classify each retained announcement into:

- internal workflow or office/productivity use;
- content generation, knowledge-base, customer-service, or disclosure-adjacent use;
- product/service integration;
- R&D or software platform launch;
- generic strategy language.

The first two categories are closest to the disclosure-writing mechanism. Product-only GenAI announcements may still be useful as broad firm-level GenAI adoption, but they should be separately tagged.

### Fallback Difference-in-exposure DID

The older branch remains useful as a fallback or robustness design:

```text
RiskSpecificity_it
= beta * PostGenAI_t * PreRiskWritingBurden_i
+ controls + firm FE + year FE / industry-year FE + eps_it
```

`PreRiskWritingBurden_i` must be measured before the GenAI shock. The main interpretation is not that all firms suddenly use GenAI, but that the writing-cost reduction matters more for firms whose risk disclosure was costly to prepare before GenAI became available.

Possible measures:

- pre-2023 risk-disclosure length;
- pre-2023 risk-category breadth;
- pre-2023 risk-disclosure annual modification burden;
- pre-2023 risk-section complexity or low readability;
- business-segment complexity;
- foreign business exposure;
- subsidiaries or geographic segments;
- pre-period debt, guarantee, litigation, supply-chain, or cash-flow risk exposure;
- low investor-relations resources;
- low analyst coverage.

### Role of Pre-period AI Technical Capability

Pre-period AI technical capability is not the main treatment because old AI patents, machine-learning capability, or knowledge-network AI scores do not directly measure GenAI-assisted annual-report writing.

It should be used as a moderator or heterogeneity variable:

```text
RiskSpecificity_it
= beta1 * PostGenAI_t * PreRiskWritingBurden_i
+ beta2 * PostGenAI_t * PreRiskWritingBurden_i * PreAITechCapability_i
+ controls + firm FE + year FE / industry-year FE + eps_it
```

The intended interpretation of `beta2` is absorptive capacity: whether firms with stronger pre-existing AI or digital foundations are more able to translate the GenAI shock into disclosure-writing changes.

## Necessary First Stage

Before interpreting the disclosure-quality outcome as a GenAI-assisted-writing effect, the project must show:

```text
TreatedGenAIAnnouncement_i * PostFirstGenAIAnnouncement_it
-> higher risk-section GAI-writing score
```

For the fallback public-shock exposure design, the analogous first stage is:

```text
PostGenAI_t * PreRiskWritingBurden_i -> higher risk-section GAI-writing score
```

Without a first stage, the DID would only be a generic post-2023 or post-announcement risk-disclosure design, not a GAI-assisted-disclosure-writing design.

## Outcome Priority

Preferred primary outcomes:

1. Verifiable risk-disclosure specificity.
2. Risk-disclosure modification or non-boilerplate intensity.

Secondary outcomes:

- analyst forecast dispersion;
- forecast error;
- price delay;
- bid-ask spread;
- abnormal turnover;
- annual-report announcement-window CAR;
- post-disclosure drift or reversal;
- annual-report inquiry-letter probability.

## Current Bottom Line

This topic is feasible only if the text-measurement pilot and first-stage pass. The empirical contribution should not be sold as "AI writes annual reports and markets react." The current stronger version is:

> Firms that publicly initiate specific GenAI applications may incorporate GenAI into disclosure-writing production. The paper tests whether this shift changes the specificity, verifiability, and boilerplate intensity of subsequent risk disclosure.

The previous `PostGenAI * PreRiskWritingBurden` design remains a fallback. It is not the preferred main story unless the specific-announcement event library is too small or cannot pass first-stage validation.
