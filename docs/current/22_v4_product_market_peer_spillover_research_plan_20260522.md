# v4 研究计划：GenAI 披露具体性与产品市场竞品溢出

日期：2026-05-22

## 0. 版本状态

本文件是 v4 的初始设计，核心是平均产品市场同业反应：

```text
Specificity_it × ProductSimilarity_ij -> PeerCAR_jt
```

后续 CSMAR 试跑显示，平均效应方向为负但不显著；更可写的正式实验设计已经更新为：

```text
Specificity_it × ProductSimilarity_ij × AIActivePeer_j,t-
-> AI-active peer CAR[-1,+1]
```

当前最新版本请以：

```text
docs/current/31_v4_experimental_design_ai_active_peer_20260522.md
```

为准。本文件保留作为路线演化和平均效应基准的来源。

## 1. 当前判断

上一版 `X = 年报 / 公告 GenAI 披露具体性，Y = 披露公司自身 |CAR|` 虽然测度干净，但研究问题偏窄：

```text
公司说得更具体，自己股票波动更大。
```

这个问题可以做，但贡献有限，且容易回到传统 disclosure information content。供应链方案能放大样本，但又和 `The Impact of Generative AI Announcements on Suppliers` 过近。

因此，当前更值得试的主线是：

```text
一家上市公司的 GenAI 披露越具体，
资本市场是否会重新评估其产品市场竞争对手？
```

它把研究对象从“披露公司自身”推到“产品市场同业 / 竞品”，核心贡献变成：

```text
GenAI 披露不仅是公司自身信息，
也可能向资本市场传递一个产品市场竞争信号。
```

## 2. 明确主 X 与主 Y

### Main X

主 X 是披露公司 `i` 在事件日 `t` 的 GenAI 披露具体性：

```text
Specificity_it = GenAI 回复 / 披露文本中的具体实体与量化细节密度
```

优先用交易所互动平台严格样本：

```text
公司回复文本本身包含 GenAI 内容的 firm-day 事件
```

原因：

- 正式公告 GenAI 事件太少，无法支撑主回归；
- 互动平台严格样本已有 402 个 firm-day events、222 家公司；
- 公司回复是公开、留痕、可交易观察的信息，不是私下沟通；
- 投资者问题可以作为触发语境和控制变量，但不能直接当公司披露。

具体性测度锚定 Hope, Hu, and Lu (2016) 的 Level of Detail 思路。中文实现时不做主观 1-5 分，而统计：

- 组织名；
- 产品 / 模型 / 平台名；
- 业务场景；
- 合作方；
- 时间；
- 金额；
- 数量 / 百分比；
- 备案号 / 项目名 / 合同名。

### Main Y

主 Y 是竞品公司 `j` 在披露公司 `i` 的 GenAI 事件窗口内的短窗市场反应：

```text
PeerCAR_jt = 竞品公司 j 在事件日 t 附近的 CAR[-1,+1]
```

主结果用 signed CAR，而不是只用 `|CAR|`。

原因：

- 如果 GenAI 披露被市场理解为竞争威胁，高相似竞品应出现负反应；
- 如果被市场理解为行业机会或需求扩张，高相似竞品可能出现正反应；
- `|CAR|` 和 ABVOL 适合解释信息含量，但 signed CAR 更能区分经济机制。

稳健性 Y：

```text
|PeerCAR[-1,+1]|
PeerABVOL[-1,+1]
PeerCAR[-2,+2]
PeerCAR[0,+1]
```

## 3. 竞品关系怎么确定

不要人工指定“竞品”。主方案使用产品市场文本相似度。

### 主定义：产品市场相似度

对每个上市公司，用事件日前一年的年报业务 / 产品文本构造产品市场向量：

```text
ProductText_i,y-1 = 主营业务 + 产品服务 + 经营范围 + 核心产品 + 主要客户行业描述
```

然后计算公司之间的文本相似度：

```text
ProductSimilarity_ij,y-1 = cosine(TF-IDF_i, TF-IDF_j)
```

竞品定义：

```text
Competitor_ij = 1{j 属于 i 在同年度产品相似度 Top 5 / Top 10}
```

这个设计对应 Hoberg-Phillips / TNIC 风格的产品市场网络思想：竞争关系由产品描述文本接近程度刻画，而不是手工指定。

### 备用定义

备用竞品口径：

- 同申万二级 / 三级行业；
- 同证监会行业；
- 同 Wind 行业；
- 同行业内市值接近的公司；
- 同行业内产品文本相似度 Top 10。

### 负控定义

负控口径：

- 同行业但产品文本相似度最低的公司；
- 不同行业但市值相近的公司；
- 随机匹配非竞品公司。

## 4. 核心回归

样本单位：

```text
focal event i,t × peer firm j
```

核心模型：

```text
PeerCAR_jt =
    beta * Specificity_it × ProductSimilarity_ij
    + EventFE_it
    + PeerFE_j
    + Controls
    + error_ijt
```

关键点：

- `EventFE_it` 吸收披露公司事件当天的所有共同冲击；
- 因为 `Specificity_it` 在同一个事件内不变，所以不能只估计 `Specificity_it` 主效应；
- 真正识别来自：同一个 GenAI 事件发生时，产品更相似的竞品是否反应更强；
- `Specificity_it × ProductSimilarity_ij` 才是主解释变量。

