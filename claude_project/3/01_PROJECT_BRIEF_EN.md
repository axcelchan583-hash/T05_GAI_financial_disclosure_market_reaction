# Project Brief for External Review

## Working Title

Specific Generative AI Disclosure and Product-Market Peer Revaluation: Evidence from Chinese Listed Firms

## Research Question

Do specific focal-firm GenAI disclosures act as competitive-risk signals that lead investors to revalue close product-market peers more negatively, especially peers that were already active in the AI competitive space before the focal disclosure?

The project is not intended to claim that GenAI disclosure causally destroys rival value. The intended interpretation is a short-window capital-market reassessment of competitive risk.

## Setting

The setting is Chinese A-share listed firms. Focal events are public GenAI / large-model / AIGC disclosures drawn from investor-interaction and investor-relations text sources. Peer firms are product-market peers identified from Chinese business-description text, with Top5 peers as the headline sample.

## Unit of Observation

```text
focal GenAI disclosure event e = firm i at date t
× product-market peer firm j
```

The headline sample uses each focal firm's first GenAI disclosure event and its Top5 product-market peers.

## Main Variables

### Main X

```text
Specificity_z_e × AIActivePeer_j,t-5
```

`Specificity_z_e` is a standardized focal-event GenAI disclosure specificity measure.

`AIActivePeer_j,t-5` indicates whether the peer had observable AI/GenAI activity before the focal event with a five-day buffer.

The paper currently uses two core AIActive definitions:

```text
current_text_history:
    peer had prior GenAI disclosure before event date t-5

ext_any:
    prior CAC generative-AI service filing
 OR prior broad-AI patent grant
 OR at least one broad-AI job posting in the prior 365 days
```

### Main Y

```text
PeerCAR[0,+1]
```

This is the signed market-model abnormal return for peer firm j over the focal disclosure date and the following trading day.

## Baseline Specification

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

The identification comes from within-event cross-sectional variation across AI-active versus non-AI-active peers. Event fixed effects absorb focal-event-level shocks, focal firm identity, event date, market conditions, and the focal disclosure's own average market impact.

This is not an IV, not a clean natural experiment, and not a standard DID. It is a short-window event-study design with within-event cross-sectional identification.

## Headline Results From the 2026-05-25 Final Checks

Announcement-cleaned sample, first focal events, market-model `PeerCAR[0,+1]`, event FE + peer industry-week FE, and pre-window peer CAR controls:

| Sample | AIActive definition | Coef on `Specificity_z × AIActivePeer` | p-value |
|---|---|---:|---:|
| Top5 | current text-history AIActive | -0.002025 | 0.036 |
| Top5 | external `ext_any` | -0.002109 | 0.024 |
| Top5 | `ext_plus_history` | -0.002265 | 0.011 |
| Top10 | current text-history AIActive | -0.001393 | 0.033 |
| Top10 | external `ext_any` | -0.001573 | 0.010 |
| Top10 | `ext_plus_history` | -0.001529 | 0.011 |

Economic interpretation: a one-standard-deviation increase in focal disclosure specificity is associated with roughly 20 basis points more negative two-day abnormal returns for AI-active close peers relative to non-AI-active peers within the same focal event.

## Specificity Validation

The main result survives controls for:

- answer length and investor question length;
- AI keyword intensity and GenAI token intensity;
- source count and answer-level event count;
- numeric detail and component-count proxies;
- all observable text controls together.

Under the external `ext_any` AIActive definition, the full observable text-controls specification remains significant:

```text
coef = -0.002246, p = 0.021
```

Under text-history AIActive, the full observable text-controls specification remains directionally stable but becomes marginal:

```text
coef = -0.001824, p = 0.071
```

## Focused Good-News and Pre-Trend Robustness

The latest focused robustness checks use the current headline sample and specification:

```text
Top5 product-market peers
first focal GenAI event
announcement-cleaned sample
PeerCAR[0,+1]
event FE + peer industry-week FE
two-way clustering by event_id and peer_code
N = 7,805
events = 2,177
peer firms = 3,345
```

### Focal-Firm Own Good-News Controls

The coefficient on `Specificity_z × AIActivePeer` remains stable after adding `FocalCAR[0,+1]` and `FocalCAR[0,+1] × AIActivePeer`:

| AIActive definition | Baseline coef | Baseline p | + FocalCAR × AIActive coef | p |
|---|---:|---:|---:|---:|
| current text-history AIActive | -0.002275 | 0.027 | -0.002283 | 0.027 |
| external `ext_any` | -0.002303 | 0.020 | -0.002307 | 0.020 |

