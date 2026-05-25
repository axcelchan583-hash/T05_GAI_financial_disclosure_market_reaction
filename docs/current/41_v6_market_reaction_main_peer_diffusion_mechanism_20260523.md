# v6 研究设计：竞品市场重估为主线，披露扩散作为机制

日期：2026-05-23

## 1. 为什么从 v5.1 调整到 v6

v5.1 的 `focal IIP GenAI disclosure -> rival IIP GenAI disclosure` 试跑后，样本量问题已经基本解决，但研究设计本身出现了新的硬伤：

```text
X 是焦点公司在互动平台 / 调研问答中的 GenAI 披露；
Y 是竞品公司在互动平台 / 调研问答中的 GenAI 跟进披露。
```

这会导致 X 和 Y 过于接近。即使同伴扩散结果显著，也更像是在回答：

```text
GenAI 话题是否在产品市场相近公司之间扩散？
```

这个问题可以做机制，但不适合继续作为整篇论文的主 Y。主论文应当回答更外部、更有经济含义的问题：

```text
一家公司的 GenAI 披露是否改变资本市场对其产品市场竞品的估值？
```

因此，v6 的核心调整是：

```text
Main Y:
    竞品资本市场反应

Mechanism Y:
    竞品 GenAI 披露跟进 / 扩散
```

## 2. v6 主研究问题

主问题：

```text
当一家上市公司在公开投资者沟通中披露 GenAI / 大模型 / AIGC 信息时，
资本市场是否会重新评估其产品市场竞品，
尤其是那些已经具备 AI / GenAI 基础、且产品市场高度相似的竞品？
```

推荐英文表述：

```text
Do firms' GenAI disclosures trigger competitive revaluation of product-market peers?
Evidence from Chinese investor-interaction platforms.
```

## 3. 主设计

### 3.1 观察单元

```text
focal GenAI disclosure event i,t × product-market peer firm j
```

焦点事件来自：

- CSMAR 投资者互动表；
- CSMAR 调研问答纪要表；
- 后续可加入交易所公告、投资者关系活动记录全文和年报 GenAI 段落。

竞品关系来自产品市场文本相似度：

```text
ProductSimilarity_ij = cosine similarity of business-description text
```

主口径：

- Top10 产品市场竞品；
- Top5 作为更严格的近邻口径；
- 低相似度同行和随机匹配公司作为 placebo peers。

### 3.2 主 X

主 X 不再只押注 `Specificity × Similarity`，因为最新 CSMAR 试跑显示具体性与同伴披露响应没有稳定信号。

更稳的主解释结构是：

```text
GenAI_Disclosure_Event_i,t
× ProductSimilarity_i,j
× AIActivePeer_j,t-1
```

其中：

- `GenAI_Disclosure_Event_i,t` 是焦点公司 GenAI 披露事件；
- `ProductSimilarity_i,j` 表示产品市场竞争接近程度；
- `AIActivePeer_j,t-1` 表示竞品在事件前已经处于 AI / GenAI 竞争空间。

`Specificity_i,t` 保留，但降为信息强度变量：

```text
Specificity_i,t
× ProductSimilarity_i,j
× AIActivePeer_j,t-1
```

也就是说，具体性不是唯一主 X，而是检验“披露内容越具体，竞争重估越强”的增强项。

### 3.3 主 Y

主 Y 必须是外部于文本披露系统的结果变量：

```text
PeerCAR_j[-1,+1]
PeerCAR_j[0,+1]
Peer abnormal turnover / volume
Peer investor attention
```

优先顺序：

1. signed peer CAR：检验竞争性重估方向；
2. abnormal turnover / volume：检验市场注意力与信息消化；
3. `|CAR|`：只作为信息含量补充，不作为主方向结果。

理论预期：

```text
高产品相似度、且事件前已经 AI-active 的竞品，
在焦点公司具体 GenAI 披露后更可能出现负向短窗重估或更强交易反应。
```

## 4. 机制：同伴披露扩散

`GenAI disclosure -> rival GenAI disclosure` 不再作为主 Y，但可以作为机制表：

```text
焦点公司 GenAI 披露
    -> 资本市场对 AI-active 近邻竞品重估
    -> 竞品随后在互动平台 / 调研问答中跟进 GenAI 披露
```

机制 Y：

```text
RivalFirstGenAIDisclosure_j within 60 / 90 / 180 days after focal event
```

最新 CSMAR 试跑支持把它保留为机制：

```text
全部焦点事件 Top10：
30d coef = 0.0041, p = 0.012
60d coef = 0.0060, p = 0.003
90d coef = 0.0061, p = 0.006

每家公司首次焦点事件 Top10：
60d coef = 0.0112, p = 0.017
90d coef = 0.0131, p = 0.009
180d coef = 0.0173, p = 0.001

pre-window placebo:
30/60/90/180d 均不显著
```

解释边界：

```text
这说明 GenAI 披露可能存在产品市场同伴扩散；
但它不能单独证明真实投资反应，也不能替代资本市场主结果。
```

## 5. 外部验证：CAC 备案与真实行动

CAC 生成式 AI 服务备案 / 深度合成算法备案可以作为外部验证，但不宜单独作为主 Y：

- 时间戳多为批次级，日度 hazard 精度不足；
- A 股可匹配主体数量有限；
- 备案适用于 public-facing 服务，不覆盖企业内部 AI 应用；
- 更适合做 6-12 个月窗口的 validation table。

推荐角色：

```text
Validation:
    焦点公司 GenAI 披露后，
    高相似度竞品是否更可能进入 CAC 备案 / 深度合成算法备案名单。
```

## 6. 已有数据基础

CSMAR 事件库已经解决早期样本太少的问题：

```text
IIP:
    answer-level GenAI events = 25,544
    firm-day GenAI events = 15,460
    firms = 2,587

IR_QA:
    answer-level GenAI events = 15,147
    firm-day GenAI events = 8,268
    firms = 1,274

Combined:
    answer-level GenAI events = 40,691
    firm-day GenAI events = 23,454
    firms = 2,800
    post-2023 firm-day events = 22,701
```

因此，现在的瓶颈不再是事件数量，而是主 Y 是否足够外部、机制是否能与主结果对上。

## 7. 最小 go / no-go

v6 需要先完成一个新的主结果 smoke test：

```text
用完整 CSMAR GenAI 事件库
× Top5 / Top10 产品市场竞品
× 日收益 / 成交量数据
重新估计 peer market reaction。
```

最低通过门槛：

1. `ProductSimilarity × AIActivePeer` 或 `Specificity × ProductSimilarity × AIActivePeer` 在 signed peer CAR 上方向合理；
2. 双向聚类 by focal event and peer firm 后仍至少边际显著；
3. Top5 强于 Top10，符合近邻竞争逻辑；
4. 低相似度 peer / 随机 peer placebo 不成立；
5. 同伴披露扩散机制表方向一致。

如果主 Y 跑不出来：

```text
不要把披露扩散强行升级为主论文。
最多写成 GenAI 话题在产品市场网络中的披露扩散短文，
目标也应明显下调。
```

## 8. 当前结论

当前最稳的定位是：

```text
Main paper:
    GenAI 披露是否引发产品市场竞品的资本市场重估？

Mechanism:
    被影响的产品市场竞品是否随后跟进 GenAI 披露？

Validation:
    是否进一步对应 CAC 备案 / 深度合成算法备案等外部行动？
```

这比 v5.1 更清楚，因为主 Y 不再是同源文本；也比早期 v4 更强，因为 CSMAR 事件库已把样本量从几百扩到两万多个 firm-day 事件，机制表也出现了可解释的同伴扩散信号。
