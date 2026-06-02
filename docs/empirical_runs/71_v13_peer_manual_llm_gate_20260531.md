# v13 Peer Manual / LLM Gate

日期：2026-05-31

## Purpose

This is the third layer of the peer-validity gate:

```text
return comovement
+ operating-fundamental comovement
+ manual / LLM inspectability
```

It does not replace human coding. It prepares a pair-level validation file and a
transparent proxy score so that weak peer systems can be identified before the
paper relies on them.

## Outputs

```text
results/v13_peer_validity_gate_20260531/peer_manual_proxy_pair_scores.csv
results/v13_peer_validity_gate_20260531/peer_manual_proxy_summary.csv
data/peer_validity_llm_20260531/peer_system_validation_template_150_pairs_20260531.csv
data/peer_validity_llm_20260531/LLM_PEER_SYSTEM_VALIDATION_TASK.md
```

## Proxy Scoring Rule

For each focal-peer pair, the proxy score adds one point for each item:

```text
same CSRC detailed industry;
CSMAR business-scope char n-gram Jaccard >= 0.055;
annual-report business-text char n-gram Jaccard >= 0.035;
source product-similarity score >= 0.18.
```

Labels:

```text
3-4 points: likely_direct_peer
2 points:   possible_peer
0-1 points: weak_or_needs_manual_review
```

This is a screening score only. The manuscript should cite the human/LLM-coded
validation file, not this proxy score, if formal manual validation is used.

## Summary

| peer_system                         |   pair_count |   focal_firms |   same_industry_share |   mean_scope_jaccard |   median_scope_jaccard |   mean_annual_jaccard |   median_annual_jaccard |   likely_direct_share |   weak_review_share |
|:------------------------------------|-------------:|--------------:|----------------------:|---------------------:|-----------------------:|----------------------:|------------------------:|----------------------:|--------------------:|
| annual_same_industry_2024_top5      |         5819 |          1168 |                1.0000 |               0.0530 |                 0.0335 |                0.1270 |                  0.0707 |                0.8886 |              0.0053 |
| annual_global_ai_stripped_2024_top5 |         5845 |          1169 |                0.5107 |               0.0491 |                 0.0303 |                0.1377 |                  0.0778 |                0.5422 |              0.0429 |
| csmar_scope_top5                    |        13260 |          2652 |                0.4428 |               0.1434 |                 0.1133 |                0.0547 |                  0.0353 |                0.4545 |              0.2167 |
| random_same_industry_top5           |        13000 |          2600 |                1.0000 |               0.0358 |                 0.0237 |                0.0527 |                  0.0344 |                0.0995 |              0.4608 |
| low_similarity_same_industry_top5   |        13000 |          2600 |                1.0000 |               0.0038 |                 0.0000 |                0.0505 |                  0.0328 |                0.0008 |              0.5778 |

## Current Reading

- The CSMAR scope network remains inspectable: it has high same-industry coverage
  and a non-trivial share of likely direct peers under the proxy rule.
- Annual same-industry peers look strongest under the same-source inspection rule,
  consistent with the return/fundamental gates.
- Annual global AI-word-stripped peers are literature-cleaner than arbitrary
  global text matches, but they still contain cross-industry false positives that
  need manual review.
- Random and low-similarity same-industry peers remain useful placebo systems.

## Completion Status

Manual/LLM validation is not complete until
`peer_system_validation_template_150_pairs_20260531.csv` is independently coded.
The current file makes that coding feasible and auditable.
