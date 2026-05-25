# v6 公告清洗与交易活跃度补充检验（2026-05-24）

## 这轮做了什么

本轮把 2026-05-24 下载的 CSMAR 公告三表整理成可复用中间表，并接入 v6 主效应面板。

原始公告数据目录：

```text
/Users/mac/computerscience/第三方资料/04_项目专用资料/T05_GAI_financial_disclosure_market_reaction/csmar_downloads_20260524
```

生成结果目录：

```text
results/v6_announcement_clean_checks_20260524
results/v6_trading_response_checks_20260524
```

脚本：

```text
scripts/run_v6_announcement_clean_checks_20260524.py
scripts/run_v6_trading_response_checks_20260524.py
```

## 公告数据合并结果

合并逻辑：

```text
公告分类关联表 -> AnnouncementID 层面的公告类型标记
公告证券关联表 -> A 股 stock_code × DeclareDate 层面的公告标记
```

用于清洗的公告类型包括：

```text
定期报告 / 业绩预告或快报 / 重大交易或治理事项 / 股价异动与风险提示
```

合并后中间表：

```text
results/v6_announcement_clean_checks_20260524/announcement_stock_day_flags_2023_2026.csv.gz
```

规模：

```text
公告分类行数：12,277,698
公告证券关联行数：9,606,736
A 股证券关联行数：2,415,820
股票-日期公告标记行数：695,403
覆盖日期：2023-01-01 至 2026-05-25
覆盖股票代码：5,902
```

## 主效应：CAR 结果

主样本仍为：

```text
每家公司首次 GenAI 披露 × Top5 产品市场近邻竞品
Y = market-model PeerCAR[0,+1] 或 PeerCAR[-1,+1]
X = Specificity_z × AIActivePeer
固定效应 = event FE；补充 event FE + peer industry-week FE
标准误 = event × peer firm 双向聚类
```

关键结果：

| 样本 | Y | FE | coef | p | N | events |
|---|---:|---|---:|---:|---:|---:|
| baseline Top5 | CAR[0,+1] | event FE | -0.001825 | 0.0166 | 11,288 | 2,646 |
| baseline Top5 | CAR[-1,+1] | event FE | -0.001921 | 0.0496 | 11,288 | 2,646 |
| baseline Top5 | CAR[0,+1] | event FE + peer industry-week FE | -0.001512 | 0.0842 | 11,288 | 2,646 |
| 剔除竞品清洗公告 | CAR[0,+1] | event FE | -0.001944 | 0.0212 | 9,355 | 2,629 |
| 剔除焦点公司清洗公告 | CAR[0,+1] | event FE + peer industry-week FE | -0.002122 | 0.0188 | 10,376 | 2,428 |
| 同时剔除焦点与竞品清洗公告 | CAR[0,+1] | event FE + peer industry-week FE | -0.002298 | 0.0201 | 8,683 | 2,416 |
| 同时剔除焦点与竞品清洗公告 | CAR[-1,+1] | event FE | -0.002073 | 0.0369 | 8,683 | 2,416 |

读法：

```text
公告污染清洗没有打掉主效应。
最稳的是 CAR[0,+1]：剔除焦点与竞品的重大/定期/业绩/风险类公告后，
Top5 AI-active 近邻竞品仍出现更负的 market-model CAR。
```

## 低相似度同行 placebo

低相似度同行同样做公告清洗后，`Specificity_z × AIActivePeer` 基本为零：

| 样本 | Y | FE | coef | p | N | events |
|---|---:|---|---:|---:|---:|---:|
| baseline low-similarity | CAR[0,+1] | event FE | 0.000109 | 0.8285 | 19,198 | 2,598 |
| baseline low-similarity | CAR[-1,+1] | event FE | 0.000208 | 0.7498 | 19,198 | 2,598 |
| 同时剔除清洗公告 | CAR[0,+1] | event FE | 0.000061 | 0.9171 | 14,753 | 2,382 |
| 同时剔除清洗公告 | CAR[-1,+1] | event FE | 0.000085 | 0.9088 | 14,753 | 2,382 |

