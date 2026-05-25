# Current Research Design

Date: 2026-05-25

## Working Title

Specific Generative AI Disclosure and Product-Market Peer Revaluation: Evidence from Chinese Listed Firms

Chinese working title:

> 生成式 AI 具体化披露与产品市场竞品的资本市场重估

## Core Research Question

When a Chinese listed firm discloses GenAI, large-model, or AIGC information in public investor communication, does the capital market revalue its product-market peers?

More specifically:

> Are more specific GenAI disclosures interpreted as credible competitive-risk signals, leading to more negative short-window revaluation among product-market peers that are already active in the AI competitive space?

## Revised Position After External Review

The project should be written as a **conditional peer-revaluation paper**.

The main result is not:

```text
GenAI disclosure makes all peers fall.
```

The main result is:

```text
Within the same focal GenAI disclosure event,
AI-active close product-market peers are revalued more negatively than non-AI-active peers,
and this relative negative revaluation is stronger when the focal disclosure is more specific.
```

Therefore, the paper's core evidence is a heterogeneity effect, not an average main effect.

## Motivation

Most AI-disclosure studies focus on the disclosing firm itself: whether AI narratives increase focal-firm valuation, attention, liquidity, or later reversal. The current design shifts the endpoint to **competitors**.

The economic idea is that a specific GenAI disclosure may reveal a credible strategic commitment by the focal firm: a concrete product, use case, deployment path, customer segment, partner, or commercialization plan. Such disclosure may not only inform investors about the focal firm; it may also make investors reassess the competitive position of close product-market rivals.

The paper should not claim a simple "focal firm wins, rival loses" business-stealing story. The current evidence does not cleanly support that. The safer mechanism is:

```text
specific GenAI disclosure
    -> credible competitive-risk / strategic-commitment signal
    -> relative negative revaluation of AI-active product-market peers
```

## Unit of Observation

```text
focal GenAI disclosure event e = firm i at date t
× product-market peer firm j
```

The primary sample uses the first GenAI disclosure event for each focal firm and its Top5 product-market peers.

## Main X

The main explanatory object is:

```text
Specificity_z_e × AIActivePeer_j,t-5
```

Where:

- `Specificity_z_e`: standardized textual specificity of the focal GenAI disclosure event.
- `AIActivePeer_j,t-5`: whether peer firm `j` had observable AI/GenAI activity before the focal event, with a five-day buffer to avoid look-ahead.

Product-market similarity is used primarily to define Top5 / Top10 peer samples rather than as the main continuous regressor in every specification.

## Main Y

Primary outcome:

```text
PeerCAR[0,+1]
```

Definition:

- signed market-model abnormal return of peer firm `j`;
- event window `[0,+1]`;
- preferred because the hypothesized mechanism is directional negative revaluation, not generic information content.

Secondary windows:

```text
PeerCAR[-1,+1]
```

Use as robustness rather than headline because `[0,+1]` is cleaner and more stable in current results.

Supplementary market outcomes:

```text
peer abnormal trading value
peer abnormal trading volume
```

These are not main Y. Current turnover/value results are directionally informative but less clean than CAR.

## Peer Definition

Main peer universe:

```text
Top5 product-market peers
```

Constructed from Chinese firm product/business-description text.

Robustness:

- Top10 peers;
- low-similarity same-industry pseudo-peers;
- random same-industry non-Top10 peers;
- AI-word-stripped product similarity, where AI / AIGC / GenAI / ChatGPT / DeepSeek / 大模型 / 生成式人工智能 / 算法 / 智能 / 智慧 and related words are removed before recomputing similarity.

Current AI-word-stripped peer network has high overlap with the original network, but the main result survives after the stripping procedure. This is useful against the objection that "AI firms simply look similar because their business descriptions contain AI words."

## AIActivePeer Definitions

### Main Text-History Definition

```text
current_text_history:
    peer had prior GenAI disclosure before event date t-5
```

This is powerful but has a real pre-window concern.

### External Validation Definition

```text
ext_any:
    prior CAC generative-AI service filing
 OR prior broad-AI patent grant
 OR at least one broad-AI job posting in prior 365 days
```

This is cleaner because it uses behavior outside the focal investor-interaction text system.

Current external evidence scale:

| Evidence source | Scale |
|---|---:|
| CAC A-share lower-bound matched firms | 106 firms |
| AI patent-title matched firms | 101 firms |
| GenAI patent-title matched firms | 28 firms |
| broad-AI hiring firms | 2,814 firms |
| GenAI hiring firms | 1,657 firms |
| post-ChatGPT historical GenAI disclosure firms | 2,771 firms |

