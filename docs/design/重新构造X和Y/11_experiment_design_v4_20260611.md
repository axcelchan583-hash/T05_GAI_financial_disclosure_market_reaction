# T05 实验设计 v4（20260611）

状态：当前实验设计 source of truth。

文档分工：

```text
本文件（11）      实验设计定稿：假设、表序、防守、执行顺序
08 + 10           编码口径 source of truth（v3.1 判定树 + v3.2 链内性亮线/L 标签）
09                理论备忘（signed detector 框架与引用栈），承重理论从此取
文献调研.md       先例地图 + 2026-06-11 撞车检查 + DT 方法借鉴备忘
```

## 1. 研究问题与定位

> 资本市场是否把可信的 GenAI 产业链 initiative 披露定价为对产品市场
> 竞争对手的横向竞争威胁——即竞争者横截面股价是否构成对披露可信度的
> "带符号检测器"？

理论框架（取自 09）：同一条 GenAI 公告对竞争者同时触发两股反向的力——
category-based contagion（概念板块同涨，正）与 competitive threat
（business stealing，负）。cheap talk 只触发 contagion（净 ≥ 0），
credible commitment 才触发 competitive（净 < 0）。竞争者净 CAR 的符号
因此揭示可信度，比发布者自身定价（信息与情绪同号叠加）更严格。

新颖性边界（2026-06-11 撞车检查，见文献调研.md）：

```text
已被占据：
    own-firm 可信度定价      AI-washing 文献（Song et al. 2026 FRL 等，含中国A股崩盘风险篇）
    供应商正向纵向溢出        Qian, Peng & Li (2025, POM)，+0.27%
本文占据：
    竞争者端（横向、负向）×可信度调节×中国A股 —— 三个孤岛之间的空白
先发风险：
    Qian 团队扩展到对手是自然下一步，进度优先于完美
```

X 的论文表述：**GenAI value-chain initiative disclosure**（产业链宽口径），
不得写成 GenAI capability disclosure。

## 2. X：编码口径定稿（分类的当前状态）

判定树与字段以 08（v3.1）+ 10（v3.2）为准，此处只给定稿摘要。

### 2.1 两问判定

```text
问1 可信性：承诺可信吗？
    框架协议亮线（自称框架/无金额无审议/另行约定，两项及以上）
    + 投资 gate（真金白银、支付安排、对赌为强信号）
问2 链内性：交付物落在 GenAI 四层链内吗？
    L=model / L=app / L=compute / L=data；
    链外泛 AI（传统CV/安防/质检等）与仅背景段蹭 ChatGPT 的判 D
```

### 2.2 判定码与事件池用途

| verdict | 定义 | 用途 |
|---|---|---|
| A | 首次、可信、公告日可用、链内 | 主样本 |
| B | 真 GenAI 但公告日不可用 | 回填更早首次日，不直接进事件研究 |
| C | 真 GenAI 但非首次/重复进展 | 剔除，首次性由 A 占用 |
| D-fw | 链内话题真、承诺假（框架协议） | cheap-talk placebo 池，保留公告日 |
| D | 链外泛 AI 或非有效事件 | 剔除，不保留事件日 |
| U | 待定 | 二次核验 |

2×2 边界（防 placebo 池污染）：

```text
              承诺可信           承诺不可信
链内           A | L=...         D-fw | L=...
链外（泛AI）    D                 D
```

### 2.3 A 类字段（一行人工码）

```text
人工码: A | OUT=1/0 | M=own/ext | L=model/app/compute/data | 证=一句原文 | R=+/- [| 日=YYYY-MM-DD]
```

- `OUT`：产出是否面向外部客户收费/销售/服务（09 框架中的 CT，
  business-stealing vs 行业 TAM 故事的关键切割变量）；
- `M`：own=自己发布/上线/备案/部署，ext=合作/投资/收购/算力承诺借外力；
- `L`：四层链内位置，全部 A 与 D-fw 必打；
- `R`：已落地（+）vs 计划意向（-）。

### 2.4 编码流程

1. DeepSeek V4-Pro 预编码分流（prompt 须含两问亮线、四层定义、2×2 边界）；
2. 人工复核优先级：A > B > D-fw > U > D 抽样 5%-10%
   （D 抽样优先抽算力类防漏保、背景段蹭热点类防误收）；