这支持“产品市场近邻”而不是普通同业 AI 热度。

## Top5 vs 低相似度同行差异检验

把 true Top5 和低相似度同行放入同一个 event-FE 回归，检验：

```text
Specificity_z × AIActivePeer × TrueTop5
```

关键结果：

| 样本 | Y | FE | coef | p | N | events |
|---|---:|---|---:|---:|---:|---:|
| baseline | CAR[0,+1] | event FE | -0.001484 | 0.0306 | 30,486 | 2,651 |
| baseline | CAR[-1,+1] | event FE | -0.001960 | 0.0264 | 30,486 | 2,651 |
| 剔除竞品清洗公告 | CAR[0,+1] | event FE | -0.001439 | 0.0462 | 25,318 | 2,651 |
| 剔除焦点公司清洗公告 | CAR[0,+1] | event FE | -0.001661 | 0.0171 | 27,961 | 2,433 |
| 同时剔除清洗公告 | CAR[0,+1] | event FE | -0.001718 | 0.0185 | 23,436 | 2,433 |
| 同时剔除清洗公告 | CAR[-1,+1] | event FE | -0.002503 | 0.0093 | 23,436 | 2,433 |

但加入 `peer industry-week FE` 后，差异项不再显著。这个结果应作为保守边界写入：

```text
true Top5 的单独回归稳健，低相似度 placebo 为零；
Top5 vs 低相似度的差异在 event FE 下显著，
但在更强的 peer industry-week FE 下变弱。
```

## 交易活跃度补充 Y

用个股日交易数据构造：

```text
abnormal log trading value
abnormal log trading shares
baseline = 事件前滚动 60 个交易日均值，跳过最近 11 个交易日
```

结果方向不是“交易更热”，而是 Top5 AI-active 近邻在具体 GenAI 披露后交易活跃度相对下降：

| 样本 | Y | FE | coef | p | N | events |
|---|---:|---|---:|---:|---:|---:|
| Top5 baseline | abnormal log trading value [0,+1] | event FE | -0.0368 | 0.0113 | 11,522 | 2,647 |
| Top5 baseline | abnormal log trading shares [0,+1] | event FE | -0.0302 | 0.0199 | 11,522 | 2,647 |
| Top5 baseline | abnormal log trading value [0,+1] | event FE + peer industry-week FE | -0.0325 | 0.0403 | 11,522 | 2,647 |
| Top5 同时剔除清洗公告 | abnormal log trading value [0,+1] | event FE + peer industry-week FE | -0.0397 | 0.0275 | 8,856 | 2,420 |
| Top10 同时剔除清洗公告 | abnormal log trading value [0,+1] | event FE + peer industry-week FE | -0.0333 | 0.0066 | 17,659 | 2,432 |

低相似度同行基本不显著；但单次随机同业 placebo 在清洗样本中出现正向异常成交额，所以交易活跃度只能作为辅助事实，不能作为主 Y。

## 当前判断

这轮结果比上一轮更稳：

```text
1. 主结果不依赖同日/短窗重大公告污染。
2. CAR[0,+1] 比 CAR[-1,+1] 更稳定，适合作为主窗口。
3. 低相似度同行 placebo 基本为零。
4. Top5 vs low-similarity 差异在 event FE 下显著，但强 FE 后变弱。
5. 交易活跃度方向与 CAR 一致偏负，但更适合做补充表。
```

暂定写法：

```text
焦点公司首次 GenAI 披露越具体，
事前已经 AI-active 的 Top5 产品市场近邻竞品，
在 [0,+1] 窗口出现更负的 market-model CAR；
该结果在剔除焦点公司与竞品的重大/定期/业绩/风险类公告后仍成立，
且低相似度同行没有类似反应。
```

下一步最值得做：

```text
1. 用更干净的 AIActivePeer：加入 CAC 备案、AI 专利、AI 招聘等外部事前证据。
2. 对 ProductSimilarity 做 AI 词剔除版，避免“两个 AI 公司天然相似”的质疑。
3. 把随机同业 placebo 扩展成 100 次公告清洗版，而不是单次随机。
```
