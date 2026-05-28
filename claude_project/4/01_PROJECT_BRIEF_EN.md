# Project Brief for External Review

Project: T05, Chinese listed firms' GenAI disclosure and product-market peer revaluation

Date: 2026-05-27

## Current Paper Identity

Working title:

> Specific Generative AI Disclosure and Product-Market Peer Revaluation: Evidence from Chinese Listed Firms

This paper should be reviewed as a capital-market revaluation paper, not as a strong causal business-stealing paper.

## Core Research Question

When a Chinese listed firm makes a GenAI / large-model / AIGC disclosure in investor-interaction or related public communication, does the market revalue its product-market peers?

More specifically:

> Are more specific GenAI disclosures interpreted as credible competitive-risk signals, leading to more negative short-window returns among AI-active close product-market peers?

## Core Design

Unit of observation:

```text
focal GenAI disclosure event e
× product-market peer firm j
```

Main sample:

```text
first focal GenAI disclosure event × Top5 product-market peers
```

Main outcome:

```text
Peer market-model CAR[0,+1]
```

Main explanatory object:

```text
Specificity_z_e × AIActivePeer_{j,t-5}
```

Main AIActive definition:

```text
ext_any =
    prior CAC generative-AI filing
 OR prior broad-AI patent grant
 OR prior broad-AI hiring in previous 365 days
```

Core robustness AIActive definition:

```text
current_text_history =
    peer had prior GenAI disclosure before event date t-5
```

Main fixed effects:

```text
event FE + peer industry-week FE
```

Main inference:

```text
two-way clustered by event_id and peer_code
```

Core controls:

```text
PeerCAR[-10,-2] + PeerCAR[-20,-2]
```

## Main Evidence Snapshot

Top5, first focal event, announcement-cleaned, PeerCAR[0,+1], event FE + peer industry-week FE, pre-window peer CAR controls:

```text
ext_any:
    coef = -0.002303, p = 0.020

current_text_history:
    coef = -0.002275, p = 0.027
```

Focal-good-news and pretrend-adjusted robustness:

```text
ext_any, residualized Y + FocalCAR[0,+1] × AIActive:
    coef = -0.002300, p = 0.020
```

Product-market proximity:

```text
Top1-3 / ext_any:
    coef = -0.003252, p = 0.016

Top6-10:
    not significant

low-similarity peers:
    not significant

random same-industry peers:
    not significant
```

Disclosure-type horse-race:

```text
Adding Type × AIActive interactions does not absorb the main result.

ext_any:
    Specificity_z × AIActive = -0.002394, p = 0.015

current_text_history:
    Specificity_z × AIActive = -0.002107, p = 0.045
```

AI supply-chain boundary:

```text
Supply-chain GenAI disclosures show positive average peer effect without event FE:
    coef = +0.004225, p = 0.026

But supply_chain × AIActive is not negative or significant.
The stacked event-DID for supply-chain disclosure is null.
```

## Intended Interpretation

The paper should claim:

> Specific GenAI disclosures are consistent with competitive-risk signals for AI-active close product-market peers.

The paper should not claim:

> GenAI disclosures causally destroy rival value or prove realized business stealing.

## Most Important Review Questions

1. Is the current design publishable as an AJG/ABS 3-level capital-market / disclosure paper?
2. Is `Specificity_z × AIActivePeer` the right headline regressor?
3. Is `ext_any` the right headline AIActive definition, with text-history as robustness?
4. Are event FE + peer industry-week FE + pre-window CAR controls sufficient for a short-window revaluation interpretation?
5. Does the product-market proximity evidence adequately validate the peer construction?
6. How should the paper present the disclosure-type horse-race and AI supply-chain boundary results?
7. What are the top remaining fatal threats before drafting?
