# v17 DeepSeek Flash Peer Network

Date: 2026-05-31

Purpose: use DeepSeek V4 Flash to select direct product-market peers from a
compact no-random candidate menu and test whether the GenAI peer-CAR result
survives under an actual generative-AI peer-selection pass.

## API Coding Setup

- Model: `deepseek-v4-flash`
- Candidate menu: no-random v16 pool, max 15 candidates per focal firm.
- Output: compact JSON code list only, no explanations.
- API key was read from environment variable and was not stored in scripts or
  outputs.

Summary file:

```text
results/v17_deepseek_flash_peer_coding_20260531/deepseek_flash_summary_full_compact15.json
```

Network file:

```text
results/v17_deepseek_flash_peer_coding_20260531/deepseek_flash_peer_network_top5_full_compact15.csv
```

## Coverage

| peer_source         |   raw_rows |   raw_events |   raw_focal_firms |   raw_peer_firms |   raw_top5_rows |   mean_peer_similarity_top5 |   median_peer_similarity_top5 |
|:--------------------|-----------:|-------------:|------------------:|-----------------:|----------------:|----------------------------:|------------------------------:|
| deepseek_flash_top5 |      96519 |        19999 |              2584 |             4173 |           96519 |                      0.3229 |                        0.3342 |

## Selected Candidate Source Mix

| candidate_source_system   |   selected_pairs |   mean_rank |   mean_similarity |
|:--------------------------|-----------------:|------------:|------------------:|
| csmar_scope               |             7158 |     2.92777 |          0.218659 |
| annual_same_industry      |             4585 |     2.85016 |          0.359126 |
| annual_global_ai_stripped |              121 |     3.60331 |          0.361217 |

## Main Effects

Specification:

```text
PeerCAR[0,+1] = beta * Specificity_z x AIActivePeer
              + AIActivePeer
              + PeerCAR[-10,-2] + PeerCAR[-20,-2]
              + event FE + peer industry-week FE
```

Sample: first focal GenAI events, announcement-cleaned observations.

| peer_source         |   top_n | ai_def               |    coef |     se |      p |   nobs |   events |   focal_firms |   peer_firms |   mean_y |   mean_ai |
|:--------------------|--------:|:---------------------|--------:|-------:|-------:|-------:|---------:|--------------:|-------------:|---------:|----------:|
| deepseek_flash_top5 |       3 | ext_any              | -0.0023 | 0.0012 | 0.0678 |   4957 |     2247 |          2247 |         2701 |  -0.0005 |    0.2372 |
| deepseek_flash_top5 |       3 | current_text_history | -0.0029 | 0.0012 | 0.0116 |   4957 |     2247 |          2247 |         2701 |  -0.0005 |    0.3113 |
| deepseek_flash_top5 |       3 | ext_no_hiring        |  0.001  | 0.0029 | 0.7356 |   4957 |     2247 |          2247 |         2701 |  -0.0005 |    0.021  |
| deepseek_flash_top5 |       3 | ext_plus_history     | -0.0032 | 0.0011 | 0.0047 |   4957 |     2247 |          2247 |         2701 |  -0.0005 |    0.3684 |
| deepseek_flash_top5 |       5 | ext_any              | -0.0021 | 0.0009 | 0.0157 |   7813 |     2311 |          2311 |         3342 |  -0.0005 |    0.2354 |
| deepseek_flash_top5 |       5 | current_text_history | -0.0023 | 0.0009 | 0.0108 |   7813 |     2311 |          2311 |         3342 |  -0.0005 |    0.3132 |
| deepseek_flash_top5 |       5 | ext_no_hiring        | -0.0028 | 0.0024 | 0.2526 |   7813 |     2311 |          2311 |         3342 |  -0.0005 |    0.0219 |
| deepseek_flash_top5 |       5 | ext_plus_history     | -0.0023 | 0.0009 | 0.0116 |   7813 |     2311 |          2311 |         3342 |  -0.0005 |    0.371  |

## Reading

This is the closest current implementation to the Cao et al.-style GenAI peer
idea. It still uses a candidate menu to avoid hallucinated stock codes, but the
final Top5 selection is made by a generative model rather than the deterministic
semantic scorer.
