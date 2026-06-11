# v25 empirical table pack: specificity x AI-active peers

## Scope

This table pack formats the two currently significant main effects from the v24 specification grid.
Both use `E2_likely_or_possible`, `legacy_detail_density`, `ext_any`, strict prior-year product-market peers, and the outcome `PeerCAR[0,+1]`.

## v24 Anchor Results

| method_variant | coef | se | p | q_bh_all | nobs | events | peer_firms |
|---|---|---|---|---|---|---|---|
| liu_product_tfidf_global_top5 | -0.009192 | 0.002602 | 0.000412 | 0.079928 | 1469 | 337 | 796 |
| ren_wang_binary_global_top10 | -0.005841 | 0.001629 | 0.000337 | 0.072844 | 2951 | 338 | 1180 |

## Why the Two Main N's Differ

`N` is the number of event-peer observations, not the number of GenAI disclosure events.
The Ren-Wang significant specification uses global Top10 peers, while the Liu significant specification uses global Top5 peers; therefore the raw event-peer panel is roughly twice as large for Ren-Wang.
The final event counts are almost the same, so the N gap mainly comes from peer-set size rather than a different event sample.

| method_variant | TopN | E2_events_total | events_with_peer_links | raw_event_peer_rows | complete_clean_rows | final_regression_N | final_events | final_peer_firms | avg_final_rows_per_event |
|---|---|---|---|---|---|---|---|---|---|
| ren_wang_binary_global_top10 | 10 | 391 | 344 | 3440 | 2958 | 2951 | 338 | 1180 | 8.73 |
| liu_product_tfidf_global_top5 | 5 | 391 | 344 | 1720 | 1471 | 1469 | 337 | 796 | 4.36 |

## Ren-Wang binary product peer, global Top10

- Peer construction: Prior-year Ren-Wang-style binary product-term peer network; global Top10 peers.
- Main model: `PeerCAR[0,+1] = Spec x AIActivePeer + AIActivePeer + pre-event peer returns + event FE + peer-industry-week FE`.

### Table 1. 变量的描述性统计

| 变量 | 观测值 | 均值 | 标准差 | 最小值 | 中位数 | 最大值 |
|---|---|---|---|---|---|---|
| PeerCAR[0,+1] | 2951 | -0.0006 | 0.0397 | -0.2195 | -0.0022 | 0.2497 |
| DetailDensity | 2951 | 4.8163 | 3.4967 | 0.0000 | 4.1096 | 31.2500 |
| Spec | 2951 | -0.0204 | 0.9387 | -1.3580 | -0.2111 | 3.9842 |
| AIActive | 2951 | 0.4561 | 0.4981 | 0.0000 | 0.0000 | 1.0000 |
| Spec x AIActive | 2951 | -0.0145 | 0.6587 | -1.3580 | 0.0000 | 3.9842 |
| PeerCAR[-10,-2] | 2951 | -0.0114 | 0.0901 | -0.3593 | -0.0147 | 0.6994 |
| PeerCAR[-20,-2] | 2951 | -0.0234 | 0.1273 | -0.5438 | -0.0246 | 0.7968 |
| TextHistory | 2951 | 0.6872 | 0.4636 | 0.0000 | 1.0000 | 1.0000 |
| PeerRank | 2951 | 5.5293 | 2.8751 | 1.0000 | 6.0000 | 10.0000 |

### Table 2. 基准回归检验

| 变量 | (1) | (2) | (3) | (4) | (5) | (6) |
|---|---|---|---|---|---|---|
|  | 事件固定效应 | 加入预收益控制 | Peer行业x周 | Peer公司固定效应 | Peer行业周+公司 | 替换AI口径 |
| Spec x AIActive | -0.0027* | -0.0027* | -0.0059*** | -0.0030 | -0.0062*** | 0.0032 |
|  | (0.0015) | (0.0015) | (0.0016) | (0.0018) | (0.0020) | (0.0026) |
| AIActive / TextHistory | -0.0015 | -0.0016 | -0.0012 | -0.0011 | 0.0001 | 0.0013 |
|  | (0.0016) | (0.0016) | (0.0017) | (0.0029) | (0.0034) | (0.0021) |
| PeerCAR[-10,-2] |  | 0.0056 | 0.0063 | 0.0207 | 0.0266 | 0.0037 |
|  |  | (0.0186) | (0.0205) | (0.0233) | (0.0272) | (0.0207) |
| PeerCAR[-20,-2] |  | -0.0232** | -0.0218* | -0.0360** | -0.0324* | -0.0200 |
|  |  | (0.0117) | (0.0127) | (0.0145) | (0.0168) | (0.0128) |
| Event FE | YES | YES | YES | YES | YES | YES |
| PeerInd x Week FE | NO | NO | YES | NO | YES | YES |
| Peer Firm FE | NO | NO | NO | YES | YES | NO |
| N | 2951 | 2951 | 2951 | 2951 | 2951 | 2951 |
| Events | 338 | 338 | 338 | 338 | 338 | 338 |
| Peer firms | 1180 | 1180 | 1180 | 1180 | 1180 | 1180 |
| Overall R2 | 0.390 | 0.393 | 0.579 | 0.692 | 0.785 | 0.576 |
| Within R2 | 0.002 | 0.006 | 0.010 | 0.010 | 0.012 | 0.005 |

