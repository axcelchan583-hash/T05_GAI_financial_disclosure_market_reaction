# v44 Event-Study Results Inventory

Date: 2026-06-07

## Scope

This note consolidates the event-study results already produced for the current T05 GenAI disclosure project. It focuses on stock-market reactions around v36 first GenAI disclosure events and separates three outcome families:

1. product-market competitors;
2. broad collaborators from supply-chain, announcement text, and annual-report text;
3. FactSet relationship counterparts.

The current event source is the v36 first-event sample: 363 focal firms. The main product-market peer event-study sample has 2,790 event-peer return observations across 316 usable GenAI events.

## 1. Product-Market Competitors

Source: `results/v29_pom_style_peer_results_20260605/`, `results/v30_stata_mcp_peer_results_20260605/`, and `results/v33_supplement_data_probe_20260605/`.

Peer construction: `liu_product_tfidf_same_industry_d_top10`.

### Day -1 / 0 / +1 Abnormal Returns

| Window | Mean AR | p-value | Median AR | Positive share | N |
|---|---:|---:|---:|---:|---:|
| Day -1 | -0.0010 | 0.3350 | -0.0026*** | 0.4520*** | 2,790 |
| Day 0 | -0.0025** | 0.0205 | -0.0023*** | 0.4577*** | 2,790 |
| Day +1 | -0.0021* | 0.0541 | -0.0025*** | 0.4434*** | 2,790 |

### CAR Windows

| Window | Mean CAR | p-value | N | Events | Peer firms | Positive share |
|---|---:|---:|---:|---:|---:|---:|
| CAR[0,+1] | -0.0047*** | 0.0045 | 2,789 | 316 | 1,384 | 0.4342 |
| CAR[0,+5] | -0.0120*** | 0.000013 | 2,621 | 313 | 1,335 | 0.4197 |
| CAR[0,+20] | -0.0293*** | 0.000000002 | 2,206 | 294 | 1,195 | 0.3790 |
| CAR[0,+60] | -0.0639*** | <0.000001 | 1,670 | 280 | 966 | 0.3665 |

Reading: product-market competitors show the cleanest and most repeatable negative event-study result. Day 0 is negative and significant; CAR[0,+1] is stronger; longer windows do not reverse, but CAR[0,+60] has materially lower coverage and should be used as supporting evidence rather than a primary table.

## 2. Pollution and Clean-Sample Checks

Source: `results/v33_supplement_data_probe_20260605/cleaned_event_study_tests.csv`.

| Sample | Outcome | Mean | p-value | N | Events | Peer firms | Reading |
|---|---|---:|---:|---:|---:|---:|---|
| Main v29 sample | PeerCAR[0,+1] | -0.0047*** | 0.0045 | 2,789 | 316 | 1,384 | Main result |
| Drop peer own GenAI event [-2,+2] | PeerCAR[0,+1] | -0.0048*** | 0.0034 | 2,773 | 316 | 1,384 | Stronger after removing peer GenAI self-events |
| Drop peer major announcement [-2,+2] | PeerCAR[0,+1] | -0.0042** | 0.0156 | 1,868 | 310 | 1,050 | CAR survives; Day 0 alone weakens |
| Drop peer any announcement [-2,+2] | PeerCAR[0,+1] | -0.0057*** | 0.0021 | 1,379 | 301 | 832 | Strong but more aggressive sample loss |
| Drop peer GenAI or major announcement | PeerCAR[0,+1] | -0.0042** | 0.0155 | 1,865 | 310 | 1,050 | Conservative pollution screen survives |

Reading: peer self-GenAI pollution is tiny and not driving the result. Major-announcement pollution is common, but the two-day CAR remains negative after cleaning. For the paper, the defensible main Y is CAR[0,+1], with AR[0] as auxiliary.

## 3. Analyst-Covered Subsample

Source: `results/v37_mechanism_closure_20260605/analyst_covered_main_effects.csv`.

| Sample | Outcome | Mean | p-value | N | Events | Peer firms | Positive share |
|---|---|---:|---:|---:|---:|---:|---:|
| Analyst-covered peers, FY+1 EPS or parent-profit revision observed within 60 days | PeerAR[0] | -0.0079*** | 0.0095 | 185 | 100 | 105 | 0.4000 |
| Analyst-covered peers, FY+1 EPS or parent-profit revision observed within 60 days | PeerCAR[0,+1] | -0.0110*** | 0.0025 | 185 | 100 | 105 | 0.4000 |
| Non-covered / no observed FY+1 revision counterpart | PeerCAR[0,+1] | -0.0042** | 0.0119 | 2,604 | 316 | 1,317 | 0.4366 |

