# v16 Full-Sample Semantic Re-ranked Peer Network

Date: 2026-05-31

Purpose: expand the v13 200-focal semantic peer re-ranking to the full focal-event
universe and test whether the current GenAI peer-CAR result survives under a
cleaner semantic product-market peer definition.

## Construction

Candidate peers are drawn from four auditable systems:

1. annual-report same-industry text Top10;
2. CSMAR business-scope text Top10;
3. annual-report global AI-word-stripped Top10;
4. random same-industry Top10, included only as a candidate pool stress test.

Candidates are re-ranked by the deterministic semantic product/category scorer
used in v13. This is an auditable LLM-style semantic reranking, not an external
API call and not a hand-picked peer list.

## Coverage

| peer_source            |   raw_rows |   raw_events |   raw_focal_firms |   raw_peer_firms |   raw_top5_rows |   mean_peer_similarity_top5 |   median_peer_similarity_top5 |
|:-----------------------|-----------:|-------------:|------------------:|-----------------:|----------------:|----------------------------:|------------------------------:|
| full_semantic_reranked |     201240 |        20124 |              2652 |             5343 |          100620 |                      0.3197 |                        0.3387 |

## Candidate Source Summary

| candidate_source_system   |   candidate_rows |   focal_firms |   mean_score |   direct_share |   mean_similarity |
|:--------------------------|-----------------:|--------------:|-------------:|---------------:|------------------:|
| csmar_scope               |            25505 |          2652 |     1.45011  |       0.50249  |         0.202887  |
| random_same_industry      |            24892 |          2599 |     1.85847  |       0.429254 |         0.0511408 |
| annual_same_industry      |            11569 |          1168 |     2.04158  |       0.595471 |         0.343406  |
| annual_global_ai_stripped |             6080 |          1081 |     0.638322 |       0.242105 |         0.376878  |

## Selected Source Mix

| candidate_source_system   |   selected_pairs |   mean_rank |   direct_share |   mean_score |   mean_similarity |
|:--------------------------|-----------------:|------------:|---------------:|-------------:|------------------:|
| csmar_scope               |             9686 |     5.1307  |       0.735288 |      2.156   |         0.221236  |
| annual_same_industry      |             9167 |     5.16439 |       0.712556 |      2.27555 |         0.349036  |
| random_same_industry      |             7503 |     6.34813 |       0.733307 |      2.46648 |         0.0623348 |
| annual_global_ai_stripped |              164 |     7.26829 |       0.981707 |      2.06098 |         0.329741  |

## Main Effects

Specification:

```text
PeerCAR[0,+1] = beta * Specificity_z x AIActivePeer
              + AIActivePeer
              + PeerCAR[-10,-2] + PeerCAR[-20,-2]
              + event FE + peer industry-week FE
```

Sample: first focal GenAI events, announcement-cleaned observations.

| peer_source            |   top_n | ai_def               |    coef |     se |      p |   nobs |   events |   focal_firms |   peer_firms |   mean_y |   mean_ai |
|:-----------------------|--------:|:---------------------|--------:|-------:|-------:|-------:|---------:|--------------:|-------------:|---------:|----------:|
| full_semantic_reranked |       3 | ext_any              | -0.0009 | 0.0013 | 0.4841 |   5044 |     2310 |          2310 |         2738 |  -0.0005 |    0.2123 |
| full_semantic_reranked |       3 | current_text_history | -0.002  | 0.0011 | 0.0596 |   5044 |     2310 |          2310 |         2738 |  -0.0005 |    0.2978 |
| full_semantic_reranked |       3 | ext_no_hiring        | -0.0028 | 0.0045 | 0.5312 |   5044 |     2310 |          2310 |         2738 |  -0.0005 |    0.0212 |
| full_semantic_reranked |       3 | ext_plus_history     | -0.0016 | 0.0011 | 0.1444 |   5044 |     2310 |          2310 |         2738 |  -0.0005 |    0.3479 |
| full_semantic_reranked |       5 | ext_any              | -0.0016 | 0.0008 | 0.0545 |   8412 |     2414 |          2414 |         3468 |  -0.0006 |    0.2165 |
| full_semantic_reranked |       5 | current_text_history | -0.0019 | 0.0008 | 0.0146 |   8412 |     2414 |          2414 |         3468 |  -0.0006 |    0.3002 |
| full_semantic_reranked |       5 | ext_no_hiring        | -0.0045 | 0.0023 | 0.0556 |   8412 |     2414 |          2414 |         3468 |  -0.0006 |    0.0219 |
| full_semantic_reranked |       5 | ext_plus_history     | -0.0017 | 0.0007 | 0.0183 |   8412 |     2414 |          2414 |         3468 |  -0.0006 |    0.351  |
| full_semantic_reranked |      10 | ext_any              | -0.0008 | 0.0006 | 0.1321 |  16704 |     2426 |          2426 |         4321 |  -0.0005 |    0.2192 |
| full_semantic_reranked |      10 | current_text_history | -0.0011 | 0.0006 | 0.0444 |  16704 |     2426 |          2426 |         4321 |  -0.0005 |    0.2993 |
| full_semantic_reranked |      10 | ext_no_hiring        | -0.0024 | 0.0019 | 0.1953 |  16704 |     2426 |          2426 |         4321 |  -0.0005 |    0.0219 |
| full_semantic_reranked |      10 | ext_plus_history     | -0.0007 | 0.0005 | 0.1835 |  16704 |     2426 |          2426 |         4321 |  -0.0005 |    0.3512 |

## Reading

This is the key go/no-go test for replacing the old CSMAR scope Top5 with a
cleaner semantic peer definition. A viable replacement should preserve a
negative and preferably significant coefficient for `ext_any` at Top5.

If `ext_any` is not negative/significant here, then the current peer-CAR result
cannot be described as robust to the full semantic product-market peer network.
