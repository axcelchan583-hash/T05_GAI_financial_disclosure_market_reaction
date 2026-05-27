# Design Freeze

Date: 2026-05-25

Purpose: freeze the main empirical design before drafting. This file should be treated as the controlling design document unless a later version explicitly supersedes it.

## Paper Identity

Working title:

> Specific Generative AI Disclosure and Product-Market Peer Revaluation: Evidence from Chinese Listed Firms

The paper is a capital-market peer-revaluation paper. It is not a hiring-response paper, not a CAC-filing paper, and not a same-platform peer-disclosure diffusion paper.

## Research Question

Do more specific focal-firm GenAI disclosures lead capital markets to revalue AI-active close product-market peers more negatively in short event windows?

Conservative interpretation:

```text
Specific GenAI disclosure acts as a credible competitive-risk / strategic-commitment signal.
The evidence is short-window market reassessment, not proof of real business stealing.
```

## Headline Sample

Freeze the headline sample as:

```text
Event source:
    merged investor communication event library
    = CSMAR investor interaction + CSMAR investor-relations Q&A

Focal event:
    first conservative GenAI firm-day disclosure per focal firm

Event period:
    2023 onward in the current CSMAR event library
    baseline starts with the post-ChatGPT China GenAI disclosure wave

Peer universe:
    Top5 product-market peers

Cleaning:
    announcement-cleaned sample
    exclude focal-firm and peer-firm major / periodic / earnings / price-risk announcement windows

Outcome:
    signed market-model PeerCAR[0,+1]
```

The current focused headline sample has:

```text
N = 7,805 event-peer observations
events = 2,177
peer firms = 3,345
```

## Main Variables

### Main X

```text
Specificity_z_e × AIActivePeer_j,t-5
```

`Specificity_z_e` is the standardized focal-event GenAI disclosure specificity measure.

`AIActivePeer_j,t-5` is the peer firm's pre-event AI activeness measured with a five-day buffer.

### Main AIActive Definition

Use external `ext_any` as the main AIActive definition:

```text
ext_any = 1 if peer firm j has any of the following before t-5:
    prior CAC generative-AI service filing
 OR prior broad-AI patent grant
 OR at least one broad-AI job posting in the prior 365 days
```

Reason:

```text
ext_any is less exposed to same-text-system concerns than disclosure-history AIActive.
It uses regulatory, patent, and hiring evidence rather than only investor-communication text.
It remains significant in the latest focused robustness checks.
```

### Robustness AIActive Definition

Use `current_text_history` as robustness / extension:

```text
current_text_history = 1 if peer firm j had prior GenAI disclosure before t-5
```

Reason:

```text
This definition is theoretically close to GenAI disclosure history and has strong power,
but it has a more serious pre-window concern and should not be the only main definition.
```

## Headline Specification

Table 2 headline specification:

```text
PeerCAR_{e,j,[0,+1]}
  = beta_1 AIActivePeer_{j,t-5}
  + beta_2 Specificity_z_e × AIActivePeer_{j,t-5}
  + event FE_e
  + peer industry × week FE
  + PeerCAR_{j,[-10,-2]}
  + PeerCAR_{j,[-20,-2]}
  + error_{e,j}
```

Standard errors:

```text
two-way clustered by event_id and peer_code
```

Identification:

```text
event FE absorbs focal-firm identity, focal event date, focal-event information level,
specificity main effect, market-wide shocks, and the average response to the focal event.
The key coefficient compares AI-active peers to non-AI-active peers within the same focal event.
```

## Table 2 Policy

Table 2 should use:

```text
main AIActive = ext_any
headline sample = first focal event × Top5 peers
outcome = PeerCAR[0,+1]
FE = event FE + peer industry-week FE
controls = PeerCAR[-10,-2] and PeerCAR[-20,-2]
cluster = event_id × peer_code
```

`current_text_history` should appear next to or immediately after the main columns as robustness, not as the headline definition.

## Robustness Hierarchy

### Core Robustness

These must be in the main paper or near-main appendix:

1. `current_text_history` AIActive.
2. Top10 product-market peers.
3. AI-word-stripped product similarity.
4. low-similarity same-industry placebo peers.
5. random same-industry non-Top10 placebo peers.
6. non-GenAI investor-interaction pseudo-events.
7. focal-firm good-news controls: `FocalCAR[0,+1]` and `FocalCAR[0,+1] × AIActivePeer`.
8. pre-trend-adjusted outcome residualized on `PeerCAR[-10,-2]`.
9. alternative window `PeerCAR[-1,+1]`.
10. source split: IIP-only and IR-QA-only, if sample size permits.

### DDD Status

The DDD specification:

```text
Specificity_z × AIActivePeer × TrueTop5
```

is a robustness / placebo design, not the headline specification.

Reason:

```text
The paper's theory is within-event conditional peer revaluation.
DDD is useful to show that the effect is concentrated in true product-market peers rather than placebo peers,
but it is less direct as the main abstract-level estimand.
```

### Mechanism Status

Peer GenAI disclosure diffusion is descriptive follow-up evidence only.

Do not use it as the main Y or as a strong mechanism because the stricter 2026-05-25 version is null after focal-event FE and peer prior disclosure-rate controls.

### External Real-Action Evidence

Future CAC filings, AI patents, AI hiring, and product-launch disclosures should be used for:

```text
specificity construct validation
convergent / predictive validity
```

They are not the main outcome of this paper.

## Theory Anchor

The paper should anchor the hypothesis in voluntary disclosure under proprietary costs and peer competitive information transfer.

Recommended theoretical structure:

```text
specific disclosure can have two opposing peer-market implications:

category validation:
    focal disclosure validates the GenAI opportunity space;
    peers may be revalued upward.

competitive-risk signal:
    focal disclosure reveals credible strategic commitment;
    close AI-active product-market peers face more negative relative revaluation.
```

The hypothesis is that the competitive-risk channel dominates among close product-market peers already active in the AI competitive space.

Candidate literature anchors to verify and cite:

- Verrecchia (1983): discretionary disclosure and proprietary costs.
- Bagnoli and Watts (2010): disclosure in strategic settings with rivals.
- product-market peer and competitive information-transfer literature.
- GenAI / AI disclosure and focal-firm market reaction literature for positioning, not as the main theory.

## Claims Allowed

Allowed:

```text
More specific focal GenAI disclosures are associated with more negative short-window revaluation
among AI-active close product-market peers.

The evidence is consistent with investors interpreting specific GenAI disclosure as a competitive-risk signal.
```

Not allowed:

```text
GenAI disclosure causally destroys rival firm value.
This proves real business stealing.
Peer disclosure diffusion is the paper's main mechanism.
CAC / patents / hiring are the paper's main Y.
```

## Frozen Decision Summary

| Decision | Frozen choice |
|---|---|
| Main Y | signed market-model `PeerCAR[0,+1]` |
| Main sample | first focal GenAI event × Top5 product-market peers |
| Main AIActive | external `ext_any` |
| Robustness AIActive | `current_text_history` |
| Headline FE | event FE + peer industry-week FE |
| Headline controls | `PeerCAR[-10,-2]`, `PeerCAR[-20,-2]` |
| Inference | two-way clustered by `event_id` and `peer_code` |
| DDD | robustness / placebo |
| peer disclosure diffusion | descriptive follow-up only |
| future CAC / patent / hiring | specificity validation only |
