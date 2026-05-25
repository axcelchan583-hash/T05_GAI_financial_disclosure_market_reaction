# v4 正式实验设计更新：AI-active 产品市场竞品重估

日期：2026-05-22

## 1. 当前判断

上一版 v4 的平均效应设计是：

```text
Specificity_it × ProductSimilarity_ij -> PeerCAR_jt
```

这个方向在经济含义上是对的，但正式 CSMAR 试跑显示，所有产品市场竞品的平均反应不够强：

```text
Top5 clean CAR[0,+1]:
    coef = -0.0116
    p = 0.120
```

因此当前不应继续把“所有竞品平均都会反应”作为主假设。更清楚、也更贴近结果的实验设计是：

```text
焦点公司的 GenAI 披露越具体，
越相似且已经处在 AI / GenAI 竞争空间中的产品市场竞品，
是否出现更负面的短窗市场反应？
```

也就是说，主问题从：

```text
GenAI disclosure specificity 是否影响所有产品市场 peer？
```

收紧为：

```text
GenAI disclosure specificity 是否触发 AI-active product-market peers 的竞争威胁重估？
```

## 2. 明确主 X 与主 Y

### Main X

主解释变量是三重交互：

```text
Specificity_it × ProductSimilarity_ij × AIActivePeer_j,t-
```

三个组成部分分别是：

1. `Specificity_it`
   焦点公司 `i` 在事件日 `t` 的 GenAI 披露具体性。当前主样本使用交易所互动平台严格事件，即公司回复文本本身包含 GenAI / 大模型 / AIGC 内容的 firm-day 事件。

2. `ProductSimilarity_ij`
   焦点公司 `i` 与竞品公司 `j` 的产品市场相似度。当前可行版本用国泰安主营业务 / 经营范围文本构造同 `IndustryNameD` 内 Top5 / Top10 peer；正式版应尽量换成事件日前一年年报业务章节文本。

3. `AIActivePeer_j,t-`
   竞品公司 `j` 在事件日前已经有 AI / GenAI 活跃证据。当前第一版可操作定义为：

```text
AIActivePeer = 1{
    peer has prior public GenAI evidence
    or peer has 2024 annual-report GenAI evidence
}
```

后续更硬的定义应加入：

- 披露前 AI / GenAI 招聘；
- 披露前 AI / GenAI 专利；
- CAC 生成式 AI 服务备案；
- 已上线 AI / GenAI 产品或模型服务；
- 软件著作权或产品公告中的 AI 应用证据。

原则是：`AIActivePeer` 必须使用事件日前或足够外生的基准期信息，不能使用事件后的实现结果。

### Main Y

主被解释变量是竞品公司 `j` 在焦点公司 `i` 的 GenAI 披露事件附近的 signed CAR：

```text
PeerCAR_jt[-1,+1]
```

当前交互项结果最强的是 clean sample 的 `CAR[-1,+1]`，因此它应升为主窗口。`CAR[0,+1]` 作为稳健性窗口保留。

Y 的方向解释：

- `beta2 < 0`：具体 GenAI 披露被市场理解为对 AI-active 竞品的竞争威胁；
- `beta2 > 0`：具体 GenAI 披露被市场理解为对 AI-active 竞品的行业机会或需求扩张信号。

当前数据更支持第一种解释。

## 3. 主回归

样本单位：

```text
focal GenAI disclosure event i,t × product-market peer j
```

主规格：

```text
PeerCAR_ijt[-1,+1] =
    beta1 * Specificity_it × ProductSimilarity_ij
  + beta2 * Specificity_it × ProductSimilarity_ij × AIActivePeer_j,t-
  + beta3 * ProductSimilarity_ij × AIActivePeer_j,t-
  + EventFE_it
  + PeerControls_j,t-
  + error_ijt
```

核心假设：

```text
H1: beta2 < 0
```

中文表述：

```text
当焦点公司的 GenAI 披露越具体时，资本市场会对已处于 AI 活跃竞争空间中的产品市场同业作出更负面的重估。
```

英文表述：

```text
More specific GenAI disclosures by focal firms trigger more negative market reactions among AI-active product-market peers.
```

## 4. 当前实证证据

### 平均主效应

正式 CSMAR 主效应方向稳定为负，但未达到常规显著性：

```text
Top5 raw CAR[0,+1]:
    coef = -0.0186
    p = 0.120

Top5 clean CAR[0,+1]:
    coef = -0.0116
    p = 0.120

Top5 clean CAR[0,+1] + peer controls:
    coef = -0.0116
    p = 0.118
```

解释：平均效应方向支持竞争威胁，但不够强，不适合作为唯一主表。

### AI-active peer 三重交互

