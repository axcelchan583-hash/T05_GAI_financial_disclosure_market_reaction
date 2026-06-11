# v34 analyst forecast revision probe

## Scope

- Input event-peer panel: v33 supplement panel.
- Analyst forecast source: local CSMAR `AF_Forecast*.xlsx`.
- Pre window: event date -90 to -1 calendar days.
- Post windows: event date to +30 and +60 calendar days.
- Forecast target years are event year (`target_offset=0`) and event year + 1 (`target_offset=1`).
- Consensus uses each analyst/broker's latest forecast inside the pre/post window, then averages across analysts.
- This is a diagnostic pass; final use needs stronger forecast-target and analyst-coverage rules.

## Headline Read

1. Analyst forecast coverage is sparse. The 60-day revision cells cover about 185 event-peer rows, 100 events, and 105 peer firms, or roughly 6.6% of the current event-peer panel.
2. Among covered observations, FY+1 EPS and FY+1 parent-profit forecasts are revised downward after focal GenAI events. The 60-day scaled revisions are about -10.6% for EPS and -9.5% for parent profit.
3. Current-year forecast revisions have the same negative direction but are not statistically sharp in this first pass.
4. Short-window peer CAR does not predict the size of analyst forecast revisions. The evidence is therefore a weak cash-flow-expectation bridge, not yet a clean cross-sectional mechanism.
5. `revision_down_rate` is reported as a descriptive rate. Its displayed mean-test p-value should not be read as a sign test against 0.5 in this diagnostic version.

## AF Source Coverage

|   af_rows_after_filter |   af_firms | min_report_dt       | max_report_dt       |   min_target_year |   max_target_year |
|-----------------------:|-----------:|:--------------------|:--------------------|------------------:|------------------:|
|                  29158 |        223 | 2022-10-11 00:00:00 | 2026-02-13 00:00:00 |              2022 |              2033 |

## Revision Coverage

| metric        |   target_offset |   post_horizon_days |   total_rows |   revision_rows |   events |   covered_events |   peer_firms |   covered_peer_firms |   mean_pre_analysts |   mean_post_analysts |   coverage |
|:--------------|----------------:|--------------------:|-------------:|----------------:|---------:|-----------------:|-------------:|---------------------:|--------------------:|---------------------:|-----------:|
| feps          |               0 |                  30 |         2789 |             147 |      316 |               82 |         1384 |                   86 |            0.400143 |             0.221226 |   0.052707 |
| feps          |               0 |                  60 |         2789 |             183 |      316 |               99 |         1384 |                  105 |            0.400143 |             0.336321 |   0.065615 |
| feps          |               1 |                  30 |         2789 |             147 |      316 |               82 |         1384 |                   86 |            0.400143 |             0.221226 |   0.052707 |
| feps          |               1 |                  60 |         2789 |             185 |      316 |              100 |         1384 |                  105 |            0.400143 |             0.336321 |   0.066332 |
| profit_parent |               0 |                  30 |         2789 |             147 |      316 |               82 |         1384 |                   86 |            0.399785 |             0.220509 |   0.052707 |
| profit_parent |               0 |                  60 |         2789 |             185 |      316 |              100 |         1384 |                  105 |            0.399785 |             0.335604 |   0.066332 |
| profit_parent |               1 |                  30 |         2789 |             147 |      316 |               82 |         1384 |                   86 |            0.399785 |             0.220509 |   0.052707 |
| profit_parent |               1 |                  60 |         2789 |             185 |      316 |              100 |         1384 |                  105 |            0.399785 |             0.335604 |   0.066332 |
| turnover      |               0 |                  30 |         2789 |             147 |      316 |               82 |         1384 |                   86 |            0.400143 |             0.221226 |   0.052707 |
| turnover      |               0 |                  60 |         2789 |             185 |      316 |              100 |         1384 |                  105 |            0.400143 |             0.336321 |   0.066332 |
| turnover      |               1 |                  30 |         2789 |             147 |      316 |               82 |         1384 |                   86 |            0.400143 |             0.221226 |   0.052707 |
| turnover      |               1 |                  60 |         2789 |             185 |      316 |              100 |         1384 |                  105 |            0.400143 |             0.336321 |   0.066332 |

## Mean Forecast Revisions

