# T05: 中国上市公司 GenAI 披露、竞品市场重估与同伴扩散机制

更新时间：2026-05-25

## 当前结论

当前主线继续保留，且比上一轮更稳。可执行版本是：

```text
Research question:
    具体化 GenAI 披露是否构成一种竞争威胁信号，
    使资本市场下调产品市场近邻中 AI-active 竞品的短窗估值？

Main X:
    焦点公司首次 GenAI 披露的 Specificity_z
    × 竞品事前 AIActivePeer
    × Top5 产品市场近邻样本定义

Main Y:
    竞品 market-model PeerCAR[0,+1]

Main sample:
    每家公司首次 GenAI 披露事件
    × Top5 产品市场近邻竞品

Main inference:
    event FE
    event FE + peer industry-week FE
    event × peer firm 双向聚类标准误
```

2026-05-25 网页版审阅后的执行口径：

```text
这不是平均 main effect，而是 conditional peer revaluation / heterogeneity effect。

主结论应写成：
    同一个焦点 GenAI 披露事件内，
    AI-active 的近产品市场竞品相对 non-AI-active 竞品出现更负的短窗 CAR，
    且这种相对负向重估随焦点披露 Specificity 更高而更强。

下一步不是继续堆新 Y，
而是补 specificity validation、pre-window controls、external AIActive 并列表、
以及 Top1-3 / Top4-5 / Top6-10 的产品市场距离梯度。
```

2026-05-25 一次性复核已完成：

```text
docs/empirical_runs/53_v6_final_review_checks_20260525.md
results/v6_final_review_checks_20260525
```

2026-05-25 又补了两项针对审稿人最可能质疑的核心稳健性：

```text
docs/empirical_runs/54_v6_focal_good_news_pretrend_checks_20260525.md
results/v6_focal_good_news_pretrend_checks_20260525
```

结论：排除“焦点公司自身利好程度”混杂、以及净化 peer pre-trend 后，`Specificity_z × AIActivePeer` 仍然稳定。

```text
Task 1: 加入焦点公司自身 FocalCAR[0,+1] 及 FocalCAR[0,+1] × AIActive。

Top5 / announcement clean / CAR[0,+1] /
event FE + peer industry-week FE /
PeerCAR[-10,-2] + PeerCAR[-20,-2] controls:

text-history AIActive:
    baseline coef = -0.002275, p = 0.027
    + FocalCAR coef = -0.002275, p = 0.027
    + FocalCAR × AIActive coef = -0.002283, p = 0.027

external ext_any:
    baseline coef = -0.002303, p = 0.020
    + FocalCAR coef = -0.002303, p = 0.020
    + FocalCAR × AIActive coef = -0.002307, p = 0.020

注意：FocalCAR[0,+1] 是 event-level 变量，在 event FE 下会被吸收；
真正有识别含义的是 FocalCAR[0,+1] × AIActive。
```

```text
Task 2: 用 PeerCAR[-10,-2] 净化 PeerCAR[0,+1] 后重跑。

text-history AIActive:
    residualized Y baseline coef = -0.002274, p = 0.027
    residualized Y + FocalCAR × AIActive coef = -0.002281, p = 0.026

external ext_any:
    residualized Y baseline coef = -0.002295, p = 0.021
    residualized Y + FocalCAR × AIActive coef = -0.002300, p = 0.020

样本量：
    N = 7,805
    events = 2,177
    peer firms = 3,345
    clustering = event_id × peer_code
```

结论很清楚：资本市场主效应通过当前 go/no-go 门槛，但披露扩散机制在更严格口径下不显著。

```text
Top5 / CAR[0,+1] / announcement clean /
event FE + peer industry-week FE /
pre-window CAR controls:

text-history AIActive:
    coef = -0.002025, p = 0.036

external ext_any:
    coef = -0.002109, p = 0.024

ext_plus_history:
    coef = -0.002265, p = 0.011

Top10 同口径：
    text-history p = 0.033
    ext_any p = 0.010
    ext_plus_history p = 0.011
```

新增几条关键判断：

