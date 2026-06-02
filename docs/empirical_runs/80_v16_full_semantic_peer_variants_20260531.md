# v16 Full Semantic Peer Variants

Date: 2026-05-31

Purpose: decompose the full semantic re-ranked peer result by candidate pool.
This addresses whether the replacement peer network is truly independent of the
old CSMAR scope network and whether random same-industry candidates are carrying
the result.

The base v16 full semantic result is documented in:

```text
docs/empirical_runs/79_v16_full_semantic_reranked_peers_20260531.md
```

## Coverage

| peer_source      |   raw_rows |   raw_events |   raw_focal_firms |   raw_peer_firms |   raw_top5_rows |   mean_peer_similarity_top5 |   median_peer_similarity_top5 |
|:-----------------|-----------:|-------------:|------------------:|-----------------:|----------------:|----------------------------:|------------------------------:|
| all_candidates   |     201240 |        20124 |              2652 |             5343 |          100620 |                      0.3197 |                        0.3387 |
| no_random        |     201240 |        20124 |              2652 |             5251 |          100620 |                      0.3366 |                        0.3451 |
| annual_only      |     169819 |        16982 |              1169 |             3360 |           84910 |                      0.3711 |                        0.3681 |
| annual_same_only |     169094 |        16968 |              1168 |             3354 |           84716 |                      0.3696 |                        0.3669 |
| csmar_scope_only |     190476 |        20124 |              2652 |             5213 |          100542 |                      0.2218 |                        0.1823 |

## Source Mix

| variant          | candidate_source_system   |   selected_pairs |   mean_rank |   direct_share |   mean_score |   mean_similarity |
|:-----------------|:--------------------------|-----------------:|------------:|---------------:|-------------:|------------------:|
| all_candidates   | csmar_scope               |             9686 |     5.1307  |       0.735288 |      2.156   |         0.221236  |
| all_candidates   | annual_same_industry      |             9167 |     5.16439 |       0.712556 |      2.27555 |         0.349036  |
| all_candidates   | random_same_industry      |             7503 |     6.34813 |       0.733307 |      2.46648 |         0.0623348 |
| all_candidates   | annual_global_ai_stripped |              164 |     7.26829 |       0.981707 |      2.06098 |         0.329741  |
| no_random        | csmar_scope               |            16783 |     5.63344 |       0.581064 |      1.59495 |         0.206767  |
| no_random        | annual_same_industry      |             9488 |     5.2089  |       0.707209 |      2.25116 |         0.349883  |
| no_random        | annual_global_ai_stripped |              249 |     7.59839 |       0.987952 |      2.04016 |         0.336027  |
| annual_only      | annual_same_industry      |            10853 |     5.4091  |       0.634663 |      2.1102  |         0.347085  |
| annual_only      | annual_global_ai_stripped |              836 |     6.67464 |       0.905502 |      1.84809 |         0.34861   |
| annual_same_only | annual_same_industry      |            11569 |     5.48215 |       0.595471 |      2.04158 |         0.343406  |
| csmar_scope_only | csmar_scope               |            25505 |     5.35287 |       0.50249  |      1.45011 |         0.202887  |

## Main Effects

Specification:

```text
PeerCAR[0,+1] = beta * Specificity_z x AIActivePeer
              + AIActivePeer
              + PeerCAR[-10,-2] + PeerCAR[-20,-2]
              + event FE + peer industry-week FE
```

Sample: first focal GenAI events, announcement-cleaned observations.