| metric        |   target_offset |   post_horizon_days | outcome            |   nobs |   events |   peer_firms |   coef_or_mean |       se |         z |        p |
|:--------------|----------------:|--------------------:|:-------------------|-------:|---------:|-------------:|---------------:|---------:|----------:|---------:|
| feps          |               0 |                  30 | revision_scaled    |    147 |       82 |           86 |      -0.133277 | 0.106294 | -1.25385  | 0.209897 |
| feps          |               0 |                  30 | revision_down_rate |    147 |       82 |           86 |       0.585034 | 0.062573 |  9.34958  | 0        |
| feps          |               0 |                  60 | revision_scaled    |    183 |       99 |          105 |      -0.128056 | 0.098285 | -1.3029   | 0.192607 |
| feps          |               0 |                  60 | revision_down_rate |    185 |      100 |          105 |       0.621622 | 0.050898 | 12.2131   | 0        |
| feps          |               1 |                  30 | revision_scaled    |    147 |       82 |           86 |      -0.094091 | 0.041127 | -2.2878   | 0.022149 |
| feps          |               1 |                  30 | revision_down_rate |    147 |       82 |           86 |       0.530612 | 0.054483 |  9.73903  | 0        |
| feps          |               1 |                  60 | revision_scaled    |    185 |      100 |          105 |      -0.105608 | 0.040848 | -2.58537  | 0.009727 |
| feps          |               1 |                  60 | revision_down_rate |    185 |      100 |          105 |       0.6      | 0.050124 | 11.9702   | 0        |
| profit_parent |               0 |                  30 | revision_scaled    |    147 |       82 |           86 |      -0.132066 | 0.1024   | -1.28971  | 0.197153 |
| profit_parent |               0 |                  30 | revision_down_rate |    147 |       82 |           86 |       0.571429 | 0.054512 | 10.4826   | 0        |
| profit_parent |               0 |                  60 | revision_scaled    |    185 |      100 |          105 |      -0.118997 | 0.095346 | -1.24805  | 0.212015 |
| profit_parent |               0 |                  60 | revision_down_rate |    185 |      100 |          105 |       0.621622 | 0.046493 | 13.3703   | 0        |
| profit_parent |               1 |                  30 | revision_scaled    |    147 |       82 |           86 |      -0.087985 | 0.045529 | -1.93253  | 0.053294 |
| profit_parent |               1 |                  30 | revision_down_rate |    147 |       82 |           86 |       0.503401 | 0.05059  |  9.95063  | 0        |
| profit_parent |               1 |                  60 | revision_scaled    |    185 |      100 |          105 |      -0.095296 | 0.044619 | -2.13577  | 0.032698 |
| profit_parent |               1 |                  60 | revision_down_rate |    185 |      100 |          105 |       0.594595 | 0.047641 | 12.4807   | 0        |
| turnover      |               0 |                  30 | revision_scaled    |    147 |       82 |           86 |      -0.018193 | 0.00849  | -2.14277  | 0.032131 |
| turnover      |               0 |                  30 | revision_down_rate |    147 |       82 |           86 |       0.591837 | 0.061397 |  9.63953  | 0        |
| turnover      |               0 |                  60 | revision_scaled    |    185 |      100 |          105 |      -0.013392 | 0.014422 | -0.928545 | 0.353125 |
| turnover      |               0 |                  60 | revision_down_rate |    185 |      100 |          105 |       0.632432 | 0.043678 | 14.4793   | 0        |
| turnover      |               1 |                  30 | revision_scaled    |    147 |       82 |           86 |      -0.011801 | 0.009732 | -1.2126   | 0.225284 |
| turnover      |               1 |                  30 | revision_down_rate |    147 |       82 |           86 |       0.496599 | 0.06205  |  8.00319  | 0        |
| turnover      |               1 |                  60 | revision_scaled    |    185 |      100 |          105 |      -0.002839 | 0.021554 | -0.131728 | 0.895199 |
| turnover      |               1 |                  60 | revision_down_rate |    185 |      100 |          105 |       0.578378 | 0.051846 | 11.1556   | 0        |

## Peer CAR Predicting Forecast Revision

