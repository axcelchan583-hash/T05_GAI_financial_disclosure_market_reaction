# v12 Annual-Report Product-Peer Main-Effect Check

日期：2026-05-30

## 目的

本轮检验把主回归中的产品市场 peer 网络从旧的 CSMAR `MAINBUSSINESS + BusinessScope`
口径替换为更接近 Hoberg and Phillips (2016, JPE) 的年报业务文本相似度口径：

```text
年度报告业务/经营章节文本
-> Chinese char 2-3 gram TF-IDF cosine similarity
-> event-specific Top5 / Top10 product-market peers
-> PeerCAR[0,+1] main regression
```

除 peer 网络外，其余口径尽量沿用当前 v6/v8 主线：

- X：`specificity_z`
- Y：`peer_car_0_p1_mm`
- 核心项：`specificity_z × AIActivePeer`
- AIActivePeer：`ext_any` 与 `current_text_history`
- 样本：first focal GenAI event，剔除焦点公司或 peer 在事件窗内有定期/业绩/重大/异常波动公告的样本
- 控制：`peer_car_pre10_m2_mm`、`peer_car_pre20_m2_mm`
- FE：event FE；event FE + peer industry-week FE
- 聚类：two-way by event and peer firm

运行脚本：

```text
scripts/run_v12_annual_report_peer_main_effect_20260530.py
```

输出目录：

```text
results/v12_annual_report_peer_main_effect_20260530
```

## 样本量

| peer network | TopN | obs | events | peer firms | mean PeerCAR[0,+1] | mean ext_any | mean text-history |
|---|---:|---:|---:|---:|---:|---:|---:|
| annual same IndustryNameD | 5 | 8,353 | 2,283 | 3,103 | 0.000209 | 0.2285 | 0.3070 |
| annual same IndustryNameD | 10 | 16,475 | 2,305 | 3,860 | -0.000118 | 0.2331 | 0.3096 |
| annual global | 5 | 8,232 | 2,292 | 2,822 | 0.000512 | 0.2389 | 0.3067 |
| annual global | 10 | 16,407 | 2,307 | 3,558 | 0.000120 | 0.2384 | 0.3051 |
| annual global AI-word-stripped | 5 | 8,232 | 2,291 | 2,811 | 0.000580 | 0.2386 | 0.3058 |
| annual global AI-word-stripped | 10 | 16,376 | 2,307 | 3,546 | -0.000003 | 0.2380 | 0.3053 |

## Top5 强 FE 主结果

规格：`PeerCAR[0,+1] ~ AIActivePeer + specificity_z × AIActivePeer + pre-window CAR controls + event FE + peer industry-week FE`。

| peer network | AIActivePeer | coef on specificity × AIActive | se | p |
|---|---|---:|---:|---:|
| annual same IndustryNameD Top5 | ext_any | 0.001020 | 0.000699 | 0.144 |
| annual same IndustryNameD Top5 | current_text_history | 0.000392 | 0.000690 | 0.570 |
| annual global Top5 | ext_any | -0.000132 | 0.000834 | 0.875 |
| annual global Top5 | current_text_history | -0.001227 | 0.000890 | 0.168 |
| annual global AI-word-stripped Top5 | ext_any | -0.000490 | 0.000822 | 0.551 |
| annual global AI-word-stripped Top5 | current_text_history | -0.001366 | 0.000888 | 0.124 |

结论：**年报文本 Top5 网络没有复制旧 CSMAR 业务范围 Top5 的负向主效应**。同细分行业年报 Top5 甚至为正向不显著；global / AI-word-stripped global Top5 为负但远不显著。

## Rank-gradient 补充

强 FE + pre-window controls 下，按年报 peer rank 分组：

