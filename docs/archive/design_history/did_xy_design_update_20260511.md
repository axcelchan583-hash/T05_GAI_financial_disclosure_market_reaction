# DID X-Y Design Update

Date: 2026-05-11

## 2026-05-11 Later Update: Main X Re-centered

After revisiting the supplier GenAI-announcement paper, the preferred DID route is no longer the continuous `PostGenAI * PreRiskWritingBurden` design as the main story.

The better main X is:

```text
TreatedGenAIAnnouncement_i * PostFirstGenAIAnnouncement_it
```

where `TreatedGenAIAnnouncement_i` identifies firms with a manually verified first specific GenAI initiative, and `PostFirstGenAIAnnouncement_it` turns on after that firm's first specific GenAI announcement.

This solves the earlier "second D is fuzzy" problem better than an inferred continuous exposure. The comparison becomes firms with specific observable GenAI adoption events versus matched firms without such events, before and after the treated firm's first event.

The old design should be retained as fallback or robustness:

```text
PostGenAI_t * PreRiskWritingBurden_i
```

The old design is still conceptually meaningful, but it is harder to sell because `PreRiskWritingBurden` is continuous and does not create a clean treated/control split by itself.

## Current Preferred X and Y

### Main X

```text
TreatedGenAIAnnouncement_i * PostFirstGenAIAnnouncement_it
```

This is an event-based DID. The treatment is the firm's first specific GenAI initiative announcement, not a generic AI capability score or a raw AI-text detector score.

Valid treatment announcements should involve specific GenAI adoption, integration, deployment, internal workflow use, content generation, knowledge-base use, customer-service GenAI, or GenAI product/service integration. Generic AI slogans, traditional AI, smart manufacturing without GenAI, and broad digital-transformation rhetoric should be excluded or separately tagged.

This is cleaner than using a raw AI-text detector score as the main X, because the detector score and the risk-specificity outcome would both be constructed from the same risk-disclosure text. It is also cleaner than relying only on pre-period writing burden because the treatment timing is observable.

### Main Y

```text
Verifiable Risk Disclosure Specificity_it
```

The outcome should measure whether risk disclosure becomes more concrete and verifiable, not merely longer or more polished.

Core components:

- numeric information: amounts, percentages, dates, maturities, quantities;
- entity-specific information: customers, suppliers, banks, creditors, guarantors, litigation parties;
- risk-category coverage: financing, cash flow, credit, supply chain, technology, policy, legal, compliance, overseas;
- concrete mitigation actions;
- lower generic boilerplate;
- lower lagged similarity or higher meaningful annual modification.

## Baseline DID Specification

```text
VerifiableRiskSpecificity_it
= beta * TreatedGenAIAnnouncement_i * PostFirstGenAIAnnouncement_it
+ controls + firm FE + industry-year FE + eps_it
```

Use matched control firms or never-announcing firms as the comparison group. Matching variables should include pre-period size, leverage, ROA, growth, market-to-book, industry, and pre-period risk-disclosure characteristics.

The fallback exposure DID remains:

```text
VerifiableRiskSpecificity_it
= beta * PostGenAI_t * PreRiskWritingBurden_i
+ controls + firm FE + year FE / industry-year FE + eps_it
```

`PreRiskWritingBurden_i` should be measured before GenAI using a window such as 2018-2021 or 2019-2021 if this fallback is used.

## Necessary First Stage

```text
RiskSectionGAIWritingScore_it
= pi * TreatedGenAIAnnouncement_i * PostFirstGenAIAnnouncement_it
+ controls + firm FE + industry-year FE + eps_it
```

This first stage is required. Without it, the design can only support a generic post-announcement risk-disclosure interpretation, not a GenAI-assisted-writing interpretation.

Fallback first stage:

```text
RiskSectionGAIWritingScore_it
= pi * PostGenAI_t * PreRiskWritingBurden_i
+ controls + firm FE + year FE / industry-year FE + eps_it
```

## Role of Pre-period AI Technical Capability

Pre-period AI technical capability is not the main X. A firm may have AI patents or old machine-learning capabilities before 2023 without using GenAI to write annual-report risk disclosure.

Use it as moderation or heterogeneity:

```text
VerifiableRiskSpecificity_it
= beta1 * PostGenAI_t * PreRiskWritingBurden_i
+ beta2 * PostGenAI_t * PreRiskWritingBurden_i * PreAITechCapability_i
+ controls + firm FE + year FE / industry-year FE + eps_it
```

Interpretation of `beta2`: whether firms with stronger pre-existing AI or digital foundations are better able to absorb the GenAI writing shock.

## Do Not Use as Main X

### Enterprise Weibo AI-generation rate

Short public-relations posts are too short and too stylistically standardized for stable AI-writing detection. They are also distant from annual-report risk-disclosure production.

Possible use: auxiliary first-stage or external validation at the firm-year corpus level, not the main treatment.

### Raw risk-section GAI-writing score

This can be used as first-stage evidence or mechanism evidence, but not as the main X, because it is extracted from the same disclosure text used to build the Y.

### Hand-coded high-risk industry binary

The hand-coded `HighRiskDiscIndustry_i` validation failed: it barely differs from the low-risk group in pre-period risk-disclosure length and has near-zero correlation with continuous pre-period risk burden. It should not be used as the main second D.

### Data-driven high pre-risk-burden binary

The within-industry top-versus-bottom-tercile burden split is better than the hand-coded industry binary, but it remains a coarsened exposure design, not direct evidence of GenAI adoption. It can be a robustness contrast after the announcement-event route is built.

## Current One-sentence Framing

Firms with specific GenAI initiative announcements provide an observable treatment timing for GenAI adoption; the paper tests whether subsequent risk disclosure becomes more verifiable, more specific, or more boilerplate-like after that adoption.
