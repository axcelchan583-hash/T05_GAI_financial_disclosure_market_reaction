# Proposed Paper Outline

Date: 2026-05-25

Working title:

> Specific Generative AI Disclosure and Product-Market Peer Revaluation: Evidence from Chinese Listed Firms

## Abstract Logic

The abstract should avoid overclaiming causality.

Suggested structure:

1. State the question: whether GenAI disclosures affect not only disclosing firms but also their product-market peers.
2. State the setting: Chinese listed firms' GenAI / large-model / AIGC disclosures in investor-interaction and related communication channels.
3. State the design: focal disclosure event × product-market peer panel, Top5 product peers, peer CAR `[0,+1]`, event fixed effects, peer industry-week fixed effects, two-way clustered standard errors.
4. State the main finding as a conditional peer effect: within the same focal event, more specific GenAI disclosures are associated with more negative CAR among pre-event AI-active product-market peers relative to non-AI-active peers.
5. State identification support: announcement cleaning, low-similarity and random peer placebos, AI-word-stripped similarity, external AI-active validation, pre-window CAR controls, non-GenAI pseudo-events.
6. State interpretation: capital markets treat specific GenAI disclosures as competitive-risk signals.

## 1. Introduction

### Opening

GenAI disclosures are not only firm-level narratives. They may also reshape investors' beliefs about competitive positions in product markets.

### Gap

Existing AI / GenAI disclosure studies mainly ask:

- does the focal firm benefit from AI narratives?
- are AI narratives credible or speculative?
- how do investors react to AI attention?

This paper asks:

> What happens to the product-market peers of the disclosing firm?

### Contribution

The contribution should be framed as:

1. **Peer-side capital-market consequence of GenAI disclosure.**
2. **Product-market network perspective rather than industry-average peer response.**
3. **Competitive-risk interpretation conditional on peer AI activeness.**
4. **Chinese investor-interaction setting with rich disclosure timing and text.**

### Conservative Boundary

Say clearly:

```text
We interpret the results as short-window market reassessment of competitive risk,
not as definitive causal evidence that GenAI disclosures destroy rival value.
```

## 2. Institutional Background

### 2.1 Chinese Investor-Interaction Platforms

Cover:

- exchange-run investor interaction;
- questions and firm replies;
- date-stamped disclosure environment;
- why this channel is useful for GenAI disclosures.

### 2.2 GenAI Disclosure Wave in China

Cover:

- ChatGPT / large-model / AIGC shock;
- Chinese listed firms' incentives to respond to investor questions;
- why specificity matters: concrete products, deployment, partners, use cases, customers, commercialization.

### 2.3 Product-Market Competition

Cover:

- why focal firm GenAI commitments can affect close peers;
- why Top5 product-market peers are better than broad industries.

## 3. Theory and Hypotheses

### Core Mechanism

Specific GenAI disclosure can reveal:

- strategic commitment;
- credible capability;
- a product or commercialization route;
- likely competitive pressure on close rivals.

However, the sign is theoretically ambiguous:

```text
category validation effect:
    specific GenAI disclosure validates the whole AI category -> peers may rise.

competitive-risk effect:
    specific GenAI disclosure reveals stronger focal commitment -> close AI-active peers may fall.
```

The paper's empirical prediction is that the competitive-risk effect dominates for AI-active product-market peers.

This is a heterogeneity prediction, not an average peer-effect prediction.

### H1: AI-Active Peer Revaluation

More specific focal GenAI disclosures are associated with more negative short-window CARs for AI-active product-market peers.

Empirical object:

```text
Specificity_z × AIActivePeer -> PeerCAR[0,+1] < 0
```

within Top5 product-market peer samples.

### H2: Product-Market Proximity

The negative revaluation should be concentrated among close product-market peers and should not appear among low-similarity or random same-industry peers.

### H3: External AI-Activeness

The effect should remain directionally similar when AI-active peers are identified using pre-event external evidence such as CAC filings, AI patent grants, and AI hiring.

### H4: Peer Disclosure Diffusion as Mechanism

After focal GenAI disclosures, close product-market peers are more likely to issue follow-up GenAI disclosures within 60 / 90 / 180 days.

This is a mechanism / response test, not the main outcome.

## 4. Data and Measurement

### 4.1 Focal GenAI Disclosure Events

Describe:

- event sources: investor interaction, IR activity records, Q&A minutes, related disclosure channels;
- GenAI keyword / classifier procedure;
- first event per focal firm as preferred sample.

### 4.2 Disclosure Specificity

