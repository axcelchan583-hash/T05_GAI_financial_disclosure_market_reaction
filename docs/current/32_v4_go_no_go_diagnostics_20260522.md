# v4 Go/No-Go 诊断：两维聚类、严格 t-5 AI-active 与 Top10 扩展

日期：2026-05-22

## 1. 目的

Claude 研究模式的核心质疑是：

```text
当前论文贡献几乎全部压在
Specificity × ProductSimilarity × AIActivePeer
这个三重交互上。
```

因此本轮不继续解释原始 `p=0.005 / 0.011`，而是做 go/no-go 诊断：

1. 用更严格的聚类标准误重新估计主交互；
2. 把 `AIActivePeer` 改成事件日前可观测的 t-5 口径；
3. 计算 AI-active 组内总效应；
4. 扩到 Top10 产品市场 peer，看信号是否稳定。

## 2. 新增脚本与输出

新增脚本：

```text
scripts/run_v4_go_no_go_diagnostics.py
```

输出目录：

```text
results/v4_go_no_go_diagnostics/
```

主要输出文件：

```text
v4_go_no_go_analysis_panel.csv
v4_go_no_go_sample_diagnostics.csv
v4_go_no_go_interaction_effects.csv
v4_go_no_go_subsample_effects.csv
v4_go_no_go_focus_main_effects.csv
```

同时扩展了 Top10 CSMAR CAR：

```text
results/v4_peer_spillover_csmar_event_study/v4_peer_event_with_car_csmar_top10.csv
results/v4_peer_spillover_controls_heterogeneity/v4_peer_event_controls_heterogeneity_top10.csv
```

## 3. 样本量

主窗口为 clean `CAR[-1,+1]`。

| Peer 口径 | clean rows | events | peer firms | AI-active rows, t-5 preobservable | AI-active share |
|---|---:|---:|---:|---:|---:|
| Top3 | 1,050 | 397 | 430 | 726 | 0.691 |
| Top5 | 1,755 | 398 | 640 | 1,203 | 0.685 |
| Top10 | 3,508 | 399 | 1,070 | 2,360 | 0.673 |

Top10 的样本量确实扩大了，但这并不自动改善结果。

## 4. AI-active 定义

本轮使用四个口径：

| 变量 | 含义 |
|---|---|
| `ai_existing_broad` | 旧口径：prior public GenAI evidence 或 2024 年报 GenAI evidence |
| `ai_public_tminus5` | peer 在事件日前至少 5 天已有公开 GenAI 事件 |
| `ai_annual_tminus5` | peer 的 2024 年报 GenAI 证据，且年报披露日早于事件日前 5 天 |
| `ai_preobs_tminus5` | `ai_public_tminus5` 或 `ai_annual_tminus5` |

当前事件集中在 2026-02-24 至 2026-05-19，所以 2024 年报证据大多是事件日前可观测信息；但以后如果扩到 2024 或 2025 事件，必须严格使用年报披露日，而不是财年。

## 5. Top5 主结果：边际存活

主规格：

```text
PeerCAR[-1,+1] =
    Specificity × ProductSimilarity
  + Specificity × ProductSimilarity × AIActivePeer
  + Event FE
  + PeerControls
```

其中 `AIActivePeer = ai_preobs_tminus5`。

### Top5, clean CAR[-1,+1], two-way clustered by event and peer

| Controls | Effect | coef | se | p |
|---|---|---:|---:|---:|
| No | incremental AI-active effect | -0.0104 | 0.0054 | 0.055 |
| Yes | incremental AI-active effect | -0.0094 | 0.0054 | 0.084 |
| No | total AI-active effect | -0.0133 | 0.0109 | 0.224 |
| Yes | total AI-active effect | -0.0133 | 0.0105 | 0.205 |

解释：

- 三重交互的“差异效应”仍为负，且在 5% 到 10% 之间；
- 但 AI-active 组内总效应本身不显著；
- 因此现在只能谨慎说：AI-active peer 的竞争敏感度相对更强；
- 不能强写为：AI-active peer 组内显著负反应。

## 6. 严格公开事件口径不支持主故事

如果只用事件日前 t-5 的公开 GenAI 事件定义 AI-active：

```text
AIActivePeer = ai_public_tminus5
```

Top5 clean `CAR[-1,+1]` 下，三重交互不成立：

| Controls | incremental effect coef | p |
|---|---:|---:|
| No | 0.0021 | 0.624 |
| Yes | 0.0032 | 0.452 |

这说明当前信号主要不是由“peer 已经有公开 GenAI 事件”驱动，而是更多来自 2024 年报 GenAI 证据或二者合并后的分组。

这是一个重要风险。

## 7. Top10 扩样本后信号消失

Top10 clean `CAR[-1,+1]` 样本扩大到 3,508 条观测，但三重交互不再显著。

`AIActivePeer = ai_preobs_tminus5`：

| Controls | Effect | coef | se | p |
|---|---|---:|---:|---:|
| No | incremental AI-active effect | -0.0042 | 0.0039 | 0.290 |
| Yes | incremental AI-active effect | -0.0025 | 0.0039 | 0.524 |
| No | total AI-active effect | -0.0039 | 0.0044 | 0.377 |
| Yes | total AI-active effect | -0.0041 | 0.0044 | 0.356 |

解释：

```text
当前结果不是广义 Top10 产品市场 peer 效应。
更像是 Top5 内的近邻竞品局部反应。
```

这不是完全坏事，因为竞争威胁本来应集中在最近竞品上；但论文必须把这写清楚，不能把结果包装成宽泛行业溢出。

## 8. 当前判断

### 不是 No-Go

原因：

- Top5 下三重交互方向仍稳定为负；
- 两维聚类后没有完全消失；
- t-5 preobservable 合并口径仍有边际显著；
- 样本有 398 个事件和 1,755 条 clean peer-event，不是小样本故事。

### 但也不是 Green-Go

原因：

- Top10 扩样本后信号消失；
- `prior public only` 口径完全不支持；
- AI-active 组内总效应不显著；
- 当前结果依赖 `2024 annual-report GenAI evidence` 这一层；
- 如果补入 CAC / 专利 / 招聘后系数消失，论文主线就不应继续。

## 9. 下一步优先级

按重要性排序：

1. **重构 AI-active composite**
   - 加入 CAC 备案；
   - 加入 AI / GenAI 专利；
   - 加入 AI 招聘；
   - 只保留事件日前 t-5 可观测证据。

2. **把主样本明确限定为 Top5 近邻竞品**
   - Top10 只能作为扩展 / placebo；
   - 论文机制写成 closest product-market rivals，而不是 broad industry peers。

3. **做 pseudo-peer placebo**
   - 同行业低相似 peer；
   - 随机 peer；
   - 不同行业同规模 peer。

4. **检查 AI-active 组内总效应**
   - 如果补强 AI-active 后仍然只有差异效应、没有组内效应，写作要更谨慎；
   - 最好能得到 AI-active 组内 `Specificity × ProductSimilarity` 为负。

5. **升级 specificity 测度**
   - 当前 Hope-style proxy 可用；
   - 但正式版最好做中文 NER：组织、产品 / 模型名、金额、百分比、日期、合作方、场景。

## 10. 当前一句话结论

```text
这条线仍可继续，但必须降温：
当前证据支持“Top5 近邻竞品中，AI-active peer 对焦点公司具体 GenAI 披露更敏感”，
还不足以支持“AI-active peers 显著负向重估”或“广义 Top10 同业溢出”。
```