更直观的组合投资组合版本：

```text
PeerSpread_it =
    mean CAR of high-similarity peers
    - mean CAR of low-similarity pseudo peers

PeerSpread_it = beta * Specificity_it + Controls + error_it
```

这个版本适合第一张图和第一张表，因为读者容易理解。

## 5. 机制解释

这篇文章不应写成“市场是否奖励 GenAI 披露”，而应写成：

```text
GenAI 披露是否改变资本市场对产品市场竞争格局的理解。
```

可能机制有两个，方向可能相反：

1. 竞争威胁机制
   披露公司越具体，说明其 GenAI 应用越接近真实产品 / 业务落地。市场可能下调相似竞品估值，尤其是 AI 能力基础弱的竞品。

2. 行业机会机制
   披露公司越具体，说明该产品市场的 GenAI 应用空间更清晰。市场可能上调同类公司估值，尤其是已有 AI 能力基础的竞品。

因此，signed CAR 的方向本身就是结果，不应预设一定为正或负。可以先提出信息溢出假说，再用异质性区分竞争威胁与行业机会。

## 6. 关键异质性

最重要的异质性是竞品自己的 AI 能力基础：

```text
PeerPriorAICapability_j
```

可用变量：

- 披露前 AI / GenAI 招聘份额；
- AI 专利；
- CAC 备案；
- 年报中已有 GenAI / AI 产品基础；
- 数字化 / 软件研发基础。

预期：

```text
Specificity_it × ProductSimilarity_ij × PeerPriorAICapability_j
```

如果高能力竞品正反应更强，说明市场看到的是行业机会；如果低能力竞品负反应更强，说明市场看到的是竞争威胁。

## 7. 与供应链论文的区别

这条路线与 `The Impact of Generative AI Announcements on Suppliers` 的区别必须写清楚：

| 维度 | 供应商论文 | v4 本项目 |
|---|---|---|
| 关系类型 | 客户-供应商垂直关系 | 产品市场水平竞争关系 |
| 事件含义 | 客户 GenAI announcement 对供应商需求 / 协作预期的影响 | 披露公司 GenAI 具体信息对竞品估值的影响 |
| 关键 X | GenAI announcement dummy | GenAI disclosure specificity |
| 关键 Y | supplier CAR | competitor / peer CAR |
| 机制 | 垂直供应链需求溢出 | 竞争威胁、行业机会、注意力转移 |
| 样本放大方式 | supplier-announcement observation | peer-event observation |

供应链关系可以保留为 robustness 或对照组：

```text
如果产品市场 peer 有反应，而供应商不明显，
说明市场处理的是竞争信号，不只是泛化的 AI 热点。
```

## 8. 可执行数据路线

### Step 1：事件样本

先用 Plan A 严格互动平台事件：

```text
402 个 firm-day GenAI 回复事件
222 家披露公司
```

正式公告样本只有 20 个 GenAI 事件，暂不作为主样本。

### Step 2：竞品网络

用事件日前一年年报文本构造产品相似度。

最小可行版本：

```text
每个披露公司取 Top 10 产品相似竞品
402 events × 10 peers ≈ 4,020 peer-event observations
```

再匹配低相似度 pseudo peers 作为对照，样本可进一步扩大。

### Step 3：市场反应

补齐 2026-02-13 之后的日收益和市场收益。

当前互动平台事件集中在 2026-02 至 2026-05，本地 CSMAR 日收益只到 2026-02-13，所以这是第一数据缺口。

### Step 4：第一版试跑

第一版只做三件事：

1. 构造产品市场 Top 10 竞品；
2. 计算竞品 `CAR[-1,+1]`；
3. 回归 `PeerCAR` 对 `Specificity × ProductSimilarity`。

不要一开始加入 future hiring、claim matched realization、复杂 validation。

## 9. 当前 Gates

继续前必须过四个门：

1. **Peer Network Gate**
   能否从年报业务文本构造出合理的产品相似度 Top 10 竞品。

2. **Return Data Gate**
   能否补齐 2026-02-13 之后的竞品日收益和市场收益。

3. **Sample Size Gate**
   Top 10 竞品口径下，是否能形成至少 2,000 个有效 peer-event CAR observations。

4. **Placebo Gate**
   高相似竞品的反应是否明显强于低相似 pseudo peers。若高低相似都一样动，说明只是在捕捉行业热度或日期冲击。

## 10. 一句话版本

```text
本文研究中国上市公司 GenAI 披露是否具有产品市场溢出效应：
当一家公司在交易所互动平台上更具体地披露 GenAI 应用时，
资本市场是否会重新定价其产品市场竞争对手。
```

## 11. 当前结论

这一版比“同公司披露具体性 -> 同公司 |CAR|”更有贡献，也比直接复制供应商反应更安全。

真正的主设计应锁定为：

```text
Main X:
    披露公司 GenAI 具体性 × 产品市场相似度

Main Y:
    竞品公司短窗 signed CAR

Main channel:
    产品市场竞争威胁 vs 行业机会重估
```

年度报告、AI 招聘、AI 专利、CAC 备案都不要抢主线：

- 年报用于构造产品相似度和 prior AI capability；
- AI 招聘 / AI 专利 / CAC 用于异质性；
- 供应链反应用于对照；
- 同公司 `|CAR|` 用于附录或前置描述。
