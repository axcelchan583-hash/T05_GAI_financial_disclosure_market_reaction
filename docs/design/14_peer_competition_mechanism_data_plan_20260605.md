# T05 peer competition mechanism and data plan

日期：2026-06-05

用途：把当前 T05 从“跑出一个负的 peer CAR”推进到“可以解释为竞争性重估”的执行版设计。本文档接在 v29-v31 结果之后使用，旧的 2026-06-01 组会版文档保留为历史口径。

## 1. 当前口径

当前主效应不再写成单纯的 `Specificity x AIActivePeer`。更合适的口径是：

```text
焦点公司 GenAI 披露事件发生后，
其产品市场同行在短窗口内出现负向异常收益。
```

已有结果：

| 证据 | 当前结果 | 文件 |
|---|---:|---|
| peer event-study sample | 2,790 event-peer rows; 316 events; 1,385 peer firms | `docs/empirical_runs/93_v29_pom_style_peer_results_20260605.md` |
| PeerAR[0] | -0.0025, clustered z = -2.3169 | `results/v29_pom_style_peer_results_20260605/` |
| PeerAR[+1] | -0.0021, clustered z = -1.9257 | `results/v29_pom_style_peer_results_20260605/` |
| `Spec x AIActivePeer` on PeerAR[0] | -0.0018, p = 0.0224 after POM-analog controls | `docs/empirical_runs/95_v31_pom_analog_cross_section_20260605.md` |
| `Spec x AIActivePeer` on PeerCAR[0,+1] | -0.0032, p = 0.0080 after POM-analog controls | `docs/empirical_runs/95_v31_pom_analog_cross_section_20260605.md` |

因此，主线应写为：

```text
GenAI initiative disclosure -> product-market peer negative revaluation.
Specificity and AI-active peer status explain where this negative revaluation is stronger.
```

本文不应直接声称已经证明真实业务挤出、长期市场份额转移或强因果。当前证据支持的是资本市场短窗口重估。

## 2. 需要排除的替代解释

一个负的 peer CAR 至少有四种解释。后续机制部分的任务是把竞争性重估从这些解释中区分出来。

| 解释 | 可观察含义 | 需要的证据 |
|---|---|---|
| 竞争性租金再分配 | 焦点公司信号越强，直接竞争对手越跌；焦点公司自身越涨，同行越跌 | 焦点-同行镜像；产品相似度梯度；Specificity 机制 |
| 行业共同坏消息 | 焦点公司和同行应同向下跌，或整个行业同步反应 | 焦点 CAR 与 peer CAR 负相关；event FE / 行业时间控制；非近邻 placebo |
| 注意力或流动性轮动 | 短期抛压会反转，可能伴随异常换手 | 长窗口 CAR 不反转；控制异常换手率、成交量、流动性 |
| 同行自身事件污染 | 负反应来自同行自己窗口内的公告或 GenAI 新闻 | 清理 peer 自身 GenAI / 业绩 / 并购 / 重大公告窗口 |

优先级最高的是 peer 自身事件污染和焦点-同行镜像。前者是防守底线；后者是竞争性再分配最直接的符号检验。

## 3. 机制支柱

### 3.1 竞争暴露度

如果市场在评估竞争冲击，效应应随焦点公司与同行之间的竞争暴露度递增。

可执行检验：

| 检验 | 变量 | 预期 |
|---|---|---|
| 产品相似度梯度 | `PeerSimilarity` / `PeerRank` 分组 | Top ranks 或高相似度 peer 更负 |
| 行业集中度 | peer 所处行业 revenue HHI | 集中行业内竞争冲击更强 |
| AI-active 同行 | `AIActivePeer` | 若是竞争而非技术传染，AI-active peer 可以更负 |
| 防守控制 | `Spec x Size`, `Spec x Beta`, `Spec x Volatility` | 排除 AIActive 只是高 beta / 高成长 firm type 的代理 |