```text
1. Specificity 不是简单 length / AI keyword count / source attention / numeric detail：
   加入这些 observable text controls 后，ext_any 口径仍 p = 0.021；
   text-history 口径全控后 p = 0.071，方向和量级稳定。

2. 产品市场距离梯度基本支持竞争接近度：
   Top1-3 ext_any coef = -0.003252, p = 0.016；
   Top6-10 不显著；
   low-similarity 和 random same-industry peer 均不显著。

3. pre-window concern 需要继续正面写：
   text-history AIActive 仍有较长 pre-window pattern；
   external ext_any 没有同样的 pre-window pattern。
   所以主文必须并列展示 text-history 与 ext_any。

4. peer disclosure diffusion 不能再当强机制：
   在 focal-event FE + baseline peer GenAI-disclosure-rate control 后，
   Top5 / Top10 的 60/90/180 天响应均不显著。
   它只能保留为描述性后续反应，不能承担论文机制主张。
```

目前最稳的结果是：

```text
Top5 first focal event, market-model CAR[0,+1],
同时剔除焦点公司与竞品的重大/定期/业绩/风险类公告：

event FE:
Specificity_z × AIActivePeer
coef = -0.002298, p = 0.008

event FE + peer industry-week FE:
Specificity_z × AIActivePeer
coef = -0.002298, p = 0.020

低相似度同行 placebo:
coef ≈ 0, p > 0.90
```

AI 词剔除版产品相似度也保留同一方向：

```text
Top5 first focal event, AI-word-stripped product similarity,
market-model CAR[0,+1],
同时剔除焦点公司与竞品的重大/定期/业绩/风险类公告：

event FE:
Specificity_z × AIActivePeer
coef = -0.002124, p = 0.011

event FE + peer industry-week FE:
Specificity_z × AIActivePeer
coef = -0.002041, p = 0.033
```

公告清洗版 100 次随机同业 placebo 也支持 Top5 不是随机同业波动：

```text
真实 Top5, drop either cleaning announcement, CAR[0,+1]:
coef = -0.002298

100 次同一细行业随机非 Top10 peer:
random median coef = -0.000055
random p05 coef = -0.001483
share random <= true Top5 = 0.00
```

外部版 AIActivePeer 第一轮也支持主方向，但需要保守表述：

```text
ext_any = prior CAC
       OR prior broad-AI patent grant
       OR >=1 broad-AI job posting in prior 365 days

Top5, drop either cleaning announcement, CAR[0,+1]:
event FE coef = -0.001897, p = 0.028
event FE + peer industry-week FE coef = -0.001800, p = 0.058

Top10, drop either cleaning announcement, CAR[0,+1]:
event FE coef = -0.001654, p = 0.004
event FE + peer industry-week FE coef = -0.001493, p = 0.014

低相似度同行 placebo:
coef ≈ 0, p = 0.888
```

把外部 AIActivePeer 接到 AI 词剔除版产品相似度后，结果进一步变稳：

```text
AI-word-stripped Top5, ext_any,
drop either cleaning announcement, CAR[0,+1]:

event FE:
coef = -0.002118, p = 0.011

event FE + peer industry-week FE:
coef = -0.002321, p = 0.011
```

当前最安全的论文表述是：

```text
焦点公司首次 GenAI 披露越具体，
事前已经 AI-active 的 Top5 产品市场近邻竞品，
在 [0,+1] 窗口出现更负的 market-model CAR；
该结果在剔除焦点公司与竞品的重大/定期/业绩/风险类公告后仍成立，
低相似度同行没有类似反应；
同一细行业随机 peer 无法复制该负向强度；
剔除产品描述中的 AI / 大模型 / 智能等通用词后，结论仍保留；
用 CAC、AI 专利授权与事前 AI 招聘构造的外部 AIActivePeer 也得到方向一致的结果；
外部 AIActivePeer 与 AI 词剔除版产品相似度同时使用时，Top5 结果仍显著；
非 GenAI 互动平台 pseudo-event 不能复制该结果；
投资者 GenAI 问题触发样本仍支持主方向。
```

当前还不能过度声称：

```text
不能说“GenAI 披露导致竞品价值下降”；
更稳的说法是“市场把具体化 GenAI 披露解读为可信竞争威胁信号”。

不能把同伴披露扩散当主 Y；
它只能作为机制 / 后续反应表。

不能把交易活跃度当主 Y；
它只能作为辅助市场反应证据。

不能把机制写成纯粹 business stealing；
focal CAR sign 分解没有显示“焦点公司涨、竞品跌”的清晰模式。

不能忽略 pre-window concern；
text-history AIActivePeer 存在显著 pre-window pattern，
因此主表或稳健性表必须加入 pre-window peer CAR 控制。
```

2026-05-25 已把三张成稿级表的试跑版补完：

