# 网页版深度研究 Prompt：竞品溢出主效应是否有正当跑显著空间

日期：2026-05-22

## 使用说明

把下面整段 prompt 复制到 ChatGPT Pro / Claude / 深度研究工具中。目标不是让模型 p-hack，而是让它独立判断：

```text
在不进行不当数据挖掘的前提下，
我们的 GenAI 披露具体性 × 产品市场竞品溢出设计，
是否存在理论上正当、文献上可防御、数据上可执行的方式提高主效应信噪比。
```

---

## Prompt

你是一名会计、金融、信息系统、运营管理交叉领域的顶刊审稿人兼实证研究设计顾问。请你帮我独立审查一个中国 A 股上市公司 GenAI 披露研究设计，并重点判断：**有没有正当可能把主效应跑得更清楚 / 更显著**。注意，禁止建议 p-hacking、事后挑窗口、机械删样本。所有建议必须满足三条标准：

1. **理论上事前可解释**：为什么这个样本切片或变量定义更应该有反应；
2. **文献上可锚定**：是否能对应事件研究、披露信息含量、产品市场竞争、供应链/同业溢出、GenAI announcement 等成熟文献；
3. **数据上可执行**：能否用中国 A 股公开数据或现有数据完成。

### 一、当前研究问题

我们原来做过很多版本，现在暂时收口到这个问题：

```text
一家上市公司在交易所互动平台上更具体地披露 GenAI / 大模型 / AIGC 应用时，
资本市场是否会重新定价其产品市场竞争对手？
```

当前主设计：

```text
Main X:
    Specificity_it × ProductSimilarity_ij

其中：
    Specificity_it = 披露公司 i 在事件日 t 的 GenAI 披露具体性
    ProductSimilarity_ij = 披露公司 i 与竞品公司 j 的产品市场文本相似度

Main Y:
    PeerCAR_jt = 竞品公司 j 在披露公司 i 的事件日 t 附近的短窗市场反应

Unit:
    focal GenAI disclosure event i,t × peer firm j
```

当前解释逻辑：

```text
如果披露公司 GenAI 声明越具体，说明其 GenAI 应用越接近真实业务 / 产品落地。
对产品相似竞品而言，这可能是竞争威胁，也可能是行业机会。
```

因此平均主效应可能混合：

```text
竞争威胁：高相似竞品 CAR 更低；
行业机会：高相似竞品 CAR 更高。
```

### 二、当前 pilot 数据与结果

事件样本来自中国交易所互动平台，严格口径为：

```text
公司回复文本本身包含 GenAI / 大模型 / AIGC / ChatGPT / DeepSeek 等内容。
投资者问题只作为触发语境，不直接视为公司披露。
```

当前事件样本：

```text
590 条 answer-level events
402 个 firm-day events
222 家披露公司
```

产品市场竞品网络：

```text
用国泰安 STK_LISTEDCOINFOANL.xlsx 中 MAINBUSSINESS + BusinessScope 文本；
中文字符 2-4 gram TF-IDF cosine；
在同 IndustryNameD 内取 Top 5 / Top 10 产品市场相似 peer。
```

X 试跑结果：

```text
Top10 peer 口径：
    399 个事件可匹配 peer；
    2,178 个 focal-peer links；
    3,978 个 event × peer X observations。

Top5 peer 口径：
    1,993 个 event × peer X observations。
```

主效应 pilot：

```text
行情：Sina Finance 日 K 公开接口，仅为 pilot；
市场收益：上证指数 sh000001；
窗口：PeerCAR[-1,+1]；
估计：market model；
主样本：Top5 peer；
CAR-linked observations: 1,906；
events: 399；
peer firms: 681。
```

当前主规格：

```text
PeerCAR_jt =
    beta1 ProductSimilarity_ij
  + beta2 Specificity_it × ProductSimilarity_ij
  + Event FE
  + error_ijt
```

当前结果：

```text
coef(Specificity × ProductSimilarity) = -0.0167
clustered SE by event = 0.0121
p = 0.168
```

加入 peer FE 后：

```text
coef = -0.0165
p = 0.213
```

Portfolio spread sanity check：

```text
Top-rank peer portfolio CAR - low-rank peer portfolio CAR
coef on Specificity = -0.0015
p = 0.355
```

`|CAR|` quick check 也不显著。

所以当前结论是：

```text
方向偏竞争威胁，但统计上不显著。
```

### 三、请重点参考的范文

请重点借鉴这篇范文的处理方式：

```text
Qian, Peng, and Li (2025),
The Impact of Generative AI Announcements on Suppliers: Evidence From the Stock Market,
Production and Operations Management, OnlineFirst.
DOI: 10.1177/10591478251398333
```

该文做法摘要如下：

1. 事件源不是交易所互动回复，而是 LexisNexis / PR Newswire / Business Wire / GlobeNewswire 等新闻稿与通讯社。
2. 他们先得到 14,941 条潜在 GenAI announcement，再筛到 2,084 条北美上市公司 announcement。
3. 排除 1,397 条泛泛提到 GenAI 与其他 IT 的 broad mention，只保留具体 GenAI initiative。
4. 最终得到 254 家公司的 initial GenAI announcements。
5. 匹配上市供应商后，最终样本是：

```text
117 announcing firms
277 suppliers
515 supplier-announcement observations
```

6. 他们主效应不是用一个很宽的窗口硬跑，而是标准事件研究：

```text
AR on day -1
AR on day 0
AR on day +1
```

主发现集中在 announcement day `AR[0]`：