注意：`AIActivePeer` 不应单独写成“同行有 AI 所以被打击”。更准确的解释是，处于相近技术空间的同行更容易被投资者拿来横向比较；若符号为负，它支持竞争风险而不是正向技术传染。

### 3.2 信号可信度

`Specificity` 是本文自己的理论脊柱。具体、可核验、有行动细节的披露比泛泛 AI 表态更可能被市场当作可信竞争信号。

可执行检验：

| 检验 | 变量 | 预期 |
|---|---|---|
| 具体性主机制 | `Spec x AIActivePeer` | 更具体披露下，AI-active peer 更负 |
| POM-analog controls | prior AI patent, sales growth, product distance, industry HHI | `Spec x AIActivePeer` 不被这些可观察特征吸收 |
| 测度防守 | 文本长度、AI 词频、source、Qian recall score | 说明 Specificity 不是普通 verbosity 或关键词密度 |

当前 v31 已经给出初步证据：加入 POM-analog controls 后，`Spec x AIActivePeer` 在 PeerAR[0] 和 PeerCAR[0,+1] 上仍为负且显著。

### 3.3 现金流与基本面通道

短窗 CAR 需要一个长期落点，否则容易被解释成注意力或交易压力。现金流通道不要求我们证明真实业务已经被抢走，但至少应证明市场反应与后续盈利预期或基本面方向一致。

优先检验：

| 检验 | 变量 | 预期 |
|---|---|---|
| 焦点-同行镜像 | focal CAR vs peer CAR | 焦点 CAR 越正，peer CAR 越负 |
| 持久性 / 无反转 | peer CAR[0,+5], [0,+20], [0,+60] | 不应快速反转为正 |
| 分析师预测修正 | event 后 EPS / profit forecast revision | 负向 peer CAR 对应 peer 预测下修 |
| 未来基本面 | peer sales growth, gross margin, market share | 高冲击 peer 后续经营指标更弱 |
| 财务脆弱性 | leverage, pledge, MB, intangibles, age | 更难跟进投资或 growth options 更脆弱的 peer 更负 |

分析师预测修正的边际收益最高，因为它比未来销售增长更接近资本市场对现金流预期的即时更新，也比长期经营结果更少受后续冲击污染。

## 4. 数据需求清单

### 4.1 可以先用现有数据构造

| 数据 | 用途 | 当前状态 |
|---|---|---|
| focal AR / CAR | 焦点-同行镜像；控制焦点公司自身好消息强度 | 可由 `results/v6_supplement_market_model_placebo_20260524/stock_returns_with_market_model_params.csv` 计算 |
| peer long-window CAR | 持久性 / 反转检验 | 可由同一 market-model returns 文件计算 |
| peer similarity / rank | 产品市场竞争暴露度 | v29/v31 样本已有 |
| `Spec` | 披露可信度机制 | v29/v31 样本已有 |
| `AIActivePeer` | 技术空间暴露 | `results/v6_external_ai_active_20260524/external_ai_evidence_first_dates_by_firm.csv` |
| sales growth / gross margin | 初步基本面控制 | `results/v13_peer_validity_gate_20260531/financials_fs_comins_annual_metrics.csv.gz` |
| market cap / size | 防守控制 | `results/v8_measurement_final_checks_20260527/matched_market_caps.csv` |

这些足够先启动 v32-v33，不需要等所有财务和分析师数据补齐。

### 4.2 需要优先补充或重新合并

| 数据 | 来源方向 | 用途 | 优先级 |
|---|---|---|---|
| peer 自身 GenAI 事件 | 当前 v36 GenAI event library / 巨潮事件库 | 清理同行自己窗口内 GenAI 污染 | 最高 |
| peer 重大公告窗口 | 巨潮公告 / CSMAR 公告 flags | 清理业绩、并购、融资、诉讼、停复牌等污染 | 最高 |
| 异常换手率 / 成交量 | CSMAR 日行情或现有 returns 文件字段核验 | 排除注意力和流动性轮动 | 高 |
| beta / volatility | 日收益估计窗口 | `Spec x Beta` / `Spec x Volatility` 防守 | 高 |
| 分析师预测修正 | CSMAR 分析师预测数据 | 现金流预期通道 | 高 |
| leverage / MB / intangibles / age / R&D | CSMAR 财务报表和公司基本信息 | 财务脆弱性与 growth options 机制 | 中 |
| 控股股东质押 | CSMAR 质押数据 | 中国情境下财务压力异质性 | 中 |
| 未来市场份额 | 行业收入聚合 | 真实竞争结果补充 | 中低 |