```text
1. 主表重跑版已完成：
   Top5 / CAR[0,+1] / announcement clean / strong FE /
   event × peer firm two-way clustering / pre-window CAR controls。
   text-history、ext_any、ext_plus_history 均保留显著。

2. Specificity validation 表已完成第一版：
   控制 length、AI keyword intensity、source attention、numeric/component proxy 后，
   主方向和量级保留；ext_any 口径最稳。

3. Product-market proximity gradient 表已完成：
   Top1-3、Top4-5、Top6-10、low-similarity、random peers，
   结果主要集中在 Top1-3；low-similarity 和 random peers 不显著。

下一步不是再找新主 Y，而是把这些表整理成论文主表和附录表。
```

## 当前主线 v6

当前不再把“竞品是否跟进 GenAI 披露”作为主 Y。这个设计的 X 和 Y 都来自互动平台 / 调研问答文本，距离太近，最多适合作为机制。

最新主线调整为：

```text
Main question:
    一家上市公司披露 GenAI / 大模型 / AIGC 信息后，
    资本市场是否会重新评估其产品市场竞品？

Main Y:
    竞品短窗资本市场反应
    signed PeerCAR[-1,+1] / PeerCAR[0,+1]
    abnormal turnover / abnormal volume

Mechanism Y:
    竞品随后是否在互动平台 / 调研问答 / 公告中跟进 GenAI 披露

Validation Y:
    竞品后续 CAC 生成式 AI 服务备案 / 深度合成算法备案
```

当前入口文档：

```text
docs/empirical_runs/53_v6_final_review_checks_20260525.md
docs/empirical_runs/50_v6_external_ai_active_on_ai_stripped_similarity_20260524.md
docs/empirical_runs/52_v6_identification_strengthening_checks_20260524.md
docs/empirical_runs/51_v6_peer_firm_fe_identification_check_20260524.md
docs/empirical_runs/49_v6_external_ai_active_peer_checks_20260524.md
docs/empirical_runs/48_v6_announcement_clean_random_placebo_20260524.md
docs/empirical_runs/47_v6_ai_stripped_similarity_checks_20260524.md
docs/empirical_runs/46_v6_announcement_clean_and_trading_response_20260524.md
docs/current/41_v6_market_reaction_main_peer_diffusion_mechanism_20260523.md
```

## 核心研究设计

### 观察单元

```text
focal GenAI disclosure event i,t × product-market peer firm j
```

### 主 X

主解释结构是：

```text
GenAI_Disclosure_Event_i,t
× ProductSimilarity_i,j
× AIActivePeer_j,t-1
```

其中：

- `GenAI_Disclosure_Event_i,t`: 焦点公司在公开投资者沟通中的 GenAI 披露；
- `ProductSimilarity_i,j`: 焦点公司与竞品的产品市场相似度；
- `AIActivePeer_j,t-1`: 竞品在事件前是否已经处于 AI / GenAI 竞争空间。

`Specificity_i,t` 仍然保留，但不再单独承担主设计：

```text
Specificity_i,t
× ProductSimilarity_i,j
× AIActivePeer_j,t-1
```

它的作用是检验“披露越具体，竞争性重估越强”，而不是把论文写成“文本具体性预测另一个文本事件”。

### 主 Y

主 Y 必须外部于披露文本系统：

```text
PeerCAR[-1,+1]
PeerCAR[0,+1]
Peer abnormal turnover
Peer abnormal volume
```

推荐主表先用 signed CAR，而不是 `|CAR|`：

```text
如果机制是竞争威胁，方向应当是 AI-active 近邻竞品出现更负面的重估；
如果只看 |CAR|，会把竞争性重估和一般信息含量混在一起。
```

## 当前识别与估计方式

当前不是 IV，也不是标准 DID。更准确地说，这是一个短窗事件研究下的横截面信息揭示设计：

```text
PeerCAR_{e,j,[0,+1]}
  = beta_1 AIActivePeer_{j,t-5}
  + beta_2 Specificity_e × AIActivePeer_{j,t-5}
  + event FE_e
  + peer industry × week FE
  + peer pre-window CAR controls
  + error_{e,j}
```

其中 `e` 是焦点公司首次 GenAI 披露事件，`j` 是其产品市场竞品。Top5 / Top10 产品相似度主要用于定义竞品样本，而不是在主回归中继续放一个连续相似度项。

估计方式：

```text
absorbed OLS
Y 和 X 先按固定效应去均值
再用 OLS 估计
标准误按 event_id × peer_code 双向聚类
```

