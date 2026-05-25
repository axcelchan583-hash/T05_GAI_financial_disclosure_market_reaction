# v4 CSMAR 行情覆盖诊断

日期：2026-05-22

## 结论

当前本地 CSMAR 日行情不能直接替换 v4 互动平台事件样本的 Sina 临时行情。原因很明确：

```text
v4 互动平台事件日期范围：2026-02-24 到 2026-05-19
本地 CSMAR 股票日行情截止：2026-02-13
本地 CSMAR 指数日行情截止：2026-02-13
```

因此，当前 CSMAR 版本事件收益面板为空，不是回归不显著，也不是代码逻辑失败，而是正式行情数据截止日期早于事件日期。

## 已完成处理

新增脚本：

```text
scripts/run_v4_peer_spillover_csmar_event_study.py
```

该脚本已经完成：

1. 读取 v4 Top N 产品市场 peer-event X 样本；
2. 从 CSMAR 日个股交易 Excel 中只抽取本研究需要的 peer 股票；
3. 从 CSMAR 指数交易 Excel 中抽取上证指数收益；
4. 缓存干净行情子集；
5. 若日期覆盖足够，可计算：
   - `peer_ar0`
   - `peer_car_0_p1`
   - `peer_car_m1_p1`
   - ST / 正常交易状态 flag
   - 涨跌停 flag
6. 自动输出覆盖诊断和回归表。

输出目录：

```text
results/v4_peer_spillover_csmar_event_study/
```

当前输出：

```text
v4_csmar_peer_daily_returns_subset.csv
v4_csmar_market_returns_000001.csv
v4_csmar_return_coverage_summary.csv
v4_csmar_regression_summary.csv
v4_peer_event_with_car_csmar.csv
```

覆盖诊断结果：

```text
Top 3 peer-event X observations: 1,197
Events: 399
Focal firms: 219
Peer firms in X: 491

CSMAR peer return rows extracted: 528,506
CSMAR peer firms covered: 483
Stock return date range: 2021-02-18 to 2026-02-13
Market return date range: 2010-02-22 to 2026-02-13

Event-return observations: 0
```

## 对研究设计的含义

这条线本身没有被否定。相反，这次诊断说明，当前最关键的数据缺口不是 X，也不是 peer network，而是正式事件研究 Y 的行情覆盖。

当前 v4 试跑中的 `Sina` 行情仍可用于方向性 pilot，但不能作为论文正式结果。正式稿需要以下三种处理之一：

1. 补齐 CSMAR / Wind / RESSET 的 2026-02-14 到 2026-05-19 日行情；
2. 将事件样本扩展到 2023-2025 年的正式公告、投资者关系记录或新闻源，使其落入现有 CSMAR 行情覆盖；
3. 暂时保留 Sina / 东方财富作为快速试跑，但在文档中标注为 pilot-only。

## 下一步建议

### 优先方案 A：补 2026 日行情

这是最直接的路线。

需要补：

```text
股票日收益：2026-02-14 到 2026-05-19
指数日收益：2026-02-14 到 2026-05-19
```

补齐后直接重跑：

```bash
/opt/miniconda3/bin/python scripts/run_v4_peer_spillover_csmar_event_study.py --max-peer-rank 3
```

然后再跑 Top 5：

```bash
/opt/miniconda3/bin/python scripts/run_v4_peer_spillover_csmar_event_study.py --max-peer-rank 5 --refresh-cache
```

### 优先方案 B：继续用 Sina 做信号搜索，但只作为 pilot

当前已经有 Sina 版本：

```text
results/v4_peer_spillover_main_effect_pilot/v4_peer_event_with_car_sina.csv
```

在正式行情没补齐前，可以先继续做：

- `AR[0]`
- `CAR[0,+1]`
- Top 1 / Top 3 peer portfolio
- 低 peer AI capability 异质性
- 涨跌停 / ST / 重大事项过滤

但所有结果只能写成 pilot，不应写成正式实证结果。

### 优先方案 C：扩展 2023-2025 事件样本

现有 CSMAR 行情覆盖到 2026-02-13，所以 2023-2025 事件可以正式跑。

当前巨潮正式公告具体候选只有 20 条，不够。若要走这条路，需要重新扩展事件源：

- 巨潮正式公告全文，而不是只靠标题；
- 投资者关系活动记录；
- 新闻稿 / 媒体公告；
- 上证 e 互动和互动易历史问答；
- 年报 GenAI 披露只能作为披露文本，不适合作为高频事件源主样本。

## 当前判断

现在的正确动作不是推翻选题，而是补齐事件研究 Y 的正式行情数据。主效应方向和题材仍可继续，当前瓶颈是数据工程。
