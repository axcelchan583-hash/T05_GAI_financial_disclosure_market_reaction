# v6 AI 词剔除版产品相似度检验（2026-05-24）

## 这轮做了什么

本轮处理一个关键质疑：

```text
当前 Top5 产品市场近邻结果，
会不会只是因为主营业务文本里共同出现 AI / 大模型 / 智能 / 算法等词，
导致两个“AI 公司”被机械地识别为竞品？
```

为此，先从公司主营业务 / 产品描述文本中剔除通用 AI 词，再重新计算产品市场相似度与 Top5 / Top10 peer network。

脚本：

```text
scripts/run_v6_ai_stripped_similarity_checks_20260524.py
```

结果目录：

```text
results/v6_ai_stripped_similarity_checks_20260524
```

主要输出：

```text
ai_stripped_product_peer_network_top10.csv
ai_stripped_peer_market_model_car_panel_with_ann_flags.csv.gz
v6_ai_stripped_similarity_regressions.csv
v6_ai_stripped_similarity_sample_summary.csv
ai_stripped_vs_original_peer_overlap.csv
```

## 剔除词表

剔除对象包括：

```text
生成式人工智能 / 生成式AI / 人工智能 / AI大模型 / 大模型 / 大语言模型
AIGC / GenAI / ChatGPT / DeepSeek / GPT / LLM / RAG / MaaS
Kimi / 通义 / 文心 / 讯飞星火 / 智谱 / 豆包
机器学习 / 深度学习 / 自然语言处理 / 计算机视觉 / 算法 / 智能 / 智慧
```

剔除后重新用中文字符 n-gram TF-IDF 计算公司间 cosine similarity。

## 与原始 peer network 的重合度

| TopN | focal firms | mean overlap | median overlap |
|---:|---:|---:|---:|
| 5 | 2,651 | 0.956 | 1.000 |
| 10 | 2,651 | 0.959 | 1.000 |

读法：

```text
剔除 AI 词没有大规模改变 peer network。
这说明原始产品相似度主要不是由 AI 词本身撑起来的；
但仍需要报告该稳健性，因为它直接回应“AI 公司机械相似”的审稿质疑。
```

## 样本规模

| TopN | sample | N | events | focal firms | peer firms | mean AIActivePeer |
|---:|---|---:|---:|---:|---:|---:|
| 5 | baseline | 11,273 | 2,645 | 2,645 | 3,973 | 0.258 |
| 5 | drop either cleaning announcement | 8,655 | 2,415 | 2,415 | 3,550 | 0.252 |
| 10 | baseline | 22,509 | 2,650 | 2,650 | 4,774 | 0.262 |
| 10 | drop either cleaning announcement | 17,261 | 2,431 | 2,431 | 4,506 | 0.257 |

这里的 `drop either cleaning announcement` 指同时剔除焦点公司与竞品在事件窗内存在重大/定期/业绩/风险类公告的观测。

## 主效应结果

模型保持不变：

```text
Y = peer market-model CAR[0,+1] 或 CAR[-1,+1]
X = Specificity_z × AIActivePeer
FE = event FE；补充 event FE + peer industry-week FE
SE = event × peer firm 双向聚类
```

关键结果：

| TopN | sample | Y | FE | coef | p | N | events |
|---:|---|---|---|---:|---:|---:|---:|
| 5 | baseline | CAR[0,+1] | event FE | -0.001784 | 0.014 | 11,273 | 2,645 |
| 5 | baseline | CAR[0,+1] | event FE + peer industry-week FE | -0.001401 | 0.096 | 11,273 | 2,645 |
| 5 | drop either cleaning announcement | CAR[0,+1] | event FE | -0.002124 | 0.011 | 8,655 | 2,415 |
| 5 | drop either cleaning announcement | CAR[0,+1] | event FE + peer industry-week FE | -0.002041 | 0.033 | 8,655 | 2,415 |
| 10 | drop either cleaning announcement | CAR[0,+1] | event FE | -0.001297 | 0.038 | 17,261 | 2,431 |
| 10 | drop either cleaning announcement | CAR[0,+1] | event FE + peer industry-week FE | -0.001481 | 0.027 | 17,261 | 2,431 |

`CAR[-1,+1]` 方向一致但弱一些：

| TopN | sample | Y | FE | coef | p |
|---:|---|---|---|---:|---:|
| 5 | drop either cleaning announcement | CAR[-1,+1] | event FE | -0.001793 | 0.066 |
| 5 | drop either cleaning announcement | CAR[-1,+1] | event FE + peer industry-week FE | -0.001375 | 0.223 |
| 10 | drop either cleaning announcement | CAR[-1,+1] | event FE | -0.001251 | 0.095 |
| 10 | drop either cleaning announcement | CAR[-1,+1] | event FE + peer industry-week FE | -0.001336 | 0.093 |

## 当前判断

这轮结果通过了关键稳健性：

```text
即使从产品描述文本中剔除 AI / GenAI / 大模型 / 智能 / 算法等词，
焦点公司首次 GenAI 披露越具体，
事前 AI-active 的 Top5 产品市场近邻竞品仍在 [0,+1] 窗口出现更负的 market-model CAR。
```

最适合作为主表的版本是：

```text
Top5, first focal event, AI-word-stripped product similarity,
drop focal and peer cleaning announcements,
Y = market-model CAR[0,+1],
FE = event FE + peer industry-week FE,

Specificity_z × AIActivePeer:
coef = -0.002041, p = 0.033
```

这不等于完全解决识别问题，但它能排除一个重要机械解释：

```text
结果不是简单由主营业务文本中的 AI 词共同出现造成的。
```

下一步继续做两项：

```text
1. 用 CAC 备案、AI/GenAI 专利、AI 招聘、历史 GenAI 披露构造外部 pre-event AIActivePeer。
2. 在最新公告清洗样本上重跑 100 次随机同业 placebo。
```
