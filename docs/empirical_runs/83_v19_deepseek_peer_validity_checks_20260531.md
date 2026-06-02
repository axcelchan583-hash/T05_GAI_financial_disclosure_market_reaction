# v19 DeepSeek Peer Validity Checks

Date: 2026-05-31

Purpose: fast non-human validation package for the DeepSeek product-market peer
definitions. This deliberately skips manual blind review and mirrors the other
Cao et al. validation layers: overlap with alternative systems, return
comovement, accounting-fundamental comovement, and homogeneity / deviation.

## Network Summary

| peer_system                            |   pair_count |   focal_firms |   peer_firms |   same_industry_share |   mean_similarity |   median_similarity |
|:---------------------------------------|-------------:|--------------:|-------------:|----------------------:|------------------:|--------------------:|
| deepseek_candidate_menu_top5           |        11864 |          2584 |         4173 |                0.787  |            0.2744 |              0.2635 |
| deepseek_open_ended_top5               |        12099 |          2585 |         2120 |                0.6744 |          nan      |            nan      |
| deepseek_open_ended_same_industry_top5 |         8160 |          2235 |         1769 |                1      |          nan      |            nan      |
| csmar_scope_top5                       |        13260 |          2652 |         4447 |                0.4428 |            0.232  |              0.1953 |
| annual_same_industry_2024_top5         |         5819 |          1168 |         2451 |                1      |            0.3623 |              0.3567 |
| annual_global_ai_stripped_2024_top5    |         5845 |          1169 |         2219 |                0.5107 |            0.3879 |              0.3777 |
| random_same_industry_top5              |        13000 |          2600 |         4889 |                0      |            0.0526 |              0.0337 |
| low_similarity_same_industry_top5      |        13000 |          2600 |         2335 |                0      |            0.0062 |              0.003  |

## Overlap with v17 Candidate-Menu DeepSeek Peers

| system_b                               |   overlap_pairs |   share_of_a |   share_of_b |   jaccard |
|:---------------------------------------|----------------:|-------------:|-------------:|----------:|
| csmar_scope_top5                       |            5258 |       0.4432 |       0.3965 |    0.2647 |
| annual_same_industry_2024_top5         |            4019 |       0.3388 |       0.6907 |    0.2941 |
| annual_global_ai_stripped_2024_top5    |            2375 |       0.2002 |       0.4063 |    0.1549 |
| deepseek_open_ended_top5               |            1425 |       0.1201 |       0.1178 |    0.0632 |
| deepseek_open_ended_same_industry_top5 |            1260 |       0.1062 |       0.1544 |    0.0671 |
| random_same_industry_top5              |             214 |       0.018  |       0.0165 |    0.0087 |
| low_similarity_same_industry_top5      |              94 |       0.0079 |       0.0072 |    0.0038 |

## Return Comovement, 2025-2026

Higher `mean_abret_beta` and `mean_abret_corr` indicate stronger market
comovement between focal firms and their peer portfolios.

| peer_system                            |   focal_firms_with_returns |   mean_abret_beta |   mean_abret_corr |   mean_raw_beta |   mean_raw_corr |
|:---------------------------------------|---------------------------:|------------------:|------------------:|----------------:|----------------:|
| annual_same_industry_2024_top5         |                       1107 |            0.6336 |            0.4352 |          0.7657 |          0.5814 |
| annual_global_ai_stripped_2024_top5    |                       1108 |            0.6178 |            0.4144 |          0.7633 |          0.5669 |
| deepseek_candidate_menu_top5           |                       2390 |            0.6008 |            0.4147 |          0.7273 |          0.5513 |
| deepseek_open_ended_top5               |                       2379 |            0.5842 |            0.3991 |          0.7347 |          0.5439 |
| csmar_scope_top5                       |                       2450 |            0.5472 |            0.3547 |          0.7053 |          0.5126 |
| deepseek_open_ended_same_industry_top5 |                       2030 |            0.5407 |            0.3961 |          0.6821 |          0.5338 |
| random_same_industry_top5              |                       2403 |            0.4592 |            0.3007 |          0.6484 |          0.475  |
| low_similarity_same_industry_top5      |                       2401 |            0.378  |            0.2459 |          0.6026 |          0.4361 |