`event FE` 吸收所有焦点事件层面的共同冲击，包括焦点公司当日信息、披露具体性本身、市场对该事件的平均反应。因此主系数不是在比较“高具体性事件的竞品平均跌不跌”，而是在比较：

```text
同一个焦点事件下，
AI-active peer 与 non-AI-active peer 的 CAR 差异；
并且这个差异是否随着焦点披露 Specificity 更高而更负。
```

加入 `peer industry × week FE` 后，进一步吸收同一周同一竞品行业的市场波动。最新又补了一版 `peer firm FE`，用来检验是否完全由某些竞品公司固定特征驱动；结果见：

```text
docs/empirical_runs/51_v6_peer_firm_fe_identification_check_20260524.md
```

识别假设必须保守表述：

```text
短窗内，在剔除焦点公司与竞品的重大/定期/业绩/风险类公告后，
没有其他与 Specificity × AIActivePeer 同步变化的竞品层面未观测冲击；
Top5 产品市场近邻确实代表竞争替代关系；
AIActivePeer 使用事件前可观察信息，避免 look-ahead。
```

因此论文不能写成“具体披露因果导致竞品下跌”。更稳的写法是：

```text
资本市场将具体化 GenAI 披露解读为可信竞争威胁信号，
并对事前处于 AI 竞争空间的产品市场近邻进行更负面的相对重估。
```

## 机制：产品市场同伴披露扩散

`focal GenAI disclosure -> rival GenAI disclosure` 现在降级为机制表。

机制问题：

```text
焦点公司 GenAI 披露后，
产品市场更接近的竞品是否更可能在 60 / 90 / 180 天内首次跟进 GenAI 披露？
```

早期 CSMAR smoke test 支持“同伴披露扩散”这个描述性现象：

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
30 / 60 / 90 / 180d 均不显著
```

但 2026-05-25 的更严格版本加入 focal-event FE 与 peer 事前 365 天 GenAI 披露频率控制后，`Specificity × Similarity` 不显著：

```text
Top5:
60d p = 0.935
90d p = 0.622
180d p = 0.886

Top10:
60d p = 0.317
90d p = 0.657
180d p = 0.555
```

解释边界：

```text
只能说早期描述性结果提示可能存在同伴披露扩散；
更严格口径下并不能证明“具体披露触发竞品跟进披露”。
因此它不能承担核心机制，只能作为补充描述或后续探索。
```

对应文档：

```text
docs/empirical_runs/40_csmar_peer_diffusion_main_effect_20260523.md
```

## v6 主结果初步试跑

已用完整 CSMAR 事件库跑了一版市场调整 CAR smoke test：

```text
docs/empirical_runs/42_v6_csmar_peer_market_reaction_smoke_20260523.md
results/v6_csmar_peer_market_reaction_smoke_20260523
```

同时已重跑一版更适合作为主表的简化主效应：

```text
docs/empirical_runs/43_v6_simple_main_effect_20260523.md
results/v6_simple_main_effect_20260523
```

当前读法：

```text
简化主效应：
    ProductSimilarity 用于定义 Top5 / Top10 peer sample；
    主交互只保留 Specificity × AIActivePeer。

每家公司首次 GenAI 披露样本，Top5 clean:
    Top5 clean CAR[0,+1],
    Specificity_z × AIActivePeer
    coef = -0.001669, p = 0.024

    Top5 clean CAR[-1,+1],
    Specificity_z × AIActivePeer
    coef = -0.002659, p = 0.014

    Top10 clean CAR[-1,+1],
    Specificity_z × AIActivePeer
    coef = -0.002113, p = 0.041
```

这说明 v6 主线目前有初步信号，但还不是正式结果。最合理的暂定表述是：

```text
焦点公司首次 GenAI 披露越具体，
产品市场近邻中事前 AI-active 的竞品，
短窗 CAR 越负。
```

下一步必须用 market-model CAR、低相似度 / 随机 peer placebo、外部 AIActivePeer 和竞品同日公告清洗来复核。

2026-05-24 已补第一轮复核：

```text
docs/empirical_runs/44_v6_market_model_and_placebo_20260524.md
results/v6_supplement_market_model_placebo_20260524
```

关键结果：

```text
market-model CAR，首次披露样本，true Top5 peers:

CAR[0,+1]:
Specificity_z × AIActivePeer
coef = -0.001825, p = 0.0166

CAR[-1,+1]:
Specificity_z × AIActivePeer
coef = -0.001921, p = 0.0496

低相似度同行 placebo:
CAR[0,+1] p = 0.828
CAR[-1,+1] p = 0.750

