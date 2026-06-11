# T05 current robustness and mechanism status

日期：2026-06-05

用途：汇总 v31-v37 后当前可以写进论文的稳健性、机制证据和不能过度表述的边界。本文档接在 `docs/design/14_peer_competition_mechanism_data_plan_20260605.md` 之后使用。

## 1. 当前结论

当前最稳的主线是：

```text
焦点公司具体 GenAI initiative 披露后，产品市场同行出现负向短窗口重估；
该负向重估在“披露更具体 × 同行具备既有 AI 活动证据”的位置更强。
```

这条主线已经通过了最关键的防守检验：`Spec x AIActivePeer` 在加入 `Spec x Size`、`Spec x Beta`、`Spec x Volatility`、`Spec x MB` 后仍为负且显著。也就是说，当前证据不支持“AIActivePeer 只是高 beta、高估值、高波动或高成长 firm type 的代理”这个反驳。

但表述必须克制：

```text
主样本支持竞争性重估机制；
严格污染清洗样本中方向和量级一致，但统计功效下降；
分析师预测结果支持现金流预期方向一致，但覆盖率低，不能写成严格现金流渠道证明。
```

## 2. 可作为正文主证据

### 2.1 主效应：peer 短窗口负异常收益

| 证据 | 结果 | 解释 | 文件 |
|---|---:|---|---|
| `PeerAR[0]` | -0.0025, p = 0.0207 | 事件日同行负反应 | `docs/empirical_runs/97_v33_supplement_data_probe_20260605.md` |
| `PeerAR[+1]` | -0.0021, p = 0.0538 | 次日仍为负，边际显著 | `docs/empirical_runs/97_v33_supplement_data_probe_20260605.md` |
| `PeerCAR[0,+1]` | -0.0047, p = 0.0045 | 当前建议的主 Y | `docs/empirical_runs/97_v33_supplement_data_probe_20260605.md` |

建议写法：

```text
由于中国披露时间和盘中/盘后信息不完全可辨，主结果以后续表格中的 CAR[0,+1] 为主，AR[0] 作为辅助。
```

### 2.2 核心机制：`Spec x AIActivePeer`

| 口径 | `Spec x AIActivePeer` | N | events | 解释 | 文件 |
|---|---:|---:|---:|---|---|
| v31 POM-analog controls, event FE, `PeerAR[0]` | -0.0018, p = 0.0224 | 2,719 | 316 | 事件日机制成立 | `docs/empirical_runs/95_v31_pom_analog_cross_section_20260605.md` |
| v31 POM-analog controls, event FE, `PeerCAR[0,+1]` | -0.0032, p = 0.0080 | 2,719 | 316 | 当前机制主列 | `docs/empirical_runs/95_v31_pom_analog_cross_section_20260605.md` |
| v36 + firm-style main effects | -0.0026, p = 0.0292 | 2,404 | 281 | 加 Size/Beta/Volatility/MB 主效应后仍成立 | `docs/empirical_runs/100_v36_spec_ai_firm_char_guard_20260605.md` |
| v36 + `Spec x firm-char` 全套交互 | -0.0025, p = 0.0334 | 2,404 | 281 | 挡住 firm-type 代理质疑 | `docs/empirical_runs/100_v36_spec_ai_firm_char_guard_20260605.md` |

建议写法：

```text
结果表明，披露具体性带来的同行负向重估并非均匀发生在所有同行身上，
而是集中在事件前已经具有可观察 AI 活动证据的同行中。
在控制披露具体性与同行规模、beta、波动率和估值特征的交互后，
该交互项仍保持负向且显著，说明 AIActivePeer 不只是一般风格因子的替代变量。
```

不要写成：

```text
本文完全证明了真实竞争挤出。
```

当前证据证明的是资本市场对竞争风险的差异化重估，不是实际市场份额已经转移。

### 2.3 单独项不显著，交互项显著

v32 结果说明：

| 变量 | `PeerCAR[0,+1]` event FE | 解释 |
|---|---:|---|
| `AIActivePeer` | -0.0015, p = 0.2888 | 单独 AI-active 分组不显著 |
| `Spec` | 0.0002, p = 0.9112 | 单独披露具体性不显著 |
| `Spec x AIActivePeer` | -0.0033, p = 0.0096 | 两者重叠位置显著 |

这支持把 `Spec x AIActivePeer` 写成机制/异质性，而不是把 `Spec` 或 `AIActivePeer` 单独写成主效应。

文件：`docs/empirical_runs/96_v32_standalone_heterogeneity_probe_20260605.md`

