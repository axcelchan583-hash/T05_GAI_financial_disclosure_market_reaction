# v4 控制变量与 Peer AI 能力异质性试跑

日期：2026-05-22

## 目的

在正式 CSMAR 事件研究版本基础上，同时试两件事：

1. 在主效应中加入 peer 事前股票特征控制变量；
2. 检验 `Specificity × ProductSimilarity × LowPeerAICapability` 三重交互。

## 脚本与输出

脚本：

```text
scripts/run_v4_controls_and_ai_capability_heterogeneity.py
```

输出目录：

```text
results/v4_peer_spillover_controls_heterogeneity/
```

主要输出：

```text
v4_controls_regression_all.csv
v4_ai_capability_heterogeneity_all.csv
v4_controls_heterogeneity_diagnostics.csv
v4_peer_event_controls_heterogeneity_top3.csv
v4_peer_event_controls_heterogeneity_top5.csv
```

## 控制变量设置

在 `Event FE` 下，焦点公司层面和事件层面变量会被吸收。因此本轮只加入同一事件内会随 peer 变化的控制变量：

```text
z_peer_beta
z_pre_mom_60
z_pre_vol_120
z_pre_absret_60
is_chinext_or_star
z_peer_rank
```

含义：

- `z_peer_beta`：市场模型估计窗口 beta；
- `z_pre_mom_60`：事件前 60 个交易日累计收益；
- `z_pre_vol_120`：事件前 120 个交易日收益波动；
- `z_pre_absret_60`：事件前 60 个交易日平均绝对收益；
- `is_chinext_or_star`：创业板 / 科创板；
- `z_peer_rank`：产品市场相似度排名。

控制变量完整率：

```text
Top 3: 100%
Top 5: 100%
```

## 控制变量结果

### Top 5 主要结果

| Sample | Y | Specification | coef | p-value | nobs |
|---|---|---|---:|---:|---:|
| Clean | CAR[0,+1] | baseline | -0.0116 | 0.120 | 1,755 |
| Clean | CAR[0,+1] | + controls | -0.0116 | 0.118 | 1,755 |
| Raw | CAR[0,+1] | baseline | -0.0186 | 0.120 | 1,906 |
| Raw | CAR[0,+1] | + controls | -0.0186 | 0.119 | 1,906 |

### 解释

控制变量几乎不改变主效应。

这说明当前负向方向不是简单由 peer 的 beta、事前动量、波动率、绝对收益、创业板/科创板属性或 peer rank 驱动。

但是控制变量也没有把平均主效应推到常规显著。

## Peer FE 结果

加入 `Peer FE` 后，主效应更弱：

```text
Top5 raw CAR[-1,+1], controls + peer FE: p = 0.260
Top5 raw CAR[0,+1], controls + peer FE: p = 0.266
Top5 clean CAR[0,+1], controls + peer FE: p = 0.285
```

这不意外。当前样本事件期很短，peer FE 会吃掉大量跨 peer 稳定差异，而我们的 product-similarity 变量本身也主要是 peer-pair 层面的相对关系。现阶段不应把 Peer FE 当作主规格。

## AI 能力异质性设置

本轮先用两个快速代理。

### Strict 口径

```text
LowPeerAICapability_Strict = 1
```

如果 peer 在事件日前没有自己的 GenAI 互动平台回复或正式 GenAI 公告。

覆盖：

```text
Top 3 low strict share: 82.5%
Top 5 low strict share: 82.3%
```

这个口径太严格，导致绝大多数 peer 都被归为 low capability。

### Broad 口径

```text
LowPeerAICapability_Broad = 1
```

如果 peer 在事件日前既没有自己的 GenAI 公开事件，也没有 2024 年报 GenAI 证据。

覆盖：

```text
Top 3 low broad share: 30.7%
Top 5 low broad share: 31.3%
```

这个口径更有区分度，但它严格说不是“AI 能力”，更像“是否已经暴露在 GenAI 叙事 / AI 赛道中”。

## 异质性结果

### Strict 口径

Strict 口径没有跑出有意义的三重交互。

最接近的结果是：

```text
Top5 clean AR[0]:
coef of x_specsim_low_strict = 0.0027
p = 0.260
```

结论：strict 口径暂时不用作为主异质性。

### Broad 口径

Broad 口径有一个值得注意但需要谨慎解释的结果：

```text
Top5 clean CAR[-1,+1]:
coef of x_specsim_low_broad = 0.0103
p = 0.050
```

线性组合：

```text
High AI evidence peer effect:
coef = -0.0132
p = 0.225

Low broad AI capability peer effect:
coef = -0.0030
p = 0.733
```

含义：

这个结果不是“低 AI 能力 peer 更受冲击”。相反，它更像是：

```text
已有 GenAI 年报/公开证据的 peer，对焦点公司的具体 GenAI 披露更敏感；
没有 GenAI 痕迹的 peer 反应较弱。
```

这可能说明市场并不是在惩罚“完全没 AI 能力”的同业，而是在 AI 相关赛道内部重新评估竞争威胁。

## 当前判断

### 1. 控制变量方向

控制变量值得保留，但它不是突破口。

它的作用是防御：

```text
结果不是由 beta、动量、波动、板块或 peer rank 驱动。
```

不是进攻：

```text
控制变量不会把平均主效应变成显著。
```

### 2. AI 能力异质性方向

`LowPeerAICapability` 这个名字目前不够准确。

如果用 strict 口径，样本区分度太弱；如果用 broad 口径，结果方向更像：

```text
Peer AI exposure / AI-active peer
```

而不是：

```text
Peer AI capability weakness
```

也就是说，下一版不应强行写“低 AI 能力同业更受威胁”。更稳的改法是：

```text
GenAI disclosure spillovers are concentrated among AI-exposed product-market peers.
```

或：

```text
The competitive-threat channel is stronger within the AI-active product-market space.
```

## 下一步建议

不要继续只磨这些快速代理。下一步应做两件更有价值的事：

1. 把 peer AI capability 做成真正的行为变量：
   - AI hiring share；
   - AI / GenAI 专利；
   - CAC 备案；
   - 正式产品或模型上线。

2. 把事件本身分成更强的类型：
   - product-oriented GenAI disclosure；
   - process / internal-efficiency disclosure；
   - concrete product / model / customer / contract / deployment detail。

当前最值得跑的下一张表不是继续加控制，而是：

```text
Specificity × ProductSimilarity × AI-active peer
```

其中 `AI-active peer` 先用年报/公开事件代理，后续用招聘、专利、CAC 备案替换。