`FocalCAR[0,+1]` itself is event-level and therefore absorbed by event fixed effects. The relevant incremental control is the interaction with AIActivePeer.

### Pre-Trend-Adjusted Outcome

The result also survives when `PeerCAR[0,+1]` is residualized on `PeerCAR[-10,-2]`:

| AIActive definition | Residualized-Y baseline coef | p | Residualized-Y + FocalCAR × AIActive coef | p |
|---|---:|---:|---:|---:|
| current text-history AIActive | -0.002274 | 0.027 | -0.002281 | 0.026 |
| external `ext_any` | -0.002295 | 0.021 | -0.002300 | 0.020 |

## Product-Market Proximity Evidence

The result is concentrated in the closest product-market peers:

| Peer group | AIActive definition | Coef | p-value |
|---|---|---:|---:|
| True Top1-3 | current text-history | -0.002472 | 0.076 |
| True Top1-3 | external `ext_any` | -0.003252 | 0.016 |
| True Top6-10 | current text-history | -0.001092 | 0.305 |
| True Top6-10 | external `ext_any` | -0.001010 | 0.298 |
| Low-similarity Top5 placebo | current text-history | -0.000131 | 0.896 |
| Low-similarity Top5 placebo | external `ext_any` | -0.000136 | 0.892 |
| Random same-industry Top5 placebo | current text-history | 0.000704 | 0.421 |
| Random same-industry Top5 placebo | external `ext_any` | -0.000990 | 0.265 |

## Lead/Lag Evidence and Pre-Window Concern

Text-history AIActive has longer pre-window concerns:

```text
CAR[-20,-11]: coef = -0.004816, p = 0.024
CAR[-10,-2]:  coef = -0.004847, p = 0.043
CAR[-5,-2]:   coef = -0.001197, p = 0.501
```

External `ext_any` does not show the same pre-window pattern:

```text
CAR[-20,-11]: p = 0.390
CAR[-10,-2]:  p = 0.973
CAR[-5,-2]:   p = 0.870
```

Therefore, the paper should show text-history AIActive and external `ext_any` side by side and include pre-window CAR controls in the headline specification.

## External AIActive Breakdown

External evidence is useful but uneven:

- `prior_ai_patent_grant` supports the main direction strongly.
- `prior_broad_ai_hiring_365_ge1` supports the main direction, especially Top10.
- `ext_any` supports the main direction.
- `prior_cac` is too sparse/noisy as a standalone moderator.
- `ext_strict` is not stable enough as a standalone main definition.

## Mechanism Result

The stricter peer-disclosure diffusion test is null.

Specification:

```text
Outcome:
    peer first follow-up GenAI disclosure within 60 / 90 / 180 days
X:
    Specificity_z × product-market similarity
Controls:
    peer prior 365-day GenAI disclosure rate
FE:
    focal-event FE
```

Results:

```text
Top5:
    60d p = 0.935
    90d p = 0.622
    180d p = 0.886

Top10:
    60d p = 0.317
    90d p = 0.657
    180d p = 0.555
```

This means peer disclosure diffusion should not be used as a core mechanism claim. It can be mentioned only as descriptive or exploratory evidence from earlier smoke tests.

## Current Safe Claim

More specific focal-firm GenAI disclosures are associated with more negative short-window market revaluation among AI-active close product-market peers. The evidence is consistent with investors interpreting specific GenAI disclosure as a credible competitive-risk signal.

## Unsafe Claims To Avoid

Do not claim:

1. GenAI disclosure causally reduces rival firm value.
2. The design proves business stealing.
3. There is no pre-window concern.
4. Peer GenAI disclosure diffusion is a strong mechanism.
5. CAC filings, patents, or hiring are the main outcomes.
6. The result is a clean natural experiment.

## Key Review Questions

1. Is this design sufficient for an AJG/ABS 3 finance/accounting/management field journal if framed as conditional capital-market peer revaluation rather than strong causality?
2. Which remaining identification threat is most damaging?
3. Should text-history AIActive or external `ext_any` be the primary AIActive definition?
4. Does the product-market proximity gradient sufficiently support the competitive-risk interpretation?
5. What additional specificity-validation evidence is essential before drafting?
6. Should peer-disclosure diffusion be dropped entirely from the main paper?
7. What would be the most defensible abstract-level claim?