```text
mean AR[0] = 0.27%，1% 显著；
median AR[0] = 0.13%，1% 显著；
positive AR proportion = 54.56%，5% 显著。
```

7. 他们估计 expected return 时用 Fama-French four-factor model，估计窗口为：

```text
[-210, -11] trading days
```

8. 如果 announcement 在周末、节假日或盘后发布，则顺延到下一交易日。
9. 他们排除了供应商自身在客户公告前已经有 GenAI announcement 的样本。
10. 他们排除了多个客户 announcement 日期重叠导致供应商反应互相污染的样本。
11. 他们排除了事件窗口 [-2, +1] 内有 board change、earnings、M&A 等 confounding events 的供应商。
12. 他们的机制和显著性主要来自横截面异质性：

```text
供应商 R&D intensity 更高；
供应商 sales growth 更高；
供应商与客户地理距离更近；
供应商所处行业竞争更低 / concentration 更高；
客户 GenAI announcement 是 product-oriented 而不是 process-oriented。
```

13. 他们还做了 PSM、IV、Heckman、DID、长期 CAR、排除 LLM release / 政府政策冲击日、替代 FF 三因子 / 五因子等稳健性。

### 四、请你完成的任务

请你基于上述信息，独立判断我们的竞品溢出设计是否还有“正当跑显著”的可能。请按以下结构回答。

#### 1. 先给一个总判断

请明确回答：

```text
继续救这条产品市场竞品溢出线，是否值得？
```

用以下三档之一：

```text
A. 值得继续，且有较明确的正当改进路径；
B. 可以继续做一次强化 pilot，但不宜押主线；
C. 不建议继续作为主线，应转向其他设计。
```

必须给出理由。

#### 2. 对照范文，指出我们现在最大的问题

请逐条比较：

```text
事件源强度；
事件定义是否具体；
事件窗口；
Y 是 AR[0] 还是 CAR[-1,+1]；
peer / supplier 关系是否足够强；
confounding events 清洗；
异质性是否理论先验足够强；
样本单位是否能放大且不引入噪音；
是否存在方向混合。
```

请指出哪些差距最可能导致我们现在不显著。

#### 3. 请提出“正当提高信噪比”的候选方案

请至少给出 8 个候选方案。每个方案必须按表格写：

```text
方案名称
怎么改 X / Y / 样本 / 模型
理论理由
对应范文或文献逻辑
预期符号
是否可能提高显著性
是否有 p-hacking 风险
执行难度
推荐优先级
```

请重点考虑但不限于：

1. 把 Y 从 `CAR[-1,+1]` 改成 `AR[0]` 或 `CAR[0,+1]`；
2. 只看交易时间前发布 / 盘后顺延后的 day 0；
3. 只保留公司回复中有明确产品 / 场景 / 客户 / 时间 / 金额 / 合作方的 high-specificity GenAI disclosure；
4. 区分 product-oriented GenAI disclosure 和 process-oriented / internal efficiency disclosure；
5. 区分竞品的 prior AI capability，高能力竞品可能正反应，低能力竞品可能负反应；
6. 竞品关系从宽行业 Top5 改成更严格的产品市场文本 Top3 / Top5；
7. 用年报业务章节替代 `BusinessScope + MAINBUSSINESS` 构造 product similarity；
8. 排除同日重大公告、财报、重组、监管问询、涨跌停、ST、北交所等噪音；
9. 使用 ABVOL / attention / investor questions as alternative Y；
10. 把平均主效应改成异质性主假说，例如：

```text
High Specificity × ProductSimilarity × Low Peer AI Capability -> negative PeerCAR
High Specificity × ProductSimilarity × High Peer AI Capability -> positive or less negative PeerCAR
```

11. 把事件源从互动平台换成更强的正式公告 / 投资者关系活动记录 / 新闻稿；
12. 用 same-event high-vs-low peer portfolio spread，而不是 observation-level regression；
13. 加入 industry-date 或 event FE 的正确规格；
14. 使用 day 0 AR 的 t-test / Wilcoxon / sign test，先回答是否有总体 peer reaction，再做回归。

#### 4. 请判断最应该优先试的 3 个版本

请不要列太多。最后必须给出 Top 3 可执行版本，每个版本明确：

```text
主 X
主 Y
样本筛选
回归 / 检验方法
预期方向
为什么比当前 pilot 更可能跑出结果
最大风险
```

#### 5. 请判断是否应该改论文故事

当前故事是：

```text
GenAI 披露具体性 -> 产品市场竞品重估
```

请判断是否应该改成：

```text
A. 产品市场竞争威胁；
B. 行业机会重估；
C. 投资者注意力 / attention spillover；
D. 异质性故事：低 AI 能力竞品是竞争威胁，高 AI 能力竞品是行业机会；
E. 放弃竞品，回到供应商或同公司信息含量。
```

必须给出排序。

#### 6. 最后给一个明确执行建议

请用很直白的话回答：

```text
下一步我应该跑哪一张表？
哪一个结果如果仍不显著，就应停止这条线？
哪一个结果如果显著，才值得继续投入？
```

请注意：不要给泛泛文献综述，不要只说“增加样本量”。我要的是围绕当前 pilot 结果和范文处理方式，判断哪些正当设计改动最可能提高信噪比。

---

## 我希望你输出的格式

请用中文输出，结构如下：

```text
一、总判断
二、范文如何处理显著性与信噪比
三、我们当前 pilot 为什么不显著
四、正当改进方案表
五、最优先跑的 Top 3
六、是否应该改故事
七、停止 / 继续的判据
```

要求直接、批判、可执行。