true Top5 vs 低相似度同行差异:
CAR[0,+1] p = 0.038
CAR[-1,+1] p = 0.037
```

目前最需要继续处理的是随机同行 placebo：`CAR[-1,+1]` 有边际负向，说明还需要 industry-week FE、多次随机抽样和同日公告清洗。

2026-05-24 已继续完成主效应完整复核：

```text
docs/empirical_runs/45_v6_main_effect_full_checks_20260524.md
results/v6_main_effect_full_checks_20260524
```

关键结果：

```text
market-model CAR，首次披露样本，true Top5 peers:

CAR[0,+1], event FE:
Specificity_z × AIActivePeer
coef = -0.001825, p = 0.0166

CAR[0,+1], event FE + peer industry-week FE:
Specificity_z × AIActivePeer
coef = -0.001513, p = 0.0839

低相似度同行 placebo:
CAR[0,+1] p = 0.828
CAR[-1,+1] p = 0.750

100 次随机同业 placebo:
CAR[0,+1] 下没有一次随机抽样比 true Top5 更负；
CAR[-1,+1] 下 event FE 没有一次更负，加入 peer industry-week FE 后只有 1% 更负。
```

当前更稳的主表述应收窄为：

```text
焦点公司首次 GenAI 披露越具体，
事前已经 AI-active 的 Top5 产品市场近邻竞品，
在 [0,+1] 窗口出现更负的 market-model CAR。
```

2026-05-24 已补公告污染清洗与交易活跃度检验：

```text
docs/empirical_runs/46_v6_announcement_clean_and_trading_response_20260524.md
results/v6_announcement_clean_checks_20260524
results/v6_trading_response_checks_20260524
```

公告补数来自 CSMAR 公告基本信息表、公告证券关联表、公告分类关联表，已整理为：

```text
announcement_stock_day_flags_2023_2026.csv.gz
覆盖 2023-01-01 至 2026-05-25
A 股证券关联行数 2,415,820
股票-日期公告标记 695,403 行
```

公告清洗后的关键结果：

```text
Top5 first focal event, market-model CAR[0,+1],
剔除焦点公司与竞品的重大/定期/业绩/风险类公告后：

event FE:
Specificity_z × AIActivePeer
coef = -0.002298, p = 0.008

event FE + peer industry-week FE:
Specificity_z × AIActivePeer
coef = -0.002298, p = 0.020

低相似度同行 placebo:
coef ≈ 0, p > 0.90
```

Top5 vs 低相似度同行差异检验：

```text
Specificity_z × AIActivePeer × TrueTop5

同时剔除焦点与竞品清洗公告，event FE:
CAR[0,+1] coef = -0.001718, p = 0.018
CAR[-1,+1] coef = -0.002503, p = 0.009

但加入 peer industry-week FE 后差异项不再显著。
```

交易活跃度补充 Y：

```text
异常成交额 / 异常成交量方向也偏负；
Top5 清洗样本中 abnormal log trading value [0,+1],
event FE + peer industry-week FE:
coef = -0.0397, p = 0.027

但单次随机同业 placebo 在清洗样本中出现正向异常成交额，
因此交易活跃度只作为辅助事实，不升级为主 Y。
```

当前最稳主表述进一步收窄为：

```text
焦点公司首次 GenAI 披露越具体，
事前已经 AI-active 的 Top5 产品市场近邻竞品，
在 [0,+1] 窗口出现更负的 market-model CAR；
该结果在剔除焦点公司与竞品的重大/定期/业绩/风险类公告后仍成立，
低相似度同行没有类似反应。
```

`CAR[-1,+1]` 可以作为补充窗口，不宜作为唯一 headline。

2026-05-24 又补了 AI 词剔除版产品相似度检验：

```text
docs/empirical_runs/47_v6_ai_stripped_similarity_checks_20260524.md
results/v6_ai_stripped_similarity_checks_20260524
```

处理逻辑：

```text
从主营业务 / 产品描述文本中剔除：
AI / AIGC / GenAI / ChatGPT / DeepSeek / 大模型 / 生成式人工智能
机器学习 / 深度学习 / 自然语言处理 / 算法 / 智能 / 智慧 等词，
然后重新计算产品市场相似度与 Top5 / Top10 peer network。
```

关键结果：

```text
Top5 first focal event, AI-word-stripped product similarity,
同时剔除焦点与竞品清洗公告，CAR[0,+1]:

event FE:
Specificity_z × AIActivePeer
coef = -0.002124, p = 0.011

