# v29 POM-style peer results

## Scope

- Sample: `combined_first_event_per_firm`.
- Peer construction: `liu_product_tfidf_same_industry_d_top10` (Product-word TF-IDF same-industry Top10).
- Table 2 is the POM-style event-study table: it tests whether product-market peers have abnormal stock returns around focal-firm GenAI disclosures.
- Table 3 is the POM-style cross-sectional regression table: it tests which observable characteristics explain or moderate those peer reactions.
- Mean-return t-statistics in Table 2 and regression standard errors in Table 3 are two-way clustered by event and peer firm.
- Wilcoxon signed-rank and binomial sign-test Z-statistics in Table 2 use normal approximations.
- `Spec` is event-level disclosure specificity, so it is absorbed by event fixed effects; `Spec x AIActivePeer` remains identified by within-event differences across peers.
- Other event-level source controls are also absorbed by event fixed effects and therefore are not displayed in Table 3.

## Table 1 Sample Summary

| sample | observations | events | focal_firms | peer_firms |
|---|---|---|---|---|
| Event-study sample | 2790 | 316 | 316 | 1385 |
| Cross-sectional regression sample | 2789 | 316 | 316 | 1384 |

## Table 2 Event Study Results on Peers' Stock Market Reaction

| Variables | Day -1 (1) | Day 0 (2) | Day 1 (3) |
|---|---|---|---|
| Average abnormal return | -0.0010 | -0.0025** | -0.0021* |
| t-test (clustered t-statistic) | (-0.9641) | (-2.3169) | (-1.9257) |
| Median abnormal return | -0.0026*** | -0.0023*** | -0.0025*** |
| Wilcoxon signed rank test (Z-statistic) | (-4.5485) | (-5.5088) | (-5.3639) |
| Positive rate of the abnormal returns | 0.4520*** | 0.4577*** | 0.4434*** |
| Binomial sign test (Z-statistic) | (-5.0738) | (-4.4680) | (-5.9825) |
| Observations | 2790 | 2790 | 2790 |

## Table 3 Cross-Sectional Regression Results on Factors Influencing Peer Reactions

| Variables | (1) | (2) | (3) | (4) | (5) | (6) |
|---|---|---|---|---|---|---|
|  | PeerAR[0] | PeerAR[0] | PeerAR[0] | PeerCAR[0,+1] | PeerCAR[0,+1] | PeerCAR[0,+1] |
|  | Event FE | Event + industry-week FE | Event + peer-firm FE | Event FE | Event + industry-week FE | Event + peer-firm FE |
| Spec | - | - | - | - | - | - |
| Spec x AIActivePeer | -0.0018** | -0.0018** | -0.0006 | -0.0033*** | -0.0033*** | -0.0009 |
|  | (0.0008) | (0.0008) | (0.0014) | (0.0012) | (0.0012) | (0.0018) |
| AIActivePeer | -0.0001 | -0.0001 | 0.0021 | -0.0014 | -0.0014 | 0.0022 |
|  | (0.0010) | (0.0010) | (0.0026) | (0.0013) | (0.0013) | (0.0037) |
| PeerRank | -0.0003 | -0.0003 | 0.0001 | -0.0002 | -0.0002 | 0.0005 |
|  | (0.0002) | (0.0002) | (0.0003) | (0.0003) | (0.0003) | (0.0005) |
| PeerSimilarity | 0.0049 | 0.0049 | 0.0261 | 0.0156 | 0.0156 | 0.0709* |
|  | (0.0143) | (0.0143) | (0.0269) | (0.0177) | (0.0177) | (0.0390) |
| PeerCAR[-10,-2] | 0.0115 | 0.0115 | -0.0037 | -0.0011 | -0.0011 | -0.0257 |
|  | (0.0117) | (0.0117) | (0.0171) | (0.0158) | (0.0158) | (0.0190) |
| PeerCAR[-20,-2] | -0.0059 | -0.0059 | -0.0060 | 0.0000 | 0.0000 | 0.0066 |
|  | (0.0081) | (0.0081) | (0.0109) | (0.0110) | (0.0110) | (0.0141) |
| Event FE | YES | YES | YES | YES | YES | YES |
| Peer industry-week FE | NO | YES | NO | NO | YES | NO |
| Peer firm FE | NO | NO | YES | NO | NO | YES |
| Observations | 2789 | 2789 | 2789 | 2789 | 2789 | 2789 |
| Events | 316 | 316 | 316 | 316 | 316 | 316 |
| Peer firms | 1384 | 1384 | 1384 | 1384 | 1384 | 1384 |
| Overall R2 | 0.439 | 0.439 | 0.716 | 0.482 | 0.482 | 0.750 |
| Within R2 | 0.004 | 0.004 | 0.003 | 0.004 | 0.004 | 0.007 |

## Headline Read

- Peer AR on day 0 is -0.0025**; the day-0 clustered statistic is -2.3169.
- In the AR0 regression, `Spec x AIActivePeer` is -0.0018** (0.0008) in column (1).
- In the CAR[0,+1] regression, `Spec x AIActivePeer` is -0.0033*** (0.0012) in column (4).

## Output Files

- `results/v29_pom_style_peer_results_20260605/table1_sample_summary.csv`
- `results/v29_pom_style_peer_results_20260605/table2_pom_style_peer_event_study.csv`
- `results/v29_pom_style_peer_results_20260605/table2_pom_style_peer_event_study_raw.csv`
- `results/v29_pom_style_peer_results_20260605/table3_pom_style_cross_section_regressions.csv`
- `results/v29_pom_style_peer_results_20260605/table3_pom_style_cross_section_regressions_raw.csv`
- `results/v29_pom_style_peer_results_20260605/analysis_sample_used_in_table2.csv`
- `results/v29_pom_style_peer_results_20260605/analysis_sample_used_in_table3.csv`
- `results/v29_pom_style_peer_results_20260605/v29_pom_style_peer_results_20260605.xlsx`

## Notes

- `***`, `**`, and `*` indicate significance at 1%, 5%, and 10% in two-sided tests.
- Wilcoxon signed-rank and binomial sign-test Z-statistics in Table 2 use normal approximations.
- `Overall R2` includes fixed-effect explanatory power; `Within R2` is the incremental explanatory power after absorbing fixed effects.
- Column (3) and column (6) add peer-firm fixed effects, so they are strict robustness checks rather than the preferred mechanism specification.