3. 每约 100 条统计 verdict/OUT/M/L/R 分布；
   若 `L=model/app` 占比过低使层间对比失去意义，回 10 号文件重议口径；
4. 报告 machine/DS/human 三方一致率（kappa），进论文编码可靠性附注。

## 3. 假设与承重结构

```text
H1 存在性（铺垫）：A 类事件的 product-market competitor CAR[0,+1] < 0
H2 符号分离（承重）：A 类竞争者 CAR 显著负于 D-fw 类（contagion 基准），
    triple-difference: (A vs D-fw) × AIActivePeer
H3 可信度梯度（承重）：Spec × AIActivePeer < 0，event FE 下
    （理论锚：Chakraborty-Harbaugh comparative cheap talk）
H4 边界条件（机制切割）：
    OUT=1 负效应强于 OUT=0（business stealing vs 行业利好同涨）
    竞争者散户持股/换手率高 -> 负效应被 contagion 抵消
    L=model/app vs L=compute 分层方向一致性检验
```

旧口径数字（v29 等：PeerAR[0]=-0.25%，Spec×AIActivePeer p=0.022）一律
provisional，v3.1/v3.2 清洗后必须重跑，论文不得引用旧口径估计。

## 4. 表序

```text
T1  样本构造与编码分布（含三方一致率 kappa）
T2  H1：A 类竞争者 CAR 主效应（market model, [0,+1], event FE, 双聚类）
T3  层间异质性：L=model/app vs L=compute（宽口径防守第一件）
T4  H2：A vs D-fw stacked contrast + triple-difference（头号贡献表）
T5  H3：Spec × AIActivePeer 机制
T6  H4：OUT、散户持股、M、R 切割
T7  验证表：A vs D-fw 事后落地率
    （网信办生成式AI备案、AI专利、算力资本开支、招聘数据；DT 借鉴）
T8  Placebo：非 AI 投资/扩产公告 -> peer CAR（宽口径防守第二件）
T9  供应商 benchmark：Qian 式供应商正向在同一事件样本复刻
    （反号图景：同一公告，对手负、供应商正；接 Fee-Thomas/Oxley 设计先例）
```

客户端不做（A 股前五大客户披露稀疏、多非上市），最多附录提及。

## 5. 识别防守清单

1. **peer 定义**（头号软肋）：candidate-menu 来源 + LLM 筛选规则 + validity
   tests 全披露；传统年报文本 peer 不复制主结果写成结果而非藏起来
   （只有 LLM 识别的直接竞品被重估，粗口径行业同行不被重估，
   符合精准竞争威胁预测）；
2. **peer 公告污染**：剔除窗口内 peer 自身 GenAI/重大公告
   （同群模仿性披露文献作为清理依据）；
3. **focal-peer 镜像**：focal CAR 越正，peer CAR 越负；
4. **长窗 CAR + 分析师预测修正**：区分现金流预期 vs 注意力轮动；
5. **AIActivePeer 同源性**：headline 用 ext_any（t-5 前可观察），
   text-history 仅并列稳健性；
6. **解释边界**：event FE 识别同一公告内 AI-active vs non-AI-active peer
   的相对差异；只写 competitive-risk reassessment / 预期重估，
   不写真实业务挤出；peer FE 下结果弱化必须披露；
7. **Bloom et al. (2013) 反向基准正面回应**：技术溢出可能数量上占优，
   论证短窗内 rivalry 信号先行、spillover 滞后，AIActivePeer 负号
   （吸收能力故事预测正号）是 competitive 压过 spillover 的直接证据。

## 6. 执行优先级（2026-06-11 起）

1. 完成 v3.1+v3.2 人工编码：先 118 条复核收尾（冲突归因统计：
   38+1 条冲突中口径性 vs 能力性占比），再 DS 用新 prompt 跑剩余队列；
2. A 样本定稿 -> 重跑 T2/T3/T4/T5（含全部防守清单项）；
3. T7 验证数据收集（备案名单、AI 专利、算力开支）可与编码并行；
4. T8 非 AI 投资公告 placebo 样本构造；
5. T9 供应商 benchmark：复用 Qian 复刻仓库管道接入 v3.1 事件样本
   （供应链关系数据处理参照 DT 双边溢出文献管道）；
6. 投稿定位沿 09：TAR/CAR 第一档，MS 冲刺档，RAST/JAE 稳妥档；
   中文期刊版本参照 DT 文献叙事模板。