event FE + peer industry-week FE:
Specificity_z × AIActivePeer
coef = -0.002041, p = 0.033
```

与原始 peer network 的重合度：

```text
Top5 mean overlap = 0.956, median overlap = 1.000
Top10 mean overlap = 0.959, median overlap = 1.000
```

这说明当前主结果不是简单由产品描述中共同出现 AI 词造成的。

2026-05-24 进一步补了公告清洗版 100 次随机同业 placebo：

```text
docs/empirical_runs/48_v6_announcement_clean_random_placebo_20260524.md
results/v6_announcement_clean_random_placebo_20260524
```

关键结果：

```text
真实 Top5, drop either cleaning announcement, CAR[0,+1]:
coef = -0.002298

100 次同一细行业随机非 Top10 peer:
random mean coef = -0.000050
random median coef = -0.000055
random 5th percentile = -0.001483
share random <= true Top5 = 0.00
```

这说明同一细行业随机公司不能复制真实 Top5 产品市场近邻的负向强度。

2026-05-24 又补了外部 pre-event AIActivePeer 第一轮：

```text
docs/empirical_runs/49_v6_external_ai_active_peer_checks_20260524.md
results/v6_external_ai_active_20260524
results/v6_external_ai_active_checks_20260524
```

外部证据规模：

```text
CAC A 股 lower-bound 匹配：106 家
AI 专利标题匹配：101 家
GenAI 专利标题匹配：28 家
broad AI 招聘：2,814 家
GenAI 招聘：1,657 家
post-ChatGPT 历史 GenAI 披露：2,771 家
```

纯外部主口径：

```text
ext_any = prior CAC
       OR prior broad-AI patent grant
       OR >=1 broad-AI job posting in prior 365 days
```

关键结果：

```text
Top5, drop either cleaning announcement, CAR[0,+1]:
event FE coef = -0.001897, p = 0.028
event FE + peer industry-week FE coef = -0.001800, p = 0.058

Top10, drop either cleaning announcement, CAR[0,+1]:
event FE coef = -0.001654, p = 0.004
event FE + peer industry-week FE coef = -0.001493, p = 0.014

低相似度同行 placebo:
coef ≈ 0, p = 0.888
```

读法：

```text
纯外部 ext_any 没有推翻主结果；
它支持方向和经济量级，但 Top5 强 FE 下是边际显著。
加入历史披露文本的 ext_plus_history 更稳，但只能作为扩展口径。
```

2026-05-24 进一步补了外部 AIActivePeer × AI 词剔除产品相似度联合检验：

```text
docs/empirical_runs/50_v6_external_ai_active_on_ai_stripped_similarity_20260524.md
results/v6_external_ai_active_ai_stripped_checks_20260524
```

关键结果：

```text
AI-word-stripped Top5, ext_any,
drop either cleaning announcement, CAR[0,+1]:

event FE coef = -0.002118, p = 0.011
event FE + peer industry-week FE coef = -0.002321, p = 0.011

AI-word-stripped Top10, ext_any,
event FE coef = -0.001525, p = 0.009
event FE + peer industry-week FE coef = -0.001343, p = 0.029
```

这说明两个关键防御可以同时成立：

```text
不是 AI 词共同出现定义竞品；
也不是历史披露文本单独定义 AI-active peer。
```

2026-05-24 又补了 peer firm FE 识别检验：

```text
docs/empirical_runs/51_v6_peer_firm_fe_identification_check_20260524.md
results/v6_peer_firm_fe_checks_20260524
```

关键结果：

```text
Current text-history AIActivePeer, original Top5,
drop either cleaning announcement, CAR[0,+1]:

event FE + peer firm FE:
coef = -0.002152, p = 0.058

event FE + peer firm FE + peer industry-week FE:
coef = -0.002915, p = 0.053

Current text-history AIActivePeer, original Top10:
event FE + peer firm FE:
coef = -0.001800, p = 0.009

event FE + peer firm FE + peer industry-week FE:
coef = -0.001922, p = 0.012

low-similarity placebo:
coef = -0.000261, p = 0.683
```

纯外部 `ext_any` 在 peer firm FE 下变弱：

```text
Original Top5:
event FE + peer firm FE p = 0.157
event FE + peer firm FE + peer industry-week FE p = 0.847