Recommended hierarchy:

```text
Main:
    current_text_history, because it is more closely tied to GenAI disclosure history.

Core parallel validation:
    ext_any, because it relies on CAC / patents / hiring and reduces same-text-system concerns.

Expanded validation:
    ext_plus_history, but clearly state that it reintroduces historical disclosure text.
```

The paper should not let text-history AIActivePeer be the only main definition. In the core table sequence, text-history AIActivePeer and external `ext_any` should be shown side by side.

## Baseline Specification

Preferred formulation:

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
two-way clustered by event_id and peer firm
```

Interpretation:

- `event FE` absorbs focal-event-level common shocks: focal firm, event date, market condition, focal disclosure specificity level, and the average market response to the focal event.
- The key coefficient compares AI-active versus non-AI-active peers within the same focal event.
- `peer industry × week FE` absorbs same-week same-industry peer-side shocks.

This is not an IV and not a standard DID. It is a short-window event-study design with within-event cross-sectional identification.

After external review, the headline specification should include pre-window peer CAR controls rather than only adding them later:

```text
preferred headline controls:
    PeerCAR[-10,-2]
    PeerCAR[-20,-2]
```

## Current Main Results

Announcement-cleaned sample means excluding focal-firm and peer-firm major / periodic / earnings / risk announcements around the event.

2026-05-25 final review checks now use pre-window peer CAR controls in the headline columns:

| Sample | AIActive definition | FE | Coef on `Specificity_z × AIActivePeer` | p-value |
|---|---|---|---:|---:|
| Top5, first focal event, CAR[0,+1] | text-history | event FE + peer industry-week FE | -0.002025 | 0.036 |
| Top5, first focal event, CAR[0,+1] | external `ext_any` | event FE + peer industry-week FE | -0.002109 | 0.024 |
| Top5, first focal event, CAR[0,+1] | `ext_plus_history` | event FE + peer industry-week FE | -0.002265 | 0.011 |
| Top10, first focal event, CAR[0,+1] | text-history | event FE + peer industry-week FE | -0.001393 | 0.033 |
| Top10, first focal event, CAR[0,+1] | external `ext_any` | event FE + peer industry-week FE | -0.001573 | 0.010 |
| Top10, first focal event, CAR[0,+1] | `ext_plus_history` | event FE + peer industry-week FE | -0.001529 | 0.011 |

Reading:

```text
The headline result now survives the pre-window CAR concern in both the disclosure-history AIActive definition and the external AIActive definition.
The paper should show text-history and ext_any side by side rather than relying on only one definition.
```

Main result:

| Sample | FE | Coef on `Specificity_z × AIActivePeer` | p-value |
|---|---|---:|---:|
| Top5, first focal event, CAR[0,+1] | event FE | -0.002298 | 0.008 |
| Top5, first focal event, CAR[0,+1] | event FE + peer industry-week FE | -0.002298 | 0.020 |
| Low-similarity placebo | event FE | near zero | > 0.90 |

AI-word-stripped similarity:

| Sample | FE | Coef | p-value |
|---|---|---:|---:|
| AI-word-stripped Top5 | event FE | -0.002124 | 0.011 |
| AI-word-stripped Top5 | event FE + peer industry-week FE | -0.002041 | 0.033 |

Random same-industry placebo:

```text
true Top5 coefficient = -0.002298
100 random same-industry non-Top10 peer draws:
    median coefficient = -0.000055
    5th percentile = -0.001483
    share(random <= true Top5) = 0.00