## Return Homogeneity, 2025-2026

Lower absolute deviation means peers move more similarly to focal firms.

| peer_system                            |   mean_abs_abret_dev |   median_abs_abret_dev |   mean_abs_ret_dev |   median_abs_ret_dev |   pair_day_obs |
|:---------------------------------------|---------------------:|-----------------------:|-------------------:|---------------------:|---------------:|
| deepseek_open_ended_same_industry_top5 |               0.0191 |                 0.0127 |             0.019  |               0.0126 |    2.15875e+06 |
| deepseek_open_ended_top5               |               0.0197 |                 0.0133 |             0.0196 |               0.0131 |    3.19927e+06 |
| deepseek_candidate_menu_top5           |               0.0203 |                 0.0136 |             0.0202 |               0.0134 |    3.29858e+06 |
| annual_same_industry_2024_top5         |               0.0205 |                 0.0137 |             0.0203 |               0.0135 |    1.61321e+06 |
| annual_global_ai_stripped_2024_top5    |               0.0206 |                 0.0138 |             0.0205 |               0.0136 |    1.60087e+06 |
| csmar_scope_top5                       |               0.0217 |                 0.0147 |             0.0216 |               0.0145 |    3.59208e+06 |
| random_same_industry_top5              |               0.0223 |                 0.0153 |             0.0222 |               0.0151 |    3.17547e+06 |
| low_similarity_same_industry_top5      |               0.0229 |                 0.0161 |             0.0228 |               0.0159 |    3.10752e+06 |

## Fundamental Comovement

| peer_system                            | metric                  |    corr |      p |   n_focal_year |   focal_firms |
|:---------------------------------------|:------------------------|--------:|-------:|---------------:|--------------:|
| deepseek_candidate_menu_top5           | gross_margin_year_resid |  0.6451 | 0      |          11372 |          2495 |
| annual_same_industry_2024_top5         | gross_margin_year_resid |  0.6316 | 0      |           5348 |          1167 |
| deepseek_open_ended_same_industry_top5 | gross_margin_year_resid |  0.6252 | 0      |           9018 |          1963 |
| deepseek_open_ended_top5               | gross_margin_year_resid |  0.5943 | 0      |          11736 |          2530 |
| annual_global_ai_stripped_2024_top5    | gross_margin_year_resid |  0.5291 | 0      |           5364 |          1169 |
| csmar_scope_top5                       | gross_margin_year_resid |  0.4413 | 0      |          12268 |          2652 |
| low_similarity_same_industry_top5      | gross_margin_year_resid |  0.3489 | 0      |          11724 |          2599 |
| random_same_industry_top5              | gross_margin_year_resid |  0.3106 | 0      |          12034 |          2598 |
| deepseek_candidate_menu_top5           | sales_growth_year_resid |  0.2394 | 0      |          11304 |          2495 |
| annual_same_industry_2024_top5         | sales_growth_year_resid |  0.2342 | 0      |           5372 |          1167 |
| deepseek_open_ended_top5               | sales_growth_year_resid |  0.233  | 0      |          11641 |          2530 |
| annual_global_ai_stripped_2024_top5    | sales_growth_year_resid |  0.2314 | 0      |           5389 |          1169 |
| deepseek_open_ended_same_industry_top5 | sales_growth_year_resid |  0.23   | 0      |           9044 |          1963 |
| csmar_scope_top5                       | sales_growth_year_resid |  0.1327 | 0      |          12137 |          2652 |
| random_same_industry_top5              | sales_growth_year_resid |  0.0598 | 0      |          11921 |          2598 |
| low_similarity_same_industry_top5      | sales_growth_year_resid | -0.0195 | 0.0356 |          11600 |          2599 |

