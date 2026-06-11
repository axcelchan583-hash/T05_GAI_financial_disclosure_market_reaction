# v36 Spec x AIActivePeer firm-characteristic guard

## Scope

- Input panel: v31 POM-analog analysis panel.
- Purpose: test Claude's key objection that `AIActivePeer` may proxy for peer firm type/style rather than AI competition exposure.
- Dependent variable: peer `CAR[0,+1]` is the decision variable; `AR[0]` is retained as auxiliary output.
- Fixed effects: event fixed effects.
- Main standard errors: two-way clustered by event and peer firm. Event-only clustered estimates are also saved because Claude requested event-level clustering.
- Firm-style controls: annual market size and MB/PB from CSMAR `FI_T10`; rolling beta and return volatility from the existing 200-day/skip-11 market-model return cache.

## Verdict

`Spec x AIActivePeer` in the full guard model: -0.0025**, p=0.0334 -> **SURVIVES** at the 10% threshold.

Decision rule: if the full model keeps a negative `Spec x AIActivePeer` with p < 0.10, the AIActive mechanism survives this guard. If not, the current mechanism has to be treated as unresolved.

## Main CAR[0,+1] Guard Table

| cluster    | model                   | Spec x AIActive   | se       |      p |    N |   events |   peer_firms |
|:-----------|:------------------------|:------------------|:---------|-------:|-----:|---------:|-------------:|
| event_peer | M1_base                 | -0.0032***        | (0.0012) | 0.008  | 2719 |      316 |         1358 |
| event      | M1_base                 | -0.0032***        | (0.0012) | 0.0071 | 2719 |      316 |         1358 |
| event_peer | M2_add_style_main       | -0.0026**         | (0.0012) | 0.0292 | 2404 |      281 |         1234 |
| event      | M2_add_style_main       | -0.0026**         | (0.0012) | 0.026  | 2404 |      281 |         1234 |
| event_peer | M3_add_each_interaction | -0.0025**         | (0.0012) | 0.0334 | 2404 |      281 |         1234 |
| event      | M3_add_each_interaction | -0.0025**         | (0.0012) | 0.0319 | 2404 |      281 |         1234 |

## Compact Two-Way Clustered Table

| sample                   | model                   | label                              | Spec x AIActive   | se       |      p |    N |   events |   peer_firms |   within_r2 | spec_x_size   | spec_x_beta   | spec_x_volatility   | spec_x_mb   |
|:-------------------------|:------------------------|:-----------------------------------|:------------------|:---------|-------:|-----:|---------:|-------------:|------------:|:--------------|:--------------|:--------------------|:------------|
| all                      | M1_base                 | Base v31 controls                  | -0.0032***        | (0.0012) | 0.008  | 2719 |      316 |         1358 |       0.01  |               |               |                     |             |
| all                      | M2_add_style_main       | Add firm-style main effects        | -0.0026**         | (0.0012) | 0.0292 | 2404 |      281 |         1234 |       0.019 |               |               |                     |             |
| all                      | M3_add_each_interaction | Add Spec x firm-style interactions | -0.0025**         | (0.0012) | 0.0334 | 2404 |      281 |         1234 |       0.02  | -0.0002       | -0.0017*      | 0.0010              | -0.0007     |
| drop_peer_genai_or_major | M1_base                 | Base v31 controls                  | -0.0030*          | (0.0016) | 0.0712 | 1808 |      310 |         1021 |       0.009 |               |               |                     |             |
| drop_peer_genai_or_major | M2_add_style_main       | Add firm-style main effects        | -0.0026           | (0.0016) | 0.1082 | 1618 |      276 |          923 |       0.023 |               |               |                     |             |
| drop_peer_genai_or_major | M3_add_each_interaction | Add Spec x firm-style interactions | -0.0025           | (0.0017) | 0.1292 | 1618 |      276 |          923 |       0.024 | -0.0001       | -0.0010       | 0.0009              | -0.0009     |

## Variable Coverage

| variable            |   nonmissing_rows |   nonmissing_events |          mean |       std |
|:--------------------|------------------:|--------------------:|--------------:|----------:|
| peer_size_raw       |              2470 |                 281 |  22.9033      | 1.21806   |
| peer_mb_raw         |              2470 |                 281 |   3.5766      | 4.08023   |
| peer_beta_raw       |              2789 |                 316 |   1.47568     | 0.511204  |
| peer_volatility_raw |              2789 |                 316 |   0.0334802   | 0.0146618 |
| peer_est_obs        |              2789 |                 316 | 199.703       | 3.47775   |
| peer_size_z         |              2470 |                 281 |  -2.04245e-15 | 1         |
| peer_beta_z         |              2789 |                 316 |   1.78336e-16 | 1         |
| peer_volatility_z   |              2789 |                 316 |  -2.54766e-17 | 1         |
| peer_mb_z           |              2470 |                 281 |  -2.28697e-16 | 1         |
| spec_x_size         |              2470 |                 281 |  -0.0511726   | 1.00998   |
| spec_x_beta         |              2789 |                 316 |  -0.0092618   | 0.97796   |
| spec_x_volatility   |              2789 |                 316 |   0.00575979  | 1.02528   |
| spec_x_mb           |              2470 |                 281 |   0.0133023   | 1.08932   |
| spec_ai             |              2789 |                 316 |   0.0103503   | 0.675935  |

## Output Files

- `results/v36_spec_ai_firm_char_guard_20260605/analysis_panel_with_firm_chars.csv.gz`
- `results/v36_spec_ai_firm_char_guard_20260605/spec_ai_firm_char_guard_regressions.csv`
- `results/v36_spec_ai_firm_char_guard_20260605/spec_ai_firm_char_guard_compact.csv`
- `results/v36_spec_ai_firm_char_guard_20260605/firm_char_coverage.csv`