# v18 Cao-Style Open-Ended DeepSeek Peers

Date: 2026-05-31

Purpose: diagnostic peer definition closer to Cao, Chen, Tucker, and Wan (2025).
Unlike v17, this pass does **not** provide a candidate menu. DeepSeek is asked to
generate up to five A-share product-market competitors for each focal firm, and
the generated names/codes are matched back to the local A-share universe.

## Setup

- Model: `deepseek-v4-flash`
- As-of year in prompt: `2025`
- Candidate menu: none
- Matching: generated six-digit code first; exact normalized Chinese short name
  second.
- API key source: `DEEPSEEK_API_KEY`; not stored in outputs.

## Summary

```json
{
  "tag": "full_asof2025",
  "model": "deepseek-v4-flash",
  "as_of_year": 2025,
  "input_focals": 2652,
  "selected_pairs": 12099,
  "network_pairs": 12099,
  "focals_with_at_least_one_peer": 2585,
  "prompt_tokens": 261111,
  "completion_tokens": 256799,
  "output_network": "/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction/results/v18_cao_style_open_ended_deepseek_peers_20260531/deepseek_open_ended_peer_network_top5_full_asof2025.csv"
}
```

## Main Effects

Specification is identical to v17:

```text
PeerCAR[0,+1] = beta * Specificity_z x AIActivePeer
              + AIActivePeer
              + PeerCAR[-10,-2] + PeerCAR[-20,-2]
              + event FE + peer industry-week FE
```

| peer_source                   |   top_n | ai_def               |    coef |     se |      p |   nobs |   events |   focal_firms |   peer_firms |   mean_y |   mean_ai |
|:------------------------------|--------:|:---------------------|--------:|-------:|-------:|-------:|---------:|--------------:|-------------:|---------:|----------:|
| deepseek_open_ended_cao_style |       3 | ext_any              | -0.0008 | 0.001  | 0.3786 |   4977 |     2257 |          2257 |         1327 |   0      |    0.3643 |
| deepseek_open_ended_cao_style |       3 | current_text_history | -0.0009 | 0.0012 | 0.4509 |   4977 |     2257 |          2257 |         1327 |   0      |    0.3392 |
| deepseek_open_ended_cao_style |       3 | ext_no_hiring        | -0.0033 | 0.0029 | 0.2512 |   4977 |     2257 |          2257 |         1327 |   0      |    0.0354 |
| deepseek_open_ended_cao_style |       3 | ext_plus_history     | -0.001  | 0.001  | 0.2796 |   4977 |     2257 |          2257 |         1327 |   0      |    0.4529 |
| deepseek_open_ended_cao_style |       5 | ext_any              | -0.0008 | 0.0007 | 0.2228 |   7934 |     2322 |          2322 |         1718 |   0.0003 |    0.344  |
| deepseek_open_ended_cao_style |       5 | current_text_history | -0.0009 | 0.0008 | 0.2546 |   7934 |     2322 |          2322 |         1718 |   0.0003 |    0.3315 |
| deepseek_open_ended_cao_style |       5 | ext_no_hiring        | -0.0026 | 0.0017 | 0.1257 |   7934 |     2322 |          2322 |         1718 |   0.0003 |    0.032  |
| deepseek_open_ended_cao_style |       5 | ext_plus_history     | -0.0011 | 0.0006 | 0.0814 |   7934 |     2322 |          2322 |         1718 |   0.0003 |    0.4355 |

## Overlap with v17 Candidate-Menu DeepSeek Peers

The open-ended Cao-style network is not a small perturbation of the v17
candidate-menu DeepSeek network.

```text
v17 candidate-menu DeepSeek pairs: 11,864; focal firms: 2,584
v18 open-ended DeepSeek pairs:     12,099; focal firms: 2,585
pair overlap:                       1,425
share of v18 pairs overlapping v17: 11.8%
share of v17 pairs overlapping v18: 12.0%
mean focal-level Jaccard overlap:    0.075
median focal-level Jaccard overlap:  0.000
same-industry share, v18:            67.4%
same-industry share, v17:            78.7%
```

This low overlap is useful diagnostically: the Cao-style open-ended procedure
selects a substantially different peer set, not merely a re-ranking of the v17
candidate menu.

## Same-Industry Filter Diagnostic

I also retain only open-ended peers whose fine industry matches the focal firm,
then re-rank the remaining peers within focal firm.

| peer_source                         |   top_n | ai_def               |    coef |     se |      p |   nobs |   events |   peer_firms |   mean_ai |
|:------------------------------------|--------:|:---------------------|--------:|-------:|-------:|-------:|---------:|-------------:|----------:|
| deepseek_open_ended_same_industry   |       3 | ext_any              |  0.0002 | 0.0010 | 0.8322 |   3916 |     1878 |         1184 |    0.3613 |
| deepseek_open_ended_same_industry   |       3 | current_text_history | -0.0024 | 0.0013 | 0.0566 |   3916 |     1878 |         1184 |    0.3401 |
| deepseek_open_ended_same_industry   |       3 | ext_no_hiring        | -0.0044 | 0.0028 | 0.1079 |   3916 |     1878 |         1184 |    0.0401 |
| deepseek_open_ended_same_industry   |       3 | ext_plus_history     | -0.0012 | 0.0011 | 0.2495 |   3916 |     1878 |         1184 |    0.4494 |
| deepseek_open_ended_same_industry   |       5 | ext_any              | -0.0006 | 0.0009 | 0.4926 |   5424 |     1905 |         1422 |    0.3475 |
| deepseek_open_ended_same_industry   |       5 | current_text_history | -0.0024 | 0.0010 | 0.0140 |   5424 |     1905 |         1422 |    0.3374 |
| deepseek_open_ended_same_industry   |       5 | ext_no_hiring        | -0.0028 | 0.0018 | 0.1175 |   5424 |     1905 |         1422 |    0.0380 |
| deepseek_open_ended_same_industry   |       5 | ext_plus_history     | -0.0019 | 0.0008 | 0.0229 |   5424 |     1905 |         1422 |    0.4390 |

The same-industry filter recovers a negative result for disclosure-history-based
AI activeness and for `ext_plus_history`, but the clean external `ext_any`
measure remains insignificant.

## Interpretation Boundary

This is closer to Cao et al. than v17, but it is also noisier in China because
open-ended generation can produce HK/US firms, subsidiaries, private firms, or
historically unavailable competitors. For this reason it should be read as a
robustness check against the auditable candidate-menu DeepSeek network, not as a
drop-in replacement unless validation quality is high.

Bottom line: the open-ended Cao-style diagnostic does **not** replicate the main
v17 headline result under `ext_any`. It is directionally negative but much
smaller and statistically insignificant. This weakens any claim that the result
is invariant to a fully open-ended LLM peer definition. The safer paper design is
therefore to keep v17 as the headline auditable peer-selection method and report
v18 as a conservative robustness / boundary check.
