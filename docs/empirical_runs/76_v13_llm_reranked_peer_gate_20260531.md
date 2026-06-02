# v13 LLM/Semantic Re-ranked Peer Gate

日期：2026-05-31

## Purpose

This file converts the LLM peer candidate menu into an actual code-safe
LLM/semantic re-ranked Top5 peer network and evaluates it using the same
return-comovement and fundamentals-comovement gates.

The network is "code-safe" because the LLM/semantic selection is restricted to a
candidate menu built from observable A-share peer systems. This follows the
spirit of LLM peer identification while avoiding hallucinated stock codes.

## Outputs

```text
results/v13_peer_validity_gate_20260531/llm_semantic_reranked_peer_network_top5_200.csv
results/v13_peer_validity_gate_20260531/llm_semantic_reranked_return_gate_200.csv
results/v13_peer_validity_gate_20260531/llm_semantic_reranked_fundamental_gate_200.csv
```

## Selected Candidate Source Mix

| candidate_source_system   |   selected_pairs |   mean_rank |   direct_share |   mean_score |
|:--------------------------|-----------------:|------------:|---------------:|-------------:|
| csmar_scope               |              383 |      2.8303 |         0.812  |       2.3655 |
| annual_same_industry      |              358 |      2.8408 |         0.8966 |       2.648  |
| random_same_industry      |              256 |      3.4688 |         0.8594 |       2.7188 |
| annual_global_ai_stripped |                3 |      3.6667 |         1      |       2      |

## Return-Comovement Gate, Matched 200-Focal Sample, 2025-2026

| peer_system                         |   pair_count |   focal_firms_with_returns |   mean_abret_corr |   median_abret_corr |   mean_raw_corr |   median_raw_corr |
|:------------------------------------|-------------:|---------------------------:|------------------:|--------------------:|----------------:|------------------:|
| annual_same_industry_2024_top5      |          419 |                         75 |            0.4359 |              0.4346 |          0.5855 |            0.6037 |
| llm_semantic_reranked_top5          |         1000 |                        178 |            0.3998 |              0.3981 |          0.5381 |            0.5414 |
| annual_global_ai_stripped_2024_top5 |          420 |                         75 |            0.3939 |              0.4224 |          0.5534 |            0.5778 |
| csmar_scope_top5                    |         1000 |                        178 |            0.3462 |              0.308  |          0.5017 |            0.488  |
| random_same_industry_top5           |          965 |                        171 |            0.3118 |              0.3169 |          0.4806 |            0.481  |
| low_similarity_same_industry_top5   |          965 |                        171 |            0.2432 |              0.257  |          0.4294 |            0.4316 |

## Fundamentals Gate, Matched 200-Focal Sample, 2025

| peer_system                         | metric            |    corr |      p |   n_focal |   focal_firms |
|:------------------------------------|:------------------|--------:|-------:|----------:|--------------:|
| csmar_scope_top5                    | sales_growth_2025 |  0.2185 | 0.0022 |       195 |           195 |
| csmar_scope_top5                    | gross_margin_2025 |  0.1955 | 0.0077 |       185 |           195 |
| annual_same_industry_2024_top5      | sales_growth_2025 | -0.0373 | 0.7365 |        84 |            84 |
| annual_same_industry_2024_top5      | gross_margin_2025 |  0.5217 | 0      |        78 |            84 |
| annual_global_ai_stripped_2024_top5 | sales_growth_2025 |  0.1656 | 0.1321 |        84 |            84 |
| annual_global_ai_stripped_2024_top5 | gross_margin_2025 |  0.4713 | 0      |        78 |            84 |
| random_same_industry_top5           | sales_growth_2025 | -0.087  | 0.2339 |       189 |           189 |
| random_same_industry_top5           | gross_margin_2025 |  0.3897 | 0      |       179 |           189 |
| low_similarity_same_industry_top5   | sales_growth_2025 | -0.303  | 0      |       188 |           188 |
| low_similarity_same_industry_top5   | gross_margin_2025 |  0.3666 | 0      |       179 |           188 |
| llm_semantic_reranked_top5          | sales_growth_2025 |  0.2169 | 0.0023 |       196 |           196 |
| llm_semantic_reranked_top5          | gross_margin_2025 |  0.4763 | 0      |       186 |           196 |

## Reading

This completes a first LLM/semantic peer-system pass. The resulting network is
not an unconstrained LLM peer list; it is an auditable LLM-style re-ranking from
literature-backed candidate systems.

The key comparison should be made on the matched 200-focal sample:

```text
If the LLM/semantic re-ranked network beats random and low-similarity systems on
return and fundamentals comovement, it passes the validity gate.

If it does not beat annual same-industry text peers, then annual-report text
peers remain the measurement-clean benchmark.
```
