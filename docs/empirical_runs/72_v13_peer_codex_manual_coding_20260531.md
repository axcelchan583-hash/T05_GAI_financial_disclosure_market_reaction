# v13 Codex-Assisted Manual Peer Coding

日期：2026-05-31

## Purpose

This file records an independent LLM-assisted semantic review of the 150-pair
peer-system validation template. It is not the same as the earlier Jaccard proxy:
the coding uses product/customer/use-case categories extracted from firm names,
industries, and business-scope excerpts.

## Output

```text
data/peer_validity_llm_20260531/peer_system_validation_coded_150_pairs_codex_20260531.csv
results/v13_peer_validity_gate_20260531/peer_system_validation_coded_150_pairs_codex_summary.csv
```

## Coding Scale

```text
3 = close direct competitor: similar product/service and similar customer/use case
2 = related product-market peer: same broad market, but products/customers differ
1 = weakly related: same industry label or supply-chain relation, not direct competitor
0 = not a product-market competitor
```

`direct_peer_share` treats scores 2 and 3 as product-market peers.

## Summary

| peer_system                         |   pairs |   mean_score |   direct_peer_share |   score_3_share |   score_0_share |
|:------------------------------------|--------:|-------------:|--------------------:|----------------:|----------------:|
| csmar_scope_top5                    |      30 |       2.2667 |              0.8000 |          0.6000 |          0.1333 |
| annual_same_industry_2024_top5      |      30 |       2.2333 |              0.7333 |          0.5000 |          0.0000 |
| annual_global_ai_stripped_2024_top5 |      30 |       2.1000 |              0.7333 |          0.5667 |          0.2000 |
| random_same_industry_top5           |      30 |       1.8667 |              0.5333 |          0.3333 |          0.0000 |
| low_similarity_same_industry_top5   |      30 |       1.5667 |              0.3000 |          0.2667 |          0.0000 |

## Reading

This semantic review is not identical to the statistical gates:

```text
Codex semantic coding:
    CSMAR scope peers are slightly higher than annual same-industry peers
    on this 150-pair sampled review.

Return/fundamental/proxy gates:
    annual same-industry annual-report peers remain the strongest measurement-clean system.
```

The key point is therefore more nuanced:

```text
CSMAR scope peers survive manual inspection and are not merely a statistical artefact.
Annual same-industry annual-report peers remain the literature-clean benchmark.
Random and low-similarity same-industry peers are meaningfully weaker in this
semantic coding pass.
```

Thus, the CSMAR scope network can be defended as "valid but not dominant."
