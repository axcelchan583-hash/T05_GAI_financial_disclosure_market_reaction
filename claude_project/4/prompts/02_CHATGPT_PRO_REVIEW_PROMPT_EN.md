# ChatGPT Pro Deep Review Prompt

I am preparing an empirical accounting/finance paper and need a hard-nosed design review. Please act like a skeptical but constructive referee for an AJG/ABS 3-level journal.

Do not give generic advice. Base your assessment on the uploaded files. If evidence is weak, say so. If a claim is too strong, rewrite it conservatively.

## Paper Idea

Working title:

> Specific Generative AI Disclosure and Product-Market Peer Revaluation: Evidence from Chinese Listed Firms

Question:

> Do more specific GenAI disclosures by Chinese listed firms lead capital markets to revalue AI-active product-market peers more negatively?

Current intended interpretation:

> Specific GenAI disclosure is a credible strategic-commitment / competitive-risk signal. The market uses it to reassess AI-active close product-market peers.

This is not intended to be a strong causal business-stealing paper.

## Core Specification

Observation:

```text
focal GenAI disclosure event e × product-market peer firm j
```

Main sample:

```text
first focal GenAI disclosure event × Top5 product-market peers
```

Outcome:

```text
Peer market-model CAR[0,+1]
```

Main regressor:

```text
Specificity_z_e × AIActivePeer_{j,t-5}
```

Main AIActive:

```text
ext_any =
    prior CAC generative-AI filing
 OR prior broad-AI patent grant
 OR prior broad-AI hiring in prior 365 days
```

Robustness AIActive:

```text
current_text_history =
    prior GenAI disclosure before t-5
```

Main fixed effects:

```text
event FE + peer industry-week FE
```

Core controls:

```text
PeerCAR[-10,-2] + PeerCAR[-20,-2]
```

Inference:

```text
two-way clustered by event_id and peer_code
```

## Key Results to Evaluate

Main result:

```text
Top5 / ext_any / event FE + peer industry-week FE / pre-window controls:
coef = -0.002303, p = 0.020

Top5 / current_text_history:
coef = -0.002275, p = 0.027
```

Good-news and pretrend robustness:

```text
ext_any / residualized Y + FocalCAR × AIActive:
coef = -0.002300, p = 0.020
```

Product-market gradient:

```text
Top1-3 / ext_any:
coef = -0.003252, p = 0.016

Top6-10, low-similarity peers, random same-industry peers:
not significant
```

Disclosure-type horse-race:

```text
Adding Type × AIActive interactions does not absorb the main specificity result.

ext_any:
Specificity_z × AIActive = -0.002394, p = 0.015
```

AI supply-chain boundary:

```text
Supply-chain disclosure has positive average peer effect without event FE:
coef = 0.004225, p = 0.026

But supply_chain × AIActive is not significant.
Stacked event-DID for supply-chain disclosure is null.
```

## Files to Use

Start from:

- `01_PROJECT_BRIEF_EN.md`
- `source_docs/01_current_paper_outline_20260527.md`
- `source_docs/02_final_review_checks_20260525.md`
- `source_docs/03_focal_good_news_pretrend_checks_20260525.md`
- `source_docs/04_disclosure_type_horserace_20260527.md`
- `source_docs/05_event_time_peer_validity_20260527.md`

Then consult CSVs and figures in `results_csv/` and `figures/`.

## Deliverable

Please produce a structured review with:

1. **One-paragraph verdict**
   - Continue, revise, or stop?
   - Realistic journal tier?

2. **Best possible paper framing**
   - Write the cleanest abstract-level story in 5-7 sentences.
   - State the strongest safe contribution.

3. **What is currently persuasive**
   - Identify the strongest three pieces of evidence.
   - Explain why they are persuasive.

4. **What is currently weak**
   - Identify the biggest design, measurement, and interpretation weaknesses.
   - Distinguish fatal from fixable weaknesses.

5. **Main table recommendation**
   - Which exact table should be Table 2?
   - Should `ext_any` or `current_text_history` be the headline AIActive?
   - Should DDD be headline or appendix?

6. **Specificity measurement**
   - What validation is still necessary?
   - How should the manual/LLM coding be used?

7. **Product-market peer validity**
   - Are the Top1-3 / Top6-10 / low-sim / random checks enough?
   - What would strengthen this section?

8. **Theory and interpretation**
   - How to distinguish competitive-risk signal from category validation?
   - How should the AI supply-chain result be framed?

9. **Revision checklist**
   - Give 10 concrete steps before drafting the full paper.

10. **Red-line claims**
   - List claims I must not make.
   - List claims I can safely make.

Use a candid referee tone. If AJG/ABS 3 is not realistic, say so directly and explain why.