AI-word-stripped Top5:
event FE + peer firm FE p = 0.230
event FE + peer firm FE + peer industry-week FE p = 0.449
```

因此当前经验判断是：

```text
主表仍以 text-history AIActivePeer 为核心；
外部 ext_any 作为验证层，说明方向不是纯文本同源造成；
peer firm FE 作为更严检验，结果支持主口径和 Top10，但不支持把 ext_any 直接升级为 headline。
```

2026-05-24 继续补了五类识别增强检验：

```text
docs/empirical_runs/52_v6_identification_strengthening_checks_20260524.md
results/v6_identification_strengthening_20260524
```

正式 DDD 结果方向正确，但强度不均匀：

```text
True Top5 vs random Top5, current text-history AIActive:
event FE coef = -0.002315, p = 0.027
event FE + peer industry-week FE coef = -0.001904, p = 0.094

True Top5 vs low-similarity Top5, current text-history AIActive:
event FE p = 0.132
event FE + peer industry-week FE p = 0.300

ext_plus_history 口径下，DDD 对 low/random peers 多数为 5%-10% 显著或边际显著。
```

pre-window placebo 暴露了一个真实风险：

```text
true Top5, current text-history AIActive:
CAR[-10,-2] p = 0.013 / 0.043
CAR[-20,-2] p = 0.009 / 0.003
```

但加入 pre-window peer CAR 控制后，事件窗主结果仍保留：

```text
current text-history AIActive,
control CAR[-10,-2] and CAR[-20,-2],
event FE + peer industry-week FE:
coef = -0.002025, p = 0.036

external ext_any,
control CAR[-10,-2] and CAR[-20,-2],
event FE + peer industry-week FE:
coef = -0.002109, p = 0.024

ext_plus_history,
control CAR[-10,-2] and CAR[-20,-2],
event FE + peer industry-week FE:
coef = -0.002265, p = 0.011
```

focal CAR sign 分解不支持简单 business stealing：

```text
focal CAR positive:
p = 0.144 / 0.230

focal CAR non-positive:
p = 0.024 / 0.048

interaction with focal positive:
p = 0.694 / 0.652
```

投资者问题触发样本支持主方向：

```text
Question contains GenAI terms:
event FE coef = -0.001837, p = 0.058
event FE + peer industry-week FE coef = -0.002123, p = 0.050

IIP quick question-triggered sample:
event FE coef = -0.002384, p = 0.056
event FE + peer industry-week FE coef = -0.002411, p = 0.091
```

Non-GenAI IIP pseudo-event placebo 不复制主结果：

```text
2,652 pseudo focal events
14,790 clean event-peer rows

event FE coef = +0.002349, p = 0.358
event FE + peer industry-week FE coef = +0.002284, p = 0.372
```

五类补强后的总体判断：

```text
题目仍然活着，但需要保守写。

可说：
    具体化 GenAI 披露被市场解读为 competitive-risk signal；
    负向重估集中在事前 AI-active 的产品市场近邻；
    该模式不能由普通 non-GenAI 互动文本、随机 peer、低相似度 peer 完整复制；
    并且在控制 pre-window peer CAR 后仍保留。

不可说：
    这是强因果；
    这是明确 business stealing；
    这是完全没有 pre-trend concern 的干净事件研究。
```

## 已完成的数据扩展

CSMAR 下载资料已整理到：

```text
/Users/mac/computerscience/第三方资料/04_项目专用资料/T05_GAI_financial_disclosure_market_reaction/csmar_downloads_20260523
```

完整 GenAI 事件库已经建好：

```text
results/csmar_genai_event_library_20260523
```

事件库规模：

```text
IIP:
    raw rows = 2,460,811
    answer-level GenAI events = 25,544
    firm-day GenAI events = 15,460
    firms = 2,587

IR_QA:
    raw rows = 1,773,908
    answer-level GenAI events = 15,147
    firm-day GenAI events = 8,268
    firms = 1,274

Combined:
    answer-level GenAI events = 40,691
    firm-day GenAI events = 23,454
    firms = 2,800
    post-2023 firm-day events = 22,701