Describe dimensions:

- concrete product or service;
- named model / platform;
- application scenario;
- customer / industry segment;
- partner;
- deployment status;
- quantitative target / investment / timeline.

Need validation:

- raw length control;
- human-coded or LLM-coded validation sample;
- distinction from generic AI word frequency.

This validation should be in the main paper. It should not be left only to an appendix.

### 4.3 Product-Market Peers

Describe:

- Chinese business-description text;
- cosine similarity;
- Top5 / Top10 peers;
- low-similarity pseudo-peers;
- random same-industry non-Top10 peers;
- AI-word-stripped similarity robustness.

### 4.4 AIActivePeer

Main:

```text
prior GenAI disclosure before t-5
```

External validation:

```text
prior CAC filing
prior AI patent grant
prior broad-AI hiring in prior 365 days
```

Core table policy:

```text
Report text-history AIActivePeer and external ext_any side by side.
```

### 4.5 Market Outcomes

Main:

```text
market-model PeerCAR[0,+1]
```

Supplementary:

```text
PeerCAR[-1,+1]
abnormal trading value
abnormal trading volume
```

### 4.6 Announcement Cleaning

Describe the cleaning procedure:

- CSMAR announcement basic table;
- announcement-security relation table;
- announcement-category relation table;
- exclude focal and peer days with major / periodic / earnings / risk announcements.

## 5. Research Design

### Main Specification

```text
PeerCAR_{e,j,[0,+1]}
  = beta_1 AIActivePeer_{j,t-5}
  + beta_2 Specificity_z_e × AIActivePeer_{j,t-5}
  + event FE_e
  + peer industry × week FE
  + pre-window peer CAR controls
  + error_{e,j}
```

Standard errors:

```text
clustered by event_id and peer firm
```

### Interpretation of Event FE

Event fixed effects absorb all focal-event-level shocks. The estimate is identified from cross-peer differences within the same focal event.

### Preferred Table Hierarchy

1. Announcement-cleaned headline sample.
2. Event FE and peer industry-week FE.
3. Pre-window peer CAR controls included in core columns.
4. Text-history AIActivePeer and external `ext_any` shown side by side.
5. Focal-firm good-news controls and pre-trend-adjusted outcome.
6. Product-market proximity gradient and placebo peers.

## 6. Main Results

### Table 1: Sample Construction and Variable Summary

Show:

- number of focal events;
- number of event-peer rows;
- Top5 / Top10 / low-sim / random samples;
- distribution of specificity;
- AIActivePeer coverage.

### Table 2: Main Peer CAR Result

Headline:

```text
Top5, first focal event, announcement-cleaned, PeerCAR[0,+1].
```

Columns:

1. event FE;
2. event FE + peer industry-week FE;
3. event FE + peer industry-week FE + pre-window peer CAR controls;
4. same headline controls with external `ext_any` AIActivePeer;
5. Top10 robustness with the same headline controls.

### Table 2B: Focal Good-News and Pre-Trend Robustness

Purpose:

```text
show that Specificity_z × AIActivePeer is not merely capturing
focal-firm own good news or continuation of peer pre-window returns.
```

Columns:

1. baseline with `PeerCAR[-10,-2]` and `PeerCAR[-20,-2]`;
2. add `FocalCAR[0,+1]`;
3. add `FocalCAR[0,+1] × AIActivePeer`;
4. residualize `PeerCAR[0,+1]` on `PeerCAR[-10,-2]`;
5. residualized outcome plus `FocalCAR[0,+1] × AIActivePeer`.

Current focused robustness result:

```text
Top5 / announcement-cleaned / event FE + peer industry-week FE:

text-history:
    baseline coef = -0.002275, p = 0.027
    + FocalCAR × AIActive coef = -0.002283, p = 0.027
    residualized Y + FocalCAR × AIActive coef = -0.002281, p = 0.026

external ext_any:
    baseline coef = -0.002303, p = 0.020
    + FocalCAR × AIActive coef = -0.002307, p = 0.020
    residualized Y + FocalCAR × AIActive coef = -0.002300, p = 0.020
```

### Table 3: Specificity Validation

This table should show that `Specificity_z` is not simply:

- text length;
- AI keyword count;
- sentiment / tone;
- readability;
- investor-question length;
- generic IR verbosity.

Suggested rows / panels:

- correlation between `Specificity_z` and component labels;
- human / LLM validation sample;
- component-level specificity: product, model, use case, customer, partner, deployment, commercialization, quantitative target;
- main regression with length / AI keyword / sentiment / readability controls.

