# X/Y Measurement Literature Anchor

日期：2026-05-31

## Purpose

This memo freezes the measurement logic for the next design discussion.

The current goal is not to invent a new GenAI construct. The paper should use
measurement choices that can be defended by existing disclosure, event-study, and
peer-spillover literatures.

## Current Measurement Boundary

The paper should be read as a capital-market revaluation study:

```text
Observable GenAI disclosure signal
-> short-window stock-market reassessment
-> concentrated among close product-market peers with prior AI positioning
```

It should not be read as:

```text
GenAI disclosure causes realized business stealing;
GenAI disclosure proves real GenAI capability;
text specificity directly equals implementation quality.
```

## X Option 1: GenAI Disclosure Event

### Measurement

`GenAIDisclosureEvent_{i,t} = 1` if firm `i` issues a disclosure at date `t` that
contains GenAI / AIGC / large-model / LLM / ChatGPT / named-model language.

Possible event sources:

```text
investor-interaction platform replies;
IR activity records;
annual/interim/quarterly reports;
exchange announcements;
product or strategy disclosures.
```

### Literature Anchor

This is best treated as a transparent event definition, not as a mature
top-journal "GenAI disclosure construct."

Relevant anchors:

- Beaver (1968, Journal of Accounting Research): disclosure events can be
  evaluated by price and volume reactions.
- MacKinlay (1997): event-study abnormal returns.
- Kothari and Warner (2007): event-study inference.
- Cheng, De Franco, Jiang, and Lin (2019, Management Science): technology-mania
  disclosure events, using blockchain 8-K disclosures and distinguishing
  speculative versus existing blockchain disclosures.
- Chinese IIP setting anchor: Lee and Zhong (2022, Journal of Accounting and
  Economics), which validates interactive investor platforms as a disclosure
  environment.

### Role in This Project

Use this as the broad sample/event trigger:

```text
focal firm first GenAI disclosure event
```

This is safer as the event screen than as the sole explanatory construct.

## X Option 2: GenAI Disclosure Specificity / Concreteness

### Recommended Chinese Name

```text
生成式人工智能披露具体性
```

or, when emphasizing observable details:

```text
生成式人工智能披露细节具体性
```

Avoid "Hope式具体性" in paper text. The safer wording is:

```text
参考 Hope, Hu and Lu (2016) 的披露具体性思想，
构造生成式人工智能披露具体性指标。
```

### Measurement

The preferred X is:

```text
GenAI_Disclosure_Specificity_{i,t}
```

computed on GenAI-relevant disclosure text as the density of concrete,
firm-specific, verifiable details.

The implementation should count details such as:

```text
named model/product/platform/application;
named partner/customer/subsidiary/business line;
deployment or launch language;
application scenario;
commercialization or customer-use language;
dates, quantities, percentages, parameter counts, customer numbers, contract
or revenue/order amounts.
```

### Literature Anchor

Main anchor:

- Hope, Hu, and Lu (2016, Review of Accounting Studies), "The Benefits of
  Specific Risk-Factor Disclosures."

Transfer logic:

```text
Hope et al. measure disclosure specificity as the amount of specific,
entity-level and quantitative detail in qualitative disclosure, scaled by text
length. This project applies the same density-of-concrete-detail logic to
GenAI-related disclosure sentences.
```

Technology-disclosure filter:

- Cheng, De Franco, Jiang, and Lin (2019, Management Science), "Riding the
  Blockchain Mania: Public Firms' Speculative 8-K Disclosures."

Transfer logic:

```text
Cheng et al. show that hot-technology disclosures should not be treated as
homogeneous. They distinguish speculative technology talk from disclosures about
existing technology activity. This project uses that logic to separate generic
GenAI talk from more substantive/concrete GenAI disclosure content.
```

### Role in This Project

This should be the main cross-event textual signal:

```text
Specificity_z_{i,t}
```

The current main regression does not identify the level effect of specificity
directly once event fixed effects are included. It identifies whether, within the
same focal event, AI-active peers react more negatively when the focal disclosure
is more specific.

## Y Option 1: Focal-Firm CAR

### Measurement

```text
FocalCAR[0,+1]_{i,t}
```

or:

```text
FocalCAR[-1,+1]_{i,t}
```

using market-model abnormal returns or factor-adjusted abnormal returns.

### Literature Anchor

- Beaver (1968, Journal of Accounting Research): information content of
  announcements through price and volume.
- MacKinlay (1997): standard event-study abnormal-return framework.
- Kothari and Warner (2007): event-study methodology.
- Hope, Hu, and Lu (2016, Review of Accounting Studies): disclosure specificity
  and market reaction / abnormal trading-volume logic in a disclosure setting.

### Role in This Project

This is the safest traditional Y, but it is also the least novel:

```text
Does the market reward/punish the disclosing firm for GenAI disclosure?
```

Use as benchmark or control, not as the preferred main Y, unless the peer-side
design fails.

## Y Option 2: Peer-Firm CAR / Product-Market Peer Revaluation

