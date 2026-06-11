# v37 mechanism closure checks

## Scope

- First check: exact focal-peer mirror closure, no event FE, industry-week FE, event-level cluster.
- Second check: peer event-study main effect in analyst-covered subsamples from v34.
- Main analyst coverage definition: FY+1 EPS or parent-profit revision observed within post 60 days.

## Verdict

1. The exact no-event-FE focal-peer mirror closure does not support a negative competition-gradient: `FocalCAR x PeerSimilarity` = 0.0003, p=0.8264.
2. In the FY+1 EPS-or-parent-profit analyst-covered subsample, PeerCAR[0,+1] = -0.0110***, p=0.0025, N=185, events=100.
3. Implication: focal-peer mirror should be closed as exploratory/null. The analyst-covered sample keeps a negative CAR[0,+1] direction, but the small covered N means this is supporting evidence, not a new main test.

## Focal-Peer Mirror Closure

| sample                   | fe                  | cluster    |   FocalCAR |   FocalCAR p |   FocalCAR x Similarity | se       |   interaction_p |   nobs |   events |   peer_firms |
|:-------------------------|:--------------------|:-----------|-----------:|-------------:|------------------------:|:---------|----------------:|-------:|---------:|-------------:|
| all                      | peer_industry_week  | event      |     0.0035 |       0.4127 |                  0.0003 | (0.0013) |          0.8264 |   2421 |      270 |         1250 |
| all                      | peer_industry_week  | event_peer |     0.0035 |       0.4136 |                  0.0003 | (0.0013) |          0.8257 |   2421 |      270 |         1250 |
| all                      | focal_industry_week | event      |     0.0035 |       0.4127 |                  0.0003 | (0.0013) |          0.8264 |   2421 |      270 |         1250 |
| all                      | focal_industry_week | event_peer |     0.0035 |       0.4136 |                  0.0003 | (0.0013) |          0.8257 |   2421 |      270 |         1250 |
| drop_peer_genai_or_major | peer_industry_week  | event      |     0.0033 |       0.5556 |                  0.0017 | (0.0016) |          0.2823 |   1617 |      264 |          933 |
| drop_peer_genai_or_major | peer_industry_week  | event_peer |     0.0033 |       0.565  |                  0.0017 | (0.0015) |          0.2792 |   1617 |      264 |          933 |
| drop_peer_genai_or_major | focal_industry_week | event      |     0.0033 |       0.5556 |                  0.0017 | (0.0016) |          0.2823 |   1617 |      264 |          933 |
| drop_peer_genai_or_major | focal_industry_week | event_peer |     0.0033 |       0.565  |                  0.0017 | (0.0015) |          0.2792 |   1617 |      264 |          933 |

## Analyst-Covered Main Effect

| sample                     | outcome       | mean_fmt   | se_fmt   |   p_fmt |   nobs |   events |   peer_firms |   positive_rate |
|:---------------------------|:--------------|:-----------|:---------|--------:|-------:|---------:|-------------:|----------------:|
| fy1_feps_60d               | PeerAR[0]     | -0.0079*** | (0.0030) |  0.0095 |    185 |      100 |          105 |        0.4      |
| fy1_feps_60d               | PeerCAR[0,+1] | -0.0110*** | (0.0036) |  0.0025 |    185 |      100 |          105 |        0.4      |
| fy1_profit_parent_60d      | PeerAR[0]     | -0.0079*** | (0.0030) |  0.0095 |    185 |      100 |          105 |        0.4      |
| fy1_profit_parent_60d      | PeerCAR[0,+1] | -0.0110*** | (0.0036) |  0.0025 |    185 |      100 |          105 |        0.4      |
| fy1_feps_or_parent_60d     | PeerAR[0]     | -0.0079*** | (0.0030) |  0.0095 |    185 |      100 |          105 |        0.4      |
| not_fy1_feps_or_parent_60d | PeerAR[0]     | -0.0022*   | (0.0011) |  0.0516 |   2604 |      316 |         1317 |        0.461598 |
| fy1_feps_or_parent_60d     | PeerCAR[0,+1] | -0.0110*** | (0.0036) |  0.0025 |    185 |      100 |          105 |        0.4      |
| not_fy1_feps_or_parent_60d | PeerCAR[0,+1] | -0.0042**  | (0.0017) |  0.0119 |   2604 |      316 |         1317 |        0.436636 |

## Output Files

- `results/v37_mechanism_closure_20260605/focal_peer_exact_closure.csv`
- `results/v37_mechanism_closure_20260605/analyst_covered_main_effects.csv`