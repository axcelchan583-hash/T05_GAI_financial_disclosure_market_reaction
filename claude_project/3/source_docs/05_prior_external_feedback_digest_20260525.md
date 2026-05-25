# ChatGPT Pro Feedback Digest

Date: 2026-05-25

## Verdict

The project should continue. It has the shape of a writeable paper, but it should be framed as a **capital-market peer revaluation paper**, not as:

- a strong causal paper;
- a real business-stealing paper;
- a peer hiring-response paper;
- a same-platform disclosure-diffusion paper.

The current strongest framing is:

> Specific GenAI disclosure as a competitive-risk / strategic-commitment signal.

The realistic target is AJG / ABS 3 if the remaining measurement and identification issues are handled well. AJG / ABS 4 is not realistic without a stronger quasi-exogenous disclosure-timing shock.

## Main Reframing

The core result is **not a main effect**.

Do not write:

```text
GenAI disclosure makes peers fall.
```

Write:

```text
Conditional peer revaluation:
Within the same focal GenAI disclosure event, AI-active close product-market peers are revalued more negatively than non-AI-active peers, and this relative negative revaluation is stronger when the focal disclosure is more specific.
```

The main coefficient is a heterogeneity coefficient:

```text
Specificity_z × AIActivePeer
```

under event fixed effects.

## What the Review Confirms

The current result is not just one isolated significant coefficient because it is supported by:

1. Top5 first-event main result;
2. low-similarity peer placebo near zero;
3. 100 random same-industry peer placebo draws that cannot reproduce the true Top5 coefficient;
4. AI-word-stripped product similarity;
5. external AIActivePeer based on CAC / patents / hiring;
6. non-GenAI pseudo-event placebo;
7. investor-question-triggered subsample;
8. peer follow-up GenAI disclosure as mechanism.

## Main Threats

### 1. Pre-window concern

This is a real problem. Text-history AIActivePeer already has negative pre-window peer CAR patterns.

Required handling:

```text
Main table or core robustness must include:
    CAR[-10,-2]
    CAR[-20,-2]
as peer pre-window controls.
```

Do not hide this in the appendix.

Update after focused robustness:

```text
Using Top5 / announcement-cleaned / event FE + peer industry-week FE,
and two-way clustering by event_id and peer_code,
the core coefficient remains significant after residualizing PeerCAR[0,+1]
on PeerCAR[-10,-2]:

text-history: coef about -0.00228, p = 0.026-0.027
ext_any:      coef about -0.00230, p = 0.020-0.021
```

### 2. AIActivePeer definition

Text-history AIActivePeer is theoretically useful but endogenous to disclosure activity and market attention.

Recommended handling:

```text
Main definition:
    text-history AIActivePeer

Core parallel definition:
    external ext_any = prior CAC OR prior AI patent grant OR prior broad-AI hiring
```

Do not let text-history be the only main definition.

### 3. Specificity measurement

This is now the most important remaining measurement task.

Reviewers will ask whether specificity is just:

- text length;
- AI keyword frequency;
- IR sophistication;
- investor attention;
- sentiment / readability;
- generic verbosity.

Required table:

```text
Specificity validation table
```

It should show that `Specificity_z` captures concrete GenAI commitment rather than length or buzzwords.

Suggested components:

- named product / service;
- named model / platform;
- use case;
- customer / industry;
- partner;
- deployment status;
- commercialization / timeline;
- quantitative target.

### 4. Product-market peer validity

Top5 product-market peers must be shown to represent competitive proximity, not just textual similarity.

Required or strongly recommended:

- Top1-3 vs Top4-5 vs Top6-10 vs low-similarity / random gradient;
- AI-word-stripped similarity;
- external validation using industry / product / return comovement / disclosure diffusion if feasible.

### 5. Timing is not exogenous

Investor-question-triggered subsample helps, but it is not a clean instrument.

Safe wording:

```text
short-window market reassessment conditional on disclosure timing
```

Unsafe wording:

```text
causal effect of disclosure timing
```

## Revised Empirical Table Priority

| Priority | Table | Purpose |
|---:|---|---|
| 1 | Main peer-CAR table with pre-window controls | Make the headline result survive the main critique. |
| 2 | Focal good-news and pre-trend robustness | Show the result is not just focal-firm own good news or peer pre-window drift. |
| 3 | Specificity validation table | Prove `Specificity_z` is not length / AI word count / sentiment. |
| 4 | Product-market proximity gradient | Show Top5 effect is economically about close competitors. |
| 5 | External AIActive table | Reduce same-text-system concern. |
| 6 | Non-GenAI pseudo-event and question-triggered tests | Defend against generic IIP specificity and timing-selection critiques. |
| 7 | Peer GenAI disclosure diffusion | Descriptive follow-up only, not main mechanism. |
| 8 | Boundary tests | Focal CAR sign, category validation versus competitive-risk. |

## Go / No-Go Threshold

Continue if all four conditions hold:

1. With pre-window CAR controls, Top5 main result remains negative and at least 5%-10% significant.
2. External `ext_any` keeps the same direction and remains credible in core specifications.
3. Non-GenAI pseudo-events and low-similarity / random peers remain null.
4. Specificity validation shows the measure is not simply length, AI keyword frequency, sentiment, or readability.

Stop or pivot if any of the following happens:

1. External AIActive completely disappears.
2. Event-time plots show the negative pattern starts long before the focal event.
3. Non-GenAI pseudo-events produce the same negative effect.
4. Specificity is fully absorbed by length / attention / generic AI word controls.

## Bottom Line

This is a cautious but viable project.

The safest paper claim is:

> More specific GenAI disclosures are associated with more negative short-window revaluation among AI-active Top5 product-market peers. The evidence is best interpreted as capital-market reassessment of competitive risk rather than strong causal proof of business stealing.