| metric        |   target_offset |   post_horizon_days | outcome         | regressor        | fe    |   nobs |   events |   peer_firms |   coef_or_mean |       se |         z |        p |
|:--------------|----------------:|--------------------:|:----------------|:-----------------|:------|-------:|---------:|-------------:|---------------:|---------:|----------:|---------:|
| feps          |               0 |                  30 | revision_scaled | peer_car_0_p1_mm | none  |    147 |       82 |           86 |       0.292458 | 1.20578  |  0.242547 | 0.808357 |
| feps          |               0 |                  30 | revision_scaled | peer_car_0_p1_mm | event |    147 |       82 |           86 |      -2.18326  | 4.98957  | -0.437564 | 0.661702 |
| feps          |               0 |                  60 | revision_scaled | peer_car_0_p1_mm | none  |    183 |       99 |          105 |       0.067419 | 1.00508  |  0.067078 | 0.946519 |
| feps          |               0 |                  60 | revision_scaled | peer_car_0_p1_mm | event |    183 |       99 |          105 |       0.157596 | 4.33798  |  0.036329 | 0.97102  |
| feps          |               1 |                  30 | revision_scaled | peer_car_0_p1_mm | none  |    147 |       82 |           86 |      -0.528688 | 0.783528 | -0.674753 | 0.499833 |
| feps          |               1 |                  30 | revision_scaled | peer_car_0_p1_mm | event |    147 |       82 |           86 |      -2.37224  | 3.8115   | -0.62239  | 0.533686 |
| feps          |               1 |                  60 | revision_scaled | peer_car_0_p1_mm | none  |    185 |      100 |          105 |      -0.463832 | 0.645871 | -0.71815  | 0.472665 |
| feps          |               1 |                  60 | revision_scaled | peer_car_0_p1_mm | event |    185 |      100 |          105 |      -0.798202 | 3.198    | -0.249594 | 0.802901 |
| profit_parent |               0 |                  30 | revision_scaled | peer_car_0_p1_mm | none  |    147 |       82 |           86 |       0.205629 | 1.19531  |  0.17203  | 0.863414 |
| profit_parent |               0 |                  30 | revision_scaled | peer_car_0_p1_mm | event |    147 |       82 |           86 |      -2.03993  | 4.96855  | -0.41057  | 0.681388 |
| profit_parent |               0 |                  60 | revision_scaled | peer_car_0_p1_mm | none  |    185 |      100 |          105 |      -0.068359 | 0.992584 | -0.06887  | 0.945093 |
| profit_parent |               0 |                  60 | revision_scaled | peer_car_0_p1_mm | event |    185 |      100 |          105 |       0.03095  | 4.27503  |  0.00724  | 0.994224 |
| profit_parent |               1 |                  30 | revision_scaled | peer_car_0_p1_mm | none  |    147 |       82 |           86 |      -0.5844   | 0.810903 | -0.720678 | 0.471108 |
| profit_parent |               1 |                  30 | revision_scaled | peer_car_0_p1_mm | event |    147 |       82 |           86 |      -2.23337  | 3.71899  | -0.600532 | 0.548152 |
| profit_parent |               1 |                  60 | revision_scaled | peer_car_0_p1_mm | none  |    185 |      100 |          105 |      -0.590378 | 0.663153 | -0.890258 | 0.373327 |
| profit_parent |               1 |                  60 | revision_scaled | peer_car_0_p1_mm | event |    185 |      100 |          105 |      -0.925554 | 3.09605  | -0.298947 | 0.764981 |
| turnover      |               0 |                  30 | revision_scaled | peer_car_0_p1_mm | none  |    147 |       82 |           86 |      -0.038393 | 0.146472 | -0.26212  | 0.793229 |
| turnover      |               0 |                  30 | revision_scaled | peer_car_0_p1_mm | event |    147 |       82 |           86 |      -0.311965 | 0.465149 | -0.670676 | 0.502427 |
| turnover      |               0 |                  60 | revision_scaled | peer_car_0_p1_mm | none  |    185 |      100 |          105 |      -0.061841 | 0.155244 | -0.398343 | 0.690377 |
| turnover      |               0 |                  60 | revision_scaled | peer_car_0_p1_mm | event |    185 |      100 |          105 |      -0.099196 | 0.433613 | -0.228767 | 0.81905  |
| turnover      |               1 |                  30 | revision_scaled | peer_car_0_p1_mm | none  |    147 |       82 |           86 |      -0.042111 | 0.17173  | -0.245214 | 0.806291 |
| turnover      |               1 |                  30 | revision_scaled | peer_car_0_p1_mm | event |    147 |       82 |           86 |      -0.218923 | 0.650504 | -0.336544 | 0.736461 |
| turnover      |               1 |                  60 | revision_scaled | peer_car_0_p1_mm | none  |    185 |      100 |          105 |       0.021393 | 0.320486 |  0.066752 | 0.946779 |
| turnover      |               1 |                  60 | revision_scaled | peer_car_0_p1_mm | event |    185 |      100 |          105 |       0.051169 | 0.537365 |  0.095222 | 0.924139 |

## Output Files

- `results/v34_analyst_forecast_revision_probe_20260605/analyst_revision_panel.csv.gz`
- `results/v34_analyst_forecast_revision_probe_20260605/revision_coverage.csv`
- `results/v34_analyst_forecast_revision_probe_20260605/revision_mean_tests.csv`
- `results/v34_analyst_forecast_revision_probe_20260605/revision_peer_car_regressions.csv`
- `results/v34_analyst_forecast_revision_probe_20260605/af_source_meta.csv`