### Table 4: Product-Market Proximity and Placebo Peers

Columns:

- Top1-3;
- Top4-5;
- Top6-10;
- low-similarity same-industry peers;
- random same-industry peers;
- formal DDD `Specificity × AIActive × TrueTop5`.

Expected pattern:

```text
The negative peer-CAR effect should attenuate as product-market proximity weakens.
```

### Table 5: AI-Word-Stripped Similarity

Show that the result survives after removing AI-related words from product descriptions before peer construction.

### Table 6: External AIActive Validation

Use:

- `ext_any`;
- `ext_strict`;
- `ext_plus_history` as expanded validation;
- single-source components only as appendix.

This table should be close to the main table, not buried late, because it addresses same-text-system concerns.

### Table 7: Non-GenAI Pseudo-Event Placebo

Same focal firms and same product-peer network, but ordinary non-GenAI IIP replies.

Expected result:

```text
null
```

### Table 8: Question-Triggered Subsample

Restrict to cases where investor question contains GenAI terms or where firm reply is quick.

Purpose:

```text
reduce concern that firm fully chooses disclosure timing.
```

## 7. Mechanism and Boundary Tests

### Mechanism: Peer GenAI Disclosure Diffusion

Y:

```text
peer follow-up GenAI disclosure within 60 / 90 / 180 days
```

Early smoke-test result:

```text
Top10 first-event sample:
60d p = 0.017
90d p = 0.009
180d p = 0.001
pre-window placebo is null
```

Stricter 2026-05-25 result:

```text
After adding focal-event FE and peer prior 365-day GenAI disclosure-rate controls,
Top5 / Top10 60d, 90d, and 180d response tests are not significant.
```

Interpretation:

Peer disclosure diffusion should be kept, at most, as descriptive follow-up evidence. It should not carry the paper's mechanism claim.

### Boundary: Focal CAR Sign Decomposition

Current result does not support simple business stealing:

- focal positive subsample: not significant;
- focal non-positive subsample: significant;
- interaction with focal positive: not significant.

This should be used to justify the conservative "competitive-risk signal" framing.

### Supplementary Market Response

Use abnormal trading value / volume as auxiliary evidence only.

## 8. Robustness and Validity Checks

Required robustness:

1. announcement-cleaned sample;
2. peer industry-week fixed effects;
3. two-way clustering by event and peer firm;
4. pre-window peer CAR controls;
5. low-similarity placebo;
6. random same-industry placebo;
7. AI-word-stripped similarity;
8. external AIActivePeer;
9. non-GenAI pseudo-events;
10. question-triggered subsample;
11. Top10 peer sample;
12. alternative CAR windows;
13. specificity validation against length, AI keyword frequency, sentiment, and readability;
14. product-market proximity gradient;
15. focal-firm good-news controls: `FocalCAR[0,+1]` and `FocalCAR[0,+1] × AIActivePeer`;
16. pre-trend-adjusted outcome residualized on `PeerCAR[-10,-2]`.

## 9. Discussion

Discuss:

- why AI-active peers are negatively revalued;
- why the effect is not generic industry hype;
- why the result should be interpreted as capital-market reassessment rather than proven real business stealing;
- why peer disclosure diffusion is only weak/descriptive rather than a confirmed strategic-response mechanism.

## 10. Conclusion

Conclusion should be modest:

> Specific GenAI disclosures have spillover implications for product-market peers. Capital markets appear to treat these disclosures as competitive-risk signals when evaluating peers already exposed to the AI competitive space.

## Appendix Plan

Appendix A: keyword and classification procedure.

Appendix B: specificity coding validation.

Appendix C: product similarity construction and AI-word-stripped variant.

Appendix D: AIActivePeer construction and external evidence matching.

Appendix E: announcement-cleaning procedure.

Appendix F: additional CAR windows and trading outcomes.

Appendix G: full placebo and DDD results.

## Writing Boundaries

Do not write:

- "GenAI disclosure causes rival value losses."
- "This is direct evidence of business stealing."
- "Peer disclosure diffusion is the main outcome."
- "AI hiring / patent / CAC filings are the main Y."

Write:

- "specific GenAI disclosures are interpreted as competitive-risk signals";
- "negative revaluation is concentrated among AI-active product-market peers";
- "the result is not reproduced by non-GenAI pseudo-events, low-similarity peers, or random peers";
- "the evidence is robust to pre-window peer CAR controls, focal-firm good-news controls, pre-trend-adjusted outcomes, and external AI-active validation."
