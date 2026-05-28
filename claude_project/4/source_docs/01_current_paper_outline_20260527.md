# Current Paper Outline

Date: 2026-05-27

Working title:

> Specific Generative AI Disclosure and Product-Market Peer Revaluation: Evidence from Chinese Listed Firms

Chinese working title:

> 生成式 AI 具体化披露、竞争威胁信号与产品市场同行重估

## Core Story

The paper should be written as a capital-market revaluation paper, not as a strong causal business-stealing paper.

One-sentence story:

> Specific GenAI disclosures reveal credible strategic commitment. Capital markets use this signal to reassess AI-active product-market peers, generating more negative short-window peer returns for close rivals.

The core result is conditional:

```text
Within the same focal GenAI disclosure event,
AI-active close product-market peers experience more negative PeerCAR[0,+1]
when the focal disclosure is more specific.
```

The core result is not:

```text
GenAI disclosures make all peers fall.
```

## Contribution

1. Peer-side capital-market consequence of GenAI disclosure.
2. Product-market network perspective rather than broad industry reaction.
3. Conditional competitive-risk signal: the negative effect appears among AI-active close peers.
4. Disclosure specificity as a strategic-commitment signal, not merely AI keyword volume.
5. Boundary evidence distinguishing competitive-risk signals from AI category validation.

## Main Variables

Main X:

```text
Specificity_z_e × AIActivePeer_{j,t-5}
```

Main Y:

```text
Peer market-model CAR[0,+1]
```

Main sample:

```text
first focal GenAI disclosure event × Top5 product-market peers
```

Main AIActive definition:

```text
ext_any =
    prior CAC filing
 OR prior broad-AI patent grant
 OR prior broad-AI hiring in the previous 365 days
```

Core robustness AIActive:

```text
current_text_history =
    prior GenAI disclosure before event date t-5
```

Main fixed effects:

```text
event FE + peer industry-week FE
```

Inference:

```text
two-way clustered by event_id and peer_code
```

## Theory and Hypotheses

### Mechanism

GenAI disclosures can have two competing interpretations.

Category validation:

```text
specific or supply-chain-oriented GenAI disclosure validates AI demand
=> peers may benefit
```

Competitive-risk signal:

```text
specific GenAI disclosure reveals focal firm's credible strategic commitment
=> AI-active close rivals are negatively revalued
```

Specificity makes the second interpretation more likely because concrete products, deployment status, use cases, customers, partners, commercialization paths, and timelines are harder to dismiss as generic hype.

### H1: Conditional Peer Revaluation

More specific focal GenAI disclosures are associated with more negative short-window CARs for AI-active Top5 product-market peers.

### H2: Product-Market Proximity

The negative revaluation should be strongest among the closest product-market peers and should attenuate among weaker product-market neighbors, low-similarity peers, and random same-industry peers.

### H3: External AI-Activeness

The result should hold when AI-active peers are identified using pre-event external evidence, not only historical disclosure text.

### H4: Boundary Between Competitive Risk and Category Validation

Supply-chain exposure disclosures should not generate the same negative AI-active peer revaluation. They may instead reflect AI demand validation.

## Empirical Design

Baseline specification:

```text
PeerCAR_{e,j,[0,+1]}
  = beta_1 AIActivePeer_{j,t-5}
  + beta_2 Specificity_z_e × AIActivePeer_{j,t-5}
  + Controls
  + EventFE_e
  + PeerIndustryWeekFE_{j,t}
  + error_{e,j}
```

Core controls:

```text
PeerCAR[-10,-2] + PeerCAR[-20,-2]
```

Identification interpretation:

Event fixed effects absorb focal-event-level information. The coefficient is identified from within-event differences between AI-active and non-AI-active peers.

## Table and Figure Plan

### Table 1: Sample Construction and Summary Statistics

Show:

- focal GenAI event counts;
- event-peer rows;
- Top5 / Top10 / low-similarity / random peer samples;
- Specificity_z distribution;
- AIActivePeer coverage;
- disclosure type counts.

Use current counts:

```text
Top5 clean sample:
    N = 7,805
    events = 2,177
    peer firms = 3,345

Disclosure type events:
    own_impl = 1,526
    supply_chain = 301
    generic_attention = 214
    denial_no_current = 251
```

### Table 2: Main Peer-CAR Result

Headline sample:

```text
first focal GenAI event × Top5 peers
announcement-cleaned
PeerCAR[0,+1]
event FE + peer industry-week FE
pre-window peer CAR controls
```

Columns:

1. `ext_any` headline.
2. `current_text_history` robustness.
3. Top10 `ext_any`.
4. Top10 `current_text_history`.
5. optional no-prewindow baseline for comparison only.

Current strongest focused result:

```text
ext_any:
    coef = -0.002303, p = 0.020

current_text_history:
    coef = -0.002275, p = 0.027
```

### Table 3: Text-Measure Robustness

Purpose:

Show that `Specificity_z` is not only length, AI keyword volume, sentiment, source attention, or generic verbosity.

Include:

- answer and question length controls;
- AI keyword intensity controls;
- source / attention controls;
- numeric-detail controls;
- main regression with all observable text controls.

### Figure 1: Window Lead/Lag

Use:

```text
results/v7_event_time_peer_validity_20260527/window_lead_lag_coefficients.png
```

Interpretation:

- `ext_any` does not show the long pre-window concern observed in text-history AIActive.
- `[0,+1]` is the economically relevant short-window outcome.
- Daily event-time decomposition is transparency evidence only; single-day coefficients are underpowered.

### Table 4 / Figure 2: Product-Market Peer Validity

Use:

```text
results/v7_event_time_peer_validity_20260527/proximity_gradient_coefficients.png
results/v7_event_time_peer_validity_20260527/product_market_peer_validity_summary.csv
```

Evidence:

```text
Top1-3, ext_any:
    coef = -0.003252, p = 0.016

Top6-10:
    not significant

low-similarity peers:
    not significant

random same-industry peers:
    not significant
```

Peer validity summary:

```text
mean product similarity:
    Top1-3 = 0.255
    Top4-5 = 0.206
    Top6-10 = 0.180
    random same-industry = 0.055
    low-similarity = 0.006
```

This table supports the claim that Top5 is a product-market peer set rather than a generic same-industry set.

### Table 5: Focal Good-News and Pre-Trend Robustness

Use:

```text
docs/empirical_runs/54_v6_focal_good_news_pretrend_checks_20260525.md
```

Columns:

1. baseline with pre-window peer CAR controls;
2. add FocalCAR[0,+1];
3. add FocalCAR[0,+1] × AIActive;
4. residualized PeerCAR[0,+1] on PeerCAR[-10,-2];
5. residualized outcome plus focal-good-news controls.

Current result:

```text
ext_any:
    residualized Y + FocalCAR × AIActive
    coef = -0.002300, p = 0.020
```

### Table 6: Placebo and Alternative Peer Definitions

Include:

- low-similarity peers;
- random same-industry non-Top10 peers;
- non-GenAI pseudo-events;
- AI-word-stripped product similarity;
- Top10 robustness.

Expected pattern:

```text
effect appears in true product-market peers
effect does not appear in low-similarity/random peers
effect does not appear in non-GenAI pseudo-events
```

### Table 7: Disclosure-Type Horse-Race and Boundary

Use:

```text
docs/empirical_runs/59_v7_disclosure_type_horserace_20260527.md
```

Disclosure types:

- own GenAI implementation/deployment/product/application;
- AI supply-chain exposure;
- generic AI attention;
- denial/no-current-involvement.

Main horse-race finding:

```text
Adding Type × AIActive interactions does not absorb the original result.

ext_any:
    Specificity_z × AIActive
    coef = -0.002394, p = 0.015

current_text_history:
    coef = -0.002107, p = 0.045
```

Boundary result:

```text
Supply-chain disclosure has positive average peer effect without event FE:
    coef = 0.004225, p = 0.026

But supply_chain × AIActive is not negative or significant.
```

Interpretation:

Supply-chain disclosure is category validation, not the competitive-risk mechanism.

### Table 8: External AIActive Breakdown

Use:

- prior CAC;
- prior AI patent grants;
- prior AI hiring;
- `ext_any`;
- `ext_strict`;
- `ext_plus_history`.

Purpose:

Show that the result does not depend solely on historical GenAI disclosure text.

### Appendix Table: Peer Disclosure Diffusion

Keep as descriptive follow-up only.

Current status:

```text
After focal-event FE and peer baseline GenAI-disclosure-rate controls,
peer follow-up GenAI disclosure response is not robust.
```

Do not use this as the main mechanism.

### Appendix Table: AI Supply-Chain DID

Use:

```text
docs/empirical_runs/58_v7_ai_supply_chain_stacked_did_20260527.md
```

Interpretation:

The DID version is null, so AI supply-chain disclosure should not become the new main design.

## Introduction Structure

Paragraph 1:

GenAI disclosures are widespread but noisy. The market must distinguish generic AI talk from credible strategic commitments.

Paragraph 2:

Prior work mostly examines the disclosing firm's own valuation, attention, or liquidity. This misses product-market externalities.

Paragraph 3:

Specific GenAI disclosure can carry competitive information. Concrete claims about products, deployment, customers, partners, and commercialization may reveal focal-firm strategic commitment.

Paragraph 4:

The sign for peers is ambiguous: category validation can benefit peers, while competitive-risk reassessment can harm close AI-active peers.

Paragraph 5:

Research design: focal GenAI disclosure event × product-market peer panel, Top5 peers, PeerCAR[0,+1], event FE, peer industry-week FE, pre-window controls, two-way clustering.

Paragraph 6:

Main findings: negative conditional peer revaluation for AI-active Top5 peers; strongest among Top1-3; absent among low-sim/random peers; robust to external AIActive, announcement cleaning, focal-good-news controls, pre-trend adjustment, and non-GenAI pseudo-events.

Paragraph 7:

Boundary: supply-chain GenAI disclosures show positive average peer reaction but no competitive-risk pattern, consistent with category validation.

Paragraph 8:

Contributions.

## Writing Boundaries

Do not claim:

- GenAI disclosure causally destroys rival value.
- This is direct evidence of realized business stealing.
- Peer disclosure diffusion is a strong mechanism.
- AI supply-chain disclosure DID is a supported main design.

Claim:

- The evidence is consistent with capital markets interpreting specific GenAI disclosures as competitive-risk signals for AI-active close product-market peers.
- The result is a short-window peer-side revaluation effect.
- Category validation and competitive risk coexist; specificity helps identify the competitive-risk side.