## 3. 可作为稳健性和防守证据

### 3.1 peer 自身事件污染清洗

| 清洗口径 | `PeerCAR[0,+1]` | N | events | 解释 |
|---|---:|---:|---:|---|
| 全样本 | -0.0047, p = 0.0045 | 2,789 | 316 | 基准 |
| 删除 peer 自身严格 GenAI 事件 | -0.0048, p = 0.0034 | 2,773 | 316 | 结果更强，peer 自己发 GenAI 不是来源 |
| 删除 peer 重大公告 | -0.0042, p = 0.0156 | 1,868 | 310 | `AR[0]` 弱化，但 `CAR[0,+1]` 仍成立 |
| 删除 peer 自身 GenAI 或重大公告 | -0.0042, p = 0.0155 | 1,865 | 310 | 当前最重要污染清洗 |

文件：`docs/empirical_runs/97_v33_supplement_data_probe_20260605.md`

建议写法：

```text
在剔除同行自身 GenAI 事件或重大公告污染后，CAR[0,+1] 仍保持负向且显著。
这降低了结果由同行自身窗口事件驱动的可能性。
```

### 3.2 严格污染清洗下的机制功效下降

v36 中，删除 peer 自身 GenAI 或重大公告后：

| 口径 | `Spec x AIActivePeer` | N | events | 解释 |
|---|---:|---:|---:|---|
| base controls | -0.0030, p = 0.0712 | 1,808 | 310 | 方向一致，10% 显著 |
| + firm-style main effects | -0.0026, p = 0.1082 | 1,618 | 276 | 方向和量级一致，功效下降 |
| + `Spec x firm-char` 全套交互 | -0.0025, p = 0.1292 | 1,618 | 276 | 不能写“稳健显著” |

文件：`docs/empirical_runs/100_v36_spec_ai_firm_char_guard_20260605.md`

建议写法：

```text
在更严格的污染清洗样本中，核心交互项方向和量级与主样本一致，
但由于样本从 2,404 行下降到 1,618 行，标准误上升，统计显著性下降。
```

不要写成：

```text
严格清洗后结果仍稳健显著。
```

### 3.3 长窗口不反转

| 窗口 | 结果 | 覆盖率 | 解释 |
|---|---:|---:|---|
| `PeerCAR[0,+20]` | -0.0293, p < 0.001 | 79.1% | 没有短期反转，支持不是简单注意力/流动性轮动 |
| `PeerCAR[0,+60]` | -0.0639, p < 0.001 | 59.9% | 方向更强，但覆盖下降，只能辅助 |

文件：`docs/empirical_runs/97_v33_supplement_data_probe_20260605.md`

建议写法：

```text
同行负向反应在较长窗口内没有快速反转，这与单纯注意力轮动或短期流动性抛压解释不一致。
```

注意：`[0,+60]` 覆盖率只有约 60%，不能作为主结果；`[0,+20]` 更适合正文或主附录。

### 3.4 分析师覆盖子样本

v34 先证明预测修正方向：

| 预测变量 | FY+1 60 日 scaled revision | 解释 |
|---|---:|---|
| EPS | -0.1056, p = 0.0097 | 覆盖样本中 FY+1 EPS 下修 |
| 归母利润 | -0.0953, p = 0.0327 | 覆盖样本中 FY+1 归母利润下修 |

v37 再证明覆盖样本中的短窗主效应仍在：

| 样本 | `PeerCAR[0,+1]` | N | events | peer firms |
|---|---:|---:|---:|---:|
| FY+1 EPS 或归母利润 60 日预测修正可观测 | -0.0110, p = 0.0025 | 185 | 100 | 105 |
| 非该覆盖样本 | -0.0042, p = 0.0119 | 2,604 | 316 | 1,317 |

文件：

- `docs/empirical_runs/98_v34_analyst_forecast_revision_probe_20260605.md`
- `docs/empirical_runs/101_v37_mechanism_closure_20260605.md`

建议写法：

```text
在可以观察分析师盈利预期修正的同行样本中，短窗口负向 CAR 与 FY+1 盈利预测下修并存。
该证据与现金流预期解释方向一致。
```

不要写成：

```text
本文已经证明市场反应通过现金流渠道形成。
```

原因：分析师覆盖率约 6.6%，且 v34 中短窗 CAR 不能稳定预测预测修正幅度。

## 4. Null 结果和应关闭的路线

### 4.1 focal-peer 镜像不支持零和再分配

v33 原始镜像显示 focal CAR 与 peer CAR 正相关。v35-v37 进一步检验 `FocalCAR x PeerSimilarity`：

