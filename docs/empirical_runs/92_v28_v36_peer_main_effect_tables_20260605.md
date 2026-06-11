# v28 v36 peer main-effect tables

## Scope

- Sample: `combined_first_event_per_firm`.
- Peer construction: `liu_product_tfidf_same_industry_d_top10` (Product-word TF-IDF same-industry Top10).
- Table 2 treats the average peer abnormal return around focal-firm GenAI disclosures as the main effect.
- Table 3 treats disclosure specificity as mechanism-like heterogeneity, not a formal mediation test.
- Standard errors are clustered by event and peer firm.

## Sample Metadata

| sample_name | method_variant | method_label | event_study_rows | event_study_events | event_study_peer_firms | mechanism_rows | mechanism_events | mechanism_peer_firms | snippet_fallback_rows | snippet_fallback_events |
|---|---|---|---|---|---|---|---|---|---|---|
| combined_first_event_per_firm | liu_product_tfidf_same_industry_d_top10 | Product-word TF-IDF same-industry Top10 | 2790 | 316 | 1385 | 2789 | 316 | 1384 | 207 | 23 |

## Table 1 Descriptive Statistics

| 变量 | 观测值 | 均值 | 标准差 | 最小值 | 中位数 | 最大值 |
|---|---|---|---|---|---|---|
| PeerAR[-1] | 2790 | -0.0010 | 0.0277 | -0.1559 | -0.0026 | 0.1834 |
| PeerAR[0] | 2790 | -0.0025 | 0.0290 | -0.1950 | -0.0023 | 0.1834 |
| PeerAR[+1] | 2790 | -0.0021 | 0.0292 | -0.1844 | -0.0025 | 0.1605 |
| PeerCAR[0,+1] | 2790 | -0.0046 | 0.0414 | -0.2340 | -0.0042 | 0.2156 |
| PeerCAR[-1,+1] | 2790 | -0.0056 | 0.0490 | -0.2336 | -0.0058 | 0.2878 |
| DetailDensity | 2790 | 5.0747 | 3.4412 | 0.0000 | 4.3605 | 30.0000 |
| Spec | 2790 | 0.0298 | 0.9778 | -1.4902 | -0.1750 | 4.2363 |
| AIActive | 2790 | 0.4491 | 0.4974 | 0.0000 | 0.0000 | 1.0000 |
| Spec x AIActive | 2790 | 0.0103 | 0.6758 | -1.4902 | 0.0000 | 4.2363 |
| PeerCAR[-10,-2] | 2790 | -0.0135 | 0.0896 | -0.3636 | -0.0162 | 0.6994 |
| PeerCAR[-20,-2] | 2789 | -0.0275 | 0.1269 | -0.5388 | -0.0277 | 0.6518 |
| PeerRank | 2790 | 5.4846 | 2.8697 | 1.0000 | 5.0000 | 10.0000 |
| PeerSimilarity | 2790 | 0.3600 | 0.0912 | 0.0530 | 0.3628 | 0.8680 |
| TextHistory | 2790 | 0.7097 | 0.4539 | 0.0000 | 1.0000 | 1.0000 |
| SnippetFallback | 2790 | 0.0742 | 0.2621 | 0.0000 | 0.0000 | 1.0000 |

## Table 2 Peer-Firm Event Study Main Effect

| 窗口 | 均值 | 标准误 | p值 | 中位数 | 正收益比例 | 观测值 | 事件数 | 同行公司数 |
|---|---|---|---|---|---|---|---|---|
| AR[-1] | -0.0010 | (0.0010) | 0.3350 | -0.0026 | 0.4520 | 2790 | 316 | 1385 |
| AR[0] | -0.0025** | (0.0011) | 0.0205 | -0.0023 | 0.4577 | 2790 | 316 | 1385 |
| AR[+1] | -0.0021* | (0.0011) | 0.0541 | -0.0025 | 0.4434 | 2790 | 316 | 1385 |
| CAR[0,+1] | -0.0046*** | (0.0016) | 0.0045 | -0.0042 | 0.4344 | 2790 | 316 | 1385 |
| CAR[-1,+1] | -0.0056*** | (0.0019) | 0.0027 | -0.0058 | 0.4312 | 2790 | 316 | 1385 |