```

External AIActive validation:

| AIActive definition | Sample | FE | Coef / p-value |
|---|---|---|---|
| `ext_any` | Top5 | event FE | coef = -0.001897, p = 0.028 |
| `ext_any` | Top5 | event FE + peer industry-week FE | coef = -0.001800, p = 0.058 |
| `ext_any` | Top10 | event FE | coef = -0.001654, p = 0.004 |
| `ext_any` | Top10 | event FE + peer industry-week FE | coef = -0.001493, p = 0.014 |
| `ext_any` | low-similarity placebo | event FE | near zero, p = 0.888 |

External AIActive plus AI-word-stripped similarity:

| Sample | FE | Coef / p-value |
|---|---|---|
| AI-word-stripped Top5, `ext_any` | event FE | coef = -0.002118, p = 0.011 |
| AI-word-stripped Top5, `ext_any` | event FE + peer industry-week FE | coef = -0.002321, p = 0.011 |

## Identification Checks

### 1. Formal DDD

Regression includes:

```text
Specificity_z × AIActivePeer × TrueTop5
```

Current results:

| Comparison | FE | Result |
|---|---|---|
| True Top5 vs low-similarity Top5, text-history AIActive | event FE | coef = -0.001542, p = 0.132 |
| True Top5 vs low-similarity Top5, text-history AIActive | strong FE | coef = -0.001115, p = 0.300 |
| True Top5 vs random Top5, text-history AIActive | event FE | coef = -0.002315, p = 0.027 |
| True Top5 vs random Top5, text-history AIActive | strong FE | coef = -0.001904, p = 0.094 |
| True Top5 vs low-similarity Top5, `ext_plus_history` | event FE | coef = -0.002122, p = 0.026 |
| True Top5 vs random Top5, `ext_plus_history` | event FE | coef = -0.001985, p = 0.041 |

Reading:

DDD supports the direction, but it is not uniformly strong. It should be a robustness table, not the headline table.

### 2. Pre-Window Placebo

Text-history AIActivePeer has a real warning sign:

```text
CAR[-10,-2]:
    event FE p = 0.013
    event FE + peer industry-week FE p = 0.043

CAR[-20,-2]:
    event FE p = 0.009
    event FE + peer industry-week FE p = 0.003
```

External `ext_any` does not show the same pre-window problem.

Required response:

```text
include peer pre-window CAR controls in main or core robustness tables.
```

### 3. Pretrend-Adjusted Main Regression

After controlling for peer pre-window CAR:

| AIActive definition | Controls | Strong-FE result |
|---|---|---|
| text-history AIActive | CAR[-10,-2] and CAR[-20,-2] | coef = -0.002025, p = 0.036 |
| external `ext_any` | CAR[-10,-2] and CAR[-20,-2] | coef = -0.002109, p = 0.024 |
| `ext_plus_history` | CAR[-10,-2] and CAR[-20,-2] | coef = -0.002265, p = 0.011 |

Reading:

The pre-window issue weakens the causal claim, but controlling for pre-window CAR does not eliminate the event-window result.

### 4. Focal CAR Sign Decomposition

Results:

| Subsample | Result |
|---|---|
| focal CAR positive | not significant, p = 0.144 / 0.230 |
| focal CAR non-positive | significant, p = 0.024 / 0.048 |
| interaction with focal positive | not significant, p = 0.694 / 0.652 |

Reading:

Do not write a simple business-stealing story. The mechanism should be competitive-risk / strategic-commitment signal, not "focal gains at rivals' expense."

### 5. Investor-Question-Triggered Subsample

| Sample | Result |
|---|---|
| question contains GenAI terms | coef = -0.001837, p = 0.058; strong FE coef = -0.002123, p = 0.050 |
| quick IIP question-triggered sample | coef = -0.002384, p = 0.056; strong FE p = 0.091 |

Reading:

This helps timing because the disclosure is more plausibly triggered by investor questions, but it is not a clean instrument.

### 6. Non-GenAI IIP Pseudo-Event Placebo

Same focal firms, same product-peer network, but non-GenAI investor-interaction events:

```text
2,652 pseudo focal events
14,790 clean event-peer rows
```

Results:

```text
event FE coef = +0.002349, p = 0.358
event FE + peer industry-week FE coef = +0.002284, p = 0.372
```

Reading:

Ordinary non-GenAI investor-interaction specificity does not reproduce the negative GenAI peer-CAR pattern. This is one of the strongest placebo results.

## Mechanism: Peer GenAI Disclosure Diffusion

This is no longer the main Y. It is a mechanism / follow-up response.

Question:

```text
After a focal firm discloses GenAI information,
are closer product-market peers more likely to issue their own GenAI disclosures within 60 / 90 / 180 days?
```

Current CSMAR results:

```text
All focal events, Top10:
30d coef = 0.0041, p = 0.012
60d coef = 0.0060, p = 0.003
90d coef = 0.0061, p = 0.006

First focal event per firm, Top10:
60d coef = 0.0112, p = 0.017
90d coef = 0.0131, p = 0.009
180d coef = 0.0173, p = 0.001

pre-window placebo:
30 / 60 / 90 / 180d not significant
```

But the stricter 2026-05-25 mechanism check does not survive:

```text
Specification:
    first focal events
    focal-event FE
    peer prior 365-day GenAI disclosure-rate control
    X = Specificity_z × product-market similarity

Top5:
    60d p = 0.935
    90d p = 0.622
    180d p = 0.886

Top10:
    60d p = 0.317
    90d p = 0.657
    180d p = 0.555