## Fundamental Homogeneity

| peer_system                            | metric                  |   mean_abs_deviation |   median_abs_deviation |   n_focal_year |   focal_firms |
|:---------------------------------------|:------------------------|---------------------:|-----------------------:|---------------:|--------------:|
| deepseek_candidate_menu_top5           | gross_margin_year_resid |               0.1093 |                 0.0802 |          11372 |          2495 |
| annual_same_industry_2024_top5         | gross_margin_year_resid |               0.1121 |                 0.0843 |           5348 |          1167 |
| deepseek_open_ended_same_industry_top5 | gross_margin_year_resid |               0.1162 |                 0.0851 |           9018 |          1963 |
| deepseek_open_ended_top5               | gross_margin_year_resid |               0.1178 |                 0.0873 |          11736 |          2530 |
| annual_global_ai_stripped_2024_top5    | gross_margin_year_resid |               0.1259 |                 0.0967 |           5364 |          1169 |
| csmar_scope_top5                       | gross_margin_year_resid |               0.1308 |                 0.0984 |          12268 |          2652 |
| random_same_industry_top5              | gross_margin_year_resid |               0.1435 |                 0.1091 |          12034 |          2598 |
| low_similarity_same_industry_top5      | gross_margin_year_resid |               0.1496 |                 0.1163 |          11724 |          2599 |
| annual_same_industry_2024_top5         | sales_growth_year_resid |               0.194  |                 0.1326 |           5372 |          1167 |
| annual_global_ai_stripped_2024_top5    | sales_growth_year_resid |               0.1956 |                 0.1347 |           5389 |          1169 |
| deepseek_open_ended_same_industry_top5 | sales_growth_year_resid |               0.2026 |                 0.132  |           9044 |          1963 |
| deepseek_open_ended_top5               | sales_growth_year_resid |               0.2029 |                 0.1343 |          11641 |          2530 |
| deepseek_candidate_menu_top5           | sales_growth_year_resid |               0.2033 |                 0.1362 |          11304 |          2495 |
| csmar_scope_top5                       | sales_growth_year_resid |               0.2203 |                 0.1471 |          12137 |          2652 |
| random_same_industry_top5              | sales_growth_year_resid |               0.2274 |                 0.1543 |          11921 |          2598 |
| low_similarity_same_industry_top5      | sales_growth_year_resid |               0.2547 |                 0.1728 |          11600 |          2599 |

## Output Stability Check

This repeats the v17 candidate-menu DeepSeek selection on a 100-focal-firm
subsample using the same deterministic prompt and temperature-0 setting, then
compares the repeated Top5 lists with the original full-run Top5 lists. This is
the closest fast analogue to the Cao et al. output-stability check, while
skipping manual blind review.

| sample_focals | orig_pairs | repeat_pairs | pair_overlap | mean_jaccard | median_jaccard | mean_common_peers | top1_same_share |
|--------------:|-----------:|-------------:|-------------:|-------------:|---------------:|------------------:|----------------:|
|            97 |        477 |          474 |          437 |       0.8708 |         1.0000 |            4.5052 |          0.8454 |

Reading: the candidate-menu DeepSeek peer list is highly stable in this
subsample. The median focal firm receives exactly the same Top5 set on rerun;
on average, 4.5 of 5 peers overlap, and the top-ranked peer is unchanged for
84.5% of focal firms.

## Reading

- The candidate-menu DeepSeek network should be judged against random and
  low-similarity placebos, not against an impossible perfect peer list.
- If candidate-menu DeepSeek peers beat random/low-similarity peers in return
  comovement and homogeneity, the peer measure has market-validity support.
- The open-ended Cao-style peer network is a useful boundary check but selects a
  substantially different and noisier set of firms in China.