### Table 3. 稳健性检验

| 变量 | (1) | (2) | (3) | (4) | (5) | (6) | (7) |
|---|---|---|---|---|---|---|---|
|  | 首次事件 | Likely only | 替换TopN | 同行业内peer | 替换AI口径 | 替换X:文本具体性 | 替换X:机器成分 |
| Peer/Event/X | E4_first_likely_or_possible<br>ren_wang_binary_global_top10<br>legacy_detail_density | E3_likely_only<br>ren_wang_binary_global_top10<br>legacy_detail_density | E2_likely_or_possible<br>ren_wang_binary_global_top5<br>legacy_detail_density | E2_likely_or_possible<br>ren_wang_binary_same_industry_d_top10<br>legacy_detail_density | E2_likely_or_possible<br>ren_wang_binary_global_top10<br>legacy_detail_density | E2_likely_or_possible<br>ren_wang_binary_global_top10<br>genai_concreteness_raw | E2_likely_or_possible<br>ren_wang_binary_global_top10<br>machine_component_sum |
| X x AI proxy | -0.0043** | -0.0083** | -0.0046** | -0.0023 | 0.0032 | 0.0018 | 0.0028* |
|  | (0.0019) | (0.0039) | (0.0023) | (0.0015) | (0.0026) | (0.0018) | (0.0014) |
| 控制变量 | YES | YES | YES | YES | YES | YES | YES |
| Event FE | YES | YES | YES | YES | YES | YES | YES |
| PeerInd x Week FE | YES | YES | YES | YES | YES | YES | YES |
| N | 2257 | 753 | 1459 | 2986 | 2951 | 2951 | 2951 |
| Events | 258 | 88 | 338 | 337 | 338 | 338 | 338 |
| Peer firms | 1136 | 482 | 725 | 1305 | 1180 | 1180 | 1180 |
| Overall R2 | 0.585 | 0.599 | 0.699 | 0.447 | 0.576 | 0.576 | 0.577 |
| Within R2 | 0.007 | 0.018 | 0.011 | 0.010 | 0.005 | 0.004 | 0.005 |

## Liu product-TF-IDF peer, global Top5

- Peer construction: Prior-year Liu-style product TF-IDF peer network from CSMAR business text; global Top5 peers.
- Main model: `PeerCAR[0,+1] = Spec x AIActivePeer + AIActivePeer + pre-event peer returns + event FE + peer-industry-week FE`.

### Table 1. 变量的描述性统计

| 变量 | 观测值 | 均值 | 标准差 | 最小值 | 中位数 | 最大值 |
|---|---|---|---|---|---|---|
| PeerCAR[0,+1] | 1469 | -0.0005 | 0.0397 | -0.2340 | -0.0023 | 0.2011 |
| DetailDensity | 1469 | 4.8500 | 3.6081 | 0.0000 | 4.1096 | 31.2500 |
| Spec | 1469 | -0.0145 | 0.9501 | -1.3580 | -0.2111 | 3.9842 |
| AIActive | 1469 | 0.4894 | 0.4999 | 0.0000 | 0.0000 | 1.0000 |
| Spec x AIActive | 1469 | -0.0030 | 0.7026 | -1.3580 | 0.0000 | 3.9842 |
| PeerCAR[-10,-2] | 1469 | -0.0121 | 0.0851 | -0.3593 | -0.0155 | 0.6538 |
| PeerCAR[-20,-2] | 1469 | -0.0274 | 0.1251 | -0.7209 | -0.0280 | 0.6861 |
| TextHistory | 1469 | 0.7134 | 0.4522 | 0.0000 | 1.0000 | 1.0000 |
| PeerRank | 1469 | 2.9782 | 1.4155 | 1.0000 | 3.0000 | 5.0000 |

### Table 2. 基准回归检验

