# v20 DeepSeek Candidate-Menu Placebo Peers

Date: 2026-06-01

Purpose: rebuild random and low-similarity placebo peer sets from the same
candidate menu used by the v17 DeepSeek Flash-selected Top5 network. This
holds the auditable candidate universe fixed and excludes the actual
DeepSeek-selected Top5 peers before constructing placebo peers.

## Construction

For each focal firm:

1. reconstruct the v17 no-random candidate menu, max 15 candidates;
2. remove the v17 DeepSeek-selected Top5 peers;
3. create `deepseek_candidate_low_similarity_top5` by choosing the remaining
   candidates with the lowest product similarity;
4. create `deepseek_candidate_random_top5` by drawing five remaining candidates
   using a deterministic focal-code seed.

These are falsification peers, not alternative headline peer definitions.

## Candidate Coverage

|   focal_firms_with_candidate_menu |   focal_firms_with_placebo_top5 |   mean_remaining_candidates |   median_remaining_candidates |
|----------------------------------:|--------------------------------:|----------------------------:|------------------------------:|
|                              2652 |                            2652 |                     7.72926 |                             8 |

## Event-Peer Coverage

| peer_source                            |   raw_rows |   raw_events |   raw_focal_firms |   raw_peer_firms |   raw_top5_rows |   mean_peer_similarity_top5 |   median_peer_similarity_top5 |
|:---------------------------------------|-----------:|-------------:|------------------:|-----------------:|----------------:|----------------------------:|------------------------------:|
| deepseek_candidate_low_similarity_top5 |     100620 |        20124 |              2652 |             4372 |          100620 |                      0.2163 |                        0.1809 |
| deepseek_candidate_random_top5         |     100620 |        20124 |              2652 |             4399 |          100620 |                      0.2847 |                        0.2934 |

## Candidate Source Mix

| network_name                           | candidate_source_system   |   selected_pairs |   mean_rank |   mean_similarity |
|:---------------------------------------|:--------------------------|-----------------:|------------:|------------------:|
| deepseek_candidate_low_similarity_top5 | csmar_scope               |            12141 |     2.94836 |          0.183555 |
| deepseek_candidate_low_similarity_top5 | annual_same_industry      |              795 |     3.63396 |          0.347971 |
| deepseek_candidate_low_similarity_top5 | annual_global_ai_stripped |              324 |     3.37963 |          0.324852 |
| deepseek_candidate_random_top5         | csmar_scope               |            10394 |     3.00298 |          0.197471 |
| deepseek_candidate_random_top5         | annual_same_industry      |             1503 |     2.95609 |          0.356005 |
| deepseek_candidate_random_top5         | annual_global_ai_stripped |             1363 |     3.02568 |          0.377252 |

## Main Effects

Specification:

```text
PeerCAR[0,+1] = beta * Specificity_z x AIActivePeer
              + AIActivePeer
              + PeerCAR[-10,-2] + PeerCAR[-20,-2]
              + event FE + peer industry-week FE
```

Sample: first focal GenAI events, announcement-cleaned observations.

| peer_source                            |   top_n | ai_def               |    coef |     se |      p |   nobs |   events |   focal_firms |   peer_firms |   mean_y |   mean_ai |
|:---------------------------------------|--------:|:---------------------|--------:|-------:|-------:|-------:|---------:|--------------:|-------------:|---------:|----------:|
| deepseek_candidate_low_similarity_top5 |       5 | ext_any              |  0.0001 | 0.001  | 0.9226 |   8388 |     2412 |          2412 |         3444 |  -0.0007 |    0.1944 |
| deepseek_candidate_low_similarity_top5 |       5 | current_text_history | -0.0007 | 0.001  | 0.4987 |   8388 |     2412 |          2412 |         3444 |  -0.0007 |    0.2758 |
| deepseek_candidate_low_similarity_top5 |       5 | ext_no_hiring        |  0.0045 | 0.0036 | 0.2117 |   8388 |     2412 |          2412 |         3444 |  -0.0007 |    0.0176 |
| deepseek_candidate_low_similarity_top5 |       5 | ext_plus_history     | -0.0006 | 0.0009 | 0.4898 |   8388 |     2412 |          2412 |         3444 |  -0.0007 |    0.3195 |
| deepseek_candidate_random_top5         |       5 | ext_any              | -0.0016 | 0.001  | 0.1067 |   8333 |     2411 |          2411 |         3438 |  -0.0003 |    0.1973 |
| deepseek_candidate_random_top5         |       5 | current_text_history | -0.0017 | 0.001  | 0.0915 |   8333 |     2411 |          2411 |         3438 |  -0.0003 |    0.2812 |
| deepseek_candidate_random_top5         |       5 | ext_no_hiring        | -0.0037 | 0.0031 | 0.2408 |   8333 |     2411 |          2411 |         3438 |  -0.0003 |    0.02   |
| deepseek_candidate_random_top5         |       5 | ext_plus_history     | -0.0015 | 0.0009 | 0.095  |   8333 |     2411 |          2411 |         3438 |  -0.0003 |    0.3235 |

## Reading

This is a stricter placebo than the older v6 random / low-similarity peer sets
because it uses the exact candidate universe that fed the headline DeepSeek
selection. If the headline result also appears in these placebo sets, then the
DeepSeek-selected-peer story is weak. If the placebo coefficients attenuate
toward zero, this supports the claim that the result is tied to the selected
product-market peers rather than any firm in the candidate menu.
