# v6 Peer-Firm FE Identification Check

Date: 2026-05-24

## Purpose

This check clarifies the current identification strategy and tests whether the main peer-CAR result survives a stricter peer-firm fixed-effect specification.

The current main design is not an IV or DID design. It is a short-window event-study cross-sectional design estimated by absorbed OLS:

```text
PeerCAR_{e,j,[0,+1]}
  = beta_1 AIActive_{j,t-5}
  + beta_2 Specificity_e × AIActive_{j,t-5}
  + event FE_e
  + peer industry × week FE
  + error_{e,j}
```

where `e` is a focal firm's first GenAI disclosure event and `j` is one of its product-market peers.

In the Top5 / Top10 specifications, product-market similarity is mainly used to define the peer sample. The coefficient of interest is `beta_2`, i.e. whether more specific focal GenAI disclosures are associated with more negative short-window CARs among peers that were already AI-active before the event.

The existing inference uses two-way clustered standard errors by focal event and peer firm.

## Identification Interpretation

With event fixed effects, all event-level common shocks are absorbed, including:

- focal event date;
- focal firm identity within that event;
- market-wide or platform-wide news common to all peers in the event;
- the main effect of focal disclosure specificity.

Therefore the coefficient is not identified by whether a high-specificity focal firm has a higher or lower average peer CAR. It is identified by whether the gap between AI-active peers and non-AI-active peers is more negative for high-specificity focal events than for low-specificity focal events.

This is best described as:

```text
event-level cross-sectional information-revelation design
```

It should not be described as a clean causal natural experiment.

## Additional Peer-Firm FE Test

I added a stricter specification:

```text
PeerCAR_{e,j,[0,+1]}
  = beta × Specificity_e × AIActive_{j,t-5}
  + event FE_e
  + peer firm FE_j
  + error_{e,j}
```

and a stronger variant:

```text
event FE + peer firm FE + peer industry × week FE
```

This test asks whether the result remains when all time-invariant peer-firm differences are absorbed.

Script:

```text
scripts/run_v6_peer_firm_fe_checks_20260524.py
```

Output:

```text
results/v6_peer_firm_fe_checks_20260524/v6_peer_firm_fe_regressions.csv
```

## Key Results

### Current Text-History AIActivePeer

```text
Original Top5, drop either cleaning announcement, CAR[0,+1]:
event FE + peer firm FE:
coef = -0.002152, p = 0.058

event FE + peer firm FE + peer industry-week FE:
coef = -0.002915, p = 0.053

Original Top10:
event FE + peer firm FE:
coef = -0.001800, p = 0.009

event FE + peer firm FE + peer industry-week FE:
coef = -0.001922, p = 0.012
```

Low-similarity placebo remains null:

```text
low-similarity same-industry:
coef = -0.000261, p = 0.683
```

### External ext_any AIActivePeer

Pure external `ext_any` is weaker under peer-firm FE:

```text
Original Top5:
event FE + peer firm FE:
coef = -0.001713, p = 0.157

event FE + peer firm FE + peer industry-week FE:
coef = -0.000297, p = 0.847

AI-word-stripped Top5:
event FE + peer firm FE:
coef = -0.001372, p = 0.230

event FE + peer firm FE + peer industry-week FE:
coef = -0.001063, p = 0.449
```

This means `ext_any` should not replace the current main AIActivePeer definition yet. It is better used as an external validation layer.

### ext_plus_history

The broader `ext_plus_history` definition is stronger, especially in Top10:

```text
Original Top10:
event FE + peer firm FE:
coef = -0.001802, p = 0.004

event FE + peer firm FE + peer industry-week FE:
coef = -0.001662, p = 0.014

AI-word-stripped Top10:
event FE + peer firm FE:
coef = -0.002082, p = 0.001

event FE + peer firm FE + peer industry-week FE:
coef = -0.002175, p = 0.001
```

## Interpretation

The peer-firm FE check is mixed but useful.

The main text-history AIActivePeer result survives around the 10% threshold in Top5 and clearly survives in Top10. The low-similarity placebo remains null. This supports the core interpretation that the effect is concentrated among product-market peers rather than generic same-industry firms.

The pure external `ext_any` definition weakens under peer-firm FE, which is not surprising because CAC, patents, and hiring are slow-moving peer-firm attributes. Peer firm FE absorbs much of the stable cross-peer variation that the external AIActive measure is designed to capture.

The safe empirical hierarchy is therefore:

```text
Main table:
    text-history AIActivePeer
    event FE
    event FE + peer industry-week FE
    event × peer firm two-way clustered SE

Robustness / validation:
    external ext_any AIActivePeer
    AI-word-stripped product similarity
    peer-firm FE checks
    low-similarity and random-peer placebo
```

The paper should not claim that the external-AIActive result survives every possible fixed-effect saturation. It should claim that the main competitive-revaluation result is not driven solely by same-source AI text, because external pre-event AI evidence and AI-word-stripped product similarity produce the same directional pattern.