| peer network | rank band | AIActivePeer | coef | p |
|---|---|---|---:|---:|
| annual same IndustryNameD | Top1-3 | ext_any | 0.000804 | 0.496 |
| annual same IndustryNameD | Top1-3 | current_text_history | 0.000119 | 0.910 |
| annual same IndustryNameD | Top4-5 | ext_any | 0.001709 | 0.242 |
| annual same IndustryNameD | Top4-5 | current_text_history | 0.002267 | 0.167 |
| annual global | Top1-3 | ext_any | 0.000529 | 0.676 |
| annual global | Top1-3 | current_text_history | 0.000109 | 0.933 |
| annual global | Top4-5 | ext_any | -0.000884 | 0.707 |
| annual global | Top4-5 | current_text_history | -0.002103 | 0.358 |
| annual global AI-word-stripped | Top1-3 | ext_any | 0.000815 | 0.533 |
| annual global AI-word-stripped | Top1-3 | current_text_history | -0.000616 | 0.633 |
| annual global AI-word-stripped | Top4-5 | ext_any | 0.000547 | 0.793 |
| annual global AI-word-stripped | Top4-5 | current_text_history | -0.001342 | 0.539 |

Top10 下 `current_text_history` 在 annual global 与 AI-word-stripped global 中有负向显著：

| peer network | rank band | AIActivePeer | coef | p |
|---|---|---|---:|---:|
| annual global | Top1-10 | current_text_history | -0.001086 | 0.034 |
| annual global AI-word-stripped | Top1-10 | current_text_history | -0.001193 | 0.018 |

但这个结果不适合作为主结果，因为：

- `ext_any` 不支持；
- Top1-3 不支持；
- 同细分行业年报 peer 不支持；
- 它更像 text-history 口径下的大范围 AI attention / same-theme exposure，而不是近产品市场竞争重估。

## 判断

本轮结果对当前论文主线是一个 **负面稳健性检验**：

1. 年报文本 peer 网络更接近 Hoberg-Phillips 的原始数据来源；
2. 但用它替代旧 CSMAR 业务范围 Top5 后，主效应不成立；
3. 因此不能把“annual-report business text + same IndustryNameD Top5”直接改成正式主 peer 定义；
4. 如果继续当前 peer-CAR 论文，应当在方法上更清楚地区分：
   - 旧 CSMAR 经营范围/主营业务口径：主结果来源，可能更贴近简短业务边界；
   - 年报业务章节口径：Hoberg-Phillips-style robustness，但结果不支持；
   - AI-word-stripped 旧口径：仍是目前最强的反驳“AI 词机械匹配”的证据。

更保守的写法是：

```text
We construct product-market peers using CSMAR business-scope text and validate
the network against alternative annual-report-based Hoberg-Phillips-style peer
definitions. The annual-report alternatives do not reproduce the headline
effect, suggesting that the documented peer revaluation is concentrated in the
business-scope neighborhood rather than in broader annual-report textual
similarity.
```

这会降低方法说服力，但比强行替换主 peer 口径安全。

## 输出文件

```text
results/v12_annual_report_peer_main_effect_20260530/annual_report_peer_main_effect_sample_summary.csv
results/v12_annual_report_peer_main_effect_20260530/annual_report_peer_main_effect_regressions.csv
results/v12_annual_report_peer_main_effect_20260530/annual_report_peer_rank_gradient_regressions.csv
results/v12_annual_report_peer_main_effect_20260530/analysis_sample_annual_same_industry_d_top5.csv.gz
results/v12_annual_report_peer_main_effect_20260530/analysis_sample_annual_same_industry_d_top10.csv.gz
results/v12_annual_report_peer_main_effect_20260530/analysis_sample_annual_global_top5.csv.gz
results/v12_annual_report_peer_main_effect_20260530/analysis_sample_annual_global_top10.csv.gz
results/v12_annual_report_peer_main_effect_20260530/analysis_sample_annual_global_ai_stripped_top5.csv.gz
results/v12_annual_report_peer_main_effect_20260530/analysis_sample_annual_global_ai_stripped_top10.csv.gz
```