| 变量 | (1) | (2) | (3) | (4) | (5) | (6) |
|---|---|---|---|---|---|---|
|  | 事件固定效应 | 加入预收益控制 | Peer行业x周 | Peer公司固定效应 | Peer行业周+公司 | 替换AI口径 |
| Spec x AIActive | -0.0082*** | -0.0082*** | -0.0092*** | -0.0063 | -0.0072 | -0.0027 |
|  | (0.0021) | (0.0021) | (0.0026) | (0.0038) | (0.0044) | (0.0025) |
| AIActive / TextHistory | -0.0030 | -0.0030 | -0.0047** | -0.0026 | -0.0042 | -0.0024 |
|  | (0.0021) | (0.0021) | (0.0023) | (0.0059) | (0.0068) | (0.0030) |
| PeerCAR[-10,-2] |  | -0.0138 | 0.0116 | -0.0097 | 0.0391 | 0.0099 |
|  |  | (0.0256) | (0.0297) | (0.0463) | (0.0512) | (0.0303) |
| PeerCAR[-20,-2] |  | 0.0017 | -0.0122 | 0.0052 | -0.0224 | -0.0127 |
|  |  | (0.0149) | (0.0161) | (0.0250) | (0.0266) | (0.0168) |
| Event FE | YES | YES | YES | YES | YES | YES |
| PeerInd x Week FE | NO | NO | YES | NO | YES | YES |
| Peer Firm FE | NO | NO | NO | YES | YES | NO |
| N | 1469 | 1469 | 1469 | 1469 | 1469 | 1469 |
| Events | 337 | 337 | 337 | 337 | 337 | 337 |
| Peer firms | 796 | 796 | 796 | 796 | 796 | 796 |
| Overall R2 | 0.531 | 0.532 | 0.659 | 0.814 | 0.855 | 0.654 |
| Within R2 | 0.013 | 0.013 | 0.017 | 0.006 | 0.010 | 0.003 |

### Table 3. 稳健性检验

| 变量 | (1) | (2) | (3) | (4) | (5) | (6) | (7) |
|---|---|---|---|---|---|---|---|
|  | 首次事件 | Likely only | 替换TopN | 同行业内peer | 替换AI口径 | 替换X:文本具体性 | 替换X:机器成分 |
| Peer/Event/X | E4_first_likely_or_possible<br>liu_product_tfidf_global_top5<br>legacy_detail_density | E3_likely_only<br>liu_product_tfidf_global_top5<br>legacy_detail_density | E2_likely_or_possible<br>liu_product_tfidf_global_top10<br>legacy_detail_density | E2_likely_or_possible<br>liu_product_tfidf_same_industry_d_top5<br>legacy_detail_density | E2_likely_or_possible<br>liu_product_tfidf_global_top5<br>legacy_detail_density | E2_likely_or_possible<br>liu_product_tfidf_global_top5<br>genai_concreteness_raw | E2_likely_or_possible<br>liu_product_tfidf_global_top5<br>machine_component_sum |
| X x AI proxy | -0.0084*** | -0.0064 | -0.0037** | -0.0037 | -0.0027 | -0.0011 | 0.0020 |
|  | (0.0031) | (0.0072) | (0.0016) | (0.0025) | (0.0025) | (0.0025) | (0.0023) |
| 控制变量 | YES | YES | YES | YES | YES | YES | YES |
| Event FE | YES | YES | YES | YES | YES | YES | YES |
| PeerInd x Week FE | YES | YES | YES | YES | YES | YES | YES |
| N | 1123 | 379 | 2923 | 1502 | 1469 | 1469 | 1469 |
| Events | 257 | 87 | 338 | 338 | 337 | 337 | 337 |
| Peer firms | 765 | 291 | 1284 | 820 | 796 | 796 | 796 |
| Overall R2 | 0.668 | 0.656 | 0.582 | 0.540 | 0.654 | 0.654 | 0.655 |
| Within R2 | 0.014 | 0.014 | 0.010 | 0.006 | 0.003 | 0.004 | 0.005 |

## Notes

- Parentheses report two-way clustered standard errors by event and peer firm.
- `***`, `**`, and `*` denote significance at 1%, 5%, and 10%, respectively.
- `Spec` is the within-event-definition winsorized z-score of the stated specificity measure.
- These are result-organization tables for the current working specification, not a final manuscript table set.

## Output Files

- `results/v25_empirical_table_pack_20260604/ren_wang_binary_global_top10_table1_descriptive.csv`
- `results/v25_empirical_table_pack_20260604/ren_wang_binary_global_top10_table2_baseline.csv`
- `results/v25_empirical_table_pack_20260604/ren_wang_binary_global_top10_table3_robustness.csv`
- `results/v25_empirical_table_pack_20260604/liu_product_tfidf_global_top5_table1_descriptive.csv`
- `results/v25_empirical_table_pack_20260604/liu_product_tfidf_global_top5_table2_baseline.csv`
- `results/v25_empirical_table_pack_20260604/liu_product_tfidf_global_top5_table3_robustness.csv`
- `results/v25_empirical_table_pack_20260604/main_effect_sample_flow.csv`
- `results/v25_empirical_table_pack_20260604/v25_empirical_table_pack_20260604.xlsx`