### 4.3 暂不作为主机制的数据

| 数据 | 原因 |
|---|---|
| `product_oriented` rule-coded category | v31 中均值约 0.896，过于不均衡；人工核验前不能作为核心机制 |
| peer follow-up GenAI disclosure | 更像战略回应或同业跟随，不足以证明现金流再分配 |
| 供应链方向结果 | 适合单独边界或 Qian 复刻，不适合作为当前产品市场 peer 主机制 |

## 5. 执行顺序

### v32: identification defense package

目标：先判断主效应是否能避开最基本的替代解释。

输出：

1. focal AR/CAR 与 peer AR/CAR 的镜像关系；
2. peer CAR[0,+5], [0,+20], [0,+60]；
3. 清理 peer 自身 GenAI / 重大公告污染前后的 Table 2；
4. 异常换手率或成交量控制，若日行情字段可用。

通过标准：

```text
peer 短窗负反应在污染清理后不消失；
焦点 CAR 与 peer CAR 呈负相关或至少不是同向坏消息；
长窗口不出现快速正向反转。
```

### v33: competition-exposure mechanism

目标：证明负反应集中在真正暴露于竞争压力的同行。

输出：

1. PeerSimilarity / PeerRank 分组事件研究；
2. `Spec x AIActivePeer` 加 `Spec x Size/Beta/Volatility`；
3. 行业 HHI 异质性；
4. low-similarity / random / weaker-peer placebo 的当前 v36 样本重跑。

通过标准：

```text
近产品市场 peer 更负；
AI-active peer 的负反应不能被 size、beta、volatility 解释；
弱竞争关系或随机同行中效应明显减弱。
```

### v34: cash-flow bridge

目标：把短窗价格反应连接到现金流预期或后续基本面。

输出：

1. 分析师 EPS / profit forecast revision；
2. forecast dispersion 或 analyst coverage 作为补充；
3. peer 后续 sales growth / gross margin；
4. peer leverage / pledge / MB / intangibles / age 异质性。

通过标准：

```text
负向 peer CAR 能预测分析师下修或未来基本面走弱；
财务脆弱或 growth-options 高的 peer 反应更负。
```

## 6. 当前论文写法

最安全的理论表述：

```text
生成式 AI initiative 披露向资本市场释放焦点公司在相关产品市场中
可能形成新竞争优势的信号。该信号并不必然冲击所有同行；
只有当同行与焦点公司产品市场距离更近、且自身处于可比较的 AI 技术空间时，
投资者才更可能把焦点公司的披露理解为竞争性威胁。
```

机制不是要证明每个同行都被真实挤出，而是证明市场反应具备三个特征：

1. 竞争暴露越强，反应越负；
2. 披露信号越可信，反应越负；
3. 反应不只是短期交易压力，而是与焦点-同行相对重估和未来现金流预期相连。

## 7. 当前边界

1. v29 的 Table 2 是主效应表，v31 的 `Spec x AIActivePeer` 是机制/异质性表。
2. event FE 下，`Spec` 作为 event-level 变量被吸收；机制识别来自同一事件内不同 peer 的横截面差异。
3. 当前 product-market peer 定义必须继续防守，不能写成无争议金标准。
4. 在人工核验前，不把 `product_oriented` 类别写成核心机制。
5. 如果 v32 的污染清理或长窗口检验失败，应把论文降级为短期市场注意力/重估现象，而不是继续写竞争性租金再分配。