当前最强结果来自：

```text
Specificity × ProductSimilarity × AIActivePeer
```

Clean sample, Top5 peers, `CAR[-1,+1]`：

| Spec | Interaction term | coef | p-value | nobs | events | peer firms |
|---|---:|---:|---:|---:|---:|---:|
| No controls | `xspecsim_ai_active_broad` | -0.0103 | 0.005 | 1,755 | 398 | 640 |
| + peer controls | `xspecsim_ai_active_broad` | -0.0095 | 0.011 | 1,755 | 398 | 640 |

控制变量包括：

```text
z_peer_beta
z_pre_mom_60
z_pre_vol_120
z_pre_absret_60
is_chinext_or_star
z_peer_rank
```

这个结果说明，市场反应不是平均发生在所有竞品上，而是集中在已经具有 AI / GenAI 相关基础或市场叙事的产品市场竞品上。

## 5. 机制解释

当前最合适的机制不是“低 AI 能力竞品被打击”。这个说法目前不够稳，因为 low capability 的可操作定义依赖缺失证据，容易把“没观察到披露”误当成“没有能力”。

更稳的机制是：

```text
AI-active peers are the relevant competitive set.
```

解释链条：

1. GenAI 披露越具体，说明焦点公司不是泛泛蹭概念，而是在产品、服务、客户、流程或商业化场景上释放更可理解的信息。
2. 产品市场越相似，竞品越可能受到同一技术应用场景的竞争影响。
3. 只有 AI-active peer 已经被投资者放进 AI / GenAI 竞争空间，市场才会把焦点公司的具体披露解释为可比竞争威胁。

因此，论文主叙事应写成：

```text
Specific GenAI disclosures reshape investors' assessment of competition among AI-active product-market peers.
```

而不是：

```text
Specific GenAI disclosures hurt all competitors.
```

## 6. 稳健性与扩展

### 必做稳健性

1. 替换事件窗口：
   - `CAR[0,+1]`
   - `AR[0]`
   - `CAR[-2,+2]`

2. 替换竞品口径：
   - Top5 产品相似 peer；
   - Top10 产品相似 peer；
   - 同行业低相似 pseudo peers；
   - 随机 pseudo peers。

3. 替换 `AIActivePeer` 定义：
   - prior public GenAI evidence；
   - annual-report GenAI evidence；
   - CAC / patent / hiring 扩展定义。

4. 控制 peer 事件前特征：
   - beta；
   - momentum；
   - volatility；
   - absolute return；
   - ChiNext / STAR；
   - peer rank；
   - size / BM / ROA 等常规变量，若可得。

### 可做机制

1. 事件披露类型：
   - product-facing / customer-facing / revenue-facing；
   - internal-process / efficiency-improvement；
   - generic AI discussion。

2. 披露时间：
   - after-close disclosure 作为事件日处理和注意力机制的稳健性。

3. 高 AI 词频 vs 真具体性：
   - 当前结果暗示反复提 AI 词可能削弱竞争威胁信号；
   - 但这不是主机制，需要更细文本分类后再写。

## 7. 降级变量

以下变量不再抢主线：

| 变量 | 当前角色 | 原因 |
|---|---|---|
| `Specificity × ProductSimilarity` 平均效应 | 基准 / 对照 | 方向稳定但不显著 |
| `LowPeerAICapability` | 暂不作为主机制 | 缺失证据不能等同于低能力 |
| `FutureMatchedPublicEvidence` | validation / 案例 | 自构造色彩较强 |
| future AI hiring | 异质性 / 机制 | 与 GenAI 披露太近，不适合作主 Y |
| AI patents / CAC 备案 | AI-active 定义或机制 | 适合增强 peer 状态，不适合作主 Y |
| 同公司 `|CAR|` | 附录 | 回到传统信息含量，贡献偏窄 |
| 供应商 CAR | 对照 / robustness | 与供应商 GenAI announcement 文献过近 |

## 8. 下一步实验顺序

1. 把三重交互主规格固化成正式脚本，而不是只保留 exploratory screen。
2. 扩展 `AIActivePeer` 的定义，加入 CAC、招聘、专利、产品上线证据。
3. 用 Top10 peer 与 pseudo peer 口径重跑。
4. 补常规控制变量，至少形成一张可给导师看的主表。
5. 对最强结果对应的事件和 peer 做人工抽样复核，确认不是几个极端公司驱动。

## 9. 一句话版本

```text
本文研究中国上市公司 GenAI 披露的竞争信息溢出：
当一家公司在交易所互动平台上更具体地披露 GenAI 应用时，
资本市场是否会对已处于 AI 活跃竞争空间中的产品市场竞品作出更负面的短窗重估。
```
