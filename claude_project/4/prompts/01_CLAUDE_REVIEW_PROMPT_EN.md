# Claude Review Prompt

You are reviewing an empirical accounting/finance research project. Please be critical and practical. Do not praise the project unless the evidence warrants it. Do not invent results that are not in the uploaded files.

## Project

The project studies whether specific GenAI disclosures by Chinese listed firms cause capital markets to revalue product-market peers. The current paper identity is:

> Specific Generative AI Disclosure and Product-Market Peer Revaluation: Evidence from Chinese Listed Firms

The intended framing is a short-window capital-market revaluation paper, not a strong causal business-stealing paper.

## Files to Read First

Please read these files in this order:

1. `01_PROJECT_BRIEF_EN.md`
2. `source_docs/01_current_paper_outline_20260527.md`
3. `source_docs/02_final_review_checks_20260525.md`
4. `source_docs/03_focal_good_news_pretrend_checks_20260525.md`
5. `source_docs/04_disclosure_type_horserace_20260527.md`
6. `source_docs/05_event_time_peer_validity_20260527.md`

Use the CSVs and figures only to verify or deepen your assessment.

## Core Design to Evaluate

Unit:

```text
focal GenAI disclosure event × product-market peer firm
```

Main outcome:

```text
Peer market-model CAR[0,+1]
```

Main explanatory object:

```text
Specificity_z × AIActivePeer
```

Main AIActive definition:

```text
ext_any = prior CAC filing OR prior broad-AI patent grant OR prior broad-AI hiring
```

Core robustness:

```text
current_text_history = prior GenAI disclosure before t-5
```

Main specification:

```text
PeerCAR[0,+1] =
    beta1 AIActivePeer
  + beta2 Specificity_z × AIActivePeer
  + event FE
  + peer industry-week FE
  + PeerCAR[-10,-2] + PeerCAR[-20,-2]
  + error
```

Standard errors are clustered by event and peer firm.

## Your Tasks

Please provide a referee-style assessment with these sections:

1. **Bottom-line verdict**
   - Is this currently worth drafting?
   - What is the realistic outlet tier?
   - Is AJG/ABS 3 plausible, or should it be downgraded?

2. **Core contribution**
   - What is the cleanest contribution claim?
   - What should the paper not claim?
   - Is the paper sufficiently distinct from generic AI disclosure / focal-firm CAR papers?

3. **Identification assessment**
   - Does event FE make the within-event interpretation credible?
   - Are peer industry-week FE and pre-window CAR controls enough?
   - How serious are residual timing, selection, and pretrend concerns?
   - Does the `ext_any` AIActive definition solve enough of the same-source concern?

4. **Measurement assessment**
   - Is `Specificity_z` sufficiently defensible?
   - Are the observable text-control checks sufficient for the current framing?
   - Are the disclosure-type horse-race results useful?
   - Is `ext_any` the right main AIActive measure?

5. **Product-market peer validity**
   - Do the Top1-3 / Top4-5 / Top6-10 / low-sim / random results support the peer construction?
   - What further validation would a reviewer ask for?

6. **Interpretation and theory**
   - Should the story be competitive risk, category validation, strategic commitment, or something else?
   - How should the AI supply-chain boundary result be used?
   - Should peer disclosure diffusion remain in the paper?

7. **Recommended paper structure**
   - Provide a revised table and figure order.
   - Identify which results should be main text vs appendix.

8. **Fatal risks and must-fix list**
   - List the top five risks that could kill the paper.
   - For each risk, give the exact empirical or writing fix.

9. **Go / revise / stop decision**
   - Give a clear decision: go draft now, revise before drafting, or stop/pivot.

Please be concrete. Use coefficient magnitudes and p-values from the uploaded files when relevant.
