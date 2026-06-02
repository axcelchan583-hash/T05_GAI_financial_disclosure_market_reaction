# v23 Qian 供应商主效应中国复刻审计

日期：2026-06-02

## 结论

本轮只做 `Qian et al. supplier stock reaction` 的最小复刻审计，不把结果包装成新论文。

> **2026-06-02 复核后补注（理解校正）**：原 verdict `main_effect_not_replicated` 容易误读为"无结果/null"。
> 实际不是 null，而是**符号反转**：中国上游供应商在客户 GenAI 事件日呈现**显著负向** AR，与 Qian 的
> 正向 +0.27% 方向相反。预设判据只检验"正向显著"，所以判 False；但真正的发现是反向显著。
> 详见文末 `## 复刻教会我们关于 Qian 的什么`。

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

## 复刻教会我们关于 Qian 的什么

这次"复刻不出正向"恰恰是理解 Qian (2025) 外部效度的最好方式。容器内对已 push 分析样本的独立复核（market-model AR）：

| 样本 | 关系 | day0 AR | t | p | 正比例 | sign p | 对照 Qian(US) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| first valid | upstream supplier | -0.277% | -2.06 | 0.040 | 0.398 | 0.001 | +0.27%, p<0.01 |
| all valid | upstream supplier | -0.184% | -2.58 | 0.010 | 0.432 | <0.001 | （方向相反） |

辅助事实：
- day-1 不显著（first 样本 p=0.93），缩尾 1/99 后 day0 更强（p=0.033 / 0.004）。
- 方向 placebo 干净：同批客户的 `downstream_customer` 关系 day0 ≈ 0（p=0.74）→ 负向**特定于上游供应商**，不是泛 AI 行情。
- 负向集中在 2024 年（-0.91%, p=0.027, 正比例 0.21）与"供应商主动列出该客户"那类边（-0.40%, p=0.053）。

由此得到对 Qian 的三点理解：

1. **Qian 的正号高度依赖美国 GenAI 供应链的"真投入品"构成**（GPU/半导体/算力等，需求被下游 GenAI 投资真实拉动）。一旦换成中国互动平台 GenAI 披露 × CSMAR 传统供应链，"需求溢出"机制失去载体。
2. **正号还依赖事件源 + 关系数据库**：Qian 用新闻通讯社的"首次具体 GenAI initiative" + Compustat Segment/FactSet 富供应链。中国正式公告路径在本审计里只剩 4 条（见样本流），必须用 GenAI 事件库扩样才有 N。
3. **中国样本的负向反转**与本项目 T05 主线"市场把 GenAI 披露读成对相关方的负面/竞争性信号"同源；对上游供应商更像**替代 / 去中介化**担忧，而非增量需求。

结论：Qian 不是"可移植的待复刻基准"，而是一个**符号会随制度与供应链构成而反转**的纵向溢出结果。本审计到此为止——是否把负向反转发展成对照表或独立检验，留待"三篇都吃透后再设计自有实验"阶段决定。
