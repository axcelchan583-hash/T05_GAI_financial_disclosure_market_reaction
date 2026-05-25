# v6 Identification-Strengthening Checks

Date: 2026-05-24

## Purpose

This file records five identification checks requested after the current v6 peer-CAR result:

1. formal DDD: true Top5 product peers versus placebo peers;
2. pre-window placebo;
3. focal-firm CAR sign decomposition;
4. investor-question-triggered subsample;
5. non-GenAI investor-interaction pseudo-event placebo.

I also add a pretrend-adjusted main regression because the pre-window test exposes a real weakness in the current text-history AIActivePeer definition.

Scripts:

```text
scripts/run_v6_identification_strengthening_checks_20260524.py
scripts/run_v6_pretrend_adjusted_main_20260524.py
```

Outputs:

```text
results/v6_identification_strengthening_20260524/formal_ddd_results.csv
results/v6_identification_strengthening_20260524/prewindow_placebo_results.csv
results/v6_identification_strengthening_20260524/focal_car_sign_results.csv
results/v6_identification_strengthening_20260524/passive_question_results.csv
results/v6_identification_strengthening_20260524/non_genai_placebo_results.csv
results/v6_identification_strengthening_20260524/pretrend_adjusted_main_results.csv
```

## 1. Formal DDD

Specification:

```text
PeerCAR_{e,j,[0,+1]}
  = beta × Specificity_e × AIActive_j × TrueTop5_{e,j}
  + lower-order terms
  + event FE
  + optional peer industry × week FE
  + error
```

The control peer group is either low-similarity same-industry peers or one random same-industry Top5 set.

### Key results

```text
True Top5 vs low-similarity Top5, current text-history AIActive:
event FE: coef = -0.001542, p = 0.132
event FE + peer industry-week FE: coef = -0.001115, p = 0.300

True Top5 vs random Top5, current text-history AIActive:
event FE: coef = -0.002315, p = 0.027
event FE + peer industry-week FE: coef = -0.001904, p = 0.094

True Top5 vs low-similarity Top5, ext_plus_history:
event FE: coef = -0.002122, p = 0.026
event FE + peer industry-week FE: coef = -0.001737, p = 0.080

True Top5 vs random Top5, ext_plus_history:
event FE: coef = -0.001985, p = 0.041
event FE + peer industry-week FE: coef = -0.001871, p = 0.077
```

### Reading

DDD supports the direction, but it is not uniformly strong. The result is better against random peers than against low-similarity same-industry peers. This means the DDD table can be used as a robustness table, but it is not yet strong enough to become the headline identification table.

## 2. Pre-Window Placebo

Outcomes:

```text
peer_car_pre10_m2_mm = market-model CAR[-10,-2]
peer_car_pre20_m2_mm = market-model CAR[-20,-2]
```

### Key results

For current text-history AIActivePeer in true Top5 peers:

```text
CAR[-10,-2], event FE:
coef = -0.005353, p = 0.013

CAR[-10,-2], event FE + peer industry-week FE:
coef = -0.004847, p = 0.043

CAR[-20,-2], event FE:
coef = -0.007642, p = 0.009

CAR[-20,-2], event FE + peer industry-week FE:
coef = -0.009149, p = 0.003
```

For external `ext_any`:

```text
true Top5 pre-window p-values are 0.637, 0.973, 0.253, and 0.556.
```

Low-similarity peers are also not significant under the current text-history definition:

```text
low Top5 current text-history p-values are 0.145 and 0.136.
```

### Reading

This is a real warning. The text-history AIActivePeer definition picks up a negative pre-event pattern among true Top5 peers. The safest response is not to hide this, but to:

1. report pre-window tests;
2. control for pre-window peer CAR in the main table;
3. use external AIActivePeer as an additional validation layer because its pre-window placebo is clean.

## 3. Pretrend-Adjusted Main Regression

I reran the main Top5 regression after controlling for peer pre-window CAR.

### Current text-history AIActivePeer

```text
No pretrend control:
event FE + peer industry-week FE coef = -0.002298, p = 0.020

Control CAR[-10,-2]:
event FE + peer industry-week FE coef = -0.002034, p = 0.034

Control CAR[-20,-2]:
event FE + peer industry-week FE coef = -0.002026, p = 0.036

Control both:
event FE + peer industry-week FE coef = -0.002025, p = 0.036
```

### External `ext_any`

```text
No pretrend control:
event FE + peer industry-week FE coef = -0.001800, p = 0.058

Control CAR[-10,-2]:
event FE + peer industry-week FE coef = -0.002093, p = 0.026

Control CAR[-20,-2]:
event FE + peer industry-week FE coef = -0.002111, p = 0.024

Control both:
event FE + peer industry-week FE coef = -0.002109, p = 0.024
```

