# v23 Qian 供应商主效应中国复刻审计

日期：2026-06-02

## 结论

本轮只做 `Qian et al. supplier stock reaction` 的最小复刻审计，不把结果包装成新论文。

预设判据：

```text
first valid focal event per firm
upstream listed supplier
AR0 或 CAR[0,+1] > 0 且 p < 0.10
Day -1 不显著
对应正收益比例 > 0.5
```

审计结论：

| main_sample | main_relation | verdict | ar0_signal | car0p1_signal | day_m1_not_significant | reason |
| --- | --- | --- | --- | --- | --- | --- |
| first_valid_events | upstream_supplier | main_effect_not_replicated | False | False | True | first-event upstream supplier AR0/CAR[0,+1] does not satisfy the pre-specified positive-significance-positive-rate gate |

## 样本流失

| sample | stage | rows | events | affected_firms | upstream_rows | downstream_rows |
| --- | --- | --- | --- | --- | --- | --- |
| first_valid_events | after_ar0_available | 546 | 325 | 388 | 259 | 287 |
| first_valid_events | after_car0p1_available | 543 | 325 | 386 | 257 | 286 |
| all_valid_events | after_ar0_available | 3013 | 1919 | 430 | 1180 | 1833 |
| all_valid_events | after_car0p1_available | 2991 | 1914 | 429 | 1171 | 1820 |
| formal_announcement_only | after_ar0_available | 4 | 3 | 3 | 4 | 0 |
| formal_announcement_only | after_car0p1_available | 4 | 3 | 3 | 4 | 0 |

## 主样本 Qian-style AR[-1,0,+1]

| day | n | mean | se | t | p_ttest | median | positive_rate | p_sign | p_wilcoxon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| day_m1 | 255 | -0.000124197 | 0.00132285 | -0.0938858 | 0.925274 | -0.00147321 | 0.458824 | 0.210322 | 0.402965 |
| day_0 | 259 | -0.00277042 | 0.00134542 | -2.05915 | 0.0404832 | -0.00386159 | 0.397683 | 0.00119077 | 0.0145014 |
| day_p1 | 259 | -0.000937048 | 0.00142566 | -0.657272 | 0.511592 | -0.000539959 | 0.486486 | 0.709358 | 0.359396 |

## 主样本 CAR

| outcome | n | mean | se | t | p_ttest | median | positive_rate | p_sign | p_wilcoxon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car_0_p1_mm | 257 | -0.00351416 | 0.00198713 | -1.76846 | 0.0781752 | -0.00179859 | 0.44358 | 0.0805063 | 0.0327041 |
| car_m1_p1_mm | 253 | -0.00323469 | 0.00241523 | -1.33929 | 0.181685 | -0.00550219 | 0.41502 | 0.00815072 | 0.0716899 |

## 方向 placebo

`downstream_customer` 只用于判断是否存在泛 AI 热点反应，不作为 Qian-style 主结果。

| sample | relation | day | n | mean | se | t | p_ttest | median | positive_rate | p_sign | p_wilcoxon | test_type | outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| first_valid_events | downstream_customer | day_m1 | 290 | -0.000177032 | 0.00108688 | -0.162881 | 0.870726 | -0.00186189 | 0.431034 | 0.0218498 | 0.102259 | AR day |  |
| first_valid_events | downstream_customer | day_0 | 287 | 0.000335586 | 0.00101205 | 0.331589 | 0.740442 | -0.000786197 | 0.477352 | 0.4788 | 0.305166 | AR day |  |
| first_valid_events | downstream_customer | day_p1 | 290 | -0.0010633 | 0.00124023 | -0.857339 | 0.391968 | 0.000187082 | 0.506897 | 0.860202 | 0.824754 | AR day |  |
| all_valid_events | downstream_customer | day_m1 | 1836 | -0.000444712 | 0.000426752 | -1.04208 | 0.29751 | -0.00105284 | 0.471678 | 0.0162019 | 0.00674926 | AR day |  |
| all_valid_events | downstream_customer | day_0 | 1833 | -6.27229e-05 | 0.000446857 | -0.140365 | 0.888387 | -0.000923623 | 0.47245 | 0.0194817 | 0.0269685 | AR day |  |
| all_valid_events | downstream_customer | day_p1 | 1833 | -0.000638106 | 0.000437757 | -1.45767 | 0.145102 | -0.000805583 | 0.469722 | 0.0101718 | 0.0160182 | AR day |  |
| first_valid_events | downstream_customer |  | 286 | -3.02465e-05 | 0.0014706 | -0.0205674 | 0.983605 | -0.000529635 | 0.48951 | 0.767553 | 0.723373 | CAR | car_0_p1_mm |
| first_valid_events | downstream_customer |  | 284 | 0.000148707 | 0.00191043 | 0.0778395 | 0.938011 | -0.00269278 | 0.43662 | 0.0376269 | 0.333742 | CAR | car_m1_p1_mm |
| all_valid_events | downstream_customer |  | 1820 | -0.000904572 | 0.000606222 | -1.49215 | 0.135834 | -0.00148869 | 0.467033 | 0.0052664 | 0.00370039 | CAR | car_0_p1_mm |
| all_valid_events | downstream_customer |  | 1811 | -0.0013012 | 0.000719921 | -1.80742 | 0.0708631 | -0.00279038 | 0.443401 | 1.59801e-06 | 0.000516886 | CAR | car_m1_p1_mm |

## 校验

| sample | check | passed | violations |
| --- | --- | --- | --- |
| first_valid_events | relation_year_window_ok | True | 0 |
| first_valid_events | customer_not_equal_affected | True | 0 |
| first_valid_events | ar0_has_valid_market_model_days_only | True | 0 |
| first_valid_events | car0p1_requires_valid_day0_and_day1 | True | 0 |
| all_valid_events | relation_year_window_ok | True | 0 |
| all_valid_events | customer_not_equal_affected | True | 0 |
| all_valid_events | ar0_has_valid_market_model_days_only | True | 0 |
| all_valid_events | car0p1_requires_valid_day0_and_day1 | True | 0 |
| formal_announcement_only | relation_year_window_ok | True | 0 |
| formal_announcement_only | customer_not_equal_affected | True | 0 |
| formal_announcement_only | ar0_has_valid_market_model_days_only | True | 0 |
| formal_announcement_only | car0p1_requires_valid_day0_and_day1 | True | 0 |

## 口径说明

- 事件：2023 年后严格 GenAI 事件，要求文本或触发词含 `AIGC / ChatGPT / GPT / 大模型 / 生成式AI / DeepSeek / LLM` 等；不靠泛 AI、RAG、Agent、NLP 单独入样。
- 供应链：CSMAR 供应链网络关系表和前五大供应商/客户表；关系年份必须在事件年前 5 年到前 1 年。
- 主关系：`upstream_supplier`，即 focal customer 的既有上市供应商。
- 最小混杂处理：剔除供应商自身在客户事件日之前或当天已有严格 GenAI 事件的观测。
- AR：使用现有 market-model 参数，剔除停牌、涨跌停、缺失 alpha/beta 或缺失收益的交易日。
- 未完成限制：本轮未系统剔除供应商同日业绩、并购、重大合同、监管处罚等非 GenAI 重大公告污染；也未做 PSM、IV、Heckman 或异质性。