### Measurement

Current main Y:

```text
PeerCAR[0,+1]_{j,t}
```

where `j` is a close product-market peer of focal firm `i`, and the event date is
the focal firm's GenAI disclosure date `t`.

Operational definition:

```text
market-model abnormal return of peer firm j from event day 0 to event day +1
```

Current headline interpretation:

```text
short-window peer-side capital-market revaluation
```

not:

```text
realized rival value destruction
```

### Literature Anchor

Event-study foundation:

- Beaver (1968)
- MacKinlay (1997)
- Kothari and Warner (2007)

Peer/information-transfer foundation:

- Foster (1981): intra-industry information transfers.
- Lang and Stulz (1992, Journal of Financial Economics): contagion and
  competitive effects around bankruptcy announcements; useful for distinguishing
  common information effects from competitive effects.
- Intra-industry information-transfer literature more generally: peer firms'
  stock prices can respond to another firm's disclosure because the event
  contains information about industry fundamentals or competitive redistribution.

Product-market peer foundation:

- Hoberg and Phillips (2016, Journal of Political Economy): text-based
  product-market networks / TNIC.
- Hoberg, Phillips, and Prabhala (2014, Journal of Finance): product-market
  threats and financial policy.
- Cao, Chen, Tucker, and Wan (2025, Review of Accounting Studies): validates
  annual-report/LLM peer systems using return, sales-growth, and gross-margin
  relatedness.

### Role in This Project

This is the most interesting Y if the paper is framed as:

```text
How does the capital market use concrete GenAI disclosure to reassess close
product-market peers?
```

The defensible claim is conditional:

```text
More specific GenAI disclosures are associated with more negative short-window
CARs for AI-active close product-market peers.
```

Do not write:

```text
GenAI disclosure causes all competitors to fall.
```

## Current Preferred Main Design

### Main X

```text
Specificity_z_{i,t}
```

interpreted as:

```text
observable GenAI disclosure specificity / concreteness
```

and supported by Hope et al. (2016) plus Cheng et al. (2019).

### Main Y

```text
PeerCAR[0,+1]_{j,t}
```

interpreted as:

```text
short-window market-model abnormal return of the focal firm's close
product-market peer
```

and supported by event-study and intra-industry information-transfer literature.

### Main Moderator / Conditioning Variable

```text
AIActivePeer_{j,t-1}
```

preferred headline definition:

```text
ext_any = prior CAC filing
       OR prior broad-AI patent grant
       OR prior broad-AI hiring in the previous 365 days
```

This should be described as:

```text
prior observable AI positioning
```

not:

```text
precise GenAI capability
```

## Current Regression Logic

With focal-event fixed effects:

```text
PeerCAR[0,+1]_{j,t}
  = beta * Specificity_z_{i,t} * AIActivePeer_{j,t-1}
  + theta * AIActivePeer_{j,t-1}
  + controls
  + event fixed effects
  + peer industry-week fixed effects
  + error
```

Because `Specificity_z_{i,t}` is an event-level variable, it is absorbed by event
fixed effects. The coefficient of interest is therefore:

```text
beta on Specificity_z × AIActivePeer
```

Interpretation:

```text
Within the same focal GenAI disclosure event, do AI-active peers experience
more negative short-window revaluation when the focal disclosure is more specific?
```

## Peer Definition Risk

The Y is only as credible as the peer system. Current v13 gate results imply:

```text
old CSMAR scope peers:
    pass return and fundamentals validation relative to random/low-similarity peers;
    preserve the existing significant PeerCAR result.

annual-report text peers:
    have stronger return, sales-growth, and gross-margin comovement;
    are cleaner under Hoberg-Phillips / Cao et al. logic;
    but do not reproduce the existing GenAI-event coefficient.
```

Therefore, peer measurement must be presented as a core measurement-risk section,
not as a solved detail.

## Recommended Next Step

Before writing a paper draft, freeze one of two paths:

### Path A: Conservative Peer-CAR Paper

```text
Main peer system:
    CSMAR business-scope text Top5

Required defense:
    return comovement gate;
    sales-growth and gross-margin comovement gate;
    random same-industry and low-similarity placebo;
    annual-report text peer replacement test reported transparently.
```

This path preserves the current significant PeerCAR result but has a peer-definition
robustness weakness.

### Path B: Literature-Clean Annual-Report Peer Paper

```text
Main peer system:
    annual-report business-section text Top5

Outcome:
    either find a new Y/specification that survives on annual-report peers,
    or abandon the peer-CAR main story.
```

This path has the cleanest peer measurement but currently loses the main result.

## Current Recommendation

The cleanest measurement statement is:

```text
X is defensible:
    GenAI disclosure specificity follows Hope et al. (2016) and Cheng et al. (2019).

Y is defensible:
    PeerCAR follows event-study and information-transfer literature.

The unresolved measurement risk is not X or Y.
It is the product-market peer definition that links the focal disclosure to the
peer-stock-price outcome.
```