Reading: the negative peer CAR remains and is larger in the analyst-covered subsample. Because coverage is only 185 peer-event observations, this is supporting evidence for a cash-flow interpretation, not a standalone main effect.

## 4. Broad Collaborator Attempts Before FactSet

Sources: `results/v38_wide_collaborator_competitor_probe_20260607/`, `results/v39_broad_collaborator_text_probe_20260607/`, `results/v40_annual_report_collaborator_probe_20260607/`, and `results/v41_annual_report_5y_collaborator_probe_20260607/`.

### Supply-Chain and Text-Matched Collaborators

| Relation type | Source | CAR[0,+1] mean | p-value | N | Events | Related firms | Event-weighted mean | Event-weighted p |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Competitor baseline | Product-market peers | -0.0046*** | 0.0045 | 2,790 | 316 | 1,385 | -0.0051*** | 0.0023 |
| Supplier/customer union | CSMAR supply-chain links | -0.0040 | 0.2900 | 142 | 70 | 122 | -0.0005 | 0.9064 |
| Event-named listed partner | Event announcement text | 0.0036 | 0.3556 | 159 | 74 | 123 | -0.0028 | 0.3410 |
| Broad collaborator union | Event text + historical text + supply chain | -0.0002 | 0.9414 | 307 | 130 | 236 | -0.0015 | 0.5769 |

### Annual-Report Collaborators

| Relation type | Source | CAR[0,+1] mean | p-value | N | Events | Related firms | Event-weighted mean | Event-weighted p |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Annual-report listed collaborator | Latest pre-event annual report only | 0.0011 | 0.7249 | 108 | 68 | 72 | 0.0015 | 0.7332 |
| Annual-report listed collaborator | Five-year pre-event annual reports | 0.0007 | 0.7591 | 268 | 128 | 167 | 0.0027 | 0.3977 |

Reading: broad collaborators from local text sources are not negative like competitors, but they do not yet deliver a clean positive CAR. The only suggestive annual-report result is Day 0 in the latest-report sample, AR[0] = 0.0046, p = 0.0715, but CAR[0,+1] is not significant.

## 5. FactSet Relationship Counterparts

Source: `results/v43_factset_grouped_relationship_results_20260607/`.

FactSet relationships are matched to v36 events using pre-event links and A-share related firms.

| Relation type | CAR[0,+1] mean | p-value | N | Events | Related firms | Event-weighted mean | Event-weighted p | Reading |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| FactSet competitor | -0.0081** | 0.0107 | 299 | 129 | 241 | -0.0092*** | 0.0005 | Strong negative competitor validation |
| FactSet upstream supplier | -0.0041 | 0.4608 | 1,039 | 168 | 769 | 0.0006 | 0.8043 | Not a positive supplier effect |
| FactSet downstream customer | -0.0006 | 0.7729 | 946 | 207 | 551 | -0.0026 | 0.1943 | No clear customer effect |
| FactSet partner all | -0.0031 | 0.2638 | 388 | 149 | 292 | 0.0006 | 0.8152 | Broad partner group is null |
| FactSet high-confidence operational partner | -0.0063** | 0.0355 | 311 | 126 | 233 | -0.0021 | 0.4392 | Operational partners are not positive |
| FactSet investment partner | 0.0066 | 0.1482 | 86 | 54 | 83 | 0.0084** | 0.0378 | Positive only under event weighting |

Reading: FactSet strongly reinforces the competitor-negative result. It does not support a broad "collaborators all gain" claim. The only positive collaborator-style signal is investment-type partners, but that construct is closer to investment or strategic ownership ties than operating GenAI cooperation.

## 6. Current Writing Implications

1. The safest main event-study claim is:

   GenAI disclosure events trigger negative short-window abnormal returns among product-market competitors.

2. The strongest validation result is:

   FactSet competitors also react negatively, with a larger CAR[0,+1] magnitude than the product-market TF-IDF peer baseline.

3. The collaborator redesign is not yet ready as a symmetric main claim:

   Existing broad collaborators do not show a stable positive absolute CAR. Investment-type partners are the only positive relation group, but they require a narrower theory and careful naming.

4. The current event-study structure can still support a relation-dependent design:

   Competitors are negatively revalued; investment-linked partners may be more favorably revalued; broad operating partners are at best neutral and sometimes negative.

5. For a paper table sequence, the current defensible order is:

   - Table 1: sample flow and event-study sample composition.
   - Table 2: product-market competitor AR[-1], AR[0], AR[+1], plus CAR[0,+1].
   - Table 3: pollution and long-window checks.
   - Table 4: FactSet relationship counterpart event study.
   - Appendix: broad collaborator screens from event text, annual reports, and CSMAR supply-chain links.
