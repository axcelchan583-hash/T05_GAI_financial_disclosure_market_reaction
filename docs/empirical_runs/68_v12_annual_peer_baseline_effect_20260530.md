# v12 Annual-Report Peer Baseline Announcement Effect

日期：2026-05-30

## Purpose

This table asks the simpler question before using specificity or AIActivePeer:

```text
Does a focal GenAI disclosure event have an average market reaction among annual-report product-market peers?
```

The test is an intercept-only event-study mean with two-way clustered standard errors by focal event and peer firm.

## Mean Peer CAR Against Zero

| peer_source               |   top_n | outcome           |   estimate |       se |        p |   nobs |   events |   peer_firms |
|:--------------------------|--------:|:------------------|-----------:|---------:|---------:|-------:|---------:|-------------:|
| annual_same_industry_d    |       5 | peer_car_0_p1_mm  |   0.000209 | 0.000501 | 0.676301 |   8353 |     2283 |         3103 |
| annual_same_industry_d    |       5 | peer_car_m1_p1_mm |   0.000606 | 0.000635 | 0.339349 |   8353 |     2283 |         3103 |
| annual_same_industry_d    |      10 | peer_car_0_p1_mm  |  -0.000118 | 0.000462 | 0.79801  |  16475 |     2305 |         3860 |
| annual_same_industry_d    |      10 | peer_car_m1_p1_mm |   0.000194 | 0.000582 | 0.739208 |  16475 |     2305 |         3860 |
| annual_global             |       5 | peer_car_0_p1_mm  |   0.000512 | 0.00052  | 0.325299 |   8232 |     2292 |         2822 |
| annual_global             |       5 | peer_car_m1_p1_mm |   0.001023 | 0.000651 | 0.116359 |   8232 |     2292 |         2822 |
| annual_global             |      10 | peer_car_0_p1_mm  |   0.00012  | 0.000452 | 0.790119 |  16407 |     2307 |         3558 |
| annual_global             |      10 | peer_car_m1_p1_mm |   0.000486 | 0.00058  | 0.402253 |  16407 |     2307 |         3558 |
| annual_global_ai_stripped |       5 | peer_car_0_p1_mm  |   0.00058  | 0.00052  | 0.265282 |   8232 |     2291 |         2811 |
| annual_global_ai_stripped |       5 | peer_car_m1_p1_mm |   0.00101  | 0.000656 | 0.123486 |   8232 |     2291 |         2811 |
| annual_global_ai_stripped |      10 | peer_car_0_p1_mm  |  -3e-06    | 0.00045  | 0.994025 |  16376 |     2307 |         3546 |
| annual_global_ai_stripped |      10 | peer_car_m1_p1_mm |   0.000448 | 0.000578 | 0.438686 |  16376 |     2307 |         3546 |

## Top5 Minus Ranks 6-10

| peer_source               | comparison            | outcome           |     coef |       se |        p |   nobs |   events |   peer_firms |
|:--------------------------|:----------------------|:------------------|---------:|---------:|---------:|-------:|---------:|-------------:|
| annual_same_industry_d    | Top5 minus ranks 6-10 | peer_car_0_p1_mm  | 0.000664 | 0.000446 | 0.136733 |  16475 |     2305 |         3860 |
| annual_same_industry_d    | Top5 minus ranks 6-10 | peer_car_m1_p1_mm | 0.000837 | 0.000541 | 0.121762 |  16475 |     2305 |         3860 |
| annual_global             | Top5 minus ranks 6-10 | peer_car_0_p1_mm  | 0.000786 | 0.000483 | 0.103719 |  16407 |     2307 |         3558 |
| annual_global             | Top5 minus ranks 6-10 | peer_car_m1_p1_mm | 0.001077 | 0.000571 | 0.059232 |  16407 |     2307 |         3558 |
| annual_global_ai_stripped | Top5 minus ranks 6-10 | peer_car_0_p1_mm  | 0.001172 | 0.000489 | 0.016469 |  16376 |     2307 |         3546 |
| annual_global_ai_stripped | Top5 minus ranks 6-10 | peer_car_m1_p1_mm | 0.001132 | 0.000563 | 0.044567 |  16376 |     2307 |         3546 |

## Interpretation

年报 peer 网络下，GenAI 披露事件本身对 peer 的平均 CAR 没有稳定负向反应。
同细分行业 Top5 的 `CAR[0,+1]` 均值为正且不显著；global / AI-word-stripped global
也不显著。Top5 与 ranks 6-10 的差异同样不显著。

这与旧 CSMAR peer 口径的 v11 baseline 一致：平均公告效应不是当前论文能讲的主故事。
如果继续 peer-CAR 设计，必须依赖有文献和理论支撑的条件效应，而不是简单公告平均效应。