```

对应脚本和记录：

```text
scripts/build_csmar_genai_event_library_20260523.py
docs/empirical_runs/38_csmar_genai_event_library_smoke_20260523.md
```

## 已降级路线

### v5.1：IIP -> IIP / CAC response

v5.1 的原始设想是：

```text
焦点公司 IIP GenAI 披露具体性
× 产品市场相似度
-> 竞品 30/60/90 天内是否跟进 IIP GenAI 披露
```

现在判断：

```text
同伴披露扩散可以做机制；
不适合作为主 Y。
```

原因：

- X 和 Y 都是 GenAI 披露文本，经济距离太近；
- 同源平台和同一分类器容易被质疑为共同方法偏误；
- 最新 CSMAR 试跑中，`Specificity × Similarity` 对竞品披露响应不显著；
- 真正有信号的是产品相似度的同伴扩散主效应，更像机制而不是终点。

对应文档：

```text
docs/current/37_v5_1_layered_iip_cac_disclosure_response_smoke_20260523.md
docs/empirical_runs/39_csmar_v5_1_response_smoke_20260523.md
```

### v5：rival hiring

v5 想把主 Y 改成竞品后续 AI-skilled hiring。现在仍不建议作为当前主线：

```text
招聘数据覆盖 2014-01-07 至 2026-03-10，约 899.6 万条；
但招聘是慢变量，难解释为焦点披露事件后的短期竞品响应；
更适合构造 pre-event AIActivePeer / prior AI capability。
```

对应文档：

```text
docs/current/34_v5_long_term_rival_ai_investment_design_20260522.md
docs/current/36_recruitment_data_and_v5_y_risk_audit_20260522.md
```

### v4：AI-active peer CAR

v4 是当前 v6 的直接前身：

```text
一家公司的 GenAI 披露越具体，
资本市场是否会对“产品越相似、且已经 AI-active 的竞品”作出更负面的短窗重估？
```

早期证据：

```text
Top5 clean CAR[-1,+1],
Specificity × ProductSimilarity × AIActivePeer:
coef = -0.0103, p = 0.005

加 peer controls:
coef = -0.0095, p = 0.011
```

更严格双向聚类后：

```text
Top5 clean CAR[-1,+1],
AIActivePeer = t-5 preobservable public or annual evidence:
coef = -0.0104, p = 0.055 without controls
coef = -0.0094, p = 0.084 with controls

Top10 不再稳健。
```

因此 v6 不是放弃 v4，而是用完整 CSMAR 事件库重新跑 v4 主问题，并把披露扩散放到机制表。

对应文档：

```text
docs/current/31_v4_experimental_design_ai_active_peer_20260522.md
docs/current/32_v4_go_no_go_diagnostics_20260522.md
```

## 下一步

v6 主市场反应已经通过第一轮公告污染清洗。下一步不是回退，也不是扩展新 Y，而是继续把主效应打硬：

```text
完整 CSMAR GenAI 事件库
× 产品市场 Top5 / Top10 竞品
× 日收益 / 成交量数据
-> peer CAR / abnormal turnover
```

最低 go/no-go 已部分通过：

1. AI-active 近邻竞品的 signed CAR 方向合理；
2. 双向聚类 by focal event and peer firm 后仍有信号；
3. Top5 经济含义更清楚，Top10 方向基本一致；
4. 低相似度 peer placebo 不成立；
5. 同伴披露扩散机制表方向一致。
6. 剔除焦点公司与竞品重大/定期/业绩/风险类公告后，Top5 `CAR[0,+1]` 仍成立。
7. 剔除产品描述中的 AI / 大模型 / 智能等通用词后，Top5 `CAR[0,+1]` 仍成立。
8. 公告清洗版 100 次随机同业 placebo 无法复制真实 Top5 的负向强度。
9. 外部 `AIActivePeer = CAC + AI专利授权 + 过去365天AI招聘` 支持方向和 placebo，但 Top5 强 FE 下为边际显著。
10. 外部 `AIActivePeer` 与 AI 词剔除版产品相似度同时使用时，Top5 `CAR[0,+1]` 仍显著。

下一轮优先做两件事：

1. **精修外部 `AIActivePeer`**
   现在已有第一版外部口径，但还应改进 CAC 公司匹配、AI 专利分类和招聘关键词人工复核。

2. **准备主表 / 稳健性表结构**
   主表用历史披露口径，外部 `ext_any` 放验证表；不要把 p=0.058 包装成完全强稳健。

已经完成、暂不再作为下一步重点：

```text
竞品自身同日重大公告清洗：已完成；
AI 词剔除版 ProductSimilarity：已完成；
公告清洗版 100 次随机同业 placebo：已完成；
外部 pre-event AIActivePeer 第一版：已完成；
外部 AIActivePeer × AI 词剔除版产品相似度：已完成；
abnormal trading value / shares：已完成，作为补充 Y；
同伴披露扩散：已降级为机制表。
```

如果外部口径精修后 `CAR[0,+1]` 的 Top5 结果仍能保留，这条主线可以进入正式论文框架。
