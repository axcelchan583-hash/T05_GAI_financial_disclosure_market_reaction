# Claude Manual Coding Summary (SV0001-SV0300)

Coder: claude_opus_coder
Coding dates: 2026-05-26 (SV0001-SV0160), 2026-05-27 (SV0161-SV0300)

## Totals

- Total coded rows: 300
- SV0001-SV0160 preserved from prior Claude web coding
- SV0161-SV0300 coded in this run (n=140)

## Score distribution (0-4)

| Score | Count | Share |
|---|---|---|
| 0 | 195 | 65.0% |
| 1 | 33 | 11.0% |
| 2 | 26 | 8.7% |
| 3 | 31 | 10.3% |
| 4 | 15 | 5.0% |

## Component `1` counts (out of 300)

| Component | Count of 1 | Share |
|---|---|---|
| C1 specific_product_service | 46 | 15.3% |
| C2 model_platform_name | 60 | 20.0% |
| C3 specific_use_case | 74 | 24.7% |
| C4 customer_or_industry | 31 | 10.3% |
| C5 partner_or_org | 13 | 4.3% |
| C6 deployment_status | 62 | 20.7% |
| C7 commercialization_or_timeline | 2 | 0.7% |
| C8 quantitative_commitment | 1 | 0.3% |

## uncertain_flag

- Count of 1: 22
- Count of 9 in any component: 0

## 10 validation_ids most likely to show coder disagreement

Limited to SV0161-SV0300 (rows coded in this run); ordered by judgment difficulty.

| validation_id | Reason |
|---|---|
| SV0177 | 自称AI大模型驱动但实际谈低空经济,边界争议 |
| SV0182 | AI大模型用于数据分析但模型未具名,场景泛 |
| SV0195 | 6nm芯片+端侧RAG平台,GenAI性质对端侧AI是否算GenAI存疑 |
| SV0200 | XSimAi为强化学习非GenAI,但同时提大模型应用 |
| SV0205 | 文心一言生态体验官身份成立但接入程度模糊 |
| SV0207 | 孩子王成为百度生态伙伴但接入是后续,得分2/3之间 |
| SV0214 | 数字代言人Yona按阶段接入,部署状态界定模糊 |
| SV0254 | 公众号宣称接入DeepSeek但公司答复否认正式合作 |
| SV0264 | 母公司中国宝武已部署,子公司中钢洛耐自身未必 |
| SV0274 | DeepSeek办公已用但本地化部署是9月计划,C6/C7界定模糊 |

## Method notes

- Followed `coding_guidelines.md` and `10_specificity_validation_codebook_20260525.md`.
- Coding is independent human-judgment style; no keyword/specificity_z matching.
- Off-construct AI (CV/OCR/RPA/AI chip supply/优化算法 etc.) coded 0 on GenAI components even when impressive; uncertain_flag=1 where construct boundary is genuinely fuzzy (SV0177, SV0182, SV0184, SV0193, SV0195, SV0200, SV0215, SV0217, SV0221, SV0224, SV0254, SV0264).
- Denials and pure attention coded all 0 / score 0 (vast majority of bin=high DeepSeek-era rows that did not have actual deployment).
- Component value `9` was not needed; binary judgment was reachable for every cell.
