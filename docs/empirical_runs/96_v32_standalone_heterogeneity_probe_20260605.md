# v32 standalone heterogeneity probe

Sample: v29 Table 3 sample, `liu_product_tfidf_same_industry_d_top10`, `combined_first_event_per_firm`. Standard errors are two-way clustered by event and peer firm.

## Key Regression Results
- peer_ar0_mm | ai | FE=event_key | coef=-0.000154, se=0.001040, p=0.8822, N=2789
- peer_car_0_p1_mm | ai | FE=event_key | coef=-0.001532, se=0.001444, p=0.2888, N=2789
- peer_ar0_mm | ai | FE=event_key+peer_industry_week | coef=-0.000154, se=0.001098, p=0.8883, N=2789
- peer_car_0_p1_mm | ai | FE=event_key+peer_industry_week | coef=-0.001532, se=0.001524, p=0.3149, N=2789
- peer_ar0_mm | spec_z | FE=event_year+focal_industry_d | coef=-0.000786, se=0.001124, p=0.4844, N=2789
- peer_car_0_p1_mm | spec_z | FE=event_year+focal_industry_d | coef=0.000178, se=0.001600, p=0.9112, N=2789
- peer_ar0_mm | spec_high_median | FE=event_year+focal_industry_d | coef=-0.000086, se=0.002309, p=0.9704, N=2789
- peer_car_0_p1_mm | spec_high_median | FE=event_year+focal_industry_d | coef=0.002510, se=0.003490, p=0.4721, N=2789
- peer_ar0_mm | spec_z | FE=event_year+focal_industry_d | coef=0.000679, se=0.001194, p=0.5698, N=2789
- peer_ar0_mm | ai | FE=event_year+focal_industry_d | coef=0.001012, se=0.001336, p=0.4486, N=2789
- peer_ar0_mm | spec_ai | FE=event_year+focal_industry_d | coef=-0.002846, se=0.001263, p=0.0242, N=2789
- peer_car_0_p1_mm | spec_z | FE=event_year+focal_industry_d | coef=0.002094, se=0.001538, p=0.1735, N=2789
- peer_car_0_p1_mm | ai | FE=event_year+focal_industry_d | coef=-0.001022, se=0.001785, p=0.5671, N=2789
- peer_car_0_p1_mm | spec_ai | FE=event_year+focal_industry_d | coef=-0.003703, se=0.001783, p=0.0379, N=2789
- peer_ar0_mm | ai | FE=event_key | coef=-0.000078, se=0.001041, p=0.9405, N=2789
- peer_ar0_mm | spec_ai | FE=event_key | coef=-0.001821, se=0.000828, p=0.0278, N=2789
- peer_car_0_p1_mm | ai | FE=event_key | coef=-0.001394, se=0.001434, p=0.3312, N=2789
- peer_car_0_p1_mm | spec_ai | FE=event_key | coef=-0.003293, se=0.001271, p=0.0096, N=2789

## 2x2 Group Means
| dep              | spec_group   | ai_group    |      mean |       se |         z |      p |   nobs |   events |   peer_firms |   positive_rate |
|:-----------------|:-------------|:------------|----------:|---------:|----------:|-------:|-------:|---------:|-------------:|----------------:|
| peer_ar0_mm      | LowSpec      | NonAIActive | -0.003604 | 0.001612 | -2.23559  | 0.0254 |    757 |      155 |          572 |          0.428  |
| peer_ar0_mm      | LowSpec      | AIActive    | -0.001973 | 0.001929 | -1.02294  | 0.3063 |    629 |      140 |          353 |          0.4547 |
| peer_ar0_mm      | HighSpec     | NonAIActive | -0.001436 | 0.001783 | -0.805133 | 0.4207 |    779 |      154 |          589 |          0.4711 |
| peer_ar0_mm      | HighSpec     | AIActive    | -0.003205 | 0.00218  | -1.47022  | 0.1415 |    624 |      138 |          355 |          0.4792 |
| peer_car_0_p1_mm | LowSpec      | NonAIActive | -0.005808 | 0.002289 | -2.53744  | 0.0112 |    757 |      155 |          572 |          0.4214 |
| peer_car_0_p1_mm | LowSpec      | AIActive    | -0.006575 | 0.00285  | -2.30718  | 0.021  |    629 |      140 |          353 |          0.4022 |
| peer_car_0_p1_mm | HighSpec     | NonAIActive | -0.000514 | 0.002577 | -0.199633 | 0.8418 |    779 |      154 |          589 |          0.4711 |
| peer_car_0_p1_mm | HighSpec     | AIActive    | -0.006466 | 0.003278 | -1.97242  | 0.0486 |    624 |      138 |          355 |          0.4359 |

## Output Files
- `results/v32_standalone_heterogeneity_probe_20260605/standalone_heterogeneity_key_results.csv`
- `results/v32_standalone_heterogeneity_probe_20260605/standalone_heterogeneity_regressions_raw.csv`
- `results/v32_standalone_heterogeneity_probe_20260605/two_by_two_group_means.csv`
- `results/v32_standalone_heterogeneity_probe_20260605/two_by_two_difference_tests_raw.csv`