# v31 POM-analog cross-sectional regressions

## Scope

- Purpose: test POM-style cross-sectional factors in the product-market peer setting.
- Input sample: v29 Table 3 analysis sample.
- Important distinction: event-level variables such as disclosure specificity and announcement category are absorbed by event fixed effects. Columns without event fixed effects are exploratory POM-style analogs, not the preferred identification specification.

## POM Variable Mapping

| POM variable | Peer-setting analog | variable | note |
|---|---|---|---|
| Supplier R&D Intensity | Prior AI patent evidence | peer_prior_ai_patent | True R&D intensity is not in the current repo data; this is a pre-event innovation-evidence proxy, not a one-for-one R&D measure. |
| Supplier Sales Growth | Peer sales growth | peer_sales_growth_z | Uses prior fiscal-year revenue growth from the available CSMAR-derived annual income metrics. |
| Supplier-Customer Distance | Product-market distance | product_distance_z | Defined as 1 minus product-text similarity; larger values indicate weaker product-market proximity. |
| Supplier Industry Concentration | Peer industry concentration | peer_industry_hhi_z | HHI computed from listed-firm revenue by industry-year where industry mapping is available. |
| Product-Oriented Announcement | Product-oriented GenAI announcement | product_oriented | Rule-coded from announcement title and LLM evidence; should be manually audited before final paper use. |
| Announcement intensity/category | Qian initiative score / disclosure specificity | qian_recall_z / spec_z | Specificity has already been used in v29; event fixed effects absorb its main effect, so the preferred mechanism uses Spec x AIActivePeer. |

## Variable Coverage

| variable | nonmissing_rows | nonmissing_events | mean |
|---|---|---|---|
| peer_prior_ai_patent | 2789 | 316 | 0.0606 |
| peer_sales_growth | 2719 | 316 | 0.0059 |
| peer_gross_margin | 2722 | 311 | 0.3050 |
| peer_log_revenue | 2789 | 316 | 21.4268 |
| peer_industry_hhi | 2789 | 316 | 0.0696 |
| product_distance | 2789 | 316 | 0.6400 |
| product_oriented | 2789 | 316 | 0.8960 |
| qian_recall_score | 2789 | 316 | 7.7842 |
| spec_z | 2789 | 316 | 0.0300 |
| ai | 2789 | 316 | 0.4493 |
| peer_financial_source:event_year_minus_1 | 2719 | 316 |  |
| peer_financial_source:snapshot_report_year | 0 | 0 |  |

## Regression Table

