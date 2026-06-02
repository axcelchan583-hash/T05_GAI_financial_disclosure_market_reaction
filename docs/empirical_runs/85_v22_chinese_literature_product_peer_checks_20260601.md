# v22 中文年报文本产品市场 peer 复刻检验

日期：2026-06-01

## 目的

本轮解决一个关键测量问题：当前显著结果依赖 `DeepSeek Flash-selected Top5 product-market peers`，但该 peer 口径不是完全照搬成熟文献。为降低“自造 peer”的风险，本轮按中国中文年报文本产品市场竞争文献重做 peer 网络。

本轮参考：

- 任宏达、王琨，2019，《会计研究》，《产品市场竞争与信息披露质量——基于上市公司年报文本分析的新证据》。
- 王琨、赵乐、任宏达，2020，《中国会计与财务研究》，《产品市场竞争与融资结构——基于公司年报文本分析的新证据》。
- 刘昌阳、刘亚辉、尹玉刚，2020，《世界经济》，《上市公司产品竞争与分析师研究报告文本信息》。

## 文献口径对应

### 1. Ren-Wang binary 口径

对应任宏达、王琨（2019）和王琨、赵乐、任宏达（2020）的核心做法：

```text
年报董事会报告/经营业务文本
-> 中文分词
-> 去停用词和非产品业务词
-> 产品业务词典
-> 公司-年度 0/1 词向量
-> firm-pair cosine similarity
-> TopN 产品市场近邻
```

本轮实现为：

- `ren_wang_binary_global`
- `ren_wang_binary_same_industry_d`

### 2. Liu-Liu-Yin product-TFIDF 口径

对应刘昌阳、刘亚辉、尹玉刚（2020）的产品词思路：

```text
产品词库/主营业务产品词
-> 年报产品词提取
-> TF-IDF 产品词向量
-> firm-pair cosine similarity
-> TopN 产品市场近邻
```

由于当前仓库没有阿里巴巴产品词库、搜狗细胞词库和 Wind 产品构成词库的原始完整版本，本轮用 CSMAR `MAINBUSSINESS` 与 `BusinessScope` 字段生成本地产品词库，作为可复现近似。

本轮实现为：

- `liu_product_tfidf_global`
- `liu_product_tfidf_same_industry_d`

## 脚本与输出

构网脚本：

```text
scripts/build_v22_chinese_literature_product_peers_20260601.py
```

回归脚本：

```text
scripts/run_v22_chinese_literature_peer_main_effect_20260601.py
```

输出目录：

```text
results/v22_chinese_literature_product_peers_20260601
results/v22_chinese_literature_peer_main_effect_20260601
```

## 网络覆盖

| peer_source | network_rows | event_peer_rows | events | focal_firms | peer_firms | mean_similarity | median_similarity | same_industry_d_rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ren_wang_binary_global | 100760 | 395060 | 19753 | 2610 | 5008 | 0.358 | 0.343 | 0.444 |
| ren_wang_binary_same_industry_d | 98437 | 389424 | 19739 | 2609 | 5061 | 0.324 | 0.324 | 1.000 |
| liu_product_tfidf_global | 100760 | 395060 | 19753 | 2610 | 5345 | 0.371 | 0.363 | 0.536 |
| liu_product_tfidf_same_industry_d | 98437 | 389424 | 19739 | 2609 | 5148 | 0.334 | 0.334 | 1.000 |

## 主效应结果

样本口径保持与当前主表一致：

- first focal GenAI event
- announcement-cleaned
- Top5 / Top10 peers
- `PeerCAR[0,+1]`
- event FE + peer industry-week FE
- pre-window peer CAR controls
- two-way clustered by event and peer firm

关键系数是：

```text
Specificity_z × AIActivePeer
```

### Top5, 强 FE

| peer_source | AIActive | coef | p | N | events |
|---|---|---:|---:|---:|---:|
| ren_wang_binary_global | ext_any | 0.000895 | 0.281 | 8162 | 2294 |
| ren_wang_binary_global | current_text_history | -0.001383 | 0.113 | 8162 | 2294 |
| ren_wang_binary_same_industry_d | ext_any | 0.001413 | 0.035 | 8329 | 2284 |
| ren_wang_binary_same_industry_d | current_text_history | 0.000472 | 0.502 | 8329 | 2284 |
| liu_product_tfidf_global | ext_any | -0.000826 | 0.354 | 8253 | 2287 |
| liu_product_tfidf_global | current_text_history | -0.000947 | 0.299 | 8253 | 2287 |
| liu_product_tfidf_same_industry_d | ext_any | -0.000797 | 0.273 | 8402 | 2286 |
| liu_product_tfidf_same_industry_d | current_text_history | -0.001585 | 0.039 | 8402 | 2286 |

### Top10, 强 FE

| peer_source | AIActive | coef | p | N | events |
|---|---|---:|---:|---:|---:|
| ren_wang_binary_global | ext_any | -0.000103 | 0.842 | 16373 | 2309 |
| ren_wang_binary_global | current_text_history | -0.001084 | 0.055 | 16373 | 2309 |
| ren_wang_binary_same_industry_d | ext_any | -0.000245 | 0.608 | 16477 | 2305 |
| ren_wang_binary_same_industry_d | current_text_history | -0.000417 | 0.383 | 16477 | 2305 |
| liu_product_tfidf_global | ext_any | -0.000663 | 0.221 | 16507 | 2308 |
| liu_product_tfidf_global | current_text_history | -0.000753 | 0.172 | 16507 | 2308 |
| liu_product_tfidf_same_industry_d | ext_any | -0.000335 | 0.495 | 16463 | 2300 |
| liu_product_tfidf_same_industry_d | current_text_history | -0.000485 | 0.314 | 16463 | 2300 |

## 判断

这轮结果不支持把“严格中文年报文本产品相似度 peer”作为主 peer 口径。

原因：

1. 最干净的外部 AIActive `ext_any` 在四套 Top5 口径里没有稳定负向结果。
2. `ren_wang_binary_same_industry_d × ext_any` 反而显著为正，方向与竞争风险重估相反。
3. `liu_product_tfidf_same_industry_d × current_text_history` Top5 显著为负，但依赖 text-history AIActive，且 Top10 消失，不能单独支撑主线。
4. 这说明任宏达、王琨 / 刘昌阳等式年报文本 peer 更适合作为“文献支撑与稳健性失败证据”，而不是当前主效应的 headline peer。

## 对当前论文设计的含义

当前显著结果更准确的定位应是：

> 在 LLM-screened direct product-market peer 中，更具体的 GenAI 披露与 AI-active close peers 的负向短窗重估相关。

但不能写成：

> 按中国成熟年报文本产品市场竞争文献构造的 peer 网络均支持主效应。

下一步如果继续推进，应在主文中诚实区分：

1. **文献基础 peer**：Hoberg-Phillips / 任宏达-王琨 / 刘昌阳等中文年报文本 similarity。
2. **当前有效 peer**：LLM 从文献基础候选集中筛出的 direct product-market competitors。
3. **验证责任**：证明 LLM-screened peers 比传统年报相似 peer 更能识别“直接竞争关系”，而不是替代已有文献口径。