```

Interpretation:

```text
The earlier diffusion result should be treated as descriptive only.
The current paper should not rely on peer disclosure diffusion as a core mechanism.
It is safer to write the mechanism as capital-market reassessment of competitive risk,
not actual rival follow-up disclosure or real investment.
```

## Data Inputs

Current data sources include:

| Data | Current role |
|---|---|
| CSMAR investor interaction / IIP Q&A | focal GenAI events, questions, replies, pseudo-events |
| Investor relations activity records / Q&A minutes | additional disclosure channel |
| CSMAR announcement data | focal and peer announcement-cleaning flags |
| Stock returns and trading data | PeerCAR, abnormal trading value, abnormal volume |
| Product/business-description text | product-market peer construction |
| CAC GenAI service filings / registrations | external AI-active validation |
| Patent data | AI / GenAI patent validation |
| Hiring data | AI hiring validation |

## Specificity Validation Requirement

This is now the most important remaining measurement task.

Reviewers are likely to ask whether `Specificity_z` is merely:

- disclosure length;
- AI keyword frequency;
- investor attention;
- IR sophistication;
- sentiment;
- readability;
- generic verbosity.

The paper therefore needs a main-text specificity validation table, not only an appendix description.

Suggested validation components:

| Component | Interpretation |
|---|---|
| named product / service | concrete GenAI application rather than generic AI talk |
| named model / platform | identifiable technology object |
| use case | operational setting |
| customer / industry | target market or demand-side specificity |
| partner | external verifiability |
| deployment status | current implementation versus vague plan |
| commercialization / timeline | credible strategic commitment |
| quantitative target | investment, revenue, cost, accuracy, user scale, or time target |

The validation table should report whether the main result survives controls for:

```text
text length
AI keyword count
sentiment / tone
readability
question length or investor-attention proxy
```

## Product-Market Peer Validity Requirement

Top5 peer status must be defended as competitive proximity, not just textual similarity.

Recommended next tests:

```text
Top1-3 peers
Top4-5 peers
Top6-10 peers
low-similarity same-industry peers
random same-industry non-Top10 peers
```

Expected pattern:

```text
negative effect should be strongest for the closest product-market peers
and should attenuate toward low-similarity / random peers.
```

## Main Remaining Risks

1. **Pre-window concern.** Text-history AIActivePeer captures some pre-event negative peer pattern.
2. **Not a strong causal design.** This is a short-window cross-sectional event design, not an exogenous shock.
3. **Mechanism is not simple business stealing.** Focal-CAR sign decomposition does not support a clean "focal up, rival down" story.
4. **AIActive definition.** The main definition is partly text-based; external validation helps but is not uniformly stronger.
5. **Specificity measurement.** Must prove `Specificity_z` is not length, AI keyword frequency, sentiment, readability, or generic IR quality.
6. **Product-market similarity.** Must convince reviewers that Top5 peers represent competitive proximity, not just industry heat.

## Immediate Execution Priorities

| Priority | Task | Reason |
|---:|---|---|
| 1 | Convert `53_v6_final_review_checks_20260525.md` into manuscript-ready tables | The main smoke tests are now complete. |
| 2 | Upgrade specificity validation with sentiment/readability or human/LLM-coded validation sample | Current validation covers obvious observables, but not all text-quality objections. |
| 3 | Put text-history AIActivePeer and external `ext_any` side by side in the first empirical table | This reduces same-text-system and endogenous disclosure-history concerns. |
| 4 | Use Top1-3 / Top4-5 / Top6-10 / low-sim / random as the main product-market validity table | This is the strongest competitive-proximity evidence. |
| 5 | Demote peer GenAI disclosure diffusion to descriptive appendix or drop it from the main paper | The stricter 2026-05-25 mechanism check is null. |

## Safe Current Claim

The safest claim is:

> More specific GenAI disclosures are associated with more negative short-window revaluation among AI-active Top5 product-market peers. The pattern survives announcement cleaning, peer industry-week fixed effects, pre-window CAR controls, AI-word-stripped product similarity, random-peer placebo, non-GenAI pseudo-event placebo, and external AI-active validation. The evidence is best interpreted as market reassessment of competitive risk rather than strong causal proof of business stealing.

## Unsafe Claims to Avoid

Do not claim:

1. GenAI disclosure causally reduces rival firm value.
2. The paper proves business stealing.
3. The pre-window issue is absent.
4. Peer GenAI disclosure diffusion is the main outcome.
5. AI hiring, patents, or CAC filings are current main Y.
