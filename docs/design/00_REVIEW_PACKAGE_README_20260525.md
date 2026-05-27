# Review Package README

Date: 2026-05-25

Project: T05 - GenAI disclosure, product-market peer revaluation, and peer diffusion

## Purpose

This folder contains the current research design and paper outline for external review by ChatGPT Pro / Claude / advisor-style reviewers.

The current paper should be reviewed as a **capital-market revaluation paper**, not as a hiring-response paper or a same-platform disclosure-diffusion paper.

## Files in This Folder

| File | Purpose |
|---|---|
| `01_current_research_design_20260525.md` | Main research design: research question, X/Y, sample, identification, current evidence, risks, and next steps. |
| `02_paper_outline_20260525.md` | Proposed manuscript outline: contribution, hypotheses, table plan, robustness plan, and writing boundary. |
| `03_chatgpt_pro_review_prompt_20260525.md` | English prompt that can be pasted into ChatGPT Pro with the design files attached. |
| `04_chatgpt_pro_feedback_digest_20260525.md` | Digest of ChatGPT Pro's feedback and the revised execution priorities. |
| `05_design_freeze_20260525.md` | Frozen headline sample, main AIActive definition, Table 2 specification, robustness hierarchy, and claim boundaries. |
| `06_specificity_validation_codebook_20260525.md` | Human/LLM codebook for validating disclosure specificity. |
| `07_specificity_validation_execution_plan_20260525.md` | Execution plan for agreement statistics, construct validation, and future-evidence validation. |
| `../empirical_runs/54_v6_focal_good_news_pretrend_checks_20260525.md` | Focused robustness checks for focal-firm good-news controls and pre-trend-adjusted peer CAR. |
| `../empirical_runs/55_specificity_validation_sample_20260525.md` | 300-event validation sample construction log. |

## Current One-Sentence Design

Do more specific GenAI disclosures by Chinese listed firms lead capital markets to revalue their **AI-active product-market peers** more negatively in short event windows?

More conservative wording:

> Do capital markets interpret specific GenAI disclosures as credible competitive-risk signals, leading to more negative short-window revaluation among product-market peers that are already active in the AI competitive space?

## Current Main Variables

| Role | Variable |
|---|---|
| Focal event | First GenAI / large-model / AIGC disclosure by a listed firm in investor-interaction and related disclosure channels. |
| Main X | `Specificity_z × AIActivePeer`, estimated within Top5 product-market peer samples. |
| Product-market relation | Top5 / Top10 peers constructed from Chinese product/business-description similarity; AI-word-stripped similarity used as robustness. |
| Main Y | Peer firm market-model `PeerCAR[0,+1]`, signed return. |
| Mechanism Y | Peer firm follow-up GenAI disclosure within 60 / 90 / 180 days. |
| Validation evidence | Pre-event CAC filing, AI patent grant, AI hiring, historical GenAI disclosure. |

## Current Empirical Status

The main result is alive but should be written conservatively:

```text
Top5 product-market peers, first focal GenAI event,
announcement-cleaned sample,
market-model PeerCAR[0,+1].

event FE:
Specificity_z × AIActivePeer coef = -0.002298, p = 0.008

event FE + peer industry-week FE:
Specificity_z × AIActivePeer coef = -0.002298, p = 0.020
```

Important support:

- low-similarity peer placebo is near zero;
- 100 random same-industry placebo draws cannot reproduce the true Top5 negative coefficient;
- AI-word-stripped product similarity preserves the result;
- external AI-active definitions based on CAC / patents / hiring support the direction;
- non-GenAI investor-interaction pseudo-events are null;
- investor-question-triggered subsample remains directionally supportive.

Important weakness:

- text-history AIActivePeer has a negative pre-window pattern, so main or core robustness tables must include pre-window peer CAR controls.

Latest focused robustness:

```text
Top5 / first focal event / announcement-cleaned / PeerCAR[0,+1]
event FE + peer industry-week FE
two-way clustering by event_id and peer_code
N = 7,805; events = 2,177; peer firms = 3,345

Adding FocalCAR[0,+1] and FocalCAR[0,+1] × AIActive:
    text-history: coef remains about -0.00228, p = 0.027
    ext_any:      coef remains about -0.00231, p = 0.020

Residualizing PeerCAR[0,+1] on PeerCAR[-10,-2]:
    text-history: coef remains about -0.00228, p = 0.026-0.027
    ext_any:      coef remains about -0.00230, p = 0.020-0.021
```

Latest design freeze:

```text
Main AIActive is now external ext_any.
Text-history AIActive is robustness / extension.
Table 2 headline specification is within-event FE heterogeneity.
DDD is robustness / placebo.
Headline sample is first focal GenAI event × Top5 product-market peers.
```

Specificity validation package:

```text
300 validation events drawn from 2,177 eligible headline focal events.
Balanced by Specificity_z tercile: low 100 / mid 100 / high 100.
Coding template and LLM input are in data/specificity_validation/.
```

## Revised Execution Priorities After External Review

The next stage should not add more outcomes. It should strengthen the current main design:

1. Headline specifications must include pre-window peer CAR controls.
2. `Specificity_z` needs a validation table showing it is not just length, AI keyword frequency, sentiment, readability, or IR verbosity.
3. External `ext_any` AIActivePeer should be shown alongside text-history AIActivePeer in core tables.
4. Product-market proximity should be shown as a gradient: Top1-3, Top4-5, Top6-10, low-similarity, and random peers.
5. Peer GenAI disclosure diffusion remains a mechanism table, not the main outcome.
