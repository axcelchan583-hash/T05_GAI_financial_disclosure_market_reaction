# v4 正式 CSMAR 行情主效应重跑

日期：2026-05-22

## 目的

用新下载并归档的 CSMAR `.dta` 日行情，替换前一版 Sina 临时行情，重跑 v4 产品市场同业溢出的主效应。

当前主线：

```text
X = GenAI disclosure specificity × product-market similarity
Y = product-market peer abnormal return
```

## 数据接入

新增行情数据：

```text
股票日收益：
/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/上市公司财务信息/_daily_2026_02_14_2026_05_22_patch_dta/

指数日收益：
/Users/mac/computerscience/第三方资料/01_数据资源/国泰安/第三方数据资源/上市公司财务信息/_idx_2026_02_14_2026_05_22_patch_dta/
```

脚本：

```text
scripts/run_v4_peer_spillover_csmar_event_study.py
```

本次更新：

- 脚本优先读取新归档的 `.dta` 文件；
- 股票收益使用 `Dretwd`；
- 指数收益使用 `TRD_Index.dta` 的 `Retindex`；
- `Retindex` 本身是小数收益率，不再除以 100；
- 输出 Top 3 与 Top 5 的独立结果文件，避免互相覆盖。

## 输出文件

目录：

```text
results/v4_peer_spillover_csmar_event_study/
```

关键输出：

```text
v4_peer_event_with_car_csmar_top3.csv
v4_peer_event_with_car_csmar_top5.csv
v4_csmar_regression_summary_top3.csv
v4_csmar_regression_summary_top5.csv
v4_csmar_return_coverage_summary_top3.csv
v4_csmar_return_coverage_summary_top5.csv
```

## 覆盖情况

### Top 3 peers

```text
X peer-event observations: 1,197
Events: 399
Focal firms: 219
Peer firms in X: 491

Matched event-return observations: 1,145
Matched events: 398
Matched peer firms: 460
Clean [-1,+1] observations: 1,050
```

### Top 5 peers

```text
X peer-event observations: 1,993
Events: 399
Focal firms: 219
Peer firms in X: 728

Matched event-return observations: 1,907
Matched events: 399
Matched peer firms: 681
Clean [-1,+1] observations: 1,755
```

清理口径：

```text
normal_trading_m1_p1 == 1
no_limit_m1_p1 == 1
obs_car_m1_p1 == 3
```

即事件窗口 `[-1,+1]` 内正常交易、无涨跌停、三日窗口完整。

## 主效应结果

模型：

```text
Peer abnormal return_ijt =
    beta * Specificity_it × ProductSimilarity_ij
  + ProductSimilarity_ij
  + Event FE
  + error_ijt
```

标准误：

```text
cluster by event_id
```

### Top 3 peers

| Sample | Y | coef | p-value | nobs | events | peer firms |
|---|---:|---:|---:|---:|---:|---:|
| Raw | AR[0] | -0.0022 | 0.697 | 1,143 | 398 | 459 |
| Raw | CAR[0,+1] | -0.0125 | 0.237 | 1,145 | 398 | 460 |
| Raw | CAR[-1,+1] | -0.0122 | 0.216 | 1,145 | 398 | 460 |
| Clean | AR[0] | -0.0049 | 0.343 | 1,050 | 397 | 430 |
| Clean | CAR[0,+1] | -0.0126 | 0.228 | 1,050 | 397 | 430 |
| Clean | CAR[-1,+1] | -0.0131 | 0.152 | 1,050 | 397 | 430 |

### Top 5 peers

| Sample | Y | coef | p-value | nobs | events | peer firms |
|---|---:|---:|---:|---:|---:|---:|
| Raw | AR[0] | -0.0051 | 0.293 | 1,904 | 399 | 680 |
| Raw | CAR[0,+1] | -0.0186 | 0.120 | 1,906 | 399 | 681 |
| Raw | CAR[-1,+1] | -0.0156 | 0.206 | 1,907 | 399 | 681 |
| Clean | AR[0] | -0.0049 | 0.265 | 1,755 | 398 | 640 |
| Clean | CAR[0,+1] | -0.0116 | 0.120 | 1,755 | 398 | 640 |
| Clean | CAR[-1,+1] | -0.0086 | 0.258 | 1,755 | 398 | 640 |

## 解释

正式 CSMAR 行情没有推翻原来的方向。所有主规格中，`Specificity × ProductSimilarity` 的系数都是负的，这与“焦点公司更具体的 GenAI 披露对产品市场同业形成竞争威胁”的方向一致。

但结果还没有达到常规显著性。最接近的是 Top 5 的 `CAR[0,+1]`：

```text
Raw Top 5 CAR[0,+1]: coef = -0.0186, p = 0.120
Clean Top 5 CAR[0,+1]: coef = -0.0116, p = 0.120
```

因此，当前不能写成“主效应显著成立”。更准确的判断是：

```text
方向稳定，但平均主效应仍弱。
```

这和前一轮判断一致：平均效应可能混合了竞争威胁和行业机会两个方向，下一步应转向理论上更干净的异质性，而不是继续只赌平均主效应。

## 当前结论

这条线继续做，但应改成：

```text
先承认平均效应方向稳定但不强；
重点转向 peer AI capability / event strength / product-oriented disclosure 的异质性。
```

最优先下一张表：

```text
Specificity × ProductSimilarity × LowPeerAICapability
```

预期：

```text
低 AI 能力同业：负向反应更强；
高 AI 能力同业：负向反应弱，甚至可能转为行业机会正向反应。
```

## 下一步

1. 构造 peer 在事件日前的 GenAI 能力：
   - 披露前是否已有 GenAI 互动回复；
   - 披露前是否已有 GenAI 正式公告；
   - 披露前是否已有 CAC 备案；
   - 披露前是否已有 AI / 大模型相关专利或招聘证据。
2. 跑三重交互：

```text
PeerCAR_ijt =
    beta1 * Specificity_it × ProductSimilarity_ij
  + beta2 * Specificity_it × ProductSimilarity_ij × LowPeerAICapability_jt
  + Event FE
  + error_ijt
```

3. 同时把事件分成：
   - product-oriented GenAI disclosure；
   - process / internal efficiency-oriented GenAI disclosure。

如果三重交互仍没有方向和强度，再考虑是否转向更强事件源，而不是继续扩互动平台平均主效应。