### Reading

This rescues part of the identification concern. The pre-window placebo fails for the text-history AIActivePeer definition, but the event-window result is not mechanically absorbed by controlling for pre-event peer CAR. In fact, the external AIActivePeer definition becomes stronger once pre-window CAR is controlled.

The paper should therefore include pre-window CAR controls in the preferred robustness table.

## 4. Focal-Firm CAR Sign Decomposition

The intended business-stealing prediction was:

```text
focal firm CAR > 0
  -> AI-active product-market peers react more negatively
```

### Results

```text
Focal CAR positive:
event FE coef = -0.001917, p = 0.144
event FE + peer industry-week FE coef = -0.001933, p = 0.230

Focal CAR non-positive:
event FE coef = -0.002601, p = 0.024
event FE + peer industry-week FE coef = -0.002646, p = 0.048

Interaction with focal positive:
p = 0.694 / 0.652
```

### Reading

This does not support a clean "focal gains at rivals' expense" business-stealing mechanism. The negative peer reaction is stronger when the focal firm's own market reaction is non-positive.

This means the mechanism should be written more conservatively:

```text
specific GenAI disclosure acts as a competitive-risk or strategic-commitment signal,
not necessarily a positive focal-firm shock that mechanically steals value from rivals.
```

The focal-CAR sign decomposition should be reported as a boundary test, not as the main mechanism.

## 5. Investor-Question-Triggered Subsample

This test restricts the sample to events where the investor question itself contains GenAI terms. A stricter IIP version additionally requires a quick IIP response within 7 calendar days.

### Results

```text
Question contains GenAI terms:
event FE coef = -0.001837, p = 0.058
event FE + peer industry-week FE coef = -0.002123, p = 0.050

IIP quick question-triggered sample:
event FE coef = -0.002384, p = 0.056
event FE + peer industry-week FE coef = -0.002411, p = 0.091

Not question-triggered:
event FE coef = -0.002620, p = 0.194
event FE + peer industry-week FE coef = -0.003720, p = 0.124
```

### Reading

This is supportive. The result survives in the subset where timing is more plausibly triggered by investor questions rather than fully chosen by managers. It is not a clean instrument, but it improves the timing story.

## 6. Non-GenAI IIP Pseudo-Event Placebo

I built a pseudo-event sample from the same investor-interaction platform:

```text
same focal firms
same product-peer network
company replies that contain no GenAI terms
investor questions that contain no GenAI terms
first pseudo-event per focal firm
```

Pseudo-event sample:

```text
2,652 pseudo focal events
26,260 event-peer rows before cleaning
14,790 rows after clean sample filters
```

DDD placebo result:

```text
Non-GenAI pseudo-event DDD:
event FE coef = +0.002349, p = 0.358
event FE + peer industry-week FE coef = +0.002284, p = 0.372
```

### Reading

This is a strong placebo result. Ordinary non-GenAI investor-interaction specificity does not reproduce the negative GenAI peer-CAR pattern.

## Overall Assessment

The five checks do not uniformly strengthen the paper. They sharpen the boundary:

### Supports the design

```text
1. Non-GenAI pseudo-events are null.
2. Investor-question-triggered GenAI events still show the predicted negative peer reaction.
3. Formal DDD has the right sign and is significant or marginal in several random / ext_plus_history specifications.
4. Event-window results survive controls for pre-window peer CAR.
5. External ext_any has clean pre-window placebo and becomes stronger after pretrend controls.
```

### Weakens the design

```text
1. Current text-history AIActivePeer fails the pre-window placebo.
2. Formal DDD is not uniformly significant, especially against low-similarity peers.
3. Focal-CAR sign decomposition does not support a simple business-stealing story.
4. Pure external ext_any still should not replace the main AIActivePeer definition because it weakens under peer firm FE.
```

## Recommended Interpretation After These Checks

The topic is still alive, but the writing must be more conservative.

Do not write:

```text
specific GenAI disclosure causes business-stealing losses for rivals.
```

Write:

```text
The market interprets specific GenAI disclosures as competitive-risk signals.
The negative revaluation is concentrated among product-market peers that are already in the AI competitive space.
The pattern is not reproduced by non-GenAI interaction events, random peers, or low-similarity peers, and it survives pre-event peer-CAR controls.
```

The preferred empirical hierarchy should become:

```text
Main:
    Top5 true product peers
    current text-history AIActivePeer
    event FE + peer industry-week FE
    event × peer firm clustered SE
    pre-window peer CAR controls included or reported immediately after main table

Validation:
    external ext_any AIActivePeer
    AI-word-stripped product similarity
    non-GenAI pseudo-event placebo
    question-triggered sample

Boundary:
    pre-window placebo warning
    focal-CAR sign decomposition
    formal DDD against placebo peers
```
