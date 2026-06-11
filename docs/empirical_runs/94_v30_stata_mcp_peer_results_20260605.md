# v30 Stata-MCP audit for POM-style peer results

## Scope

- Purpose: independently audit the v29 POM-style peer event-study and cross-sectional regression results in Stata.
- Input: `results/v29_pom_style_peer_results_20260605/analysis_sample_used_in_table2.csv` and `analysis_sample_used_in_table3.csv`.
- Stata commands: `ivreg2` for intercept-only two-way clustered event-study means; `reghdfe` for high-dimensional fixed-effect regressions.
- Cluster structure: two-way clustering by event and peer firm.

## Table 2 Stata Audit

| Outcome | N | Mean | SE | Z | p | Median | Wilcoxon Z | Positive Share | Sign Z |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PeerAR[-1] | 2790 | -0.000950 | 0.000986 | -0.964094 | 0.334999 | -0.002572 | -4.548504 | 0.451971 | -5.073793 |
| PeerAR[0] | 2790 | -0.002540 | 0.001096 | -2.316912 | 0.020509 | -0.002253 | -5.508761 | 0.457706 | -4.467967 |
| PeerAR[+1] | 2790 | -0.002101 | 0.001091 | -1.925661 | 0.054147 | -0.002502 | -5.363930 | 0.443369 | -5.982532 |

## Table 3 Stata Audit

| Col | Dependent Variable | Fixed Effects | N | Events | Peers | Spec x AIActivePeer | SE | p | Overall R2 | Within R2 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| (1) | PeerAR[0] | Event FE | 2789 | 316 | 1384 | -0.001821 | 0.000779 | 0.019458 | 0.439375 | 0.003586 |
| (2) | PeerAR[0] | Event + IndustryWeek FE | 2789 | 316 | 1384 | -0.001821 | 0.000817 | 0.025890 | 0.439375 | 0.003586 |
| (3) | PeerAR[0] | Event + PeerFirm FE | 2789 | 316 | 1384 | -0.000640 | 0.001368 | 0.640142 | 0.716657 | 0.003095 |
| (4) | PeerCAR[0,+1] | Event FE | 2789 | 316 | 1384 | -0.003293 | 0.001196 | 0.005912 | 0.482296 | 0.004467 |
| (5) | PeerCAR[0,+1] | Event + IndustryWeek FE | 2789 | 316 | 1384 | -0.003293 | 0.001255 | 0.008678 | 0.482296 | 0.004467 |
| (6) | PeerCAR[0,+1] | Event + PeerFirm FE | 2789 | 316 | 1384 | -0.000921 | 0.001792 | 0.607186 | 0.750425 | 0.006731 |

## Audit Verdict

- Table 2 is consistent with v29: Day 0 and Day +1 peer abnormal returns are negative, while Day -1 mean return is not statistically significant.
- Table 3 is consistent with v29: the `Spec x AIActivePeer` coefficient is negative and statistically significant under event fixed effects, but becomes insignificant after adding peer-firm fixed effects.
- The peer-firm fixed-effect columns should be read as strict robustness checks. They use only within-peer variation across events and absorb much of the cross-sectional channel that the mechanism is trying to identify.

## Output Files

- `results/v30_stata_mcp_peer_results_20260605/stata_table2_raw.csv`
- `results/v30_stata_mcp_peer_results_20260605/stata_table3_raw.csv`
- `results/v30_stata_mcp_peer_results_20260605/stata_v30.log`
- `scripts/run_v30_stata_mcp_peer_results_20260605.do`