| 口径 | `FocalCAR x PeerSimilarity` | 解释 |
|---|---:|---|
| v35 no event FE + peer industry-week FE + two-way cluster | 0.0003, p = 0.8257 | 不支持负向竞争梯度 |
| v37 no event FE + peer industry-week FE + event cluster | 0.0003, p = 0.8264 | Claude 指定口径下仍不支持 |
| v37 清洗 peer GenAI/重大公告后 | 0.0017, p = 0.2823 | 方向更不是负 |

文件：

- `docs/empirical_runs/99_v35_focal_peer_two_component_probe_20260605.md`
- `docs/empirical_runs/101_v37_mechanism_closure_20260605.md`

建议写法：

```text
我们也检验了跨事件 focal-peer 镜像关系，但未发现焦点公司 CAR 与产品相似度共同产生的负向竞争梯度。
因此，本文不依赖跨事件零和镜像识别竞争机制；
核心识别来自同一事件内不同同行的横截面差异。
```

不要继续投入这条线，除非未来有更强的事件分类或残差化设计。

### 4.2 announcement category 不宜作为核心机制

v31 中 `product_oriented` 均值约 0.896，分布过于不均衡；`Product-oriented x AIActivePeer` 也没有稳定结果。

建议：人工核验前，不把产品导向公告类别作为主机制。可以保留为附录或未来扩展。

## 5. 稳健性分层

### 正文主表/主机制可用

| 模块 | 当前判断 |
|---|---|
| `PeerCAR[0,+1]` 主效应 | 可作为主结果 |
| `Spec x AIActivePeer` | 可作为核心机制/异质性 |
| firm-character guard | 可作为机制防守主表 |

### 附录稳健性可用

| 模块 | 当前判断 |
|---|---|
| 删除 peer 自身 GenAI 事件 | 强稳健 |
| 删除 peer 重大公告 / GenAI 或重大公告 | `CAR[0,+1]` 稳健，`AR[0]` 弱化 |
| 长窗口 `[0,+20]` | 可作为排除短期反转的证据 |
| event-only cluster vs event/peer cluster | 结论不变 |

### 只能作为支持性机制

| 模块 | 当前判断 |
|---|---|
| 分析师 FY+1 下修 | 方向一致，但覆盖率低 |
| 分析师覆盖子样本主效应 | 很强，但样本选择明显 |
| `[0,+60]` 长窗口 | 方向强，但覆盖下降 |

### 应作为 null / 关闭路线

| 模块 | 当前判断 |
|---|---|
| focal-peer 零和镜像 | 不支持，不要作为机制 |
| `FocalCAR x PeerSimilarity` | 精确口径下 p = 0.8264，关闭 |
| product-oriented announcement category | 当前不可作为核心机制 |

## 6. 当前可写的机制段骨架

本文机制部分建议按四块组织：

1. **事件污染清洗**：排除同行自身 GenAI 或重大公告驱动结果。
2. **披露可信度与技术空间重叠**：`Spec x AIActivePeer` 说明负向重估集中在可信披露与技术可比同行交叠处。
3. **firm-character guard**：加入 `Spec x Size/Beta/Volatility/MB` 后核心交互仍成立，排除一般风格因子解释。
4. **持久性与盈利预期落点**：长窗口不反转；分析师覆盖样本中，短窗负 CAR 与 FY+1 盈利预测下修并存。

一段较安全的论文表述：

```text
这些结果共同表明，焦点公司具体 GenAI 披露引发的同行重估并非由同行自身窗口事件、
一般风格特征或短期注意力轮动单独解释。负向反应集中在具有既有 AI 活动证据的同行中，
且在控制披露具体性与规模、beta、波动率和估值特征的交互后仍然存在。
在分析师覆盖的子样本中，短窗负向 CAR 与 FY+1 盈利预测下修方向一致，
进一步支持市场将该披露理解为竞争风险信号。
```

## 7. 仍需补的工作

| 优先级 | 工作 | 目的 |
|---|---|---|
| 高 | 把 v31/v36/v37 整理成论文机制表 | 形成可直接放进 manuscript 的 Table |
| 高 | 长窗口 `[0,+20]` 做 late-event / coverage sensitivity | 防止长窗口因样本覆盖变化被质疑 |
| 中 | 加异常换手率 / 成交额控制 | 进一步排除注意力和流动性解释 |
| 中 | 人工核验 `product_oriented` 或放弃该类别 | 避免使用分布失衡的规则变量 |
| 中低 | 未来基本面 sales growth / gross margin | 给现金流解释补长期落点 |
