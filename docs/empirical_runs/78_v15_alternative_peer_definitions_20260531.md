# v15 Alternative Peer Definitions

Date: 2026-05-31

Purpose: try peer definitions with clearer literature support beyond the old
CSMAR scope peer network.

## Peer Systems

1. `patent_fine_ipc_lagged`: lagged fine patent-class vectors. This follows the
   technological-proximity tradition (Jaffe-style technology space; Bloom,
   Schankerman, and Van Reenen-style technology spillovers; Cao, Ma, Tucker, and
   Wan-style technological peer pressure).
2. `common_analyst_lagged`: lagged common analyst / brokerage coverage. This
   follows the common-analyst / information-peer tradition.
3. `llm_semantic_reranked_200`: code-safe semantic re-ranking from the existing
   200-focal LLM/semantic gate.

## Coverage

| peer_source               |   raw_rows |   raw_events |   raw_focal_firms |   raw_peer_firms |   raw_top5_rows |   mean_peer_similarity_top5 |   median_peer_similarity_top5 |
|:--------------------------|-----------:|-------------:|------------------:|-----------------:|----------------:|----------------------------:|------------------------------:|
| patent_fine_ipc_lagged    |     130310 |        13031 |              1764 |             3660 |           65155 |                      0.9423 |                        0.9815 |
| common_analyst_lagged     |     140747 |        14075 |              1732 |             3580 |           70375 |                      0.5582 |                        0.5345 |
| llm_semantic_reranked_200 |       6005 |         1201 |               200 |              820 |            6005 |                      0.324  |                        0.3746 |

## Main Effects

Specification:

```text
PeerCAR[0,+1] = beta * Specificity_z x AIActivePeer
              + AIActivePeer
              + PeerCAR[-10,-2] + PeerCAR[-20,-2]
              + event FE + peer industry-week FE
```

Sample: first focal GenAI events, announcement-cleaned observations.

| peer_source               |   top_n | ai_def               |    coef |     se |      p |   nobs |   events |   focal_firms |   peer_firms |   mean_y |   mean_ai |
|:--------------------------|--------:|:---------------------|--------:|-------:|-------:|-------:|---------:|--------------:|-------------:|---------:|----------:|
| patent_fine_ipc_lagged    |       5 | ext_any              |  0.001  | 0.0011 | 0.3869 |   5307 |     1510 |          1510 |         2137 |  -0.0003 |    0.2687 |
| patent_fine_ipc_lagged    |       5 | current_text_history |  0.001  | 0.0012 | 0.4219 |   5307 |     1510 |          1510 |         2137 |  -0.0003 |    0.3037 |
| patent_fine_ipc_lagged    |       5 | ext_no_hiring        | -0.0009 | 0.0026 | 0.7312 |   5307 |     1510 |          1510 |         2137 |  -0.0003 |    0.0268 |
| patent_fine_ipc_lagged    |       5 | ext_plus_history     |  0.0009 | 0.0012 | 0.4608 |   5307 |     1510 |          1510 |         2137 |  -0.0003 |    0.3716 |
| patent_fine_ipc_lagged    |      10 | ext_any              | -0.0002 | 0.0007 | 0.8015 |  10405 |     1513 |          1513 |         2748 |  -0.0004 |    0.2716 |
| patent_fine_ipc_lagged    |      10 | current_text_history |  0.0007 | 0.0007 | 0.3223 |  10405 |     1513 |          1513 |         2748 |  -0.0004 |    0.3087 |
| patent_fine_ipc_lagged    |      10 | ext_no_hiring        |  0.0024 | 0.0015 | 0.1259 |  10405 |     1513 |          1513 |         2748 |  -0.0004 |    0.0259 |
| patent_fine_ipc_lagged    |      10 | ext_plus_history     |  0.0006 | 0.0007 | 0.3905 |  10405 |     1513 |          1513 |         2748 |  -0.0004 |    0.3749 |
| common_analyst_lagged     |       5 | ext_any              | -0.0013 | 0.0015 | 0.381  |   5073 |     1408 |          1408 |         2191 |  -0      |    0.2653 |
| common_analyst_lagged     |       5 | current_text_history | -0.0007 | 0.0013 | 0.5977 |   5073 |     1408 |          1408 |         2191 |  -0      |    0.2925 |
| common_analyst_lagged     |       5 | ext_no_hiring        | -0.0067 | 0.0055 | 0.2227 |   5073 |     1408 |          1408 |         2191 |  -0      |    0.0197 |
| common_analyst_lagged     |       5 | ext_plus_history     | -0.0009 | 0.0013 | 0.4731 |   5073 |     1408 |          1408 |         2191 |  -0      |    0.3607 |
| common_analyst_lagged     |      10 | ext_any              |  0      | 0.0008 | 0.9631 |  10165 |     1420 |          1420 |         2751 |  -0.0002 |    0.2638 |
| common_analyst_lagged     |      10 | current_text_history | -0.0012 | 0.0008 | 0.1238 |  10165 |     1420 |          1420 |         2751 |  -0.0002 |    0.2996 |
| common_analyst_lagged     |      10 | ext_no_hiring        | -0.0016 | 0.0025 | 0.5307 |  10165 |     1420 |          1420 |         2751 |  -0.0002 |    0.0214 |
| common_analyst_lagged     |      10 | ext_plus_history     | -0.0013 | 0.0007 | 0.0645 |  10165 |     1420 |          1420 |         2751 |  -0.0002 |    0.3661 |
| llm_semantic_reranked_200 |       5 | ext_any              | -0.0026 | 0.0021 | 0.2161 |    633 |      178 |           178 |          540 |  -0.0032 |    0.1501 |
| llm_semantic_reranked_200 |       5 | current_text_history | -0.005  | 0.0023 | 0.0324 |    633 |      178 |           178 |          540 |  -0.0032 |    0.237  |
| llm_semantic_reranked_200 |       5 | ext_no_hiring        | -0.0024 | 0.0028 | 0.3926 |    633 |      178 |           178 |          540 |  -0.0032 |    0.0047 |
| llm_semantic_reranked_200 |       5 | ext_plus_history     | -0.0048 | 0.0022 | 0.0273 |    633 |      178 |           178 |          540 |  -0.0032 |    0.2765 |

## Interpretation

- A usable replacement peer system should have enough event coverage and a
  stable negative coefficient under external `ext_any`.
- A peer system with strong literature support but null main effects is still
  useful as a replacement-test / falsification system, not as the headline peer
  definition.
- If only the old CSMAR scope peer system preserves the negative coefficient,
  the paper must either defend that old system directly or abandon the current
  competitive-risk main-effect framing.
