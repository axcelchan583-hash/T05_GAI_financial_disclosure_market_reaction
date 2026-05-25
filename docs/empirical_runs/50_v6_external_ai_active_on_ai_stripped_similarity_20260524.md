# v6 外部 AIActivePeer × AI 词剔除产品相似度联合检验（2026-05-24）

## 这轮做了什么

本轮把两个关键防御同时叠加：

```text
1. ProductSimilarity:
   使用 AI-word-stripped 产品相似度，
   即从主营业务 / 产品描述中剔除 AI / AIGC / 大模型 / 智能 / 算法等通用词后重算 peer network。

2. AIActivePeer:
   使用外部 pre-event 行为证据，
   ext_any = prior CAC OR prior broad-AI patent grant OR >=1 broad-AI hiring in prior 365 days。
```

目的：

```text
确认主效应不是由“AI 词共同出现”定义竞品，
也不是完全由“历史 GenAI 披露文本”定义 AI-active peer。
```

脚本：

```text
scripts/run_v6_external_ai_active_ai_stripped_checks_20260524.py
```

结果目录：

```text
results/v6_external_ai_active_ai_stripped_checks_20260524
```

## 样本覆盖

公告清洗后：

| peer group | N | events | current text history | ext_any | ext_strict | ext_plus_history |
|---|---:|---:|---:|---:|---:|---:|
| AI-stripped Top5 | 8,655 | 2,415 | 0.252 | 0.205 | 0.103 | 0.319 |
| AI-stripped Top10 | 17,261 | 2,431 | 0.257 | 0.206 | 0.105 | 0.323 |

## 主结果：CAR[0,+1]

公告清洗样本，`Y = market-model CAR[0,+1]`。

### AI-stripped Top5

| AIActivePeer 口径 | FE | coef | p |
|---|---|---:|---:|
| current_text_history | event FE | -0.002124 | 0.011 |
| current_text_history | event FE + peer industry-week FE | -0.002041 | 0.033 |
| ext_any | event FE | -0.002118 | 0.011 |
| ext_any | event FE + peer industry-week FE | -0.002321 | 0.011 |
| ext_strict | event FE | -0.002863 | 0.016 |
| ext_strict | event FE + peer industry-week FE | -0.003340 | 0.007 |
| ext_plus_history | event FE | -0.002503 | 0.002 |
| ext_plus_history | event FE + peer industry-week FE | -0.002772 | 0.001 |

### AI-stripped Top10

| AIActivePeer 口径 | FE | coef | p |
|---|---|---:|---:|
| current_text_history | event FE | -0.001297 | 0.038 |
| current_text_history | event FE + peer industry-week FE | -0.001481 | 0.027 |
| ext_any | event FE | -0.001525 | 0.009 |
| ext_any | event FE + peer industry-week FE | -0.001343 | 0.029 |
| ext_plus_history | event FE | -0.001567 | 0.007 |
| ext_plus_history | event FE + peer industry-week FE | -0.001732 | 0.005 |

## 当前判断

这是目前最强的一轮稳健性：

```text
在同时使用 AI-word-stripped product similarity 和外部 ext_any AIActivePeer 时，
Top5 / Top10 的 CAR[0,+1] 主效应均为负且显著；
Top5 在 event FE + peer industry-week FE 下 p = 0.011。
```

可写入论文的保守表述：

```text
The result is robust to defining product-market peers after removing generic AI-related terms
and to defining AI-active peers using external pre-event evidence from CAC filings,
AI patent grants, and AI hiring postings.
```

仍要注意：

```text
ext_any 不是完美测度。
CAC A 股匹配是 lower-bound；
AI 专利目前是标题关键词；
AI 招聘尚未人工抽样验证关键词精度。
```

但它已经足以回应最核心的审稿质疑：

```text
主效应不是单纯文本同源、AI 词共同出现或历史披露定义造成的。
```
