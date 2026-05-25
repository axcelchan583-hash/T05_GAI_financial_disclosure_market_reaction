# v8.3 年报文本 pilot：GenAI forward-looking claim 抽取

**日期**：2026-05-17

## 1. 这次跑了什么

数据源：

```text
2024 年 A 股年报 TXT，共 5405 份：用于抽取 forward-looking GenAI claim
2025 年 A 股年报 TXT，共 5440 份：用于扫描一年后的 textual realization clues
```

抽取规则：

```text
句子包含 GenAI-specific 关键词
且包含前瞻性动词 / 计划性动词
```

这比上一版 firm-year 粗 pilot 更接近 v8.3，但仍不是最终主实验。原因是：

```text
current support 仍用年度 AI 投资表近似
future realization 使用 2025 AI 投资表 + 2025 年报同 claim type 文本线索近似
还没有做 claim-type matched hard evidence
```

## 2. 抽取结果

```text
含 GenAI 关键词的年报数：1615
含 forward-looking GenAI candidate 的年报数：1321
candidate sentence 数：7469
candidate firm 数：1321
2025 年报含 GenAI 关键词公司数：2031
2025 年报含 GenAI 落地线索公司数：1160
2025 年报 GenAI 落地线索句子数：5105
```

## 3. 粗 2x2

```text
HighSpecificity = SpecificityScore >= 3
NoCurrentAISupport_2024 = 2024 年 AI 投资表无支撑
FutureAISupport_2025 = 2025 年 AI 投资表有支撑
FutureTypeMatchedTextEvidence_2025 = 2025 年报中出现同公司、同 claim type 的 GenAI 落地线索
FutureAnyEvidence_2025 = FutureAISupport_2025 或 FutureTypeMatchedTextEvidence_2025
```

| HighSpecificity   | NoCurrentAISupport_2024   |   n_sentences |   n_firms |   future_2025_invest_support_available |   future_2025_invest_support_rate |   future_2025_text_type_evidence_rate |   future_2025_any_evidence_rate |   mean_specificity |
|:------------------|:--------------------------|--------------:|----------:|---------------------------------------:|----------------------------------:|--------------------------------------:|--------------------------------:|-------------------:|
| False             | False                     |          6101 |      1183 |                                 0.1773 |                            0.1764 |                                0.7646 |                          0.8172 |             1.3981 |
| False             | True                      |           368 |        85 |                                 0.0326 |                            0.0326 |                                0.625  |                          0.6576 |             1.3886 |
| True              | False                     |           944 |       404 |                                 0.1271 |                            0.1261 |                                0.786  |                          0.822  |             3.1345 |
| True              | True                      |            56 |        30 |                                 0      |                            0      |                                0.7321 |                          0.7321 |             3.1071 |

核心格：

```text
HighSpecificity = 1 且 NoCurrentAISupport_2024 = 1
```

样本量：

```text
56 sentences
30 firms
```

## 4. Claim type 分布

| claim_type                   |   n_sentences |   n_firms |   mean_specificity |   high_specificity_share |   no_current_support_share |   future_text_type_evidence_rate |   future_any_evidence_rate |
|:-----------------------------|--------------:|----------:|-------------------:|-------------------------:|---------------------------:|---------------------------------:|---------------------------:|
| foundation_model             |          5511 |      1132 |             1.6803 |                   0.137  |                     0.0584 |                           0.8298 |                     0.8645 |
| specific_product_application |           764 |       305 |             1.6662 |                   0.1335 |                     0.0497 |                           0.7906 |                     0.8351 |
| generic_or_unclear           |           736 |       369 |             1.1386 |                   0.0571 |                     0.0625 |                           0.4959 |                     0.6101 |
| application_integration      |           328 |       207 |             1.5945 |                   0.1738 |                     0.0335 |                           0.3598 |                     0.4573 |
| internal_workflow            |           130 |       100 |             2.1538 |                   0.3385 |                     0.0538 |                           0.1385 |                     0.3385 |

## 5. 输出文件

```text
/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_3_claim_text_pilot/annual_report_genai_forward_candidates_2024.csv
/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_3_claim_text_pilot/annual_report_genai_2x2_grid_2024.csv
/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_3_claim_text_pilot/annual_report_genai_by_claim_type_2024.csv
/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_3_claim_text_pilot/annual_report_genai_top_examples_2024.csv
/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_3_claim_text_pilot/annual_report_future_text_evidence_sentences_2025.csv
/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_3_claim_text_pilot/annual_report_future_text_evidence_by_type_2025.csv
```

## 6. 硬判断

这个 pilot 支持继续推进 v8.3 的原因：

```text
1. 2024 年报中能抽到 GenAI-specific forward-looking candidate
2. 能形成 HighSpecificity × NoCurrentSupport 的核心格
3. 可以做人工复核样本，检查 specificity rubric 是否可用
```

它还不能证明主效应，原因：

```text
1. 年报句子不是所有 GenAI claim 来源，只覆盖 formal annual report
2. current support 目前是 broad AI investment，不是 GenAI claim-type matched support
3. future realization 目前是 2025 broad AI investment support + 2025 annual-report textual clues，不是 matched hard evidence
4. 句子抽取仍是规则法，需要人工标注 valid / weak / invalid
```

下一步应该人工复核：

```text
/Users/mac/computerscience/23选题探索/T05_GAI_financial_disclosure_market_reaction/results/v8_3_claim_text_pilot/annual_report_genai_top_examples_2024.csv
```

重点看三件事：

```text
句子是否真的是 GenAI-specific
句子是否真的是 forward-looking claim
SpecificityScore >= 3 是否符合人类直觉
```