| Variables | (1) | (2) | (3) | (4) | (5) | (6) | (7) | (8) |
|---|---|---|---|---|---|---|---|---|
|  | PeerAR[0] | PeerCAR[0,+1] | PeerAR[0] | PeerCAR[0,+1] | PeerAR[0] | PeerCAR[0,+1] | PeerAR[0] | PeerCAR[0,+1] |
|  | POM peer controls, Event FE | POM peer controls, Event FE | Announcement features, Year + industry FE | Announcement features, Year + industry FE | Specificity mechanism, Event FE | Specificity mechanism, Event FE | Announcement category x AIActive, Event FE | Announcement category x AIActive, Event FE |
| Prior AI patent evidence | -0.0012 | -0.0027 | -0.0033 | -0.0078** | -0.0011 | -0.0022 | -0.0011 | -0.0022 |
|  | (0.0026) | (0.0030) | (0.0029) | (0.0036) | (0.0026) | (0.0031) | (0.0026) | (0.0031) |
| Peer sales growth | -0.0011* | -0.0024*** | -0.0006 | -0.0016* | -0.0011* | -0.0021** | -0.0011* | -0.0021** |
|  | (0.0006) | (0.0009) | (0.0007) | (0.0009) | (0.0006) | (0.0008) | (0.0006) | (0.0009) |
| Product-market distance | -0.0017* | -0.0029** | -0.0003 | 0.0003 | -0.0016 | -0.0028** | -0.0016 | -0.0028** |
|  | (0.0011) | (0.0014) | (0.0010) | (0.0014) | (0.0010) | (0.0013) | (0.0010) | (0.0013) |
| Peer industry concentration | 0.0031** | 0.0044 | 0.0048 | 0.0069 | 0.0030** | 0.0044 | 0.0030** | 0.0047* |
|  | (0.0013) | (0.0031) | (0.0040) | (0.0055) | (0.0013) | (0.0029) | (0.0013) | (0.0029) |
| Product-oriented announcement |  |  | -0.0019 | -0.0077 |  |  |  |  |
|  |  |  | (0.0032) | (0.0048) |  |  |  |  |
| Qian initiative score |  |  | 0.0003 | 0.0016 |  |  |  |  |
|  |  |  | (0.0014) | (0.0017) |  |  |  |  |
| Disclosure specificity |  |  | -0.0007 | 0.0001 |  |  |  |  |
|  |  |  | (0.0011) | (0.0015) |  |  |  |  |
| AIActivePeer |  |  |  |  | -0.0001 | -0.0008 | -0.0010 | -0.0056 |
|  |  |  |  |  | (0.0011) | (0.0015) | (0.0024) | (0.0045) |
| Specificity x AIActivePeer |  |  |  |  | -0.0018** | -0.0032*** |  |  |
|  |  |  |  |  | (0.0008) | (0.0012) |  |  |
| Product-oriented x AIActivePeer |  |  |  |  |  |  | 0.0010 | 0.0052 |
|  |  |  |  |  |  |  | (0.0026) | (0.0048) |
| Qian score x AIActivePeer |  |  |  |  |  |  | -0.0006 | -0.0006 |
|  |  |  |  |  |  |  | (0.0010) | (0.0014) |
| Peer size | 0.0001 | -0.0004 | 0.0012 | 0.0005 | 0.0000 | -0.0006 | 0.0000 | -0.0006 |
|  | (0.0007) | (0.0010) | (0.0008) | (0.0011) | (0.0007) | (0.0009) | (0.0007) | (0.0010) |
| Peer gross margin | 0.0004 | 0.0017* |  |  |  |  |  |  |
|  | (0.0008) | (0.0010) |  |  |  |  |  |  |
| PeerCAR[-10,-2] | 0.0121 | -0.0009 | 0.0216 | 0.0183 | 0.0124 | 0.0005 | 0.0124 | 0.0002 |
|  | (0.0121) | (0.0162) | (0.0151) | (0.0186) | (0.0120) | (0.0162) | (0.0120) | (0.0162) |
| PeerCAR[-20,-2] | -0.0063 | -0.0029 | -0.0139 | -0.0243 | -0.0062 | -0.0028 | -0.0065 | -0.0033 |
|  | (0.0088) | (0.0118) | (0.0107) | (0.0156) | (0.0087) | (0.0118) | (0.0087) | (0.0118) |
| Event FE | YES | YES | NO | NO | YES | YES | YES | YES |
| Year FE | NO | NO | YES | YES | NO | NO | NO | NO |
| Focal industry FE | NO | NO | YES | YES | NO | NO | NO | NO |
| Observations | 2652 | 2652 | 2719 | 2719 | 2719 | 2719 | 2719 | 2719 |
| Events | 311 | 311 | 316 | 316 | 316 | 316 | 316 | 316 |
| Peer firms | 1314 | 1314 | 1358 | 1358 | 1358 | 1358 | 1358 | 1358 |
| Overall R2 | 0.442 | 0.484 | 0.043 | 0.068 | 0.446 | 0.486 | 0.445 | 0.486 |
| Within R2 | 0.005 | 0.010 | 0.006 | 0.012 | 0.006 | 0.010 | 0.004 | 0.008 |

## Specificity Mechanism Columns

| col | dep | spec_ai_coef | spec_ai_se | spec_ai_p | nobs | events |
|---|---|---|---|---|---|---|
| (5) | PeerAR[0] | -0.001806 | 0.000791 | 0.0224 | 2719 | 316 |
| (6) | PeerCAR[0,+1] | -0.003194 | 0.001205 | 0.0080 | 2719 | 316 |

## Notes

- `Supplier R&D Intensity` from POM is not directly available in the current local data. The closest current proxy is prior AI patent evidence.
- `Product-oriented announcement` is rule-coded and must be manually audited before it is used as a final paper variable.
- `Disclosure specificity` has already been built. Under event fixed effects, its main effect is absorbed; the credible specification is the interaction `Specificity x AIActivePeer`.
- Standard errors are two-way clustered by event and peer firm, following the v29 implementation.

## Output Files

- `results/v31_pom_analog_cross_section_20260605/pom_variable_mapping.csv`
- `results/v31_pom_analog_cross_section_20260605/pom_analog_variable_coverage.csv`
- `results/v31_pom_analog_cross_section_20260605/pom_analog_cross_section_regressions.csv`
- `results/v31_pom_analog_cross_section_20260605/pom_analog_cross_section_regressions_raw.csv`
- `results/v31_pom_analog_cross_section_20260605/analysis_panel_pom_analog.csv.gz`
- `results/v31_pom_analog_cross_section_20260605/v31_pom_analog_cross_section_20260605.xlsx`
