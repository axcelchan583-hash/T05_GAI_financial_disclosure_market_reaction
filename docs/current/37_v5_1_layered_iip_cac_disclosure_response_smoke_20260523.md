# v5.1 A+B 分层设计与最小试跑记录

日期：2026-05-23

> 2026-05-23 更新：完整 CSMAR 事件库试跑后，v5.1 不再作为当前主线。`IIP GenAI disclosure -> rival IIP GenAI disclosure` 的 X 和 Y 同源且距离过近，应降级为机制或补充表。当前主线见 `docs/current/41_v6_market_reaction_main_peer_diffusion_mechanism_20260523.md`。

## 1. 当时判断（已被 v6 修正）

Claude 网页版提出的 A+B 分层框架在当时被视为最值得继续的方向：

```text
Design A:
    焦点公司 IIP GenAI 披露具体性
    × 产品市场相似度
    -> 竞品 30/60/90 天内是否跟进 IIP GenAI 披露

Design B:
    同一焦点事件
    × 产品市场相似度
    -> 竞品 180/365/540 天内是否进入 CAC 生成式 AI 服务备案 / 登记
```

但本次试跑后必须加一条硬边界：

```text
当前本地 IIP 数据不能支撑 v5.1 正式 go/no-go。
它只能支撑接口可行性和短样本 smoke test。
```

原因是现有互动平台合并样本主要集中在 2026 年：

- `genai_interactive_qa_answered_combined_2023_2026.csv`: 990 条已回答问答；
- 回答日期：2026-02-19 至 2026-05-19；
- 当前严格 firm-day 事件：402 个；
- 严格事件日期：2026-02-24 至 2026-05-19。

这意味着 90 天响应窗口完全无法完整观察，30/60 天也只是 2026 年短窗口。

## 2. 公共接口补爬探测

本次重新探测了原始脚本使用的两个接口。

### 深交所互动易

接口可访问，但关键词搜索明显偏近期结果。以 page size = 20 探测：

| keyword | total | pages | last-page date pattern |
|---|---:|---:|---|
| `大模型` | 1128 | 57 | 最后一页仍主要在 2026-01 至 2026-02 |
| `AI大模型` | 772 | 39 | 最后一页仍主要在 2026-01 至 2026-02 |
| `人工智能` | 940 | 47 | 最后一页仍主要在 2026-01 至 2026-02 |
| `AIGC` | 85 | 5 | 全部集中在 2026 |
| `DeepSeek` | 249 | 13 | 全部集中在 2026 |
| `生成式人工智能` | 14 | 1 | 全部集中在 2026 |

结论：

```text
现有互动易关键词搜索接口不能自然翻出 2023-2025 的历史 GenAI 问答。
要么需要换官方历史接口 / 按公司抓取，要么需要从 CSMAR/Wind 导出互动平台全量数据。
```

### 上证 e 互动

接口可访问，且支持 `sdate` / `edate` 参数。但本次关键词计数显示：

| keyword | 2023 | 2024 | 2025 | 2026-01-01 至 2026-05-22 |
|---|---:|---:|---:|---:|
| `ChatGPT` | 0 | 0 | 0 | 1 |
| `大模型` | 0 | 0 | 0 | 127 |
| `AIGC` | 0 | 0 | 0 | 13 |
| `DeepSeek` | 0 | 0 | 0 | 37 |

结论：

```text
上证 e 互动可以补，但按当前关键词与回答日期口径，历史 GenAI 问答非常稀疏。
```

## 3. Design A smoke test：IIP -> IIP 跟进披露

使用现有 v4 Top10 产品市场竞品面板：

```text
input:
    results/v4_peer_spillover_x_pilot/v4_peer_event_x_top10.csv
    results/plan_a_irqa_multichannel_event_study/plan_a_irqa_strict_firm_day_events.csv

output:
    results/v5_1_disclosure_response_smoke/
```

### 3.1 IIP-only 事件库

Y 定义为竞品在焦点事件后 30/60/90 天内是否出现严格 IIP GenAI firm-day 事件。

| window | sample | full-window obs | response events | response rate |
|---:|---|---:|---:|---:|
| 30 | Top10 | 2500 | 233 | 9.32% |
| 30 | Top5 | 1250 | 120 | 9.60% |
| 60 | Top10 | 1550 | 198 | 12.77% |
| 60 | Top5 | 775 | 109 | 14.06% |
| 90 | Top10 | 0 | 0 | NA |
| 90 | Top5 | 0 | 0 | NA |

核心交互 `Specificity × Similarity` 的 event FE 结果：

| window | sample | coef | p-value |
|---:|---|---:|---:|
| 30 | Top10 | -0.0107 | 0.286 |
| 30 | Top5 | -0.0025 | 0.908 |
| 60 | Top10 | -0.0001 | 0.995 |
| 60 | Top5 | -0.0001 | 0.997 |

结论：

```text
现有 2026 IIP-only 样本没有出现 A 设计所需的正向 similarity-gradient 信号。
```

但这个结果不应作为最终否定，因为样本窗口太短，且没有 2023-2025 的历史 IIP 事件库。

### 3.2 IIP + 巨潮投资者关系活动记录作为竞品披露事件库

为了提高 Y 的覆盖，将巨潮 IR 活动记录中的 GenAI 命中也并入竞品披露事件库：

```text
combined event library:
    551 disclosure events
    274 firms
    2023-04-06 至 2026-05-19
```

响应率略有提高：