## Table 3 Disclosure Specificity Mechanism/Heterogeneity

| 变量 | (1) | (2) | (3) | (4) | (5) | (6) |
|---|---|---|---|---|---|---|
|  | PeerCAR[0,+1] | PeerCAR[0,+1] | PeerCAR[0,+1] | PeerAR[0] | PeerCAR[-1,+1] | PeerCAR[0,+1] |
|  | 事件固定效应 | 加入预收益控制 | Peer公司固定效应 | 替换被解释变量 | 替换被解释变量 | 替换AI口径 |
| Spec | - | - | - | - | - | - |
| Spec x AIActive | -0.0034*** | -0.0033*** | -0.0010 | -0.0019** | -0.0028* | 0.0021 |
|  | (0.0012) | (0.0012) | (0.0018) | (0.0008) | (0.0016) | (0.0018) |
| AIActive / TextHistory | -0.0013 | -0.0013 | 0.0023 | 0.0000 | -0.0014 | 0.0014 |
|  | (0.0013) | (0.0014) | (0.0037) | (0.0010) | (0.0017) | (0.0020) |
| PeerCAR[-10,-2] |  | -0.0016 | -0.0256 | 0.0111 | -0.0095 | -0.0020 |
|  |  | (0.0158) | (0.0193) | (0.0117) | (0.0215) | (0.0159) |
| PeerCAR[-20,-2] |  | -0.0001 | 0.0065 | -0.0061 | 0.0029 | -0.0004 |
|  |  | (0.0111) | (0.0142) | (0.0081) | (0.0142) | (0.0111) |
| Event FE | YES | YES | YES | YES | YES | YES |
| Peer Firm FE | NO | NO | YES | NO | NO | NO |
| N | 2789 | 2789 | 2789 | 2789 | 2789 | 2789 |
| Events | 316 | 316 | 316 | 316 | 316 | 316 |
| Peer firms | 1384 | 1384 | 1384 | 1384 | 1384 | 1384 |
| Overall R2 | 0.481 | 0.481 | 0.749 | 0.438 | 0.439 | 0.481 |
| Within R2 | 0.003 | 0.003 | 0.003 | 0.002 | 0.002 | 0.001 |

## Notes

- `Spec` is the winsorized and standardized `DetailDensity` measure.
- `Spec` itself is absorbed by event fixed effects in Table 3 because specificity is event-level.
- `Overall R2` includes the explanatory power of fixed effects; `Within R2` is the incremental explanatory power after absorbing fixed effects.
- The main interpretation is: GenAI disclosures reduce product-market peer valuations on average; more specific disclosures further reduce returns of AI-active product-market peers.
- `***`, `**`, and `*` indicate significance at 1%, 5%, and 10%.

## Output Files

- `results/v28_v36_peer_main_effect_tables_20260605/table1_descriptive_statistics.csv`
- `results/v28_v36_peer_main_effect_tables_20260605/table2_peer_event_study_main_effect.csv`
- `results/v28_v36_peer_main_effect_tables_20260605/table2_peer_event_study_main_effect_raw.csv`
- `results/v28_v36_peer_main_effect_tables_20260605/table3_specificity_mechanism_regressions.csv`
- `results/v28_v36_peer_main_effect_tables_20260605/table3_specificity_mechanism_regressions_raw.csv`
- `results/v28_v36_peer_main_effect_tables_20260605/sample_metadata.csv`
- `results/v28_v36_peer_main_effect_tables_20260605/v28_v36_peer_main_effect_tables_20260605.xlsx`
