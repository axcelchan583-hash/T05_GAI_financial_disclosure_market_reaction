# v6 公告清洗版 100 次随机同业 placebo（2026-05-24）

## 这轮做了什么

本轮处理一个更直接的质疑：

```text
真实 Top5 产品市场近邻的负反应，
会不会只是同一行业里随机公司也会出现的 AI 热点共同波动？
```

做法：

```text
1. 保留每家公司首次 GenAI 披露事件。
2. 对每个 focal event，在同一 CSRC 细行业中随机抽取 5 家非真实 Top10 产品近邻公司。
3. 重复 100 次随机抽样。
4. 每次都重新匹配日收益、market-model abnormal return、AIActivePeer。
5. 每次都套用最新公告清洗：剔除焦点公司或随机 peer 在事件窗内有重大/定期/业绩/风险类公告的观测。
6. 回归设定与主表一致：event FE；补充 event FE + peer industry-week FE；标准误 event × peer firm 双向聚类。
```

脚本：

```text
scripts/run_v6_announcement_clean_random_placebo_20260524.py
```

结果目录：

```text
results/v6_announcement_clean_random_placebo_20260524
```

输出：

```text
v6_announcement_clean_true_top5_reference.csv
v6_announcement_clean_repeated_random_placebo_draws.csv
v6_announcement_clean_repeated_random_placebo_summary.csv
v6_announcement_clean_random_placebo_sample_by_draw.csv
```

## 随机 placebo 样本规模

100 次随机抽样后的样本规模约为：

| 指标 | mean | min | max |
|---|---:|---:|---:|
| obs | 7,723 | 7,585 | 7,807 |
| events | 2,373 | 2,361 | 2,385 |
| peer firms | 3,679 | 3,616 | 3,728 |
| mean AIActivePeer | 0.274 | 0.263 | 0.284 |

真实 Top5 公告清洗样本为：

```text
obs = 8,683
events = 2,416
peer firms = 3,573
mean AIActivePeer = 0.256
```

## 真实 Top5 参照结果

真实 Top5、同时剔除焦点与竞品清洗公告：

| Y | FE | coef | p | N | events |
|---|---|---:|---:|---:|---:|
| CAR[0,+1] | event FE | -0.002298 | 0.008 | 8,683 | 2,416 |
| CAR[0,+1] | event FE + peer industry-week FE | -0.002298 | 0.020 | 8,683 | 2,416 |
| CAR[-1,+1] | event FE | -0.002073 | 0.037 | 8,683 | 2,416 |
| CAR[-1,+1] | event FE + peer industry-week FE | -0.001469 | 0.194 | 8,683 | 2,416 |

## 100 次随机同业 placebo 分布

| Y | FE | random mean | p05 | p50 | p95 | true Top5 coef | share random <= true |
|---|---|---:|---:|---:|---:|---:|---:|
| CAR[0,+1] | event FE | -0.000050 | -0.001483 | -0.000055 | 0.001506 | -0.002298 | 0.00 |
| CAR[0,+1] | event FE + peer industry-week FE | -0.000050 | -0.001483 | -0.000055 | 0.001506 | -0.002298 | 0.00 |
| CAR[-1,+1] | event FE | -0.000058 | -0.001548 | -0.000036 | 0.001618 | -0.002073 | 0.02 |
| CAR[-1,+1] | event FE + peer industry-week FE | -0.000058 | -0.001548 | -0.000036 | 0.001618 | -0.001469 | 0.08 |

随机样本中出现“负向且 p<0.05”的比例：

| Y | FE | share random negative p<0.05 |
|---|---|---:|
| CAR[0,+1] | event FE | 0.03 |
| CAR[0,+1] | event FE + peer industry-week FE | 0.03 |
| CAR[-1,+1] | event FE | 0.01 |
| CAR[-1,+1] | event FE + peer industry-week FE | 0.01 |

说明：

```text
随机同业 placebo 是同一细行业内抽样，因此 event FE + peer industry-week FE 与 event FE 的随机分布几乎一致。
这个检验的重点不是新增固定效应，而是确认“同一行业随机公司”不能复制真实 Top5 的负反应。
```

## 当前判断

这轮是对主结果很有用的加强：

```text
在 CAR[0,+1] 主窗口下，100 次随机同业抽样没有一次比真实 Top5 更负。
随机同业分布中心接近 0，真实 Top5 约为 -0.00230。
```

因此当前最稳的主结果组合是：

```text
1. 真实 Top5 产品市场近邻：负向显著。
2. 低相似度同行 placebo：不显著且接近 0。
3. 100 次随机同业 placebo：没有复制真实 Top5 的负向强度。
4. AI 词剔除版产品相似度：仍保留负向显著。
5. 公告污染清洗：没有打掉主效应。
```

剩下最大的识别短板：

```text
AIActivePeer 仍需要更外部、更严格的 pre-event 版本。
下一步应优先合并 CAC 备案、AI/GenAI 专利、AI 招聘、历史 GenAI 披露。
```