| window | sample | full-window obs | response events | response rate |
|---:|---|---:|---:|---:|
| 30 | Top10 | 2500 | 242 | 9.68% |
| 30 | Top5 | 1250 | 129 | 10.32% |
| 60 | Top10 | 1550 | 206 | 13.29% |
| 60 | Top5 | 775 | 116 | 14.97% |

但核心交互仍无信号：

| window | sample | coef | p-value |
|---:|---|---:|---:|
| 30 | Top10 | -0.0113 | 0.266 |
| 30 | Top5 | -0.0035 | 0.873 |
| 60 | Top10 | 0.0021 | 0.907 |
| 60 | Top5 | 0.0033 | 0.929 |

结论：

```text
巨潮 IR 作为 Y-side 补充能增加事件数，但不能替代完整 IIP 历史事件库。
```

## 4. Design B smoke test：IIP / IR -> CAC 备案

本地 CAC 表已经覆盖到 2026-04：

```text
data/interim/cac_genai_service_filing_records.csv

records: 1358
source batches: 2024-04 至 2026-04
filing date range: 2023-08-31 至 2026-04-30
unique filing entities: 1183
```

使用保守的 A 股简称包含匹配：

```text
matched CAC rows: 151
matched A-share firms: 106
first-event A-share firms: 106
```

这只是 lower-bound match。它会漏掉很多子公司、控股平台和集团主体，但误匹配风险较低。

### 4.1 焦点事件与相似竞品面板

焦点事件库合并：

- 巨潮 IR GenAI 活动记录；
- 正式公告 GenAI 事件；
- 当前 IIP 严格 firm-day 事件。

用于 B smoke test 的焦点事件：

```text
focal events: 450
event date range: 2023-04-10 至 2026-05-19
event-peer panel: 4500 rows
```

产品市场相似度临时用 `v4_company_product_text_latest.csv` 的业务文本重新计算 Top10。

### 4.2 CAC response 结果

完整窗口样本很小：

| window | full-window obs | response events | response rate | full-window focal events |
|---:|---:|---:|---:|---:|
| 180 | 280 | 6 | 2.14% | 28 |
| 365 | 220 | 9 | 4.09% | 22 |
| 540 | 190 | 12 | 6.32% | 19 |

回归中 `Specificity × Similarity` 有弱正向迹象，但不能解释为正式证据：

| window | coef on interaction | t-stat | p-value |
|---:|---:|---:|---:|
| 180 | 0.0264 | 1.63 | 0.102 |
| 365 | 0.0240 | 1.52 | 0.129 |
| 540 | 0.0150 | 0.79 | 0.427 |

注意：这里的 specificity 对巨潮 IR 焦点事件是占位口径，不是正式文本具体性。因此 B smoke test 只能说明：

```text
CAC 备案作为 cross-source corroboration 有一点可试空间；
但目前 full-window 样本太小，不能单独支撑论文。
```

## 5. 输出文件

本次试跑结果保存在：

```text
results/v5_1_disclosure_response_smoke/
```

主要文件：

- `v5_1_response_smoke_summary.csv`
- `v5_1_response_smoke_regressions.csv`
- `v5_1_response_smoke_panel_current_iip.csv`
- `v5_1_combined_disclosure_event_library_iip_cninfo_ir.csv`
- `v5_1_response_smoke_summary_iip_plus_cninfo_ir.csv`
- `v5_1_response_smoke_regressions_iip_plus_cninfo_ir.csv`
- `v5_1_response_smoke_panel_iip_plus_cninfo_ir.csv`
- `v5_1_cac_filing_a_share_name_matched_lower_bound.csv`
- `v5_1_cac_first_event_by_a_share_lower_bound.csv`
- `v5_1_focal_event_library_for_cac_smoke.csv`
- `v5_1_cac_response_smoke_panel_lower_bound_match.csv`
- `v5_1_cac_response_smoke_summary_lower_bound_match.csv`
- `v5_1_cac_response_smoke_regressions_lower_bound_match.csv`

## 6. Go / No-Go 判断

### 现在不能 go

不能用当前样本直接写 v5.1，原因很具体：

1. IIP 历史事件库缺 2023-2025；
2. 90 天响应窗口在当前 IIP 样本中完全不可观察；
3. A 端 `Specificity × Similarity` 在现有短样本里没有正向信号；
4. B 端 CAC 虽有弱正向迹象，但 full-window 响应事件只有 6-12 个。

### 但可以继续补数据

v5.1 没被否定。真正的下一步不是换模型，而是补事件库：

```text
优先级 1:
    获取 / 导出 2023-2025 互动易 + e互动全量问答数据。

优先级 2:
    重新构造焦点 GenAI IIP disclosure event library。

优先级 3:
    跑 Design A 的正式 smoke test:
        RivalResponse90 ~ Specificity × ProductSimilarity
        + focal-event FE
        + rival baseline GenAI posting rate

优先级 4:
    对 CAC 做人工主体匹配，把 lower-bound match 升级为 parent/subsidiary match。
```

### 最低继续标准

如果补齐 2023-2025 IIP 后，仍然出现：

```text
Specificity × ProductSimilarity 对 RivalResponse90 没有正向方向；
AI-word-stripped similarity 后结果消失；
低相似度 placebo 同样显著；
```

则 v5.1 应停止，不应用 Cox 或更多交互项硬救。

## 7. 当前最诚实表述

现阶段最稳的说法是：

```text
v5.1 的 A+B 设计在理论和文献锚点上成立；
本地数据已证明接口与 CAC 外部验证源可用；
但当前互动平台历史事件库不足，正式 go/no-go 需要先补 2023-2025 IIP 全量问答。
```
