# Claude Brief: V5 Research Design on GenAI Disclosure and Rival AI Hiring

Date: 2026-05-22

## Suggested Files to Upload

```text
/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/README.md
/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/docs/current/34_v5_long_term_rival_ai_investment_design_20260522.md
/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/docs/current/32_v4_go_no_go_diagnostics_20260522.md
/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/v4_go_no_go_diagnostics/v4_go_no_go_sample_diagnostics.csv
/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/v4_go_no_go_diagnostics/v4_go_no_go_focus_main_effects.csv
/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/v4_go_no_go_diagnostics/v4_go_no_go_interaction_effects.csv
```

If upload space is limited, upload only:

```text
34_v5_long_term_rival_ai_investment_design_20260522.md
32_v4_go_no_go_diagnostics_20260522.md
v4_go_no_go_focus_main_effects.csv
```

## Brief

I am developing an empirical research project on Chinese listed firms' GenAI disclosures and their effects on product-market rivals.

The project has gone through several versions. The previous v4 design studied whether a focal firm's specific GenAI disclosure causes negative short-window stock-market reactions among AI-active product-market rivals. The v4 evidence is suggestive but not strong enough to be the final main design: the Top5 rival results are negative and marginally significant after stricter clustering, but the effect weakens in Top10 rivals and depends heavily on the AI-active peer definition.

Because of this, I am considering a v5 redesign. The v5 design no longer treats short-window rival CAR as the final outcome. Instead, it treats rival CAR, turnover, or attention as short-term market signals. The main long-term outcome becomes whether product-market rivals subsequently increase real AI investment, measured primarily through AI-skilled hiring intensity.

The proposed v5 structure is:

```text
Main X:
Focal firm GenAI disclosure specificity × product-market similarity

Main Y:
Rival firm's future AI-skilled hiring intensity / AI hiring share

Short-term surrogate:
Rival CAR / turnover / market attention around the focal disclosure event
```

The intuition is that a more specific GenAI disclosure by one firm may reveal a credible competitive threat. If the focal firm and a rival are close product-market competitors, the rival may respond by increasing AI-skilled hiring in subsequent quarters. The short-window stock-market reaction is not the final result; it is used as a possible early signal of which rival-event pairs later translate into real AI investment responses.

This design is also meant to connect with the causal ML / targeting literature on long-term outcomes, short-term surrogate signals, heterogeneous treatment effects, and policy-learning-style screening. However, the first step is not to use complex causal ML. The first step is a simple empirical smoke test: whether focal disclosure specificity interacted with product-market similarity predicts rivals' future AI hiring response.

## Main Questions

Please evaluate the v5 design directly.

1. Is the v5 research question clearer and more publishable than the v4 short-window peer-CAR design?

2. Does moving the main Y from rival CAR to rival future AI-skilled hiring solve the "so what?" problem, or does it create new measurement and identification problems?

3. Is the X-Y distance defensible?

```text
X = focal firm's GenAI disclosure specificity × product-market similarity
Y = rival firm's future AI hiring response
```

In particular, does this avoid the weaker design:

```text
focal firm says AI -> focal firm later hires AI workers
```

4. What is the most defensible main Y?

Possible candidates:

```text
future AI hiring share
change in AI hiring share
log(1 + AI job postings)
future GenAI-only hiring
AI patents
software copyrights / CAC filings / product launches
```

5. What is the minimum acceptable empirical test before continuing this project?

The current proposed smoke test is:

```text
FutureAIHiring_j,t+1:t+2 =
    beta * Specificity_it × ProductSimilarity_ij
  + EventFE_it
  + PeerFE_j
  + Peer pre-event controls
  + error_ijt
```

6. How should the short-term market signal be used?

Should rival CAR / turnover be:

```text
a mechanism variable,
a surrogate signal,
a moderator,
a validation outcome,
or dropped entirely?
```

7. What are the biggest risks that would make v5 not worth pursuing?

Please focus especially on:

```text
event timing,
hiring data coverage,
AI hiring measurement,
product-market peer definition,
pre-trends,
same-industry AI waves,
and whether the causal-ML / surrogate framing is overkill.
```

8. If v5 is viable, what should the paper's cleanest empirical design look like?

Please return:

```text
one recommended main X,
one recommended main Y,
one baseline model,
the most important fixed effects and controls,
the required placebo tests,
the role of v4 peer CAR evidence,
and a go/no-go threshold for the first hiring smoke test.
```

## Current Preference

My current preference is:

```text
Main X:
Specificity_it × ProductSimilarity_ij

Main Y:
Delta AI hiring share of rival firm j over t+1 to t+2 quarters

Main sample:
focal GenAI disclosure event × Top5 product-market rival

Main interpretation:
Specific GenAI disclosures can trigger real AI investment responses among close product-market rivals.

Short-term CAR:
early market signal / surrogate, not final outcome.
```

Please be critical. If the design is not viable, say so directly and explain which part fails first.