| peer_source      |   top_n | ai_def               |    coef |     se |      p |   nobs |   events |   focal_firms |   peer_firms |   mean_y |   mean_ai |
|:-----------------|--------:|:---------------------|--------:|-------:|-------:|-------:|---------:|--------------:|-------------:|---------:|----------:|
| all_candidates   |       5 | ext_any              | -0.0016 | 0.0008 | 0.0545 |   8412 |     2414 |          2414 |         3468 |  -0.0006 |    0.2165 |
| all_candidates   |       5 | current_text_history | -0.0019 | 0.0008 | 0.0146 |   8412 |     2414 |          2414 |         3468 |  -0.0006 |    0.3002 |
| all_candidates   |       5 | ext_no_hiring        | -0.0045 | 0.0023 | 0.0556 |   8412 |     2414 |          2414 |         3468 |  -0.0006 |    0.0219 |
| all_candidates   |       5 | ext_plus_history     | -0.0017 | 0.0007 | 0.0183 |   8412 |     2414 |          2414 |         3468 |  -0.0006 |    0.351  |
| all_candidates   |      10 | ext_any              | -0.0008 | 0.0006 | 0.1321 |  16704 |     2426 |          2426 |         4321 |  -0.0005 |    0.2192 |
| all_candidates   |      10 | current_text_history | -0.0011 | 0.0006 | 0.0444 |  16704 |     2426 |          2426 |         4321 |  -0.0005 |    0.2993 |
| all_candidates   |      10 | ext_no_hiring        | -0.0024 | 0.0019 | 0.1953 |  16704 |     2426 |          2426 |         4321 |  -0.0005 |    0.0219 |
| all_candidates   |      10 | ext_plus_history     | -0.0007 | 0.0005 | 0.1835 |  16704 |     2426 |          2426 |         4321 |  -0.0005 |    0.3512 |
| no_random        |       5 | ext_any              | -0.002  | 0.0008 | 0.0154 |   8572 |     2413 |          2413 |         3495 |  -0.0006 |    0.2187 |
| no_random        |       5 | current_text_history | -0.0021 | 0.0007 | 0.006  |   8572 |     2413 |          2413 |         3495 |  -0.0006 |    0.2982 |
| no_random        |       5 | ext_no_hiring        | -0.0048 | 0.0029 | 0.0956 |   8572 |     2413 |          2413 |         3495 |  -0.0006 |    0.0208 |
| no_random        |       5 | ext_plus_history     | -0.0024 | 0.0007 | 0.0008 |   8572 |     2413 |          2413 |         3495 |  -0.0006 |    0.3494 |
| no_random        |      10 | ext_any              | -0.0011 | 0.0006 | 0.0599 |  17133 |     2428 |          2428 |         4395 |  -0.0005 |    0.2172 |
| no_random        |      10 | current_text_history | -0.0011 | 0.0006 | 0.0677 |  17133 |     2428 |          2428 |         4395 |  -0.0005 |    0.2983 |
| no_random        |      10 | ext_no_hiring        | -0.0028 | 0.0018 | 0.1171 |  17133 |     2428 |          2428 |         4395 |  -0.0005 |    0.0215 |
| no_random        |      10 | ext_plus_history     | -0.001  | 0.0005 | 0.07   |  17133 |     2428 |          2428 |         4395 |  -0.0005 |    0.3487 |
| annual_only      |       5 | ext_any              |  0      | 0.0011 | 0.9824 |   3540 |     1043 |          1043 |         1772 |  -0.0001 |    0.2777 |
| annual_only      |       5 | current_text_history | -0.0005 | 0.001  | 0.6187 |   3540 |     1043 |          1043 |         1772 |  -0.0001 |    0.4065 |
| annual_only      |       5 | ext_no_hiring        | -0.0011 | 0.0039 | 0.7762 |   3540 |     1043 |          1043 |         1772 |  -0.0001 |    0.0347 |
| annual_only      |       5 | ext_plus_history     | -0.0002 | 0.001  | 0.86   |   3540 |     1043 |          1043 |         1772 |  -0.0001 |    0.4669 |
| annual_only      |      10 | ext_any              |  0.0003 | 0.0008 | 0.7022 |   7137 |     1050 |          1050 |         2573 |   0      |    0.2843 |
| annual_only      |      10 | current_text_history | -0.0004 | 0.0009 | 0.6523 |   7137 |     1050 |          1050 |         2573 |   0      |    0.4031 |
| annual_only      |      10 | ext_no_hiring        |  0.0003 | 0.0026 | 0.8958 |   7137 |     1050 |          1050 |         2573 |   0      |    0.0352 |
| annual_only      |      10 | ext_plus_history     |  0.0004 | 0.0008 | 0.6624 |   7137 |     1050 |          1050 |         2573 |   0      |    0.4648 |
| annual_same_only |       5 | ext_any              |  0.0004 | 0.0011 | 0.7376 |   3511 |     1040 |          1040 |         1766 |   0.0001 |    0.2777 |
| annual_same_only |       5 | current_text_history | -0.0009 | 0.001  | 0.4004 |   3511 |     1040 |          1040 |         1766 |   0.0001 |    0.4073 |
| annual_same_only |       5 | ext_no_hiring        | -0.0001 | 0.004  | 0.9793 |   3511 |     1040 |          1040 |         1766 |   0.0001 |    0.0356 |
| annual_same_only |       5 | ext_plus_history     | -0.0003 | 0.0011 | 0.7719 |   3511 |     1040 |          1040 |         1766 |   0.0001 |    0.47   |
| annual_same_only |      10 | ext_any              |  0.0002 | 0.0008 | 0.8158 |   7047 |     1047 |          1047 |         2559 |  -0.0001 |    0.2855 |
| annual_same_only |      10 | current_text_history | -0.0004 | 0.0009 | 0.6741 |   7047 |     1047 |          1047 |         2559 |  -0.0001 |    0.4064 |
| annual_same_only |      10 | ext_no_hiring        |  0.0006 | 0.0028 | 0.8277 |   7047 |     1047 |          1047 |         2559 |  -0.0001 |    0.0353 |
| annual_same_only |      10 | ext_plus_history     |  0.0004 | 0.0008 | 0.6394 |   7047 |     1047 |          1047 |         2559 |  -0.0001 |    0.4697 |
| csmar_scope_only |       5 | ext_any              | -0.0021 | 0.0009 | 0.0192 |   8601 |     2418 |          2418 |         3520 |  -0.0008 |    0.2106 |
| csmar_scope_only |       5 | current_text_history | -0.0018 | 0.0009 | 0.0388 |   8601 |     2418 |          2418 |         3520 |  -0.0008 |    0.2776 |
| csmar_scope_only |       5 | ext_no_hiring        | -0.0065 | 0.0026 | 0.013  |   8601 |     2418 |          2418 |         3520 |  -0.0008 |    0.0192 |
| csmar_scope_only |       5 | ext_plus_history     | -0.0026 | 0.0008 | 0.0016 |   8601 |     2418 |          2418 |         3520 |  -0.0008 |    0.3289 |
| csmar_scope_only |      10 | ext_any              | -0.0014 | 0.0006 | 0.0258 |  16546 |     2431 |          2431 |         4463 |  -0.0008 |    0.2074 |
| csmar_scope_only |      10 | current_text_history | -0.0015 | 0.0007 | 0.0201 |  16546 |     2431 |          2431 |         4463 |  -0.0008 |    0.2724 |
| csmar_scope_only |      10 | ext_no_hiring        | -0.0031 | 0.0021 | 0.1486 |  16546 |     2431 |          2431 |         4463 |  -0.0008 |    0.0195 |
| csmar_scope_only |      10 | ext_plus_history     | -0.0015 | 0.0006 | 0.0144 |  16546 |     2431 |          2431 |         4463 |  -0.0008 |    0.3214 |

## Reading Rule

- `no_random` is the cleaner candidate-pool version for a paper table.
- `annual_only` is the most literature-clean annual-report text version.
- `csmar_scope_only` tests whether the old result is simply reappearing through
  the old CSMAR business-scope candidates.
